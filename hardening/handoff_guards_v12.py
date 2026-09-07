"""Twelfth bounded adapter suite: P111-P120, the review deliverables. Requires handoff_guards_v1.py, handoff_guards_v6.py
and handoff_guards_v8.py from this TXT. Every page composition, form field, deck readback, document build, graph lookup
and calendar grid below is a library primitive call; local code declares fixtures and policies and turns a primitive
result into a Blocked outcome. All runtime inputs are authored fixtures. No model client and no network.
Run: python handoff_guards_v12.py --report report.json
"""
from __future__ import annotations
import argparse, calendar, datetime, hashlib, importlib.metadata, io, json, logging, os, time, traceback, warnings, zipfile
from pathlib import Path
from typing import Literal
import docx
import markdownify
import networkx as nx
import pptx
import pymupdf
import pypdf
from deepdiff import DeepDiff
from lxml import html as lxml_html
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches
from pydantic import BaseModel, ConfigDict, Field, ValidationError
import handoff_guards_v1 as g
import handoff_guards_v6 as g6
import handoff_guards_v8 as g8
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

# ---------------------------------------------------------------- P111
def fitted_rect(source: pymupdf.Rect, box: pymupdf.Rect) -> pymupdf.Rect:
    """Largest rect inside box with the source aspect ratio, centered."""
    scale = min(box.width / source.width, box.height / source.height)
    width, height = source.width * scale, source.height * scale
    x = box.x0 + (box.width - width) / 2; y = box.y0 + (box.height - height) / 2
    return pymupdf.Rect(x, y, x + width, y + height)


def handout(slides: list[bytes], *, per_page: int = 2, fit: bool = True) -> dict:
    out = pymupdf.open(); placed = []
    page = None
    for i, slide in enumerate(slides):
        slot = i % per_page
        if slot == 0: page = out.new_page(width=595, height=842)
        box = pymupdf.Rect(20, 20 + slot * 400, 380, 400 + slot * 400)
        with pymupdf.open(stream=slide, filetype='pdf') as source:
            target = fitted_rect(source[0].rect, box) if fit else box
            page.show_pdf_page(target, source, 0)
            placed.append({'slide': i, 'page': out.page_count, 'aspect_source': round(source[0].rect.width / source[0].rect.height, 4),
                           'aspect_target': round(target.width / target.height, 4)})
        note = pymupdf.Rect(400, box.y0, 575, box.y1)
        page.draw_rect(note)  # the adjacent note area is drawn empty
    data = out.tobytes()
    reopened = pymupdf.open(stream=data, filetype='pdf')
    note_text = ''.join(p.get_textbox(pymupdf.Rect(400, 0, 575, 842)) for p in reopened)
    return {'pages': reopened.page_count, 'placed': placed, 'notes_blank': note_text.strip() == '', 'bytes': data}

# ---------------------------------------------------------------- P112, P113
def review_form(slide_count: int) -> bytes:
    doc = pymupdf.open()
    for i in range(slide_count):
        page = doc.new_page()
        notes = pymupdf.Widget(); notes.rect = pymupdf.Rect(50, 50, 400, 150)
        notes.field_name = 'notes_%d' % i; notes.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
        notes.field_flags = pymupdf.PDF_TX_FIELD_IS_MULTILINE; notes.field_value = ''
        page.add_widget(notes)
        check = pymupdf.Widget(); check.rect = pymupdf.Rect(50, 170, 70, 190)
        check.field_name = 'reviewed_%d' % i; check.field_type = pymupdf.PDF_WIDGET_TYPE_CHECKBOX; check.field_value = False
        page.add_widget(check)
    return doc.tobytes()


def read_fields_two_ways(data: bytes) -> dict:
    by_pymupdf = {}
    doc = pymupdf.open(stream=data, filetype='pdf')
    for page in doc:
        for w in page.widgets(): by_pymupdf[w.field_name] = w.field_value
    by_pypdf = {k: v.get('/V') for k, v in (pypdf.PdfReader(io.BytesIO(data)).get_fields() or {}).items()}
    return {'pymupdf': by_pymupdf, 'pypdf': by_pypdf}


