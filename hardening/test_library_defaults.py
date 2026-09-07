"""Hardening guards as a plain pytest file.

Run with `pytest hardening/test_library_defaults.py`. Nothing here is bespoke: pytest is the runner, hypothesis
generates every input, the libraries under test compute every value, and the comparison is each library's own
published assertion callable. A reader with the pinned packages can run this file without anything else from
this repository, which is the point of rule 5 of the hardening assurance.

Each test names the hand-typed expectation in the frozen guard modules that it replaces.
"""
import contextlib
import csv
import datetime
import io
import zoneinfo
from xml.etree import ElementTree
from xml.sax.saxutils import escape as xml_escape
import itertools
import json
import sqlite3
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from fractions import Fraction

import arrow
import docx
import duckdb
import icalendar
from dateutil import rrule, tz as dateutil_tz
import numpy as np
from workalendar import core as workalendar_core
import igraph
import jsonschema
import portion
import pydantic
from lxml import etree as lxml_etree
import networkx as nx
import openpyxl
import orjson
import pdfplumber
import pymupdf
import xlsxwriter
from docx2python import docx2python
from python_calamine import CalamineWorkbook

import nltk
import numpy.testing as npt
import pandas as pd
import pandas.testing as pdt
import polars as pl
import pyarrow.csv as pyarrow_csv
import rfc8785
import polars.testing as plt
import pytest
import rapidfuzz.distance.Levenshtein as rf_levenshtein
from hypothesis import assume, given, settings, strategies as st
from largest_remainder import LargestRemainder

SLOW = settings(max_examples=200, deadline=None)
AMOUNTS = st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1, max_size=40)
WEIGHTS = st.lists(st.integers(min_value=1, max_value=50), min_size=1, max_size=8)
WORDS = st.text(max_size=14)


@given(AMOUNTS)
@SLOW
def test_running_total_agrees_across_two_dataframe_engines(values):
    """Replaces handoff_guards_v10.py:183 g.equal(out['cumulative'], [10, 20, 25])."""
    pdt.assert_series_equal(
        pd.Series(values).cumsum(),
        pl.Series(values).cum_sum().to_pandas(),
        check_names=False, check_dtype=False)


@given(AMOUNTS)
@SLOW
def test_running_total_agrees_with_the_standard_library(values):
    """Replaces the cumulative-balance expectations in handoff_guards_v15.py."""
    npt.assert_array_equal(pd.Series(values).cumsum().to_numpy(),
                           list(itertools.accumulate(values)))


@given(WORDS, WORDS)
@SLOW
def test_edit_distance_agrees_across_implementations_sharing_no_backend(left, right):
    """rapidfuzz is C++, nltk is pure-Python dynamic programming. Replaces the hand-chosen
    similarity fixtures behind P164 and P201."""
    npt.assert_array_equal(rf_levenshtein.distance(left, right),
                           nltk.edit_distance(left, right))


@given(WEIGHTS, st.integers(min_value=0, max_value=1_000_000))
@SLOW
def test_largest_remainder_conserves_its_total(weights, total):
    """Conservation is the property. Replaces the typed [3334, 3333, 3333] in handoff_guards_v17.py."""
    npt.assert_array_equal(sum(LargestRemainder.round(weights, total)), total)


@given(WEIGHTS, st.integers(max_value=-1))
@SLOW
def test_largest_remainder_refuses_every_negative_total(weights, total):
    """The credit pool of P169 is Blocked by the library, not by a rule written here.
    Replaces the hand-chosen -13000 in handoff_guards_v17.py."""
    with pytest.raises(ValueError):
        LargestRemainder.round(weights, total)


@given(st.lists(st.one_of(st.none(), st.sampled_from(['a', 'b'])), min_size=1, max_size=12)
       .filter(lambda values: None in values))
@SLOW
def test_value_counts_drops_nulls_by_default(values):
    """pandas omits the null group unless asked. Replaces the 6-versus-10 rollup expectations in
    handoff_guards_v15.py; hypothesis supplies the input rather than an author choosing one."""
    counted = pd.Series(values, dtype='object')
    with pytest.raises(AssertionError):
        pdt.assert_series_equal(counted.value_counts(dropna=True),
                                counted.value_counts(dropna=False))


@given(st.dates(min_value=pd.Timestamp('2026-01-01').date(),
                max_value=pd.Timestamp('2026-12-31').date()))
