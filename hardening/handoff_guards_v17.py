"""Seventeenth bounded adapter suite: P161-P170, cash-flow classification, native presentation notes, PDF annotation,
edit-distance lookup, OpenDocument conversion and recalculation, chart round trips, expense policy, cent allocation
and break-even handoffs. Requires handoff_guards_v1.py from this TXT.

Every meaningful operation below is a library primitive call. Coverage and uniqueness are pandera schema constraints
and a pandas Index operation; the edit-distance lookup is rapidfuzz alone, reading the distance the call returns;
the cent apportionment is largest_remainder and apportionment, which is why the credit pool is Blocked rather than
allocated. Local code declares fixtures and policies and turns a primitive result into a Blocked outcome; it does
not reimplement an operation a library performs. All runtime inputs are authored fixtures. No model client and no
network.
Run: python handoff_guards_v17.py --report report.json
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, io, json, logging, traceback, warnings, zipfile
from decimal import Decimal, DivisionByZero, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP, ROUND_UP
from pathlib import Path
import numpy as np
import openpyxl
import pandas as pd
import pandera.pandas as pandera
import pymupdf
import rapidfuzz
from odf import teletype
from odf.namespaces import OFFICENS, TABLENS
from odf.opendocument import OpenDocumentSpreadsheet, OpenDocumentText, load as odf_load
from odf.table import Table, TableCell, TableRow
from odf.text import LineBreak, P, S, Tab
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches
from largest_remainder import LargestRemainder
import apportionment.methods as apportionment
from rapidfuzz import process
from rapidfuzz.distance import DamerauLevenshtein, Levenshtein
import handoff_guards_v1 as g
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

CENT = Decimal('0.01')
CLASSES = ['operating', 'investing', 'financing']

# ---------------------------------------------------------------- P161
JOURNAL_IDS = ['J01', 'J02', 'J03', 'J04']
CLASSIFICATION_SCHEMA = pandera.DataFrameSchema({
    'journal': pandera.Column(str, pandera.Check.isin(JOURNAL_IDS), unique=True),
    'classification': pandera.Column(str, pandera.Check.isin(CLASSES)),
    'amount': pandera.Column(object),
})


def covers_exactly(frame: pd.DataFrame, declared: list[str]) -> pd.DataFrame:
    """Membership and uniqueness are the schema's; the two-way gap is an Index operation."""
    try:
        checked = CLASSIFICATION_SCHEMA.validate(frame, lazy=True)
    except pandera.errors.SchemaErrors as failure:
        raise g.Blocked('classification rejected: %s'
                        % failure.failure_cases[['check', 'failure_case']].to_dict('records'))
    missing = pd.Index(declared).symmetric_difference(pd.Index(checked['journal']))
    if len(missing):
        raise g.Blocked('classification does not cover the journal: %s' % list(missing))
    return checked


def statement_lines(rows: list[dict], *, complete: str) -> dict:
    """complete='observed' returns only the classes that occur; 'null' and 'zero' force all three."""
    totals = pd.DataFrame(rows).groupby('classification')['amount'].sum()
    if complete == 'observed':
        pass
    elif complete == 'null':
        totals = totals.reindex(CLASSES)
    elif complete == 'zero':
        totals = totals.reindex(CLASSES, fill_value=Decimal('0.00'))
    else:
        raise g.Blocked('unknown completion mode %r' % complete)
    return {k: (None if pd.isna(v) else v) for k, v in totals.items()}


# ---------------------------------------------------------------- P162
def small_png() -> bytes:
    import struct, zlib
    def chunk(tag, body):
        payload = tag + body
        return struct.pack('>I', len(body)) + payload + struct.pack('>I', zlib.crc32(payload) & 0xffffffff)
    rows = b''.join(b'\x00' + bytes([9, 9, 9]) * 4 for _ in range(4))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 4, 4, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


def slide_deck() -> bytes:
    deck = Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[5])
    slide.shapes.title.text = 'Node.js TSC 2024-01-17'
    box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(4), Inches(1))
    box.text_frame.text = 'Line one'
    box.text_frame.add_paragraph().text = 'Line two'
    slide.shapes.add_picture(io.BytesIO(small_png()), Inches(5), Inches(2), Inches(1), Inches(1))
    buf = io.BytesIO(); deck.save(buf); return buf.getvalue()


def package_parts(document: bytes) -> set:
    with zipfile.ZipFile(io.BytesIO(document)) as archive:
        return set(archive.namelist())


def notes_probe(document: bytes, *, how: str) -> bytes:
    """how='property' reads slide.notes_slide; 'guarded' reads slide.has_notes_slide."""
    deck = Presentation(io.BytesIO(document))
    slide = deck.slides[0]
    if how == 'property':
        slide.notes_slide
    elif how == 'guarded':
        slide.has_notes_slide
    else:
        raise g.Blocked('unknown notes probe %r' % how)
    buf = io.BytesIO(); deck.save(buf); return buf.getvalue()