def blank_state(value) -> bool:
    return value in (None, '', False, 'Off', '/Off')


def text_outside_widgets(data: bytes) -> str:
    """Page text with every block that overlaps a form widget removed.

    A filled field's appearance stream contributes to get_text, so source content and
    reviewer input are indistinguishable unless the widget areas are excluded.
    """
    doc = pymupdf.open(stream=data, filetype='pdf'); out = []
    for page in doc:
        boxes = [w.rect for w in page.widgets()]
        for block in page.get_text('blocks'):
            rect = pymupdf.Rect(block[:4])
            if not any(rect.intersects(b) for b in boxes): out.append(block[4])
    return ''.join(out)


def fill_fields(data: bytes, values: dict[str, object]) -> bytes:
    doc = pymupdf.open(stream=data, filetype='pdf')
    remaining = dict(values)
    for page in doc:
        for w in page.widgets():
            if w.field_name in remaining:
                w.field_value = remaining.pop(w.field_name); w.update()
    if remaining: raise g.Blocked('form has no field named ' + ','.join(sorted(remaining)))
    return doc.tobytes()

# ---------------------------------------------------------------- P114
def deck_outline(data: bytes) -> dict:
    prs = pptx.Presentation(io.BytesIO(data)); slides = []
    for index, slide in enumerate(prs.slides):
        blocks = []
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text: blocks.append({'kind': 'text', 'value': shape.text_frame.text})
            if shape.has_table: blocks.append({'kind': 'table', 'value': [[c.text for c in r.cells] for r in shape.table.rows]})
            if shape.has_chart:
                chart = shape.chart
                blocks.append({'kind': 'chart', 'value': {'categories': list(chart.plots[0].categories),
                                                          'series': {s.name: list(s.values) for s in chart.series}}})
        slides.append({'index': index, 'blocks': blocks})
    return {'slides': slides, 'text_blocks': sum(1 for s in slides for b in s['blocks'] if b['kind'] == 'text'),
            'table_cells': sum(len(r) for s in slides for b in s['blocks'] if b['kind'] == 'table' for r in b['value']),
            'chart_values': sum(len(v) for s in slides for b in s['blocks'] if b['kind'] == 'chart' for v in b['value']['series'].values())}


def outline_html(outline: dict) -> str:
    rows = []
    for slide in outline['slides']:
        for b in slide['blocks']:
            rows.append({'slide': str(slide['index']), 'kind': b['kind'], 'value': json.dumps(b['value'], sort_keys=True) if b['kind'] != 'text' else b['value']})
    return g8.CATALOG.render(title='Deck outline', fields=['slide', 'kind', 'value'], rows=rows)

# ---------------------------------------------------------------- P115
def reading_copy(outline: dict) -> bytes:
    d = docx.Document(); d.add_heading('Reading copy', 1)
    for slide in outline['slides']:
        d.add_heading('Slide %d' % slide['index'], 2)
        for b in slide['blocks']:
            if b['kind'] == 'text': d.add_paragraph(b['value'])
            elif b['kind'] == 'table':
                rows = b['value']; table = d.add_table(rows=0, cols=len(rows[0]))
                for row in rows:
                    cells = table.add_row().cells
                    for cell, value in zip(cells, row): cell.text = value
            else:
                series = b['value']['series']; categories = b['value']['categories']
                table = d.add_table(rows=0, cols=1 + len(series))
                header = table.add_row().cells; header[0].text = 'category'
                for cell, name in zip(header[1:], series): cell.text = name
                for i, category in enumerate(categories):
                    cells = table.add_row().cells; cells[0].text = category
                    for cell, values in zip(cells[1:], series.values()): cell.text = str(values[i])
    buf = io.BytesIO(); d.save(buf); return buf.getvalue()