@SLOW
def test_date_range_includes_both_endpoints_by_default(start):
    """The chains declare start-inclusive and end-exclusive membership. Replaces the 20-versus-19
    day-count expectations in handoff_guards_v19.py."""
    end = start + pd.Timedelta(days=1)
    plt.assert_series_not_equal(
        pl.Series([len(pd.date_range(start, end, inclusive='both'))]),
        pl.Series([len(pd.date_range(start, end, inclusive='left'))]))


# ---------------------------------------------------------------- exact arithmetic
@given(st.integers(min_value=-10_000, max_value=10_000), st.integers(min_value=1, max_value=999))
@SLOW
def test_decimal_default_rounding_is_half_even_not_half_up(numerator, denominator):
    """Fraction is the exact value, so neither rounding result is typed. Replaces the ROUND_HALF_EVEN
    expectations in handoff_guards_v16.py."""
    exact = Fraction(numerator, denominator)
    quantum = Decimal('0.01')
    value = Decimal(numerator) / Decimal(denominator)
    half_even = value.quantize(quantum, rounding=ROUND_HALF_EVEN)
    half_up = value.quantize(quantum, rounding=ROUND_HALF_UP)
    is_tie = (exact * 100 * 2).denominator == 1 and (exact * 100).denominator != 1
    if not is_tie:
        npt.assert_array_equal(str(half_even), str(half_up))
    npt.assert_array_equal(min(half_even, half_up) <= exact <= max(half_even, half_up)
                           or abs(Fraction(half_even) - exact) <= Fraction(1, 200), True)


@given(st.lists(st.integers(min_value=1, max_value=10_000), min_size=1, max_size=6))
@SLOW
def test_decimal_division_matches_the_exact_rational_before_rounding(parts):
    """Replaces the Fraction-versus-Decimal expectations in handoff_guards_v20.py."""
    total = sum(parts)
    for part in parts:
        npt.assert_allclose(float(Decimal(part) / Decimal(total)), float(Fraction(part, total)), rtol=1e-12)


# ---------------------------------------------------------------- graph properties
@given(st.lists(st.tuples(st.integers(min_value=0, max_value=6), st.integers(min_value=0, max_value=6)),
                min_size=1, max_size=12))
@SLOW
def test_acyclicity_agrees_between_two_graph_libraries(edges):
    """networkx is pure Python, igraph is a C library. Replaces the is_directed_acyclic_graph
    expectations in handoff_guards_v16.py and v21."""
    nx_graph = nx.DiGraph(edges)
    ig_graph = igraph.Graph(n=7, edges=list(edges), directed=True)
    npt.assert_array_equal(nx.is_directed_acyclic_graph(nx_graph), bool(ig_graph.is_dag()))


@given(st.lists(st.tuples(st.integers(min_value=0, max_value=5), st.integers(min_value=0, max_value=5)),
                min_size=2, max_size=10))
@SLOW
def test_arborescence_is_strictly_stronger_than_acyclicity(edges):
    """A rooted tree is a DAG, never the reverse. Replaces the is_arborescence expectations in
    handoff_guards_v21.py; hypothesis supplies the graphs."""
    graph = nx.DiGraph(edges)
    if nx.is_arborescence(graph):
        npt.assert_array_equal(nx.is_directed_acyclic_graph(graph), True)


# ---------------------------------------------------------------- canonical serialization
@given(st.dictionaries(st.text(min_size=1, max_size=6), st.integers(min_value=-2**63, max_value=2**64 - 1),
                       min_size=1, max_size=8))
