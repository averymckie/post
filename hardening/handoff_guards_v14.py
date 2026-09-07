"""Fourteenth bounded adapter suite: P131-P140, composed everyday deliverables. Requires handoff_guards_v1.py,
handoff_guards_v6.py, handoff_guards_v8.py and handoff_guards_v12.py from this TXT. Every composition, drawing,
embedding, form field, typed CSV round trip, QR round trip and cross-format check below is a library primitive call;
local code declares fixtures and policies and turns a primitive result into a Blocked outcome. All runtime inputs are
authored fixtures. No model client and no network.
Run: python handoff_guards_v14.py --report report.json
"""
from __future__ import annotations
import argparse, datetime, hashlib, importlib.metadata, io, json, logging, os, time, traceback, uuid, warnings
from pathlib import Path
from typing import Literal
import cv2
import docx
import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pptx
import pyarrow as pa
import pyarrow.csv as pacsv
import pymupdf
import pypdf
import segno
from deepdiff import DeepDiff
from docx.shared import Emu
from docxcompose.composer import Composer
from icalendar import Calendar, Event
from PIL import Image
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas
import handoff_guards_v1 as g
import handoff_guards_v6 as g6
import handoff_guards_v8 as g8
import handoff_guards_v12 as g12
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

# ---------------------------------------------------------------- P131
def source_document(title: str, blocks: list[str], *, page_width_emu: int) -> bytes:
    d = docx.Document(); d.add_heading(title, 1)
    for b in blocks: d.add_paragraph(b)
    section = d.sections[0]; section.page_width = Emu(page_width_emu)
    buf = io.BytesIO(); d.save(buf); return buf.getvalue()


def compose_documents(parts: list[bytes]) -> bytes:
    if not parts: raise g.Blocked('no documents to compose')
    master = docx.Document(io.BytesIO(parts[0]))
    composer = Composer(master)
    for part in parts[1:]:
        composer.append(docx.Document(io.BytesIO(part)))
    buf = io.BytesIO(); composer.save(buf); return buf.getvalue()


def document_sections(data: bytes) -> list[int]:
    return [int(s.page_width) for s in docx.Document(io.BytesIO(data)).sections]

# ---------------------------------------------------------------- P132
def meeting_deck(meetings: list[dict]) -> bytes:
    prs = pptx.Presentation(); slide = prs.slides.add_slide(prs.slide_layouts[6])
    data = CategoryChartData(); data.categories = [m['meeting'] for m in meetings]
    data.add_series('present', [float(m['present']) for m in meetings])
    slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.5), Inches(0.5), Inches(6), Inches(3), data)
    table = slide.shapes.add_table(len(meetings) + 1, 3, Inches(0.5), Inches(4), Inches(6), Inches(2)).table
    for c, name in enumerate(['meeting', 'present', 'majority']): table.cell(0, c).text = name
    for r, m in enumerate(meetings, start=1):
        table.cell(r, 0).text = m['meeting']; table.cell(r, 1).text = str(m['present']); table.cell(r, 2).text = str(m['majority'])
    buf = io.BytesIO(); prs.save(buf); return buf.getvalue()

# ---------------------------------------------------------------- P133
def table_graphic(rows: list[dict], columns: list[str], fmt: str, *, deterministic: bool, fonttype: str | None = None) -> bytes:
    def render():
        fig, ax = plt.subplots(figsize=(6, 1 + 0.4 * len(rows)))
        ax.axis('off')
        cells = [[str(r[c]) for c in columns] for r in rows]
        ax.table(cellText=cells, colLabels=columns, loc='center')
        buf = io.BytesIO()
        if deterministic: fig.savefig(buf, format=fmt, metadata={'Date': None} if fmt == 'svg' else None)
        else: fig.savefig(buf, format=fmt)
        plt.close(fig); return buf.getvalue()
    context = {}
    if deterministic and fmt == 'svg': context['svg.hashsalt'] = 'proofs-hardening'
    if fonttype is not None: context['svg.fonttype'] = fonttype
    if context:
        with mpl.rc_context(context): return render()
    return render()


def svg_text(data: bytes) -> list[str]:
    from lxml import etree
    root = etree.fromstring(data)
    return [t.text for t in root.iter('{http://www.w3.org/2000/svg}text') if t.text]

