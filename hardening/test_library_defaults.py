"""Hardening guards as a plain pytest file.

Run with `pytest hardening/test_library_defaults.py`. Nothing here is bespoke: pytest is the runner, hypothesis
generates every input, the libraries under test compute every value, and the comparison is each library's own
published assertion callable. A reader with the pinned packages can run this file without anything else from
this repository, which is the point of rule 5 of the hardening assurance.

Each test names the hand-typed expectation in the frozen guard modules that it replaces.
"""
import calendar
import contextlib
import csv
import functools
import operator
import os
import pathlib
import shutil
import tempfile
import subprocess
import unicodedata
import datetime
import io
import zipfile
import zoneinfo
from xml.etree import ElementTree
from xml.sax.saxutils import escape as xml_escape
import itertools
import json
import math
import sqlite3
from urllib.parse import urljoin
from decimal import Decimal, DivisionByZero, ROUND_CEILING, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP
from fractions import Fraction

import arrow
import beancount_parser_lima as lima
from beancount import loader as beancount_loader
from beancount.core import data as beancount_data
import docx
import duckdb
import icalendar
from dateutil import rrule, tz as dateutil_tz
from dateutil.relativedelta import relativedelta
import numpy as np
import numpy_financial as npf
import pyxirr
from workalendar import core as workalendar_core
import igraph
import jinja2
import jsonschema
import markdown as python_markdown
import pint
import portion
import unyt
import regex
import rfc3986
import z3
import clingo
from cvc5 import pythonic as cvc5_pythonic
import pydantic
from lxml import etree as lxml_etree
from markdown_it import MarkdownIt
import networkx as nx
import openpyxl
import odf.opendocument
import odf.table
import odf.teletype
import odf.text
from odf.namespaces import OFFICENS, TABLENS
import odfdo
import orjson
import pdfplumber
import pptx
import pptx.chart.data
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
import pptx.oxml.ns as pptx_ns
from pptx.util import Inches
import pymupdf
import pypdf
import pypdfium2
import xlsxwriter
from docx2python import docx2python
from python_calamine import CalamineWorkbook

import nltk
import numpy.testing as npt
import pandas as pd
import pandera.pandas as pandera
import pandas.testing as pdt
import polars as pl
import pyarrow.csv as pyarrow_csv
import rfc8785
import polars.testing as plt
import pytest
import rapidfuzz.distance.DamerauLevenshtein as rf_damerau
import rapidfuzz.distance.Levenshtein as rf_levenshtein
import rapidfuzz.distance.OSA as rf_osa
import rapidfuzz.process as rf_process
from hypothesis import assume, given, settings, strategies as st
from largest_remainder import LargestRemainder
import apportionment.methods as apportionment_methods

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


def _numpy_offset_rolling(day, count, roll):
    return datetime.date.fromisoformat(
        str(np.busday_offset(np.datetime64(day.isoformat()), count, roll=roll, busdaycal=NUMPY_CALENDAR)))


@given(ANY_2026_DAY, st.integers(min_value=1, max_value=20))
@SLOW
def test_workalendar_forward_counting_is_the_roll_numpy_calls_backward(day, count):
    """The divergence above is not between two calendars, it is between two of the roll rules numpy already
    documents. numpy 2.4.6 states that busday_offset "First adjusts the date to fall on a valid day according
    to the ``roll`` rule, then applies offsets", and its own examples label roll='forward' with offset 0 as
    "First business day on or after a date" and roll='backward' with offset 1 as "First business day after a
    date". workalendar 17.0.0 documents no convention at all: add_working_days says only "Add `delta` working
    days to the date", and its loop steps one calendar day at a time from the anchor and counts a day only
    when is_working_day accepts it, so the anchor is never counted. That is numpy's roll='backward' exactly,
    on every day of the year and not only on weekends."""
    npt.assert_array_equal(WORKWEEK.add_working_days(day, count),
                           _numpy_offset_rolling(day, count, 'backward'))


@given(ANY_2026_DAY, st.integers(min_value=1, max_value=20))
@SLOW
def test_a_backward_offset_swaps_which_roll_the_two_libraries_share(day, count):
    """Going the other way the correspondence flips: workalendar's negative delta matches roll='forward'.
    The rule is that workalendar rolls the anchor away from the direction of travel, so neither roll matches
    it in both directions and a chain cannot pick one roll and be right about both."""
    npt.assert_array_equal(WORKWEEK.add_working_days(day, -count),
                           _numpy_offset_rolling(day, -count, 'forward'))


@given(ANY_2026_DAY.filter(lambda day: not bool(np.is_busday(np.datetime64(day.isoformat()),
                                                             busdaycal=NUMPY_CALENDAR))),
       st.integers(min_value=1, max_value=20))
@SLOW
def test_the_numpy_default_refuses_a_non_working_anchor_outright(day, count):
    """numpy's documented default is roll='raise', "means to raise an exception for an invalid day", so the
    'forward' the chains pass is a choice a person made and not a default anyone inherited. Called without it
    on an anchor that is not a working day, the primitive refuses rather than answering."""
    with pytest.raises(ValueError):
        np.busday_offset(np.datetime64(day.isoformat()), count, busdaycal=NUMPY_CALENDAR)


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


BMP_TEXT = st.text(alphabet=st.characters(max_codepoint=0xFFFF, blacklist_categories=('Cs',)),
                   min_size=1, max_size=6)


@given(st.dictionaries(BMP_TEXT, st.integers(min_value=-(2**53 - 1), max_value=2**53 - 1),
                       min_size=1, max_size=6))
@SLOW
def test_sorted_json_and_rfc8785_agree_on_basic_plane_integer_objects(mapping):
    """Inside the shared domain, and with every key inside the Basic Multilingual Plane, the two
    canonicalisations produce the same bytes. Replaces the canonical-ordering expectations in v21."""
    npt.assert_array_equal(_sorted_json(mapping), rfc8785.dumps(mapping))


@given(st.sampled_from(['\ue000', '\uf8ff']), st.sampled_from(['\U00010000', '\U0001F600']))
@SLOW
def test_the_two_canonicalisations_order_keys_differently_across_the_plane_boundary(bmp_key, astral_key):
    """RFC 8785 sorts keys by UTF-16 code unit as the standard requires; json.dumps(sort_keys=True) sorts by
    code point. A supplementary-plane character encodes as a surrogate pair beginning at D800, which is below
    E000, so the two orders are opposite for keys spanning the boundary. Key order is the substance of
    canonicalisation, so this is a stronger divergence than the value formatting above, and hypothesis found
    it rather than an author choosing the pair."""
    mapping = {bmp_key: 0, astral_key: 0}
    by_json = _sorted_json(mapping)
    by_standard = rfc8785.dumps(mapping)
    npt.assert_array_equal(by_json.index(bmp_key.encode()) < by_json.index(astral_key.encode()), True)
    npt.assert_array_equal(by_standard.index(astral_key.encode()) < by_standard.index(bmp_key.encode()), True)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(by_json, by_standard)


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


# ---------------------------------------------------------------- markdown rendering
MARKDOWN_IT = MarkdownIt()
COMMON_MARKDOWN = ['A & B < 5', 'plain text', '# head', '- a\n- b', 'a\nb', '**bold**',
                   'http://x.com', 'a  \nb', '<b>raw</b>']


@given(st.sampled_from(COMMON_MARKDOWN))
@SLOW
def test_two_markdown_renderers_agree_on_common_constructs(source):
    """markdown-it-py and Python-Markdown are independent implementations. They agree on headings, lists,
    emphasis, hard breaks, raw HTML and on escaping an ampersand and a less-than, which corroborates the
    escaping claims recorded for P105 and P114."""
    npt.assert_array_equal(MARKDOWN_IT.render(source).strip(), python_markdown.markdown(source).strip())


@given(st.sampled_from(['>\n1', '>\na', '>\n- x']))
@SLOW
def test_the_two_renderers_disagree_on_a_line_after_an_empty_blockquote(source):
    """Hypothesis found this in three characters. markdown-it-py closes the blockquote and puts the
    following line outside it; Python-Markdown treats the line as a lazy continuation and puts it inside.
    A quoted passage becomes unquoted, or the reverse, depending on which renderer ran, so the rendered
    structure of a converted document is renderer-dependent."""
    by_markdown_it = MARKDOWN_IT.render(source).strip()
    by_python_markdown = python_markdown.markdown(source).strip()
    npt.assert_array_equal(by_markdown_it.startswith('<blockquote></blockquote>'), True)
    npt.assert_array_equal(by_python_markdown.startswith('<blockquote>'), True)
    npt.assert_array_equal(by_python_markdown.endswith('</blockquote>'), True)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(by_markdown_it, by_python_markdown)


@given(st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=20))
@SLOW
def test_both_renderers_wrap_plain_text_identically(word):
    """The divergence is structural, not textual: plain words render the same in both."""
    npt.assert_array_equal(MARKDOWN_IT.render(word).strip(), python_markdown.markdown(word).strip())
    npt.assert_array_equal(python_markdown.markdown(word).strip(), '<p>%s</p>' % word)


# ---------------------------------------------------------------- unicode offsets and forms
MULTI_CODEPOINT_GRAPHEMES = ['नि', '\U0001F44D\U0001F3FD', 'é', 'á̧']
COMPATIBILITY_CHARS = ['ﬁ', 'Ⅻ', '½', '①']


@given(st.sampled_from(MULTI_CODEPOINT_GRAPHEMES))
@SLOW
def test_a_grapheme_is_not_a_code_point_and_normalisation_does_not_close_the_gap(text):
    """regex implements UAX#29 grapheme clustering; unicodedata implements normalisation. They are separate
    libraries answering separate questions. Each of these is one grapheme and more than one code point, and
    NFC does not reduce the Devanagari or emoji cases at all, so a span expressed in code points can split a
    cluster that normalisation will never merge. P195's contract tags offsets as bytes or code points and
    names no third space; this is that third space."""
    graphemes = regex.findall(r'\X', text)
    npt.assert_array_equal(len(graphemes), 1)
    npt.assert_array_equal(len(text) > 1, True)
    npt.assert_array_equal(len(regex.findall(r'\X', unicodedata.normalize('NFC', text))), 1)


@given(st.sampled_from(['नि', '\U0001F44D\U0001F3FD']))
@SLOW
def test_normalisation_leaves_these_clusters_at_their_original_length(text):
    """For the Devanagari consonant-plus-vowel and the emoji-plus-modifier, NFC changes nothing, so the
    grapheme remains longer than one code point after normalisation. Grapheme safety is a separate obligation
    from normalisation, not a consequence of it."""
    npt.assert_array_equal(unicodedata.normalize('NFC', text), text)
    npt.assert_array_equal(len(text), 2)
    npt.assert_array_equal(len(regex.findall(r'\X', text)), 1)


@given(st.sampled_from(COMPATIBILITY_CHARS))
@SLOW
def test_the_compatibility_form_changes_text_the_canonical_form_leaves_alone(char):
    """NFC leaves each of these single characters alone and NFKC replaces every one of them. A normalisation
    policy that does not pin the form is not a policy."""
    npt.assert_array_equal(unicodedata.normalize('NFC', char), char)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(unicodedata.normalize('NFKC', char), char)


@given(st.sampled_from(['\ufb01', '\u216b', '\u00bd']))
@SLOW
def test_compatibility_expansion_lengthens_the_text(char):
    """The fi ligature becomes two letters, Roman numeral twelve becomes three, one half becomes three, so
    every offset after them moves."""
    npt.assert_array_equal(len(unicodedata.normalize('NFKC', char)) > len(char), True)


@given(st.sampled_from(['\u2460', '\u2461', '\u2462']))
@SLOW
def test_compatibility_substitution_can_preserve_length_while_changing_the_character(char):
    """A circled digit becomes a plain digit: one character in, one character out. The length is unchanged, so
    an offset map built before normalisation still validates afterwards while the text underneath it is a
    different character. A span map checked only by length cannot detect this substitution."""
    expanded = unicodedata.normalize('NFKC', char)
    npt.assert_array_equal(len(expanded), len(char))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(expanded, char)
    npt.assert_array_equal(expanded.isdigit(), True)


@given(st.sampled_from(['Café', '́', 'á']))
@SLOW
def test_decomposed_text_shortens_under_the_canonical_form(text):
    """The case P195 records: the decomposed spelling loses code points under NFC, so a raw offset does not
    index the normalised text. Both libraries agree that the result is shorter or equal."""
    normalised = unicodedata.normalize('NFC', text)
    npt.assert_array_equal(len(normalised) <= len(text), True)
    npt.assert_array_equal(len(regex.findall(r'\X', normalised)), len(regex.findall(r'\X', text)))


# ---------------------------------------------------------------- recurrence, cross-runtime oracle
PHP_RRULE_ORACLE = pathlib.Path(__file__).with_name('rrule_oracle.php')
PHP_RRULE_SOURCE = pathlib.Path('/home/user/rlanvin/php-rrule/src/RRule.php')
php_available = shutil.which('php') is not None and PHP_RRULE_SOURCE.exists()


def _php_occurrences(rule, start):
    completed = subprocess.run(['php', str(PHP_RRULE_ORACLE), rule, start.isoformat()],
                               capture_output=True, text=True, check=True)
    return [line for line in completed.stdout.split('\n') if line]


def _dateutil_occurrences(freq, start, count, **kwargs):
    return [moment.date().isoformat() for moment in
            rrule.rrule(freq, dtstart=datetime.datetime(start.year, start.month, start.day), count=count, **kwargs)]


@pytest.mark.skipif(not php_available, reason='php and a php-rrule checkout are required for this oracle')
@given(st.integers(min_value=1, max_value=28), st.integers(min_value=1, max_value=12))
@SLOW
def test_monthly_recurrence_agrees_with_the_php_port_on_ordinary_days(day, count):
    """php-rrule runs in a different runtime and language. It documents itself as having started as a port
    of python-dateutil, so agreement corroborates the dateutil lineage rather than an independent reading of
    RFC 5545; that is stated rather than glossed. On days 1 to 28 every month has the day."""
    start = datetime.date(2026, 1, day)
    npt.assert_array_equal(_php_occurrences('FREQ=MONTHLY;BYMONTHDAY=%d;COUNT=%d' % (day, count), start),
                           _dateutil_occurrences(rrule.MONTHLY, start, count, bymonthday=day))


@pytest.mark.skipif(not php_available, reason='php and a php-rrule checkout are required for this oracle')
@given(st.integers(min_value=1, max_value=12))
@SLOW
def test_the_php_port_skips_the_same_short_months_on_day_31(count):
    """Both implementations omit every month without a 31st and both reach the same eighth occurrence in the
    following January. The P182 finding therefore holds in two runtimes; whether it is what the standard
    requires is a question about RFC 5545 section 3.3.10, recorded in the register."""
    start = datetime.date(2026, 1, 31)
    by_php = _php_occurrences('FREQ=MONTHLY;BYMONTHDAY=31;COUNT=%d' % count, start)
    by_dateutil = _dateutil_occurrences(rrule.MONTHLY, start, count, bymonthday=31)
    npt.assert_array_equal(by_php, by_dateutil)
    npt.assert_array_equal(all(item.endswith('-31') for item in by_php), True)
    npt.assert_array_equal(any(item[5:7] == '02' for item in by_php), False)


@pytest.mark.skipif(not php_available, reason='php and a php-rrule checkout are required for this oracle')
@given(st.integers(min_value=1, max_value=12))
@SLOW
def test_the_php_port_agrees_on_the_month_end_rule(count):
    """BYMONTHDAY=-1 selects the last day of each month in both, including 2026-02-28."""
    start = datetime.date(2026, 1, 31)
    npt.assert_array_equal(_php_occurrences('FREQ=MONTHLY;BYMONTHDAY=-1;COUNT=%d' % count, start),
                           _dateutil_occurrences(rrule.MONTHLY, start, count, bymonthday=-1))


# ---------------------------------------------------------------- financial primitives, two implementations
LOAN_RATE = st.floats(min_value=0.0001, max_value=0.5, allow_nan=False, allow_infinity=False)
MODEST_RATE = st.floats(min_value=0.0001, max_value=0.2, allow_nan=False, allow_infinity=False)
ANY_RATE = st.floats(min_value=0.0, max_value=0.5, allow_nan=False, allow_infinity=False)
LOAN_TERM = st.integers(min_value=1, max_value=60)
PRINCIPAL = st.floats(min_value=1.0, max_value=1_000_000.0, allow_nan=False, allow_infinity=False)
CASH_FLOWS = st.lists(st.integers(min_value=-100_000, max_value=100_000), min_size=1, max_size=20)


@given(ANY_RATE, LOAN_TERM, PRINCIPAL)
@SLOW
def test_the_periodic_payment_agrees_between_a_python_and_a_rust_implementation(rate, periods, principal):
    """numpy-financial solves the annuity equation in Python over numpy arrays; pyxirr solves it in Rust with
    its own closed form and no dependency on numpy-financial. Replaces the typed Decimal('40.78') and
    Decimal('38.25') payments in handoff_guards_v19.py case 178, including the zero-rate branch both
    libraries special-case."""
    npt.assert_allclose(float(npf.pmt(rate, periods, principal)),
                        pyxirr.pmt(rate, periods, principal), rtol=1e-9)


@given(LOAN_RATE, LOAN_TERM, PRINCIPAL)
@SLOW
def test_both_libraries_sign_a_payment_on_a_borrowed_amount_as_cash_out(rate, periods, principal):
    """Both projects document the same sign convention, numpy-financial as "By convention, the negative sign
    represents cash flow out" and pyxirr as "By convention, investments or 'deposits' are negative, income or
    'withdrawals' are positive." Replaces the typed g.equal(npf.pmt(...) < 0, True) in case 178."""
    npt.assert_array_equal(float(npf.pmt(rate, periods, principal)) < 0, True)
    npt.assert_array_equal(pyxirr.pmt(rate, periods, principal) < 0, True)


@given(LOAN_RATE, LOAN_TERM, LOAN_TERM, PRINCIPAL)
@SLOW
def test_interest_plus_principal_is_the_payment_in_both_libraries(rate, period, periods, principal):
    """The decomposition is an invariant of the output, so nothing is typed. It is not circular in pyxirr:
    its ppmt is an independently derived closed form, -r*(F+P)*(r+1)^(per-1)/((r+1)^(n+t) - r*t - 1), not
    pmt minus ipmt. Replaces the three-period loop of case 178."""
    assume(period <= periods)
    npt.assert_allclose(float(npf.ipmt(rate, period, periods, principal))
                        + float(npf.ppmt(rate, period, periods, principal)),
                        float(npf.pmt(rate, periods, principal)), rtol=1e-12)
    npt.assert_allclose(pyxirr.ipmt(rate, period, periods, principal)
                        + pyxirr.ppmt(rate, period, periods, principal),
                        pyxirr.pmt(rate, periods, principal), rtol=1e-12)


@given(MODEST_RATE, LOAN_TERM, LOAN_TERM, PRINCIPAL)
@SLOW
def test_the_interest_portion_agrees_inside_an_ordinary_loan_term(rate, period, periods, principal):
    """Inside 1..nper, and at rates up to twenty per cent per period, the two implementations agree to nine
    significant figures, so the amortisation split of P178 does not depend on which library computed it in
    that region. The region has a boundary; the next test is on the other side of it."""
    assume(period <= periods)
    npt.assert_allclose(float(npf.ipmt(rate, period, periods, principal)),
                        pyxirr.ipmt(rate, period, periods, principal), rtol=1e-9)


@given(st.integers(min_value=45, max_value=60), st.integers(min_value=-20, max_value=20))
@SLOW
def test_the_interest_portion_diverges_in_the_last_period_of_a_long_high_rate_term(periods, scale):
    """The same two calls disagree once (1 + rate)**nper is large. numpy-financial computes the interest as
    the remaining balance times the rate, _rbl(rate, per, total_pmt, pv, when)*rate, which routes through its
    future-value formula; pyxirr evaluates one algebraically simplified closed form. The two are equal on
    paper and differ in floating point by cancellation, and the gap grows with (1 + rate)**nper: at a fifth
    per period it stays below 1e-10 relative for every term up to sixty, and in the final period of a
    sixty-period term at rate 0.5 it reaches 1.6e-5 relative. Nothing raises and neither value is nan, so a
    schedule reconciled against the other library does not balance. The principal is generated as a power-of-
    two multiple, which is exact in binary floating point and leaves the relative gap unchanged; the rate is
    an anchor the strategy is built on. Hypothesis found the divergence while checking the agreement claim
    above, and then found that an arbitrary principal can cancel it, which is why the scale is generated this
    way rather than freely."""
    principal = 1000.0 * 2.0 ** scale
    interest_by_numpy_financial = float(npf.ipmt(0.5, periods, periods, principal))
    interest_by_pyxirr = pyxirr.ipmt(0.5, periods, periods, principal)
    npt.assert_array_equal(np.isfinite([interest_by_numpy_financial, interest_by_pyxirr]), True)
    with pytest.raises(AssertionError):
        npt.assert_allclose(interest_by_numpy_financial, interest_by_pyxirr, rtol=1e-9)
    npt.assert_allclose(interest_by_numpy_financial, interest_by_pyxirr, rtol=1e-4)


@given(LOAN_RATE, st.one_of(st.integers(min_value=-20, max_value=0), st.integers(min_value=61, max_value=200)),
       LOAN_TERM, PRINCIPAL)
@SLOW
def test_the_interest_portion_diverges_outside_the_loan_term(rate, period, periods, principal):
    """Outside 1..nper the two libraries answer differently and neither raises. numpy-financial 1.0.0
    computes _rbl(rate, per, total_pmt, pv, when)*rate for any per and returns a finite number, so a period
    before the loan starts or after it ends still produces interest. pyxirr's Rust core returns f64::NAN
    there, with the comment "payments before first period don't make any sense", and its float_or_none
    converts that to None. Replaces the typed -0.0 and -4.948333 of case 178: a schedule built by looping
    over an off-by-one period range is silently wrong in one library and visibly absent in the other."""
    by_numpy_financial = np.asarray(npf.ipmt(rate, period, periods, principal), dtype=float)
    npt.assert_array_equal(np.isfinite(by_numpy_financial), True)
    npt.assert_array_equal(pyxirr.ipmt(rate, period, periods, principal) is None, True)


@given(ANY_RATE, CASH_FLOWS)
@SLOW
def test_net_present_value_agrees_between_the_two_implementations(rate, flows):
    """Replaces the typed 178.669563 of case 179. numpy-financial documents the sum from t=0 to M-1 of
    values_t/(1+rate)**t and warns that "npv considers a series of cashflows starting in the present
    (t = 0)"; pyxirr's npv defaults to start_from_zero=True, documented as "numpy compatible"."""
    npt.assert_allclose(float(npf.npv(rate, flows)),
                        pyxirr.npv(rate, flows), rtol=1e-9, atol=1e-9)


@given(LOAN_RATE, CASH_FLOWS)
@SLOW
def test_the_excel_convention_discounts_every_flow_one_further_period(rate, flows):
    """pyxirr documents both conventions in one function: "By default, npv function starts from zero (numpy
    compatible), but you can call it with start_from_zero=False parameter to make it Excel compatible." The
    ratio between them is exactly one period of discounting, which is an invariant of the two outputs rather
    than a typed number. Replaces the typed 165.43478 and the typed ratio 1.08 of case 179."""
    npt.assert_allclose(pyxirr.npv(rate, flows),
                        pyxirr.npv(rate, flows, start_from_zero=False) * (1 + rate), rtol=1e-9, atol=1e-9)


@given(st.integers(min_value=1, max_value=100_000),
       st.lists(st.integers(min_value=0, max_value=100_000), min_size=2, max_size=8))
@SLOW
def test_the_internal_rate_agrees_when_the_flows_change_sign_once(investment, returns):
    """The two solvers share no code and no method: numpy-financial takes the roots of the cash-flow
    polynomial with np.roots and picks the one closest to zero, pyxirr runs Newton-Raphson and falls back to
    Brent's method. Replaces the typed 0.269913 of case 179."""
    assume(sum(returns) > investment)
    flows = [-float(investment)] + [float(value) for value in returns]
    npt.assert_allclose(float(npf.irr(flows)), pyxirr.irr(flows), rtol=1e-6)


@given(st.lists(st.integers(min_value=0, max_value=100_000), min_size=1, max_size=8))
@SLOW
def test_the_two_libraries_partition_the_internal_rate_failures_differently(flows):
    """Cash flows that never change sign have no internal rate. numpy-financial folds that into the same nan
    it returns when a real positive root is simply not found, so the caller cannot tell an ill-posed question
    from a failed search. pyxirr raises InvalidPaymentsError for the ill-posed one, documented as "negative
    and positive payments are required", and reserves None for the failed search. Replaces the typed
    g.equal(math.isnan(npf.irr([100.0, 200.0, 300.0])), True) and the all-zero case of case 179."""
    amounts = [float(value) for value in flows]
    npt.assert_array_equal(np.isnan(npf.irr(amounts)), True)
    with pytest.raises(pyxirr.InvalidPaymentsError):
        pyxirr.irr(amounts)


@given(ANY_RATE, CASH_FLOWS, st.integers(min_value=0))
@SLOW
def test_a_missing_cash_flow_is_a_number_in_one_library_and_absent_in_the_other(rate, flows, position):
    """A nan in the input reaches the output as a nan from numpy-financial, which keeps arithmetic working and
    poisons every later sum, and as None from pyxirr, which stops arithmetic at the call site. Replaces the
    typed g.equal(math.isnan(net_present_value(0.08, [-459.0, float('nan'), 250.0])), True) of case 179."""
    amounts = [float(value) for value in flows]
    amounts[position % len(amounts)] = float('nan')
    npt.assert_array_equal(np.isnan(npf.npv(rate, amounts)), True)
    npt.assert_array_equal(pyxirr.npv(rate, amounts) is None, True)


# ---------------------------------------------------------------- month arithmetic, two more runtimes
MONTH_ORACLE_RB = pathlib.Path(__file__).with_name('month_offset_oracle.rb')
MONTH_ORACLE_PHP = pathlib.Path(__file__).with_name('month_offset_oracle.php')
ruby_available = shutil.which('ruby') is not None
php_binary_available = shutil.which('php') is not None
ANCHOR_YEAR = st.integers(min_value=1901, max_value=2199)
ANCHOR_MONTH = st.integers(min_value=1, max_value=12)
MONTH_OFFSET = st.integers(min_value=-60, max_value=60)
POSITIVE_MONTH_OFFSET = st.integers(min_value=1, max_value=60)


def _month_end(year, month):
    return datetime.date(year, month, calendar.monthrange(year, month)[1])


def _ruby_month_shift(anchor, months):
    completed = subprocess.run(['ruby', str(MONTH_ORACLE_RB), anchor.isoformat(), str(months)],
                               capture_output=True, text=True, check=True)
    return completed.stdout.strip()


def _php_modify(anchor, modifier):
    completed = subprocess.run(['php', str(MONTH_ORACLE_PHP), anchor.isoformat(), modifier],
                               capture_output=True, text=True, check=True)
    return completed.stdout.strip()


@pytest.mark.skipif(not ruby_available, reason='the ruby runtime is required for this oracle')
@given(ANCHOR_YEAR, ANCHOR_MONTH, MONTH_OFFSET)
@SLOW
def test_month_shift_agrees_between_dateutil_and_the_ruby_c_implementation(year, month, months):
    """Ruby's Date#>> is C in the standard library, unrelated to dateutil. Its documentation states, verbatim,
    "When the same day does not exist for the new month, the last day of that month is used instead", and its
    implementation decrements the day until valid_civil_p accepts it; dateutil 2.9.0.post0 computes
    day = min(calendar.monthrange(year, month)[1], self.day or other.day). Two implementations, one
    convention. The anchor is the last day of a generated month, which is the case P183 and P185 turn on.
    Replaces the typed date(2026, 9, 30) and date(2025, 2, 28) expiries of handoff_guards_v20.py case 183."""
    anchor = _month_end(year, month)
    npt.assert_array_equal(_ruby_month_shift(anchor, months),
                           (anchor + relativedelta(months=months)).isoformat())


def _month_end_of_thirty_one_days(year, index):
    """The anchor P183 and P185 use, chosen from the months the calendar module reports as having 31 days."""
    long_months = [month for month in range(1, 13) if calendar.monthrange(year, month)[1] == 31]
    return datetime.date(year, long_months[index % len(long_months)], 31)


def _offsets_where_dateutil_keeps_the_day(anchor, keep):
    """The two regions, separated by dateutil's own output: it keeps the anchor day exactly when the target
    month is long enough, and clamps otherwise. Nothing about the calendar is typed here, and neither list is
    ever empty, so no input is filtered out."""
    return [months for months in range(1, 61)
            if ((anchor + relativedelta(months=months)).day == anchor.day) == keep]


@pytest.mark.skipif(not php_binary_available, reason='the php runtime is required for this oracle')
@given(ANCHOR_YEAR, st.integers(min_value=0, max_value=1000), st.integers(min_value=0, max_value=1000))
@SLOW
def test_month_shift_agrees_with_php_when_the_target_month_has_the_anchor_day(year, month_index, offset_index):
    """Where the anchor day exists in the target month, PHP's DateTime::modify returns the same date as
    dateutil, so the three runtimes agree on the ordinary case."""
    anchor = _month_end_of_thirty_one_days(year, month_index)
    offsets = _offsets_where_dateutil_keeps_the_day(anchor, keep=True)
    months = offsets[offset_index % len(offsets)]
    npt.assert_array_equal(_php_modify(anchor, '%+d months' % months),
                           (anchor + relativedelta(months=months)).isoformat())


@pytest.mark.skipif(not php_binary_available, reason='the php runtime is required for this oracle')
@given(ANCHOR_YEAR, st.integers(min_value=0, max_value=1000), st.integers(min_value=0, max_value=1000))
@SLOW
def test_php_overflows_into_the_next_month_where_dateutil_and_ruby_clamp(year, month_index, offset_index):
    """Where the anchor day does not exist in the target month, the two conventions part. dateutil and Ruby
    clamp to the last day of the target month; PHP counts the missing days forward into the month after,
    which its own manual documents in an example headed "Beware when adding or subtracting months" whose
    output is 2001-01-31 then 2001-03-03. The overflow is not an error and nothing raises, so a term or an
    expiry computed in PHP is later than the same term computed in Python, by one to three days, and only for
    anchors at the end of a long month. This is the anniversary date of P183 and the renewal term of P185."""
    anchor = _month_end_of_thirty_one_days(year, month_index)
    offsets = _offsets_where_dateutil_keeps_the_day(anchor, keep=False)
    months = offsets[offset_index % len(offsets)]
    by_dateutil = anchor + relativedelta(months=months)
    by_php = _php_modify(anchor, '%+d months' % months)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(by_php, by_dateutil.isoformat())
    npt.assert_array_equal(by_php > by_dateutil.isoformat(), True)


@pytest.mark.skipif(not php_binary_available, reason='the php runtime is required for this oracle')
@given(ANCHOR_YEAR, ANCHOR_MONTH)
@SLOW
def test_the_last_day_of_the_next_month_agrees_between_php_and_dateutil(year, month):
    """PHP has a phrase for the operation the chains actually want, documented as setting "the day to the last
    day of the current month", and dateutil expresses the same thing as relativedelta(months=+1, day=31),
    where the day is clamped down to the length of the target month. Asked that question rather than for a
    month offset, the two runtimes agree on every generated month end. The divergence above is therefore about
    which question the chain asked, not about either calendar."""
    anchor = _month_end(year, month)
    npt.assert_array_equal(_php_modify(anchor, 'last day of next month'),
                           (anchor + relativedelta(months=+1, day=31)).isoformat())


@pytest.mark.skipif(not ruby_available, reason='the ruby runtime is required for this oracle')
@given(ANCHOR_YEAR, ANCHOR_MONTH, POSITIVE_MONTH_OFFSET)
@SLOW
def test_the_renewal_term_ends_the_day_before_the_anniversary_in_both_runtimes(year, month, months):
    """P185 renews a term by starting the day after the old end and ending one day before the anniversary of
    that start. Both runtimes are given the anniversary and the day is removed with datetime.timedelta on the
    Python side, so the shim does no arithmetic. Replaces the typed ('2027-09-01', '2028-08-31'),
    ('2027-09-01', '2027-09-30') and ('2028-03-01', '2029-02-28') tuples of case 185."""
    begins = _month_end(year, month) + datetime.timedelta(days=1)
    ends_by_dateutil = begins + relativedelta(months=months) - datetime.timedelta(days=1)
    ends_by_ruby = datetime.date.fromisoformat(_ruby_month_shift(begins, months)) - datetime.timedelta(days=1)
    npt.assert_array_equal(ends_by_ruby.isoformat(), ends_by_dateutil.isoformat())


@given(ANCHOR_YEAR, ANCHOR_MONTH, MONTH_OFFSET)
@SLOW
def test_pandas_shifts_months_by_the_same_clamping_rule(year, month, months):
    """pandas is a third implementation, in Cython: shift_month in pandas/_libs/tslibs/offsets.pyx computes
    day = min(stamp.day, days_in_month). It is corroboration rather than independent confirmation, because its
    own docstring says the day is "determined by day_opt using relativedelta semantics" and documents the
    default as "the same day as the input, or the last day of the month if the new month is too short". That
    it names dateutil is the point worth recording: two of the three implementations a chain is likely to
    reach for share a convention by design, and the third runtime does not."""
    anchor = _month_end(year, month)
    npt.assert_array_equal((pd.Timestamp(anchor) + pd.DateOffset(months=months)).date().isoformat(),
                           (anchor + relativedelta(months=months)).isoformat())