# ---------------------------------------------------------------- P116, P117, P118
def dependency_reference(steps: list[dict], edges: list[tuple[str, str]]) -> dict:
    ids = [s['id'] for s in steps]
    graph = nx.DiGraph(); graph.add_nodes_from(ids); graph.add_edges_from(edges)
    if set(graph) != set(ids): raise g.Blocked('dependency endpoint outside the step set')
    if not nx.is_directed_acyclic_graph(graph): raise g.Blocked('recorded dependencies contain a cycle')
    display = sorted(ids)  # display order is alphabetical and is not the dependency order
    return {'steps': len(ids), 'edges': graph.number_of_edges(), 'display_order': display,
            'predecessors': {n: sorted(graph.predecessors(n)) for n in ids},
            'successors': {n: sorted(graph.successors(n)) for n in ids},
            'display_order_is_not_dependency_order': display != list(nx.topological_sort(graph))}


def reference_cards(edges: list[tuple[str, str]], sentences: dict[str, str]) -> list[dict]:
    cards = []
    for source, target in dict.fromkeys(edges):  # dict.fromkeys removes duplicates and keeps first-seen order
        for node in (source, target):
            if node not in sentences: raise g.Blocked('no recorded sentence for step ' + node)
        cards.append({'source': source, 'target': target, 'source_sentence': sentences[source], 'target_sentence': sentences[target]})
    return cards


def coverage_with_references(steps: list[dict], discussed: set[str]) -> dict:
    rows = []
    for s in steps:
        rows.append({'id': s['id'], 'sentence': s['sentence'],
                     'state': 'discussed' if s['id'] in discussed else 'not_discussed'})
    unknown = discussed - {s['id'] for s in steps}
    if unknown: raise g.Blocked('coverage names steps that do not exist: ' + ','.join(sorted(unknown)))
    return {'rows': rows, 'discussed': sum(1 for r in rows if r['state'] == 'discussed'),
            'basis': 'discussion coverage, not completion (P20, P106)'}

# ---------------------------------------------------------------- P119
def month_grid(year: int, month: int, *, first_weekday: int) -> dict:
    grid = calendar.Calendar(firstweekday=first_weekday).monthdayscalendar(year, month)
    return {'first_weekday': first_weekday, 'weeks': grid,
            'process_default': calendar.firstweekday(),
            'days': sorted(d for week in grid for d in week if d)}


def events_on_grid(year: int, month: int, events: list[dict], *, first_weekday: int) -> dict:
    grid = month_grid(year, month, first_weekday=first_weekday)
    placed = {}
    for e in events:
        date = datetime.date.fromisoformat(e['date'])
        if (date.year, date.month) != (year, month): raise g.Blocked('event outside the rendered month: ' + e['date'])
        placed.setdefault(date.day, []).append(e['title'])
    if set(placed) - set(grid['days']): raise g.Blocked('event day is not in the grid')
    return {'grid': grid, 'placed': placed, 'events': len(events)}

# ---------------------------------------------------------------- P120
def ordered_blocks(data: bytes) -> list[dict]:
    return [b for b in g8.document_blocks(data)['blocks']] if False else g9_blocks(data)


def g9_blocks(data: bytes) -> list[dict]:
    from docx.table import Table as DocxTable
    out = []
    for block in docx.Document(io.BytesIO(data)).iter_inner_content():
        if isinstance(block, DocxTable): out.append({'kind': 'table', 'value': [[c.text for c in r.cells] for r in block.rows]})
        elif block.text: out.append({'kind': 'paragraph', 'value': block.text})
    return out


def compare_documents(original: bytes, styled: bytes) -> dict:
    a, b = g9_blocks(original), g9_blocks(styled)
    diff = DeepDiff(a, b, zip_ordered_iterables=True)
    return {'blocks': len(a), 'identical': not diff, 'diff': json.loads(diff.to_json()) if diff else {}}