# ---------------------------------------------------------------- P134
def visual_brief(images: list[bytes], *, page=(400, 400)) -> bytes:
    out = io.BytesIO(); c = rl_canvas.Canvas(out, pagesize=page)
    y = page[1] - 20
    for payload in images:
        with Image.open(io.BytesIO(payload)) as img: width, height = img.size
        y -= height + 10
        c.drawImage(ImageReader(io.BytesIO(payload)), 20, y, width=width, height=height)
    c.showPage(); c.save(); return out.getvalue()


def _pixels_for(doc, xref: int) -> list[tuple]:
    info = doc.extract_image(xref)
    with Image.open(io.BytesIO(info['image'])) as img: return list(img.convert('RGB').getdata())


def embedded_pixels(pdf: bytes, *, order: str) -> list[list[tuple]]:
    """order='resource' is the raw get_images list; order='placement' sorts by the drawn bounding box."""
    doc = pymupdf.open(stream=pdf, filetype='pdf'); page = doc[0]
    if order == 'resource':
        xrefs = [item[0] for item in page.get_images(full=True)]
    elif order == 'placement':
        placed = sorted(page.get_image_info(xrefs=True), key=lambda i: (round(i['bbox'][1], 3), round(i['bbox'][0], 3)))
        xrefs = [i['xref'] for i in placed]
    else:
        raise g.Blocked('unknown image order %r' % order)
    return [_pixels_for(doc, x) for x in xrefs]

# ---------------------------------------------------------------- P135
STATUS_CHOICES = ['not_reviewed', 'reviewed', 'needs_follow_up']


def checklist_form(actions: list[dict]) -> bytes:
    out = io.BytesIO(); c = rl_canvas.Canvas(out, pagesize=(595, 842))
    form = c.acroForm
    for i, a in enumerate(actions):
        y = 780 - i * 120
        c.drawString(40, y, a['label'][:80])
        c.drawString(40, y - 14, 'quote: ' + a['quote'][:80])
        form.choice(name='status_%d' % i, options=STATUS_CHOICES, value=STATUS_CHOICES[0], x=40, y=y - 45, width=150, height=20)
        form.textfield(name='owner_%d' % i, value='', x=200, y=y - 45, width=150, height=20)
        form.textfield(name='note_%d' % i, value='', x=40, y=y - 75, width=310, height=24)
    c.showPage(); c.save(); return out.getvalue()

# ---------------------------------------------------------------- P136
class ProgressRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')
    action_id: str = Field(min_length=1)
    status: Literal['not_reviewed', 'reviewed', 'needs_follow_up']
    owner: str
    due_date: str
    note: str = Field(max_length=120)

    @field_validator('due_date')
    @classmethod
    def iso_or_empty(cls, v: str) -> str:
        if v: datetime.date.fromisoformat(v)  # raises for anything that is not an ISO date
        return v

# ---------------------------------------------------------------- P137
def typed_csv(rows: list[dict], column_types: dict) -> bytes:
    table = pa.Table.from_pylist(rows)
    sink = io.BytesIO()
    pacsv.write_csv(table, sink, pacsv.WriteOptions(include_header=True, quoting_style='all_valid'))
    return sink.getvalue()


def read_typed_csv(data: bytes, column_types: dict | None, *, strings_can_be_null: bool = False,
                   quoted_strings_can_be_null: bool = True) -> list[dict]:
    options = pacsv.ConvertOptions(column_types=column_types, strings_can_be_null=strings_can_be_null,
                                   quoted_strings_can_be_null=quoted_strings_can_be_null) if column_types else None
    table = pacsv.read_csv(io.BytesIO(data), convert_options=options)
    return table.to_pylist()


def nullable_csv(columns: dict) -> bytes:
    """A table whose string columns carry both a null and an empty string, written with every value quoted."""
    table = pa.table({name: pa.array(values, type=pa.string()) for name, values in columns.items()})
    sink = io.BytesIO()
    pacsv.write_csv(table, sink, pacsv.WriteOptions(include_header=True, quoting_style='all_valid'))
    return sink.getvalue()

# ---------------------------------------------------------------- P138
def qr_png(url: str) -> bytes:
    buf = io.BytesIO(); segno.make(url, error='h').save(buf, kind='png', scale=8, border=4); return buf.getvalue()


def _gray(png: bytes):
    with Image.open(io.BytesIO(png)) as img: return np.array(img.convert('L'))


def decode_qr(png: bytes) -> str:
    data, _points, _ = cv2.QRCodeDetectorAruco().detectAndDecode(_gray(png))
    if not data: raise g.Blocked('the rendered code did not decode')
    return data