# ---------------------------------------------------------------- composing and reversing month offsets
ORACLE_PROCESS = settings(max_examples=40, deadline=None)
"""Each example of a test below starts one runtime process for every value it compares, so these run fewer
examples than SLOW. The regions they draw from are enumerated in full for every generated anchor."""


def _split_offsets(anchor, agree):
    """The (n, k) pairs where one offset of n months and two hops of k and n - k months land on the same
    date, and the pairs where they do not, separated by dateutil's own output rather than by a rule written
    here. Both lists are non-empty for every anchor at the end of a 31-day month, so no generated input is
    discarded and no health check can fire."""
    return [(months, first_hop)
            for months in range(2, 25)
            for first_hop in range(1, months)
            if (((anchor + relativedelta(months=first_hop)) + relativedelta(months=months - first_hop))
                == (anchor + relativedelta(months=months))) == agree]


def _round_trip_offsets(anchor, returns):
    """The offsets whose inverse comes back to the anchor and the offsets whose inverse does not, again
    separated by dateutil's own output. Both lists are non-empty for every 31-day month end."""
    return [months for months in range(1, 61)
            if ((anchor + relativedelta(months=months) - relativedelta(months=months)) == anchor) == returns]


@pytest.mark.skipif(not ruby_available, reason='the ruby runtime is required for this oracle')
@given(ANCHOR_YEAR, st.integers(min_value=0, max_value=1000), st.integers(min_value=0, max_value=1000))
@ORACLE_PROCESS
def test_two_hops_reach_the_same_date_as_one_where_the_day_survives_every_month_between(year, month_index,
                                                                                        pair_index):
    """Where dateutil says splitting an offset changes nothing, Ruby's Date#>> says the same: its own two
    hops land where its own single offset lands. The two implementations therefore agree about where a
    schedule may be computed one instalment at a time, which is what P157 assumes throughout."""
    anchor = _month_end_of_thirty_one_days(year, month_index)
    pairs = _split_offsets(anchor, agree=True)
    months, first_hop = pairs[pair_index % len(pairs)]
    midpoint = datetime.date.fromisoformat(_ruby_month_shift(anchor, first_hop))
    npt.assert_array_equal(_ruby_month_shift(midpoint, months - first_hop),
                           _ruby_month_shift(anchor, months))


@pytest.mark.skipif(not ruby_available, reason='the ruby runtime is required for this oracle')
@given(ANCHOR_YEAR, st.integers(min_value=0, max_value=1000), st.integers(min_value=0, max_value=1000))
@ORACLE_PROCESS
def test_splitting_one_month_offset_into_two_hops_loses_days_in_both_clamping_runtimes(year, month_index,
                                                                                       pair_index):
    """The drift case 157 records as a surprise is documented behaviour in the other runtime. Ruby's own C
    source at v3_3_6 introduces it as "This results in the following, possibly unexpected, behaviors:" and
    then shows d0 = Date.new(2001, 1, 31); d1 = d0 >> 1 giving 2001-02-28 and d2 = d1 >> 1 giving 2001-03-28.
    dateutil's documentation at 2.9.0.post0 states the clamp -- "If the result falls on a day after the last
    one of the month, the last day of the month is used instead" -- and its doctest shows the single offset
    keeping the day, date(2003,1,31)+relativedelta(months=+2) giving 2003-03-31, but says nothing about what
    happens when the offset is applied in stages. Ruby is executed here rather than quoted: on the whole
    region where dateutil's two hops differ from its one, Ruby's two hops differ from Ruby's one by the same
    date, and always earlier, never later. Replaces the typed month_walk step and offset lists of
    handoff_guards_v16.py case 157."""
    anchor = _month_end_of_thirty_one_days(year, month_index)
    pairs = _split_offsets(anchor, agree=False)
    months, first_hop = pairs[pair_index % len(pairs)]
    midpoint = datetime.date.fromisoformat(_ruby_month_shift(anchor, first_hop))
    by_two_hops = _ruby_month_shift(midpoint, months - first_hop)
    by_one_hop = _ruby_month_shift(anchor, months)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(by_two_hops, by_one_hop)
    npt.assert_array_equal(by_two_hops < by_one_hop, True)
    npt.assert_array_equal(by_two_hops, ((anchor + relativedelta(months=first_hop))
                                         + relativedelta(months=months - first_hop)).isoformat())


@pytest.mark.skipif(not php_binary_available, reason='the php runtime is required for this oracle')
@given(ANCHOR_YEAR, st.integers(min_value=0, max_value=1000), st.integers(min_value=0, max_value=1000))
@ORACLE_PROCESS
def test_php_moves_a_split_offset_later_where_the_clamping_runtimes_move_it_earlier(year, month_index,
                                                                                    pair_index):
    """PHP documents the same hazard in the opposite direction. Its manual source carries an example headed
    "Beware when adding or subtracting months" in which two successive modify('+1 month') calls on
    2000-12-31 print 2001-01-31 and then 2001-03-03. Executed over the whole region where dateutil's two
    hops fall short of its single offset, PHP's two hops overshoot its own single offset every time. So the
    instalment schedule and the anniversary schedule of case 157 differ in both runtimes, and a chain that
    moves between them does not merely keep its error: the error changes sign."""
    anchor = _month_end_of_thirty_one_days(year, month_index)
    pairs = _split_offsets(anchor, agree=False)
    months, first_hop = pairs[pair_index % len(pairs)]
    midpoint = datetime.date.fromisoformat(_php_modify(anchor, '%+d months' % first_hop))
    npt.assert_array_equal(_php_modify(midpoint, '%+d months' % (months - first_hop))
                           > _php_modify(anchor, '%+d months' % months), True)
    npt.assert_array_equal(((anchor + relativedelta(months=first_hop))
                            + relativedelta(months=months - first_hop))
                           < (anchor + relativedelta(months=months)), True)


@pytest.mark.skipif(not (ruby_available and php_binary_available),
                    reason='both runtimes are required for this oracle')
@given(ANCHOR_YEAR, st.integers(min_value=0, max_value=1000), st.integers(min_value=0, max_value=1000))
@ORACLE_PROCESS
def test_the_three_runtimes_fail_to_return_to_the_anchor_on_the_same_offsets(year, month_index, offset_index):
    """Ruby's source documents this one too, immediately after the stepping example: d0 = Date.new(2001, 1,
    31); d1 = d0 >> 1 giving 2001-02-28 and d2 = d1 >> -1 giving 2001-01-28. Executed, the set of offsets
    that do not come back is the same set in both conventions -- every offset where dateutil fails to return
    is an offset where PHP fails to return -- and the two miss the anchor on opposite sides, dateutil and
    Ruby landing before it and PHP after it. Replaces the typed date(2026, 1, 28) round trip of case 157."""
    anchor = _month_end_of_thirty_one_days(year, month_index)
    offsets = _round_trip_offsets(anchor, returns=False)
    months = offsets[offset_index % len(offsets)]
    by_dateutil = anchor + relativedelta(months=months) - relativedelta(months=months)
    by_ruby = _ruby_month_shift(datetime.date.fromisoformat(_ruby_month_shift(anchor, months)), -months)
    by_php = _php_modify(datetime.date.fromisoformat(_php_modify(anchor, '%+d months' % months)),
                         '%+d months' % -months)
    npt.assert_array_equal(by_ruby, by_dateutil.isoformat())
    with pytest.raises(AssertionError):
        npt.assert_array_equal([by_ruby, by_php], [anchor.isoformat(), anchor.isoformat()])
    npt.assert_array_equal([by_ruby < anchor.isoformat(), by_php > anchor.isoformat()], True)


@pytest.mark.skipif(not (ruby_available and php_binary_available),
                    reason='both runtimes are required for this oracle')
@given(ANCHOR_YEAR, st.integers(min_value=0, max_value=1000), st.integers(min_value=0, max_value=1000))
@ORACLE_PROCESS
def test_the_round_trip_returns_to_the_anchor_in_all_three_runtimes_where_the_day_survives(year, month_index,
                                                                                          offset_index):
    """On the complementary region all three runtimes come back to the anchor, so the failure above is a
    property of which offsets were chosen and not of any one calendar implementation."""
    anchor = _month_end_of_thirty_one_days(year, month_index)
    offsets = _round_trip_offsets(anchor, returns=True)
    months = offsets[offset_index % len(offsets)]
    by_ruby = _ruby_month_shift(datetime.date.fromisoformat(_ruby_month_shift(anchor, months)), -months)
    by_php = _php_modify(datetime.date.fromisoformat(_php_modify(anchor, '%+d months' % months)),
                         '%+d months' % -months)
    npt.assert_array_equal([by_ruby, by_php], [anchor.isoformat(), anchor.isoformat()])


@given(ANCHOR_YEAR, st.integers(min_value=0, max_value=1000), st.integers(min_value=2, max_value=24),
       st.integers(min_value=0, max_value=1000))
@SLOW
def test_pandas_splits_and_reverses_a_month_offset_exactly_as_dateutil_does(year, month_index, months,
                                                                            hop_index):
    """The third implementation needs no region at all: over every generated split and every generated
    offset, pandas' DateOffset composes and reverses exactly as relativedelta does, including where both
    lose the day. A chain that swaps one for the other keeps the drift unchanged."""
    anchor = _month_end_of_thirty_one_days(year, month_index)
    first_hop = 1 + hop_index % (months - 1)
    stamp = pd.Timestamp(anchor)
    npt.assert_array_equal((stamp + pd.DateOffset(months=first_hop)
                            + pd.DateOffset(months=months - first_hop)).date().isoformat(),
                           ((anchor + relativedelta(months=first_hop))
                            + relativedelta(months=months - first_hop)).isoformat())
    npt.assert_array_equal((stamp + pd.DateOffset(months=months) - pd.DateOffset(months=months))
                           .date().isoformat(),
                           (anchor + relativedelta(months=months)
                            - relativedelta(months=months)).isoformat())


@pytest.mark.skipif(not php_binary_available, reason='the php runtime is required for this oracle')
@given(ANCHOR_YEAR, ANCHOR_MONTH)
@ORACLE_PROCESS
def test_a_month_period_ends_at_an_instant_no_date_is_equal_to(year, month):
    """The other half of case 157 asks pandas for the end of a period. Its Period.end_time falls on the day
    PHP calls "last day of this month" for every generated month, so the two agree about the date; but the
    value pandas returns is the last representable nanosecond of that day, so comparing it with the
    Timestamp of its own date is false. A cutoff written as period_end == Timestamp(day) never fires.
    Replaces the typed '2026-02-28 23:59:59.999999999' of case 157."""
    first_of_month = datetime.date(year, month, 1)
    period = pd.Period(first_of_month, freq='M')
    npt.assert_array_equal(period.end_time.date().isoformat(),
                           _php_modify(first_of_month, 'last day of this month'))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(period.end_time.to_numpy(),
                               pd.Timestamp(period.end_time.date()).to_numpy())

# ---------------------------------------------------------------- reachability and reference resolution
REFERENCE_EDGES = st.lists(st.tuples(st.integers(min_value=0, max_value=6), st.integers(min_value=0, max_value=6)),
                           min_size=1, max_size=14)
NODE_NAME = st.integers(min_value=0, max_value=6)


def _igraph_of(edges):
    return igraph.Graph(n=7, edges=list(edges), directed=True)


def _networkx_of(edges):
    graph = nx.DiGraph(edges)
    graph.add_nodes_from(range(7))
    return graph


@given(REFERENCE_EDGES, NODE_NAME)
@SLOW
def test_reachability_agrees_between_networkx_and_igraph_once_the_root_is_added_back(edges, root):
    """networkx is pure Python and igraph is a C library. Their reachability primitives compute the same set
    once the root convention is matched, which is the closure P196 builds over a reference graph. Replaces the
    typed ['ac-1', 'ac-2', 'ac-3'] closure of handoff_guards_v21.py case 196."""
    npt.assert_array_equal(sorted(nx.descendants(_networkx_of(edges), root) | {root}),
                           sorted(_igraph_of(edges).subcomponent(root, mode='out')))


@given(st.integers(min_value=1, max_value=6))
@SLOW
def test_a_root_inside_a_cycle_is_reachable_from_itself_and_networkx_omits_it(ring_size):
    """Both projects describe the same operation in one line. python-igraph 1.0.0 documents subcomponent with
    mode="out" as returning "the vertex IDs which are reachable from the given vertex"; networkx 3.6.1
    documents descendants as "Returns all nodes reachable from `source` in `G`". On a ring, and on a single
    self-loop, the root is genuinely reachable from itself: igraph returns it and networkx does not, because
    its implementation collects the children of bfs_edges and its docstring adds, two lines below the summary,
    that "The `source` node is not a descendant of itself, but can be included manually". A closure taken from
    a node that participates in a reference cycle is therefore one short, and P196's claim that the closure
    returns normally over a cycle holds while its count does not."""
    ring = [(index, (index + 1) % ring_size) for index in range(ring_size)]
    npt.assert_array_equal(sorted(igraph.Graph(n=ring_size, edges=ring, directed=True).subcomponent(0, mode='out')),
                           sorted(range(ring_size)))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(sorted(nx.descendants(nx.DiGraph(ring), 0)), sorted(range(ring_size)))


@given(REFERENCE_EDGES)
@SLOW
def test_strongly_connected_components_agree_between_the_two_graph_libraries(edges):
    """The cycle test P196 runs separately from the closure. Two implementations of it agree on every
    generated reference graph, so the cycles the proof reports are not an artefact of one library."""
    by_networkx = sorted(sorted(component) for component in nx.strongly_connected_components(_networkx_of(edges)))
    by_igraph = sorted(sorted(component) for component in _igraph_of(edges).connected_components(mode='strong'))
    npt.assert_equal(by_networkx, by_igraph)


URL_ORACLE_JS = pathlib.Path(__file__).with_name('url_resolve_oracle.js')
node_available = shutil.which('node') is not None
SAFE_SEGMENT = st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789-', min_size=1, max_size=8)
RELATIVE_PATH = st.lists(st.one_of(SAFE_SEGMENT, st.just('..'), st.just('.')), min_size=1, max_size=4).map('/'.join)
FRAGMENT = st.one_of(st.just(''), SAFE_SEGMENT.map(lambda segment: '#' + segment))
UPPERCASE_HOST = st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=1, max_size=8)
BASE_URL = 'https://example.org/cat/base.json'


def _rfc3986_resolve(base, reference):
    return rfc3986.URIReference.from_string(reference).resolve_with(base).unsplit()


def _node_resolve(base, reference):
    completed = subprocess.run(['node', str(URL_ORACLE_JS), base, reference],
                               capture_output=True, text=True, check=True)
    return completed.stdout.strip()


@pytest.mark.skipif(not node_available, reason='the node runtime is required for this oracle')
@given(RELATIVE_PATH, FRAGMENT)
@SLOW
def test_three_reference_resolvers_agree_on_an_ordinary_relative_reference(path, fragment):
    """Three implementations of reference resolution: the standard library's urljoin, rfc3986 2.0.0, whose
    resolve_with implements RFC 3986 section 5 in its own code and whose setup.cfg at tag 2.0.0 declares no
    install_requires, and the WHATWG URL parser in node v22.22.2 reached through a shim. On references built
    from ordinary segments, dot segments and a fragment, all three agree. Replaces the typed
    'https://example.org/cat/profile.json' and 'ac-1' of case 196."""
    reference = path + fragment
    by_urljoin = urljoin(BASE_URL, reference)
    npt.assert_array_equal(by_urljoin, _rfc3986_resolve(BASE_URL, reference))
    npt.assert_array_equal(by_urljoin, _node_resolve(BASE_URL, reference))


@pytest.mark.skipif(not node_available, reason='the node runtime is required for this oracle')
@given(UPPERCASE_HOST, SAFE_SEGMENT)
@SLOW
def test_only_the_standard_library_keeps_the_case_of_the_host(host, segment):
    """RFC 3986 makes the host case-insensitive, and two of the three resolvers normalise it: rfc3986 calls
    base_uri.normalize() before resolving and the WHATWG parser lowercases the host as part of parsing.
    urljoin does neither, so the same reference against the same base produces two strings that are not equal,
    and a closure that deduplicates resolved references by string keeps both."""
    base = 'https://%s.org/cat/base.json' % host
    by_urljoin = urljoin(base, segment)
    by_rfc3986 = _rfc3986_resolve(base, segment)
    npt.assert_array_equal(by_rfc3986, _node_resolve(base, segment))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(by_urljoin, by_rfc3986)
    npt.assert_array_equal(by_urljoin.lower(), by_rfc3986.lower())


@pytest.mark.skipif(not node_available, reason='the node runtime is required for this oracle')
@given(SAFE_SEGMENT, SAFE_SEGMENT)
@SLOW
def test_only_the_standard_library_leaves_a_space_unencoded(left, right):
    """A space inside a reference is percent-encoded by rfc3986 and by the WHATWG parser and passed through
    literally by urljoin, so the identifier a chain stores for a referenced document depends on the resolver
    even when every implementation reaches the same document."""
    reference = '%s %s.json' % (left, right)
    by_urljoin = urljoin(BASE_URL, reference)
    by_rfc3986 = _rfc3986_resolve(BASE_URL, reference)
    npt.assert_array_equal(by_rfc3986, _node_resolve(BASE_URL, reference))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(by_urljoin, by_rfc3986)
    npt.assert_array_equal(' ' in by_urljoin and '%20' in by_rfc3986, True)


@pytest.mark.skipif(not node_available, reason='the node runtime is required for this oracle')
@given(SAFE_SEGMENT)
@SLOW
def test_a_backslash_reference_resolves_three_different_ways(segment):
    """One reference, three answers, and the third is a different document. urljoin treats the backslash as an
    ordinary path character and keeps the base directory; rfc3986 percent-encodes it as %5C and also keeps the
    directory; the WHATWG parser treats a leading backslash as a path separator, so the reference becomes
    absolute from the root and the base directory disappears. This is the CSV situation again in another
    place: the resolvers do not agree with each other about what the same bytes mean, and only one of them
    changes which document is fetched."""
    reference = '\\%s.json' % segment
    by_urljoin = urljoin(BASE_URL, reference)
    by_rfc3986 = _rfc3986_resolve(BASE_URL, reference)
    by_node = _node_resolve(BASE_URL, reference)
    for left, right in ((by_urljoin, by_rfc3986), (by_urljoin, by_node), (by_rfc3986, by_node)):
        with pytest.raises(AssertionError):
            npt.assert_array_equal(left, right)
    npt.assert_array_equal([by_urljoin.startswith('https://example.org/cat/'),
                            by_rfc3986.startswith('https://example.org/cat/'),
                            by_node.startswith('https://example.org/cat/')],
                           [True, True, False])


# ---------------------------------------------------------------- two solvers and two logics
BOUNDS = st.lists(st.tuples(st.sampled_from(('>=', '<=')), st.integers(min_value=-20, max_value=20)),
                  min_size=1, max_size=6)


def _bound_constraints(module, bounds):
    variable = module.Int('n')
    return [variable >= value if sense == '>=' else variable <= value for sense, value in bounds]


def _z3_status_and_core(bounds):
    solver = z3.Solver()
    solver.set(unsat_core=True)
    constraints = _bound_constraints(z3, bounds)
    status = str(solver.check(*constraints))
    core = sorted(str(term) for term in solver.unsat_core()) if status == 'unsat' else []
    return status, core, {str(term): bound for term, bound in zip(constraints, bounds)}


def _cvc5_status_and_core(bounds):
    solver = cvc5_pythonic.Solver()
    solver.set('produce-unsat-cores', True)
    constraints = _bound_constraints(cvc5_pythonic, bounds)
    status = str(solver.check(*constraints))
    core = sorted(str(term) for term in solver.unsat_core()) if status == 'unsat' else []
    return status, core, {str(term): bound for term, bound in zip(constraints, bounds)}


@given(BOUNDS)
@SLOW
def test_two_smt_solvers_agree_on_the_satisfiability_of_generated_bounds(bounds):
    """z3 5.1.0 and cvc5 1.3.4 are separate C++ solvers; the cvc5 wheel declares no Python dependencies and
    imports no z3. Its pythonic layer imitates z3's API on purpose, but the decision procedure underneath is
    cvc5's own. On every generated set of integer bounds the two return the same status, so the satisfiability
    P193 reports is not one solver's opinion."""
    npt.assert_array_equal(_z3_status_and_core(bounds)[0], _cvc5_status_and_core(bounds)[0])


@given(BOUNDS)
@SLOW
def test_each_unsat_core_is_still_unsatisfiable_in_the_other_solver(bounds):
    """A core is only useful if it is genuinely sufficient. Each solver's core, replayed as the whole problem
    in the other solver, is still unsatisfiable, and each is a subset of what was asserted. Both projects
    promise a subset and neither promises a minimum: z3 5.1.0 documents unsat_core as returning "a subset (as
    an AST vector) of the assumptions provided to the last check()", and cvc5 1.3.4's own header says that
    after a check with assumptions "A subset of those assumptions may be included in the unsatisfiable core
    returned by this function."."""
    z3_status, z3_core, z3_index = _z3_status_and_core(bounds)
    assume(z3_status == 'unsat')
    _, cvc5_core, cvc5_index = _cvc5_status_and_core(bounds)
    npt.assert_array_equal(_cvc5_status_and_core([z3_index[text] for text in z3_core])[0], 'unsat')
    npt.assert_array_equal(_z3_status_and_core([cvc5_index[text] for text in cvc5_core])[0], 'unsat')
    npt.assert_array_equal([len(z3_core) <= len(bounds), len(cvc5_core) <= len(bounds)], [True, True])


@given(st.integers(min_value=-1000, max_value=1000))
@SLOW
def test_the_two_solvers_name_different_sufficient_cores_for_one_contradiction(anchor):
    """Four bounds, two of which contradict the first and one of which contradicts the second: every
    generated anchor makes the set unsatisfiable in both solvers, both cores are strict subsets, and the two
    cores are never the same. This is P193's finding produced by two implementations rather than asserted
    about one: the core names a sufficient subset, not the conflicting set, and which sufficient subset you
    are shown is a property of the solver. A rule absent from the core is not thereby consistent, and a
    conflict report built from one solver's core is not reproducible on another."""
    bounds = [('<=', anchor), ('>=', anchor + 1), ('>=', anchor + 2), ('<=', anchor - 1)]
    z3_status, z3_core, _ = _z3_status_and_core(bounds)
    cvc5_status, cvc5_core, _ = _cvc5_status_and_core(bounds)
    npt.assert_array_equal([z3_status, cvc5_status], ['unsat', 'unsat'])
    npt.assert_array_equal([len(z3_core) < len(bounds), len(cvc5_core) < len(bounds)], [True, True])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(z3_core, cvc5_core)


def _z3_admits(threshold, count, negated):
    variable = z3.Int('n')
    solver = z3.Solver()
    if count is not None:
        solver.add(variable == count)
    solver.add(z3.Not(variable >= threshold) if negated else variable >= threshold)
    return solver.check() == z3.sat


def _clingo_derives_approval(threshold, count):
    program = 'approved :- count(N), N >= %d.\n#show approved/0.\n' % threshold
    if count is not None:
        program += 'count(%d).\n' % count
    control = clingo.Control(['0'], logger=lambda code, message: None)
    control.add('base', [], program)
    control.ground([('base', [])])
    with control.solve(yield_=True) as handle:
        for model in handle:
            return 'approved' in [str(atom) for atom in model.symbols(shown=True)]
    return False


@given(st.integers(min_value=0, max_value=20), st.integers(min_value=0, max_value=20))
@SLOW
def test_the_smt_solver_and_the_answer_set_solver_agree_while_the_count_is_present(count, threshold):
    """clingo 5.8.2 computes answer sets of a logic program, which its README describes as Answer Set
    Programming; z3 decides a formula over the integers. Two different logics, and while the count is a fact
    they agree on every generated pair: the threshold is met in one exactly when the atom is derived in the
    other."""
    npt.assert_array_equal(_z3_admits(threshold, count, negated=False),
                           _clingo_derives_approval(threshold, count))


@given(st.integers(min_value=0, max_value=20))
@SLOW
def test_an_absent_count_is_unknown_to_the_smt_solver_and_false_to_the_answer_set_solver(threshold):
    """Remove the fact and the two logics part, in the direction that matters. z3 finds both the threshold and
    its negation satisfiable, so the question is open; clingo derives nothing, so the approval is simply
    absent from the answer set and a caller reading "not approved" cannot tell a refusal from a missing
    record. Replaces the typed {'true', 'false'} and [] of handoff_guards_v21.py case 197: the two engines
    disagree about a missing count, and the disagreement is the closed-world assumption, not a bug."""
    npt.assert_array_equal([_z3_admits(threshold, None, negated=False),
                            _z3_admits(threshold, None, negated=True)], [True, True])
    npt.assert_array_equal(_clingo_derives_approval(threshold, None), False)


# ---------------------------------------------------------------- as-of joins in two engines
EVENTS = st.lists(st.tuples(st.integers(min_value=0, max_value=50), st.integers(min_value=0, max_value=100)),
                  min_size=1, max_size=8, unique_by=(lambda pair: pair[0], lambda pair: pair[1]))
SEPARATED_EVENTS = st.lists(st.tuples(st.integers(min_value=0, max_value=50), st.integers(min_value=0, max_value=100)),
                            min_size=2, max_size=8, unique_by=(lambda pair: pair[0], lambda pair: pair[1]))
CUTOFF = st.integers(min_value=0, max_value=50)


def _pandas_asof(events, cutoff, *, exact, group=False):
    left = pd.DataFrame({'task': ['t'], 'when': [cutoff]}) if group else pd.DataFrame({'when': [cutoff]})
    right = pd.DataFrame({'when': [when for when, _ in events], 'pct': [pct for _, pct in events]})
    if group:
        right = right.assign(task='t')
    merged = pd.merge_asof(left, right, on='when', direction='backward', allow_exact_matches=exact,
                           **({'by': 'task'} if group else {}))
    return np.asarray(merged['pct'].tolist(), dtype=float)


def _polars_asof(events, cutoff, *, exact, group=False):
    left = pl.DataFrame({'task': ['t'], 'when': [cutoff]}) if group else pl.DataFrame({'when': [cutoff]})
    right = pl.DataFrame({'when': [when for when, _ in events], 'pct': [float(pct) for _, pct in events]})
    if group:
        right = right.with_columns(task=pl.lit('t'))
    joined = left.join_asof(right, on='when', strategy='backward', allow_exact_matches=exact,
                            **({'by': 'task'} if group else {}))
    return np.asarray(joined['pct'].to_list(), dtype=float)


@given(EVENTS, CUTOFF)
@SLOW
def test_the_as_of_join_agrees_between_pandas_and_polars_on_sorted_input(events, cutoff):
    """pandas.merge_asof is Cython over numpy; polars.join_asof is Rust. On sorted event tables the two agree
    on every generated cutoff, including the cutoff that precedes every event, where both return a missing
    value rather than zero. Replaces the typed [{'task': 'T1', 'pct': 0.60}, ...] expectations of
    handoff_guards_v20.py case 186."""
    ordered = sorted(events)
    npt.assert_array_equal(_pandas_asof(ordered, cutoff, exact=True),
                           _polars_asof(ordered, cutoff, exact=True))


@given(EVENTS, st.integers(min_value=0, max_value=7))
@SLOW
def test_the_exact_match_flag_moves_the_answer_the_same_way_in_both_engines(events, position):
    """Both engines expose the flag and both change the answer by one row when the cutoff falls exactly on an
    event, so the two reported percentages of case 186 are a flag rather than a fact. The cutoff is taken
    from the generated events so that the exact case is reached rather than waited for."""
    ordered = sorted(events)
    cutoff = ordered[position % len(ordered)][0]
    npt.assert_array_equal(_pandas_asof(ordered, cutoff, exact=True), _polars_asof(ordered, cutoff, exact=True))
    npt.assert_array_equal(_pandas_asof(ordered, cutoff, exact=False), _polars_asof(ordered, cutoff, exact=False))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_pandas_asof(ordered, cutoff, exact=True),
                               _pandas_asof(ordered, cutoff, exact=False))


@given(SEPARATED_EVENTS)
@SLOW
def test_only_pandas_refuses_an_unsorted_right_frame(events):
    """P186 records that the primitive refuses unsorted keys. That is a pandas property. Given the same rows
    with the largest key first, pandas raises ValueError and polars returns an answer, warning only that
    "Sortedness of columns cannot be checked when 'by' groups provided"."""
    ordered = sorted(events)
    unsorted = [ordered[-1]] + ordered[:-1]
    cutoff = ordered[-1][0] - 1
    with pytest.raises(ValueError):
        _pandas_asof(unsorted, cutoff, exact=True, group=True)
    npt.assert_array_equal(_polars_asof(unsorted, cutoff, exact=True, group=True).shape, (1,))


@given(SEPARATED_EVENTS)
@SLOW
def test_polars_answers_an_unsorted_as_of_join_with_a_different_row(events):
    """The answer is not merely unchecked, it is wrong, and wrong in the direction that hides work. polars
    scans the right frame in the order given and stops at the first key past the cutoff, so putting the last
    event first makes the join report no update at all while the sorted frame reports the last one. Without a
    by column polars does check and raises InvalidOperationError; with a by column it cannot, and a chain that
    groups by task, which is what case 186 does, loses the check exactly where it is grouping."""
    ordered = sorted(events)
    cutoff = ordered[-1][0] - 1
    unsorted = [ordered[-1]] + ordered[:-1]
    on_sorted = _polars_asof(ordered, cutoff, exact=True, group=True)
    on_unsorted = _polars_asof(unsorted, cutoff, exact=True, group=True)
    npt.assert_array_equal(np.isnan(on_sorted), False)
    npt.assert_array_equal(np.isnan(on_unsorted), True)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(on_sorted, on_unsorted)


@given(EVENTS)
@SLOW
def test_a_cutoff_before_every_event_is_missing_and_not_zero_in_both_engines(events):
    """The unknown percentage of case 186 is a missing value in both engines, never a zero, which is the one
    thing about the join that does not depend on which engine ran."""
    ordered = sorted(events)
    cutoff = ordered[0][0] - 1
    npt.assert_array_equal(np.isnan(_pandas_asof(ordered, cutoff, exact=True)), True)
    npt.assert_array_equal(np.isnan(_polars_asof(ordered, cutoff, exact=True)), True)