def shape_texts(document: bytes, *, guarded: bool) -> list[str]:
    deck = Presentation(io.BytesIO(document))
    out = []
    for shape in deck.slides[0].shapes:
        if guarded and not shape.has_text_frame:
            continue
        out.append(shape.text)
    return out


def write_notes(document: bytes, paragraphs: list[str]) -> bytes:
    deck = Presentation(io.BytesIO(document))
    frame = deck.slides[0].notes_slide.notes_text_frame
    frame.text = paragraphs[0]
    for extra in paragraphs[1:]:
        frame.add_paragraph().text = extra
    buf = io.BytesIO(); deck.save(buf); return buf.getvalue()


def read_notes(document: bytes) -> tuple[str, int]:
    frame = Presentation(io.BytesIO(document)).slides[0].notes_slide.notes_text_frame
    return frame.text, len(frame.paragraphs)


# ---------------------------------------------------------------- P163
def review_pdf() -> bytes:
    doc = pymupdf.open(); page = doc.new_page()
    for y, line in ((100, 'The TSC approves the charter.'), (130, 'the tsc approves the charter.'),
                    (190, 'A quick brown fox jumps over'), (205, 'the lazy dog completely.')):
        page.insert_text((72, y), line)
    return doc.tobytes()


def find(document: bytes, phrase: str) -> list:
    return pymupdf.open('pdf', document)[0].search_for(phrase)


def recovered(document: bytes, rect) -> str:
    return pymupdf.open('pdf', document)[0].get_textbox(rect)


def highlight(document: bytes, phrase: str, comment: str, *, update: bool) -> bytes:
    doc = pymupdf.open('pdf', document); page = doc[0]
    hits = page.search_for(phrase)
    if not hits:
        raise g.Blocked('phrase not present: %r' % phrase)
    annot = page.add_highlight_annot(hits[0])
    annot.set_info(content=comment, title='reviewer')
    if update:
        annot.update()
    return doc.tobytes()


def saved_annotations(document: bytes) -> list[dict]:
    page = pymupdf.open('pdf', document)[0]
    return [{'content': a.info.get('content'), 'title': a.info.get('title'),
             'vertices': len(a.vertices or []), 'type': a.type[1]} for a in page.annots()]


def exact_hit(document: bytes, phrase: str) -> list:
    """Keep only hits whose recovered characters equal the query exactly."""
    return [r for r in find(document, phrase) if recovered(document, r) == phrase]


# ---------------------------------------------------------------- P164
WORDS = ['governance', 'governing', 'members', 'member', 'team', 'teams', 'term',
         'release', 'releases', 'voting', 'vote', 'contributors', 'contributor']


def lookup(query: str, words: list[str], *, scorer, cutoff, limit, processor=None) -> list[str]:
    hits = process.extract(query, words, scorer=scorer, score_cutoff=cutoff, limit=limit, processor=processor)
    return [h[0] for h in hits]


# ---------------------------------------------------------------- P165
def odt_document() -> bytes:
    doc = OpenDocumentText()
    doc.text.addElement(P(text='Body one'))
    spaced = P(); spaced.addText('A'); spaced.addElement(S(c=3)); spaced.addText('B')
    doc.text.addElement(spaced)
    tabbed = P(); tabbed.addText('left'); tabbed.addElement(Tab()); tabbed.addText('right')
    doc.text.addElement(tabbed)
    broken = P(); broken.addText('first'); broken.addElement(LineBreak()); broken.addText('second')
    doc.text.addElement(broken)
    table = Table(name='T1'); row = TableRow()
    for value in ('cell A', 'cell B'):
        cell = TableCell(); cell.addElement(P(text=value)); row.addElement(cell)
    table.addElement(row); doc.text.addElement(table)
    buf = io.BytesIO(); doc.write(buf); return buf.getvalue()


def odt_blocks(document: bytes, *, scope: str) -> list[str]:
    """scope='flat' is getElementsByType(P); 'body' walks the top-level body children only."""
    doc = odf_load(io.BytesIO(document))
    if scope == 'flat':
        return [teletype.extractText(p) for p in doc.getElementsByType(P)]
    if scope == 'body':
        return [teletype.extractText(n) for n in doc.text.childNodes if n.qname[1] in ('p', 'table')]
    if scope == 'cells':
        return [teletype.extractText(c) for c in doc.getElementsByType(TableCell)]
    raise g.Blocked('unknown odt scope %r' % scope)


# ---------------------------------------------------------------- P166
def ods_document() -> bytes:
    doc = OpenDocumentSpreadsheet(); table = Table(name='Schedule'); row = TableRow()
    start = TableCell(valuetype='date', datevalue='2014-07-31'); start.addElement(P(text='2014-07-31'))
    finish = TableCell(valuetype='date', datevalue='2012-06-22'); finish.addElement(P(text='2012-06-22'))
    elapsed = TableCell(valuetype='float', value='766', formula='of:=[.A1]-[.B1]'); elapsed.addElement(P(text='766'))
    for cell in (start, finish, elapsed):
        row.addElement(cell)
    table.addElement(row); doc.spreadsheet.addElement(table)
    buf = io.BytesIO(); doc.write(buf); return buf.getvalue()