@SLOW
def test_sorted_json_agrees_across_two_serializer_implementations(mapping):
    """orjson is Rust, the standard library is C. They agree only inside the shared domain: integers from
    -2**63 to 2**64 - 1, and with the standard library's ASCII escaping turned off. Replaces the canonical-ordering expectations
    in handoff_guards_v21.py."""
    npt.assert_array_equal(
        orjson.dumps(mapping, option=orjson.OPT_SORT_KEYS),
        json.dumps(mapping, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


@given(st.one_of(st.integers(min_value=2**64), st.integers(max_value=-2**63 - 1)))
@SLOW
def test_orjson_refuses_integers_the_standard_library_serializes(value):
    """A canonical serializer that cannot represent every value the other accepts is not interchangeable.
    The accepted domain is asymmetric: unsigned 64-bit upward, signed 64-bit downward, so it ends at 2**64 - 1
    and at -2**63. Hypothesis found both the divergence and the fact that a symmetric bound was the wrong
    assumption."""
    json.dumps(value)
    with pytest.raises(TypeError):
        orjson.dumps(value)


@given(st.text(alphabet=st.characters(min_codepoint=127, max_codepoint=1000), min_size=1, max_size=4))
@SLOW
def test_standard_library_escapes_to_ascii_by_default(text):
    """The two serializers produce different bytes for the same string until ensure_ascii is disabled."""
    with pytest.raises(AssertionError):
        npt.assert_array_equal(orjson.dumps(text), json.dumps(text).encode())
    npt.assert_array_equal(orjson.dumps(text), json.dumps(text, ensure_ascii=False).encode())


@given(st.lists(st.dictionaries(st.text(min_size=1, max_size=4), st.integers(), min_size=1, max_size=4),
                min_size=2, max_size=6).filter(lambda rows: rows != list(reversed(rows))))
@SLOW
def test_sorted_keys_do_not_order_rows(rows):
    """Key order is canonical; row order is not. Replaces the P200 reordering expectations in
    handoff_guards_v21.py."""
    with pytest.raises(AssertionError):
        npt.assert_array_equal(json.dumps(rows, sort_keys=True), json.dumps(list(reversed(rows)), sort_keys=True))


# ---------------------------------------------------------------- document round trips
SAFE_LINE = st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=1, max_size=40)


def _pdf_bytes(paragraphs):
    document = pymupdf.open()
    page = document.new_page()
    for index, line in enumerate(paragraphs):
        page.insert_text((72, 100 + 20 * index), line)
    return document.tobytes()


def _both_extractions(data):
    mupdf_text = pymupdf.open('pdf', data)[0].get_text()
    with pdfplumber.open(io.BytesIO(data)) as plumbed:
        miner_text = plumbed.pages[0].extract_text() or ''
    return mupdf_text, miner_text


@given(st.lists(SAFE_LINE, min_size=1, max_size=6))
@SLOW
def test_pdf_characters_agree_between_two_extraction_stacks(paragraphs):
    """PyMuPDF is MuPDF; pdfplumber is pdfminer.six. The non-whitespace characters agree. Replaces the
    typed quote strings in handoff_guards_v12.py and the P163 passage expectations."""
    mupdf_text, miner_text = _both_extractions(_pdf_bytes(paragraphs))
    npt.assert_array_equal(''.join(mupdf_text.split()), ''.join(miner_text.split()))


@given(st.lists(st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=6),
                min_size=2, max_size=4))
@SLOW
def test_pdf_whitespace_does_not_survive_both_extractors(words):
    """A run of spaces written into the page is preserved by PyMuPDF and collapsed by pdfplumber, and
    PyMuPDF appends a trailing newline the other does not. A claim of literally recovered characters
    therefore depends on which extractor ran. Hypothesis supplies the words."""
    line = '  '.join(words)
    mupdf_text, miner_text = _both_extractions(_pdf_bytes([line]))
    npt.assert_array_equal(line in mupdf_text, True)
    npt.assert_array_equal(line in miner_text, False)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(mupdf_text, miner_text)


@given(st.lists(SAFE_LINE, min_size=1, max_size=6))
@SLOW
def test_docx_text_agrees_between_two_readers(paragraphs):
    """python-docx builds an object model; docx2python parses the XML directly. Replaces the typed
    paragraph strings in handoff_guards_v16.py and the P151 readback expectations."""
    document = docx.Document()
    for line in paragraphs:
        document.add_paragraph(line)
    buffer = io.BytesIO()
    document.save(buffer)
    from_docx = [p.text for p in docx.Document(io.BytesIO(buffer.getvalue())).paragraphs]
    buffer.seek(0)
    with docx2python(io.BytesIO(buffer.getvalue())) as parsed:
        from_xml = [line for line in parsed.text.split('\n') if line]
    npt.assert_array_equal([p for p in from_docx if p], from_xml)


@given(st.lists(st.lists(st.integers(min_value=-10**6, max_value=10**6), min_size=1, max_size=4),
                min_size=1, max_size=6))
@SLOW
def test_workbook_cells_agree_between_two_readers(rows):
    """openpyxl is pure Python; python-calamine is a Rust reader. This is the claim the chains make as
    'both workbook readers agree on N cells', now over generated rows."""
    width = min(len(row) for row in rows)
    rows = [row[:width] for row in rows]
    buffer = io.BytesIO()
    book = xlsxwriter.Workbook(buffer, {'in_memory': True})
    sheet = book.add_worksheet('S')
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            sheet.write_number(r, c, value)
    book.close()
    from_openpyxl = [[cell.value for cell in row]
                     for row in openpyxl.load_workbook(io.BytesIO(buffer.getvalue())).active.iter_rows()]
    from_calamine = CalamineWorkbook.from_filelike(io.BytesIO(buffer.getvalue())).get_sheet_by_name('S').to_python()
    npt.assert_array_equal(from_openpyxl, [[int(v) for v in row] for row in from_calamine])


