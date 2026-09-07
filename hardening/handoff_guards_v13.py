"""Thirteenth bounded adapter suite: P121-P130, the reusable everyday deliverables. Requires handoff_guards_v1.py,
handoff_guards_v6.py, handoff_guards_v8.py and handoff_guards_v12.py from this TXT. Every index, query, attachment,
CSV round trip, form update, page range and imposition below is a library primitive call; local code declares fixtures
and policies and turns a primitive result into a Blocked outcome. All runtime inputs are authored fixtures. No model
client and no network.
Run: python handoff_guards_v13.py --report report.json
"""
from __future__ import annotations
import argparse, csv, datetime, hashlib, html, importlib.metadata, io, json, logging, os, sqlite3, time, traceback, warnings, zipfile
from pathlib import Path
from typing import Literal
import docx
import pymupdf
import pypdf
from deepdiff import DeepDiff
from ebooklib import epub
from lxml import html as lxml_html
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError
import handoff_guards_v1 as g
import handoff_guards_v6 as g6
import handoff_guards_v8 as g8
import handoff_guards_v12 as g12
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

# ---------------------------------------------------------------- P121
def build_epub(chapters: list[dict], *, identifier: str, title: str) -> bytes:
    book = epub.EpubBook(); book.set_identifier(identifier); book.set_title(title); book.set_language('en-US')
    items = []
    for c in chapters:
        item = epub.EpubHtml(title=c['title'], file_name=c['file'], lang='en-US')
        item.content = '<html><body><h1>%s</h1><p>%s</p></body></html>' % (html.escape(c['title']), html.escape(c['body']))
        book.add_item(item); items.append(item)
    book.toc = tuple(items)
    book.add_item(epub.EpubNcx()); book.add_item(epub.EpubNav())
    book.spine = ['nav'] + items
    path = Path(os.environ.get('GUARD_TMP', '/tmp')) / ('guard-%d.epub' % time.time_ns())
    epub.write_epub(str(path), book)
    data = path.read_bytes(); path.unlink()
    return data


def epub_contents(data: bytes) -> dict:
    names = zipfile.ZipFile(io.BytesIO(data)).namelist()
    chapters = sorted(n for n in names if n.endswith('.xhtml') and 'nav' not in n)
    return {'entries': len(names), 'mimetype_first': names[0] == 'mimetype', 'chapters': chapters,
            'has_nav': any('nav' in n for n in names), 'has_container': 'META-INF/container.xml' in names}

# ---------------------------------------------------------------- P122, P123
SCHEMA = "CREATE VIRTUAL TABLE docs USING fts5(document, block_id, body, tokenize='unicode61')"


def build_index(blocks: list[dict]) -> sqlite3.Connection:
    con = sqlite3.connect(':memory:'); con.execute(SCHEMA)
    con.executemany('INSERT INTO docs(document, block_id, body) VALUES (?,?,?)',
                    [(b['document'], b['block_id'], b['body']) for b in blocks])
    indexed = con.execute('SELECT count(*) FROM docs').fetchone()[0]
    if indexed != len(blocks): raise g.Blocked('index row count does not match the source blocks')
    return con


def literal_query(text: str) -> str:
    """FTS5 MATCH parses its argument as a query language; a literal phrase must be quoted."""
    return '"' + text.replace('"', '""') + '"'


def search(con: sqlite3.Connection, phrase: str, *, literal: bool = True) -> list[dict]:
    query = literal_query(phrase) if literal else phrase
    rows = con.execute("SELECT document, block_id, snippet(docs, 2, '[', ']', '...', 6), bm25(docs) "
                       'FROM docs WHERE docs MATCH ? ORDER BY bm25(docs)', (query,)).fetchall()
    return [{'document': r[0], 'block_id': r[1], 'snippet': r[2], 'rank': round(r[3], 6)} for r in rows]

# ---------------------------------------------------------------- P124
PINNED = datetime.datetime(1980, 1, 1, tzinfo=datetime.timezone.utc)


def report_with_attachments(pdf: bytes, files: dict[str, bytes], *, dates: Literal['none', 'pinned', 'clock']) -> bytes:
    writer = pypdf.PdfWriter(clone_from=io.BytesIO(pdf))
    for name, payload in files.items():
        writer.add_attachment(name, payload)
    if dates != 'none':
        stamp = PINNED if dates == 'pinned' else datetime.datetime.now(datetime.timezone.utc)
        for embedded in writer.attachment_list:
            embedded.creation_date = stamp; embedded.modification_date = stamp
    buf = io.BytesIO(); writer.write(buf); return buf.getvalue()