def edit_date(document: bytes, new_date: str) -> bytes:
    doc = odf_load(io.BytesIO(document))
    doc.getElementsByType(TableCell)[0].setAttrNS(OFFICENS, 'date-value', new_date)
    buf = io.BytesIO(); doc.write(buf); return buf.getvalue()


def cell_views(document: bytes, index: int) -> dict:
    cell = odf_load(io.BytesIO(document)).getElementsByType(TableCell)[index]
    return {'value': cell.getAttrNS(OFFICENS, 'value'), 'date': cell.getAttrNS(OFFICENS, 'date-value'),
            'formula': cell.getAttrNS(TABLENS, 'formula'), 'text': teletype.extractText(cell)}


# ---------------------------------------------------------------- P167
CATEGORIES = ['Travel', 'Software', 'Facilities', 'Contingency', 'Training']
AMOUNTS = (1200.25, 2130.00, 85.00, 0.00, 1140.25)


def chart_deck(categories=CATEGORIES, values=AMOUNTS, series='Actual') -> bytes:
    deck = Presentation(); slide = deck.slides.add_slide(deck.slide_layouts[6])
    data = CategoryChartData(); data.categories = list(categories); data.add_series(series, tuple(values))
    slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(1), Inches(1), Inches(6), Inches(4), data)
    buf = io.BytesIO(); deck.save(buf); return buf.getvalue()


def chart_state(document: bytes) -> dict:
    chart = Presentation(io.BytesIO(document)).slides[0].shapes[0].chart
    part = chart._workbook.xlsx_part
    cells = None
    if part is not None:
        sheet = openpyxl.load_workbook(io.BytesIO(part.blob)).active
        cells = [[c.value for c in row] for row in sheet.iter_rows()]
    return {'categories': list(chart.plots[0].categories), 'values': list(chart.series[0].values),
            'types': [type(v).__name__ for v in chart.series[0].values], 'workbook': cells}


def rebind_workbook(document: bytes) -> bytes:
    deck = Presentation(io.BytesIO(document)); chart = deck.slides[0].shapes[0].chart
    data = CategoryChartData(); data.categories = list(chart.plots[0].categories)
    data.add_series('Actual', tuple(chart.series[0].values))
    chart.replace_data(data)
    buf = io.BytesIO(); deck.save(buf); return buf.getvalue()


def sever_workbook(document: bytes) -> bytes:
    deck = Presentation(io.BytesIO(document))
    deck.slides[0].shapes[0].chart._workbook.xlsx_part = None
    buf = io.BytesIO(); deck.save(buf); return buf.getvalue()


# ---------------------------------------------------------------- P168
def parse_rates(raw: str, *, strict: bool) -> dict:
    if strict:
        return {k: Decimal(v) for k, v in g.strict_json_loads(raw).items()}
    return json.loads(raw)


def convert(amount: str, rate, *, mode: str) -> Decimal:
    """mode='float' multiplies by the parsed JSON number; 'string' routes it through Decimal(str(...))."""
    if mode == 'float':
        return (Decimal(amount) * rate).quantize(CENT, rounding=ROUND_HALF_UP)
    if mode == 'string':
        return (Decimal(amount) * Decimal(str(rate))).quantize(CENT, rounding=ROUND_HALF_UP)
    raise g.Blocked('unknown conversion mode %r' % mode)


RECEIPT_SCHEMA = pandera.DataFrameSchema({'receipt_id': pandera.Column(str, unique=True)})


def reused_receipts(references: list[str]) -> list[str]:
    """The duplicate and its identifier come from the schema, not from a local tally."""
    try:
        RECEIPT_SCHEMA.validate(pd.DataFrame({'receipt_id': references}), lazy=True)
    except pandera.errors.SchemaErrors as failure:
        return sorted(set(failure.failure_cases['failure_case']))
    return []


# ---------------------------------------------------------------- P169
def hamilton(total_cents: int, weights: list[int], *, library: str) -> list[int]:
    """Both researched implementations of the largest-remainder method; no local rounding rule."""
    if library == 'largest_remainder':
        return LargestRemainder.round(list(weights), total=total_cents)
    if library == 'apportionment':
        return apportionment.compute('hamilton', list(weights), total_cents, verbose=False)
    raise g.Blocked('unknown apportionment library %r' % library)


def allocate(pool_cents: int, weights: dict, *, library: str = 'largest_remainder') -> dict:
    if any(w is None for w in weights.values()):
        raise g.Blocked('a driver weight is missing; the pool stays unallocated')
    if pool_cents < 0:
        raise g.Blocked('no researched primitive conserves a negative pool')
    keys = sorted(weights)
    return dict(zip(keys, hamilton(pool_cents, [weights[k] for k in keys], library=library)))