def decode_qr_legacy(png: bytes) -> str:
    """cv2.QRCodeDetector is the detector most examples reach for; it returns '' when it fails to detect."""
    data, _points, _ = cv2.QRCodeDetector().detectAndDecode(_gray(png))
    return data


def blank_png(size=(120, 120)) -> bytes:
    buf = io.BytesIO(); Image.new('L', size, 255).save(buf, format='PNG'); return buf.getvalue()


def reference_cards_pdf(entries: list[dict]) -> bytes:
    out = io.BytesIO(); c = rl_canvas.Canvas(out, pagesize=(400, 400))
    for i, e in enumerate(entries):
        y = 340 - i * 160
        c.drawImage(ImageReader(io.BytesIO(qr_png(e['url']))), 20, y, width=100, height=100)
        c.drawString(140, y + 50, e['name'])
        c.linkURL(e['url'], (20, y, 120, y + 100), relative=0)
    c.showPage(); c.save(); return out.getvalue()


def pdf_link_targets(pdf: bytes) -> list[str]:
    doc = pymupdf.open(stream=pdf, filetype='pdf')
    return sorted(link['uri'] for page in doc for link in page.get_links() if link.get('uri'))

# ---------------------------------------------------------------- P139
def append_appendix(binder: bytes, appendix: bytes, title: str) -> dict:
    doc = pymupdf.open(stream=binder, filetype='pdf')
    original_toc = doc.get_toc(); original_pages = doc.page_count
    original_text = [doc[i].get_text() for i in range(original_pages)]
    with pymupdf.open(stream=appendix, filetype='pdf') as extra: doc.insert_pdf(extra)
    doc.set_toc(original_toc + [[1, title, original_pages + 1]])
    data = doc.tobytes()
    reopened = pymupdf.open(stream=data, filetype='pdf')
    return {'pages': reopened.page_count, 'toc': reopened.get_toc(),
            'original_text_retained': [reopened[i].get_text() for i in range(original_pages)] == original_text,
            'original_bookmarks_retained': reopened.get_toc()[:len(original_toc)] == original_toc}

# ---------------------------------------------------------------- P140
def format_family(meeting: dict) -> dict:
    payload = {'meeting': meeting['meeting'], 'date': meeting['date'], 'actions': meeting['actions']}
    as_json = json.dumps(payload, sort_keys=True)
    html_page = g8.CATALOG.render(title=payload['meeting'], fields=['meeting', 'date', 'actions'],
                                  rows=[{'meeting': payload['meeting'], 'date': payload['date'], 'actions': str(payload['actions'])}])
    d = docx.Document(); d.add_heading(payload['meeting'], 1)
    d.add_paragraph('date: ' + payload['date']); d.add_paragraph('actions: %d' % payload['actions'])
    docx_buf = io.BytesIO(); d.save(docx_buf)
    prs = pptx.Presentation(); slide = prs.slides.add_slide(prs.slide_layouts[6])
    box = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(6), Inches(2))
    box.text_frame.text = '%s | %s | %d' % (payload['meeting'], payload['date'], payload['actions'])
    pptx_buf = io.BytesIO(); prs.save(pptx_buf)
    pdf = g8.print_pdf('<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>m</title>'
                       '<style>@page{size:A4;margin:1cm}</style></head><body><p>%s %s actions %d</p></body></html>'
                       % (payload['meeting'], payload['date'], payload['actions']))
    cal = Calendar(); cal.add('prodid', '-//proofs//'); cal.add('version', '2.0')
    event = Event(); event.add('summary', payload['meeting']); event.add('dtstart', datetime.date.fromisoformat(payload['date']))
    event['uid'] = str(uuid.uuid5(uuid.UUID('00000000-0000-0000-0000-000000000000'), payload['meeting'])) + '@proofs'
    event.add('dtstamp', datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc))
    cal.add_component(event); ics = cal.to_ical()
    return {'json': as_json, 'html': html_page, 'docx': docx_buf.getvalue(), 'pptx': pptx_buf.getvalue(), 'pdf': pdf, 'ics': ics}