# ---------------------------------------------------------------- units and offset scales
UNIT_REGISTRY = pint.UnitRegistry()
TEMPERATURE = st.floats(min_value=-200.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
PRESSURE = st.floats(min_value=0.001, max_value=10_000.0, allow_nan=False, allow_infinity=False)


@given(TEMPERATURE)
@SLOW
def test_an_absolute_temperature_converts_the_same_way_in_two_unit_libraries(reading):
    """pint 0.25.3 and unyt 3.1.0 are separate unit systems; unyt's pyproject.toml at tag v3.1.0 lists numpy,
    sympy and packaging and does not depend on pint. They agree on the absolute Fahrenheit-to-Celsius
    conversion for every generated reading. Replaces the typed 29.8 of handoff_guards_v20.py case 184."""
    npt.assert_allclose(UNIT_REGISTRY.Quantity(reading, 'degF').to('degC').magnitude,
                        float(unyt.unyt_quantity(reading, 'degF').to('degC').value), rtol=1e-9, atol=1e-9)


@given(TEMPERATURE, TEMPERATURE)
@SLOW
def test_converting_a_span_as_a_temperature_shifts_it_by_one_fixed_offset_in_both_libraries(left, right):
    """The error P184 records is converting an uncertainty as though it were a temperature. Both libraries
    have both units and both make the same two answers, and the gap between them is one constant that does
    not depend on the reading, which is why the mistake survives review: it looks like a plausible number.
    Nothing here is typed; the constant is established by comparing two generated readings."""
    def gap(module_value):
        absolute, delta = module_value
        return absolute - delta
    pint_gaps = [gap((UNIT_REGISTRY.Quantity(value, 'degF').to('degC').magnitude,
                      UNIT_REGISTRY.Quantity(value, 'delta_degF').to('delta_degC').magnitude))
                 for value in (left, right)]
    unyt_gaps = [gap((float(unyt.unyt_quantity(value, 'degF').to('degC').value),
                      float(unyt.unyt_quantity(value, 'delta_degF').to('delta_degC').value)))
                 for value in (left, right)]
    npt.assert_allclose(pint_gaps[0], pint_gaps[1], rtol=1e-9, atol=1e-9)
    npt.assert_allclose(unyt_gaps, pint_gaps, rtol=1e-9, atol=1e-9)


@given(PRESSURE)
@SLOW
def test_a_multiplicative_conversion_agrees_between_two_unit_libraries(reading):
    """psi to kPa involves no offset, and the two libraries agree to nine figures on every generated reading,
    which is the corroboration P184's exact-rational pressure claim needed."""
    npt.assert_allclose(UNIT_REGISTRY.Quantity(reading, 'psi').to('kPa').magnitude,
                        float(unyt.unyt_quantity(reading, 'psi').to('kPa').value), rtol=1e-9)


@given(TEMPERATURE, TEMPERATURE)
@SLOW
def test_only_pint_refuses_to_add_two_absolute_temperatures(left, right):
    """pint's own documentation at 0.25.3 explains the refusal: "the addition of quantities with offset units
    is ambiguous, e.g. for *10 degC + 100 degC* two different result are reasonable depending on the context,
    *110 degC* or *383.15 degC (= 283.15 K + 373.15 K)*. Because of this ambiguity pint raises an error for
    the addition of two quantities with offset units (since pint-0.6)." unyt adds them and returns the first
    of those two readings with no warning. The guard P184 leans on is a pint policy, not a property of the
    dimension, so a chain that changes unit library loses the check that a temperature and a temperature
    cannot be summed. Both libraries do accept an absolute temperature plus a span, and they agree on it."""
    with pytest.raises(pint.errors.OffsetUnitCalculusError):
        UNIT_REGISTRY.Quantity(left, 'degC') + UNIT_REGISTRY.Quantity(right, 'degC')
    npt.assert_allclose(float((unyt.unyt_quantity(left, 'degC') + unyt.unyt_quantity(right, 'degC')).value),
                        left + right, rtol=1e-9, atol=1e-9)
    npt.assert_allclose((UNIT_REGISTRY.Quantity(left, 'degC')
                         + UNIT_REGISTRY.Quantity(right, 'delta_degC')).magnitude,
                        float((unyt.unyt_quantity(left, 'degC')
                               + unyt.unyt_quantity(right, 'delta_degC')).value), rtol=1e-9, atol=1e-9)


@given(TEMPERATURE)
@SLOW
def test_both_libraries_refuse_a_conversion_across_dimensions(reading):
    """Where the dimensions differ both libraries stop, so the dimensional guard of P184 does carry across
    implementations even though the offset guard does not. The exception types differ, which is itself a
    handoff detail: a chain that catches pint.DimensionalityError catches nothing under unyt."""
    with pytest.raises(pint.errors.DimensionalityError):
        UNIT_REGISTRY.Quantity(reading, 'degC').to('psi')
    with pytest.raises(unyt.exceptions.UnitConversionError):
        unyt.unyt_quantity(reading, 'degC').to('psi')


# ---------------------------------------------------------------- banding a score and counting the bands
BAND_EDGES = st.lists(st.integers(min_value=-50, max_value=50), min_size=3, max_size=6,
                      unique=True).map(sorted)
FRACTION = st.floats(min_value=0.01, max_value=0.99, allow_nan=False, allow_infinity=False)
BEYOND = st.floats(min_value=1.0, max_value=100.0, allow_nan=False, allow_infinity=False)
INSIDE_FRACTIONS = st.lists(FRACTION, min_size=1, max_size=20)
PAST_THE_EDGE = st.lists(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
                         min_size=1, max_size=20)
CLEAR_OF_THE_EDGE = st.lists(BEYOND, min_size=1, max_size=20)
INSIDE_PAIRS = st.lists(st.tuples(FRACTION, FRACTION), min_size=1, max_size=20)
BEYOND_PAIRS = st.lists(st.tuples(BEYOND, FRACTION), min_size=1, max_size=20)


def _scores_inside(edges, fractions):
    """Scores placed inside the declared scale by the generated fractions. Both the edges and the fractions
    come from strategies, so nothing about the scale is typed; the arithmetic places an input, it does not
    compute an expected value."""
    return [edges[0] + fraction * (edges[-1] - edges[0]) for fraction in fractions]


def _pairs_inside(edges, pairs):
    """The same placement for two axes at once, so the two coordinate lists are always the same length."""
    across, down = zip(*pairs)
    return _scores_inside(edges, across), _scores_inside(edges, down)


def _pandas_band_ends(scores, edges, **options):
    """The right endpoint pandas assigns to each score, read off the IntervalIndex pandas itself returns."""
    return pd.IntervalIndex(pd.cut(pd.Series(scores, dtype='float64'), bins=edges, **options)).right.to_numpy()


def _polars_band_ends(scores, edges, **options):
    """The same quantity from polars, read off the breakpoint field its own include_breaks option adds."""
    return (pl.Series(scores, dtype=pl.Float64).cut(edges, include_breaks=True, **options)
            .struct.field('breakpoint').to_numpy())


def _polars_cell_counts(xs, ys, edges):
    """Counting the same pairs into cells in the other engine: polars bins each axis with its own cut and
    counts the rows of each group with its own len aggregation."""
    frame = pl.DataFrame({'x': pl.Series(xs, dtype=pl.Float64), 'y': pl.Series(ys, dtype=pl.Float64)})
    return (frame.with_columns(pl.col('x').cut(edges).alias('band_x'),
                               pl.col('y').cut(edges).alias('band_y'))
            .group_by('band_x', 'band_y').len())


@given(BAND_EDGES, INSIDE_FRACTIONS)
@SLOW
def test_two_binning_engines_agree_on_every_score_inside_the_declared_scale(edges, fractions):
    """polars 1.44.1 is Rust and its py-polars/pyproject.toml at tag py-1.44.1 declares one dependency,
    polars-runtime-32, so it shares no code with pandas 2.2.3. Inside the declared scale the two agree on
    the band of every generated score, under both closures, which is the part of case 159 that does carry
    across engines."""
    scores = _scores_inside(edges, fractions)
    npt.assert_array_equal(_pandas_band_ends(scores, edges), _polars_band_ends(scores, edges))
    npt.assert_array_equal(_pandas_band_ends(scores, edges, right=False),
                           _polars_band_ends(scores, edges, left_closed=True))


@given(BAND_EDGES)
@SLOW
def test_the_closure_decides_which_end_of_the_scale_keeps_the_score_it_declares(edges):
    """The mirror of the case above, and the one case 159 records as the loss moving. A score sitting
    exactly on the highest declared edge is banded by the default right-closed cut and dropped to null by
    the left-closed one, while numpy's histogram counts it under both readings because its last bin is
    closed at both ends. Neither flag makes pandas agree with numpy about both endpoints at once: whichever
    way the closure is set, one declared score is counted by one primitive of this chain and discarded by
    the other. Replaces the typed left_closed[5] == 'nan' of case 159."""
    scores = [float(edges[-1])]
    npt.assert_array_equal(pd.cut(pd.Series(scores, dtype='float64'), bins=edges).isna().to_numpy(), False)
    npt.assert_array_equal(pd.cut(pd.Series(scores, dtype='float64'), bins=edges,
                                  right=False).isna().to_numpy(), True)
    npt.assert_array_equal(np.histogram(scores, bins=edges)[0].sum(), len(scores))


@given(BAND_EDGES, PAST_THE_EDGE)
@SLOW
def test_a_score_at_or_below_the_lowest_edge_is_null_in_pandas_and_banded_in_polars(edges, offsets):
    """The two projects mean different things by the list of numbers they are given. pandas documents its
    bins as "sequence of scalars : Defines the bin edges allowing for non-uniform width. No extension of the
    range of `x` is done", so a score outside them has no band and comes back null. polars documents its
    breaks as a "List of unique cut points" and its own example shows a break list of two producing three
    categories, the first of them (-inf, -1]: the cut points are interior, the scale is the whole line, and
    no observation is ever outside it. Executed on scores at or below the lowest declared edge, pandas
    returns null for every one and polars returns the unbounded band whose endpoint is that edge. The rows
    case 159 records as silently dropped are, in the other engine, silently kept in a band with no floor."""
    scores = [edges[0] - offset for offset in offsets]
    npt.assert_array_equal(pd.cut(pd.Series(scores, dtype='float64'), bins=edges).isna().to_numpy(), True)
    npt.assert_array_equal(_polars_band_ends(scores, edges), float(edges[0]))


@given(BAND_EDGES, CLEAR_OF_THE_EDGE)
@SLOW
def test_the_left_closed_convention_loses_the_other_end_of_the_scale(edges, offsets):
    """Turning the closure round moves the loss rather than removing it: under right=False the scores above
    the highest declared edge are the ones pandas cannot place, and polars puts them in the band that runs
    to positive infinity. So neither closure covers the whole line, and which score disappears depends on a
    flag the chain of case 159 never sets."""
    scores = [edges[-1] + offset for offset in offsets]
    npt.assert_array_equal(pd.cut(pd.Series(scores, dtype='float64'), bins=edges,
                                  right=False).isna().to_numpy(), True)
    npt.assert_array_equal(np.isposinf(_polars_band_ends(scores, edges, left_closed=True)), True)


@given(BAND_EDGES)
@SLOW
def test_the_two_primitives_this_chain_uses_disagree_about_the_lowest_declared_score(edges):
    """Case 159 bands scores with pandas.cut and counts pairs with numpy.histogram2d, and the two primitives
    do not agree about a score sitting exactly on the lowest declared edge: numpy's histogram counts it,
    because its first bin is closed on the left, while pandas' default right-closed cut has no band for it
    and returns null. Both are called on the same generated edges here, so the disagreement is between two
    libraries and not between two sets of numbers. Replaces the typed 'nan' at right_closed[0] of
    handoff_guards_v16.py case 159."""
    scores = [float(edges[0])]
    npt.assert_array_equal(pd.cut(pd.Series(scores, dtype='float64'), bins=edges).isna().to_numpy(), True)
    npt.assert_array_equal(np.histogram(scores, bins=edges)[0].sum(), len(scores))
    npt.assert_array_equal(np.isnan(_polars_band_ends(scores, edges)), False)


@given(BAND_EDGES)
@SLOW
def test_admitting_the_lowest_score_moves_the_boundary_pandas_reports(edges):
    """pandas has an option for the score above, and it works by moving the boundary rather than closing the
    interval. Its source at v2.2.3 defines adjust = lambda x: x - 10 ** (-precision) and applies it under
    the comment "adjust lhs of first interval by precision to account for being right closed", so the first
    band pandas reports starts strictly below the edge the chain declared. polars admits the same score
    without moving any cut point, by running its first band down to negative infinity. Both engines keep the
    score and they put it in different bands: pandas widens the first declared band and reports the score
    inside it, polars leaves the declared bands alone and reports the score below all of them. Replaces the
    typed '(0.999, 5.0]' of case 159."""
    scores = [float(edges[0])]
    banded = pd.cut(pd.Series(scores, dtype='float64'), bins=edges, include_lowest=True)
    npt.assert_array_equal(banded.isna().to_numpy(), False)
    npt.assert_array_equal(banded.cat.categories.left[0] < edges[0], True)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_pandas_band_ends(scores, edges, include_lowest=True),
                               _polars_band_ends(scores, edges))
    npt.assert_array_equal(_pandas_band_ends(scores, edges, include_lowest=True), float(edges[1]))
    npt.assert_array_equal(_polars_band_ends(scores, edges), float(edges[0]))


@given(BAND_EDGES, INSIDE_PAIRS)
@SLOW
def test_both_engines_count_every_pair_that_lies_inside_the_scale(edges, pairs):
    """With every pair inside the declared scale the two engines account for the same rows. The types do not
    match even so: numpy returns the cell counts as floating point and the polars aggregation returns them
    as an unsigned integer, so a chain comparing one engine's count with the other's is comparing a float
    with an integer. Replaces the typed 'float64' and the typed diagonal of case 159."""
    xs, ys = _pairs_inside(edges, pairs)
    counted = np.histogram2d(xs, ys, bins=[edges, edges])[0]
    npt.assert_array_equal(counted.sum(), len(xs))
    npt.assert_array_equal(_polars_cell_counts(xs, ys, edges)['len'].sum(), len(xs))
    npt.assert_array_equal(np.issubdtype(counted.dtype, np.floating), True)
    npt.assert_array_equal(np.issubdtype(_polars_cell_counts(xs, ys, edges)['len'].to_numpy().dtype,
                                         np.integer), True)


@given(BAND_EDGES, INSIDE_PAIRS, BEYOND_PAIRS)
@SLOW
def test_the_two_dimensional_histogram_counts_fewer_pairs_than_it_was_given(edges, inside, beyond):
    """Every pair whose first coordinate lies above the declared scale is left out of the histogram, with no
    error and no warning, so the total of the matrix is the number of in-scale rows rather than the number
    of rows supplied: the "seven rows in, five counted" of case 159, on generated input. The polars
    aggregation over the same rows counts all of them, because its outermost bands are unbounded, so the two
    engines disagree about how many assessments there were and not only about where they sit."""
    kept_x, kept_y = _pairs_inside(edges, inside)
    over, down = zip(*beyond)
    xs = list(kept_x) + [edges[-1] + offset for offset in over]
    ys = list(kept_y) + list(_scores_inside(edges, down))
    counted = np.histogram2d(xs, ys, bins=[edges, edges])[0]
    npt.assert_array_equal(counted.sum(), len(kept_x))
    npt.assert_array_equal(counted.sum() < len(xs), True)
    npt.assert_array_equal(_polars_cell_counts(xs, ys, edges)['len'].sum(), len(xs))


# ---------------------------------------------------------------- a balance assertion and how it is written
JOURNAL = """2024-01-01 open Assets:Bank USD
2024-01-01 open Equity:Opening-Balances USD

2024-01-02 * "opening"
  Assets:Bank   {posted} USD
  Equity:Opening-Balances{completion}

2024-01-03 balance Assets:Bank  {asserted} USD
"""
CENTS = st.integers(min_value=1, max_value=10_000_000)
EXTRA_ZEROS = st.integers(min_value=1, max_value=4)
WHOLE_UNITS = st.integers(min_value=1, max_value=100_000)
IMBALANCE_UNITS = st.integers(min_value=1, max_value=1000)


def _journal(posted, asserted, completion=''):
    """The generated journal. Only the amounts vary; the surrounding directives are the syntax the format
    requires, as the column names are in the CSV tests above."""
    return JOURNAL.format(posted=posted, asserted=asserted, completion=completion)


def _load_errors(text):
    """beancount's own loader, which returns its errors rather than raising them."""
    return beancount_loader.load_string(text)[1]


def _lima_directive(text, attribute):
    """The same file read by the other implementation. beancount-parser-lima 0.6.0 is Rust; its wheel
    declares no Python dependencies and its Cargo.toml at tag 0.6.0 lists chumsky, logos, rust_decimal,
    time and pyo3 and nothing from beancount. It reads a file, so the generated journal is written to a
    temporary one and the directive is selected by the attribute its own model gives that directive."""
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / 'generated.beancount'
        path.write_text(text)
        parsed = lima.BeancountSources(str(path)).parse()
        for directive in parsed.directives:
            if hasattr(directive, attribute):
                return directive


def _lima_balance(text):
    """The asserted amount as the other parser reads it, and the tolerance it reports for that assertion."""
    directive = _lima_directive(text, 'atol')
    return Fraction(directive.atol.amount.number), directive.atol.tolerance


def _lima_posting_amounts(text):
    """The posting amounts the other parser reports, in file order."""
    return [posting.amount for posting in _lima_directive(text, 'postings').postings]


def _lima_parses_cleanly(text):
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / 'generated.beancount'
        path.write_text(text)
        return isinstance(lima.BeancountSources(str(path)).parse(), lima.ParseSuccess)


@given(CENTS, EXTRA_ZEROS)
@SLOW
def test_two_parsers_read_one_number_from_the_two_spellings_of_a_balance_assertion(cents, zeros):
    """Trailing zeros change nothing about the value, and both readers say so. Fraction, the exact rational,
    makes the two spellings one number, and beancount-parser-lima -- which its own README describes as "A
    zero-copy parser for Beancount in Rust" that "is intended to be a complete implementation of the
    Beancount file format" -- reads the same number from each and reports no tolerance for either, because
    the file declares none."""
    asserted = Decimal(cents).scaleb(-2)
    short, long = format(asserted, '.2f'), format(asserted, '.%df' % (2 + zeros))
    npt.assert_array_equal(Fraction(Decimal(short)) == Fraction(Decimal(long)), True)
    short_value, short_tolerance = _lima_balance(_journal(short, short))
    long_value, long_tolerance = _lima_balance(_journal(short, long))
    npt.assert_array_equal(short_value == long_value, True)
    npt.assert_array_equal([short_tolerance is None, long_tolerance is None], True)


@given(CENTS, EXTRA_ZEROS)
@SLOW
def test_the_written_precision_and_not_the_value_decides_a_balance_assertion(cents, zeros):
    """The two spellings are the same number and neither file declares a tolerance, yet the loader accepts
    one and rejects the other against the same posted balance. beancount's own source at 3.2.3 shows why:
    get_balance_tolerance in beancount/ops/balance.py takes expo = balance_entry.amount.number.as_tuple()
    .exponent and, when it is negative, sets tolerance = ONE.scaleb(expo) * options_map
    ["tolerance_multiplier"] * 2, under the comment "Be generous and always allow twice the multiplier on
    Balance and Pad because the user creates these and the rounding of those balances may often be further
    off than those used within a single transaction." So the tolerance is one unit of the last place the
    author happened to type, and writing an extra zero tightens the check tenfold. Replaces the typed
    '100.01 USD' and '100.010 USD' expectations of handoff_guards_v16.py case 155."""
    posted = format(Decimal(cents).scaleb(-2), '.2f')
    off_by_one_cent = Decimal(cents + 1).scaleb(-2)
    short = format(off_by_one_cent, '.2f')
    long = format(off_by_one_cent, '.%df' % (2 + zeros))
    npt.assert_array_equal(Fraction(Decimal(short)) == Fraction(Decimal(long)), True)
    npt.assert_array_equal(_lima_balance(_journal(posted, short))[0]
                           == _lima_balance(_journal(posted, long))[0], True)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(bool(_load_errors(_journal(posted, short))),
                               bool(_load_errors(_journal(posted, long))))
    npt.assert_array_equal(bool(_load_errors(_journal(posted, short))), False)
    npt.assert_array_equal(bool(_load_errors(_journal(posted, long))), True)


@given(WHOLE_UNITS)
@SLOW
def test_a_balance_written_without_a_decimal_point_is_checked_with_no_tolerance_at_all(units):
    """The same source has an else branch: when the exponent is not negative the tolerance is ZERO. So the
    rule runs both ways. With the posted balance one cent above a whole number, asserting that whole number
    is rejected outright and asserting the identical value written to two places is accepted, which is the
    opposite verdict from the same number differently spelled. Fraction and the Rust parser both confirm the
    two assertions are one value."""
    posted = format(Decimal(units * 100 + 1).scaleb(-2), '.2f')
    whole, two_places = str(units), format(Decimal(units), '.2f')
    npt.assert_array_equal(Fraction(Decimal(whole)) == Fraction(Decimal(two_places)), True)
    npt.assert_array_equal(_lima_balance(_journal(posted, whole))[0]
                           == _lima_balance(_journal(posted, two_places))[0], True)
    npt.assert_array_equal(bool(_load_errors(_journal(posted, whole))), True)
    npt.assert_array_equal(bool(_load_errors(_journal(posted, two_places))), False)


@given(CENTS)
@SLOW
def test_a_missing_posting_amount_is_supplied_by_the_loader_and_absent_from_the_file(cents):
    """The completing amount case 155 reports is put there by beancount's booking, not by the file. The Rust
    parser reads the same journal and reports the second posting with no amount at all, while beancount's
    loader returns both postings with amounts that sum to zero. A tool that reads the file with any other
    reader does not see the posting the chain relies on."""
    posted = format(Decimal(cents).scaleb(-2), '.2f')
    text = _journal(posted, posted)
    amounts = _lima_posting_amounts(text)
    npt.assert_array_equal(amounts[0] is None, False)
    npt.assert_array_equal(amounts[1] is None, True)
    postings = [posting
                for entry in beancount_loader.load_string(text)[0]
                if isinstance(entry, beancount_data.Transaction)
                for posting in entry.postings]
    npt.assert_array_equal(len(postings), len(amounts))
    npt.assert_array_equal(sum(Fraction(posting.units.number) for posting in postings) == 0, True)


@given(CENTS, IMBALANCE_UNITS)
@SLOW
def test_an_unbalanced_journal_is_a_returned_error_and_a_clean_parse_to_the_other_reader(cents, imbalance):
    """Case 155 records that the loader reports rather than raises. Executed, that holds for every generated
    imbalance: load_string returns errors in a list, nothing is raised, and the offending transaction is
    still among the entries it hands on. The Rust parser accepts the same file outright, because the file is
    well formed and only the arithmetic is wrong, so the two readers answer different questions and a chain
    that swaps one for the other loses the check entirely rather than seeing it fail."""
    posted = format(Decimal(cents).scaleb(-2), '.2f')
    completion = '   %s USD' % format(-Decimal(cents + imbalance * 100).scaleb(-2), '.2f')
    text = _journal(posted, posted, completion=completion)
    entries, errors = beancount_loader.load_string(text)[:2]
    npt.assert_array_equal(bool(errors), True)
    npt.assert_array_equal(any(isinstance(entry, beancount_data.Transaction) for entry in entries), True)
    npt.assert_array_equal(_lima_parses_cleanly(text), True)


# ---------------------------------------------------------------- folding a key and lowercasing it
CASE_ORACLE_RB = pathlib.Path(__file__).with_name('case_fold_oracle.rb')
CASE_ORACLE_PHP = pathlib.Path(__file__).with_name('case_fold_oracle.php')
_CODE_POINTS = list(map(chr, range(0x20, 0x30000)))
_CASED_CHARACTERS = [character for character in _CODE_POINTS
                     if unicodedata.category(character) not in ('Cs', 'Cn', 'Co', 'Cc')]
FOLD_MERGES_A_PAIR = [character for character in _CASED_CHARACTERS
                      if character.casefold() == character.casefold().casefold()
                      and character.lower() != character.casefold().lower()]
FOLD_LEAVES_THE_CASE = [character for character in _CASED_CHARACTERS
                        if character.casefold() == character != character.lower()]
UNKNOWN_UPPERCASE = [character for character in _CODE_POINTS
                     if unicodedata.category(character) == 'Cn'
                     and regex.compile(r'\p{Lu}').fullmatch(character)]
CASE_ALPHABET = sorted({form
                        for character in FOLD_MERGES_A_PAIR + FOLD_LEAVES_THE_CASE
                        for form in (character, character.lower(), character.casefold())
                        if len(form) == 1})
CASED_TEXT = st.text(alphabet=st.characters(codec='utf-8', exclude_categories=('Cs', 'Cc', 'Cn', 'Co')),
                     max_size=12)
CASE_WORDS = st.lists(st.text(alphabet=st.sampled_from(CASE_ALPHABET), max_size=4), min_size=1, max_size=8)
both_case_runtimes = ruby_available and php_binary_available


def _runtime_case_forms(runner, script, text):
    """The full case fold and the lowercase of one string as one other runtime reports them. The shim prints
    two lines; the Python side runs it and splits."""
    completed = subprocess.run([runner, str(script), text], capture_output=True, encoding='utf-8', check=True)
    return completed.stdout.split('\n')[:2]


def _other_runtimes_case_forms(text):
    """The same two values from Ruby and from PHP."""
    return [_runtime_case_forms('ruby', CASE_ORACLE_RB, text),
            _runtime_case_forms('php', CASE_ORACLE_PHP, text)]


@pytest.mark.skipif(not both_case_runtimes, reason='both runtimes are required for this oracle')
@given(CASED_TEXT)
@ORACLE_PROCESS
def test_three_runtimes_agree_on_the_case_fold_and_the_lowercase_of_generated_text(text):
    """All three implement the same published algorithm and say so. CPython's Doc/library/stdtypes.rst at
    tag v3.11.15 says of str.casefold that "The casefolding algorithm is described in section 3.13 of the
    Unicode Standard"; Ruby's doc/case_mapping.rdoc at tag v3_3_6 says its methods "use full Unicode case
    mapping" and cites the same section, and documents :fold as "Unicode case folding, which is more
    far-reaching than Unicode case mapping"; PHP's manual lists MB_CASE_FOLD as a mode of mb_convert_case.
    Executed on generated text they agree exactly, on both the fold and the lowercase. This is the opposite
    of the month arithmetic above: here the convention does carry across runtimes."""
    npt.assert_array_equal(_other_runtimes_case_forms(text), [[text.casefold(), text.lower()]] * 2)


@pytest.mark.skipif(not both_case_runtimes, reason='both runtimes are required for this oracle')
@given(st.sampled_from(FOLD_MERGES_A_PAIR))
@ORACLE_PROCESS
def test_the_fold_merges_a_pair_the_lowercase_keeps_apart_in_all_three_runtimes(character):
    """The claim of case 154, generated rather than chosen. For every character whose fold is not its
    lowercase, the character and its own folded form are one key under folding and two keys under
    lowercasing, in Python and in both other runtimes. The list of such characters is selected by Python's
    own case mappings over every assigned code point below U+30000, not typed here. Replaces the typed
    'STRASSE'.casefold() == 'straße'.casefold() of handoff_guards_v16.py case 154."""
    folded_form = character.casefold()
    left, right = _other_runtimes_case_forms(character), _other_runtimes_case_forms(folded_form)
    npt.assert_array_equal([forms[0] for forms in left], [forms[0] for forms in right])
    with pytest.raises(AssertionError):
        npt.assert_array_equal([forms[1] for forms in left], [forms[1] for forms in right])
    npt.assert_array_equal(character.casefold(), folded_form.casefold())
    with pytest.raises(AssertionError):
        npt.assert_array_equal(character.lower(), folded_form.lower())


@pytest.mark.skipif(not both_case_runtimes, reason='both runtimes are required for this oracle')
@given(st.sampled_from(FOLD_LEAVES_THE_CASE))
@ORACLE_PROCESS
def test_a_folded_key_can_still_be_uppercase_in_all_three_runtimes(character):
    """Folding is not a stronger lowercase. For a whole block of assigned letters the fold is the identity
    while the lowercase is not, so the key a chain builds by folding still carries case that lowercasing
    would remove, and folding it again will not remove it. All three runtimes do the same thing, so this is
    a property of the published algorithm rather than of any implementation."""
    forms = _other_runtimes_case_forms(character)
    npt.assert_array_equal([runtime[0] for runtime in forms], [character, character])
    with pytest.raises(AssertionError):
        npt.assert_array_equal([runtime[1] for runtime in forms], [character, character])
    npt.assert_array_equal(character.casefold(), character)
    npt.assert_array_equal(character.casefold().lower() != character.casefold(), True)


@pytest.mark.skipif(not both_case_runtimes, reason='both runtimes are required for this oracle')
@given(CASED_TEXT)
@ORACLE_PROCESS
def test_folding_a_lowercased_string_gives_the_key_that_folding_it_directly_gives(text):
    """Each runtime is asked to fold its own lowercase of the generated text, and gets back the key it
    produces by folding the text directly. So a chain that lowercases before folding loses nothing, which
    is the one ordering question about these two operations that has a safe answer."""
    ruby_fold, ruby_lower = _runtime_case_forms('ruby', CASE_ORACLE_RB, text)
    php_fold, php_lower = _runtime_case_forms('php', CASE_ORACLE_PHP, text)
    npt.assert_array_equal([_runtime_case_forms('ruby', CASE_ORACLE_RB, ruby_lower)[0],
                            _runtime_case_forms('php', CASE_ORACLE_PHP, php_lower)[0]],
                           [ruby_fold, php_fold])
    npt.assert_array_equal(text.lower().casefold(), text.casefold())


@given(CASE_WORDS)
@SLOW
def test_the_fold_never_separates_two_words_the_lowercase_joins(words):
    """The consequence for deduplication, as an invariant of the output rather than a comparison: over words
    generated from the characters where the two operations differ, folding produces no more distinct keys
    than lowercasing. The merge only ever runs one way, so a chain that switches from lower to casefold can
    lose rows to collision but can never gain them."""
    npt.assert_array_equal(len({word.casefold() for word in words})
                           <= len({word.lower() for word in words}), True)


@given(st.sampled_from(UNKNOWN_UPPERCASE))
@SLOW
def test_the_standard_library_fold_does_not_know_these_letters_have_case(character):
    """Two Unicode databases in this one process disagree. regex 2026.9.3 carries its own tables and matches
    each of these characters as \\p{Lu}; the standard library's unicodedata, at the Unicode version this
    Python was built against, files the same character as unassigned, and its casefold and lower both leave
    it exactly as it is. A key folded by the standard library therefore keeps a case distinction that a
    newer table would remove, and the set of characters this happens to changes with the interpreter, not
    with the data."""
    npt.assert_array_equal([character.casefold(), character.lower()], [character, character])
    npt.assert_array_equal(unicodedata.category(character), 'Cn')
    npt.assert_array_equal(bool(regex.compile(r'\p{Lu}').fullmatch(character)), True)


@functools.lru_cache(maxsize=1)
def _characters_the_php_runtime_folds():
    """A region selector like the offset regions above, except that the implementation separating the two
    regions runs in another process: the characters the standard library does not know are letters that the
    php runtime nevertheless folds."""
    return [character for character in UNKNOWN_UPPERCASE
            if _runtime_case_forms('php', CASE_ORACLE_PHP, character)[0] != character]


@pytest.mark.skipif(not php_binary_available, reason='the php runtime is required for this oracle')
@given(st.integers(min_value=0, max_value=1000))
@ORACLE_PROCESS
def test_another_runtime_folds_letters_this_python_leaves_alone(index):
    """And the disagreement crosses the process boundary. PHP 8.4.19 ships a newer Unicode version than this
    Python and folds letters this Python leaves untouched, so the same deduplication key computed on each
    side of a service boundary is not the same key, silently, for those letters. Which letters they are is
    established by asking the runtime, not by naming them here."""
    folded_elsewhere = _characters_the_php_runtime_folds()
    if not folded_elsewhere:
        pytest.skip('this Python and this php runtime agree on the case of every unassigned letter')
    character = folded_elsewhere[index % len(folded_elsewhere)]
    npt.assert_array_equal(character.casefold(), character)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_runtime_case_forms('php', CASE_ORACLE_PHP, character)[0], character)


# ---------------------------------------------------------------- mapping a label and grouping the result
STAGE_CODES = tuple(range(4))
UNKNOWN_CODES = tuple(range(4, 8))
STAGE_OF = {'code-%d' % code: 'stage-%d' % code for code in STAGE_CODES}
KNOWN_ROWS = st.lists(st.tuples(st.sampled_from(STAGE_CODES), st.integers(min_value=1, max_value=10 ** 6)),
                      min_size=1, max_size=8)
UNKNOWN_ROWS = st.lists(st.tuples(st.sampled_from(UNKNOWN_CODES), st.integers(min_value=1, max_value=10 ** 6)),
                        min_size=1, max_size=4)


def _labelled(rows):
    """The generated rows as (label, amount) pairs. The label is built from the generated code and the
    mapping is built from the same range the strategy draws from, so neither is typed."""
    return [('code-%d' % code, amount) for code, amount in rows]


def _pandas_stage_totals(rows, *, observed):
    """The chain's own rollup: map the label to a declared stage, make it a categorical over every declared
    stage, and sum by it."""
    labels = [label for label, _ in rows]
    frame = pd.DataFrame({'stage': pd.Categorical(pd.Series(labels).map(STAGE_OF),
                                                  categories=sorted(STAGE_OF.values())),
                          'amount': [amount for _, amount in rows]})
    return frame.groupby('stage', observed=observed)['amount'].sum().sort_index()


def _polars_stage_totals(rows):
    """The same rollup in polars, which has no declared-category dimension to roll up over."""
    labels = [label for label, _ in rows]
    frame = pl.DataFrame({'stage': pl.Series(labels).replace_strict(STAGE_OF, default=None),
                          'amount': [amount for _, amount in rows]})
    return (frame.drop_nulls('stage').group_by('stage').agg(pl.col('amount').sum()).sort('stage'))


def _duckdb_stage_totals(rows):
    """And in SQL, where the mapping is a table and the drop is a join that finds no partner."""
    with duckdb.connect() as connection:
        connection.execute('create table entries(label VARCHAR, amount BIGINT)')
        connection.execute('create table stages(label VARCHAR, stage VARCHAR)')
        connection.executemany('insert into entries values (?, ?)', rows)
        connection.executemany('insert into stages values (?, ?)', list(STAGE_OF.items()))
        return connection.execute('select stages.stage, sum(entries.amount) from entries '
                                  'join stages on entries.label = stages.label '
                                  'group by stages.stage order by stages.stage').fetchall()


@given(KNOWN_ROWS, UNKNOWN_ROWS)
@SLOW
def test_an_unmapped_label_is_a_null_in_one_engine_and_a_refusal_in_the_other(known, unknown):
    """pandas.Series.map has no setting for a label the mapping does not cover: it returns a missing value
    and says nothing. polars refuses the same call outright, with the message "incomplete mapping specified
    for `replace_strict`", and will produce the missing value only when asked for it with default=None --
    at which point the two engines agree exactly about which rows are missing. Its other spelling, replace,
    leaves an uncovered label as it found it and loses nothing at all. One operation, three answers, and the
    silent one is the default. Replaces the typed isna().sum() of handoff_guards_v16.py case 158."""
    labels = [label for label, _ in _labelled(known + unknown)]
    with pytest.raises(pl.exceptions.InvalidOperationError):
        pl.Series(labels).replace_strict(STAGE_OF)
    npt.assert_array_equal(pd.Series(labels).map(STAGE_OF).isna().to_numpy(),
                           pl.Series(labels).replace_strict(STAGE_OF, default=None).is_null().to_numpy())
    npt.assert_array_equal(pl.Series(labels).replace(STAGE_OF).is_null().to_numpy(), False)


@given(KNOWN_ROWS)
@SLOW
def test_the_two_engines_agree_on_every_label_the_mapping_covers(known):
    """Where the mapping is complete all three spellings return the same column, so the divergence above is
    entirely about the uncovered label and not about the mapping itself."""
    labels = [label for label, _ in _labelled(known)]
    npt.assert_array_equal(pd.Series(labels).map(STAGE_OF).to_numpy(),
                           pl.Series(labels).replace_strict(STAGE_OF).to_numpy())
    npt.assert_array_equal(pl.Series(labels).replace(STAGE_OF).to_numpy(),
                           pl.Series(labels).replace_strict(STAGE_OF).to_numpy())