# ---------------------------------------------------------------- P170
def minimum_volume(fixed: str, contribution: str, *, rounding=ROUND_CEILING) -> Decimal:
    try:
        return (Decimal(fixed) / Decimal(contribution)).to_integral_value(rounding=rounding)
    except DivisionByZero:
        raise g.Blocked('zero contribution has no finite break-even volume')
    except InvalidOperation:
        raise g.Blocked('zero fixed cost over zero contribution is undetermined')


def profit(volume: int, contribution: str, fixed: str) -> Decimal:
    return Decimal(volume) * Decimal(contribution) - Decimal(fixed)


def volume_range(low: int, high: int, *, step) -> list:
    return [v.item() if hasattr(v, 'item') else v for v in np.arange(low, high, step)]


C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(161)
def a_schema_names_the_identifier_a_set_comparison_would_hide():
    def frame(ids, classes):
        return pd.DataFrame({'journal': ids, 'classification': classes,
                             'amount': [Decimal('100.00')] * len(ids)})
    exact = frame(JOURNAL_IDS, ['operating', 'operating', 'investing', 'financing'])
    g.equal(len(covers_exactly(exact, JOURNAL_IDS)), 4)
    doubled = frame(['J01', 'J02', 'J02', 'J03'], ['operating'] * 4)
    g.rejects(g.Blocked, lambda: covers_exactly(doubled, JOURNAL_IDS))
    try:
        covers_exactly(doubled, JOURNAL_IDS)
    except g.Blocked as blocked:
        g.equal('J02' in str(blocked), True)  # the duplicate identifier is named
        g.equal('field_uniqueness' in str(blocked), True)
    unknown = frame(['J01', 'J02', 'J03', 'J99'], ['operating'] * 4)
    try:
        covers_exactly(unknown, JOURNAL_IDS)
    except g.Blocked as blocked:
        g.equal('J99' in str(blocked), True)  # the unknown identifier is named
    short = frame(['J01', 'J02', 'J03'], ['operating'] * 3)
    try:
        covers_exactly(short, JOURNAL_IDS)
    except g.Blocked as blocked:
        g.equal("['J04']" in str(blocked), True)  # the uncovered identifier is named
    g.equal(len(pd.Index(JOURNAL_IDS).symmetric_difference(pd.Index(JOURNAL_IDS))), 0)
    rows = [{'journal': j, 'classification': c, 'amount': Decimal('100.00')}
            for j, c in zip(['J01', 'J02', 'J02', 'J03', 'J04'],
                            ['operating', 'operating', 'operating', 'investing', 'financing'])]
    totals = statement_lines(rows, complete='observed')
    g.equal(totals['operating'], Decimal('300.00'))  # what the unchecked frame would have produced
    partial = [{'journal': 'J01', 'classification': 'operating', 'amount': Decimal('10.00')},
               {'journal': 'J02', 'classification': 'financing', 'amount': Decimal('5.00')}]
    observed = statement_lines(partial, complete='observed')
    g.equal(sorted(observed), ['financing', 'operating']); g.equal(len(observed), 2)
    nulled = statement_lines(partial, complete='null')
    g.equal(list(nulled), CLASSES); g.equal(nulled['investing'] is None, True)
    zeroed = statement_lines(partial, complete='zero')
    g.equal(zeroed['investing'], Decimal('0.00'))
    g.equal(nulled['investing'] == zeroed['investing'], False)
    g.rejects(g.Blocked, lambda: statement_lines(partial, complete='fill'))
    return {'coverage_is_a_schema_and_an_index_operation': True,
            'duplicate_unknown_and_missing_are_named_separately': True,
            'absent_classification_is_dropped_not_zeroed': True,
            'fill_value_fabricates_a_measurement': True}