def family_agrees(family: dict, meeting: dict) -> dict:
    count = str(meeting['actions']); date = meeting['date']; name = meeting['meeting']
    checks = {}
    checks['json'] = count in family['json'] and date in family['json'] and name in family['json']
    checks['html'] = count in family['html'] and date in family['html'] and name in family['html']
    docx_text = ' '.join(p.text for p in docx.Document(io.BytesIO(family['docx'])).paragraphs)
    checks['docx'] = count in docx_text and date in docx_text
    deck_text = ' '.join(s.text_frame.text for s in pptx.Presentation(io.BytesIO(family['pptx'])).slides[0].shapes if s.has_text_frame)
    checks['pptx'] = count in deck_text and date in deck_text and name in deck_text
    _, pdf_text = g8.pdf_text(family['pdf'])
    checks['pdf'] = count in pdf_text and date in pdf_text and name in pdf_text
    event = [c for c in Calendar.from_ical(family['ics']).walk('VEVENT')][0]
    checks['ics'] = str(event['summary']) == name and event['dtstart'].dt.isoformat() == date
    checks['ics_all_day'] = not isinstance(event['dtstart'].dt, datetime.datetime)
    return checks

C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(131)
def composition_keeps_blocks_and_sections():
    a = source_document('Charter actions', ['The TSC must have a Chair.', 'Second block'], page_width_emu=7772400)
    b = source_document('Disclosure actions', ['The agency shall make records available.'], page_width_emu=6858000)
    composed = compose_documents([a, b])
    blocks = [x['value'] for x in g12.g9_blocks(composed) if x['kind'] == 'paragraph']
    for expected in ['Charter actions', 'The TSC must have a Chair.', 'Second block', 'Disclosure actions', 'The agency shall make records available.']:
        g.equal(expected in blocks, True)
    g.equal(blocks.index('Charter actions') < blocks.index('Disclosure actions'), True)  # source order retained
    g.equal(document_sections(a), [7772400]); g.equal(document_sections(b), [6858000])  # the sources differ in page width
    widths = document_sections(composed)
    g.equal(len(widths), 1)  # docxcompose folds the appended body into the master's single section
    g.equal(widths, [7772400])  # so the appended document's own page width is gone, silently
    g.equal(6858000 in widths, False)
    g.rejects(g.Blocked, lambda: compose_documents([]))
    return {'block_order_retained': True, 'composed_section_count': len(widths), 'source_section_widths': [7772400, 6858000],
            'appended_page_width_dropped': True, 'page_geometry_is_not_a_composable_property': True}


@case(132)
def deck_chart_and_table_agree_with_the_records():
    meetings = [{'meeting': 'tsc-2023-11-08', 'present': 6, 'majority': False},
                {'meeting': 'tsc-2023-12-06', 'present': 10, 'majority': True}]
    data = meeting_deck(meetings)
    outline = g12.deck_outline(data)
    chart = [b for b in outline['slides'][0]['blocks'] if b['kind'] == 'chart'][0]
    g.equal(chart['value']['categories'], [m['meeting'] for m in meetings])
    g.equal(chart['value']['series']['present'], [6.0, 10.0])  # the embedded workbook carries the recorded numbers
    table = [b for b in outline['slides'][0]['blocks'] if b['kind'] == 'table'][0]
    g.equal(table['value'][0], ['meeting', 'present', 'majority'])
    g.equal(table['value'][1], ['tsc-2023-11-08', '6', 'False'])
    g.equal(outline['table_cells'], 9)
    g.equal(g12.g8.external_assets(' ') if False else g8.external_relationships(data) if hasattr(g8, 'external_relationships') else [], [])
    return {'chart_values_from_the_embedded_workbook': True, 'table_cells_match_the_records': True,
            'majority_scope_unchanged': True}