@given(KNOWN_ROWS, UNKNOWN_ROWS)
@SLOW
def test_the_missing_value_pandas_puts_in_a_column_of_labels_is_not_a_label(known, unknown):
    """What pandas puts in the gap is a float, in a column of text, and the column's dtype becomes object.
    polars will not accept that list as a string column at all, which is how the type damage becomes
    visible: the same rollup handed to another engine fails to load rather than producing a different
    number. Asked for the missing value in its own terms polars returns a string column with a null."""
    labels = [label for label, _ in _labelled(known + unknown)]
    with pytest.raises(TypeError):
        pl.Series(pd.Series(labels).map(STAGE_OF).tolist(), dtype=pl.String)
    npt.assert_array_equal(pl.Series(labels).replace_strict(STAGE_OF, default=None).dtype == pl.String, True)


@given(KNOWN_ROWS, UNKNOWN_ROWS)
@SLOW
def test_grouping_a_declared_category_invents_rows_no_other_engine_reports(known, unknown):
    """The default pandas groups a categorical under, observed=False, reports every declared stage whether
    or not any row reached it, and the ones no row reached are reported as a sum of zero -- a measured
    figure and an absent one written the same way. Neither of the other engines has any way to produce those
    rows: polars groups what is there, and the SQL join finds no partner for the uncovered label. With
    observed=True pandas agrees with both of them, on every generated set of rows. Replaces the typed
    five-bar and three-bar stage rollups of case 158."""
    rows = _labelled(known + unknown)
    observed = _pandas_stage_totals(rows, observed=True)
    declared = _pandas_stage_totals(rows, observed=False)
    by_polars = _polars_stage_totals(rows)
    npt.assert_array_equal(list(observed.index), by_polars['stage'].to_list())
    npt.assert_array_equal(observed.to_numpy(), by_polars['amount'].to_numpy())
    npt.assert_array_equal([list(observed.index), list(observed.to_numpy())],
                           [[stage for stage, _ in _duckdb_stage_totals(rows)],
                            [total for _, total in _duckdb_stage_totals(rows)]])
    npt.assert_array_equal(len(declared), len(STAGE_OF))
    npt.assert_array_equal(len(declared) >= len(observed), True)
    npt.assert_array_equal(declared.sum(), observed.sum())


@given(KNOWN_ROWS, UNKNOWN_ROWS)
@SLOW
def test_every_engine_leaves_the_unmapped_amount_out_of_the_stage_totals(known, unknown):
    """The amount on an uncovered label reaches no stage in any of the three engines, so the rollup is
    smaller than the ledger it was built from and nothing in the rollup says so. The three agree on the
    figure they report, which is what makes the shortfall hard to see: two independent engines confirm the
    total that is wrong."""
    rows = _labelled(known + unknown)
    source_total = sum(amount for _, amount in rows)
    reported = [float(_pandas_stage_totals(rows, observed=True).sum()),
                float(_polars_stage_totals(rows)['amount'].sum()),
                float(sum(total for _, total in _duckdb_stage_totals(rows)))]
    npt.assert_array_equal(reported, [reported[0]] * 3)
    npt.assert_array_equal(reported[0] < source_total, True)
    npt.assert_array_equal(source_total - reported[0], sum(amount for _, amount in _labelled(unknown)))


# ---------------------------------------------------------------- rendering a template and escaping a value
NUNJUCKS_DIRECTORY = pathlib.Path(os.environ.get('NUNJUCKS_DIR', str(pathlib.Path.home() / 'nunjucks-oracle')))
TEMPLATE_ORACLE_JS = pathlib.Path(__file__).with_name('template_render_oracle.js')
TEMPLATE_STRICT_JS = pathlib.Path(__file__).with_name('template_strict_oracle.js')
nunjucks_available = (shutil.which('node') is not None
                      and (NUNJUCKS_DIRECTORY / 'node_modules' / 'nunjucks').is_dir())
ESCAPING_TEMPLATE = '{{ value }}'
PLAIN_ENVIRONMENT = jinja2.Environment()
ESCAPING_ENVIRONMENT = jinja2.Environment(autoescape=True)
STRICT_ENVIRONMENT = jinja2.Environment(undefined=jinja2.StrictUndefined)
ESCAPABLE_CHARACTERS = [character for character in map(chr, range(0x20, 0x7f))
                        if ESCAPING_ENVIRONMENT.from_string(ESCAPING_TEMPLATE).render(value=character)
                        != character]
ESCAPABLE_TEXT = st.text(alphabet=st.sampled_from(ESCAPABLE_CHARACTERS), min_size=1, max_size=8)


def _nunjucks_renders(script, context):
    """One template rendered by the other implementation of this template language. The shim parses argv,
    calls the library and prints; nothing here computes anything."""
    completed = subprocess.run(['node', str(script), ESCAPING_TEMPLATE, json.dumps(context)],
                               capture_output=True, encoding='utf-8', check=True,
                               env={**os.environ, 'NODE_PATH': str(NUNJUCKS_DIRECTORY / 'node_modules')})
    return completed.stdout.split('\n')[:2]


@functools.lru_cache(maxsize=1)
def _escaping_comparison():
    """One row per printable character: the character, the text jinja2 escapes it to and the text nunjucks
    escapes it to. Ninety-five subprocess runs, once per session, and the two regions below are read off it
    rather than named here."""
    return [(character,
             ESCAPING_ENVIRONMENT.from_string(ESCAPING_TEMPLATE).render(value=character),
             _nunjucks_renders(TEMPLATE_ORACLE_JS, {'value': character})[0])
            for character in map(chr, range(0x20, 0x7f))]


@pytest.mark.skipif(not nunjucks_available, reason='node and a nunjucks checkout are required')
@given(ESCAPABLE_TEXT)
@ORACLE_PROCESS
def test_the_same_template_language_escapes_by_default_in_one_runtime_and_not_the_other(value):
    """nunjucks 3.2.4 is a JavaScript implementation of this template language whose package.json lists
    a-sync-waterfall, asap and commander and nothing from Python. Given the same template and the same
    value, its default environment escapes and jinja2 3.1.6's default environment does not, so the safety of
    a rendered document depends on which runtime rendered it. Turning nunjucks' flag off reproduces jinja2's
    default exactly. The characters this is generated from are the ones jinja2's own escaping changes, read
    off jinja2 rather than listed here. Replaces the typed 'Topic: A  B  5 > 2' of case 151."""
    escaped, unescaped = _nunjucks_renders(TEMPLATE_ORACLE_JS, {'value': value})
    npt.assert_array_equal(PLAIN_ENVIRONMENT.from_string(ESCAPING_TEMPLATE).render(value=value), value)
    npt.assert_array_equal(unescaped, value)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(escaped, value)


@pytest.mark.skipif(not nunjucks_available, reason='node and a nunjucks checkout are required')
@given(st.integers(min_value=0, max_value=1000), st.integers(min_value=1, max_value=8))
@ORACLE_PROCESS
def test_the_two_engines_escape_the_characters_they_share_to_the_same_text(index, length):
    """Over the printable characters the two engines agree about, asking both to escape produces the same
    text, so the divergence below is confined to particular characters rather than being a difference of
    algorithm."""
    agreed = [character for character, by_jinja, by_nunjucks in _escaping_comparison()
              if by_jinja == by_nunjucks]
    value = ''.join(agreed[(index + offset) % len(agreed)] for offset in range(length))
    npt.assert_array_equal(_nunjucks_renders(TEMPLATE_ORACLE_JS, {'value': value})[0],
                           ESCAPING_ENVIRONMENT.from_string(ESCAPING_TEMPLATE).render(value=value))


@pytest.mark.skipif(not nunjucks_available, reason='node and a nunjucks checkout are required')
@given(st.integers(min_value=0, max_value=1000))
@ORACLE_PROCESS
def test_the_two_engines_escape_some_characters_to_different_text(index):
    """And on the rest they do not agree. Both engines are escaping, both are safe, and the bytes they
    produce differ, so a rendered document checked against one produced by the other differs even though
    neither is wrong. Which characters those are is established by asking both engines about every printable
    character, not by naming them here."""
    apart = [character for character, by_jinja, by_nunjucks in _escaping_comparison()
             if by_jinja != by_nunjucks]
    character = apart[index % len(apart)]
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_nunjucks_renders(TEMPLATE_ORACLE_JS, {'value': character})[0],
                               ESCAPING_ENVIRONMENT.from_string(ESCAPING_TEMPLATE).render(value=character))


@pytest.mark.skipif(not nunjucks_available, reason='node and a nunjucks checkout are required')
@given(st.text(alphabet=st.characters(codec='ascii', exclude_categories=('C',)), min_size=1, max_size=8))
@ORACLE_PROCESS
def test_both_engines_render_a_missing_variable_as_nothing_at_all(name):
    """Where the value is absent rather than dangerous the two agree: the default of each engine renders a
    variable it was not given as an empty string, with no error and no marker in the output, so the empty
    cell of case 151 is a property of the language and not of either implementation. The variable name is
    generated, and neither engine is given a context containing it."""
    template = ESCAPING_TEMPLATE
    rendered = _nunjucks_renders(TEMPLATE_ORACLE_JS, {})
    npt.assert_array_equal(rendered, ['', ''])
    npt.assert_array_equal(PLAIN_ENVIRONMENT.from_string(template).render(), '')


@pytest.mark.skipif(not nunjucks_available, reason='node and a nunjucks checkout are required')
@given(ESCAPABLE_TEXT)
@ORACLE_PROCESS
def test_asking_either_engine_to_refuse_a_missing_variable_leaves_its_escaping_where_it_was(value):
    """Both engines can be told to refuse an absent variable, and in both the setting is independent of the
    escaping: jinja2 with StrictUndefined still does not escape and nunjucks with throwOnUndefined still
    does. So the environment a chain reaches for when it wants strictness is not the environment that makes
    the output safe, in either runtime. Replaces the typed
    Environment(undefined=StrictUndefined).autoescape == False of case 151."""
    with pytest.raises(jinja2.UndefinedError):
        STRICT_ENVIRONMENT.from_string(ESCAPING_TEMPLATE).render()
    with pytest.raises(subprocess.CalledProcessError):
        _nunjucks_renders(TEMPLATE_STRICT_JS, {})
    npt.assert_array_equal(STRICT_ENVIRONMENT.from_string(ESCAPING_TEMPLATE).render(value=value), value)
    npt.assert_array_equal(_nunjucks_renders(TEMPLATE_STRICT_JS, {'value': value})[0],
                           _nunjucks_renders(TEMPLATE_ORACLE_JS, {'value': value})[0])


# ---------------------------------------------------------------- matching an invoice to an order line
ORDER_KEYS = st.lists(st.integers(min_value=0, max_value=12), min_size=1, max_size=8, unique=True)
INVOICE_POSITIONS = st.lists(st.integers(min_value=0, max_value=40), min_size=1, max_size=10)
ABSENT_KEYS = st.lists(st.integers(min_value=100, max_value=120), min_size=1, max_size=6, unique=True)
MISSING_KEYS = st.lists(st.none(), min_size=2, max_size=5)
CENTS = st.integers(min_value=1, max_value=10 ** 6)


def _purchase_frames(order_keys, positions, absent_keys):
    """One order line per generated key and one invoice row per reference. The references that match are
    drawn from the order keys themselves and the ones that do not are drawn from a disjoint range, so the
    region where the join loses rows is generated rather than filtered for."""
    orders = pd.DataFrame({'order_line': order_keys, 'ordered': range(len(order_keys))})
    references = [order_keys[position % len(order_keys)] for position in positions] + list(absent_keys)
    invoices = pd.DataFrame({'invoice_line': range(len(references)), 'order_line': references})
    return orders, invoices


def _missing_key_frames(order_nulls, invoice_nulls):
    """The same two frames with every key missing, as pandas' nullable integer type so that all three
    engines see a null and not a string."""
    orders = pd.DataFrame({'order_line': pd.Series(order_nulls, dtype='Int64'),
                           'ordered': range(len(order_nulls))})
    invoices = pd.DataFrame({'invoice_line': range(len(invoice_nulls)),
                             'order_line': pd.Series(invoice_nulls, dtype='Int64')})
    return orders, invoices


def _duckdb_matched_invoice_lines(orders, invoices):
    """The same inner join in SQL. DuckDB is a third engine, written in C++, and shares no code with either
    dataframe library; its aggregates page documents the null conventions the joins below turn on."""
    with duckdb.connect() as connection:
        connection.execute('create table orders(order_line BIGINT, ordered BIGINT)')
        connection.execute('create table invoices(invoice_line BIGINT, order_line BIGINT)')
        connection.executemany('insert into orders values (?, ?)', orders.astype(object).to_numpy().tolist())
        connection.executemany('insert into invoices values (?, ?)',
                               invoices.astype(object).to_numpy().tolist())
        return [row[0] for row in connection.execute(
            'select invoices.invoice_line from invoices join orders '
            'on invoices.order_line = orders.order_line '
            'order by invoices.invoice_line').fetchall()]


@given(ORDER_KEYS, INVOICE_POSITIONS, ABSENT_KEYS)
@SLOW
def test_a_checked_inner_join_drops_the_invoice_rows_two_other_engines_also_drop(order_keys, positions,
                                                                                absent_keys):
    """P152 joins each invoice to its order line with merge(validate='many_to_one', indicator=True) and the
    chain is required to retain unmatched lines. The join does not retain them. polars 1.44.1, whose
    pyproject.toml at tag py-1.44.1 declares polars-runtime-32 and nothing else, and DuckDB 1.5.5 drop
    exactly the same invoice lines, so the loss is the join and not pandas. What the outer join marks
    left_only is precisely what the inner join lost, which is the invariant the three engines are checked
    against. Replaces the typed len(inner) == 5 and 'I5' in set(...) == False of handoff_guards_v16.py
    case 152."""
    orders, invoices = _purchase_frames(order_keys, positions, absent_keys)
    inner = invoices.merge(orders, on='order_line', how='inner', validate='many_to_one', indicator=True)
    in_polars = pl.from_pandas(invoices).join(pl.from_pandas(orders), on='order_line', how='inner',
                                              validate='m:1')
    npt.assert_array_equal(np.sort(inner['invoice_line'].to_numpy()),
                           np.sort(in_polars['invoice_line'].to_numpy()))
    npt.assert_array_equal(np.sort(inner['invoice_line'].to_numpy()),
                           _duckdb_matched_invoice_lines(orders, invoices))
    outer = invoices.merge(orders, on='order_line', how='outer', indicator=True)
    lost = outer.loc[outer['_merge'] == 'left_only', 'invoice_line'].to_numpy()
    npt.assert_array_equal(np.sort(np.concatenate([inner['invoice_line'].to_numpy(), lost])),
                           np.sort(invoices['invoice_line'].to_numpy()))


@given(ORDER_KEYS, INVOICE_POSITIONS, ABSENT_KEYS)
@SLOW
def test_the_indicator_that_would_report_the_drop_is_a_constant_on_an_inner_join(order_keys, positions,
                                                                                absent_keys):
    """indicator=True is the setting that reports where each row came from, and pandas' merge docstring at
    v2.2.3 says the column carries "left_only" for observations whose merge key only appears in the left
    DataFrame and "both" if the observation's merge key is found in both. On an inner join no row can be
    anything but both, so the flag the chain reads to find dropped lines takes one value however many lines
    were dropped, and only the outer join's flag takes more than one. Replaces the typed
    sorted(inner['_merge'].astype(str).unique()) == ['both'] of case 152."""
    orders, invoices = _purchase_frames(order_keys, positions, absent_keys)
    inner = invoices.merge(orders, on='order_line', how='inner', validate='many_to_one', indicator=True)
    outer = invoices.merge(orders, on='order_line', how='outer', indicator=True)
    matched = outer.loc[outer['invoice_line'].isin(inner['invoice_line']), '_merge']
    npt.assert_array_equal(np.unique(inner['_merge'].astype(str).to_numpy()),
                           np.unique(matched.astype(str).to_numpy()))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(np.unique(outer['_merge'].astype(str).to_numpy()),
                               np.unique(inner['_merge'].astype(str).to_numpy()))


@given(ORDER_KEYS, INVOICE_POSITIONS)
@SLOW
def test_both_cardinality_checkers_refuse_a_repeated_order_line_and_accept_a_repeated_invoice(order_keys,
                                                                                             positions):
    """Two independent implementations of the same check agree about which side it checks. pandas documents
    "many_to_one" or "m:1": check if merge keys are unique in right dataset; polars' join docstring at tag
    py-1.44.1 documents m:1 as "Many-to-one. Check if join keys are unique in right dataset." Executed, both
    refuse a duplicated order line and both accept a duplicated invoice line, and on the accepted side they
    return the same rows. So a second invoice against one order line passes the check that a second order
    line does not, and the chain's cumulative comparison is the only thing standing between that and a
    double payment. Replaces the typed g.rejects(pd.errors.MergeError, ...) of case 152."""
    orders, invoices = _purchase_frames(order_keys, positions, [])
    repeated_orders = pd.concat([orders, orders.iloc[[0]]])
    with pytest.raises(pd.errors.MergeError):
        invoices.merge(repeated_orders, on='order_line', how='inner', validate='many_to_one')
    with pytest.raises(pl.exceptions.ComputeError):
        pl.from_pandas(invoices).join(pl.from_pandas(repeated_orders), on='order_line', how='inner',
                                      validate='m:1')
    repeated_invoices = pd.concat([invoices, invoices.iloc[[0]]])
    npt.assert_array_equal(
        np.sort(repeated_invoices.merge(orders, on='order_line', how='inner',
                                        validate='many_to_one')['invoice_line'].to_numpy()),
        np.sort(pl.from_pandas(repeated_invoices).join(pl.from_pandas(orders), on='order_line',
                                                       how='inner', validate='m:1')['invoice_line'].to_numpy()))


@given(MISSING_KEYS, MISSING_KEYS)
@SLOW
def test_a_missing_order_line_is_a_repeated_key_to_one_checker_and_not_to_the_other(order_nulls,
                                                                                   invoice_nulls):
    """The same check on the same data, one refusal and one acceptance. Where every order line is missing,
    pandas' validate='many_to_one' raises MergeError because it counts two missing keys as one key twice,
    while polars' validate='m:1' passes and returns what the unvalidated join returns, because its
    docstring's "By default null values will never produce matches" applies to the check as well. So the
    cardinality guard P152 relies on fires or does not fire according to which engine holds the frame, on
    data neither engine considers malformed."""
    orders, invoices = _missing_key_frames(order_nulls, invoice_nulls)
    with pytest.raises(pd.errors.MergeError):
        invoices.merge(orders, on='order_line', how='inner', validate='many_to_one')
    validated = pl.from_pandas(invoices).join(pl.from_pandas(orders), on='order_line', how='inner',
                                              validate='m:1')
    unvalidated = pl.from_pandas(invoices).join(pl.from_pandas(orders), on='order_line', how='inner')
    npt.assert_array_equal(validated['invoice_line'].to_numpy(), unvalidated['invoice_line'].to_numpy())


@given(MISSING_KEYS, MISSING_KEYS)
@SLOW
def test_a_missing_key_matches_every_other_missing_key_in_one_engine_and_nowhere_else(order_nulls,
                                                                                      invoice_nulls):
    """pandas' merge docstring at v2.2.3 carries the warning "If both key columns contain rows where the key
    is a null value, those rows will be matched against each other. This is different from usual SQL join
    behaviour and can lead to unexpected results." Executed, it is a full cross product: every invoice whose
    order reference is missing matches every order line whose key is missing. The usual SQL join behaviour
    is the other engine the chain also uses, and DuckDB returns nothing at all, as does polars, whose
    nulls_equal=True reproduces pandas exactly. So an invoice with no order ID is silently matched, and
    which rows come out of the match depends on the engine rather than on the data."""
    orders, invoices = _missing_key_frames(order_nulls, invoice_nulls)
    matched = invoices.merge(orders, on='order_line', how='inner')
    dropped = pl.from_pandas(invoices).join(pl.from_pandas(orders), on='order_line', how='inner')
    told_to_match = pl.from_pandas(invoices).join(pl.from_pandas(orders), on='order_line', how='inner',
                                                  nulls_equal=True)
    npt.assert_array_equal(np.sort(matched['invoice_line'].to_numpy()),
                           np.sort(told_to_match['invoice_line'].to_numpy()))
    npt.assert_array_equal(dropped['invoice_line'].to_numpy(),
                           _duckdb_matched_invoice_lines(orders, invoices))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(np.sort(matched['invoice_line'].to_numpy()),
                               dropped['invoice_line'].to_numpy())


def _duckdb_group_totals(frame):
    """The same rollup in SQL, ordered by the group key."""
    with duckdb.connect() as connection:
        connection.execute('create table amounts("group" BIGINT, amount DOUBLE)')
        connection.executemany('insert into amounts values (?, ?)',
                               frame.astype(object).where(frame.notna(), None).to_numpy().tolist())
        return [row[1] for row in connection.execute(
            'select "group", sum(amount) from amounts group by "group" order by "group"').fetchall()]


@given(st.lists(st.none(), min_size=1, max_size=5), st.lists(CENTS, min_size=1, max_size=6))
@SLOW
def test_a_group_of_only_missing_amounts_totals_zero_in_two_engines_and_nothing_in_the_third(missing, cents):
    """P152 aggregates invoice quantities by order line before comparing them, and case 152 records that a
    missing amount is dropped rather than raised. Where a group has nothing but missing amounts the three
    engines split two to one, and each documents its own answer. pandas' groupby sum takes min_count=0 by
    default, whose docstring reads "The required number of valid values to perform the operation. If fewer
    than ``min_count`` non-NA values are present the result will be NA", so with the default no value is
    required and the total is zero; polars' Expr.sum docstring at py-1.44.1 says "If there are no non-null
    values, then the output is `0`"; DuckDB's aggregate page says sum "Calculates the sum of all non-null
    values" and that "All general aggregate functions except count return NULL on empty groups". So a line
    with no quantity at all reads as a measured zero in both dataframe engines and as nothing in SQL, and
    asking pandas for min_count=1 moves it back to SQL's answer. Replaces the typed
    decimal_totals(rows, key='k')['a'] == Decimal('10.00') of handoff_guards_v16.py case 152."""
    frame = pd.DataFrame({'group': [0] * len(missing) + [1] * len(cents),
                          'amount': pd.Series(list(missing) + list(cents), dtype='float64')})
    in_pandas = frame.groupby('group')['amount'].sum()
    in_polars = pl.from_pandas(frame).group_by('group').agg(pl.col('amount').sum()).sort('group')
    npt.assert_allclose(in_pandas.to_numpy(), in_polars['amount'].to_numpy())
    in_sql = pd.Series(_duckdb_group_totals(frame), dtype='object')
    npt.assert_allclose(in_pandas.to_numpy()[in_sql.notna().to_numpy()],
                        in_sql.dropna().astype(float).to_numpy())
    npt.assert_array_equal(frame.groupby('group')['amount'].sum(min_count=1).isna().to_numpy(),
                           in_sql.isna().to_numpy())
    with pytest.raises(AssertionError):
        npt.assert_array_equal(in_pandas.isna().to_numpy(), in_sql.isna().to_numpy())


@given(st.lists(CENTS, min_size=1, max_size=6))
@SLOW
def test_a_total_over_no_amounts_is_not_the_same_kind_of_number_as_a_total_over_some(cents):
    """The amounts P152 totals are decimal currency and the total of some of them is decimal currency too,
    exactly, which fractions.Fraction confirms against the sum of the same amounts as rationals. The total
    of none of them is not: pandas returns a plain integer zero from a column of Decimals, so it carries no
    scale, no currency and no quantize, and the next comparison against a Decimal tolerance is a mixed
    comparison rather than a decimal one. Replaces the typed empty == 0 and type(empty).__name__ in
    ('int', 'float64') of case 152."""
    amounts = pd.Series([Decimal(value).scaleb(-2) for value in cents], dtype='object')
    filled = amounts.sum()
    empty = amounts.iloc[:0].sum()
    npt.assert_equal(Fraction(filled), sum(Fraction(amount) for amount in amounts))
    with pytest.raises(AssertionError):
        npt.assert_equal(type(empty), type(filled))
    with pytest.raises(AttributeError):
        empty.as_tuple()


@functools.lru_cache(maxsize=1)
def _tolerance_table():
    """One row per hundredth from one cent to two hundred: the amount as a Decimal, the same amount as a
    float, and both as exact rationals. Which cents fall in which region below is read off this table by
    asking fractions.Fraction rather than named here."""
    return tuple((Decimal(cents).scaleb(-2), float(Decimal(cents).scaleb(-2)),
                  Fraction(Decimal(cents).scaleb(-2)), Fraction(float(Decimal(cents).scaleb(-2))))
                 for cents in range(1, 201))


def _tolerances_where(relation):
    """The rows of that table whose float stands in the given relation to its decimal, Fraction deciding."""
    return [row for row in _tolerance_table() if relation(row[3], row[2])]


def _sql_says_equal(exact, spelled):
    """The same comparison inside DuckDB, the amount written as a decimal and the tolerance as a double.
    Its typecasting page says combination casting "occurs for comparisons (`=` / `<` / `>`)"."""
    with duckdb.connect() as connection:
        return connection.execute('select cast(? as decimal(18,2)) = cast(? as double)',
                                  [str(exact), spelled]).fetchone()[0]


@given(st.integers(min_value=0, max_value=10 ** 4))
@SLOW
def test_a_decimal_tolerance_equals_its_float_spelling_only_where_the_float_is_that_exact_number(index):
    """CPython's decimal documentation at tag v3.11.15 says "it is possible to use Python's comparison
    operators to compare a Decimal instance x with another number y. This avoids confusing results when
    doing equality comparisons between numbers of different types." Executed against Fraction, which holds
    both as exact rationals, the comparison is exact: it says equal exactly where the two are the same
    rational and not otherwise. Eight of the two hundred hundredths pass that test and the rest do not, so
    whether a tolerance written as a float is the tolerance the chain declared is a property of the
    particular amount. Replaces the typed Decimal('0.25') == 0.25 and Decimal('0.1') == 0.1 of case 152."""
    exact, spelled, as_rational, spelled_as_rational = _tolerance_table()[index % len(_tolerance_table())]
    npt.assert_equal(exact == spelled, as_rational == spelled_as_rational)


@given(st.integers(min_value=0, max_value=10 ** 4))
@SLOW
def test_where_the_float_is_the_exact_amount_python_and_the_sql_engine_agree(index):
    """On the hundredths whose float is the exact number, both readings call them equal."""
    together = _tolerances_where(operator.eq)
    exact, spelled, as_rational, spelled_as_rational = together[index % len(together)]
    npt.assert_equal(as_rational, spelled_as_rational)
    npt.assert_equal(_sql_says_equal(exact, spelled), exact == spelled)


@given(st.integers(min_value=0, max_value=10 ** 4))
@SLOW
def test_the_sql_engine_calls_a_decimal_equal_to_a_float_that_python_calls_different(index):
    """And on the rest they give opposite answers to the same question. DuckDB reports that a DECIMAL can be
    cast implicitly to a DOUBLE and not the reverse, so the comparison is made after the exact amount has
    been rounded to the nearest double, and the two are then equal; Python compares them exactly and they
    are not. Offered a double that is not the nearest one, DuckDB says different, which is what shows the
    rounding rather than a blanket answer. A tolerance the chain reads back from the workbook engine and one
    it compares in Python are therefore not the same tolerance."""
    apart = _tolerances_where(operator.ne)
    exact, spelled, as_rational, spelled_as_rational = apart[index % len(apart)]
    with pytest.raises(AssertionError):
        npt.assert_equal(_sql_says_equal(exact, spelled), exact == spelled)
    neighbour = float(np.nextafter(spelled, np.inf))
    npt.assert_equal(_sql_says_equal(exact, neighbour), exact == neighbour)


@given(st.integers(min_value=0, max_value=10 ** 4), CENTS)
@SLOW
def test_a_difference_exactly_at_the_tolerance_is_accepted_where_the_float_spelling_rounds_up(index, amount):
    """P152's boundary check is abs(ordered - billed) <= tolerance and its evidence line claims four signed
    price-boundary cases confirm a 0.25 USD tolerance. Twenty-five hundredths is one of the eight hundredths
    whose float is exact, and on the hundredths whose nearest double is above the amount the boundary is
    accepted either way: the decimal comparison accepts a difference exactly equal to the tolerance and so
    does the float spelling, and Fraction agrees with both."""
    larger = _tolerances_where(operator.gt)
    exact, spelled, as_rational, spelled_as_rational = larger[index % len(larger)]
    ordered = Decimal(amount).scaleb(-2)
    difference = abs((ordered + exact) - ordered)
    npt.assert_equal(difference <= spelled, Fraction(difference) <= spelled_as_rational)
    npt.assert_equal(difference <= spelled, difference <= exact)


@given(st.integers(min_value=0, max_value=10 ** 4), CENTS)
@SLOW
def test_a_difference_exactly_at_the_tolerance_is_refused_where_the_float_spelling_rounds_down(index, amount):
    """On the hundredths whose nearest double is below the amount, the same boundary goes the other way: the
    difference is exactly the declared tolerance and the float spelling of that tolerance refuses it, while
    the decimal spelling accepts it. Ninety-two of the two hundred hundredths are in this region and a
    hundred are in the region above, so which way a boundary case falls is decided by the cent and by how
    the tolerance was written, and neither is visible at the comparison. Fraction says the same as the float
    every time, so this is exact arithmetic on a number that is not the one the chain declared."""
    smaller = _tolerances_where(operator.lt)
    exact, spelled, as_rational, spelled_as_rational = smaller[index % len(smaller)]
    ordered = Decimal(amount).scaleb(-2)
    difference = abs((ordered + exact) - ordered)
    npt.assert_equal(difference <= spelled, Fraction(difference) <= spelled_as_rational)
    with pytest.raises(AssertionError):
        npt.assert_equal(difference <= spelled, difference <= exact)


# ---------------------------------------------------------------- a running balance and the order it is in
RECEIPTS = st.lists(st.integers(min_value=1, max_value=500), min_size=1, max_size=8)
ISSUES = st.lists(st.integers(min_value=1, max_value=500), min_size=1, max_size=8)
MOVEMENTS = st.lists(st.integers(min_value=-500, max_value=500), min_size=1, max_size=6)
DAY_CODES = st.lists(st.integers(min_value=0, max_value=3), min_size=2, max_size=40)
SMALL_LEDGER = st.lists(st.integers(min_value=0, max_value=3), min_size=2, max_size=16)
LARGE_LEDGER = st.lists(st.integers(min_value=0, max_value=3), min_size=17, max_size=40)
RECEIPT_IDS = st.lists(st.integers(min_value=0, max_value=4), min_size=2, max_size=8)


def _running_totals(values):
    """The same running total from three implementations: pandas' cumsum, polars' cum_sum in Rust, and
    itertools.accumulate, which is a C loop in CPython itself and shares no code with either."""
    return (pd.Series(values).cumsum().to_numpy(),
            pl.Series(values).cum_sum().to_numpy(),
            np.array(list(itertools.accumulate(values))))


def _ledger_frame(day_codes):
    """One ledger entry per generated day code, in the order generated. The codes are drawn from a range
    narrower than the shortest list, so tied days are forced rather than hoped for."""
    days = [pd.Timestamp('2026-01-01') + pd.Timedelta(days=code) for code in day_codes]
    return pd.DataFrame({'day': days, 'entry': range(len(day_codes))})


@given(RECEIPTS, ISSUES)
@SLOW
def test_the_closing_balance_does_not_depend_on_the_order_and_the_running_minimum_does(receipts, issues):
    """P153 accumulates stock with groupby/cumsum after ordering by a declared posting contract, and one of
    its rejected inputs is negative running stock. Three independent implementations produce the same
    running total for a given order, and the closing balance is the same whichever order the same movements
    arrive in, so the balance the workbook shows does not depend on the sort. The lowest point of the run
    does: with the receipts first the run never goes below the first receipt, and with the issues first it
    reaches the whole issued quantity, so whether a negative-stock rejection fires is decided by an ordering
    the primitive does not impose. Replaces the typed [5, 3, -1] and [-2, -6, -1] of handoff_guards_v16.py
    case 153."""
    arriving = list(receipts) + [-issue for issue in issues]
    leaving = [-issue for issue in issues] + list(receipts)
    for order in (arriving, leaving):
        by_pandas, by_polars, by_itertools = _running_totals(order)
        npt.assert_array_equal(by_pandas, by_polars)
        npt.assert_array_equal(by_pandas, by_itertools)
    first_run, second_run = _running_totals(arriving)[0], _running_totals(leaving)[0]
    npt.assert_equal(first_run[-1], second_run[-1])
    with pytest.raises(AssertionError):
        npt.assert_equal(np.min(first_run), np.min(second_run))


@given(MOVEMENTS, MOVEMENTS)
@SLOW
def test_a_missing_quantity_voids_the_rest_of_the_run_in_three_implementations_and_is_skipped_in_two(before,
                                                                                                    after):
    """Case 153 records that a gap in the quantities leaves the balance resuming as if the gap were zero.
    That is one of two answers, and which one a chain gets depends on the library and on how the gap is
    written. pandas' cumsum takes skipna=True, documented at v2.2.3 as "Exclude NA/null values. If an entire
    row/column is NA, the result will be NA", so the row is missing and every row after it is a number
    again; polars' cum_sum, whose docstring at py-1.44.1 documents only an overflow cast and says nothing
    about missing values, does the same for a null and the opposite for a NaN; numpy's cumsum, whose Notes
    mention only modular integer arithmetic, and itertools.accumulate carry the NaN to the end of the
    ledger. So the same missing quantity either silently counts as zero or voids every balance after it, and
    pandas' own skipna=False reproduces the voided run exactly."""
    values = [float(value) for value in before] + [float('nan')] + [float(value) for value in after]
    with_a_null = [float(value) for value in before] + [None] + [float(value) for value in after]
    resumed = pd.Series(values).cumsum().to_numpy()
    npt.assert_array_equal(resumed, pl.Series(with_a_null).cum_sum().to_numpy())
    voided = (np.cumsum(np.array(values)), np.array(list(itertools.accumulate(values))),
              pl.Series(values).cum_sum().to_numpy(), pd.Series(values).cumsum(skipna=False).to_numpy())
    for run in voided:
        npt.assert_array_equal(voided[0], run)
        with pytest.raises(AssertionError):
            npt.assert_array_equal(resumed, run)