@case(162)
def reading_the_notes_property_creates_the_notes():
    deck = slide_deck()
    before = package_parts(deck)
    g.equal(any('notesSlides' in n for n in before), False)
    touched = notes_probe(deck, how='property')
    added = sorted(package_parts(touched) - before)
    g.equal(len(added), 5)  # a read added a notes slide, a notes master, their relationships and a second theme
    g.equal(any(n.startswith('ppt/notesSlides/') for n in added), True)
    g.equal(any(n.startswith('ppt/notesMasters/') for n in added), True)
    g.equal('ppt/theme/theme2.xml' in added, True)
    g.equal(hashlib.sha256(touched).hexdigest() == hashlib.sha256(deck).hexdigest(), False)
    guarded = notes_probe(deck, how='guarded')
    g.equal(sorted(package_parts(guarded) - before), [])  # has_notes_slide adds nothing
    g.rejects(g.Blocked, lambda: notes_probe(deck, how='xml'))
    g.rejects(AttributeError, lambda: shape_texts(deck, guarded=False))  # a picture has no text attribute
    g.equal(shape_texts(deck, guarded=True), ['Node.js TSC 2024-01-17', 'Line one\nLine two'])
    written = write_notes(deck, ['A & B < 5 > 2', 'second note line'])
    text, paragraphs = read_notes(written)
    g.equal(text, 'A & B < 5 > 2\nsecond note line')  # the literal survives python-pptx unchanged
    g.equal(paragraphs, 2); g.equal(text.count('\n'), 1)
    g.equal(len(text.split('\n')), paragraphs)  # only because no paragraph contains a newline of its own
    kept = package_parts(written) & before
    g.equal(len(kept), len(before))  # every part the deck already had is still present
    return {'notes_slide_property_mutates_the_package': True, 'parts_added_by_a_read': 5,
            'has_notes_slide_is_the_non_mutating_test': True, 'shape_text_raises_on_a_picture': True,
            'notes_text_joins_paragraphs_with_a_newline': True}


@case(163)
def a_matched_rectangle_is_not_the_matched_phrase():
    pdf = review_pdf()
    hits = find(pdf, 'the tsc approves')
    g.equal(len(hits), 2)  # ASCII case-insensitive by default, so the capitalised line matches too
    g.equal(recovered(pdf, hits[0]), 'The TSC approves')
    g.equal(recovered(pdf, hits[1]), 'the tsc approves')
    g.equal(recovered(pdf, hits[0]) == recovered(pdf, hits[1]), False)  # an exact comparison separates them
    g.equal(len(exact_hit(pdf, 'the tsc approves')), 1)
    g.equal(len(find(pdf, 'Budget was approved')), 0)
    multi = find(pdf, 'jumps over the lazy dog')
    g.equal(len(multi), 2)  # the phrase spans a line break and still matches
    g.equal(recovered(pdf, multi[0]), 'jumps over\nletely.')  # the rectangle catches the line below it
    g.equal(recovered(pdf, multi[0]) == 'jumps over the lazy dog', False)
    g.equal(len(exact_hit(pdf, 'jumps over the lazy dog')), 0)  # so the exact filter rejects the whole match
    g.equal(type(find(pdf, 'the tsc approves')[0]).__name__, 'Rect')
    quads = pymupdf.open('pdf', pdf)[0].search_for('the tsc approves', quads=True)
    g.equal(type(quads[0]).__name__, 'Quad')
    for update in (False, True):
        saved = highlight(pdf, 'the tsc approves', 'illustrative comment', update=update)
        annots = saved_annotations(saved)
        g.equal(len(annots), 1)
        g.equal(annots[0]['content'], 'illustrative comment')  # set_info persists with or without update()
        g.equal(annots[0]['title'], 'reviewer'); g.equal(annots[0]['vertices'], 4)
        g.equal(annots[0]['type'], 'Highlight')
    g.rejects(g.Blocked, lambda: highlight(pdf, 'Budget was approved', 'c', update=True))
    return {'search_for_is_ascii_case_insensitive': True, 'search_for_matches_across_a_line_break': True,
            'textbox_of_a_hit_crosses_lines': True, 'exact_comparison_is_the_only_filter': True,
            'set_info_persists_without_update': True}


@case(164)
def the_default_limit_drops_the_ties_the_chain_promises():
    exact = lookup('governacne', WORDS, scorer=DamerauLevenshtein.distance, cutoff=1, limit=None)
    g.equal(exact, ['governance'])  # one adjacent transposition
    g.equal(DamerauLevenshtein.distance('governacne', 'governance'), 1)
    g.equal(Levenshtein.distance('governacne', 'governance'), 2)
    g.equal(lookup('governacne', WORDS, scorer=Levenshtein.distance, cutoff=1, limit=None), [])
    crowded = WORDS + ['ter%d' % i for i in range(8)]
    capped = lookup('term', crowded, scorer=DamerauLevenshtein.distance, cutoff=2, limit=5)
    every = lookup('term', crowded, scorer=DamerauLevenshtein.distance, cutoff=2, limit=None)
    g.equal(len(capped), 5); g.equal(len(every), 11)
    g.equal(set(capped) < set(every), True)
    g.equal(sorted(set(every) - set(capped)), ['teams', 'ter3', 'ter4', 'ter5', 'ter6', 'ter7'])
    g.equal('teams' in every and 'teams' not in capped, True)  # a real source word is among the dropped ties
    g.equal(lookup('MEMBERS', WORDS, scorer=DamerauLevenshtein.distance, cutoff=1, limit=None), [])
    g.equal(DamerauLevenshtein.distance('MEMBERS', 'members'), 7)  # no processor means no case folding
    folded = lookup('MEMBERS', WORDS, scorer=DamerauLevenshtein.distance, cutoff=1, limit=None,
                    processor=str.casefold)
    g.equal(sorted(folded), ['member', 'members'])
    scores = {h[0]: h[1] for h in process.extract('MEMBERS', WORDS, scorer=DamerauLevenshtein.distance,
                                                  score_cutoff=1, limit=None, processor=str.casefold)}
    g.equal(scores, {'members': 0, 'member': 1})  # extract already returns the distance
    similar = lookup('governacne', WORDS, scorer=DamerauLevenshtein.similarity, cutoff=1, limit=None)
    g.equal(len(similar), len(WORDS))  # the same cutoff on a similarity scorer returns every word
    g.equal('team' in similar and 'release' in similar, True)
    g.equal(lookup('governacne', WORDS, scorer=DamerauLevenshtein.normalized_similarity, cutoff=1, limit=None), [])
    g.equal(lookup('zzzxqv', WORDS, scorer=DamerauLevenshtein.distance, cutoff=1, limit=None), [])
    return {'default_limit_truncates_ties': True, 'ties_dropped': 6, 'processor_default_is_none': True,
            'uppercase_query_returns_nothing': True, 'cutoff_meaning_flips_with_the_scorer': True,
            'transposition_needs_the_damerau_metric': True}