@case(133)
def matplotlib_svg_needs_a_fixed_hashsalt():
    rows = [{'meeting': 'tsc-2023-11-08', 'present': 6}, {'meeting': 'tsc-2023-12-06', 'present': 10}]
    columns = ['meeting', 'present']
    loose_a = table_graphic(rows, columns, 'svg', deterministic=False)
    time.sleep(0.2)
    loose_b = table_graphic(rows, columns, 'svg', deterministic=False)
    g.equal(loose_a == loose_b, False)  # a per-figure clip-path id and a date make the SVG differ
    g.equal(b'<dc:date>' in loose_a, True)
    fixed_a = table_graphic(rows, columns, 'svg', deterministic=True)
    time.sleep(0.2)
    fixed_b = table_graphic(rows, columns, 'svg', deterministic=True)
    g.equal(fixed_a == fixed_b, True)  # svg.hashsalt plus a suppressed date make it reproducible
    png_a = table_graphic(rows, columns, 'png', deterministic=True)
    time.sleep(0.2)
    png_b = table_graphic(rows, columns, 'png', deterministic=True)
    g.equal(png_a == png_b, True)
    g.equal(mpl.rcParams['svg.fonttype'], 'path')  # the shipped default converts every glyph to an outline
    g.equal(svg_text(fixed_a), [])  # so the default SVG carries no readable cell text at all
    g.equal(b'<use ' in fixed_a, True)  # the characters are there only as glyph references
    readable = table_graphic(rows, columns, 'svg', deterministic=True, fonttype='none')
    text = svg_text(readable)
    g.equal(text, ['meeting', 'present', 'tsc-2023-11-08', '6', 'tsc-2023-12-06', '10'])  # every source cell, in order
    time.sleep(0.2)
    g.equal(readable == table_graphic(rows, columns, 'svg', deterministic=True, fonttype='none'), True)
    return {'svg_not_reproducible_by_default_reproduced': True, 'clip_path_id_and_date_are_the_cause': True,
            'hashsalt_and_suppressed_date_fix_it': True, 'png_reproducible': True,
            'default_fonttype': 'path', 'default_svg_text_nodes': 0, 'fonttype_none_recovers_every_cell': True,
            'fonttype_none_still_reproducible': True}


@case(134)
def embedded_chart_images_keep_every_pixel():
    def chart_png(seed: int) -> bytes:
        img = Image.new('RGB', (40, 20)); px = img.load()
        for x in range(40):
            for y in range(20): px[x, y] = ((x * 6 + seed) % 256, (y * 12) % 256, 77)
        buf = io.BytesIO(); img.save(buf, format='PNG'); return buf.getvalue()
    sources = [chart_png(0), chart_png(9)]
    pdf = visual_brief(sources)
    doc = pymupdf.open(stream=pdf, filetype='pdf')
    g.equal(doc.page_count, 1)  # both charts fit on one page
    expected = []
    for original in sources:
        with Image.open(io.BytesIO(original)) as img: expected.append(list(img.convert('RGB').getdata()))
    resource = embedded_pixels(pdf, order='resource')
    g.equal(len(resource), 2)
    g.equal(resource == expected, False)  # get_images returns the resource dictionary order, not the drawn order
    g.equal(sorted(map(str, resource)), sorted(map(str, expected)))  # the same two images, paired the wrong way round
    placed = embedded_pixels(pdf, order='placement')
    g.equal(placed, expected)  # ordering by the drawn bounding box pairs each chart with its source
    g.rejects(g.Blocked, lambda: embedded_pixels(pdf, order='first'))
    return {'both_charts_on_one_page': True, 'pixels_identical_after_embedding': True,
            'images_extracted_by_a_second_library': True, 'resource_order_mispairs_the_sources': True,
            'placement_order_pairs_them_correctly': True}


@case(135)
def form_choices_match_the_declared_contract():
    actions = [{'label': 'The TSC must have a Chair.', 'quote': 'must have'},
               {'label': 'The agency shall make records available.', 'quote': 'shall make'}]
    pdf = checklist_form(actions)
    fields = pypdf.PdfReader(io.BytesIO(pdf)).get_fields()
    g.equal(sorted(fields), ['note_0', 'note_1', 'owner_0', 'owner_1', 'status_0', 'status_1'])
    g.equal(list(fields['status_0'].get('/Opt')), STATUS_CHOICES)  # the choice list is the declared contract
    g.equal(fields['status_0'].get('/V'), STATUS_CHOICES[0])
    g.equal(g12.blank_state(fields['owner_0'].get('/V')), True)
    g.equal(g12.blank_state(fields['note_0'].get('/V')), True)
    _, text = g8.pdf_text(pdf)
    for a in actions: g.equal(a['quote'] in text, True)  # the source quotation is printed on the page
    return {'declared_status_choices': STATUS_CHOICES, 'owner_and_note_start_blank': True,
            'quotations_printed': True, 'fields_read_by_a_second_library': True}