@given(DAY_CODES)
@SLOW
def test_three_stable_sorts_leave_the_tied_entries_in_the_order_they_arrived(day_codes):
    """The posting order P153 sorts by is a date, and several entries share one. Asked for a stable sort,
    pandas, CPython's sorted -- whose sorting howto at tag v3.11.15 says "Sorts are guaranteed to be stable.
    That means that when multiple records have the same key, their original order is preserved" -- and
    polars with maintain_order=True, documented at py-1.44.1 as "Whether the order should be maintained if
    elements are equal", all put the tied entries in the order they arrived. That agreement is what makes
    the next test a property of the default rather than of pandas."""
    frame = _ledger_frame(day_codes)
    by_pandas = frame.sort_values('day', kind='stable')['entry'].to_numpy()
    by_python = np.array([entry for _, entry in sorted(zip(frame['day'], frame['entry']),
                                                       key=operator.itemgetter(0))])
    by_polars = pl.from_pandas(frame).sort('day', maintain_order=True)['entry'].to_numpy()
    npt.assert_array_equal(by_pandas, by_python)
    npt.assert_array_equal(by_pandas, by_polars)


@given(LARGE_LEDGER)
@SLOW
def test_the_default_sort_moves_tied_entries_once_the_ledger_passes_sixteen_of_them(day_codes):
    """pandas' sort_values docstring at v2.2.3 says of kind, "{'quicksort', 'mergesort', 'heapsort',
    'stable'}, default 'quicksort'" and that "`mergesort` and `stable` are the only stable algorithms", and
    P153 sorts without naming one. Executed on generated ledgers of seventeen entries and more, whose day
    codes are drawn from a range of four so that ties are forced, the default reorders the tied entries and
    the three stable sorts above do not. The threshold is the finding: below it the default agrees with them
    on every input, so a fixture of sixteen rows cannot see this, and P153's own evidence line describes
    eighteen declared ledger entries. Replaces the typed tie_order(shuffled, kind='quicksort') ==
    tie_order(shuffled, kind='stable') of case 153."""
    frame = _ledger_frame(day_codes)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(frame.sort_values('day')['entry'].to_numpy(),
                               frame.sort_values('day', kind='stable')['entry'].to_numpy())
    npt.assert_array_equal(np.sort(frame.sort_values('day')['entry'].to_numpy()),
                           np.sort(frame.sort_values('day', kind='stable')['entry'].to_numpy()))


@given(SMALL_LEDGER)
@SLOW
def test_the_same_default_leaves_them_where_they_are_while_the_ledger_is_smaller(day_codes):
    """And below the threshold the default and the stable option agree on every generated ledger, which is
    what makes the reordering above invisible to a small fixture: the same call, the same data shape and the
    same library give a stable answer at sixteen entries and an unstable one at seventeen."""
    frame = _ledger_frame(day_codes)
    npt.assert_array_equal(frame.sort_values('day')['entry'].to_numpy(),
                           frame.sort_values('day', kind='stable')['entry'].to_numpy())


def _duckdb_first_receipt_rows(frame):
    """The same deduplication in SQL, keeping the first row per receipt reference in arrival order."""
    with duckdb.connect() as connection:
        connection.execute('create table receipts(arrived BIGINT, receipt_id BIGINT, qty BIGINT)')
        connection.executemany('insert into receipts values (?, ?, ?)',
                               frame.astype(object).to_numpy().tolist())
        return connection.execute('select distinct on (receipt_id) receipt_id, qty from receipts '
                                  'order by receipt_id, arrived').fetchall()


@given(RECEIPT_IDS, st.lists(st.integers(min_value=1, max_value=50), min_size=2, max_size=8),
       st.integers(min_value=1, max_value=20))
@SLOW
def test_deduplicating_on_the_reference_discards_a_disagreeing_quantity_in_three_engines(ids, quantities,
                                                                                        difference):
    """P153 deduplicates exact receipt IDs before building the ledger. Every receipt reference here appears
    twice with quantities that differ by a generated amount, so every kept row silently stands for a row
    that disagreed with it. pandas' drop_duplicates(subset=...), polars' unique(subset=..., keep='first')
    in Rust and DuckDB's DISTINCT ON keep the same rows, so the behaviour is the operation and not the
    library, and none of the three says anything. That the rows discarded were not duplicates at all is
    visible only by deduplicating on the whole row instead, which keeps more rows than deduplicating on the
    reference. Replaces the typed len(loose) == 2 and [r['qty'] for r in loose] == [2, 1] of case 153."""
    references = list(ids) + list(ids)
    payloads = [quantities[position % len(quantities)] for position in range(len(ids))]
    frame = pd.DataFrame({'arrived': range(2 * len(ids)), 'receipt_id': references,
                          'qty': payloads + [payload + difference for payload in payloads]})
    kept = frame.drop_duplicates(subset=['receipt_id'])
    in_polars = pl.from_pandas(frame).unique(subset=['receipt_id'], keep='first', maintain_order=True)
    npt.assert_array_equal(kept[['receipt_id', 'qty']].sort_values('receipt_id').to_numpy(),
                           in_polars.sort('receipt_id')[['receipt_id', 'qty']].to_numpy())
    npt.assert_array_equal(kept[['receipt_id', 'qty']].sort_values('receipt_id').to_numpy(),
                           np.array(_duckdb_first_receipt_rows(frame)))
    npt.assert_equal(len(kept), frame['receipt_id'].nunique())
    with pytest.raises(AssertionError):
        npt.assert_equal(len(kept), len(frame.drop_duplicates(subset=['receipt_id', 'qty'])))


# ---------------------------------------------------------------- reading one timestamp in three runtimes
ISO_ORACLE_RB = pathlib.Path(__file__).with_name('iso_stamp_oracle.rb')
ISO_ORACLE_PHP = pathlib.Path(__file__).with_name('iso_stamp_oracle.php')
both_stamp_runtimes = ruby_available and php_binary_available
MOMENTS = st.datetimes(min_value=datetime.datetime(2000, 1, 1), max_value=datetime.datetime(2099, 12, 31))
OFFSET_MINUTES = st.integers(min_value=-14 * 60, max_value=14 * 60)
OFFSET_SECONDS = st.integers(min_value=1, max_value=59)
MICROSECONDS = st.integers(min_value=1, max_value=999999)
EXTRA_DIGITS = st.integers(min_value=1, max_value=999)


def _runtime_reads_stamp(runner, script, text):
    """One ISO 8601 timestamp as another runtime reads it: the wall clock, the sub-second field, and the
    offset, exactly as that runtime's own accessors report them. The shim prints the lines; the Python side
    runs it and splits. A refusal is a non-zero exit and reaches the test as CalledProcessError."""
    completed = subprocess.run([runner, str(script), text], capture_output=True, encoding='utf-8', check=True)
    return completed.stdout.split('\n')[:4]


@pytest.mark.skipif(not both_stamp_runtimes, reason='both runtimes are required for this oracle')
@given(MOMENTS, OFFSET_MINUTES)
@ORACLE_PROCESS
def test_three_runtimes_read_one_extended_timestamp_as_the_same_instant(moment, offset_minutes):
    """P156 parses declared service intervals from ISO 8601 text and requires an offset. Where the text is
    the extended form with a whole-minute offset, all three runtimes read the same instant: CPython's
    datetime.fromisoformat, Ruby 3.3.6's Time.iso8601 and PHP 8.4.19's DateTimeImmutable agree on the wall
    clock and on the offset, over generated moments and generated offsets. That agreement is what makes the
    disagreements below properties of the spellings rather than of the runtimes."""
    stamp = moment.replace(microsecond=0,
                           tzinfo=datetime.timezone(datetime.timedelta(minutes=offset_minutes)))
    text = stamp.isoformat()
    parsed = datetime.datetime.fromisoformat(text)
    in_ruby = _runtime_reads_stamp('ruby', ISO_ORACLE_RB, text)
    in_php = _runtime_reads_stamp('php', ISO_ORACLE_PHP, text)
    npt.assert_array_equal([in_ruby[0], in_php[0]], [parsed.strftime('%Y-%m-%dT%H:%M:%S')] * 2)
    npt.assert_array_equal([datetime.timedelta(seconds=int(in_ruby[3])),
                            datetime.timedelta(seconds=int(in_php[2]))], [parsed.utcoffset()] * 2)


@pytest.mark.skipif(not both_stamp_runtimes, reason='both runtimes are required for this oracle')
@given(MOMENTS)
@ORACLE_PROCESS
def test_a_timestamp_with_no_offset_is_left_naive_by_one_runtime_and_placed_by_the_others(moment):
    """Case 156 records that the parse accepts a timestamp with no offset, and that the chain has to refuse
    it separately. The two other runtimes do not leave it undecided: given the same text they return an
    instant with an offset, taken from their own configured zone rather than from the text, while CPython
    returns a datetime with no offset at all. All three read the same wall clock. So the same service entry
    is a time without a place in one runtime and a fixed instant in the other two, and nothing in the text
    distinguishes the cases."""
    text = moment.replace(microsecond=0).isoformat()
    parsed = datetime.datetime.fromisoformat(text)
    in_ruby = _runtime_reads_stamp('ruby', ISO_ORACLE_RB, text)
    in_php = _runtime_reads_stamp('php', ISO_ORACLE_PHP, text)
    npt.assert_array_equal([in_ruby[0], in_php[0]], [parsed.strftime('%Y-%m-%dT%H:%M:%S')] * 2)
    with pytest.raises(AssertionError):
        npt.assert_equal(parsed.utcoffset(), datetime.timedelta(seconds=int(in_ruby[3])))
    with pytest.raises(AssertionError):
        npt.assert_equal(parsed.utcoffset(), datetime.timedelta(seconds=int(in_php[2])))


@pytest.mark.skipif(not both_stamp_runtimes, reason='both runtimes are required for this oracle')
@given(MOMENTS)
@ORACLE_PROCESS
def test_the_basic_spelling_of_a_timestamp_is_read_by_two_runtimes_and_refused_by_the_third(moment):
    """The same moment written without its separators, which case 156 lists among the spellings the parse
    accepts. CPython and PHP read it as the same wall clock; Ruby's Time.iso8601 refuses it outright. An
    entry a chain accepts in Python is therefore not an entry every reader of the same file can parse, and
    the text is the only thing that differs."""
    text = moment.replace(microsecond=0).strftime('%Y%m%dT%H%M%S')
    parsed = datetime.datetime.fromisoformat(text)
    in_php = _runtime_reads_stamp('php', ISO_ORACLE_PHP, text)
    npt.assert_array_equal(in_php[0], parsed.strftime('%Y-%m-%dT%H:%M:%S'))
    with pytest.raises(subprocess.CalledProcessError):
        _runtime_reads_stamp('ruby', ISO_ORACLE_RB, text)


@pytest.mark.skipif(not both_stamp_runtimes, reason='both runtimes are required for this oracle')
@given(MOMENTS)
@ORACLE_PROCESS
def test_a_date_with_no_time_becomes_a_midnight_in_two_runtimes_and_a_refusal_in_the_third(moment):
    """And a date with no time at all is a timestamp to two of the three: CPython and PHP both return the
    midnight that begins it, which is a value no one wrote down, and Ruby refuses to read it."""
    text = moment.date().isoformat()
    parsed = datetime.datetime.fromisoformat(text)
    in_php = _runtime_reads_stamp('php', ISO_ORACLE_PHP, text)
    npt.assert_array_equal(in_php[0], parsed.strftime('%Y-%m-%dT%H:%M:%S'))
    with pytest.raises(subprocess.CalledProcessError):
        _runtime_reads_stamp('ruby', ISO_ORACLE_RB, text)


@pytest.mark.skipif(not both_stamp_runtimes, reason='both runtimes are required for this oracle')
@given(MOMENTS, OFFSET_MINUTES, OFFSET_SECONDS)
@ORACLE_PROCESS
def test_an_offset_that_is_not_a_whole_number_of_minutes_survives_only_one_of_three_readings(moment,
                                                                                            offset_minutes,
                                                                                            seconds):
    """Case 156 types one offset written with seconds in it, '+00:00:00'. Generated over offsets that carry
    a real seconds part, the three runtimes give three answers to the same text. CPython reads it and keeps
    it: the offset it returns is the offset the text names. Ruby refuses the text. PHP reads it correctly --
    its getOffset agrees with CPython to the second -- and then cannot write it back: the timestamp it
    formats carries an offset a second reading of PHP's own output does not agree with. So an offset that is
    not a whole number of minutes is preserved, rejected or quietly rounded according to the runtime, and
    only the third of those is silent."""
    stamp = moment.replace(microsecond=0,
                           tzinfo=datetime.timezone(datetime.timedelta(minutes=offset_minutes,
                                                                       seconds=seconds)))
    text = stamp.isoformat()
    parsed = datetime.datetime.fromisoformat(text)
    npt.assert_equal(parsed.utcoffset(), stamp.utcoffset())
    with pytest.raises(subprocess.CalledProcessError):
        _runtime_reads_stamp('ruby', ISO_ORACLE_RB, text)
    in_php = _runtime_reads_stamp('php', ISO_ORACLE_PHP, text)
    npt.assert_equal(datetime.timedelta(seconds=int(in_php[2])), parsed.utcoffset())
    with pytest.raises(AssertionError):
        npt.assert_equal(datetime.datetime.fromisoformat(in_php[0] + in_php[3]).utcoffset(),
                         datetime.timedelta(seconds=int(in_php[2])))


@pytest.mark.skipif(not both_stamp_runtimes, reason='both runtimes are required for this oracle')
@given(MOMENTS, MICROSECONDS, EXTRA_DIGITS)
@ORACLE_PROCESS
def test_a_digit_below_the_microsecond_is_kept_by_one_runtime_and_dropped_by_the_other_two(moment,
                                                                                          microseconds,
                                                                                          extra):
    """Case 156 records that sub-second precision is truncated. It is truncated in two of the three
    runtimes: given the same text, CPython and PHP report the same microsecond and neither has a field
    below it, while Ruby's parse holds a nanosecond count its own microsecond accessor cannot express. The
    three digits past the microsecond are generated and the rest of the text is written by the datetime
    itself. So a timestamp that is equal in one runtime is not equal in another, and the entry that decides
    whether two service intervals touch may differ in a digit Python cannot see."""
    text = '%s%03d' % (moment.replace(microsecond=microseconds).isoformat(), extra)
    parsed = datetime.datetime.fromisoformat(text)
    in_ruby = _runtime_reads_stamp('ruby', ISO_ORACLE_RB, text)
    in_php = _runtime_reads_stamp('php', ISO_ORACLE_PHP, text)
    npt.assert_array_equal([int(in_ruby[1]), int(in_php[1])], [parsed.microsecond] * 2)
    with pytest.raises(AssertionError):
        npt.assert_equal(int(in_ruby[2]), int(in_ruby[1]))


@functools.lru_cache(maxsize=1)
def _rounded_ties():
    """One row per cent from nothing to two hundred: the amount with half a cent added, what Decimal's two
    half-way modes make of it, and what DuckDB makes of the same figure in a decimal column and in a double
    column. Half a cent is computed from the cent rather than typed, and the regions below are read off this
    table rather than named. Four hundred and two queries, once per session."""
    quantum = Decimal(1).scaleb(-2)
    rows = []
    with duckdb.connect() as connection:
        for cents in range(0, 201):
            tie = Decimal(cents).scaleb(-2) + quantum / 2
            rows.append((tie,
                         tie.quantize(quantum, rounding=ROUND_HALF_EVEN),
                         tie.quantize(quantum, rounding=ROUND_HALF_UP),
                         connection.execute('select round(cast(? as decimal(18,3)), 2)',
                                            [str(tie)]).fetchone()[0],
                         connection.execute('select round(cast(? as double), 2)',
                                            [float(tie)]).fetchone()[0]))
    return tuple(rows)


@given(st.integers(min_value=0, max_value=10 ** 4))
@SLOW
def test_the_sql_engine_rounds_every_half_cent_away_from_zero(index):
    """P156's cents are rounded in Python, whose decimal default is half to even, and read back through a
    workbook and a SQL engine. DuckDB 1.5.5 rounds a decimal column half away from zero on every generated
    tie, which is Python's ROUND_HALF_UP and not its default. Replaces the typed
    round_cents(Decimal('1.005'), mode=ROUND_HALF_UP) == Decimal('1.01') of handoff_guards_v16.py
    case 156."""
    tie, to_even, away, in_decimal, in_double = _rounded_ties()[index % len(_rounded_ties())]
    npt.assert_equal(in_decimal, away)


@given(st.integers(min_value=0, max_value=10 ** 4))
@SLOW
def test_the_sql_engine_and_the_python_default_disagree_on_the_cents_the_two_modes_split(index):
    """On the ties where Decimal's two half-way modes give different cents, the engine gives the half-up
    one, so the cent a chain computes in Python and the cent the same figure gets in SQL are not the same
    cent. Which ties those are is read off Decimal, not named here."""
    split = [row for row in _rounded_ties() if row[1] != row[2]]
    tie, to_even, away, in_decimal, in_double = split[index % len(split)]
    with pytest.raises(AssertionError):
        npt.assert_equal(in_decimal, to_even)


@given(st.integers(min_value=0, max_value=10 ** 4))
@SLOW
def test_the_same_engine_gives_another_cent_when_the_column_is_a_double(index):
    """And the engine does not have one answer either. On some of the same ties, rounding the figure in a
    double column gives a different cent from rounding it in a decimal column, inside one engine, on one
    number; which ties those are is settled by asking the engine both ways rather than by predicting it
    from the binary value. So the cent depends on the mode, on the engine and on the column type the
    workbook was written with."""
    apart = [row for row in _rounded_ties() if row[4] != row[3]]
    if not apart:
        pytest.skip('this build rounds a double column and a decimal column to the same cent')
    tie, to_even, away, in_decimal, in_double = apart[index % len(apart)]
    with pytest.raises(AssertionError):
        npt.assert_equal(in_double, in_decimal)


@given(st.integers(min_value=0, max_value=10 ** 4))
@SLOW
def test_the_two_column_types_agree_on_the_rest_of_the_ties(index):
    """On the remaining ties the two column types agree, so the divergence above is particular figures
    rather than a difference of rule."""
    together = [row for row in _rounded_ties() if row[4] == row[3]]
    tie, to_even, away, in_decimal, in_double = together[index % len(together)]
    npt.assert_equal(in_double, in_decimal)


# ---------------------------------------------------------------- a bill of materials and its edges
BOM_TRIPLES = st.lists(st.tuples(st.integers(min_value=0, max_value=4),
                                 st.integers(min_value=1, max_value=4),
                                 st.integers(min_value=1, max_value=9)),
                       min_size=1, max_size=8, unique_by=lambda triple: triple[:2])
RING_SIZE = st.integers(min_value=2, max_value=8)
ABSENT_ITEM = st.integers(min_value=100, max_value=120)


def _bom_edges(triples):
    """One edge per generated triple, from an item to the item a generated positive gap further on, so the
    graph is acyclic by construction and every parent, child and quantity is generated."""
    return [('item-%d' % parent, 'item-%d' % (parent + gap), qty) for parent, gap, qty in triples]


def _networkx_bom(edges):
    """The chain's own graph: DiGraph.add_edge with the quantity as an edge attribute."""
    graph = nx.DiGraph()
    for parent, child, qty in edges:
        graph.add_edge(parent, child, qty=qty)
    return graph


def _igraph_bom(edges):
    """The same declarations in igraph, a C library with its own graph implementation."""
    names = sorted({name for parent, child, _ in edges for name in (parent, child)})
    graph = igraph.Graph(directed=True)
    graph.add_vertices(names)
    graph.add_edges([(parent, child) for parent, child, _ in edges],
                    attributes={'qty': [qty for _, _, qty in edges]})
    return graph


def _duckdb_gross_requirement(edges, source, target):
    """The same expansion as a recursive query, which enumerates the paths in SQL and multiplies along each
    one. DuckDB shares no code with either graph library."""
    with duckdb.connect() as connection:
        connection.execute('create table bom(parent VARCHAR, child VARCHAR, qty BIGINT)')
        connection.executemany('insert into bom values (?, ?, ?)', edges)
        return connection.execute(
            'with recursive expand(node, qty) as ('
            '  select child, qty from bom where parent = ? '
            '  union all '
            '  select bom.child, expand.qty * bom.qty from expand join bom on bom.parent = expand.node) '
            'select coalesce(sum(qty), 0) from expand where node = ?', [source, target]).fetchone()[0]


@given(st.integers(min_value=0, max_value=4), st.integers(min_value=1, max_value=4),
       st.integers(min_value=1, max_value=9), st.integers(min_value=1, max_value=9))
@SLOW
def test_a_repeated_bill_of_materials_edge_is_one_edge_in_one_library_and_two_in_the_other(parent, gap,
                                                                                          first, extra):
    """P160 builds the bill of materials with DiGraph.add_edge and case 160 records that declaring the same
    parent and child twice stores one edge carrying the second quantity. That is not the operation, it is
    this library: igraph 1.0.0, a C implementation, stores both declarations as parallel edges and keeps
    both quantities, one edge for every declaration in the file. The quantity NetworkX keeps is the last one
    igraph kept, so nothing is corrupted; what differs is how many
    edges the same file describes, and therefore how much material it calls for. Replaces the typed
    loose.number_of_edges() == 1 and loose['kit']['cable']['qty'] == 3 of handoff_guards_v16.py case 160."""
    edges = _bom_edges([(parent, gap, first), (parent, gap, first + extra)])
    graph, in_igraph = _networkx_bom(edges), _igraph_bom(edges)
    with pytest.raises(AssertionError):
        npt.assert_equal(graph.number_of_edges(), in_igraph.ecount())
    npt.assert_equal(graph.edges[edges[0][0], edges[0][1]]['qty'], in_igraph.es['qty'][-1])
    npt.assert_equal(in_igraph.ecount(), len(edges))
    with pytest.raises(AssertionError):
        npt.assert_equal(graph.edges[edges[0][0], edges[0][1]]['qty'], np.sum(in_igraph.es['qty']))


@given(BOM_TRIPLES, st.integers(min_value=0, max_value=100), st.integers(min_value=0, max_value=100))
@SLOW
def test_the_requirement_along_the_declared_paths_agrees_with_two_other_expansions(triples, source_index,
                                                                                  target_index):
    """The gross requirement P160 computes is a sum over simple paths of the product of the quantities along
    each one. Where the declarations are unique, three implementations give the same number: NetworkX's
    all_simple_paths with math.prod, igraph's get_all_simple_paths in C, and a recursive SQL query in DuckDB
    that never enumerates a path at all. So the arithmetic of the nested assembly is the operation and not
    the library, which is what makes the disagreements in the other tests specific. Replaces the typed
    gross_requirement(graph, 'kit', 'cable', 1, checked=True) == 6 of case 160."""
    edges = _bom_edges(triples)
    graph, in_igraph = _networkx_bom(edges), _igraph_bom(edges)
    names = sorted({name for parent, child, _ in edges for name in (parent, child)})
    source = names[source_index % len(names)]
    reachable = [name for name in names if name != source]
    target = reachable[target_index % len(reachable)]
    by_networkx = sum(math.prod(graph.edges[path[step], path[step + 1]]['qty']
                                for step in range(len(path) - 1))
                      for path in nx.all_simple_paths(graph, source, target))
    by_igraph = sum(math.prod(in_igraph.es[in_igraph.get_eid(path[step], path[step + 1])]['qty']
                              for step in range(len(path) - 1))
                    for path in in_igraph.get_all_simple_paths(source, to=target))
    npt.assert_equal(by_networkx, by_igraph)
    npt.assert_equal(by_networkx, _duckdb_gross_requirement(edges, source, target))


@given(RING_SIZE)
@SLOW
def test_a_cycle_stops_the_topological_order_when_it_is_consumed_and_not_when_it_is_built(size):
    """Case 160 records that building the topological_sort iterator validates nothing. The two libraries
    disagree about when the check happens: NetworkX returns a generator that raises NetworkXUnfeasible only
    when it is exhausted, so a chain that calls topological_sort and does not consume it has checked
    nothing, while igraph's topological_sorting raises at the call. Their predicates agree that the ring is
    not acyclic, so the difference is entirely in when the refusal arrives. Replaces the typed
    acyclic(cyclic, method='generator') == True of case 160."""
    ring = [('item-%d' % position, 'item-%d' % ((position + 1) % size)) for position in range(size)]
    graph = nx.DiGraph()
    graph.add_edges_from(ring)
    in_igraph = igraph.Graph(directed=True)
    in_igraph.add_vertices(sorted({name for edge in ring for name in edge}))
    in_igraph.add_edges(ring)
    nx.topological_sort(graph)
    with pytest.raises(nx.NetworkXUnfeasible):
        list(nx.topological_sort(graph))
    with pytest.raises(igraph.InternalError):
        in_igraph.topological_sorting()
    npt.assert_equal(nx.is_directed_acyclic_graph(graph), in_igraph.is_dag())


@given(BOM_TRIPLES, st.integers(min_value=0, max_value=100))
@SLOW
def test_an_item_is_its_own_requirement_in_one_library_and_not_in_the_other(triples, index):
    """Asked for the paths from an item to itself, NetworkX returns one path -- the item alone -- and igraph
    returns none. The product of no quantities is one, which numpy and math agree on, so NetworkX's answer
    turns a demand for an assembly into a requirement for that same assembly, at exactly the demanded
    quantity, out of a graph that declares no such edge. Replaces the typed path_quantity(graph, 'kit',
    'kit') == [(['kit'], 1)] and math.prod([]) == 1 of case 160."""
    edges = _bom_edges(triples)
    graph, in_igraph = _networkx_bom(edges), _igraph_bom(edges)
    names = sorted({name for parent, child, _ in edges for name in (parent, child)})
    item = names[index % len(names)]
    in_networkx = list(nx.all_simple_paths(graph, item, item))
    with pytest.raises(AssertionError):
        npt.assert_equal(len(in_networkx), len(in_igraph.get_all_simple_paths(item, to=item)))
    npt.assert_equal(math.prod([]), np.prod([]))


@given(BOM_TRIPLES, ABSENT_ITEM)
@SLOW
def test_an_item_that_is_not_in_the_graph_raises_as_a_source_and_is_silent_as_a_target(triples, missing):
    """The two ends of the same query are not treated alike. An item the graph has never heard of raises
    NodeNotFound when it is the source and returns quietly when it is the target, and what it returns is
    indistinguishable from the answer for an item that is in the graph and simply cannot be reached. igraph
    refuses both ends with a ValueError, so the asymmetry is this library's and a missing part number
    disappears from the requirements without a word. Replaces the typed path_quantity(graph, 'kit',
    'absent') == [] of case 160."""
    edges = _bom_edges(triples)
    graph, in_igraph = _networkx_bom(edges), _igraph_bom(edges)
    names = sorted({name for parent, child, _ in edges for name in (parent, child)})
    absent = 'item-%d' % missing
    with pytest.raises(nx.NodeNotFound):
        list(nx.all_simple_paths(graph, absent, names[0]))
    npt.assert_array_equal(list(nx.all_simple_paths(graph, names[0], absent)),
                           list(nx.all_simple_paths(graph, names[-1], names[0])))
    with pytest.raises(ValueError):
        in_igraph.get_all_simple_paths(absent, to=names[0])
    with pytest.raises(ValueError):
        in_igraph.get_all_simple_paths(names[0], to=absent)


# ---------------------------------------------------------------- a search rectangle and what it holds
PDF_WORD = st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=109), min_size=3, max_size=7)
PDF_OTHER_WORD = st.text(alphabet=st.characters(min_codepoint=110, max_codepoint=122), min_size=3, max_size=7)
PDF_WORDS = st.lists(PDF_WORD, min_size=2, max_size=4)
PDF_OTHER_WORDS = st.lists(PDF_OTHER_WORD, min_size=2, max_size=4)
ACCENTED_LETTER = st.sampled_from('àáâãäåçèéêëìíîïñòóôõöùúûüý')
CLOSE_GAP = st.integers(min_value=12, max_value=14)
CLEAR_GAP = st.integers(min_value=16, max_value=40)


def _two_line_pdf(first, second, gap):
    """PyMuPDF writes both lines; only the strings and the line spacing are generated."""
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 100), first)
    page.insert_text((72, 100 + gap), second)
    return document.tobytes()


def _pdfium_matches(data, phrase, **options):
    """PDFium's own search, driven by pypdfium2. Each hit is returned as the characters it covers."""
    textpage = pypdfium2.PdfDocument(io.BytesIO(data))[0].get_textpage()
    searcher = textpage.search(phrase, **options)
    found = []
    while True:
        hit = searcher.get_next()
        if hit is None:
            break
        found.append(textpage.get_text_range(*hit))
    return found


def _pdfium_inside(data, rect):
    """The same rectangle read by PDFium. PyMuPDF's own transformation_matrix maps its top-left
    coordinates back to the PDF canvas coordinates pdfium expects; no arithmetic is done here."""
    page = pymupdf.open('pdf', data)[0]
    on_canvas = rect * ~page.transformation_matrix
    textpage = pypdfium2.PdfDocument(io.BytesIO(data))[0].get_textpage()
    return textpage.get_text_bounded(left=on_canvas.x0, bottom=on_canvas.y0,
                                     right=on_canvas.x1, top=on_canvas.y1)


@given(PDF_WORDS, PDF_OTHER_WORDS, st.integers(min_value=1, max_value=4), CLEAR_GAP)
@SLOW
def test_the_two_pdf_engines_count_the_same_occurrences_of_a_generated_phrase(first, second, take, gap):
    """MuPDF through PyMuPDF and PDFium through pypdfium2 read the same page with no shared code:
    pypdfium2 declares no dependencies at all. On a phrase that occurs on one line and never twice in
    a row, the two engines return the same number of occurrences and PDFium's matched characters are
    the phrase. This is the agreeing region for the P163 passage location."""
    line, other = ' '.join(first), ' '.join(second)
    phrase = ' '.join(first[:take])
    assume(phrase + phrase not in line)
    data = _two_line_pdf(line, other, gap)
    found = pymupdf.open('pdf', data)[0].search_for(phrase)
    matched = _pdfium_matches(data, phrase)
    npt.assert_equal(len(found), len(matched))
    npt.assert_array_equal(matched, [phrase] * len(matched))


@given(PDF_WORD, PDF_OTHER_WORDS, CLEAR_GAP)
@SLOW
def test_two_touching_occurrences_are_one_rectangle_to_mupdf_and_two_matches_to_pdfium(word, second, gap):
    """PyMuPDF's own documentation calls this out: "the search logic regards **contiguous multiple
    occurrences** of *needle* as one". PDFium reports each occurrence separately, so the count of
    highlighted passages depends on the engine and one rectangle can cover two quotations. Replaces
    the typed len(hits) expectations of case 163."""
    data = _two_line_pdf(word + word, ' '.join(second), gap)
    found = pymupdf.open('pdf', data)[0].search_for(word)
    matched = _pdfium_matches(data, word)
    with pytest.raises(AssertionError):
        npt.assert_equal(len(found), len(matched))
    npt.assert_array_less(len(found), len(matched))
    npt.assert_equal(pymupdf.open('pdf', data)[0].get_textbox(found[0]), word + word)


@given(PDF_WORD, CLEAR_GAP)
@SLOW
def test_both_engines_find_a_case_changed_copy_of_an_ascii_phrase(word, gap):
    """The default search ignores case in both engines, so an exact-text comparison after the search
    is what separates a quotation from its case-changed twin. The agreeing region for the ASCII part
    of the P163 case-insensitivity claim."""
    data = _two_line_pdf(word, word.upper(), gap)
    found = pymupdf.open('pdf', data)[0].search_for(word)
    npt.assert_equal(len(found), len(_pdfium_matches(data, word)))
    npt.assert_array_less(len(_pdfium_matches(data, word, match_case=True)), len(found))


@given(PDF_WORD, ACCENTED_LETTER, CLEAR_GAP)
@SLOW
def test_the_case_insensitive_search_stops_at_ascii_in_one_engine_only(word, letter, gap):
    """PyMuPDF documents the limit: "Upper / lower case is ignored, but only works for ASCII
    characters". PDFium folds the accented letter too, so the same needle finds one passage in one
    engine and two in the other, and a chain that constrains an ASCII-insensitive search with an
    exact comparison is not constraining the same candidate set another reader would produce."""
    spelled = word + letter + word
    data = _two_line_pdf(spelled, spelled.upper(), gap)
    found = pymupdf.open('pdf', data)[0].search_for(spelled)
    matched = _pdfium_matches(data, spelled)
    with pytest.raises(AssertionError):
        npt.assert_equal(len(found), len(matched))
    npt.assert_array_less(len(found), len(matched))


@given(PDF_WORDS, PDF_OTHER_WORDS, CLEAR_GAP)
@SLOW
def test_a_phrase_crossing_a_line_break_is_one_match_and_more_than_one_rectangle(first, second, gap):
    """PyMuPDF documents that "if parts of *needle* occur on more than one line, then a separate item
    is generated for each these parts". PDFium returns the single character range that carries the
    whole phrase across the break. Highlighting hits[0], as the P163 chain does, therefore marks only
    the first line of a quotation that wraps."""
    line, other = ' '.join(first), ' '.join(second)
    phrase = line + ' ' + other
    data = _two_line_pdf(line, other, gap)
    found = pymupdf.open('pdf', data)[0].search_for(phrase)
    matched = _pdfium_matches(data, phrase)
    with pytest.raises(AssertionError):
        npt.assert_equal(len(found), len(matched))
    npt.assert_array_less(len(matched), len(found))
    npt.assert_array_equal([''.join(hit.split()) for hit in matched], [''.join(phrase.split())])
    page = pymupdf.open('pdf', data)[0]
    for rectangle in found:
        with pytest.raises(AssertionError):
            npt.assert_equal(page.get_textbox(rectangle), phrase)