@case(165)
def a_flat_paragraph_list_is_not_the_document_body():
    document = odt_document()
    flat = odt_blocks(document, scope='flat')
    body = odt_blocks(document, scope='body')
    g.equal(len(flat), 6); g.equal(len(body), 5)  # four body paragraphs and one table
    g.equal(flat[4:], ['cell A', 'cell B'])  # the table cells are indistinguishable in the flat list
    g.equal(body[4], 'cell Acell B')  # extracting a table welds its cells with no separator
    g.equal(odt_blocks(document, scope='cells'), ['cell A', 'cell B'])
    g.equal(body[4] == ''.join(odt_blocks(document, scope='cells')), True)
    g.equal(len(flat) == len(body), False)  # a positional comparison against a Word body shifts from the table on
    g.equal(flat[0], 'Body one')
    g.equal(flat[1], 'A   B')  # text:s is expanded to its declared space count
    g.equal(flat[2], 'left\tright')  # text:tab becomes a tab
    g.equal(flat[3], 'first\nsecond')  # text:line-break becomes a newline inside one paragraph
    g.equal(flat[3].count('\n'), 1); g.equal(len(flat[3].split('\n')), 2)
    g.rejects(g.Blocked, lambda: odt_blocks(document, scope='headers'))
    return {'flat_paragraph_list_includes_table_cells': True, 'table_extraction_welds_cells': True,
            'whitespace_elements_are_expanded': True, 'paragraph_counts_disagree': True}


@case(166)
def the_typed_value_moves_and_the_displayed_text_does_not():
    original = ods_document()
    before = cell_views(original, 0)
    g.equal(before['date'], '2014-07-31'); g.equal(before['text'], '2014-07-31')
    formula_before = cell_views(original, 2)
    g.equal(formula_before['formula'], 'of:=[.A1]-[.B1]')
    g.equal(formula_before['value'], '766'); g.equal(formula_before['text'], '766')
    edited = edit_date(original, '2014-08-01')
    after = cell_views(edited, 0)
    g.equal(after['date'], '2014-08-01')  # the typed value moved
    g.equal(after['text'], '2014-07-31')  # the displayed paragraph did not
    g.equal(after['date'] == after['text'], False)  # two readers of one cell disagree
    dependent = cell_views(edited, 2)
    g.equal(dependent['formula'], 'of:=[.A1]-[.B1]')  # the formula survives
    g.equal(dependent['value'], '766')  # its cached result is stale
    g.equal(dependent['text'], '766')
    g.equal(cell_views(edited, 1)['date'], '2012-06-22')  # no other cell moved
    g.equal(hashlib.sha256(edited).hexdigest() == hashlib.sha256(original).hexdigest(), False)
    g.equal(cell_views(original, 0)['date'], '2014-07-31')  # the source document is untouched
    return {'attribute_edit_leaves_display_text_stale': True, 'cached_formula_result_stays_stale': True,
            'formula_text_survives_the_edit': True, 'recalculation_is_load_bearing': True}