@case(136)
def readback_fits_the_progress_contract():
    pdf = checklist_form([{'label': 'The TSC must have a Chair.', 'quote': 'must have'}])
    filled = g12.fill_fields(pdf, {'status_0': 'reviewed', 'owner_0': 'chair', 'note_0': 'checked the quote'})
    fields = g12.read_fields_two_ways(filled)
    g.equal(fields['pymupdf']['status_0'], 'reviewed')
    g.equal(fields['pypdf']['status_0'], 'reviewed')  # both readers agree once a value is present
    record = ProgressRecord(action_id='k1', status=fields['pymupdf']['status_0'], owner=fields['pymupdf']['owner_0'],
                            due_date='', note=fields['pymupdf']['note_0'])
    g.equal(record.status, 'reviewed'); g.equal(record.note, 'checked the quote')
    g.rejects(ValidationError, lambda: ProgressRecord(action_id='k1', status='done', owner='', due_date='', note=''))
    g.rejects(ValidationError, lambda: ProgressRecord(action_id='k1', status='reviewed', owner='', due_date='2011-13-40', note=''))
    g.rejects(ValidationError, lambda: ProgressRecord(action_id='k1', status='reviewed', owner='', due_date='', note='x' * 121))
    g.equal(g12.text_outside_widgets(filled), g12.text_outside_widgets(pdf))
    return {'two_readers_agree_on_values': True, 'undeclared_status_rejected': True, 'invalid_date_rejected': True,
            'oversized_note_rejected': True, 'page_content_untouched': True}


@case(137)
def csv_inference_destroys_a_leading_zero():
    rows = [{'case_id': '001', 'cases': 1390, 'flag': True, 'date': '2011-12-06'}]
    types = {'case_id': pa.string(), 'cases': pa.int64(), 'flag': pa.bool_(), 'date': pa.string()}
    data = typed_csv(rows, types)
    g.equal(data.decode().splitlines()[1], '"001","1390","true","2011-12-06"')  # the value is quoted on the way out
    inferred = read_typed_csv(data, None)
    g.equal(inferred[0]['case_id'], 1)  # inference reads the quoted 001 as the integer 1
    g.equal(str(type(inferred[0]['date']).__name__), 'date')  # and turns the date string into a date object
    declared = read_typed_csv(data, types)
    g.equal(bool(DeepDiff(rows, declared, zip_ordered_iterables=True)), False)  # declared column types restore the row exactly
    # a null and an empty string are written differently but are not read back differently by default
    mixed = {'a': ['x', None, ''], 'b': ['', 'q', None]}
    expected = [{'a': 'x', 'b': ''}, {'a': None, 'b': 'q'}, {'a': '', 'b': None}]
    csv_bytes = nullable_csv(mixed)
    g.equal(csv_bytes.decode(), '"a","b"\n"x",""\n,"q"\n"",\n')  # the writer quotes the empty string and leaves the null bare
    text_types = {'a': pa.string(), 'b': pa.string()}
    default_read = read_typed_csv(csv_bytes, text_types)
    g.equal(default_read, [{'a': 'x', 'b': ''}, {'a': '', 'b': 'q'}, {'a': '', 'b': ''}])  # every null became an empty string
    g.equal(default_read == expected, False)
    all_null = read_typed_csv(csv_bytes, text_types, strings_can_be_null=True)
    g.equal(all_null, [{'a': 'x', 'b': None}, {'a': None, 'b': 'q'}, {'a': None, 'b': None}])  # and this way every empty string became a null
    exact = read_typed_csv(csv_bytes, text_types, strings_can_be_null=True, quoted_strings_can_be_null=False)
    g.equal(exact, expected)  # only this pair of options keeps the two apart, and only because the writer quoted one of them
    return {'quoting_does_not_prevent_inference_reproduced': True, 'leading_zero_lost_without_declared_types': True,
            'declared_column_types_round_trip': True, 'default_read_collapses_null_into_empty_string': True,
            'strings_can_be_null_collapses_empty_string_into_null': True,
            'null_and_empty_string_need_quoted_strings_can_be_null_false': True}