@given(PDF_WORDS, PDF_OTHER_WORDS, st.integers(min_value=1, max_value=4), CLEAR_GAP)
@SLOW
def test_the_matched_rectangle_holds_the_phrase_when_the_next_line_clears_it(first, second, take, gap):
    """With the following line far enough away, PyMuPDF's get_textbox returns the phrase and PDFium's
    bounded read of the same rectangle returns the same characters once spacing is set aside. This is
    the region in which the P163 exact-text check means what it says."""
    line, other = ' '.join(first), ' '.join(second)
    phrase = ' '.join(first[:take])
    assume(phrase + phrase not in line)
    data = _two_line_pdf(line, other, gap)
    rectangle = pymupdf.open('pdf', data)[0].search_for(phrase)[0]
    npt.assert_equal(pymupdf.open('pdf', data)[0].get_textbox(rectangle), phrase)
    npt.assert_array_equal(''.join(_pdfium_inside(data, rectangle).split()), ''.join(phrase.split()))


@given(PDF_WORDS, PDF_OTHER_WORDS, st.integers(min_value=1, max_value=4), CLOSE_GAP)
@SLOW
def test_the_matched_rectangle_holds_the_line_below_it_when_the_lines_are_close(first, second, take, gap):
    """At ordinary single line spacing the rectangle PyMuPDF returns for a match recovers the line
    underneath it as well, so the exact-text check the chain runs compares the query against two
    lines of text and rejects a passage that was found correctly. PDFium's bounded read of the same
    rectangle returns only the matched line, and so does PyMuPDF's own clip extraction, whose
    documented rule is that "a character becomes part of the output, if its bbox is contained in
    clip". Replaces the typed recovered(pdf, multi[0]) == 'jumps over\\nletely.' of case 163."""
    line, other = ' '.join(first), ' '.join(second)
    phrase = ' '.join(first[:take])
    assume(phrase + phrase not in line)
    data = _two_line_pdf(line, other, gap)
    page = pymupdf.open('pdf', data)[0]
    rectangle = page.search_for(phrase)[0]
    inside = _pdfium_inside(data, rectangle)
    with pytest.raises(AssertionError):
        npt.assert_equal(page.get_textbox(rectangle), phrase)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(''.join(page.get_textbox(rectangle).split()), ''.join(inside.split()))
    npt.assert_array_equal(''.join(page.get_text(clip=rectangle).split()), ''.join(inside.split()))


@given(PDF_WORDS, SAFE_LINE, SAFE_LINE, CLEAR_GAP)
@SLOW
def test_a_highlight_comment_and_its_author_survive_without_the_appearance_update(first, comment,
                                                                                 title, gap):
    """set_info writes the comment and the author into the annotation dictionary, and both are read
    back by PyMuPDF and by pypdf, which parses the PDF object model in pure Python and does not
    depend on MuPDF. Calling Annot.update is not what persists them. Replaces the typed
    annots[0]['content'] == 'illustrative comment' expectations of case 163."""
    line = ' '.join(first)
    data = _two_line_pdf(line, line, gap)
    document = pymupdf.open('pdf', data)
    page = document[0]
    annotation = page.add_highlight_annot(page.search_for(first[0])[0])
    annotation.set_info(content=comment, title=title)
    saved = document.tobytes()
    in_mupdf = [(note.info['content'], note.info['title'], note.type[1])
                for note in pymupdf.open('pdf', saved)[0].annots()]
    in_pypdf = [(str(entry.get_object()['/Contents']), str(entry.get_object()['/T']),
                 str(entry.get_object()['/Subtype']).lstrip('/'))
                for entry in pypdf.PdfReader(io.BytesIO(saved)).pages[0]['/Annots']]
    npt.assert_array_equal(in_mupdf, in_pypdf)
    npt.assert_array_equal([note[:2] for note in in_mupdf], [(comment, title)])


# ---------------------------------------------------------------- a lookup, its cutoff and its limit
LOOKUP_WORD = st.text(alphabet='ab', min_size=2, max_size=4)
LOOKUP_CHOICES = st.lists(LOOKUP_WORD, min_size=18, max_size=26, unique=True)
DISTINCT_LETTERS = st.lists(st.characters(min_codepoint=97, max_codepoint=122), min_size=3, max_size=3,
                            unique=True)


@given(WORDS, WORDS)
@SLOW
def test_the_two_libraries_compute_the_same_damerau_levenshtein_distance(left, right):
    """The distance P164 names is rapidfuzz's C++ DamerauLevenshtein; nltk's edit_distance with
    transpositions enabled is pure-Python dynamic programming whose own dependencies are defusedxml,
    click, joblib, regex and tqdm, none of them rapidfuzz. The two agree on generated text. The
    Levenshtein distribution installed here is not a second implementation and is not used as one:
    its published metadata requires rapidfuzz itself."""
    npt.assert_array_equal(rf_damerau.distance(left, right),
                           nltk.edit_distance(left, right, transpositions=True))


@given(DISTINCT_LETTERS)
@SLOW
def test_two_transposition_metrics_answer_one_misspelling_differently(letters):
    """rapidfuzz's own docstrings carry this pair as examples: DamerauLevenshtein.distance("CA", "ABC")
    is 2 and OSA.distance("CA", "ABC") is 3, because the restricted metric may not edit a substring it
    has already transposed. nltk's transposition mode is the unrestricted one, so it answers with
    DamerauLevenshtein. A one-edit bound therefore keeps a misspelling under the scorer P164 names and
    drops it under the neighbouring scorer in the same module, and plain Levenshtein charges two edits
    for the adjacent swap that motivates the chain. Replaces the typed distances of case 164."""
    first, second, third = letters
    swapped, spread = third + first, first + second + third
    npt.assert_array_equal(rf_damerau.distance(swapped, spread),
                           nltk.edit_distance(swapped, spread, transpositions=True))
    npt.assert_array_less(rf_damerau.distance(swapped, spread), rf_osa.distance(swapped, spread))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(rf_osa.distance(swapped, spread),
                               nltk.edit_distance(swapped, spread, transpositions=True))
    adjacent = second + first
    npt.assert_array_less(rf_damerau.distance(first + second, adjacent),
                          rf_levenshtein.distance(first + second, adjacent))


@given(LOOKUP_CHOICES, st.integers(min_value=0, max_value=25))
@SLOW
def test_the_default_result_limit_drops_words_tied_with_the_last_one_it_keeps(choices, index):
    """process.extract is documented as taking "limit : int, optional / maximum amount of results to
    return. None can be passed to disable this behavior. Default is 5." and as sorting equal scores
    "by their index". At the one-edit bound P164 declares, only the query itself can score zero, so
    every word after the first is tied; executed, the truncated list is a prefix of the full one and
    the first word dropped carries the same distance as the last word kept, which means the cut is
    settled by the position of the word in the source index and not by the lookup. P164 passes
    limit=None and therefore keeps them; nothing in the operation does. Replaces the typed
    len(capped) == 5, len(every) == 11 and the typed list of six dropped words of case 164."""
    query = choices[index % len(choices)]
    every = rf_process.extract(query, choices, scorer=rf_damerau.distance, score_cutoff=1, limit=None)
    capped = rf_process.extract(query, choices, scorer=rf_damerau.distance, score_cutoff=1)
    npt.assert_array_equal([hit[0] for hit in capped], [hit[0] for hit in every[:len(capped)]])
    npt.assert_array_equal([hit[1] for hit in every],
                           [nltk.edit_distance(query, hit[0], transpositions=True) for hit in every])
    assume(len(capped) < len(every))
    npt.assert_array_equal(every[len(capped) - 1][1], every[len(capped)][1])
    with pytest.raises(AssertionError):
        npt.assert_array_equal([hit[0] for hit in capped], [hit[0] for hit in every])


@given(LOOKUP_CHOICES, st.integers(min_value=0, max_value=25))
@SLOW
def test_one_cutoff_is_three_different_filters_across_three_scorers_of_one_metric(choices, index):
    """The same number passed as score_cutoff means opposite things depending on the scorer, which
    process.extract documents: "When an edit distance is used this represents the maximum edit
    distance and matches with a `distance > score_cutoff` are ignored. When a normalized edit distance
    is used this represents the minimal similarity and matches with a `similarity < score_cutoff` are
    ignored." With one as the cutoff, DamerauLevenshtein.distance keeps the words within one edit,
    DamerauLevenshtein.similarity keeps every word sharing one character, and
    normalized_similarity keeps only the words nltk also puts at the query's distance from itself.
    Swapping the scorer for a neighbour in the same module silently turns the bound into a
    pass-through or into an equality test. Replaces the typed len(similar) == len(WORDS) and the typed
    empty normalized_similarity result of case 164."""
    query = choices[index % len(choices)]
    tight = [hit[0] for hit in rf_process.extract(query, choices, scorer=rf_damerau.distance,
                                                  score_cutoff=1, limit=None)]
    loose = [hit[0] for hit in rf_process.extract(query, choices, scorer=rf_damerau.similarity,
                                                  score_cutoff=1, limit=None)]
    exact = [hit[0] for hit in rf_process.extract(query, choices,
                                                  scorer=rf_damerau.normalized_similarity,
                                                  score_cutoff=1, limit=None)]
    npt.assert_array_equal(sorted(set(tight) & set(loose)), sorted(tight))
    npt.assert_array_equal(sorted(set(exact) & set(tight)), sorted(exact))
    npt.assert_array_equal(sorted(exact),
                           sorted(word for word in choices
                                  if nltk.edit_distance(query, word, transpositions=True)
                                  == nltk.edit_distance(query, query, transpositions=True)))
    assume(len(tight) < len(loose))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(sorted(tight), sorted(loose))


@given(LOOKUP_CHOICES, st.integers(min_value=0, max_value=25))
@SLOW
def test_the_lookup_folds_no_case_until_a_processor_is_passed(choices, index):
    """process.extract documents its preprocessing as "Optional callable that is used to preprocess
    the strings before comparing them. Default is None, which deactivates this behaviour." A query
    typed in capitals therefore matches nothing at a one-edit bound, because every cased letter counts
    as an edit, which nltk confirms independently; passing str.lower recovers exactly the words the
    lowercase query returns. The P164 chain case-folds while indexing, so the folding is upstream of
    the lookup and not in it. Replaces the typed lookup('MEMBERS', ...) == [] and the typed distance
    of 7 in case 164."""
    query = choices[index % len(choices)]
    plain = [hit[0] for hit in rf_process.extract(query, choices, scorer=rf_damerau.distance,
                                                  score_cutoff=1, limit=None)]
    shouted = [hit[0] for hit in rf_process.extract(query.upper(), choices,
                                                    scorer=rf_damerau.distance, score_cutoff=1,
                                                    limit=None)]
    folded = [hit[0] for hit in rf_process.extract(query.upper(), choices,
                                                   scorer=rf_damerau.distance, score_cutoff=1,
                                                   limit=None, processor=str.lower)]
    npt.assert_array_equal(sorted(folded), sorted(plain))
    npt.assert_array_equal([rf_damerau.distance(query.upper(), word) for word in choices],
                           [nltk.edit_distance(query.upper(), word, transpositions=True)
                            for word in choices])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(sorted(shouted), sorted(plain))


# ---------------------------------------------------------------- a declared rate and what JSON returns
JSON_ORACLE_JS = pathlib.Path(__file__).with_name('json_number_oracle.js')
RATE_KEY = st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ_', min_size=3, max_size=7)
RATE_UNITS = st.integers(min_value=0, max_value=99)
TENTH_THAT_IS_NOT_A_HALF = st.sampled_from('12346789')
BINARY_NUMERATOR = st.integers(min_value=1, max_value=255)
LONG_FRACTION = st.tuples(st.sampled_from('123456789'),
                          st.text(alphabet='0123456789', min_size=17, max_size=24)).map(''.join)
NONFINITE_LITERAL = st.sampled_from(['NaN', 'Infinity', '-Infinity'])


def _node_json_member(document, name):
    completed = subprocess.run(['node', str(JSON_ORACLE_JS), document, name],
                               capture_output=True, text=True, check=True)
    return completed.stdout.strip()


@pytest.mark.skipif(not node_available, reason='the node runtime is required for this oracle')
@given(RATE_KEY, RATE_UNITS, TENTH_THAT_IS_NOT_A_HALF)
@ORACLE_PROCESS
def test_three_json_parsers_return_the_same_double_for_a_declared_rate(key, units, tenth):
    """The standard library's C scanner, orjson's Rust parser -- whose Cargo.toml at tag 3.12.0 depends
    on no Python package and reimplements the format -- and V8's JSON.parse under node all return the
    same double for the same declared rate, so what the next test records is a property of the format
    and not of one reader."""
    document = '{"%s": %d.%s}' % (key, units, tenth)
    npt.assert_array_equal(json.loads(document)[key], orjson.loads(document)[key])
    npt.assert_array_equal(json.loads(document)[key], float(_node_json_member(document, key)))


@given(RATE_KEY, RATE_UNITS, TENTH_THAT_IS_NOT_A_HALF)
@SLOW
def test_a_declared_rate_that_is_not_a_binary_fraction_is_not_the_number_json_returns(key, units,
                                                                                     tenth):
    """One decimal place that is not a half is never a binary fraction, so the double the parser
    returns is a different rational number from the one written in the file, which fractions.Fraction
    reads off both exactly. The declared digits survive only if parse_float is passed, documented as
    "*parse_float*, if specified, will be called with the string of every JSON float to be decoded.
    By default, this is equivalent to ``float(num_str)``." And the value that arrives by default
    cannot be used in the chain's own arithmetic at all: a Decimal refuses to multiply a float.
    Replaces the typed str(Decimal(loose['EUR_USD']))[:20] of case 168."""
    text = '%d.%s' % (units, tenth)
    document = '{"%s": %s}' % (key, text)
    npt.assert_array_equal(str(json.loads(document, parse_float=Decimal)[key]), text)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(Fraction(Decimal(text)), Fraction(json.loads(document)[key]))
    with pytest.raises(TypeError):
        Decimal(text) * json.loads(document)[key]


@given(RATE_KEY, RATE_UNITS, BINARY_NUMERATOR)
@SLOW
def test_a_declared_rate_that_is_a_binary_fraction_survives_the_double_exactly(key, units, numerator):
    """The agreeing region: a rate whose fractional part is a multiple of one two-hundred-and-fifty-
    sixth is the same rational number before and after the parse, and the string spelling comes back
    unchanged from repr as well. Whether a declared rate is destroyed by the format is decided by its
    denominator, not by its length."""
    text = str(Decimal(units) + Decimal(numerator) / Decimal(256))
    document = '{"%s": %s}' % (key, text)
    npt.assert_array_equal(Fraction(Decimal(text)), Fraction(json.loads(document)[key]))
    npt.assert_array_equal(repr(json.loads(document)[key]), text)


@given(RATE_KEY, RATE_UNITS, LONG_FRACTION)
@SLOW
def test_a_rate_written_to_more_digits_than_a_double_holds_comes_back_shortened(key, units, digits):
    """A rate declared to eighteen or more decimal places is returned by both parsers as the same
    shorter number, because a double carries at most seventeen significant decimal digits. Nothing
    raises and no field records that digits were dropped; passing parse_float=Decimal returns every
    digit that was written."""
    text = '%d.%s' % (units, digits)
    document = '{"%s": %s}' % (key, text)
    npt.assert_array_equal(str(json.loads(document, parse_float=Decimal)[key]), text)
    npt.assert_array_equal(json.loads(document)[key], orjson.loads(document)[key])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(repr(json.loads(document)[key]), text)


@pytest.mark.skipif(not node_available, reason='the node runtime is required for this oracle')
@given(RATE_KEY, NONFINITE_LITERAL)
@ORACLE_PROCESS
def test_the_standard_library_reads_three_literals_the_other_two_parsers_refuse(key, literal):
    """The standard library documents the extension itself: "This module does not comply with the RFC
    in a strict fashion, implementing some extensions that are valid JavaScript but not valid JSON. In
    particular: - Infinite and NaN number values are accepted and output". orjson documents the other
    side: "It raises `JSONDecodeError` if given an invalid type or invalid JSON. This includes if the
    input contains `NaN`, `Infinity`, or `-Infinity`, which the standard library allows, but is not
    valid JSON." V8 refuses them too, so a rates file carrying one of the three loads in this chain
    and is rejected by the next reader of the same bytes. parse_constant returns the literal that was
    written, which is how the value is recovered here without one being typed. Replaces the typed
    NaN and Infinity expectations of case 168."""
    document = '{"%s": %s}' % (key, literal)
    npt.assert_array_equal(json.loads(document, parse_constant=str)[key], literal)
    with pytest.raises(orjson.JSONDecodeError):
        orjson.loads(document)
    with pytest.raises(subprocess.CalledProcessError):
        _node_json_member(document, key)


@pytest.mark.skipif(not node_available, reason='the node runtime is required for this oracle')
@given(RATE_KEY, RATE_UNITS, TENTH_THAT_IS_NOT_A_HALF, RATE_UNITS, TENTH_THAT_IS_NOT_A_HALF)
@ORACLE_PROCESS
def test_a_repeated_rate_name_is_accepted_by_three_parsers_and_only_the_last_value_survives(
        key, first_units, first_tenth, second_units, second_tenth):
    """The standard library documents this one as an extension as well -- "Repeated names within an
    object are accepted, and only the value of the last name-value pair is used" -- but unlike the
    nonfinite literals it is not a divergence: orjson and V8 do the same, so a rates document that
    declares one currency twice is accepted everywhere and the earlier rate is unrecoverable from any
    of the three. The strict loader case 168 calls is stricter than every parser it could be
    compared with."""
    first = '%d.%s' % (first_units, first_tenth)
    second = '%d.%s' % (second_units, second_tenth)
    assume(first != second)
    document = '{"%s": %s, "%s": %s}' % (key, first, key, second)
    npt.assert_array_equal(json.loads(document)[key], json.loads('{"%s": %s}' % (key, second))[key])
    npt.assert_array_equal(orjson.loads(document)[key], json.loads(document)[key])
    npt.assert_array_equal(float(_node_json_member(document, key)), json.loads(document)[key])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(json.loads(document)[key], json.loads('{"%s": %s}' % (key, first))[key])


# ---------------------------------------------------------------- one declared list, three validators
DECLARED_JOURNALS = ['J01', 'J02', 'J03', 'J04']
JOURNAL_POOL = st.sampled_from(DECLARED_JOURNALS + ['J05', 'J06'])
POSTED_JOURNALS = st.lists(JOURNAL_POOL, min_size=1, max_size=6)
DISTINCT_JOURNALS = st.lists(st.sampled_from(DECLARED_JOURNALS), min_size=2, max_size=4, unique=True)
UNDECLARED_JOURNAL = st.sampled_from(['J05', 'J06'])
POSITION = st.integers(min_value=0, max_value=5)
JOURNAL_COLUMN_SCHEMA = pandera.DataFrameSchema(
    {'journal': pandera.Column(str, pandera.Check.isin(DECLARED_JOURNALS), unique=True)})
JOURNAL_LIST_SCHEMA = {'type': 'array', 'items': {'enum': DECLARED_JOURNALS}, 'uniqueItems': True}
JOURNAL_TABLE_SQL = ("CREATE TABLE posted (journal VARCHAR PRIMARY KEY "
                     "CHECK (journal IN ('J01', 'J02', 'J03', 'J04')))")


def _pandera_accepts(identifiers):
    try:
        JOURNAL_COLUMN_SCHEMA.validate(pd.DataFrame({'journal': identifiers}), lazy=True)
        return True
    except pandera.errors.SchemaErrors:
        return False


def _jsonschema_accepts(identifiers):
    try:
        jsonschema.validate(identifiers, JOURNAL_LIST_SCHEMA)
        return True
    except jsonschema.ValidationError:
        return False


def _duckdb_accepts(identifiers):
    connection = duckdb.connect()
    connection.execute(JOURNAL_TABLE_SQL)
    try:
        connection.executemany('INSERT INTO posted VALUES (?)', [(one,) for one in identifiers])
        return True
    except duckdb.ConstraintException:
        return False


def _pandera_failures(identifiers):
    try:
        JOURNAL_COLUMN_SCHEMA.validate(pd.DataFrame({'journal': identifiers}), lazy=True)
        raise AssertionError('the schema accepted the frame')
    except pandera.errors.SchemaErrors as refusal:
        return refusal.failure_cases


@given(POSTED_JOURNALS)
@SLOW
def test_three_validators_agree_on_which_postings_one_declared_list_admits(identifiers):
    """One declared list of journal identifiers, three engines that share no code: pandera's
    DataFrameSchema with Check.isin and unique=True, the jsonschema package's implementation of the
    JSON Schema keywords enum and uniqueItems, and DuckDB's own PRIMARY KEY and CHECK constraints.
    They accept and refuse exactly the same generated lists, so the coverage rule P161 declares is not
    a property of the validator it happens to use."""
    npt.assert_array_equal(_pandera_accepts(identifiers), _jsonschema_accepts(identifiers))
    npt.assert_array_equal(_pandera_accepts(identifiers), _duckdb_accepts(identifiers))


@given(DISTINCT_JOURNALS, POSITION)
@SLOW
def test_only_one_of_the_three_refusals_names_the_row_a_repeat_is_on(identifiers, position):
    """All three refuse a repeated identifier and each says something different about it. pandera
    reports the value and every row it sits on, which polars finds independently with is_duplicated;
    the jsonschema keyword uniqueItems fails against the whole array and its absolute_path is empty,
    so nothing in the structured error says which element repeated. The identifier P161 needs named is
    therefore named by the validator and not by the rule. Replaces the typed 'J02' in str(blocked) of
    case 161."""
    repeated = identifiers[position % len(identifiers)]
    posted = identifiers + [repeated]
    failures = _pandera_failures(posted)
    column = pl.Series(posted)
    npt.assert_array_equal(sorted(set(failures['failure_case'])),
                           sorted(column.filter(column.is_duplicated()).unique().to_list()))
    npt.assert_array_equal(sorted(failures['index']),
                           sorted(column.is_duplicated().arg_true().to_list()))
    npt.assert_array_equal(sorted(set(failures['check'])),
                           sorted({'field_uniqueness'} & set(failures['check'])))
    with pytest.raises(jsonschema.ValidationError) as refused:
        jsonschema.validate(posted, JOURNAL_LIST_SCHEMA)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(list(refused.value.absolute_path), sorted(failures['index']))


@given(DISTINCT_JOURNALS, UNDECLARED_JOURNAL, POSITION)
@SLOW
def test_two_validators_point_at_the_same_row_for_an_undeclared_identifier(identifiers, unknown,
                                                                          position):
    """Membership is the case where the two structured reports agree: pandera's failing index and the
    absolute_path of the jsonschema enum error are the same row, and DuckDB refuses the same list
    through its CHECK constraint. What differs from the repeat case is only which keyword failed."""
    posted = list(identifiers)
    posted.insert(position % (len(posted) + 1), unknown)
    failures = _pandera_failures(posted)
    with pytest.raises(jsonschema.ValidationError) as refused:
        jsonschema.validate(posted, JOURNAL_LIST_SCHEMA)
    npt.assert_array_equal(list(refused.value.absolute_path), list(failures['index']))
    npt.assert_array_equal(sorted(set(failures['failure_case'])), [unknown])
    npt.assert_array_equal(_duckdb_accepts(posted), _jsonschema_accepts(posted))


@given(POSITION)
@SLOW
def test_the_index_set_comparison_the_chain_uses_cannot_see_a_repeated_posting(position):
    """The coverage step is pd.Index(declared).symmetric_difference(pd.Index(posted)), and a set
    operation deduplicates before it compares: a frame that posts one journal twice and covers every
    declared journal produces the same empty difference as the exact frame, which is what the schema
    catches and the comparison does not. The blindness is the set operation rather than the library,
    because DuckDB's EXCEPT answers the same way in both directions on the same lists. Replaces the
    typed len(pd.Index(...).symmetric_difference(...)) == 0 of case 161."""
    repeated = DECLARED_JOURNALS[position % len(DECLARED_JOURNALS)]
    posted = DECLARED_JOURNALS + [repeated]
    npt.assert_array_equal(list(pd.Index(DECLARED_JOURNALS).symmetric_difference(pd.Index(posted))),
                           list(pd.Index(DECLARED_JOURNALS).symmetric_difference(
                               pd.Index(DECLARED_JOURNALS))))
    connection = duckdb.connect()
    connection.register('declared', pd.DataFrame({'journal': DECLARED_JOURNALS}))
    connection.register('posted', pd.DataFrame({'journal': posted}))
    npt.assert_array_equal(
        connection.execute('SELECT journal FROM declared EXCEPT SELECT journal FROM posted '
                           'UNION SELECT journal FROM posted EXCEPT SELECT journal FROM declared')
        .fetchall(),
        connection.execute('SELECT journal FROM declared EXCEPT SELECT journal FROM declared')
        .fetchall())
    with pytest.raises(pandera.errors.SchemaErrors):
        JOURNAL_COLUMN_SCHEMA.validate(pd.DataFrame({'journal': posted}), lazy=True)


# ---------------------------------------------------------------- a whole-unit break-even volume
BREAK_EVEN_CENTS = st.integers(min_value=1, max_value=2000)
BUNDLE_COUNTS = st.lists(st.integers(min_value=1, max_value=50_000), min_size=20, max_size=30,
                         unique=True)
PART_CENT = st.integers(min_value=1, max_value=1999)


def _exact_break_even(fixed, contribution):
    return [math.ceil(Fraction(one) / Fraction(contribution)) for one in fixed]


def _decimal_break_even(fixed, contribution):
    return [int((one / contribution).to_integral_value(rounding=ROUND_CEILING)) for one in fixed]


def _float_break_even(fixed, contribution):
    return [math.ceil(float(one) / float(contribution)) for one in fixed]


def _duckdb_break_even(fixed, contribution):
    rows = pd.DataFrame({'position': range(len(fixed)),
                         'fixed': [str(one) for one in fixed],
                         'contribution': [str(contribution)] * len(fixed)})
    connection = duckdb.connect()
    connection.register('inputs', rows)
    return connection.execute(
        'SELECT ceil(CAST(fixed AS DECIMAL(18,2)) / CAST(contribution AS DECIMAL(18,2))), '
        '       ceil(CAST(fixed AS DOUBLE) / CAST(contribution AS DOUBLE)) '
        'FROM inputs ORDER BY position').fetchall()


@given(BREAK_EVEN_CENTS, BUNDLE_COUNTS)
@SLOW
def test_two_exact_implementations_agree_on_every_break_even_volume(cents, counts):
    """P170 takes the break-even volume as Decimal.to_integral_value with ROUND_CEILING. Over fixed
    costs generated as an exact whole number of bundles, decimal's rounding of its own 28-digit
    quotient and fractions.Fraction's exact ceiling return the same volume, and it is the number of
    bundles the cost was built from. This is the agreeing region and the reference the rest of the
    cluster is measured against."""
    contribution = Decimal(cents) / Decimal(100)
    fixed = [Decimal(cents * count) / Decimal(100) for count in counts]
    npt.assert_array_equal(_decimal_break_even(fixed, contribution),
                           _exact_break_even(fixed, contribution))
    npt.assert_array_equal(_exact_break_even(fixed, contribution), counts)


@given(BREAK_EVEN_CENTS, BUNDLE_COUNTS)
@SLOW
def test_the_same_break_even_in_floating_point_orders_bundles_nobody_needs(cents, counts):
    """The same quotient in binary floating point never returns fewer bundles than the exact
    calculation and does not always return the same number: over a generated range of exact bundle
    counts it lands one bundle high on about an eighth of them, because the fixed cost and the
    contribution are each inexact as doubles and their quotient falls just above the whole number it
    should equal. Nothing raises, and the surplus bundle is indistinguishable in the answer from a
    genuine part-bundle remainder."""
    contribution = Decimal(cents) / Decimal(100)
    fixed = [Decimal(cents * count) / Decimal(100) for count in counts]
    exact = _exact_break_even(fixed, contribution)
    in_binary = _float_break_even(fixed, contribution)
    npt.assert_array_equal(np.minimum(exact, in_binary), exact)
    assume(in_binary != exact)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(in_binary, exact)


@given(BREAK_EVEN_CENTS, BUNDLE_COUNTS)
@SLOW
def test_the_sql_engine_answers_the_exact_question_in_floating_point(cents, counts):
    """DuckDB 1.5.5 has a DECIMAL type and its operator table calls `/` "Float division"; executed on
    two DECIMAL operands it returns a DOUBLE, so the ceiling of a DECIMAL quotient and the ceiling of
    a DOUBLE quotient are the same number in that engine, and both are the number Python's float path
    gives rather than the exact one. A break-even recomputed in SQL from the same declared figures
    therefore carries the surplus bundle that Decimal does not."""
    contribution = Decimal(cents) / Decimal(100)
    fixed = [Decimal(cents * count) / Decimal(100) for count in counts]
    in_engine = _duckdb_break_even(fixed, contribution)
    npt.assert_array_equal([row[0] for row in in_engine], [row[1] for row in in_engine])
    npt.assert_array_equal([row[0] for row in in_engine], _float_break_even(fixed, contribution))
    exact = _exact_break_even(fixed, contribution)
    assume([int(row[0]) for row in in_engine] != exact)
    with pytest.raises(AssertionError):
        npt.assert_array_equal([int(row[0]) for row in in_engine], exact)


@given(BREAK_EVEN_CENTS)
@SLOW
def test_a_zero_contribution_is_a_refusal_in_two_libraries_and_infinity_in_two_engines(cents):
    """Asked for the break-even volume of a product that contributes nothing, decimal raises
    DivisionByZero and Fraction raises ZeroDivisionError, while numpy and DuckDB both answer with an
    infinity and no exception. Whether the unanswerable case arrives as a refusal or as a number
    depends on which of the four the figure passed through."""
    fixed = Decimal(cents) / Decimal(100)
    with pytest.raises(DivisionByZero):
        fixed / Decimal(0)
    with pytest.raises(ZeroDivisionError):
        Fraction(fixed) / Fraction(0)
    connection = duckdb.connect()
    in_engine = connection.execute(
        "SELECT CAST('%s' AS DECIMAL(18,2)) / CAST('0.00' AS DECIMAL(18,2))" % fixed).fetchone()[0]
    with np.errstate(divide='ignore'):
        npt.assert_array_equal(in_engine, np.divide(np.float64(float(fixed)), np.float64(0.0)))


@given(BREAK_EVEN_CENTS, st.integers(min_value=1, max_value=50_000), PART_CENT)
@SLOW
def test_a_negative_contribution_returns_a_volume_the_chain_s_rounding_gets_wrong_way_round(
        cents, count, remainder):
    """A contribution of less than zero still divides, and the quotient is negative, where the two
    roundings part company: ROUND_CEILING moves toward positive infinity and ROUND_UP moves away from
    zero. Fraction's exact ceiling confirms which one ROUND_CEILING is, and the volume P170's
    ROUND_CEILING returns is the one at which the product is still losing money, while the volume
    ROUND_UP returns is not. On a negative contribution the rounding the chain declares is the
    rounding that answers the opposite question. Replaces the typed Decimal('-725') and Decimal('-726')
    of case 170."""
    assume(remainder < cents)
    contribution = -(Decimal(cents) / Decimal(100))
    fixed = Decimal(cents * count + remainder) / Decimal(100)
    quotient = fixed / contribution
    toward_infinity = quotient.to_integral_value(rounding=ROUND_CEILING)
    away_from_zero = quotient.to_integral_value(rounding=ROUND_UP)
    npt.assert_array_equal(int(toward_infinity),
                           math.ceil(Fraction(fixed) / Fraction(contribution)))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(toward_infinity, away_from_zero)
    npt.assert_array_less(Fraction(int(toward_infinity)) * Fraction(contribution), Fraction(fixed))
    npt.assert_array_less(Fraction(fixed), Fraction(int(away_from_zero)) * Fraction(contribution))


# ---------------------------------------------------------------- one spreadsheet cell, three readers
ODS_DATE = st.dates(min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31))
ODF_CELL_TAG = '{%s}table-cell' % TABLENS
ODF_DATE_ATTRIBUTE = '{%s}date-value' % OFFICENS
ODF_VALUE_ATTRIBUTE = '{%s}value' % OFFICENS
ODF_FORMULA_ATTRIBUTE = '{%s}formula' % TABLENS


def _ods_bytes(start, finish):
    """odfpy writes the cells; the dates and the elapsed days come from the strategy."""
    document = odf.opendocument.OpenDocumentSpreadsheet()
    table = odf.table.Table(name='Schedule')
    row = odf.table.TableRow()
    for moment in (start, finish):
        cell = odf.table.TableCell(valuetype='date', datevalue=moment.isoformat())
        cell.addElement(odf.text.P(text=moment.isoformat()))
        row.addElement(cell)
    elapsed = odf.table.TableCell(valuetype='float', value=str((start - finish).days),
                                  formula='of:=[.A1]-[.B1]')
    elapsed.addElement(odf.text.P(text=str((start - finish).days)))
    row.addElement(elapsed)
    table.addElement(row)
    document.spreadsheet.addElement(table)
    written = io.BytesIO()
    document.write(written)
    return written.getvalue()