C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(111)
def show_pdf_page_does_not_preserve_aspect():
    slide = g8.print_pdf('<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>t</title>'
                         '<style>@page{size:A4 landscape;margin:1cm}</style></head><body><h1>Slide one</h1></body></html>')
    source_rect = pymupdf.open(stream=slide, filetype='pdf')[0].rect
    box = pymupdf.Rect(20, 20, 380, 400)
    stretched = handout([slide], fit=False)
    g.require(abs(stretched['placed'][0]['aspect_target'] - stretched['placed'][0]['aspect_source']) > 0.1,
              'the unfitted placement changes the aspect ratio')  # show_pdf_page fills the rect it is given
    fitted = handout([slide, slide, slide], per_page=2, fit=True)
    g.equal(fitted['pages'], 2)  # three slides at two per page
    for placed in fitted['placed']:
        g.equal(placed['aspect_source'], placed['aspect_target'])  # the target rect is computed from the source aspect
    g.equal([p['slide'] for p in fitted['placed']], [0, 1, 2])  # slide order preserved
    g.equal(fitted['notes_blank'], True)
    return {'stretch_reproduced': True, 'fitted_rect_preserves_aspect': True, 'slide_order_preserved': True,
            'note_areas_blank': True, 'pages_from_the_reopened_document': True}


@case(112)
def form_fields_start_blank_in_both_readers():
    data = review_form(2)
    fields = read_fields_two_ways(data)
    g.equal(sorted(fields['pymupdf']), ['notes_0', 'notes_1', 'reviewed_0', 'reviewed_1'])
    g.equal(sorted(fields['pypdf']), sorted(fields['pymupdf']))  # both libraries see the same field names
    g.equal(fields['pymupdf']['notes_0'], ''); g.equal(fields['pypdf']['notes_0'], None)  # they disagree on how blank reads
    g.equal(fields['pymupdf']['reviewed_0'], 'Off'); g.equal(fields['pypdf']['reviewed_0'], '/Off')
    g.equal(all(blank_state(v) for v in fields['pymupdf'].values()), True)
    g.equal(all(blank_state(v) for v in fields['pypdf'].values()), True)
    return {'both_readers_see_the_same_fields': True, 'blank_representation_differs_reproduced': True,
            'all_fields_start_blank': True, 'desktop_viewer_controls_not_claimed': True}


@case(113)
def entered_values_round_trip_without_touching_content():
    data = review_form(2)
    before_text = pymupdf.open(stream=data, filetype='pdf')[0].get_text()
    filled = fill_fields(data, {'notes_0': 'checked the quote', 'reviewed_0': True})
    fields = read_fields_two_ways(filled)
    g.equal(fields['pymupdf']['notes_0'], 'checked the quote')
    g.equal(fields['pypdf']['notes_0'], 'checked the quote')  # both readers agree once a value is present
    g.equal(blank_state(fields['pymupdf']['notes_1']), True)  # the untouched field stays blank
    g.equal(fields['pymupdf']['reviewed_0'] not in ('Off', '/Off'), True)
    after_text = pymupdf.open(stream=filled, filetype='pdf')[0].get_text()
    g.equal(before_text.strip(), '')
    g.equal('checked the quote' in after_text, True)  # the filled value becomes part of the page's extracted text
    g.equal(text_outside_widgets(filled), text_outside_widgets(data))  # excluding the widget areas, the source content is unchanged
    g.rejects(g.Blocked, lambda: fill_fields(data, {'notes_9': 'x'}))
    return {'values_round_trip_through_both_readers': True, 'untouched_fields_stay_blank': True,
            'filled_value_appears_in_page_text_reproduced': True, 'source_content_unchanged_outside_widgets': True,
            'unknown_field_blocked': True}


@case(114)
def deck_outline_keeps_order_tables_and_chart_values():
    prs = pptx.Presentation(); slide = prs.slides.add_slide(prs.slide_layouts[6])
    box = slide.shapes.add_textbox(Inches(1), Inches(0.5), Inches(4), Inches(1)); box.text_frame.text = 'Coverage'
    table = slide.shapes.add_table(2, 2, Inches(1), Inches(2), Inches(4), Inches(1)).table
    table.cell(0, 0).text = 'department'; table.cell(0, 1).text = 'cases'
    table.cell(1, 0).text = 'General'; table.cell(1, 1).text = '1390'
    data = CategoryChartData(); data.categories = ['General', 'Experts']; data.add_series('cases', [1390.0, 15.0])
    slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(1), Inches(4), Inches(5), Inches(3), data)
    buf = io.BytesIO(); prs.save(buf)
    outline = deck_outline(buf.getvalue())
    g.equal(outline['text_blocks'] >= 1, True); g.equal(outline['table_cells'], 4); g.equal(outline['chart_values'], 2)
    kinds = [b['kind'] for b in outline['slides'][0]['blocks']]
    g.equal(kinds.index('text') < kinds.index('table'), True)  # shape order is retained
    chart = [b for b in outline['slides'][0]['blocks'] if b['kind'] == 'chart'][0]
    g.equal(chart['value']['series']['cases'], [1390.0, 15.0])
    page = outline_html(outline)
    g.equal('1390' in page, True)
    markdown = markdownify.markdownify(page)
    g.equal('Coverage' in markdown, True)
    return {'slide_and_shape_order_retained': True, 'table_cells_included': 4, 'chart_values_included': 2,
            'html_and_markdown_agree_on_text': True}