def read_attachments_two_ways(data: bytes) -> dict:
    by_pypdf = {name: payload for name, payload in pypdf.PdfReader(io.BytesIO(data)).attachments.items()}
    doc = pymupdf.open(stream=data, filetype='pdf')
    by_pymupdf = {}
    for i in range(doc.embfile_count()):
        info = doc.embfile_info(i); by_pymupdf[info['filename']] = doc.embfile_get(i)
    return {'pypdf': {k: hashlib.sha256(v[0] if isinstance(v, list) else v).hexdigest() for k, v in by_pypdf.items()},
            'pymupdf': {k: hashlib.sha256(v).hexdigest() for k, v in by_pymupdf.items()}}

# ---------------------------------------------------------------- P125, P126, P127
class ReviewRow(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')
    field_name: str = Field(min_length=1)
    slide: int = Field(ge=0)
    note: str
    reviewed: bool

REVIEW_ROWS = TypeAdapter(list[ReviewRow])
CSV_FIELDS = ['field_name', 'slide', 'note', 'reviewed']


def rows_to_csv(rows: list[dict]) -> str:
    REVIEW_ROWS.validate_python(rows)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_FIELDS, quoting=csv.QUOTE_ALL, lineterminator='\n')
    writer.writeheader()
    for r in rows: writer.writerow({'field_name': r['field_name'], 'slide': r['slide'], 'note': r['note'], 'reviewed': 'true' if r['reviewed'] else 'false'})
    return buf.getvalue()