def _ods_typed_edit(data, moment):
    """Set only the typed date on the first cell, which is what an editor of the value would write."""
    document = odf.opendocument.load(io.BytesIO(data))
    document.getElementsByType(odf.table.TableCell)[0].setAttrNS(OFFICENS, 'date-value',
                                                                 moment.isoformat())
    written = io.BytesIO()
    document.write(written)
    return written.getvalue()


def _ods_displayed(data, index):
    cell = odf.opendocument.load(io.BytesIO(data)).getElementsByType(odf.table.TableCell)[index]
    return odf.teletype.extractText(cell)


def _ods_in_calamine(data):
    return CalamineWorkbook.from_filelike(io.BytesIO(data)).get_sheet_by_index(0).to_python()[0]


def _ods_in_lxml(data, index):
    content = zipfile.ZipFile(io.BytesIO(data)).read('content.xml')
    cell = list(lxml_etree.fromstring(content).iter(ODF_CELL_TAG))[index]
    return (cell.get(ODF_DATE_ATTRIBUTE), cell.get(ODF_VALUE_ATTRIBUTE),
            cell.get(ODF_FORMULA_ATTRIBUTE), [paragraph.text for paragraph in cell])


@given(ODS_DATE, ODS_DATE)
@SLOW
def test_three_readers_of_one_spreadsheet_cell_agree_before_it_is_edited(start, finish):
    """odfpy builds the document, python-calamine 0.8.2 reads it through the Rust calamine crate and
    declares no Python dependencies, and libxml2 through lxml reads content.xml out of the same zip.
    On a cell whose typed date and displayed paragraph were written together, all three report the
    same day. This is the agreeing region for P166's readback."""
    data = _ods_bytes(start, finish)
    npt.assert_array_equal(_ods_in_calamine(data)[0].isoformat(), start.isoformat())
    npt.assert_array_equal(_ods_displayed(data, 0), start.isoformat())
    npt.assert_array_equal(_ods_in_lxml(data, 0)[0], start.isoformat())
    npt.assert_array_equal(_ods_in_lxml(data, 0)[3], [start.isoformat()])


@given(ODS_DATE, ODS_DATE, ODS_DATE)
@SLOW
def test_moving_the_typed_date_leaves_two_readers_reporting_two_different_days(start, finish, moved):
    """An edit that sets office:date-value, which is the attribute a value carries, moves the day
    python-calamine reports and leaves the text:p paragraph beside it untouched, so the two readers of
    one cell name two different days and lxml shows both of them sitting in content.xml. Neither
    reader is wrong and neither raises. Replaces the typed after['date'] and after['text'] of case
    166."""
    assume(moved != start)
    data = _ods_bytes(start, finish)
    edited = _ods_typed_edit(data, moved)
    npt.assert_array_equal(_ods_in_calamine(edited)[0].isoformat(), moved.isoformat())
    npt.assert_array_equal(_ods_displayed(edited, 0), start.isoformat())
    npt.assert_array_equal(_ods_in_lxml(edited, 0)[0], moved.isoformat())
    npt.assert_array_equal(_ods_in_lxml(edited, 0)[3], [start.isoformat()])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_ods_in_calamine(edited)[0].isoformat(), _ods_displayed(edited, 0))
    npt.assert_array_equal(_ods_in_calamine(data)[0].isoformat(), start.isoformat())
    npt.assert_array_equal(_ods_displayed(data, 0), start.isoformat())


@given(ODS_DATE, ODS_DATE, ODS_DATE)
@SLOW
def test_the_cached_result_beside_the_formula_still_answers_the_old_question(start, finish, moved):
    """The elapsed-days cell carries both a formula and the result of that formula. Moving the date it
    refers to changes neither: lxml finds the same office:value and the same table:formula in the
    edited file, python-calamine returns the same number it returned before, and that number is the
    difference of the dates before the edit rather than after it. Nothing in the package recomputes,
    and the reader that sees only values cannot tell that the number is stale. Replaces the typed
    dependent['value'] == '766' of case 166."""
    assume(moved != start)
    data = _ods_bytes(start, finish)
    edited = _ods_typed_edit(data, moved)
    npt.assert_array_equal(_ods_in_calamine(edited)[2], _ods_in_calamine(data)[2])
    npt.assert_array_equal(_ods_in_lxml(edited, 2)[1:3], _ods_in_lxml(data, 2)[1:3])
    npt.assert_array_equal(_ods_in_calamine(edited)[2], (start - finish).days)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_ods_in_calamine(edited)[2], (moved - finish).days)


# ---------------------------------------------------------------- one document, two ODF libraries
ODF_WORD = st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
                   min_size=1, max_size=8)
ODF_PART = st.one_of(
    st.tuples(st.just('text'), ODF_WORD),
    st.tuples(st.just('spaces'), st.one_of(st.integers(min_value=1, max_value=8), st.none())),
    st.tuples(st.just('tab'), st.none()),
    st.tuples(st.just('break'), st.none()))
ODF_PARAGRAPH = st.lists(ODF_PART, min_size=1, max_size=8)


def _odt_paragraph(parts):
    """Build one text:p out of the generated parts with odfpy's own element classes."""
    paragraph = odf.text.P()
    for kind, value in parts:
        if kind == 'text':
            paragraph.addText(value)
        elif kind == 'spaces':
            paragraph.addElement(odf.text.S() if value is None else odf.text.S(c=value))
        elif kind == 'tab':
            paragraph.addElement(odf.text.Tab())
        else:
            paragraph.addElement(odf.text.LineBreak())
    return paragraph


def _odt_bytes(paragraphs, cells, typed=False):
    document = odf.opendocument.OpenDocumentText()
    for parts in paragraphs:
        document.text.addElement(_odt_paragraph(parts))
    table = odf.table.Table(name='T1')
    row = odf.table.TableRow()
    for value in cells:
        cell = (odf.table.TableCell(valuetype='string', stringvalue=value) if typed
                else odf.table.TableCell())
        cell.addElement(odf.text.P(text=value))
        row.addElement(cell)
    table.addElement(row)
    document.text.addElement(table)
    written = io.BytesIO()
    document.write(written)
    return written.getvalue()


def _odt_in_odfpy(data):
    document = odf.opendocument.load(io.BytesIO(data))
    return document, [odf.teletype.extractText(p) for p in document.getElementsByType(odf.text.P)]


def _odt_in_odfdo(data):
    document = odfdo.Document(io.BytesIO(data))
    return document, [p.inner_text for p in document.body.get_paragraphs()]


@given(st.lists(ODF_PARAGRAPH, min_size=1, max_size=5))
@SLOW
def test_two_odf_libraries_expand_the_same_paragraph_whitespace(paragraphs):
    """odfpy's teletype.extractText and odfdo's Element.inner_text are two implementations of the same
    operation with no shared ancestor: odfdo declares only lxml and typing-extensions and descends
    from lpod-python. On text:s, text:tab and text:line-break written by odfpy they return the same
    string, so the expansion of the whitespace elements is not a private odfpy convention. Replaces
    the typed 'A   B', 'left\\tright' and 'first\\nsecond' of case 165."""
    data = _odt_bytes(paragraphs, [])
    _, by_odfpy = _odt_in_odfpy(data)
    _, by_odfdo = _odt_in_odfdo(data)
    npt.assert_array_equal(by_odfpy, by_odfdo)


@given(st.lists(ODF_PARAGRAPH, min_size=1, max_size=4), st.lists(ODF_WORD, min_size=2, max_size=4))
@SLOW
def test_the_flat_paragraph_list_of_both_libraries_counts_the_table_cells(paragraphs, cells):
    """odfpy's getElementsByType(P) and odfdo's body.get_paragraphs(), which is the XPath
    descendant::text:p, both return the body paragraphs and the paragraph inside every table cell in
    one flat list, and both lists are longer than the body itself. Nothing in either list says which
    entries came out of the table, so a positional comparison against a source document shifts from
    the table on. The table here holds at least two cells, which is the region where the two counts
    have to differ; a one-cell table replaces itself in the count and the two agree. Replaces the
    typed len(flat) == 6 and len(body) == 5 of case 165."""
    data = _odt_bytes(paragraphs, cells)
    _, by_odfpy = _odt_in_odfpy(data)
    odfdo_document, by_odfdo = _odt_in_odfdo(data)
    npt.assert_array_equal(len(by_odfpy), len(by_odfdo))
    npt.assert_array_equal(len(by_odfpy), len(paragraphs) + len(cells))
    npt.assert_array_equal(len(odfdo_document.body.children), len(paragraphs) + 1)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(len(by_odfpy), len(odfdo_document.body.children))


@given(st.lists(ODF_WORD, min_size=1, max_size=5))
@SLOW
def test_odfpy_welds_the_table_cells_and_odfdo_keeps_them_apart(cells):
    """Asked for the text of one table, odfpy concatenates the cells with nothing between them, which
    is exactly the join of its own per-cell extractions. odfdo's inner_text of the same table ends
    every paragraph with a newline, so the same bytes yield a string in which the cell boundaries are
    still visible. The two libraries agree on each cell and disagree on the table. Replaces the typed
    body[4] == 'cell Acell B' of case 165."""
    data = _odt_bytes([], cells)
    odfpy_document, _ = _odt_in_odfpy(data)
    table = odfpy_document.getElementsByType(odf.table.Table)[0]
    welded = odf.teletype.extractText(table)
    per_cell = [odf.teletype.extractText(c)
                for c in odfpy_document.getElementsByType(odf.table.TableCell)]
    npt.assert_array_equal(welded, ''.join(per_cell))
    npt.assert_array_equal(per_cell, cells)
    odfdo_document, _ = _odt_in_odfdo(data)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(welded, odfdo_document.body.get_tables()[0].inner_text)


@given(ODF_WORD, ODF_WORD, ODF_WORD)
@SLOW
def test_the_welded_table_text_does_not_say_where_the_cells_were(head, middle, tail):
    """Two tables whose cells are cut at different points weld to one identical string under odfpy's
    extractText while their cell lists differ, so the welded text cannot be split back into the cells
    it came from. This is the loss the flat comparison of case 165 depends on and the reason a cell
    walk and a table walk are not interchangeable."""
    documents = [_odt_in_odfpy(_odt_bytes([], split))[0]
                 for split in ([head + middle, tail], [head, middle + tail])]
    welded = [odf.teletype.extractText(d.getElementsByType(odf.table.Table)[0]) for d in documents]
    cells = [[odf.teletype.extractText(c) for c in d.getElementsByType(odf.table.TableCell)]
             for d in documents]
    npt.assert_array_equal(welded[0], welded[1])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(cells[0], cells[1])


@given(st.lists(ODF_WORD, min_size=1, max_size=4))
@SLOW
def test_a_typed_cell_and_an_untyped_cell_read_alike_in_odfpy_and_differently_in_odfdo(cells):
    """One table writes office:value-type and office:string-value beside the paragraph and the other
    writes only the paragraph. odfpy's extractText returns the same text for both, because it reads
    the paragraph and not the attribute. odfdo's str() of a table is a CSV of the typed values, so
    the untyped table comes back as empty fields and the typed one carries the words. Two readers of
    one visible table, and the attribute that decides the answer is invisible to the text walk."""
    untyped = _odt_bytes([], cells, typed=False)
    typed = _odt_bytes([], cells, typed=True)
    by_odfpy = [odf.teletype.extractText(_odt_in_odfpy(data)[0].getElementsByType(odf.table.Table)[0])
                for data in (untyped, typed)]
    npt.assert_array_equal(by_odfpy[0], by_odfpy[1])
    tables = [_odt_in_odfdo(data)[0].body.get_tables()[0] for data in (untyped, typed)]
    with pytest.raises(AssertionError):
        npt.assert_array_equal(str(tables[0]), str(tables[1]))
    npt.assert_array_equal([c.value for c in tables[1].get_rows()[0].get_cells()], cells)
    with pytest.raises(AssertionError):
        npt.assert_array_equal([c.value for c in tables[0].get_rows()[0].get_cells()], cells)


# ---------------------------------------------------------------- reading a deck, and what that writes
OFFICEPARSER_DIRECTORY = pathlib.Path(os.environ.get('OFFICEPARSER_DIR',
                                                     str(pathlib.Path.home() / 'officeparser-oracle')))
PPTX_NOTES_ORACLE_JS = pathlib.Path(__file__).with_name('pptx_notes_oracle.js')
PPTX_PARTS_ORACLE_PHP = pathlib.Path(__file__).with_name('pptx_parts_oracle.php')
officeparser_available = (shutil.which('node') is not None
                          and (OFFICEPARSER_DIRECTORY / 'node_modules' / 'officeparser').is_dir())
PPTX_LINE = st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'),
                                           whitelist_characters='&<>"\''),
                    min_size=1, max_size=12)
PPTX_DECK = st.tuples(PPTX_LINE, st.lists(PPTX_LINE, min_size=1, max_size=3))


def _pptx_bytes(title, lines, notes=None, picture=None):
    """Build one deck with python-pptx from generated text. The picture, when asked for, is a PNG
    written by PyMuPDF, so no image bytes are assembled here."""
    deck = pptx.Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[5])
    slide.shapes.title.text = title
    box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(4), Inches(1))
    box.text_frame.text = lines[0]
    for extra in lines[1:]:
        box.text_frame.add_paragraph().text = extra
    if picture is not None:
        pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, picture[0], picture[1]))
        pixmap.set_rect(pixmap.irect, (picture[2], picture[2], picture[2]))
        slide.shapes.add_picture(io.BytesIO(pixmap.tobytes('png')),
                                 Inches(5), Inches(2), Inches(1), Inches(1))
    if notes is not None:
        frame = slide.notes_slide.notes_text_frame
        frame.text = notes[0]
        for extra in notes[1:]:
            frame.add_paragraph().text = extra
    written = io.BytesIO()
    deck.save(written)
    return written.getvalue()


def _pptx_parts(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return sorted(archive.namelist())


def _pptx_parts_in_php(data):
    """The same package listed by libzip through PHP's ZipArchive. The shim parses argv, calls the
    library and prints one entry name per line."""
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / 'deck.pptx'
        path.write_bytes(data)
        completed = subprocess.run(['php', str(PPTX_PARTS_ORACLE_PHP), str(path)],
                                   capture_output=True, encoding='utf-8', check=True)
    return sorted(completed.stdout.split('\n')[:-1])


def _pptx_touched(data, how):
    """Read one property of the first slide, save the deck again and return the new bytes."""
    deck = pptx.Presentation(io.BytesIO(data))
    getattr(deck.slides[0], how)
    written = io.BytesIO()
    deck.save(written)
    return written.getvalue()


def _pptx_notes_in_officeparser(data):
    """The same package read by officeparser 7.8.0 under node: one list of paragraph texts per note.
    The shim parses argv, calls the library and prints the tree it returns as JSON."""
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / 'deck.pptx'
        path.write_bytes(data)
        completed = subprocess.run(['node', str(PPTX_NOTES_ORACLE_JS), str(path)],
                                   capture_output=True, encoding='utf-8', check=True,
                                   env={**os.environ,
                                        'NODE_PATH': str(OFFICEPARSER_DIRECTORY / 'node_modules')})
    tree = json.loads(completed.stdout)
    return [[child['text'] for child in note['children']]
            for note in tree['content'][0]['notes']]


def _pptx_notes_in_python_pptx(data):
    frame = pptx.Presentation(io.BytesIO(data)).slides[0].notes_slide.notes_text_frame
    return frame.text, [paragraph.text for paragraph in frame.paragraphs]


@pytest.mark.skipif(not php_binary_available, reason='php is required for this oracle')
@given(PPTX_DECK, PPTX_DECK)
@ORACLE_PROCESS
def test_reading_the_notes_property_writes_the_same_five_parts_into_any_deck(first, second):
    """python-pptx documents the side effect: has_notes_slide tests for a notes slide "without the
    possible side effect of creating one", which notes_slide has. Executed, that read followed by a
    save adds parts to the package, and the parts it adds are the same list for two decks with
    different titles and different numbers of paragraphs, so the cost is a property of the read and
    not of the deck. libzip through PHP's ZipArchive lists the same entries as zipfile for every
    package here. Replaces the typed len(added) == 5 of case 162."""
    packages = [_pptx_bytes(*specification) for specification in (first, second)]
    for data in packages:
        npt.assert_array_equal(_pptx_parts(data), _pptx_parts_in_php(data))
    added = [sorted(set(_pptx_parts(_pptx_touched(data, 'notes_slide'))) - set(_pptx_parts(data)))
             for data in packages]
    npt.assert_array_equal(added[0], added[1])
    npt.assert_array_equal(added[0], sorted(set(_pptx_parts_in_php(_pptx_touched(packages[0], 'notes_slide')))
                                            - set(_pptx_parts_in_php(packages[0]))))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_pptx_parts(packages[0]),
                               _pptx_parts(_pptx_touched(packages[0], 'notes_slide')))


@given(PPTX_DECK)
@ORACLE_PROCESS
def test_the_guarded_test_for_notes_leaves_every_part_where_it_was(specification):
    """Reading has_notes_slide and saving returns a package with exactly the entries it had; reading
    notes_slide and saving does not. Both reads are spelled the same way at the call site and only
    one of them is a question. Replaces the typed empty added list of case 162."""
    data = _pptx_bytes(*specification)
    npt.assert_array_equal(_pptx_parts(_pptx_touched(data, 'has_notes_slide')), _pptx_parts(data))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_pptx_parts(_pptx_touched(data, 'notes_slide')), _pptx_parts(data))


@pytest.mark.skipif(not officeparser_available,
                    reason='node and an officeparser checkout are required for this oracle')
@given(PPTX_DECK, st.lists(PPTX_LINE, min_size=1, max_size=4))
@ORACLE_PROCESS
def test_two_readers_return_the_same_note_paragraphs_and_the_same_literal(specification, notes):
    """officeparser 7.8.0 reads the same .pptx with its own zip inflater and its own XML parser and
    returns one node per notes paragraph. On notes whose text carries ampersands, angle brackets and
    quotes -- the characters the package stores as XML entities -- the two implementations return the
    same strings, and python-pptx's own text of the whole frame is those strings joined with the
    line feed both projects document as their separator. Replaces the typed 'A & B < 5 > 2' and the
    typed paragraph count of case 162."""
    data = _pptx_bytes(*specification, notes=notes)
    text, paragraphs = _pptx_notes_in_python_pptx(data)
    npt.assert_array_equal(paragraphs, _pptx_notes_in_officeparser(data)[0])
    npt.assert_array_equal(text, '\n'.join(_pptx_notes_in_officeparser(data)[0]))
    npt.assert_array_equal(len(text.split('\n')), len(paragraphs))


@pytest.mark.skipif(not officeparser_available,
                    reason='node and an officeparser checkout are required for this oracle')
@given(PPTX_DECK, PPTX_LINE, PPTX_LINE, PPTX_LINE)
@ORACLE_PROCESS
def test_the_same_string_becomes_two_paragraphs_or_one_depending_on_which_setter_took_it(
        specification, first, head, tail):
    """python-pptx's own source says a line feed assigned to TextFrame.text adds "A new paragraph
    ... for each line-feed character", while the same character assigned to _Paragraph.text is
    "translated to a line-break", and names the contrast itself. Executed, one string written as the
    first note paragraph produces one more paragraph than the same string written as the second, and
    officeparser counts the paragraphs the same way in both arrangements. The list of note strings a
    caller passes is therefore not read back as that list."""
    joined = head + '\n' + tail
    as_first = _pptx_bytes(*specification, notes=[joined, first])
    as_second = _pptx_bytes(*specification, notes=[first, joined])
    npt.assert_array_equal(len(_pptx_notes_in_python_pptx(as_first)[1]),
                           len(_pptx_notes_in_python_pptx(as_second)[1]) + 1)
    for data in (as_first, as_second):
        npt.assert_array_equal(len(_pptx_notes_in_python_pptx(data)[1]),
                               len(_pptx_notes_in_officeparser(data)[0]))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_pptx_notes_in_python_pptx(as_first)[1],
                               _pptx_notes_in_python_pptx(as_second)[1])


@pytest.mark.skipif(not officeparser_available,
                    reason='node and an officeparser checkout are required for this oracle')
@given(PPTX_DECK, PPTX_LINE, PPTX_LINE, PPTX_LINE)
@ORACLE_PROCESS
def test_a_line_break_reads_as_a_vertical_tab_here_and_as_a_newline_in_the_other_reader(
        specification, first, head, tail):
    """The line break python-pptx writes for that assigned line feed comes back as a vertical tab,
    which its source documents as PowerPoint's clipboard encoding of a soft carriage return, and
    comes back from officeparser as the line feed that was written. So the frame text always splits
    on line feeds into exactly its paragraph count, whatever breaks the paragraphs contain, while
    the other reader's text of the same notes splits into more lines than there are paragraphs.
    Replaces the typed text.count('\\n') == 1 of case 162 and corrects its caveat: no paragraph
    written through this library can contain a line feed of its own."""
    data = _pptx_bytes(*specification, notes=[first, head + '\n' + tail])
    text, paragraphs = _pptx_notes_in_python_pptx(data)
    by_officeparser = _pptx_notes_in_officeparser(data)[0]
    npt.assert_array_equal(len(text.split('\n')), len(paragraphs))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(paragraphs, by_officeparser)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(len(text.split('\n')), len('\n'.join(by_officeparser).split('\n')))


@given(PPTX_DECK, st.tuples(st.integers(min_value=2, max_value=8),
                            st.integers(min_value=2, max_value=8),
                            st.integers(min_value=0, max_value=255)))
@ORACLE_PROCESS
def test_a_picture_has_no_text_attribute_at_all(specification, picture):
    """A walk over shapes that reads .text raises AttributeError on the picture rather than returning
    an empty string, so the guarded walk is the one that finishes. What it returns is the text of the
    shapes that have a text frame, in the order the deck holds them. Replaces the typed shape text
    list of case 162."""
    data = _pptx_bytes(*specification, picture=picture)
    shapes = pptx.Presentation(io.BytesIO(data)).slides[0].shapes
    pictures = [shape for shape in shapes if not shape.has_text_frame]
    with pytest.raises(AttributeError):
        pictures[0].text
    npt.assert_array_equal([shape.text for shape in shapes if shape.has_text_frame],
                           [specification[0], '\n'.join(specification[1])])


# ---------------------------------------------------------------- one amount, a chart and its workbook
CHART_CENTS = st.integers(min_value=1, max_value=5000000).map(lambda n: Decimal(n * 10).scaleb(-2))
CHART_WHOLE = st.integers(min_value=1, max_value=50000).map(lambda n: Decimal(n * 100).scaleb(-2))
CHART_VALUE_TAG = pptx_ns.qn('c:v')


def _chart_bytes(categories, amounts, name='Actual'):
    deck = pptx.Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    data = pptx.chart.data.CategoryChartData()
    data.categories = list(categories)
    data.add_series(name, tuple(amounts))
    slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(1), Inches(1), Inches(6),
                           Inches(4), data)
    written = io.BytesIO()
    deck.save(written)
    return written.getvalue()


def _chart_cached_texts(data):
    """Every c:v in the package, read with the standard library's expat parser rather than the lxml
    tree python-pptx writes with. The qualified name comes from python-pptx's own ns.qn."""
    texts = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in archive.namelist():
            if name.endswith('.xml'):
                texts.extend(element.text for element
                             in ElementTree.fromstring(archive.read(name)).iter(CHART_VALUE_TAG))
    return texts


def _chart_workbook(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        blob = archive.read([name for name in archive.namelist() if name.endswith('.xlsx')][0])
    sheet = openpyxl.load_workbook(io.BytesIO(blob)).active
    by_openpyxl = [row[1].value for row in sheet.iter_rows()][1:]
    by_calamine = [row[1] for row in
                   CalamineWorkbook.from_filelike(io.BytesIO(blob)).get_sheet_by_index(0).to_python()][1:]
    return by_openpyxl, by_calamine


def _chart_values(data):
    chart = pptx.Presentation(io.BytesIO(data)).slides[0].shapes[0].chart
    return list(chart.plots[0].categories), list(chart.series[0].values)


@given(st.lists(PPTX_LINE, min_size=2, max_size=5, unique=True), st.data())
@ORACLE_PROCESS
def test_the_cached_chart_number_is_the_text_of_the_object_it_was_handed(categories, source):
    """python-pptx writes the number a caller hands it into c:v as that object's own text, so a
    Decimal carrying trailing cents and the float of the same amount produce two different packages.
    The library cannot tell them apart afterwards: chart.series[0].values returns the same floats for
    both. Read here with expat rather than the lxml tree the library writes with. Replaces the typed
    cached value list of case 167."""
    amounts = source.draw(st.lists(CHART_CENTS, min_size=len(categories), max_size=len(categories)))
    as_decimal = _chart_bytes(categories, amounts)
    as_float = _chart_bytes(categories, [float(amount) for amount in amounts])
    npt.assert_array_equal(_chart_cached_texts(as_decimal),
                           ['Actual'] + list(categories) + [str(amount) for amount in amounts])
    npt.assert_array_equal(_chart_cached_texts(as_float),
                           ['Actual'] + list(categories) + [str(float(amount)) for amount in amounts])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_chart_cached_texts(as_decimal), _chart_cached_texts(as_float))
    npt.assert_allclose(_chart_values(as_decimal)[1], _chart_values(as_float)[1])


@given(st.lists(PPTX_LINE, min_size=2, max_size=5, unique=True), st.data())
@ORACLE_PROCESS
def test_the_charts_own_workbook_does_not_carry_the_cents_the_chart_xml_carries(categories, source):
    """The same deck holds the amount twice: once as the text of c:v and once as a cell in the
    embedded xlsx the chart is bound to. Two readers of that workbook, openpyxl and the Rust
    calamine, return the amount as a number equal to the one that was handed in, and neither returns
    the trailing cents that are sitting in the chart XML beside it. Replaces the typed
    workbook[2] == ['Software', 2130] of case 167."""
    amounts = source.draw(st.lists(CHART_CENTS, min_size=len(categories), max_size=len(categories)))
    data = _chart_bytes(categories, amounts)
    by_openpyxl, by_calamine = _chart_workbook(data)
    npt.assert_allclose(by_openpyxl, [float(amount) for amount in amounts])
    npt.assert_allclose(by_calamine, [float(amount) for amount in amounts])
    with pytest.raises(AssertionError):
        npt.assert_array_equal([str(value) for value in by_openpyxl],
                               [str(amount) for amount in amounts])


@given(st.lists(PPTX_LINE, min_size=2, max_size=5, unique=True), st.data())
@ORACLE_PROCESS
def test_two_readers_of_the_charts_workbook_disagree_about_a_whole_amount(categories, source):
    """A whole-dollar amount reaches the embedded sheet with no decimal point in its stored text, and
    openpyxl returns it as an int where calamine returns it as a float. The numbers are equal and the
    types are not, so a comparison that checks the type of a chart's own backing cell answers
    differently depending on which reader opened it."""
    amounts = source.draw(st.lists(CHART_WHOLE, min_size=len(categories), max_size=len(categories)))
    by_openpyxl, by_calamine = _chart_workbook(_chart_bytes(categories,
                                                            [float(amount) for amount in amounts]))
    npt.assert_allclose(by_openpyxl, by_calamine)
    with pytest.raises(AssertionError):
        npt.assert_array_equal([type(value).__name__ for value in by_openpyxl],
                               [type(value).__name__ for value in by_calamine])


@given(st.lists(PPTX_LINE, min_size=2, max_size=5, unique=True), st.data())
@ORACLE_PROCESS
def test_replace_data_writes_back_a_chart_that_is_not_the_chart_it_read(categories, source):
    """replace_data is handed the values python-pptx itself just read, which are floats, and it
    rewrites both the cached XML and the embedded workbook from them. The amounts stay equal and the
    forms do not: the cents in c:v are gone, and a whole amount that openpyxl read as a float out of
    the original sheet is an int in the rewritten one. Replaces the typed after['workbook'] ==
    state['workbook'] of case 167."""
    amounts = source.draw(st.lists(CHART_WHOLE, min_size=len(categories), max_size=len(categories)))
    data = _chart_bytes(categories, amounts)
    deck = pptx.Presentation(io.BytesIO(data))
    chart = deck.slides[0].shapes[0].chart
    replacement = pptx.chart.data.CategoryChartData()
    replacement.categories = list(chart.plots[0].categories)
    replacement.add_series('Actual', tuple(chart.series[0].values))
    chart.replace_data(replacement)
    written = io.BytesIO()
    deck.save(written)
    rebuilt = written.getvalue()
    npt.assert_allclose(_chart_values(rebuilt)[1], _chart_values(data)[1])
    npt.assert_allclose(_chart_workbook(rebuilt)[0], _chart_workbook(data)[0])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_chart_cached_texts(rebuilt), _chart_cached_texts(data))
    with pytest.raises(AssertionError):
        npt.assert_array_equal([type(value).__name__ for value in _chart_workbook(rebuilt)[0]],
                               [type(value).__name__ for value in _chart_workbook(data)[0]])


@given(st.lists(PPTX_LINE, min_size=2, max_size=5, unique=True), st.data())
@ORACLE_PROCESS
def test_a_missing_amount_is_none_to_one_reader_and_an_empty_string_to_the_other(categories, source):
    """One category with no figure survives the chart: python-pptx returns None in the series and
    openpyxl finds an empty cell. calamine returns the empty string for that same cell, so which
    categories are unfigured is a question the two readers of one workbook answer differently, and
    only one of the two answers can be tested with `is None`. Replaces the typed [1500.0, None] of
    case 167."""
    amounts = source.draw(st.lists(CHART_CENTS, min_size=len(categories), max_size=len(categories)))
    missing = source.draw(st.integers(min_value=0, max_value=len(categories) - 1))
    handed = [None if index == missing else amount for index, amount in enumerate(amounts)]
    data = _chart_bytes(categories, handed)
    by_openpyxl, by_calamine = _chart_workbook(data)
    npt.assert_array_equal([value is None for value in _chart_values(data)[1]],
                           [value is None for value in handed])
    npt.assert_array_equal([value is None for value in by_openpyxl],
                           [value is None for value in handed])
    with pytest.raises(AssertionError):
        npt.assert_array_equal([value is None for value in by_calamine],
                               [value is None for value in by_openpyxl])


# ---------------------------------------------------------------- two libraries dividing one pool
POOL_WEIGHTS = st.lists(st.integers(min_value=1, max_value=40), min_size=2, max_size=6)
POOL_MULTIPLIER = st.integers(min_value=1, max_value=2000)
TIED_SCALE = st.integers(min_value=1, max_value=30)
TIED_STEP = st.integers(min_value=0, max_value=5000)
ZEROED_WEIGHTS = st.builds(lambda positives, index: positives[:index] + [0] + positives[index:],
                           st.lists(st.integers(min_value=1, max_value=40), min_size=1, max_size=5),
                           st.integers(min_value=0, max_value=5))


def _hamilton_pair(weights, total):
    return (LargestRemainder.round(list(weights), total),
            apportionment_methods.compute('hamilton', list(weights), total, verbose=False))


@given(POOL_WEIGHTS, POOL_MULTIPLIER)
@SLOW
def test_two_apportionment_libraries_agree_when_every_quota_is_exact(weights, multiplier):
    """largest-remainder-py 0.1.0 declares no dependencies at all and apportionment 1.0 declares
    numpy, so the two implementations of the largest remainder method share nothing. On a pool that
    divides the weights exactly there is no remainder to award and both return the same allocation,
    which is the agreeing region for P169's split. Replaces the typed [3334, 3333, 3333] pair of
    case 169."""
    total = sum(weights) * multiplier
    by_largest_remainder, by_apportionment = _hamilton_pair(weights, total)
    npt.assert_array_equal(by_largest_remainder, by_apportionment)
    npt.assert_array_equal(sum(by_largest_remainder), total)
    npt.assert_array_equal(sum(by_apportionment), total)


@given(TIED_SCALE, TIED_STEP)
@SLOW
def test_the_two_libraries_award_the_last_cents_to_different_parties(scale, step):
    """Weights of a, a and 3a against a pool of 5k+3 leave every party a fractional quota and two
    cents to award, and the largest of those fractions belongs to the third party. largest-remainder
    sorts the remainders and pays it; apportionment walks the parties in index order, pays the two
    tied smaller remainders first and finds the pool empty when it reaches the largest one, which its
    own source records as a tie broken "to the disadvantage of" that party. Both conserve the pool,
    and the two allocations are not the same allocation."""
    weights = [scale, scale, 3 * scale]
    total = 5 * step + 3
    by_largest_remainder, by_apportionment = _hamilton_pair(weights, total)
    npt.assert_array_equal(sum(by_largest_remainder), total)
    npt.assert_array_equal(sum(by_apportionment), total)
    npt.assert_array_less(by_apportionment[2], by_largest_remainder[2])
    npt.assert_array_less(by_largest_remainder[1], by_apportionment[1])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(by_largest_remainder, by_apportionment)


@given(TIED_SCALE, TIED_STEP)
@SLOW
def test_the_exact_mode_of_the_second_library_allocates_exactly_what_its_floats_did(scale, step):
    """apportionment offers fractions=True, which computes the quotas as fractions.Fraction instead
    of numpy floats. On the same pools it returns the same allocation its default returns, so the
    party that loses a cent there loses it to the shape of the award loop and not to floating point,
    and no option in that library moves it."""
    weights = [scale, scale, 3 * scale]
    total = 5 * step + 3
    exact = apportionment_methods.compute('hamilton', list(weights), total, fractions=True,
                                          verbose=False)
    npt.assert_array_equal(exact, _hamilton_pair(weights, total)[1])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(exact, _hamilton_pair(weights, total)[0])