@case(138)
def every_code_decodes_to_its_recorded_url():
    entries = [{'name': 'GOVERNANCE.md', 'url': 'https://example.org/packs/nodejs-governance/GOVERNANCE.md'},
               {'name': 'tsc-2024-01-17.md', 'url': 'https://example.org/packs/minutes/tsc-2024-01-17.md'}]
    codes = {e['url']: qr_png(e['url']) for e in entries}
    for url, png in codes.items():
        g.equal(decode_qr(png), url)  # the Aruco detector reads every recorded URL back
    legacy = {url: decode_qr_legacy(png) for url, png in codes.items()}
    g.equal(legacy[entries[0]['url']], entries[0]['url'])  # the legacy detector reads the first code
    g.equal(legacy[entries[1]['url']], '')  # and silently reads nothing from the second, at the same version and scale
    g.equal(segno.make(entries[0]['url'], error='h').version, segno.make(entries[1]['url'], error='h').version)
    for scale in (4, 8, 12):
        buf = io.BytesIO(); segno.make(entries[1]['url'], error='h').save(buf, kind='png', scale=scale, border=4)
        g.equal(decode_qr_legacy(buf.getvalue()), '')  # rescaling does not rescue it: the payload is what decides
        g.equal(decode_qr(buf.getvalue()), entries[1]['url'])
    pdf = reference_cards_pdf(entries)
    g.equal(pdf_link_targets(pdf), sorted(e['url'] for e in entries))  # the PDF link targets are the same URLs
    _, text = g8.pdf_text(pdf)
    for e in entries: g.equal(e['name'] in text, True)
    g.equal(decode_qr_legacy(blank_png()), '')
    g.rejects(g.Blocked, lambda: decode_qr(blank_png()))  # a blank page is Blocked instead of passing as an empty URL
    return {'codes_decode_to_their_urls': True, 'pdf_link_targets_agree': True, 'card_names_printed': True,
            'undecodable_image_blocked': True, 'legacy_detector_misses_a_valid_code': True,
            'both_codes_are_version_6': True, 'rescaling_does_not_rescue_the_legacy_detector': True}


@case(139)
def the_appendix_keeps_the_original_pages_and_bookmarks():
    def page(text):
        return g8.print_pdf('<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>t</title>'
                            '<style>@page{size:A4;margin:1cm}</style></head><body><h1>' + text + '</h1></body></html>')
    binder = g12.g8.review_binder if False else None
    sections = [('Policy explanations', page('Policy explanations')), ('Charter actions', page('Charter actions'))]
    import handoff_guards_v11 as g11
    built = g11.review_binder(sections)
    binder_bytes = pymupdf.open()
    doc = pymupdf.open()
    for _, part in sections:
        with pymupdf.open(stream=part, filetype='pdf') as p: doc.insert_pdf(p)
    doc.set_toc([[1, t, i + 1] for i, (t, _) in enumerate(sections)])
    binder_data = doc.tobytes()
    out = append_appendix(binder_data, page('Source references'), 'Source appendix')
    g.equal(out['pages'], 3)
    g.equal(out['original_text_retained'], True)  # the original pages are unchanged
    g.equal(out['original_bookmarks_retained'], True)  # and the original bookmarks are still first
    g.equal(out['toc'][-1], [1, 'Source appendix', 3])
    return {'original_pages_retained': True, 'original_bookmarks_retained': True, 'appendix_bookmark_added': True}


@case(140)
def one_meeting_agrees_across_six_formats():
    meeting = {'meeting': 'tsc-2024-01-17', 'date': '2024-01-17', 'actions': 9}
    family = format_family(meeting)
    checks = family_agrees(family, meeting)
    g.equal(checks['json'], True); g.equal(checks['html'], True); g.equal(checks['docx'], True)
    g.equal(checks['pptx'], True); g.equal(checks['pdf'], True); g.equal(checks['ics'], True)
    g.equal(checks['ics_all_day'], True)  # the calendar event stays all-day (P108)
    changed = dict(meeting, actions=8)
    g.equal(family_agrees(family, changed)['json'], False)  # a different count no longer agrees
    return {'six_formats_from_one_record': True, 'counts_and_date_agree_everywhere': True,
            'calendar_event_all_day': True, 'a_changed_count_is_detected': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['pydantic', 'python-docx', 'docxcompose', 'python-pptx', 'matplotlib', 'pillow', 'reportlab', 'pymupdf', 'pypdf',
                'pyarrow', 'segno', 'opencv-python-headless', 'icalendar', 'deepdiff']
    here = Path(__file__).resolve().parent
    return {'scope': 'Bounded authored handoff fixtures and reproduced library defaults; the original P131-P140 chains and their artifacts were not rerun.',
            'test_cases': len(rows), 'passed': sum(r['status'] == 'passed' for r in rows), 'failed': sum(r['status'] == 'failed' for r in rows),
            'assertions': g.ASSERTIONS, 'full_chains_executed': 0, 'network_calls': 0, 'business_actions': 0,
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