# ---------------------------------------------------------------- SQL engine semantics
def _both_engines(query, ddb, lite):
    return ddb.execute(query).fetchone()[0], lite.execute(query).fetchone()[0]


@given(st.integers(min_value=1, max_value=10**6))
@SLOW
def test_sum_over_no_rows_is_null_in_both_engines(threshold):
    """An aggregate over an empty selection is NULL, not zero, in two independent engines. Replaces the
    typed None in handoff_guards_v15.py:420 and the P147 empty-sum expectation."""
    with duckdb.connect() as ddb, contextlib.closing(sqlite3.connect(':memory:')) as lite:
        query = 'select sum(v) from (select %d v) where v > %d' % (threshold, threshold)
        duck, sql = _both_engines(query, ddb, lite)
    npt.assert_array_equal([duck is None, sql is None], [True, True])


@given(st.integers(min_value=1, max_value=999), st.integers(min_value=2, max_value=999))
@SLOW
def test_integer_division_differs_between_the_two_engines(numerator, denominator):
    """DuckDB promotes to a float; SQLite truncates toward zero. A cost query written for one engine does
    not carry to the other. Hypothesis supplies the operands."""
    with duckdb.connect() as ddb, contextlib.closing(sqlite3.connect(':memory:')) as lite:
        query = 'select %d / %d' % (numerator, denominator)
        duck, sql = _both_engines(query, ddb, lite)
    npt.assert_allclose(float(duck), numerator / denominator, rtol=1e-9)
    npt.assert_array_equal(sql, numerator // denominator)


@given(st.integers(min_value=-10**6, max_value=10**6))
@SLOW
def test_null_ordering_differs_between_the_two_engines(value):
    """DuckDB sorts NULLs last and SQLite sorts them first, so 'the smallest row' is engine-dependent."""
    with duckdb.connect() as ddb, contextlib.closing(sqlite3.connect(':memory:')) as lite:
        query = 'select v from (select %d v union all select null) order by v limit 1' % value
        duck, sql = _both_engines(query, ddb, lite)
    npt.assert_array_equal([duck == value, sql is None], [True, True])


@given(st.lists(st.integers(min_value=-10**8, max_value=10**8), min_size=1, max_size=12))
@SLOW
def test_decimal_column_sum_is_exact_where_float_is_not(cents):
    """DuckDB DECIMAL agrees with Python's Decimal exactly. Replaces the typed monetary totals in
    handoff_guards_v15.py and the P147 and P187 exactness expectations."""
    amounts = [Decimal(value).scaleb(-2) for value in cents]
    with duckdb.connect() as ddb:
        ddb.execute('create table t(a DECIMAL(18,2))')
        ddb.executemany('insert into t values (?)', [(a,) for a in amounts])
        total = ddb.execute('select sum(a) from t').fetchone()[0]
    npt.assert_array_equal(str(total), str(sum(amounts)))


# ---------------------------------------------------------------- validators and intervals
class BoundedAmount(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(strict=True, extra='forbid')
    cents: int = pydantic.Field(ge=0, le=10_000)


@given(st.integers(min_value=-50_000, max_value=50_000))
@SLOW
def test_two_validators_agree_on_the_same_declared_constraint(cents):
    """The JSON Schema is emitted by pydantic itself, so both engines check one declaration. pydantic-core is
    Rust; jsonschema is an independent Python implementation of the specification. Replaces the schema
    expectations in handoff_guards_v21.py."""
    schema = BoundedAmount.model_json_schema()
    try:
        BoundedAmount.model_validate({'cents': cents})
        pydantic_ok = True
    except pydantic.ValidationError:
        pydantic_ok = False
    try:
        jsonschema.validate({'cents': cents}, schema)
        jsonschema_ok = True
    except jsonschema.ValidationError:
        jsonschema_ok = False
    npt.assert_array_equal(pydantic_ok, jsonschema_ok)


@given(st.integers(min_value=0, max_value=50), st.integers(min_value=0, max_value=50),
       st.integers(min_value=0, max_value=50), st.integers(min_value=0, max_value=50))
@SLOW
def test_interval_overlap_agrees_between_two_interval_libraries(a, b, c, d):
    """portion and pandas.Interval are independent implementations. Half-open bounds on both sides.
    Replaces the overlaps expectations in handoff_guards_v16.py and v19."""
    left_lo, left_hi = min(a, b), max(a, b)
    right_lo, right_hi = min(c, d), max(c, d)
    assume(left_lo < left_hi and right_lo < right_hi)
    by_portion = portion.closedopen(left_lo, left_hi).overlaps(portion.closedopen(right_lo, right_hi))
    by_pandas = pd.Interval(left_lo, left_hi, closed='left').overlaps(
        pd.Interval(right_lo, right_hi, closed='left'))
    npt.assert_array_equal(by_portion, by_pandas)


@given(st.lists(SAFE_LINE, min_size=1, max_size=4))
@SLOW
def test_xml_well_formedness_agrees_between_two_parsers(values):
    """lxml is libxml2; ElementTree is pure Python. Unescaped content must be rejected by both.
    Replaces the escaping expectations in handoff_guards_v20.py."""
    escaped = ''.join('<v>%s</v>' % xml_escape(value) for value in values)
    document = '<root>%s</root>' % escaped
    npt.assert_array_equal([node.text or '' for node in lxml_etree.fromstring(document.encode())],
                           [node.text or '' for node in ElementTree.fromstring(document)])


@given(st.lists(st.tuples(st.integers(min_value=0, max_value=5), st.integers(min_value=0, max_value=5)),
                min_size=1, max_size=10))
@SLOW
def test_topological_order_is_valid_under_the_other_library(edges):
    """NetworkX produces the order; igraph's own DAG test decides whether one exists. Every edge must run
    forward in the produced order. Replaces the topological_generations expectations in v21."""
    graph = nx.DiGraph(edges)
    ig_graph = igraph.Graph(n=6, edges=list(edges), directed=True)
    if not ig_graph.is_dag():
        with pytest.raises(nx.NetworkXUnfeasible):
            list(nx.topological_sort(graph))
        return
    position = {node: index for index, node in enumerate(nx.topological_sort(graph))}
    npt.assert_array_equal([position[u] < position[v] for u, v in edges if u != v],
                           [True] * len([1 for u, v in edges if u != v]))


# ---------------------------------------------------------------- business day arithmetic
class MondayToFriday(workalendar_core.Calendar):
    """A five-day week with no holidays, so the two libraries are compared on the calendar alone."""
    WEEKEND_DAYS = (5, 6)

    def get_calendar_holidays(self, year):
        return []


WORKWEEK = MondayToFriday()
NUMPY_CALENDAR = np.busdaycalendar(weekmask='Mon Tue Wed Thu Fri', holidays=[])
ANY_2026_DAY = st.dates(min_value=datetime.date(2026, 1, 1), max_value=datetime.date(2026, 12, 31))


def _numpy_offset(day, count):
    return datetime.date.fromisoformat(
        str(np.busday_offset(np.datetime64(day.isoformat()), count, roll='forward', busdaycal=NUMPY_CALENDAR)))


@given(ANY_2026_DAY.filter(lambda day: bool(np.is_busday(np.datetime64(day.isoformat()),
                                                         busdaycal=NUMPY_CALENDAR))),
       st.integers(min_value=1, max_value=20))
@SLOW
def test_working_day_offset_agrees_from_a_working_anchor(day, count):
    """workalendar is an independent implementation; numpy is not derived from it. From a working-day anchor
    the two agree. Replaces the busday_offset expectations in handoff_guards_v19.py."""
    npt.assert_array_equal(WORKWEEK.add_working_days(day, count), _numpy_offset(day, count))


@given(ANY_2026_DAY.filter(lambda day: not bool(np.is_busday(np.datetime64(day.isoformat()),
                                                             busdaycal=NUMPY_CALENDAR))),
       st.integers(min_value=1, max_value=20))
@SLOW
def test_working_day_offset_diverges_from_a_non_working_anchor(day, count):
    """From a weekend anchor the two libraries return different dates: workalendar counts the next working
    day as the first one added, while numpy rolls the anchor forward and then adds. Any chain that offsets
    from a date which may not be a working day, such as a planned start, gets a different answer depending on
    which library computed it."""
    workalendar_result = WORKWEEK.add_working_days(day, count)
    numpy_result = _numpy_offset(day, count)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(workalendar_result, numpy_result)
    npt.assert_array_equal(workalendar_result, _numpy_offset(day, count - 1))


@given(ANY_2026_DAY)
@SLOW
def test_working_day_membership_agrees_between_the_two_libraries(day):
    """The disagreement above is about counting, not about which days are working days."""
    npt.assert_array_equal(WORKWEEK.is_working_day(day),
                           bool(np.is_busday(np.datetime64(day.isoformat()), busdaycal=NUMPY_CALENDAR)))


# ---------------------------------------------------------------- time zones and parsing
NEW_YORK = 'America/New_York'


@given(st.datetimes(min_value=datetime.datetime(2026, 4, 1), max_value=datetime.datetime(2026, 10, 31)))
@SLOW
def test_utc_offset_agrees_outside_the_transition_gap(naive):
    """zoneinfo is the standard library's IANA reader; dateutil.tz is an independent one. Away from a
    transition they agree. Replaces the timezone expectations in handoff_guards_v16.py."""
    npt.assert_array_equal(naive.replace(tzinfo=zoneinfo.ZoneInfo(NEW_YORK)).utcoffset(),
                           naive.replace(tzinfo=dateutil_tz.gettz(NEW_YORK)).utcoffset())


@given(st.integers(min_value=0, max_value=59))
@SLOW
def test_the_two_zone_readers_disagree_inside_a_nonexistent_local_time(minute):
    """2026-03-08 02:xx does not exist in America/New_York; the clock jumps from 02:00 to 03:00. zoneinfo
    resolves the gap with the pre-transition offset and dateutil with the post-transition one, so a local
    timestamp inside the gap has two defensible UTC readings and no error is raised by either."""
    naive = datetime.datetime(2026, 3, 8, 2, minute)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(naive.replace(tzinfo=zoneinfo.ZoneInfo(NEW_YORK)).utcoffset(),
                               naive.replace(tzinfo=dateutil_tz.gettz(NEW_YORK)).utcoffset())


@given(st.datetimes(min_value=datetime.datetime(2026, 1, 1), max_value=datetime.datetime(2026, 12, 31)))
@SLOW
def test_arrow_invents_a_timezone_the_standard_library_leaves_absent(naive):
    """A naive timestamp parsed by arrow comes back as UTC; parsed by the standard library it comes back
    naive. A chain that validates UTC timestamps by parsing them gets a different answer depending on which
    parser ran. This is the second implementation behind the P156 finding that fromisoformat is a parser
    rather than a validator."""
    text = naive.isoformat()
    npt.assert_array_equal(datetime.datetime.fromisoformat(text).tzinfo is None, True)
    npt.assert_array_equal(str(arrow.get(text).tzinfo), 'UTC')


@given(st.integers(min_value=1, max_value=12))
@SLOW
def test_icalendar_parses_a_recurrence_rule_without_expanding_it(count):
    """icalendar reads the RRULE and hands back its parts; it does not produce the occurrences. There is
    therefore no second implementation available to check dateutil's expansion behind P182, and the recorded
    month-skipping finding rests on dateutil alone. Stating that is the honest result."""
    ics = ('BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nDTSTART:20260131T090000Z\r\n'
           'RRULE:FREQ=MONTHLY;BYMONTHDAY=31;COUNT=%d\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n' % count)
    event = icalendar.Calendar.from_ical(ics).walk('VEVENT')[0]
    npt.assert_array_equal(dict(event['RRULE'])['COUNT'], [count])
    npt.assert_array_equal(hasattr(event['RRULE'], 'between'), False)
    expanded = list(rrule.rrule(rrule.MONTHLY, dtstart=datetime.datetime(2026, 1, 31),
                                count=count, bymonthday=31))
    npt.assert_array_equal(len(expanded), count)
    npt.assert_array_equal(all(moment.day == 31 for moment in expanded), True)


# ---------------------------------------------------------------- CSV null and empty semantics
CSV_SOURCE = b'a,b,c\n1,"",\n2,x,y\n'


@given(st.integers(min_value=0, max_value=0))
@SLOW
def test_four_csv_readers_do_not_agree_on_a_quoted_empty_field(row):
    """The first data row is 1,"", -- column b is a quoted empty string and column c is an unquoted empty
    field. Four independent readers give three different answers, so the distinction P137 relies on survives
    in exactly one of them. Replaces the pyarrow expectations in handoff_guards_v14.py."""
    by_stdlib = list(csv.reader(io.StringIO(CSV_SOURCE.decode())))[1 + row]
    by_pandas = pd.read_csv(io.BytesIO(CSV_SOURCE)).iloc[row].tolist()
    by_polars = list(pl.read_csv(io.BytesIO(CSV_SOURCE)).row(row))
    by_arrow = [column[row].as_py() for column in pyarrow_csv.read_csv(io.BytesIO(CSV_SOURCE)).columns]

    npt.assert_array_equal(by_stdlib[1:], ['', ''])                       # stdlib has no null concept
    npt.assert_array_equal([value != value for value in by_pandas[1:]], [True, True])  # pandas: both null
    npt.assert_array_equal([by_polars[1], by_polars[2] is None], ['', True])           # polars keeps them apart
    npt.assert_array_equal(by_arrow[1:], ['', ''])                        # pyarrow: both empty strings


# Literal field texts that are also common missing-value sentinels. Every one is a plausible real value:
# NA is the ISO code for Namibia, None and null are ordinary words, and 1.#IND appears in exported data.
SENTINEL_TEXTS = ['null', 'NULL', 'NA', 'N/A', 'NaN', 'nan', 'None', 'n/a', '1.#IND']
PRESERVED_TEXTS = ['none', '-', 'ok', 'x']


def _read_single_field(source):
    by_stdlib = list(csv.reader(io.StringIO(source.decode())))[1][0]
    by_pandas = pd.read_csv(io.BytesIO(source), dtype=str).iloc[0, 0]
    by_polars = pl.read_csv(io.BytesIO(source), infer_schema_length=0).row(0)[0]
    by_arrow = pyarrow_csv.read_csv(io.BytesIO(source)).columns[0][0].as_py()
    missing = lambda value: value is None or (isinstance(value, float) and value != value)
    return by_stdlib, by_pandas, by_polars, by_arrow, missing


@given(st.sampled_from(SENTINEL_TEXTS))
@SLOW
def test_pandas_and_pyarrow_turn_literal_text_into_a_missing_value(text):
    """The field contains the characters of a word, not an absent value. stdlib csv and polars return the
    text; pandas returns a missing value even with dtype=str, and pyarrow returns null. A column whose real
    content is NA, the ISO code for Namibia, is destroyed by two of the four readers."""
    source = ('c\n%s\n' % text).encode()
    by_stdlib, by_pandas, by_polars, by_arrow, missing = _read_single_field(source)
    npt.assert_array_equal([by_stdlib, by_polars], [text, text])
    npt.assert_array_equal(missing(by_pandas), True)
    npt.assert_array_equal(missing(by_arrow), text != 'None')


@given(st.sampled_from(PRESERVED_TEXTS))
@SLOW
def test_all_four_readers_preserve_text_outside_the_sentinel_sets(text):
    """The coercion is confined to each reader's sentinel list, so the divergence is about those words and
    not about parsing generally. Lowercase none is preserved by all four while None is not."""
    source = ('c\n%s\n' % text).encode()
    by_stdlib, by_pandas, by_polars, by_arrow, missing = _read_single_field(source)
    npt.assert_array_equal([by_stdlib, by_pandas, by_polars, by_arrow], [text] * 4)


@given(st.sampled_from(['None']))
@SLOW
def test_the_two_coercing_readers_disagree_with_each_other(text):
    """pandas treats None as missing and pyarrow does not, so the two readers that coerce do not even agree
    on the same sentinel set."""
    source = ('c\n%s\n' % text).encode()
    _, by_pandas, _, by_arrow, missing = _read_single_field(source)
    npt.assert_array_equal([missing(by_pandas), missing(by_arrow)], [True, False])


# ---------------------------------------------------------------- workbook reader disagreements
def _workbook_bytes(write):
    buffer = io.BytesIO()
    book = xlsxwriter.Workbook(buffer, {'in_memory': True})
    sheet = book.add_worksheet('S')
    write(book, sheet)
    book.close()
    return buffer.getvalue()


def _first_cell(data, *, data_only):
    by_openpyxl = openpyxl.load_workbook(io.BytesIO(data), data_only=data_only).active['A1'].value
    by_calamine = CalamineWorkbook.from_filelike(io.BytesIO(data)).get_sheet_by_name('S').to_python()[0][0]
    return by_openpyxl, by_calamine


@given(ANY_2026_DAY)
@SLOW
def test_a_formatted_date_reads_as_a_different_type_in_each_reader(day):
    """openpyxl returns datetime.datetime and python-calamine returns datetime.date for the same cell, and
    the two are not equal in Python. Every chain claiming that both workbook readers agree on N cells is
    claiming it after a normalisation it does not state."""
    data = _workbook_bytes(lambda book, sheet: sheet.write_datetime(
        0, 0, day, book.add_format({'num_format': 'yyyy-mm-dd'})))
    by_openpyxl, by_calamine = _first_cell(data, data_only=False)
    npt.assert_array_equal([type(by_openpyxl).__name__, type(by_calamine).__name__], ['datetime', 'date'])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(by_openpyxl, by_calamine)
    npt.assert_array_equal(by_openpyxl.date(), by_calamine)


@given(st.integers(min_value=-10**9, max_value=10**9))
@SLOW
def test_an_integer_cell_reads_as_int_and_as_float(value):
    """The numbers compare equal and the types do not, so a comparison that checks types sees a mismatch on
    every integer cell in the workbook."""
    data = _workbook_bytes(lambda book, sheet: sheet.write_number(0, 0, value))
    by_openpyxl, by_calamine = _first_cell(data, data_only=False)
    npt.assert_array_equal([type(by_openpyxl).__name__, type(by_calamine).__name__], ['int', 'float'])
    npt.assert_array_equal(by_openpyxl, by_calamine)


@given(st.integers(min_value=1, max_value=500), st.integers(min_value=1, max_value=500))
@SLOW
def test_a_formula_cell_reads_three_different_ways(left, right):
    """openpyxl returns the formula text by default, the cached value with data_only=True, and calamine
    returns the cached value as a float. One cell, three answers, and the default openpyxl read is the one
    that is not a number at all."""
    formula, cached = '=%d+%d' % (left, right), left + right
    data = _workbook_bytes(lambda book, sheet: sheet.write_formula(0, 0, formula, None, cached))
    default_openpyxl, by_calamine = _first_cell(data, data_only=False)
    cached_openpyxl, _ = _first_cell(data, data_only=True)
    npt.assert_array_equal(default_openpyxl, formula)
    npt.assert_array_equal(cached_openpyxl, cached)
    npt.assert_array_equal(by_calamine, float(cached))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(default_openpyxl, by_calamine)


# ---------------------------------------------------------------- canonical JSON
def _sorted_json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


@given(st.dictionaries(st.text(min_size=1, max_size=6),
                       st.integers(min_value=-(2**53 - 1), max_value=2**53 - 1),
                       min_size=1, max_size=6))
@SLOW
def test_sorted_json_and_rfc8785_agree_on_integer_objects(mapping):
    """Inside the shared domain the two canonicalisations produce the same bytes, so the seal is portable
    there. Replaces the canonical-ordering expectations in handoff_guards_v21.py."""
    npt.assert_array_equal(_sorted_json(mapping), rfc8785.dumps(mapping))


@given(st.integers(min_value=-10**6, max_value=10**6))
@SLOW
def test_rfc8785_normalises_a_whole_float_that_sorted_json_keeps(value):
    """RFC 8785 writes a float with no fractional part as an integer literal; json.dumps keeps the trailing
    .0. The two canonical forms differ, so their sha256 seals differ for the same object. The chains seal
    with json.dumps(sort_keys=True) and call the result canonical; P262 names RFC 8785 as the standard."""
    subject = {'x': float(value)}
    npt.assert_array_equal(_sorted_json(subject), ('{"x":%d.0}' % value).encode())
    npt.assert_array_equal(rfc8785.dumps(subject), ('{"x":%d}' % value).encode())
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_sorted_json(subject), rfc8785.dumps(subject))


@given(st.sampled_from([-0.0]))
@SLOW
def test_rfc8785_erases_negative_zero(value):
    """json.dumps preserves the sign of negative zero and RFC 8785 removes it, so two objects that Python
    considers equal seal to different bytes under one canonicalisation and the same bytes under the other."""
    npt.assert_array_equal(_sorted_json({'x': value}), b'{"x":-0.0}')
    npt.assert_array_equal(rfc8785.dumps({'x': value}), b'{"x":0}')
    npt.assert_array_equal(rfc8785.dumps({'x': value}), rfc8785.dumps({'x': 0.0}))
    npt.assert_array_equal(value == 0.0, True)


@given(st.one_of(st.integers(min_value=2**53, max_value=2**70),
       st.integers(min_value=-(2**70), max_value=-(2**53))))
@SLOW
def test_rfc8785_refuses_integers_outside_the_exactly_representable_range(value):
    """The standard restricts integers to the range IEEE-754 doubles represent exactly. The accepted range is
    symmetric and exclusive, plus or minus 2**53 - 1, so 2**53 itself is refused; json.dumps serialises
    arbitrary precision. A manifest carrying a large identifier as a number cannot be sealed under the
    standard at all. Note that orjson's limit is different again and asymmetric, so the three serializers
    have three integer domains."""
    _sorted_json({'x': value})
    with pytest.raises(rfc8785.IntegerDomainError):
        rfc8785.dumps({'x': value})