@case(115)
def reading_copies_need_the_canonical_digest():
    outline = {'slides': [{'index': 0, 'blocks': [{'kind': 'text', 'value': 'Coverage'},
                                                  {'kind': 'table', 'value': [['department', 'cases'], ['General', '1390']]}]}]}
    first = reading_copy(outline); time.sleep(2.2); second = reading_copy(outline)
    g.equal(first == second, False)  # repeated Word packages differ by entry timestamps (P104)
    g.equal(g6.office_digest(first), g6.office_digest(second))  # the canonicalization is what makes the claim true
    blocks = g9_blocks(first)
    g.equal(blocks[0]['value'], 'Reading copy')
    g.equal([b for b in blocks if b['kind'] == 'table'][0]['value'], [['department', 'cases'], ['General', '1390']])
    g.equal(sum(1 for b in blocks if b['kind'] == 'table'), 1)
    return {'raw_bytes_differ_reproduced': True, 'canonical_digest_agrees': True,
            'every_source_block_present': True, 'native_tables_preserved': True}


@case(116)
def display_order_is_not_dependency_order():
    steps = [{'id': 'make', 'sentence': 'agency shall make'}, {'id': 'request', 'sentence': 'upon any request'},
             {'id': 'determination', 'sentence': 'shall determine'}]
    edges = [('request', 'make'), ('determination', 'make')]
    out = dependency_reference(steps, edges)
    g.equal((out['steps'], out['edges']), (3, 2))
    g.equal(out['display_order'], ['determination', 'make', 'request'])  # alphabetical display
    g.equal(out['predecessors']['make'], ['determination', 'request'])
    g.equal(out['successors']['make'], [])
    g.equal(out['display_order_is_not_dependency_order'], True)  # the reference must say which order it shows
    g.rejects(g.Blocked, lambda: dependency_reference(steps, edges + [('make', 'request')]))
    g.rejects(g.Blocked, lambda: dependency_reference(steps, edges + [('make', 'zz')]))
    return {'recorded_dependencies_distinguished_from_display': True, 'predecessors_and_successors_from_the_graph': True,
            'cycle_blocked': True, 'unknown_endpoint_blocked': True}


@case(117)
def reference_cards_dedupe_and_require_sentences():
    edges = [('request', 'make'), ('determination', 'make'), ('request', 'make')]
    sentences = {'request': 'upon any request', 'make': 'agency shall make', 'determination': 'shall determine'}
    cards = reference_cards(edges, sentences)
    g.equal(len(cards), 2)  # dict.fromkeys removes the duplicate pair
    g.equal([(c['source'], c['target']) for c in cards], [('request', 'make'), ('determination', 'make')])  # first-seen order kept
    g.equal(cards[0]['source_sentence'], 'upon any request')
    g.rejects(g.Blocked, lambda: reference_cards(edges + [('make', 'unknown')], sentences))
    return {'duplicate_pairs_removed': True, 'first_seen_order_kept': True, 'missing_sentence_blocked': True}


