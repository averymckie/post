"""Ninth bounded adapter suite: P81-P90, native Office authoring and the proof catalog. Requires handoff_guards_v1.py
and handoff_guards_v3.py from this TXT. Every workbook write, document readback, package inspection, graph grouping,
Markdown parse and DOM assertion below is a library primitive call; local code declares fixtures and policies and turns
a primitive result into a Blocked outcome. All runtime inputs are authored fixtures. No model client and no network.
Run: python handoff_guards_v9.py --report report.json [--jsdom-dir DIR]
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, io, json, logging, os, re, shutil, subprocess, tempfile, traceback, warnings, zipfile
from pathlib import Path
from typing import Literal
import docx
import networkx as nx
import openpyxl
import pptx
import xlsxwriter
from deepdiff import DeepDiff
from docx.oxml.ns import qn
from docx.table import Table as DocxTable
from lxml import etree
from markdown_it import MarkdownIt
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Emu, Inches
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from python_calamine import CalamineWorkbook
import handoff_guards_v1 as g
import handoff_guards_v8 as g8
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

# ---------------------------------------------------------------- P81, P82
def authored_workbook(rows: list[tuple[str, int]], *, cache: Literal['computed', 'default'], missing: list[int] = ()) -> bytes:
    buf = io.BytesIO(); book = xlsxwriter.Workbook(buf, {'in_memory': True}); sheet = book.add_worksheet('measures')
    sheet.freeze_panes(1, 0)
    sheet.write_row(0, 0, ['activity', 'events'])
    for i, (name, value) in enumerate(rows, start=1):
        sheet.write(i, 0, name)
        if i in missing: sheet.write_blank(i, 1, None)  # a missing source cell stays blank, never zero
        else: sheet.write_number(i, 1, value)
    total = sum(v for i, (_, v) in enumerate(rows, start=1) if i not in missing)
    formula_row = len(rows) + 1
    if cache == 'computed': sheet.write_formula(formula_row, 1, '=SUM(B2:B%d)' % (len(rows) + 1), None, total)
    else: sheet.write_formula(formula_row, 1, '=SUM(B2:B%d)' % (len(rows) + 1))
    sheet.conditional_format(1, 1, len(rows), 1, {'type': 'cell', 'criteria': '>', 'value': 100, 'format': None})
    book.close(); return buf.getvalue()


def formula_cache(data: bytes) -> dict:
    cached = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
    text = openpyxl.load_workbook(io.BytesIO(data))
    ws_c, ws_t = cached.active, text.active
    cells = [(c.coordinate, c.value) for row in ws_t.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith('=')]
    if not cells: raise g.Blocked('no formula found')
    coord = cells[0][0]
    return {'formula': cells[0][1], 'cached': ws_c[coord].value}


def blank_cells(data: bytes) -> dict:
    ws = openpyxl.load_workbook(io.BytesIO(data)).active
    by_openpyxl = [c.value for row in ws.iter_rows(min_col=2, max_col=2, min_row=2) for c in row]
    sheet = CalamineWorkbook.from_filelike(io.BytesIO(data)).get_sheet_by_index(0).to_python(skip_empty_area=False)
    by_calamine = [r[1] for r in sheet[1:]]
    return {'openpyxl': by_openpyxl, 'calamine': by_calamine}

# ---------------------------------------------------------------- P82
def enumerate_workbook_rule(threshold: int, domain: range, invalid: list) -> dict:
    decided = {n: n >= threshold for n in domain}
    refused = []
    for value in invalid:
        if not isinstance(value, int) or isinstance(value, bool) or value < 0: refused.append(repr(value))
        else: raise g.Blocked('an input the domain should have covered was routed to the invalid list: ' + repr(value))
    return {'domain': [domain.start, domain.stop], 'threshold': threshold, 'decided': sum(decided.values()),
            'refused_invalid': refused, 'roster_limit': 'the recorded 18-member roster is a 2026 retrieval, not a verified historical roster (P13)'}

# ---------------------------------------------------------------- P83, P84, P86
def document_blocks(data: bytes) -> dict:
    d = docx.Document(io.BytesIO(data))
    by_api = []
    for block in d.iter_inner_content():
        if isinstance(block, DocxTable): by_api.append(('table', [[c.text for c in r.cells] for r in block.rows]))
        else: by_api.append(('paragraph', block.text))
    body = etree.fromstring(zipfile.ZipFile(io.BytesIO(data)).read('word/document.xml'))
    text_nodes = [t.text for t in body.iter(qn('w:t')) if t.text and t.text.strip()]
    page_breaks = len([b for b in body.iter(qn('w:br')) if b.get(qn('w:type')) == 'page'])
    return {'blocks': by_api, 'text_nodes': text_nodes, 'explicit_page_breaks': page_breaks,
            'page_count_available': hasattr(d, 'page_count')}


def repeating_header_and_unsplit(data: bytes) -> dict:
    body = etree.fromstring(zipfile.ZipFile(io.BytesIO(data)).read('word/document.xml'))
    return {'tblHeader': len(body.findall('.//' + qn('w:tblHeader'))), 'cantSplit': len(body.findall('.//' + qn('w:cantSplit')))}


def action_document(rows: list[list[str]]) -> bytes:
    d = docx.Document(); d.add_heading('Required actions', 1)
    table = d.add_table(rows=0, cols=len(rows[0]))
    for i, row in enumerate(rows):
        cells = table.add_row().cells
        for cell, value in zip(cells, row): cell.text = value
        tr_pr = table.rows[i]._tr.get_or_add_trPr()
        if i == 0: tr_pr.append(etree.SubElement(etree.Element('x'), qn('w:tblHeader')))  # header repeats on each page
        tr_pr.append(etree.SubElement(etree.Element('x'), qn('w:cantSplit')))  # a row is never split across pages
    buf = io.BytesIO(); d.save(buf); return buf.getvalue()


def case_brief_document(cases: list[dict], fields: list[str]) -> bytes:
    d = docx.Document()
    for i, c in enumerate(cases):
        if i: d.add_page_break()  # each case begins on its own page
        d.add_heading(c['case_id'], 1)
        table = d.add_table(rows=0, cols=2)
        for f in fields:
            cells = table.add_row().cells
            cells[0].text = f; cells[1].text = 'not recorded' if c[f] is None else str(c[f])
    buf = io.BytesIO(); d.save(buf); return buf.getvalue()

# ---------------------------------------------------------------- P85
def slide_map(nodes: list[dict], edges: list[tuple[str, str]]) -> dict:
    graph = nx.DiGraph(); graph.add_nodes_from(n['id'] for n in nodes); graph.add_edges_from(edges)
    if set(graph) != {n['id'] for n in nodes}: raise g.Blocked('connector endpoint outside the shape set')
    components = [sorted(c) for c in nx.weakly_connected_components(graph)]
    if not nx.is_directed_acyclic_graph(graph): raise g.Blocked('connector graph has a cycle; no topological order exists')
    order = list(nx.topological_sort(graph))
    prs = pptx.Presentation(); slide = prs.slides.add_slide(prs.slide_layouts[6])
    shapes = {}
    for i, n in enumerate(nodes):
        box = slide.shapes.add_textbox(Inches(1), Inches(0.5 + 0.6 * i), Inches(3), Inches(0.4))
        box.text_frame.text = n['text']; shapes[n['id']] = box
    for a, b in edges:
        connector = slide.shapes.add_connector(1, Emu(0), Emu(0), Emu(0), Emu(0))
        connector.begin_connect(shapes[a], 0); connector.end_connect(shapes[b], 0)
    buf = io.BytesIO(); prs.save(buf)
    return {'components': sorted(components), 'order': order, 'isolated': sorted(c[0] for c in components if len(c) == 1),
            'shapes': len(shapes), 'connectors': len(edges), 'bytes': buf.getvalue(), 'edges_inferred': 0}


def deck_shapes(data: bytes) -> dict:
    prs = pptx.Presentation(io.BytesIO(data)); slide = prs.slides[0]
    texts = [s.text_frame.text for s in slide.shapes if s.has_text_frame]
    connectors = [s for s in slide.shapes if s.shape_type is not None and s.element.tag.endswith('}cxnSp')]
    attached = 0
    for c in connectors:
        xml = etree.tostring(c.element).decode()
        if 'stCxn' in xml and 'endCxn' in xml: attached += 1
    return {'texts': texts, 'connectors': len(connectors), 'attached_connectors': attached}

# ---------------------------------------------------------------- P87
def briefing_deck(categories: list[str], values: list[float]) -> bytes:
    prs = pptx.Presentation(); slide = prs.slides.add_slide(prs.slide_layouts[6])
    data = CategoryChartData(); data.categories = categories; data.add_series('events', values)
    slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(1), Inches(1), Inches(6), Inches(4), data)
    buf = io.BytesIO(); prs.save(buf); return buf.getvalue()


def chart_readback(data: bytes) -> dict:
    prs = pptx.Presentation(io.BytesIO(data)); chart = next(s.chart for s in prs.slides[0].shapes if s.has_chart)
    plot = chart.plots[0]
    return {'categories': list(plot.categories), 'values': list(chart.series[0].values), 'type': str(chart.chart_type)}

# ---------------------------------------------------------------- P88
def external_relationships(package: bytes) -> list[str]:
    out = []
    with zipfile.ZipFile(io.BytesIO(package)) as z:
        for name in z.namelist():
            if not name.endswith('.rels'): continue
            root = etree.fromstring(z.read(name))
            for rel in root:
                if rel.get('TargetMode') == 'External': out.append('%s -> %s' % (name, rel.get('Target')))
    return sorted(out)


def checked_native_package(package: bytes) -> dict:
    external = external_relationships(package)
    if external: raise g.Blocked('native package carries an external relationship: ' + external[0])
    return {'external_relationships': 0}


def libreoffice_export(package: bytes, suffix: str) -> dict:
    if not shutil.which('soffice'): return {'available': False, 'reason': 'soffice not on PATH'}
    tmp = Path(tempfile.mkdtemp()); src = tmp / ('input' + suffix); src.write_bytes(package)
    run = subprocess.run(['soffice', '-env:UserInstallation=file://' + str(tmp / 'profile'), '--headless', '--norestore',
                          '--convert-to', 'pdf', '--outdir', str(tmp), str(src)], capture_output=True, text=True, timeout=600)
    produced = sorted(tmp.glob('*.pdf'))
    if not produced: return {'available': False, 'reason': 'conversion produced no file: ' + (run.stderr or run.stdout).strip()[:120]}
    return {'available': True, 'pages': g8.pdf_text(produced[0].read_bytes())[0]}

# ---------------------------------------------------------------- P89
class ProofEntry(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')
    proof_id: str = Field(pattern=r'^P\d+$')
    title: str = Field(min_length=1)
    line: int = Field(ge=1)

HEADING = re.compile(r'^(P\d+)\s+(.*)$')


def parse_catalog(markdown_text: str) -> dict:
    tokens = MarkdownIt().parse(markdown_text)
    entries = []; seen = set()
    for i, token in enumerate(tokens):
        if token.type != 'heading_open' or token.tag != 'h2': continue
        inline = tokens[i + 1]
        match = HEADING.match(inline.content.strip())
        if not match: continue
        proof_id, title = match.group(1), match.group(2).strip()
        if proof_id in seen: raise g.Blocked('duplicate proof id: ' + proof_id)
        seen.add(proof_id)
        entries.append(ProofEntry(proof_id=proof_id, title=title, line=token.map[0] + 1).model_dump())
    fences = [t for t in tokens if t.type == 'fence']
    return {'entries': entries, 'fences': len(fences),
            'heading_like_lines_inside_fences': sum(len(re.findall(r'(?m)^## P\d+', t.content)) for t in fences)}

C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(81)
def formula_caches_must_be_computed_not_defaulted():
    rows = [('Confirmation of receipt', 1434), ('T02 Check', 1368), ('T03 Adjust', 55)]
    defaulted = authored_workbook(rows, cache='default')
    computed = authored_workbook(rows, cache='computed')
    g.equal(formula_cache(defaulted)['cached'], 0)  # the default cache is a zero nobody computed (P80)
    g.equal(formula_cache(computed)['cached'], 2857)
    g.equal(formula_cache(computed)['formula'], '=SUM(B2:B4)')
    with_missing = authored_workbook(rows, cache='computed', missing=[3])
    cells = blank_cells(with_missing)
    g.equal(cells['openpyxl'][2], None)  # a missing source cell stays blank
    g.equal(cells['calamine'][2], '')
    g.equal(formula_cache(with_missing)['cached'], 2802)  # and is excluded from the computed total
    g.rejects(g.Blocked, lambda: g8.read_two_ways(with_missing, data_rows=4))  # a blank cell reads None through one reader and '' through the other
    return {'default_cache_is_zero_reproduced': True, 'computed_cache_supplied_explicitly': True,
            'missing_cells_stay_blank_not_zero': True, 'blank_cell_breaks_the_two_reader_check_reproduced': "openpyxl None vs calamine ''",
            'conditional_format_and_freeze_panes_are_presentation_only': True}


@case(82)
def rule_explorer_enumerates_valid_and_refuses_invalid():
    out = enumerate_workbook_rule(10, range(0, 19), [-1, 9.5, True, 'ten'])
    g.equal(out['decided'], 9)  # 10..18 inclusive
    g.equal(len(out['refused_invalid']), 4)
    g.require('not a verified historical roster' in out['roster_limit'], 'the roster limit travels with the result')
    g.rejects(g.Blocked, lambda: enumerate_workbook_rule(10, range(0, 19), [12]))  # a valid input must not be filed as invalid
    return {'complete_domain_enumerated': True, 'invalid_inputs_refused': 4, 'roster_limit_recorded': True,
            'domain_is_not_the_input_space': 'integers 0..18 only (P54)'}


@case(83)
def python_docx_cannot_paginate():
    d = docx.Document(); d.add_heading('Policy explanations', 1)
    for i in range(3): d.add_paragraph('meeting tsc-2023-12-0%d present 10' % i)
    d.add_page_break(); d.add_paragraph('second page')
    buf = io.BytesIO(); d.save(buf); data = buf.getvalue()
    out = document_blocks(data)
    g.equal(out['page_count_available'], False)  # python-docx exposes no page count; pagination belongs to a renderer
    g.equal(out['explicit_page_breaks'], 1)  # only the explicit break is knowable from the file
    g.equal([b[1] for b in out['blocks'] if b[0] == 'paragraph'][0], 'Policy explanations')
    g.equal('Policy explanations' in out['text_nodes'], True)
    api_text = [b[1] for b in out['blocks'] if b[0] == 'paragraph' and b[1]]
    g.equal(all(t in out['text_nodes'] for t in api_text), True)  # python-docx and lxml readbacks agree
    return {'no_page_count_api_reproduced': True, 'balanced_pages_claim_needs_a_renderer': True,
            'explicit_breaks_are_the_only_structural_signal': True, 'two_readbacks_agree': True}


@case(84)
def table_formatting_round_trips_in_the_xml():
    rows = [['action', 'actor', 'quote'], ['make', 'agency', 'shall make'], ['have', 'TSC', 'must have']]
    data = action_document(rows)
    fmt = repeating_header_and_unsplit(data)
    g.equal(fmt['tblHeader'], 1); g.equal(fmt['cantSplit'], 3)  # header repeats once, no row may split
    out = document_blocks(data)
    table = [b[1] for b in out['blocks'] if b[0] == 'table'][0]
    g.equal(table, rows)
    for value in ['shall make', 'must have', 'agency']:
        g.equal(value in out['text_nodes'], True)
    return {'repeating_header_written_and_read': True, 'unsplit_rows_written_and_read': True,
            'table_content_preserved': True, 'xml_text_nodes_checked': len(out['text_nodes'])}


@case(85)
def slide_map_infers_no_edges():
    nodes = [{'id': 'n1', 'text': 'share'}, {'id': 'n2', 'text': 'ensure'}, {'id': 'n3', 'text': 'isolated'}]
    edges = [('n1', 'n2')]
    out = slide_map(nodes, edges)
    g.equal(out['components'], [['n1', 'n2'], ['n3']])  # the isolated node is retained as its own component
    g.equal(out['isolated'], ['n3']); g.equal(out['edges_inferred'], 0)
    back = deck_shapes(out['bytes'])
    g.equal(sorted(back['texts']), ['ensure', 'isolated', 'share'])
    g.equal((back['connectors'], back['attached_connectors']), (1, 1))  # the connector is explicitly attached at both ends
    g.rejects(g.Blocked, lambda: slide_map(nodes, edges + [('n2', 'n1')]))  # a cycle has no topological order
    g.rejects(g.Blocked, lambda: slide_map(nodes, edges + [('n1', 'zz')]))
    return {'isolated_nodes_retained': True, 'no_edges_inferred': True, 'connectors_attached_at_both_ends': True,
            'cycle_blocked': True}


@case(86)
def each_case_begins_on_its_own_page():
    fields = ['department', 'deadline', 'outcome']
    cases = [{'case_id': 'case-10011', 'department': 'General', 'deadline': '2011-12-06', 'outcome': 'flagged'},
             {'case_id': 'case-10017', 'department': 'Experts', 'deadline': '2011-12-06', 'outcome': 'unflagged'},
             {'case_id': 'case-10024', 'department': 'General', 'deadline': None, 'outcome': None}]
    data = case_brief_document(cases, fields)
    out = document_blocks(data)
    g.equal(out['explicit_page_breaks'], len(cases) - 1)  # a break between cases, none before the first
    g.equal(out['text_nodes'].count('not recorded'), 2)  # the third case keeps its missing values explicit
    g.equal('None' in out['text_nodes'], False)
    tables = [b[1] for b in out['blocks'] if b[0] == 'table']
    g.equal(len(tables), 3); g.equal(tables[0][0], ['department', 'General'])
    return {'page_break_per_case': True, 'missing_values_explicit': True, 'distinct_case_states_preserved': True,
            'rendered_page_count_still_needs_a_renderer': True}


@case(87)
def chart_values_read_back_from_the_deck():
    categories = ['General', 'Experts', 'Customer contact']; values = [1390.0, 15.0, 29.0]
    data = briefing_deck(categories, values)
    back = chart_readback(data)
    g.equal(back['categories'], categories); g.equal(back['values'], values)
    g.equal(checked_native_package(data), {'external_relationships': 0})
    g.require('COLUMN_CLUSTERED' in back['type'], 'the chart type is the declared one')
    return {'chart_values_round_trip': True, 'categories_preserved': True, 'embedded_workbook_is_native': True,
            'no_external_relationship': True}


@case(88)
def native_packages_carry_no_external_relationship():
    prs = pptx.Presentation(); slide = prs.slides.add_slide(prs.slide_layouts[6])
    box = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1)); box.text_frame.text = 'clean'
    clean = io.BytesIO(); prs.save(clean); clean_bytes = clean.getvalue()
    g.equal(external_relationships(clean_bytes), [])
    run = box.text_frame.paragraphs[0].runs[0]
    run.hyperlink.address = 'https://example.com/x'  # the authoring API adds an external relationship without complaint
    linked = io.BytesIO(); prs.save(linked); linked_bytes = linked.getvalue()
    external = external_relationships(linked_bytes)
    g.equal(len(external), 1); g.require('https://example.com/x' in external[0], 'the external target is named')
    g.rejects(g.Blocked, lambda: checked_native_package(linked_bytes))
    export = libreoffice_export(clean_bytes, '.pptx')
    return {'external_relationship_created_silently_reproduced': True, 'package_scan_blocks_it': True,
            'libreoffice_export': export, 'native_render_outside_python_audit_scope': True}


@case(89)
def a_heading_inside_a_fence_is_not_a_proof():
    source = ('# Proofs\n\n## P1  procedures -> facts\n\ntext\n\n```\n## P999  not a proof\n```\n\n'
              '## P2  facts -> ordered steps\n\nmore\n')
    out = parse_catalog(source)
    g.equal([e['proof_id'] for e in out['entries']], ['P1', 'P2'])  # the fenced heading never becomes a proof
    g.equal(out['heading_like_lines_inside_fences'], 1); g.equal(out['fences'], 1)
    g.equal(out['entries'][0]['title'], 'procedures -> facts')
    g.rejects(g.Blocked, lambda: parse_catalog(source + '\n## P1  duplicate\n'))
    g.rejects(ValidationError, lambda: ProofEntry.model_validate({'proof_id': '1', 'title': 'x', 'line': 1}))
    return {'fenced_heading_excluded_reproduced': True, 'ids_unique': True, 'titles_retained_verbatim': True,
            'snapshot_does_not_claim_current_artifact_integrity': True}


@case(90)
def proof_explorer_renders_the_typed_catalog():
    source = '# Proofs\n\n## P1  procedures -> facts\n\n## P2  facts -> ordered steps\n'
    catalog = parse_catalog(source)['entries']
    rows = [{'proof_id': e['proof_id'], 'title': e['title'], 'line': str(e['line'])} for e in catalog]
    page = g8.CATALOG.render(title='Proof explorer', fields=['proof_id', 'title', 'line'], rows=rows)
    g.equal('procedures -&gt; facts' in page, True)  # the arrow in a title is escaped, not interpreted
    if g8.jsdom_available():
        dom = g8.run_dom(page)
        g.equal([r[0] for r in dom['rows']], ['P1', 'P2'])
        g.equal(dom['externalRequests'], 0); g.equal(dom['lang'], 'en-US')
    return {'catalog_rendered_from_typed_entries': True, 'titles_escaped': True, 'dom_checked': g8.jsdom_available(),
            'print_states_not_rebuilt': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['pydantic', 'python-docx', 'python-pptx', 'XlsxWriter', 'openpyxl', 'python-calamine', 'networkx', 'lxml', 'markdown-it-py', 'deepdiff']
    here = Path(__file__).resolve().parent
    return {'scope': 'Bounded authored handoff fixtures and reproduced library defaults; the original P81-P90 chains and their artifacts were not rerun. The formulas engine and a working LibreOffice import filter were not available, and those limits are recorded rather than claimed.',
            'test_cases': len(rows), 'passed': sum(r['status'] == 'passed' for r in rows), 'failed': sum(r['status'] == 'failed' for r in rows),
            'assertions': g.ASSERTIONS, 'full_chains_executed': 0, 'network_calls': 0, 'business_actions': 0,
            'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256': {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in ['handoff_guards_v1.py', 'handoff_guards_v8.py']},
            'library_versions': {n: importlib.metadata.version(n) for n in packages}, 'results': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True); p.add_argument('--jsdom-dir', default=os.environ.get('JSDOM_DIR', ''))
    args = p.parse_args(); os.environ['JSDOM_DIR'] = args.jsdom_dir; g8.JSDOM_DIR = args.jsdom_dir
    result = run(); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ['test_cases', 'passed', 'failed', 'assertions']}))
    if result['failed']:
        print('\n'.join(r['error'] for r in result['results'] if r['error'])); raise SystemExit(1)