@case(167)
def a_currency_amount_becomes_a_float_and_the_workbook_can_be_severed():
    deck = chart_deck()
    state = chart_state(deck)
    g.equal(state['categories'], CATEGORIES)
    g.equal(state['values'], [1200.25, 2130.0, 85.0, 0.0, 1140.25])
    g.equal(state['types'], ['float'] * 5)  # every cached amount is a float, never a Decimal
    g.equal(state['workbook'][2], ['Software', 2130])  # 2130.00 is stored as an integer
    g.equal(type(state['workbook'][2][1]).__name__, 'int')
    g.equal(state['workbook'][4], ['Contingency', 0])
    g.equal(state['workbook'][1], ['Travel', 1200.25])
    g.equal(Decimal('2130.00') == state['workbook'][2][1], True)  # numerically equal
    g.equal(str(state['workbook'][2][1]) == '2130.00', False)  # but the stored form has lost the cents
    rebound = rebind_workbook(deck)
    after = chart_state(rebound)
    g.equal(after['workbook'], state['workbook'])  # replace_data rebuilds the same embedded cells
    g.equal(after['values'], state['values'])
    g.equal(after['categories'], state['categories'])
    unknown = chart_deck(['Travel', 'Facilities'], (1500.00, None), series='Budget')
    known = chart_state(unknown)
    g.equal(known['values'], [1500.0, None])  # a missing budget stays missing
    g.equal(known['values'][1] is None, True)
    g.equal(known['workbook'][2], ['Facilities', None])
    g.rejects(AssertionError, lambda: sever_workbook(deck))  # a severed workbook fails save with an empty assert
    try:
        sever_workbook(deck)
    except AssertionError as failure:
        g.equal(str(failure), '')  # the failure names neither the chart nor the missing part
    return {'cached_amounts_are_floats': True, 'embedded_workbook_drops_trailing_cents': True,
            'replace_data_rebuilds_the_workbook': True, 'unknown_value_survives_as_none': True,
            'severed_workbook_fails_with_a_bare_assert': True}


@case(168)
def a_rate_that_survives_json_is_no_longer_the_declared_rate():
    raw = '{"EUR_USD": 1.1, "GBP_USD": 1.25}'
    loose = parse_rates(raw, strict=False)
    g.equal(type(loose['EUR_USD']).__name__, 'float')
    g.rejects(TypeError, lambda: Decimal('40.00') * loose['EUR_USD'])  # a Decimal cannot multiply a float at all
    g.equal(str(Decimal(loose['EUR_USD']))[:20], '1.100000000000000088')
    g.equal(convert('40.00', loose['EUR_USD'], mode='string'), Decimal('44.00'))
    g.equal(convert('40.00', Decimal(loose['EUR_USD']), mode='float'), Decimal('44.00'))
    g.equal(convert('40.00', loose['EUR_USD'], mode='string')
            == convert('40.00', Decimal(loose['EUR_USD']), mode='float'), True)  # agrees here, so it survives review
    g.rejects(g.Blocked, lambda: convert('40.00', Decimal('1.1'), mode='decimal'))
    strict = parse_rates('{"EUR_USD": "1.1"}', strict=True)
    g.equal(strict['EUR_USD'], Decimal('1.1'))
    g.equal(strict['EUR_USD'].as_tuple().exponent, -1)  # a string-carried rate keeps its declared precision
    g.equal(json.loads('{"r": NaN}')['r'] != json.loads('{"r": NaN}')['r'], True)  # NaN admitted by default
    g.equal(json.loads('{"r": Infinity}')['r'] == float('inf'), True)
    g.rejects(g.Blocked, lambda: g.strict_json_loads('{"r": NaN}'))
    g.rejects(g.Blocked, lambda: g.strict_json_loads('{"r": 1, "r": 2}'))
    g.equal(reused_receipts(['R01', 'R02', 'R01', 'R03']), ['R01'])
    g.equal(reused_receipts(['R01', 'R02']), [])
    meals = pd.DataFrame([{'day': '2026-09-07', 'amt': Decimal('60.00')},
                          {'day': '2026-09-07', 'amt': Decimal('50.00')}])
    daily = meals.groupby('day')['amt'].sum()
    g.equal(daily['2026-09-07'], Decimal('110.00'))
    g.equal(daily['2026-09-07'] > Decimal('60.00'), True)  # both claims breach the cap; neither is chosen
    g.equal(len(meals), 2)
    return {'json_numbers_arrive_as_floats': True, 'decimal_times_float_raises': True,
            'float_and_string_paths_agree_at_this_magnitude': True,
            'json_admits_nan_and_infinity': True, 'counter_finds_the_reused_receipt': True}