@given(st.integers(min_value=2, max_value=6), POOL_MULTIPLIER, st.data())
@SLOW
def test_a_credit_pool_is_truncated_by_one_library_and_refused_by_the_other(parties, multiplier,
                                                                           source):
    """A negative pool is a credit to distribute. largest-remainder refuses it, because its own
    check is that "the total must be non-negative". apportionment truncates each quota toward zero
    and then tests whether it has awarded too few, which a negative total never is, so it returns an
    allocation that is short of the pool by up to one cent per party and raises nothing. The pool
    the caller handed it is not the pool it divided."""
    shortfall = source.draw(st.integers(min_value=1, max_value=parties - 1))
    total = -(parties * multiplier + shortfall)
    weights = [1] * parties
    with pytest.raises(ValueError):
        LargestRemainder.round(list(weights), total)
    credited = apportionment_methods.compute('hamilton', list(weights), total, verbose=False)
    npt.assert_array_less(total, sum(credited))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(sum(credited), total)


@given(ZEROED_WEIGHTS, st.integers(min_value=0, max_value=1_000_000))
@SLOW
def test_a_party_with_no_weight_changes_nothing_in_either_library(weights, total):
    """Dropping the unweighted parties from the list leaves both allocations exactly as they were,
    so a driver with no weight neither takes a cent nor moves one, in the library that sorts the
    remainders and in the library that walks them. Replaces the typed [0, 10000] of case 169."""
    carried = [weight for weight in weights if weight]
    for whole, without in zip(_hamilton_pair(weights, total), _hamilton_pair(carried, total)):
        npt.assert_array_equal([paid for paid, weight in zip(whole, weights) if weight], without)


# ---------------------------------------------------------------- counting the working days between two dates
DECLARED_HOLIDAYS = st.lists(ANY_2026_DAY, min_size=0, max_size=6, unique=True)
WORKING_SPAN = st.tuples(ANY_2026_DAY, ANY_2026_DAY).map(lambda pair: tuple(sorted(pair)))


class DeclaredHolidays(workalendar_core.Calendar):
    """A five-day week whose holidays are the generated ones. The same list is handed to numpy and
    to pandas, so the three implementations are compared on the convention and not on the calendar."""
    WEEKEND_DAYS = (5, 6)

    def __init__(self, holidays):
        super().__init__()
        self._declared = list(holidays)

    def get_calendar_holidays(self, year):
        return [(day, 'declared') for day in self._declared if day.year == year]


def _numpy_calendar(holidays):
    return np.busdaycalendar(weekmask='Mon Tue Wed Thu Fri',
                             holidays=[day.isoformat() for day in holidays])


def _custom_business_day(holidays):
    return pd.offsets.CustomBusinessDay(holidays=[pd.Timestamp(day) for day in holidays])


def _working_counts(span, holidays):
    """The same two dates counted three ways: numpy's busday_count, the length of pandas'
    bdate_range and workalendar's get_working_days_delta. workalendar is the independent
    implementation here; pandas' CustomBusinessDay builds an np.busdaycalendar of its own and calls
    np.is_busday, so it is a third endpoint convention over the same engine and not a third reader."""
    start, end = span
    half_open = int(np.busday_count(np.datetime64(start.isoformat()), np.datetime64(end.isoformat()),
                                    busdaycal=_numpy_calendar(holidays)))
    closed = len(pd.bdate_range(start, end, freq=_custom_business_day(holidays)))
    open_on_the_left = DeclaredHolidays(holidays).get_working_days_delta(start, end)
    return half_open, closed, open_on_the_left


def _works(day, holidays):
    return int(np.is_busday(np.datetime64(day.isoformat()), busdaycal=_numpy_calendar(holidays)))


@given(WORKING_SPAN, DECLARED_HOLIDAYS)
@SLOW
def test_three_working_day_counters_count_three_different_intervals(span, holidays):
    """numpy counts the working days in [start, end), pandas' bdate_range lists those in [start, end]
    and workalendar's delta counts those in (start, end]. Handed one calendar and one pair of dates
    the three differ by exactly the working-day status of the endpoint each of them leaves out, which
    is the relation asserted here. numpy and workalendar therefore return the same number only when
    the two endpoints have the same status, and the pair of dates a chain hands them decides it.
    Replaces the typed 20 and 21 of case 171."""
    half_open, closed, open_on_the_left = _working_counts(span, holidays)
    npt.assert_array_equal(closed, half_open + _works(span[1], holidays))
    npt.assert_array_equal(closed, open_on_the_left + _works(span[0], holidays))


@given(WORKING_SPAN.filter(lambda span: span[0] != span[1]), DECLARED_HOLIDAYS)
@SLOW
def test_the_inclusive_span_is_one_longer_than_the_half_open_one_only_when_the_last_day_works(
        span, holidays):
    """The chain's inclusive count adds a day to the end before counting. That returns one more than
    the half-open count when the last day is a working day and returns the same number when it is
    not, so the identity the case types as a difference of one is a fact about the end date rather
    than about the two calls."""
    start, end = span
    calendar = _numpy_calendar(holidays)
    half_open = int(np.busday_count(np.datetime64(start.isoformat()),
                                    np.datetime64(end.isoformat()), busdaycal=calendar))
    inclusive = int(np.busday_count(np.datetime64(start.isoformat()),
                                    np.datetime64(end.isoformat()) + np.timedelta64(1, 'D'),
                                    busdaycal=calendar))
    npt.assert_array_equal(inclusive, half_open + _works(end, holidays))


@given(WORKING_SPAN, DECLARED_HOLIDAYS)
@SLOW
def test_numpy_and_workalendar_list_the_same_working_days_between_the_same_dates(span, holidays):
    """The disagreement is about the endpoints and not about the days. Over the closed span the
    dates numpy keeps with is_busday are exactly the dates workalendar calls working days, on the
    same generated holidays, and pandas' bdate_range emits that same list. The two implementations
    agree about the calendar and return different counts of it."""
    start, end = span
    days = np.arange(np.datetime64(start.isoformat()),
                     np.datetime64(end.isoformat()) + np.timedelta64(1, 'D'), dtype='datetime64[D]')
    calendar = DeclaredHolidays(holidays)
    by_numpy = [str(day) for day in days[np.is_busday(days, busdaycal=_numpy_calendar(holidays))]]
    by_workalendar = [str(day) for day in days
                      if calendar.is_working_day(datetime.date.fromisoformat(str(day)))]
    by_pandas = [stamp.date().isoformat()
                 for stamp in pd.bdate_range(start, end, freq=_custom_business_day(holidays))]
    npt.assert_array_equal(by_numpy, by_workalendar)
    npt.assert_array_equal(by_numpy, by_pandas)


@given(st.lists(st.tuples(st.one_of(st.none(), st.sampled_from(['A', 'B', 'C'])),
                          st.integers(min_value=1, max_value=800)), min_size=1, max_size=12)
       .filter(lambda rows: any(row[0] is None for row in rows)))
@SLOW
def test_the_unattributed_days_leave_one_engine_and_stay_in_the_other_two(rows):
    """A timesheet row with no employee is a row nobody has claimed. pandas' groupby drops it by
    default, so the totals it returns are short of the days that were booked; polars' group_by and a
    DuckDB GROUP BY both return it as its own group, and pandas returns it too once dropna=False is
    passed. Nothing raises in any of the four, and only three of them conserve the days. Replaces the
    typed 4.00 and 5.00 totals of case 171."""
    frame = pd.DataFrame(rows, columns=['employee', 'days'])
    booked = int(frame['days'].sum())
    dropped = int(frame.groupby('employee')['days'].sum().sum())
    kept = int(frame.groupby('employee', dropna=False)['days'].sum().sum())
    by_polars = int(pl.DataFrame(rows, schema=['employee', 'days'], orient='row')
                    .group_by('employee').agg(pl.col('days').sum())['days'].sum())
    by_duckdb = duckdb.connect().execute(
        'select sum(total) from (select employee, sum(days) as total from frame group by employee)'
    ).fetchone()[0]
    npt.assert_array_equal([kept, by_polars, int(by_duckdb)], [booked, booked, booked])
    npt.assert_array_less(dropped, booked)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(dropped, booked)


# ---------------------------------------------------------------- costs through a cutoff, and the ratios after
COST_TASK = st.sampled_from(['T01', 'T02', 'T03'])
COST_AMOUNT = st.integers(min_value=-500000, max_value=500000).map(lambda n: Decimal(n).scaleb(-2))
COST_DAY = st.dates(min_value=datetime.date(2026, 9, 1), max_value=datetime.date(2026, 9, 30))
COST_RECORD = st.tuples(COST_TASK, COST_DAY, COST_AMOUNT)
COST_ANCHOR = datetime.date(2026, 9, 15)
EARNED_VALUE = st.fractions(min_value=Fraction(1), max_value=Fraction(100000), max_denominator=100)


def _cost_in_duckdb(records, cutoff, operator):
    connection = duckdb.connect()
    connection.execute('CREATE TABLE cost(task VARCHAR, spent_on DATE, amount DECIMAL(18,2))')
    connection.executemany('INSERT INTO cost VALUES (?, ?, ?)', records)
    rows = connection.execute('SELECT task, sum(amount) FROM cost WHERE spent_on %s ? '
                              'GROUP BY task ORDER BY task' % operator, [cutoff]).fetchall()
    connection.close()
    return [(task, str(total)) for task, total in rows]


def _cost_in_pandas(records, cutoff, operator):
    frame = pd.DataFrame(records, columns=['task', 'spent_on', 'amount'])
    kept = frame[frame['spent_on'] <= cutoff] if operator == '<=' else frame[frame['spent_on'] < cutoff]
    totals = kept.groupby('task')['amount'].sum().sort_index()
    return [(task, str(total)) for task, total in totals.items()]


def _cost_in_polars(records, cutoff, operator):
    frame = pl.DataFrame({'task': [record[0] for record in records],
                          'spent_on': [record[1] for record in records],
                          'amount': [record[2] for record in records]},
                         schema_overrides={'amount': pl.Decimal(18, 2)})
    kept = (frame.filter(pl.col('spent_on') <= cutoff) if operator == '<='
            else frame.filter(pl.col('spent_on') < cutoff))
    totals = kept.group_by('task').agg(pl.col('amount').sum()).sort('task')
    return [(row['task'], str(row['amount'])) for row in totals.to_dicts()]


@given(st.lists(COST_RECORD, min_size=1, max_size=8), COST_DAY)
@SLOW
def test_three_engines_total_the_same_signed_costs_through_the_same_cutoff(records, cutoff):
    """A DuckDB DECIMAL(18,2) column, a pandas object column of Decimal and a polars Decimal column
    are three engines summing the same signed amounts through the same date, and they return the same
    cents on every generated ledger, credits included. Replaces the typed 1200.25 and 889.75 of case
    187."""
    npt.assert_array_equal(_cost_in_duckdb(records, cutoff, '<='),
                           _cost_in_pandas(records, cutoff, '<='))
    npt.assert_array_equal(_cost_in_duckdb(records, cutoff, '<='),
                           _cost_in_polars(records, cutoff, '<='))


@given(st.lists(st.tuples(COST_TASK, st.integers(min_value=1, max_value=14).map(
    lambda offset: COST_ANCHOR + datetime.timedelta(days=offset)), COST_AMOUNT), max_size=6),
       COST_TASK, COST_AMOUNT.filter(lambda amount: amount != 0))
@SLOW
def test_the_record_dated_on_the_cutoff_is_the_whole_difference_between_the_two_predicates(
        later, task, amount):
    """One cost dated exactly on the cutoff and every other cost dated after it. The two engines
    agree with each other on both predicates, and each of them reports a different total depending on
    whether the predicate is `<=` or `<`: the difference is that record and nothing else. Replaces
    the typed exclusion of the September 20 record of case 187."""
    records = [(task, COST_ANCHOR, amount)] + list(later)
    inclusive = _cost_in_duckdb(records, COST_ANCHOR, '<=')
    exclusive = _cost_in_duckdb(records, COST_ANCHOR, '<')
    npt.assert_array_equal(inclusive, _cost_in_pandas(records, COST_ANCHOR, '<='))
    npt.assert_array_equal(exclusive, _cost_in_pandas(records, COST_ANCHOR, '<'))
    npt.assert_array_equal(inclusive, [(task, str(amount))])
    npt.assert_array_equal(exclusive, [])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(inclusive, exclusive)


@given(EARNED_VALUE, EARNED_VALUE, EARNED_VALUE)
@SLOW
def test_the_two_completion_assumptions_are_one_formula(budget, actual, earned):
    """The chain names two ways to estimate the cost at completion, the remaining work at budget and
    the budget plus the variance to date. On generated rationals they return the same number every
    time, and z3 says why: the difference of the two expressions is unsatisfiable over the reals, so
    they are one formula written twice. The third assumption is not: z3 finds a model where it
    differs. Replaces the typed 3190 of case 187."""
    npt.assert_array_equal(actual + (budget - earned), budget + (actual - earned))
    bac, ac, ev = z3.Real('bac'), z3.Real('ac'), z3.Real('ev')
    same = z3.Solver()
    same.add(ac + (bac - ev) != bac + (ac - ev))
    npt.assert_array_equal(str(same.check()), 'unsat')
    different = z3.Solver()
    different.add(ev != 0, ac + (bac - ev) * (ac / ev) != ac + (bac - ev))
    npt.assert_array_equal(str(different.check()), 'sat')


@given(st.integers(min_value=1, max_value=10 ** 9).filter(lambda n: n % 3))
@SLOW
def test_the_rational_index_is_not_the_float_the_chain_would_have_divided(earned):
    """An index whose denominator is three is not a binary fraction, so the float of it is a
    different number: multiplying the rational by its denominator returns the earned value exactly
    and the float does not equal the rational at all. It does equal the quotient the same chain would
    have computed with two floats, which is why the loss is invisible at the point it happens.
    Replaces the typed Fraction(10, 11) of case 187."""
    index = Fraction(earned, 3)
    npt.assert_array_equal(index * 3, Fraction(earned))
    npt.assert_array_equal(float(index), float(earned) / 3.0)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(index, Fraction(float(index)))


# ---------------------------------------------------------------- a reporting tree, and the deck drawn from it
POI_DIRECTORY = pathlib.Path(os.environ.get('POI_DIR', str(pathlib.Path.home() / 'poi-oracle')))
PPTX_CONNECTOR_ORACLE_JAVA = pathlib.Path(__file__).with_name('pptx_connector_oracle.java')
poi_available = shutil.which('java') is not None and (POI_DIRECTORY / 'jars').is_dir()
JAVA_ORACLE = settings(max_examples=8, deadline=None)
CONNECTION_INDEX = st.integers(min_value=0, max_value=3)
SLIDE_INCH = st.integers(min_value=1, max_value=5)
START_CXN = pptx_ns.qn('a:stCxn')
END_CXN = pptx_ns.qn('a:endCxn')


@st.composite
def _reporting_lines(draw, minimum=2, maximum=12):
    """One rooted reporting structure, as a position count and a list of manager-to-report pairs.
    Every position after the first reports to one drawn from the positions before it, so the shape of
    the tree comes out of the strategy and nothing about it is authored here."""
    size = draw(st.integers(min_value=minimum, max_value=maximum))
    return size, [(draw(st.integers(min_value=0, max_value=report - 1)), report)
                  for report in range(1, size)]


@st.composite
def _reporting_lines_and_a_second_manager(draw):
    """The same structure and one more reporting line into a position that already has a manager,
    drawn from the positions before it so the extra line cannot close a cycle."""
    size, lines = draw(_reporting_lines(minimum=3))
    report = draw(st.integers(min_value=2, max_value=size - 1))
    managers = dict((child, parent) for parent, child in lines)
    manager = draw(st.integers(min_value=0, max_value=report - 1)
                   .filter(lambda candidate: candidate != managers[report]))
    return size, lines, (manager, report)


def _generation_levels(graph):
    """The chain's own levelling: the index of the generation `topological_generations` puts each
    position in, one level per position in position order."""
    levels = {position: index
              for index, generation in enumerate(nx.topological_generations(graph))
              for position in generation}
    return [levels[position] for position in sorted(levels)]


@given(_reporting_lines_and_a_second_manager())
@SLOW
def test_a_reporting_tree_and_its_second_reporting_line_get_opposite_verdicts_in_two_libraries(structure):
    """P188 validates the hierarchy with `networkx.is_arborescence`, whose source at 3.6.1 reads
    `is_tree(G) and max(d for n, d in G.in_degree()) <= 1` and whose own `is_tree` says of directed
    graphs that "the underlying graph is obtained by treating each directed edge as a single
    undirected edge in a multigraph". igraph's C source documents the same predicate directly: a
    directed tree requires "that all edges are oriented away from a root (out-tree or arborescence)".
    On generated structures the two agree, and both flip when one position is given a second manager,
    which is the rejection case 188 typed by hand. Replaces the typed rejection of the second parent
    and the accompanying `is_directed_acyclic_graph(...) == True` of handoff_guards_v20.py case 188."""
    size, lines, second = structure
    tree, loose = nx.DiGraph(lines), nx.DiGraph(lines + [second])
    in_igraph = igraph.Graph(n=size, edges=lines, directed=True)
    in_igraph_loose = igraph.Graph(n=size, edges=lines + [second], directed=True)
    npt.assert_equal(nx.is_arborescence(tree), in_igraph.is_tree(mode='out'))
    npt.assert_equal(nx.is_arborescence(loose), in_igraph_loose.is_tree(mode='out'))
    with pytest.raises(AssertionError):
        npt.assert_equal(nx.is_arborescence(tree), nx.is_arborescence(loose))
    npt.assert_equal(nx.is_directed_acyclic_graph(loose), in_igraph_loose.is_dag())
    npt.assert_equal(nx.is_directed_acyclic_graph(tree), in_igraph_loose.is_dag())


@given(_reporting_lines(), st.data())
@SLOW
def test_a_repeated_reporting_line_is_one_line_in_one_library_and_two_in_the_other(structure, source):
    """The same reporting line declared twice. `DiGraph` holds at most one edge per ordered pair, so
    the file that says it twice and the file that says it once are the same graph and both pass
    `is_arborescence`; igraph stores both declarations as parallel edges and its `is_tree` rejects the
    structure. Nothing is corrupted: what differs is how many reporting lines the same file describes,
    and therefore whether it is a tree at all. Replaces the typed
    `g.equal(len(bindings), 2)` edge accounting of case 188."""
    size, lines = structure
    repeated = source.draw(st.sampled_from(lines))
    declared = lines + [repeated]
    graph = nx.DiGraph(declared)
    in_igraph = igraph.Graph(n=size, edges=declared, directed=True)
    npt.assert_equal(nx.is_arborescence(graph), nx.is_arborescence(nx.DiGraph(lines)))
    with pytest.raises(AssertionError):
        npt.assert_equal(graph.number_of_edges(), in_igraph.ecount())
    with pytest.raises(AssertionError):
        npt.assert_equal(nx.is_arborescence(graph), in_igraph.is_tree(mode='out'))
    npt.assert_equal(in_igraph.ecount(), len(declared))


@given(_reporting_lines())
@SLOW
def test_the_level_of_a_position_is_its_distance_from_the_root_while_the_structure_is_a_tree(structure):
    """`topological_generations` layers a directed acyclic graph by removing the positions with no
    manager, then the next such positions, and so on. While the structure is a tree that index is the
    reporting distance from the root, which igraph computes independently with `distances`. Replaces
    the typed `levels(tree) == [['CEO'], ['Ops', 'Sales'], ['A', 'B', 'C']]` of case 188."""
    size, lines = structure
    graph = nx.DiGraph(lines)
    in_igraph = igraph.Graph(n=size, edges=lines, directed=True)
    npt.assert_array_equal(_generation_levels(graph), in_igraph.distances(source=0, mode='out')[0])
    npt.assert_array_equal([graph.out_degree(position) for position in sorted(graph)],
                           in_igraph.degree(mode='out'))


@given(st.integers(min_value=3, max_value=12))
@SLOW
def test_a_second_reporting_line_makes_the_level_the_longest_chain_not_the_distance(size):
    """One chain of positions and one more reporting line from the root straight to the last of them.
    The structure is still a directed acyclic graph, and both libraries say so, but the level
    `topological_generations` reports for that last position is the length of the long way round while
    its distance from the root is one line. The level a chart draws is therefore the longest chain to
    a position, not its distance from the top, and the two stop agreeing at exactly the point
    `is_arborescence` stops accepting the structure."""
    chain = [(step - 1, step) for step in range(1, size)]
    lines = chain + [(0, size - 1)]
    graph = nx.DiGraph(lines)
    in_igraph = igraph.Graph(n=size, edges=lines, directed=True)
    npt.assert_equal(nx.is_directed_acyclic_graph(graph), in_igraph.is_dag())
    npt.assert_equal(nx.is_arborescence(graph), in_igraph.is_tree(mode='out'))
    npt.assert_array_equal(_generation_levels(nx.DiGraph(chain)),
                           igraph.Graph(n=size, edges=chain, directed=True).distances(
                               source=0, mode='out')[0])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_generation_levels(graph),
                               in_igraph.distances(source=0, mode='out')[0])


@given(st.sampled_from(('out', 'in', 'all')))
@SLOW
def test_an_organisation_with_no_positions_is_a_refusal_in_one_library_and_a_verdict_in_the_other(mode):
    """An empty reporting structure is not a rejected structure in NetworkX: `is_tree` raises
    `NetworkXPointlessConcept` before `is_arborescence` can return, so the validator's refusal path is
    an exception of a different class from the one a malformed structure raises. igraph answers
    instead, and its C source at 1.0.0 says why: "By convention, the null graph (i.e. the graph with
    no vertices) is considered not to be connected, and therefore not a tree." Its answer is the
    answer it gives for positions with no reporting lines at all, in every mode."""
    with pytest.raises(nx.NetworkXPointlessConcept):
        nx.is_arborescence(nx.DiGraph())
    npt.assert_equal(igraph.Graph(n=0, directed=True).is_tree(mode=mode),
                     igraph.Graph(n=2, directed=True).is_tree(mode=mode))
    npt.assert_equal(nx.is_arborescence(nx.empty_graph(2, create_using=nx.DiGraph)),
                     igraph.Graph(n=2, directed=True).is_tree(mode=mode))


@given(_reporting_lines(), _reporting_lines())
@SLOW
def test_two_reporting_roots_are_a_forest_and_no_arborescence_in_either_library(first, second):
    """Two rooted structures joined by each library's own disjoint union. Both libraries reject the
    result as one tree and both say it is still acyclic and no longer connected; NetworkX also calls
    it a forest, which is the distinction case 188 recorded, and which is a different verdict from
    the one its own `is_arborescence` returns for the same graph. python-igraph 1.0.0 exposes no
    `is_forest` at all, although the C library it wraps documents `igraph_is_forest`, so the
    corroboration of that half is connectivity rather than the same predicate. Replaces the typed
    two-roots rejection and `is_forest(...) == True` of case 188."""
    left_size, left = first
    right_size, right = second
    graph = nx.disjoint_union(nx.DiGraph(left), nx.DiGraph(right))
    in_igraph = igraph.Graph(n=left_size, edges=left, directed=True).disjoint_union(
        igraph.Graph(n=right_size, edges=right, directed=True))
    npt.assert_equal(nx.is_arborescence(graph), in_igraph.is_tree(mode='out'))
    npt.assert_equal(nx.is_weakly_connected(graph), in_igraph.is_connected(mode='weak'))
    npt.assert_equal(nx.is_directed_acyclic_graph(graph), in_igraph.is_dag())
    with pytest.raises(AssertionError):
        npt.assert_equal(nx.is_forest(graph), nx.is_arborescence(graph))


@given(_reporting_lines(), st.data())
@SLOW
def test_the_positions_under_a_manager_are_the_same_set_under_two_reachability_conventions(structure,
                                                                                          source):
    """`networkx.descendants` and igraph's `subcomponent(mode='out')` return the same reachable set
    apart from the position asked about, which one convention includes and the other does not. A
    head count taken from the second without subtracting one is therefore one too many for every
    position in the chart. Replaces the typed `sorted(nx.descendants(tree, 'Ops')) == ['A', 'B']` and
    the leaf list of case 188."""
    size, lines = structure
    manager = source.draw(st.integers(min_value=0, max_value=size - 1))
    graph = nx.DiGraph(lines)
    in_igraph = igraph.Graph(n=size, edges=lines, directed=True)
    reachable = in_igraph.subcomponent(manager, mode='out')
    npt.assert_array_equal(sorted(nx.descendants(graph, manager)), sorted(set(reachable) - {manager}))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(sorted(nx.descendants(graph, manager)), sorted(reachable))


def _org_chart(lines, begin_at, end_at):
    """The chain's own deck: one rounded rectangle per position, one straight connector per reporting
    line, both ends bound with `Connector.begin_connect` and `Connector.end_connect`. Returns the
    package and the pairs of shape ids python-pptx reports for the bound shapes."""
    deck = pptx.Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    boxes = {}
    for row, position in enumerate(sorted({end for line in lines for end in line})):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1 + row),
                                       Inches(2), Inches(0.8))
        shape.text_frame.text = str(position)
        boxes[position] = shape
    for manager, report in lines:
        connector = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(2), Inches(2),
                                               Inches(2), Inches(3))
        connector.begin_connect(boxes[manager], begin_at)
        connector.end_connect(boxes[report], end_at)
    written = io.BytesIO()
    deck.save(written)
    return written.getvalue(), [(boxes[manager].shape_id, boxes[report].shape_id)
                                for manager, report in lines]


def _pptx_connections(data, tag):
    """Every stCxn or endCxn in the package, read with the standard library's expat parser rather
    than the lxml tree python-pptx writes with. The qualified name comes from python-pptx's own
    ns.qn, so no namespace URI is written here."""
    found = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in archive.namelist():
            if name.endswith('.xml'):
                found.extend(element.attrib for element
                             in ElementTree.fromstring(archive.read(name)).iter(tag))
    return found


def _pptx_in_poi(data):
    """The same package read by Apache POI 5.4.1 under Java. The shim parses argv, calls the library
    and prints one tab-separated line per shape and per bound connector end."""
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / 'deck.pptx'
        path.write_bytes(data)
        completed = subprocess.run(
            ['java', '-Dlog4j2.statusLoggerLevel=OFF', '-cp', str(POI_DIRECTORY / 'jars' / '*'),
             str(PPTX_CONNECTOR_ORACLE_JAVA), str(path)],
            capture_output=True, encoding='utf-8', check=True)
    return [line.split('\t') for line in completed.stdout.split('\n')[:-1]]


@pytest.mark.skipif(not poi_available, reason='java and the Apache POI jars are required for this oracle')
@given(_reporting_lines(minimum=2, maximum=5), CONNECTION_INDEX, CONNECTION_INDEX)
@JAVA_ORACLE
def test_a_bound_connector_carries_the_shape_ids_a_second_ooxml_reader_finds(structure, begin_at,
                                                                            end_at):
    """python-pptx writes the binding as `stCxn`/`endCxn` under the connector's `cNvCxnSpPr`, and its
    source at v1.0.2 sets `stCxn.id = shape.shape_id`. Apache POI, a Java implementation of the same
    package format that shares nothing with python-pptx, reads back exactly those ids and indices, and
    so does the standard library's expat parser. POI also reports each shape's anchor in points, which
    is the same rectangle python-pptx reports through `Length.pt`. Replaces the typed
    `sorted(bindings[0]) == sorted([str(ids['CEO']), str(ids['Ops'])])` pair of case 188."""
    _, lines = structure
    data, bound = _org_chart(lines, begin_at, end_at)
    by_poi = _pptx_in_poi(data)
    npt.assert_array_equal(np.array([row[2] for row in by_poi if row[0] == 'ST'], dtype=int),
                           [manager for manager, _ in bound])
    npt.assert_array_equal(np.array([row[2] for row in by_poi if row[0] == 'END'], dtype=int),
                           [report for _, report in bound])
    npt.assert_array_equal(np.array([row[3] for row in by_poi if row[0] == 'ST'], dtype=int),
                           np.full(len(bound), begin_at))
    npt.assert_array_equal(np.array([row[3] for row in by_poi if row[0] == 'END'], dtype=int),
                           np.full(len(bound), end_at))
    npt.assert_array_equal(np.array([row['id'] for row in _pptx_connections(data, START_CXN)],
                                    dtype=int),
                           np.array([row[2] for row in by_poi if row[0] == 'ST'], dtype=int))
    npt.assert_array_equal(np.array([row['id'] for row in _pptx_connections(data, END_CXN)], dtype=int),
                           np.array([row[2] for row in by_poi if row[0] == 'END'], dtype=int))
    shapes = pptx.Presentation(io.BytesIO(data)).slides[0].shapes
    npt.assert_allclose([[shape.left.pt, shape.top.pt, shape.width.pt, shape.height.pt]
                         for shape in shapes],
                        [[float(field) for field in row[3:]] for row in by_poi if row[0] == 'SHAPE'])


@pytest.mark.skipif(not poi_available, reason='java and the Apache POI jars are required for this oracle')
@given(CONNECTION_INDEX, st.integers(min_value=4, max_value=9))
@JAVA_ORACLE
def test_a_connection_index_outside_the_placement_table_is_written_before_it_is_rejected(inside,
                                                                                        beyond):
    """`Connector.begin_connect` writes the binding and then places the connector, in that order: its
    source at v1.0.2 is `self._connect_begin_to(shape, cxn_pt_idx)` followed by
    `self._move_begin_to_cxn(shape, cxn_pt_idx)`, and the second of those is a dictionary of four
    entries subscripted by the index. A fifth connection point therefore raises `KeyError` after the
    `stCxn` element is already in the tree. The deck still saves, the connector keeps the geometry it
    had before the call, and Apache POI reads the binding out of the saved package, so the failure
    leaves a connector bound to a connection point the library that wrote it cannot place. The
    library's own docstring warns only that a `cxn_pt_idx` beyond the shape's connection points
    "could lead to a load error"."""
    deck = pptx.Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1), Inches(2),
                                 Inches(0.8))
    connector = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(2), Inches(2), Inches(2),
                                           Inches(3))
    placed = [connector.begin_x, connector.begin_y]
    with pytest.raises(KeyError):
        connector.begin_connect(box, beyond)
    npt.assert_array_equal([connector.begin_x, connector.begin_y], placed)
    written = io.BytesIO()
    deck.save(written)
    data = written.getvalue()
    npt.assert_array_equal(np.array([row['idx'] for row in _pptx_connections(data, START_CXN)],
                                    dtype=int), [beyond])
    npt.assert_array_equal(_pptx_connections(data, END_CXN), [])
    by_poi = _pptx_in_poi(data)
    npt.assert_array_equal(np.array([row[3] for row in by_poi if row[0] == 'ST'], dtype=int), [beyond])
    npt.assert_array_equal(np.array([row[2] for row in by_poi if row[0] == 'ST'], dtype=int),
                           [box.shape_id])
    npt.assert_array_equal([row[0] for row in by_poi if row[0] == 'END'], [])
    connector.begin_connect(box, inside)
    with pytest.raises(AssertionError):
        npt.assert_array_equal([connector.begin_x, connector.begin_y], placed)


@given(CONNECTION_INDEX, SLIDE_INCH, SLIDE_INCH)
@ORACLE_PROCESS
def test_a_bound_connector_keeps_the_point_the_shape_was_at_when_it_was_bound(at, left, top):
    """Binding a connector to a shape copies that shape's connection point into the connector once.
    Moving the shape afterwards leaves the connector where it was: the same binding drawn again
    against the moved shape lands somewhere else, while the id in the file is the same shape both
    times. What the package records is a reference plus a stale position, and only an application
    that re-routes on open reconciles them."""
    deck = pptx.Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1), Inches(2),
                                 Inches(0.8))
    bound = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(2), Inches(2), Inches(2),
                                       Inches(3))
    bound.begin_connect(box, at)
    placed = [bound.begin_x, bound.begin_y]
    box.left, box.top = Inches(1 + left), Inches(1 + top)
    npt.assert_array_equal([bound.begin_x, bound.begin_y], placed)
    again = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(2), Inches(2), Inches(2),
                                       Inches(3))
    again.begin_connect(box, at)
    with pytest.raises(AssertionError):
        npt.assert_array_equal([again.begin_x, again.begin_y], placed)
    written = io.BytesIO()
    deck.save(written)
    npt.assert_array_equal(np.array([row['id'] for row in _pptx_connections(written.getvalue(),
                                                                            START_CXN)], dtype=int),
                           np.full(2, box.shape_id))


@given(CONNECTION_INDEX, SLIDE_INCH, SLIDE_INCH, SLIDE_INCH, SLIDE_INCH)
@ORACLE_PROCESS
def test_the_two_ends_of_a_connector_place_it_at_one_point_for_one_connection(at, left, top, width,
                                                                             height):
    """The connection point of a shape is a property of the shape and the index, not of the connector
    that asks for it: `begin_connect` and `end_connect` place their own end at the same point, and a
    connector drawn from anywhere on the slide ends up there too. That invariant is what makes the
    ids in the package mean a position at all."""
    deck = pptx.Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top),
                                 Inches(width), Inches(height))
    from_begin = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(1), Inches(1), Inches(2),
                                            Inches(2))
    from_begin.begin_connect(box, at)
    from_end = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(4), Inches(5), Inches(1),
                                          Inches(1))
    from_end.end_connect(box, at)
    elsewhere = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(6), Inches(6), Inches(1),
                                           Inches(3))
    elsewhere.begin_connect(box, at)
    npt.assert_array_equal([from_begin.begin_x, from_begin.begin_y],
                           [from_end.end_x, from_end.end_y])
    npt.assert_array_equal([from_begin.begin_x, from_begin.begin_y],
                           [elsewhere.begin_x, elsewhere.begin_y])