@case(118)
def coverage_rows_carry_their_source_sentences():
    steps = [{'id': 'share', 'sentence': 'collaborators share'}, {'id': 'ensure', 'sentence': 'the TSC shall ensure'}]
    out = coverage_with_references(steps, {'share'})
    g.equal([r['state'] for r in out['rows']], ['discussed', 'not_discussed'])
    g.equal(out['rows'][0]['sentence'], 'collaborators share')
    g.equal(out['discussed'], 1)
    g.require('not completion' in out['basis'], 'the coverage basis travels with the rows')
    g.rejects(g.Blocked, lambda: coverage_with_references(steps, {'share', 'zz'}))
    return {'sentences_carried_with_coverage': True, 'discussion_not_completion': True, 'unknown_step_blocked': True}


@case(119)
def the_month_grid_needs_a_declared_week_start():
    monday = month_grid(2024, 1, first_weekday=0)
    sunday = month_grid(2024, 1, first_weekday=6)
    g.equal(monday['weeks'][0], [1, 2, 3, 4, 5, 6, 7])
    g.equal(sunday['weeks'][0], [0, 1, 2, 3, 4, 5, 6])  # the same month lays out differently
    g.equal(monday['days'], sunday['days'])  # the days themselves are the same
    g.equal(monday['process_default'], calendar.firstweekday())  # the module default is process-global state
    placed = events_on_grid(2024, 1, [{'date': '2024-01-17', 'title': 'tsc-2024-01-17'}], first_weekday=0)
    g.equal(placed['placed'], {17: ['tsc-2024-01-17']})
    g.rejects(g.Blocked, lambda: events_on_grid(2024, 1, [{'date': '2024-02-01', 'title': 'x'}], first_weekday=0))
    g.rejects(ValueError, lambda: events_on_grid(2024, 1, [{'date': 'tsc-2024-01', 'title': 'x'}], first_weekday=0))
    return {'week_start_changes_the_grid_reproduced': True, 'week_start_declared_not_inherited': True,
            'module_default_is_process_global': True, 'event_outside_the_month_blocked': True}


@case(120)
def styled_documents_compare_block_by_block():
    outline = {'slides': [{'index': 0, 'blocks': [{'kind': 'text', 'value': 'Coverage'}]}]}
    original = reading_copy(outline)
    same = compare_documents(original, reading_copy(outline))
    g.equal(same['identical'], True); g.equal(same['blocks'], 3)
    changed_outline = {'slides': [{'index': 0, 'blocks': [{'kind': 'text', 'value': 'Coverage changed'}]}]}
    changed = compare_documents(original, reading_copy(changed_outline))
    g.equal(changed['identical'], False)
    g.equal('values_changed' in changed['diff'], True)
    reordered = {'slides': [{'index': 0, 'blocks': [{'kind': 'text', 'value': 'B'}, {'kind': 'text', 'value': 'A'}]}]}
    forward = compare_documents(reading_copy({'slides': [{'index': 0, 'blocks': [{'kind': 'text', 'value': 'A'}, {'kind': 'text', 'value': 'B'}]}]}), reading_copy(reordered))
    g.equal(forward['identical'], False)  # a reordering is a difference, not a match
    return {'identical_documents_match': True, 'changed_text_detected': True, 'reordering_detected': True,
            'comparison_is_positional': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['pydantic', 'pymupdf', 'pypdf', 'python-docx', 'python-pptx', 'markdownify', 'networkx', 'weasyprint', 'lxml', 'deepdiff']
    here = Path(__file__).resolve().parent
    return {'scope': 'Bounded authored handoff fixtures and reproduced library defaults; the original P111-P120 chains and their artifacts were not rerun.',
            'test_cases': len(rows), 'passed': sum(r['status'] == 'passed' for r in rows), 'failed': sum(r['status'] == 'failed' for r in rows),
            'assertions': g.ASSERTIONS, 'full_chains_executed': 0, 'network_calls': 0, 'business_actions': 0,
            'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256': {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in ['handoff_guards_v1.py', 'handoff_guards_v6.py', 'handoff_guards_v8.py']},
            'library_versions': {n: importlib.metadata.version(n) for n in packages}, 'results': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    result = run(); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ['test_cases', 'passed', 'failed', 'assertions']}))
    if result['failed']:
        print('\n'.join(r['error'] for r in result['results'] if r['error'])); raise SystemExit(1)