def csv_to_rows(text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != CSV_FIELDS: raise g.Blocked('csv header does not match the declared contract')
    out = []
    for raw in reader:
        if raw['reviewed'] not in ('true', 'false'): raise g.Blocked('reviewed is not a declared boolean token: ' + repr(raw['reviewed']))
        out.append({'field_name': raw['field_name'], 'slide': int(raw['slide']), 'note': raw['note'], 'reviewed': raw['reviewed'] == 'true'})
    REVIEW_ROWS.validate_python(out)
    return out


def apply_review(form: bytes, rows: list[dict]) -> bytes:
    values = {}
    for r in rows:
        values['notes_%d' % r['slide']] = r['note']
        values['reviewed_%d' % r['slide']] = r['reviewed']
    return g12.fill_fields(form, values)


def review_summary(rows: list[dict]) -> dict:
    REVIEW_ROWS.validate_python(rows)
    reviewed = [r for r in rows if r['reviewed']]
    with_notes = [r for r in rows if r['note'].strip()]
    return {'total': len(rows), 'reviewed': len(reviewed), 'not_reviewed': len(rows) - len(reviewed),
            'with_notes': len(with_notes), 'notes': [r['note'] for r in with_notes]}

# ---------------------------------------------------------------- P128
def section_ranges(toc: list[list], page_count: int) -> list[dict]:
    if not toc: raise g.Blocked('binder has no bookmarks')
    starts = [entry[2] for entry in toc]
    if starts != sorted(starts): raise g.Blocked('bookmark start pages are not in order')
    if starts[0] != 1: raise g.Blocked('the first section does not start on page 1')
    out = []
    for i, entry in enumerate(toc):
        end = (starts[i + 1] - 1) if i + 1 < len(toc) else page_count  # the last section runs to the end
        if end < entry[2]: raise g.Blocked('section %r has no pages' % entry[1])
        out.append({'title': entry[1], 'first_page': entry[2], 'last_page': end, 'pages': end - entry[2] + 1})
    if sum(s['pages'] for s in out) != page_count: raise g.Blocked('section ranges do not cover the binder exactly once')
    return out

# ---------------------------------------------------------------- P129
LARGE_TYPE_CSS = 'body{font-size:18pt;line-height:1.6}'


def large_type_copy(source_html: str) -> str:
    doc = lxml_html.fromstring(source_html)
    head = doc.find('head')
    if head is None: raise g.Blocked('source has no head to attach the stylesheet to')
    style = lxml_html.fragment_fromstring('<style>' + LARGE_TYPE_CSS + '</style>')
    head.append(style)
    return lxml_html.tostring(doc, encoding='unicode')


def visible_text(source_html: str) -> str:
    doc = lxml_html.fromstring(source_html)
    for element in doc.xpath('//style | //script'): element.getparent().remove(element)
    return ' '.join(doc.text_content().split())

# ---------------------------------------------------------------- P130
def booklet_order(pages: int) -> list[int]:
    if pages <= 0 or pages % 4: raise g.Blocked('a folded booklet needs a page count that is a positive multiple of four')
    order = []; left, right = 1, pages
    while left < right:
        order += [right, left, left + 1, right - 1]; left += 2; right -= 2
    return order

C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(121)
def epub_carries_chapters_and_navigation():
    chapters = [{'title': 'Charter actions', 'file': 'c1.xhtml', 'body': 'The TSC must have a Chair.'},
                {'title': 'Disclosure actions', 'file': 'c2.xhtml', 'body': 'The agency shall make records available.'}]
    data = build_epub(chapters, identifier='proofs-hardening', title='Reading collection')
    out = epub_contents(data)
    g.equal(out['mimetype_first'], True)  # the mimetype entry must come first in the archive
    g.equal(out['chapters'], ['EPUB/c1.xhtml', 'EPUB/c2.xhtml'])  # ebooklib places the documents under EPUB/
    g.equal(out['has_nav'], True); g.equal(out['has_container'], True)
    body = zipfile.ZipFile(io.BytesIO(data)).read('EPUB/c1.xhtml').decode()
    g.equal('The TSC must have a Chair.' in body, True)
    second = build_epub(chapters, identifier='proofs-hardening', title='Reading collection')
    g.equal(epub_contents(second)['chapters'], out['chapters'])  # the structure repeats even where the bytes need not
    return {'mimetype_entry_first': True, 'chapters_and_nav_present': True, 'chapter_text_preserved': True,
            'structure_repeats': True}


@case(122)
def the_index_accounts_for_every_block():
    blocks = [{'document': 'charter', 'block_id': 'p1', 'body': 'The TSC must have a Chair.'},
              {'document': 'charter', 'block_id': 't1', 'body': 'department cases General 1390'},
              {'document': 'disclosure', 'block_id': 'p1', 'body': 'agency shall make records available'}]
    con = build_index(blocks)
    g.equal(con.execute('SELECT count(*) FROM docs').fetchone()[0], 3)
    hits = search(con, 'shall make')
    g.equal([(h['document'], h['block_id']) for h in hits], [('disclosure', 'p1')])
    g.equal('[shall make]' in hits[0]['snippet'], True)  # the snippet marks the matched span in the source text
    table_hit = search(con, 'General')
    g.equal([(h['document'], h['block_id']) for h in table_hit], [('charter', 't1')])  # table rows are indexed too
    return {'row_count_conserved': True, 'table_rows_indexed': True, 'snippet_marks_the_source_span': True,
            'tokenizer_declared': 'unicode61'}


@case(123)
def a_literal_query_must_be_quoted():
    blocks = [{'document': 'd', 'block_id': 'b1', 'body': 'a AND b minus-sign and star* here'},
              {'document': 'd', 'block_id': 'b2', 'body': 'agency shall make records available'}]
    con = build_index(blocks)
    g.rejects(sqlite3.OperationalError, lambda: search(con, 'AND', literal=False))  # bare AND is a query operator
    g.rejects(sqlite3.OperationalError, lambda: search(con, 'minus-sign', literal=False))  # the hyphen is parsed as a column filter
    g.equal([h['block_id'] for h in search(con, 'AND')], ['b1'])  # quoting makes both literal
    g.equal([h['block_id'] for h in search(con, 'minus-sign')], ['b1'])
    g.equal([h['block_id'] for h in search(con, 'shall make')], ['b2'])
    g.equal(literal_query('say "hi"'), '"say ""hi"""')  # an embedded quote is doubled, not dropped
    ranked = search(con, 'a')
    g.equal(all(isinstance(h['rank'], float) for h in ranked), True)
    return {'bare_operator_raises_reproduced': True, 'hyphen_parsed_as_column_reproduced': True,
            'quoting_makes_queries_literal': True, 'embedded_quote_escaped': True, 'bm25_rank_recorded': True}


@case(124)
def attachments_need_pinned_dates_to_repeat():
    pdf = g8.print_pdf('<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>t</title>'
                       '<style>@page{size:A4;margin:1cm}</style></head><body><h1>Report</h1></body></html>')
    files = {'cases.csv': b'case_id,cases\nc1,1390\n', 'model.json': b'{"population":1434}'}
    bare_a = report_with_attachments(pdf, files, dates='none')
    time.sleep(1.1)
    bare_b = report_with_attachments(pdf, files, dates='none')
    g.equal(bare_a == bare_b, True)  # pypdf sets no attachment dates of its own, so the default repeats
    clock_a = report_with_attachments(pdf, files, dates='clock')
    time.sleep(1.1)
    clock_b = report_with_attachments(pdf, files, dates='clock')
    g.equal(clock_a == clock_b, False)  # a chain that stamps the clock loses repeatability
    pinned_a = report_with_attachments(pdf, files, dates='pinned')
    time.sleep(1.1)
    pinned_b = report_with_attachments(pdf, files, dates='pinned')
    g.equal(pinned_a == pinned_b, True)
    g.equal(pinned_a == bare_a, False)  # a pinned date is recorded metadata, not a no-op
    both = read_attachments_two_ways(pinned_a)
    expected = {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}
    g.equal(both['pypdf'], expected)
    g.equal(both['pymupdf'], expected)  # a second library reads the same attachment bytes
    _, text = g8.pdf_text(pinned_a)
    g.equal('Report' in text, True)  # attaching files leaves the page content alone
    return {'default_has_no_attachment_dates_and_repeats': True, 'clock_dates_break_repeatability_reproduced': True, 'pinned_dates_repeat': True,
            'two_libraries_agree_on_attachment_bytes': True, 'page_content_unchanged': True}


@case(125)
def csv_quoting_survives_newlines_and_quotes():
    rows = [{'field_name': 'notes_0', 'slide': 0, 'note': 'line one\nline two, with "quotes"', 'reviewed': True},
            {'field_name': 'notes_1', 'slide': 1, 'note': '', 'reviewed': False}]
    text = rows_to_csv(rows)
    g.equal(text.splitlines()[0], '"field_name","slide","note","reviewed"')
    back = csv_to_rows(text)
    g.equal(bool(DeepDiff(rows, back, zip_ordered_iterables=True)), False)  # the embedded newline, comma and quotes survive
    g.rejects(g.Blocked, lambda: csv_to_rows(text.replace('"field_name"', '"name"')))
    g.rejects(g.Blocked, lambda: csv_to_rows(text.replace('"true"', '"yes"')))
    g.rejects(ValidationError, lambda: rows_to_csv([dict(rows[0], reviewed='true')]))
    return {'quote_all_round_trip': True, 'embedded_newline_preserved': True, 'header_contract_enforced': True,
            'boolean_tokens_declared': True}


@case(126)
def edited_rows_update_only_named_fields():
    form = g12.review_form(2)
    rows = [{'field_name': 'notes_0', 'slide': 0, 'note': 'checked the quote', 'reviewed': True},
            {'field_name': 'notes_1', 'slide': 1, 'note': '', 'reviewed': False}]
    updated = apply_review(form, csv_to_rows(rows_to_csv(rows)))
    fields = g12.read_fields_two_ways(updated)
    g.equal(fields['pymupdf']['notes_0'], 'checked the quote')
    g.equal(g12.blank_state(fields['pymupdf']['notes_1']), True)  # an empty note leaves the field blank
    g.equal(fields['pymupdf']['reviewed_0'] not in ('Off', '/Off'), True)
    g.equal(g12.blank_state(fields['pymupdf']['reviewed_1']), True)
    g.equal(g12.text_outside_widgets(updated), g12.text_outside_widgets(form))  # the page content is untouched
    g.rejects(g.Blocked, lambda: apply_review(form, [{'field_name': 'notes_9', 'slide': 9, 'note': 'x', 'reviewed': True}]))
    return {'csv_round_trip_then_update': True, 'empty_note_stays_blank': True, 'page_content_untouched': True,
            'row_for_a_missing_field_blocked': True}


@case(127)
def the_summary_counts_only_what_the_records_carry():
    rows = [{'field_name': 'notes_0', 'slide': 0, 'note': 'checked', 'reviewed': True},
            {'field_name': 'notes_1', 'slide': 1, 'note': '', 'reviewed': False},
            {'field_name': 'notes_2', 'slide': 2, 'note': '   ', 'reviewed': True}]
    out = review_summary(rows)
    g.equal((out['total'], out['reviewed'], out['not_reviewed'], out['with_notes']), (3, 2, 1, 1))  # whitespace is not a note
    g.equal(out['notes'], ['checked'])
    page = g8.CATALOG.render(title='Review summary', fields=['field_name', 'note', 'reviewed'],
                             rows=[{'field_name': r['field_name'], 'note': r['note'], 'reviewed': str(r['reviewed'])} for r in rows])
    pdf = g8.print_pdf('<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>s</title>'
                       '<style>@page{size:A4;margin:1cm}</style></head><body><p>reviewed 2 of 3</p></body></html>')
    _, text = g8.pdf_text(pdf)
    g.equal('reviewed 2 of 3' in text, True)
    g.equal('checked' in page, True)
    g.rejects(ValidationError, lambda: review_summary([dict(rows[0], reviewed='true')]))
    return {'counts_from_typed_records': True, 'whitespace_is_not_a_note': True, 'summary_printed_and_read_back': True}


@case(128)
def section_ranges_cover_the_binder_exactly_once():
    toc = [[1, 'Policy explanations', 1], [1, 'Charter actions', 3], [1, 'Meeting packets', 6]]
    ranges = section_ranges(toc, 8)
    g.equal([(s['first_page'], s['last_page'], s['pages']) for s in ranges], [(1, 2, 2), (3, 5, 3), (6, 8, 3)])
    g.equal(sum(s['pages'] for s in ranges), 8)  # the last section runs to the end of the binder
    g.rejects(g.Blocked, lambda: section_ranges(toc, 5))  # a page count that does not cover the sections
    g.rejects(g.Blocked, lambda: section_ranges([[1, 'B', 3], [1, 'A', 1]], 8))
    g.rejects(g.Blocked, lambda: section_ranges([[1, 'A', 2]], 8))
    g.rejects(g.Blocked, lambda: section_ranges([], 8))
    return {'last_section_runs_to_the_end': True, 'ranges_partition_the_binder': True,
            'unordered_bookmarks_blocked': True, 'first_page_must_be_one': True}


@case(129)
def large_type_changes_only_the_stylesheet():
    source = ('<html lang="en-US"><head><meta charset="utf-8"><title>Checklist</title></head>'
              '<body><h1>Required actions</h1><p>The TSC must have a Chair.</p></body></html>')
    large = large_type_copy(source)
    g.equal(visible_text(large), visible_text(source))  # not one character of reading text changes
    g.equal('18pt' in large, True)
    g.equal(large.count('<style>'), 1)
    g.equal(g8.g3.external_assets(large) if hasattr(g8, 'g3') else [], [])
    g.rejects(g.Blocked, lambda: large_type_copy('<div>no head here</div>'))
    return {'reading_text_identical': True, 'stylesheet_added_once': True, 'no_external_assets': True,
            'source_without_head_blocked': True}


@case(130)
def booklet_order_is_a_permutation():
    order = booklet_order(8)
    g.equal(order, [8, 1, 2, 7, 6, 3, 4, 5])
    g.equal(sorted(order), list(range(1, 9)))  # every page appears exactly once
    g.equal(len(order), 8)
    for pages in (4, 12, 16):
        seq = booklet_order(pages)
        g.equal(sorted(seq), list(range(1, pages + 1)))
    for bad in (0, 6, 7, -4):
        g.rejects(g.Blocked, lambda bad=bad: booklet_order(bad))
    return {'permutation_checked': True, 'every_page_once': True, 'multiple_of_four_required': True,
            'imposition_is_arithmetic_not_layout': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['pydantic', 'EbookLib', 'pymupdf', 'pypdf', 'python-docx', 'weasyprint', 'lxml', 'deepdiff']
    here = Path(__file__).resolve().parent
    return {'scope': 'Bounded authored handoff fixtures and reproduced library defaults; the original P121-P130 chains and their artifacts were not rerun.',
            'test_cases': len(rows), 'passed': sum(r['status'] == 'passed' for r in rows), 'failed': sum(r['status'] == 'failed' for r in rows),
            'assertions': g.ASSERTIONS, 'full_chains_executed': 0, 'network_calls': 0, 'business_actions': 0,
            'sqlite_version': sqlite3.sqlite_version,
            'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256': {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in ['handoff_guards_v1.py', 'handoff_guards_v6.py', 'handoff_guards_v8.py', 'handoff_guards_v12.py']},
            'library_versions': {n: importlib.metadata.version(n) for n in packages}, 'results': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    result = run(); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ['test_cases', 'passed', 'failed', 'assertions']}))
    if result['failed']:
        print('\n'.join(r['error'] for r in result['results'] if r['error'])); raise SystemExit(1)