@case(169)
def no_researched_primitive_conserves_the_credit_pool():
    g.equal(hamilton(100_00, [1, 1, 1], library='largest_remainder'), [3334, 3333, 3333])
    g.equal(hamilton(100_00, [1, 1, 1], library='apportionment'), [3334, 3333, 3333])
    g.equal(sum(hamilton(100_00, [1, 1, 1], library='largest_remainder')), 100_00)
    g.equal(hamilton(10_01, [1, 1], library='largest_remainder'), [501, 500])
    g.equal(hamilton(0, [1, 1, 1], library='largest_remainder'), [0, 0, 0])
    g.equal(hamilton(100_00, [0, 1], library='largest_remainder'), [0, 10000])
    g.rejects(ValueError, lambda: hamilton(-130_00, [1, 1, 1], library='largest_remainder'))
    credited = hamilton(-130_00, [1, 1, 1], library='apportionment')
    g.equal(credited, [-4333, -4333, -4333]); g.equal(sum(credited), -129_99)
    g.equal(sum(credited) == -130_00, False)  # the second library does not conserve the pool
    g.rejects(g.Blocked, lambda: hamilton(100_00, [1, 1], library='hamilton'))
    g.equal(allocate(100_00, {'ops': 1, 'sales': 1}), {'ops': 5000, 'sales': 5000})
    g.equal(sum(allocate(100_00, {'ops': 1, 'sales': 1}).values()), 100_00)
    g.equal(allocate(85_00, {'ops': 3, 'sales': 1}), {'ops': 6375, 'sales': 2125})
    g.rejects(g.Blocked, lambda: allocate(85_00, {'ops': 3, 'sales': None}))  # the pool stays unallocated
    g.rejects(g.Blocked, lambda: allocate(-130_00, {'ops': 1, 'sales': 1}))  # and a credit is Blocked
    return {'largest_remainder_refuses_a_negative_total': True,
            'apportionment_loses_a_cent_on_a_credit': True,
            'credit_pool_has_no_conserving_primitive': True,
            'missing_weight_holds_the_pool': True}


@case(170)
def two_exceptions_mean_no_break_even_and_a_negative_one_means_nothing():
    g.equal(minimum_volume('725.25', '11.00'), Decimal('66'))
    g.equal(str(Decimal('725.25') / Decimal('11.00'))[:8], '65.93181')
    g.equal(profit(65, '11.00', '725.25'), Decimal('-10.25'))
    g.equal(profit(66, '11.00', '725.25'), Decimal('0.75'))
    g.equal(profit(70, '11.00', '725.25'), Decimal('44.75'))
    g.rejects(g.Blocked, lambda: minimum_volume('725.25', '0.00'))  # DivisionByZero
    g.rejects(g.Blocked, lambda: minimum_volume('0.00', '0.00'))  # InvalidOperation, a different exception
    caught = []
    for fixed, contribution in (('725.25', '0.00'), ('0.00', '0.00')):
        try:
            minimum_volume(fixed, contribution)
        except g.Blocked as blocked:
            caught.append(str(blocked)[:12])
    g.equal(len(caught), 2); g.equal(caught[0] != caught[1], True)
    g.equal(minimum_volume('725.25', '-1.00'), Decimal('-725'))  # a negative contribution yields a negative volume
    g.equal(minimum_volume('725.25', '-1.00') < 0, True)  # arithmetically fine and not a supported volume
    g.equal(minimum_volume('725.25', '-1.00', rounding=ROUND_UP), Decimal('-726'))
    g.equal(minimum_volume('725.25', '-1.00') == minimum_volume('725.25', '-1.00', rounding=ROUND_UP), False)
    g.equal(Decimal('-65.9').to_integral_value(ROUND_CEILING), Decimal('-65'))
    g.equal(Decimal('-65.9').to_integral_value(ROUND_UP), Decimal('-66'))
    g.equal(minimum_volume('660.00', '11.00'), Decimal('60'))  # an exact quotient is not rounded up
    g.equal(profit(60, '11.00', '660.00'), Decimal('0.00'))
    whole = volume_range(0, 101, step=1)
    g.equal(len(whole), 101); g.equal(whole[0], 0); g.equal(whole[-1], 100)
    drifting = volume_range(0, 1, step=0.1)
    g.equal(len(drifting), 10); g.equal(drifting[-1], 0.9)  # the declared endpoint is not enumerated
    g.equal(0.7 in drifting, False)  # nor is a value the declared step should produce
    g.equal(len(volume_range(0, 1.0001, step=0.1)), 11)
    return {'zero_and_undetermined_raise_different_exceptions': True,
            'negative_contribution_yields_a_negative_volume': True,
            'ceiling_and_up_disagree_on_negatives': True, 'float_step_drops_the_endpoint': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['apportionment', 'largest-remainder', 'numpy', 'odfpy', 'openpyxl', 'pandas',
                'pandera', 'PyMuPDF', 'python-pptx', 'rapidfuzz']
    here = Path(__file__).resolve().parent
    return {'scope': 'Bounded authored cash-flow, presentation, PDF, lexical, OpenDocument, chart, expense, allocation and break-even fixtures and reproduced library defaults; the original P161-P170 chains and their artifacts were not rerun.',
            'test_cases': len(rows), 'passed': sum(r['status'] == 'passed' for r in rows), 'failed': sum(r['status'] == 'failed' for r in rows),
            'assertions': g.ASSERTIONS, 'full_chains_executed': 0, 'network_calls': 0, 'business_actions': 0,
            'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256': {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in ['handoff_guards_v1.py']},
            'library_versions': {n: importlib.metadata.version(n) for n in packages}, 'results': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    result = run(); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ['test_cases', 'passed', 'failed', 'assertions']}))
    if result['failed']:
        print('\n'.join(r['error'] for r in result['results'] if r['error'])); raise SystemExit(1)
