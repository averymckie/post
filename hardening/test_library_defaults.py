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
import difflib
import functools
import hashlib
import hmac
import operator
import os
import pathlib
import shutil
import struct
import tempfile
import subprocess
import unicodedata
import datetime
import inspect
import io
import zipfile
import zoneinfo
from xml.etree import ElementTree
from typing import Literal
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
import cv2
from beancount import loader as beancount_loader
from beancount.core import data as beancount_data
import docx
import duckdb
import icalendar
from dateutil import rrule, tz as dateutil_tz
from dateutil.relativedelta import relativedelta
from fontTools.ttLib import TTFont
import numpy as np
import numpy_financial as npf
import pyxirr
from workalendar import core as workalendar_core
import html5lib
import igraph
import jinja2
import jsonschema
import markdown as python_markdown
import pint
import portion
import unyt
import regex
import tantivy
import rfc3986
import z3
import clingo
from cvc5 import pythonic as cvc5_pythonic
import pydantic
import pyshacl
import rdflib
from lxml import etree as lxml_etree
from lxml import html as lxml_html
from markdown_it import MarkdownIt
import matplotlib

matplotlib.use('Agg')  # the shim-free backend, so the chart tests draw without a display
import matplotlib.dates as matplotlib_dates
import matplotlib.font_manager as matplotlib_font_manager
import matplotlib.pyplot as matplotlib_pyplot
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
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
import repro_zipfile
import xlsxwriter
import xlsxwriter.exceptions
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
import segno
import scipy.sparse as scipy_sparse
import zxingcpp
import scipy.sparse.linalg as scipy_linsolve
from scipy.sparse.linalg import spsolve as scipy_spsolve
import polars.testing as plt
import pytest
import rapidfuzz.distance.DamerauLevenshtein as rf_damerau
import rapidfuzz.distance.Levenshtein as rf_levenshtein
import rapidfuzz.distance.OSA as rf_osa
import rapidfuzz.process as rf_process
from unittest import mock

from hypothesis import assume, given, settings, strategies as st
from hypothesis.extra import numpy as hyp_np
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


# ---------------------------------------------------------------- bookings, and what overlapping means
GUAVA_DIRECTORY = pathlib.Path(os.environ.get('GUAVA_DIR', str(pathlib.Path.home() / 'guava-oracle')))
INTERVAL_OVERLAP_ORACLE_JAVA = pathlib.Path(__file__).with_name('interval_overlap_oracle.java')
guava_available = shutil.which('java') is not None and (GUAVA_DIRECTORY / 'jars').is_dir()
CLOSURE = st.sampled_from(('both', 'left', 'right', 'neither'))
BOOKING_ANCHOR = pd.Timestamp('2026-09-23', tz='UTC')
BOOKING_HOUR = st.integers(min_value=0, max_value=20)
BOOKING_LENGTH = st.integers(min_value=1, max_value=3)
PORTION_CLOSURES = {'both': portion.closed, 'left': portion.closedopen,
                    'right': portion.openclosed, 'neither': portion.open}


def _booking(hour, length, closed):
    """One booking as P180 builds them: a pandas Interval between two UTC timestamps with a declared
    closure."""
    start = BOOKING_ANCHOR + pd.Timedelta(hours=hour)
    return pd.Interval(start, start + pd.Timedelta(hours=length), closed=closed)


def _in_portion(booking):
    """The same two endpoints and the same closure in portion 2.6.2, whose only declared dependency
    is sortedcontainers, so none of pandas is under it."""
    return PORTION_CLOSURES[booking.closed](booking.left, booking.right)


def _in_guava(pairs):
    """The same pairs of endpoints as Guava ranges under Java: for each pair, whether Guava calls the
    two ranges connected and whether their intersection is non-empty. The shim parses argv, calls the
    library and prints; the endpoints crossing to it are Timestamp.value, the nanoseconds pandas
    itself stores."""
    arguments = []
    for first, second in pairs:
        for booking in (first, second):
            arguments += [str(booking.left.value), str(booking.right.value), booking.closed]
    completed = subprocess.run(['java', '-cp', str(GUAVA_DIRECTORY / 'jars' / '*'),
                                str(INTERVAL_OVERLAP_ORACLE_JAVA)] + arguments,
                               capture_output=True, encoding='utf-8', check=True)
    printed = completed.stdout.split('\n')[:-1]
    return [(printed[at] == 'true', printed[at + 1] == 'true')
            for at in range(0, len(printed), 2)]


@pytest.mark.skipif(not guava_available, reason='java and the Guava jars are required for this oracle')
@given(BOOKING_HOUR, BOOKING_LENGTH, CLOSURE, BOOKING_HOUR, BOOKING_LENGTH, CLOSURE)
@JAVA_ORACLE
def test_three_implementations_agree_on_whether_two_bookings_overlap(hour, length, closed,
                                                                    other_hour, other_length,
                                                                    other_closed):
    """P180 detects conflicting bookings with pandas.Interval.overlaps, documented at v2.2.3 as "Two
    intervals overlap if they share a common point, including closed endpoints. Intervals that only
    have an open endpoint in common do not overlap." Two independent implementations of the same
    relation say the same thing on generated bookings under every combination of the four closures:
    portion 2.6.2, which defines overlaps as "if their intersection is non-empty", and Guava
    33.7.1-jre under Java, whose Range answers it as a connected pair with a non-empty
    intersection."""
    first = _booking(hour, length, closed)
    second = _booking(other_hour, other_length, other_closed)
    npt.assert_equal(first.overlaps(second), _in_portion(first).overlaps(_in_portion(second)))
    npt.assert_equal(first.overlaps(second), _in_guava([(first, second)])[0][1])


@pytest.mark.skipif(not guava_available, reason='java and the Guava jars are required for this oracle')
@given(BOOKING_HOUR, BOOKING_LENGTH, BOOKING_LENGTH, st.integers(min_value=1, max_value=3))
@JAVA_ORACLE
def test_a_handover_and_a_gap_are_one_answer_from_the_interval_and_two_from_the_others(hour, length,
                                                                                      next_length,
                                                                                      gap):
    """A booking that starts exactly when another ends, and a booking that starts hours later, are
    the same answer from pandas: neither overlaps. Both other libraries have a word for the first and
    not for the second. portion calls them adjacent, "if they do not overlap and their union form a
    single atomic interval"; Guava calls them connected, and its own documentation gives this very
    case: "[2, 4) and [4, 6) are connected, because both enclose the empty range [4, 4)". A roster
    built on overlaps alone cannot tell a handover from an empty hour, and P180's coverage gaps are
    exactly that distinction."""
    first = _booking(hour, length, 'left')
    handover = _booking(hour + length, next_length, 'left')
    apart = _booking(hour + length + gap, next_length, 'left')
    npt.assert_equal(first.overlaps(handover), first.overlaps(apart))
    (handover_connected, handover_intersects), (apart_connected, apart_intersects) = _in_guava(
        [(first, handover), (first, apart)])
    npt.assert_equal(_in_portion(first).adjacent(_in_portion(handover)),
                     handover_connected and not handover_intersects)
    npt.assert_equal(_in_portion(first).adjacent(_in_portion(apart)),
                     apart_connected and not apart_intersects)
    with pytest.raises(AssertionError):
        npt.assert_equal(_in_portion(first).adjacent(_in_portion(handover)),
                         _in_portion(first).adjacent(_in_portion(apart)))
    with pytest.raises(AssertionError):
        npt.assert_equal(handover_connected, apart_connected)


@pytest.mark.skipif(not guava_available, reason='java and the Guava jars are required for this oracle')
@given(BOOKING_HOUR, BOOKING_LENGTH, BOOKING_LENGTH)
@JAVA_ORACLE
def test_the_same_two_clock_times_conflict_or_not_according_to_the_declared_closure(hour, length,
                                                                                   next_length):
    """The four timestamps are the same in both pairs and only the declared closure differs: under
    the start-inclusive, end-exclusive reading P180 declares, a booking ending when another starts is
    not a conflict, and under closed-on-both-ends it is. All three libraries agree on each reading
    separately and therefore reproduce the contradiction rather than resolve it. Replaces the typed
    `desk.overlaps(later) == False` and `both_desk.overlaps(both_later) == True` of
    handoff_guards_v19.py case 180."""
    left_first, left_second = _booking(hour, length, 'left'), _booking(hour + length, next_length,
                                                                      'left')
    both_first, both_second = _booking(hour, length, 'both'), _booking(hour + length, next_length,
                                                                      'both')
    npt.assert_array_equal([left_first.left, left_first.right, left_second.left, left_second.right],
                           [both_first.left, both_first.right, both_second.left, both_second.right])
    pairs = _in_guava([(left_first, left_second), (both_first, both_second)])
    npt.assert_equal(left_first.overlaps(left_second), pairs[0][1])
    npt.assert_equal(both_first.overlaps(both_second), pairs[1][1])
    npt.assert_equal(left_first.overlaps(left_second),
                     _in_portion(left_first).overlaps(_in_portion(left_second)))
    npt.assert_equal(both_first.overlaps(both_second),
                     _in_portion(both_first).overlaps(_in_portion(both_second)))
    with pytest.raises(AssertionError):
        npt.assert_equal(left_first.overlaps(left_second), both_first.overlaps(both_second))


@pytest.mark.skipif(not guava_available, reason='java and the Guava jars are required for this oracle')
@given(BOOKING_HOUR, BOOKING_LENGTH, BOOKING_LENGTH)
@JAVA_ORACLE
def test_two_bookings_with_different_closures_are_compared_without_an_error(hour, length,
                                                                           next_length):
    """Nothing in any of the three libraries objects to comparing a booking closed on the right with
    one closed on the left, and the shared endpoint belongs to both, so the pair conflicts where the
    same clock times under the declared closure do not. A roster assembled from records whose
    closures were set in different places therefore answers, and answers differently, without
    anything to show that the two were built by different rules. Replaces the typed
    `right_desk.overlaps(later) == True` of case 180."""
    right_first = _booking(hour, length, 'right')
    left_first = _booking(hour, length, 'left')
    second = _booking(hour + length, next_length, 'left')
    pairs = _in_guava([(right_first, second), (left_first, second)])
    npt.assert_equal(right_first.overlaps(second), pairs[0][1])
    npt.assert_equal(right_first.overlaps(second),
                     _in_portion(right_first).overlaps(_in_portion(second)))
    npt.assert_equal(left_first.overlaps(second), pairs[1][1])
    with pytest.raises(AssertionError):
        npt.assert_equal(right_first.overlaps(second), left_first.overlaps(second))


@pytest.mark.skipif(not guava_available, reason='java and the Guava jars are required for this oracle')
@given(BOOKING_HOUR, st.sampled_from(('both', 'left', 'right')))
@JAVA_ORACLE
def test_a_booking_of_no_length_conflicts_with_itself_only_when_both_ends_are_closed(hour, closed):
    """A booking whose start and end are the same instant is a well-formed Interval in pandas for
    every closure, and it conflicts with itself under exactly one of them: closed on both ends it is
    the single point, and under either half-open reading it holds nothing at all. portion says the
    same by collapsing three of the four to the empty interval, and Guava says it by intersecting an
    empty range with itself."""
    booking = _booking(hour, 0, closed)
    npt.assert_equal(booking.closed, closed)
    npt.assert_equal(booking.length, booking.right - booking.left)
    npt.assert_equal(booking.overlaps(booking), not _in_portion(booking).empty)
    npt.assert_equal(booking.overlaps(booking), _in_guava([(booking, booking)])[0][1])


@pytest.mark.skipif(not guava_available, reason='java and the Guava jars are required for this oracle')
@given(BOOKING_HOUR)
@JAVA_ORACLE
def test_a_booking_of_no_length_closed_at_neither_end_is_a_refusal_in_the_third_library(hour):
    """The fourth closure of the same zero-length booking is where the three libraries stop agreeing
    on what exists. pandas builds the object and reports its closure back; portion returns the empty
    interval, which is the same value it returns for the two half-open ones, so the closure is gone;
    Guava refuses to construct it at all, its `open` factory documented to throw
    IllegalArgumentException "if lower is greater than or equal to upper", which reaches this test as
    a non-zero exit. A booking of no length is therefore a record in one library, a nothing in the
    second and an error in the third, and only the first of those can be written to a roster."""
    booking = _booking(hour, 0, 'neither')
    npt.assert_equal(booking.closed, 'neither')
    npt.assert_equal(_in_portion(booking).empty, _in_portion(_booking(hour, 0, 'left')).empty)
    with pytest.raises(AssertionError):
        npt.assert_equal(_in_portion(booking).empty, _in_portion(_booking(hour, 0, 'both')).empty)
    with pytest.raises(subprocess.CalledProcessError):
        _in_guava([(booking, booking)])


@given(st.lists(st.tuples(BOOKING_HOUR, BOOKING_LENGTH), min_size=2, max_size=5), CLOSURE, st.data())
@SLOW
def test_an_index_of_bookings_counts_the_probe_against_itself(entries, closed, source):
    """IntervalIndex.overlaps compares the probe with every interval in the index, the probe included
    when it is one of them, so the conflict count P180 reports is one larger than the number of other
    bookings that clash. The whole vector agrees with portion booking by booking, and the extra hit
    is exactly the probe's verdict on itself. Replaces the typed
    `conflicts([desk, training, later], desk, drop_self=False) == 2` of case 180."""
    bookings = [_booking(hour, length, closed) for hour, length in entries]
    position = source.draw(st.integers(min_value=0, max_value=len(bookings) - 1))
    probe = bookings[position]
    index = pd.IntervalIndex(bookings)
    without = pd.IntervalIndex([booking for at, booking in enumerate(bookings) if at != position])
    npt.assert_array_equal(list(index.overlaps(probe)),
                           [_in_portion(booking).overlaps(_in_portion(probe)) for booking in bookings])
    npt.assert_equal(index.overlaps(probe)[position], probe.overlaps(probe))
    npt.assert_equal(int(np.sum(index.overlaps(probe))),
                     int(np.sum(without.overlaps(probe))) + int(probe.overlaps(probe)))


# ---------------------------------------------------------------- shapes, and the nodes they never look at
SHACL_DIRECTORY = pathlib.Path(os.environ.get('SHACL_DIR', str(pathlib.Path.home() / 'shacl-oracle')))
SHACL_VALIDATE_ORACLE_JS = pathlib.Path(__file__).with_name('shacl_validate_oracle.js')
shacl_oracle_available = (shutil.which('node') is not None
                          and (SHACL_DIRECTORY / 'node_modules' / 'rdf-validate-shacl').is_dir())
SHACL_ORACLE = settings(max_examples=10, deadline=None)
EXAMPLE = rdflib.Namespace('http://example.org/')
LOCAL_NAME = st.from_regex(r'\A[a-z][a-z0-9]{0,7}\Z')
EVIDENCE_DATE = st.dates(min_value=datetime.date(2000, 1, 1), max_value=datetime.date(2099, 12, 31))
NOT_A_DATE = st.from_regex(r'\A[a-zA-Z]{1,10}\Z')


def _control_shapes():
    """P194's shapes graph, built with rdflib's own vocabulary rather than written out as text: one
    node shape targeting the control class and requiring an owner and a typed evidence date."""
    shapes = rdflib.Graph()
    shapes.add((EXAMPLE.ControlShape, rdflib.RDF.type, rdflib.SH.NodeShape))
    shapes.add((EXAMPLE.ControlShape, rdflib.SH.targetClass, EXAMPLE.Control))
    owner, evidence = rdflib.BNode(), rdflib.BNode()
    shapes.add((EXAMPLE.ControlShape, rdflib.SH.property, owner))
    shapes.add((owner, rdflib.SH.path, EXAMPLE.owner))
    shapes.add((owner, rdflib.SH.minCount, rdflib.Literal(1)))
    shapes.add((EXAMPLE.ControlShape, rdflib.SH.property, evidence))
    shapes.add((evidence, rdflib.SH.path, EXAMPLE.evidenceDate))
    shapes.add((evidence, rdflib.SH.minCount, rdflib.Literal(1)))
    shapes.add((evidence, rdflib.SH.datatype, rdflib.XSD.date))
    return shapes


def _control_graph(name, class_name, owner, evidence):
    """One control node of the named class, with the owner and evidence date supplied by the caller.
    Every term comes from rdflib; nothing here is written as turtle."""
    graph = rdflib.Graph()
    node = EXAMPLE[name]
    graph.add((node, rdflib.RDF.type, EXAMPLE[class_name]))
    for predicate, value in owner + evidence:
        graph.add((node, predicate, value))
    return graph


def _in_pyshacl(data, shapes):
    """pySHACL 0.40.1 over rdflib 7.6.0, the pair P194 names, reporting conformance and the number of
    sh:ValidationResult nodes in the report graph it returns."""
    conforms, report, _ = pyshacl.validate(data, shacl_graph=shapes, advanced=True)
    return bool(conforms), len(list(report.subjects(rdflib.RDF.type, rdflib.SH.ValidationResult)))


def _in_rdf_validate_shacl(data, shapes):
    """The same two graphs validated by rdf-validate-shacl 0.6.5 under node, a JavaScript
    implementation of the same W3C recommendation. Both graphs cross as turtle written by rdflib's own
    serializer; the shim parses argv, calls the library and prints two lines."""
    with tempfile.TemporaryDirectory() as directory:
        paths = []
        for graph, name in ((shapes, 'shapes.ttl'), (data, 'data.ttl')):
            path = pathlib.Path(directory) / name
            path.write_text(graph.serialize(format='turtle'), encoding='utf-8')
            paths.append(str(path))
        completed = subprocess.run(['node', str(SHACL_VALIDATE_ORACLE_JS)] + paths,
                                   capture_output=True, encoding='utf-8', check=True,
                                   env={**os.environ,
                                        'NODE_PATH': str(SHACL_DIRECTORY / 'node_modules')})
    conforms, results = completed.stdout.split('\n')[:2]
    return conforms == 'true', int(results)


@pytest.mark.skipif(not shacl_oracle_available,
                    reason='node and the rdf-validate-shacl checkout are required for this oracle')
@given(LOCAL_NAME, LOCAL_NAME, EVIDENCE_DATE)
@SHACL_ORACLE
def test_a_control_with_an_owner_and_a_typed_evidence_date_conforms_in_two_implementations(name,
                                                                                          owner,
                                                                                          when):
    """P194 is recorded as a theoretical requirement, so its positive test had never been run. Run
    now, pySHACL 0.40.1 and rdf-validate-shacl 0.6.5 under node return the same verdict and the same
    number of results for every generated control."""
    shapes = _control_shapes()
    data = _control_graph(name, 'Control', [(EXAMPLE.owner, EXAMPLE[owner])],
                          [(EXAMPLE.evidenceDate, rdflib.Literal(when))])
    npt.assert_array_equal(_in_pyshacl(data, shapes), _in_rdf_validate_shacl(data, shapes))


@pytest.mark.skipif(not shacl_oracle_available,
                    reason='node and the rdf-validate-shacl checkout are required for this oracle')
@given(LOCAL_NAME, LOCAL_NAME, EVIDENCE_DATE)
@SHACL_ORACLE
def test_a_control_without_an_owner_is_the_same_single_violation_in_both(name, owner, when):
    """The first of P194's adverse tests. Removing the owner link produces one violation in both
    implementations, and the graph that keeps it produces none in either, so the count the chain
    reports is not a property of the validator it happened to use."""
    shapes = _control_shapes()
    evidence = [(EXAMPLE.evidenceDate, rdflib.Literal(when))]
    without = _control_graph(name, 'Control', [], evidence)
    with_owner = _control_graph(name, 'Control', [(EXAMPLE.owner, EXAMPLE[owner])], evidence)
    npt.assert_array_equal(_in_pyshacl(without, shapes), _in_rdf_validate_shacl(without, shapes))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_in_pyshacl(without, shapes), _in_pyshacl(with_owner, shapes))


@pytest.mark.skipif(not shacl_oracle_available,
                    reason='node and the rdf-validate-shacl checkout are required for this oracle')
@given(LOCAL_NAME, LOCAL_NAME, NOT_A_DATE)
@SHACL_ORACLE
def test_an_ill_typed_evidence_date_is_the_same_single_violation_in_both(name, owner, text):
    """The second adverse test. A literal that carries the date datatype but no date in it fails
    sh:datatype in both implementations, with the same count, even though one reaches that verdict
    through rdflib's lexical parser and the other through rdf-validate-datatype."""
    shapes = _control_shapes()
    data = _control_graph(name, 'Control', [(EXAMPLE.owner, EXAMPLE[owner])],
                          [(EXAMPLE.evidenceDate, rdflib.Literal(text, datatype=rdflib.XSD.date))])
    npt.assert_array_equal(_in_pyshacl(data, shapes), _in_rdf_validate_shacl(data, shapes))


@pytest.mark.skipif(not shacl_oracle_available,
                    reason='node and the rdf-validate-shacl checkout are required for this oracle')
@given(LOCAL_NAME, LOCAL_NAME, EVIDENCE_DATE, st.from_regex(r'\A[A-Z][a-z]{2,7}\Z').filter(
           lambda word: word != 'Control'))
@SHACL_ORACLE
def test_a_node_of_another_class_conforms_vacuously_in_both(name, owner, when, other_class):
    """P194's third adverse test, and the one its contract is written around: "Zero targeted nodes
    cannot count as success when controls were expected." A node whose class is not the targeted one
    is not selected by any shape, so the missing owner is never looked for and the report is
    identical to the report for a graph that satisfies everything. Both implementations answer this
    way, so the vacuous pass is what SHACL specifies and not one library's default. Replaces the
    typed `shacl(wrong_class) == (True, 0)` of handoff_guards_v21.py case 194."""
    shapes = _control_shapes()
    evidence = [(EXAMPLE.evidenceDate, rdflib.Literal(when))]
    unselected = _control_graph(name, other_class, [], evidence)
    conforming = _control_graph(name, 'Control', [(EXAMPLE.owner, EXAMPLE[owner])], evidence)
    npt.assert_array_equal(_in_pyshacl(unselected, shapes),
                           _in_rdf_validate_shacl(unselected, shapes))
    npt.assert_array_equal(_in_pyshacl(unselected, shapes), _in_pyshacl(conforming, shapes))
    npt.assert_array_equal(_in_rdf_validate_shacl(unselected, shapes),
                           _in_rdf_validate_shacl(conforming, shapes))


@pytest.mark.skipif(not shacl_oracle_available,
                    reason='node and the rdf-validate-shacl checkout are required for this oracle')
@given(LOCAL_NAME, EVIDENCE_DATE)
@SHACL_ORACLE
def test_a_graph_with_no_controls_at_all_conforms_in_both(name, when):
    """The empty case of the same rule. A graph holding no node of the targeted class conforms in
    both implementations, and so does a graph holding nothing at all, so a validation report cannot
    distinguish a complete inventory from an empty file."""
    shapes = _control_shapes()
    empty = rdflib.Graph()
    unrelated = _control_graph(name, 'Widget', [], [(EXAMPLE.evidenceDate, rdflib.Literal(when))])
    npt.assert_array_equal(_in_pyshacl(empty, shapes), _in_rdf_validate_shacl(empty, shapes))
    npt.assert_array_equal(_in_pyshacl(empty, shapes), _in_pyshacl(unrelated, shapes))


@given(st.lists(LOCAL_NAME, min_size=1, max_size=4, unique=True), EVIDENCE_DATE)
@SLOW
def test_the_inventory_reconciliation_is_what_notices_the_unselected_control(names, when):
    """The independent target inventory P194 requires beside the shape validation. rdflib's own
    subjects() reports which nodes carry the targeted class, and the expected identifiers that are
    not among them are the coverage defect; a DuckDB EXCEPT over the same two lists finds the same
    ones. For a graph whose controls all carry another class the whole inventory is missing, and that
    is the only signal, because the validation report is the report of a conforming graph. Replaces
    the typed `target_coverage(wrong_class, ['c1']) == ['c1']` of case 194."""
    graph = rdflib.Graph()
    for name in names:
        graph.add((EXAMPLE[name], rdflib.RDF.type, EXAMPLE.Widget))
        graph.add((EXAMPLE[name], EXAMPLE.evidenceDate, rdflib.Literal(when)))
    targeted = sorted(str(subject).rsplit('/', 1)[-1]
                      for subject in graph.subjects(rdflib.RDF.type, EXAMPLE.Control))
    expected = pd.DataFrame({'name': pd.Series(names, dtype='object')})
    present = pd.DataFrame({'name': pd.Series(targeted, dtype='object')})
    with duckdb.connect() as connection:
        connection.register('expected', expected)
        connection.register('present', present)
        missing = [row[0] for row in connection.execute(
            'select name from expected except select name from present order by name').fetchall()]
    npt.assert_array_equal(missing, sorted(set(names) - set(targeted)))
    npt.assert_array_equal(missing, sorted(names))
    npt.assert_array_equal(targeted, [])


# ---------------------------------------------------------------- coverage, and the domain it is relative to
COMPARISONS = {'<': operator.lt, '<=': operator.le, '>': operator.gt, '>=': operator.ge}
DECISION_THRESHOLD = st.integers(min_value=-20, max_value=20)
DOMAIN_DISTANCE = st.integers(min_value=0, max_value=20)


def _rows_in(module, rows):
    """P198's decision rows as expressions of one integer variable in the given solver's API. The
    comparison comes from the standard library's operator module, so the row is built by applying a
    named function to the solver's own variable and nothing is written twice."""
    variable = module.Int('n')
    return variable, [COMPARISONS[sense](variable, value) for sense, value in rows]


def _uncovered_in(module, rows, floor):
    """P198's gap query: a point of the declared domain that no row covers."""
    variable, predicates = _rows_in(module, rows)
    solver = module.Solver()
    solver.add(variable >= floor)
    solver.add(module.Not(module.Or(predicates)))
    status = str(solver.check())
    if status == 'sat':
        return status, int(str(solver.model()[variable]))
    return status, None


def _overlapping_in(module, rows, floor):
    """P198's overlap query: a point of the declared domain that more than one row answers."""
    variable, predicates = _rows_in(module, rows)
    solver = module.Solver()
    solver.add(variable >= floor)
    solver.add(module.And(predicates))
    status = str(solver.check())
    if status == 'sat':
        model = solver.model()
        return status, int(str(model[variable])), str(model.eval(module.And(predicates)))
    return status, None, None


@given(DECISION_THRESHOLD, DECISION_THRESHOLD)
@SLOW
def test_a_partition_of_the_declared_domain_has_no_gap_and_no_overlap_in_either_solver(threshold,
                                                                                      floor):
    """P198's theoretical positive test, run. Rows below and at-or-above one generated threshold
    partition the declared domain: the gap query and the overlap query are both unsatisfiable, in z3
    5.1.0 and in cvc5 1.3.4, whose decision procedures share no code. Replaces the typed
    `uncovered([...]) is None` and `overlapping([...]) is None` of handoff_guards_v21.py case 198."""
    rows = [('<', threshold), ('>=', threshold)]
    npt.assert_array_equal(_uncovered_in(z3, rows, floor), _uncovered_in(cvc5_pythonic, rows, floor))
    npt.assert_array_equal(_overlapping_in(z3, rows, floor),
                           _overlapping_in(cvc5_pythonic, rows, floor))
    npt.assert_array_equal(_uncovered_in(z3, rows, floor)[0], 'unsat')
    npt.assert_array_equal(_overlapping_in(z3, rows, floor)[0], 'unsat')


@given(DECISION_THRESHOLD, DOMAIN_DISTANCE)
@SLOW
def test_moving_one_row_off_the_boundary_leaves_exactly_the_boundary_uncovered(threshold, below):
    """P198's first adverse test. Changing the second row from at-or-above to strictly above the
    threshold leaves one point of the domain unanswered, and both solvers return that point: the
    threshold itself, whatever it was generated as, from any floor at or below it."""
    rows = [('<', threshold), ('>', threshold)]
    floor = threshold - below
    npt.assert_array_equal(_uncovered_in(z3, rows, floor), _uncovered_in(cvc5_pythonic, rows, floor))
    npt.assert_array_equal(_uncovered_in(z3, rows, floor), ['sat', threshold])


@given(DECISION_THRESHOLD, DOMAIN_DISTANCE)
@SLOW
def test_the_same_gap_is_gone_when_the_domain_starts_above_it(threshold, above):
    """Totality is relative to the declared domain, which is P198's own contract sentence. The rows
    that leave the threshold unanswered leave nothing unanswered once the domain begins above it, and
    both solvers agree, so the same table is total or not according to a bound that is not in the
    table at all."""
    rows = [('<', threshold), ('>', threshold)]
    floor = threshold + 1 + above
    npt.assert_array_equal(_uncovered_in(z3, rows, floor), _uncovered_in(cvc5_pythonic, rows, floor))
    npt.assert_array_equal(_uncovered_in(z3, rows, floor)[0], 'unsat')
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_uncovered_in(z3, rows, floor),
                               _uncovered_in(z3, rows, threshold))


@given(DECISION_THRESHOLD, st.integers(min_value=1, max_value=20), DOMAIN_DISTANCE)
@SLOW
def test_two_rows_that_both_answer_the_same_request_are_a_witness_both_solvers_find(threshold, gap,
                                                                                   below):
    """P198's second adverse test. A second row admitting everything from a lower threshold overlaps
    the first everywhere above the higher one; both solvers find a witness, and each solver's own
    model evaluates the conjunction of the rows to true, so the witness is checked by the solver that
    produced it rather than by arithmetic written here."""
    rows = [('>=', threshold), ('>=', threshold - gap)]
    floor = threshold - below
    by_z3 = _overlapping_in(z3, rows, floor)
    by_cvc5 = _overlapping_in(cvc5_pythonic, rows, floor)
    npt.assert_array_equal(by_z3[0], by_cvc5[0])
    npt.assert_array_equal(by_z3[0], 'sat')
    npt.assert_array_equal([by_z3[2], by_cvc5[2]], ['True', 'True'])


@given(DECISION_THRESHOLD, st.sampled_from(('<', '<=', '>', '>=')))
@SLOW
def test_a_one_row_coverage_question_is_answered_by_one_solver_and_refused_by_the_other(threshold,
                                                                                       sense):
    """A decision table with one row is a coverage question in z3 and an error in cvc5. z3's Or, read
    at raw.githubusercontent.com/Z3Prover/z3/z3-5.1.0/src/api/python/z3/z3.py, hands whatever it is
    given to Z3_mk_or, which accepts one argument; cvc5's pythonic Or collapses a single expression
    but not a single-element list -- "if len(args) == 1 and type(args[0]) is not list: return
    args[0]" -- and its term manager refuses the kind below two children. Declaring the same row
    twice is accepted by both and gives z3's answer, so the refusal is about the arity of the list
    and not about the question. P198 builds its query from a list comprehension over the rows, so a
    one-row table reaches this."""
    rows = [(sense, threshold)]
    doubled = rows + rows
    with pytest.raises(RuntimeError):
        _uncovered_in(cvc5_pythonic, rows, threshold)
    npt.assert_array_equal(_uncovered_in(z3, rows, threshold),
                           _uncovered_in(z3, doubled, threshold))
    npt.assert_array_equal(_uncovered_in(z3, doubled, threshold),
                           _uncovered_in(cvc5_pythonic, doubled, threshold))


@given(st.integers(min_value=1, max_value=6))
@SLOW
def test_the_enumerated_domain_is_the_same_grid_in_two_libraries(size):
    """The finite domain P198 enumerates beside the solver, itertools.product over a range, is the
    grid numpy's indices produces for the same shape, in the same order and with the same number of
    points. Replaces the typed `len(known) == 9` of case 198."""
    npt.assert_array_equal(list(itertools.product(range(size), repeat=2)),
                           np.indices((size, size)).reshape(2, -1).T)


# ---------------------------------------------------------------- a uniqueness contract, and the index under it
MANIFEST_KEY = st.from_regex(r'\A[A-Z][0-9]\Z')
MANIFEST_ROWS = st.lists(st.tuples(MANIFEST_KEY, MANIFEST_KEY), min_size=1, max_size=6, unique=True)


def _manifest_schema(movements=None):
    """P177's manifest contract: two text columns that together identify a row, and optionally the
    declared set of movements a row may name."""
    columns = {'movement': pandera.Column(str) if movements is None
               else pandera.Column(str, pandera.Check.isin(list(movements))),
               'package': pandera.Column(str)}
    return pandera.DataFrameSchema(columns, unique=['movement', 'package'])


def _manifest_frame(rows):
    return pd.DataFrame(list(rows), columns=['movement', 'package'])


def _manifest_in_duckdb(rows):
    """The same two columns as a DuckDB table whose primary key is the pair, which is the same
    contract stated to a different engine. Returns the number of rows the engine kept."""
    with duckdb.connect() as connection:
        connection.execute('create table manifest(movement VARCHAR, package VARCHAR, '
                           'primary key (movement, package))')
        connection.executemany('insert into manifest values (?, ?)', [list(row) for row in rows])
        return connection.execute('select count(*) from manifest').fetchone()[0]


@given(MANIFEST_ROWS)
@SLOW
def test_a_manifest_of_distinct_rows_passes_the_uniqueness_contract_in_three_engines(rows):
    """P177 states the identity of a manifest row with pandera's `unique=['movement', 'package']`.
    On generated rows that are distinct, pandera returns the frame unchanged, polars counts as many
    unique rows as it has rows, and DuckDB accepts every row into a table whose primary key is the
    same pair. Replaces the typed `len(checked) == 6` of handoff_guards_v19.py case 177."""
    frame = _manifest_frame(rows)
    pdt.assert_frame_equal(_manifest_schema().validate(frame, lazy=True), frame)
    in_polars = pl.from_pandas(frame)
    npt.assert_equal(in_polars.n_unique(), in_polars.height)
    npt.assert_equal(_manifest_in_duckdb(rows), len(rows))


@given(MANIFEST_ROWS, st.data())
@SLOW
def test_a_repeated_manifest_row_is_found_by_the_schema_and_by_two_other_engines(rows, source):
    """The same manifest with one of its rows declared twice. pandera reports it as
    `multiple_fields_uniqueness`, polars flags both copies and nothing else, and DuckDB refuses the
    insert on the primary key. Replaces the typed rejection of the duplicated manifest of case 177."""
    repeated = source.draw(st.sampled_from(rows))
    declared = list(rows) + [repeated]
    frame = _manifest_frame(declared)
    with pytest.raises(pandera.errors.SchemaErrors) as rejection:
        _manifest_schema().validate(frame, lazy=True)
    npt.assert_array_equal(sorted({str(case) for case in rejection.value.failure_cases['check']}),
                           ['multiple_fields_uniqueness'])
    in_polars = pl.from_pandas(frame)
    plt.assert_frame_equal(in_polars.filter(in_polars.is_duplicated()).unique(maintain_order=True),
                           pl.DataFrame({'movement': [repeated[0]], 'package': [repeated[1]]}))
    with pytest.raises(duckdb.ConstraintException):
        _manifest_in_duckdb(declared)


@given(MANIFEST_ROWS)
@SLOW
def test_the_index_a_concatenation_repeats_defeats_the_uniqueness_report(rows):
    """Appending a row with `pd.concat` keeps that row's index label, so the frame carries the label
    twice, and pandera's uniqueness report then fails inside pandas' reshaping with "Columns with
    duplicate values are not supported in stack" -- a ValueError, not a schema error, so a caller
    that catches schema errors does not catch it and the manifest is neither accepted nor rejected.
    Resetting the index first turns the same frame into an ordinary rejection. polars has no index at
    all, and its verdict on the two frames is the same one. Replaces the typed
    `list(duplicated.index) == [0, 1, 2, 3, 4, 5, 0]` of case 177."""
    frame = _manifest_frame(rows)
    concatenated = pd.concat([frame, frame.iloc[[0]]])
    npt.assert_array_equal(list(concatenated.index), list(frame.index) + [frame.index[0]])
    with pytest.raises(ValueError,
                       match='Columns with duplicate values are not supported in stack'):
        _manifest_schema().validate(concatenated, lazy=True)
    with pytest.raises(pandera.errors.SchemaErrors):
        _manifest_schema().validate(concatenated.reset_index(drop=True), lazy=True)
    plt.assert_series_equal(pl.from_pandas(concatenated).is_duplicated(),
                            pl.from_pandas(concatenated.reset_index(drop=True)).is_duplicated())


@given(MANIFEST_ROWS, MANIFEST_KEY)
@SLOW
def test_a_movement_outside_the_declared_set_is_rejected_by_the_schema_and_by_a_check_constraint(
        rows, absent):
    """The declared movement set is the other half of P177's contract. A row naming a movement
    outside it is rejected by pandera's isin check, and by a DuckDB foreign key into a table holding
    the same declared movements, and polars' is_in names the same row. Each engine is told the
    declared set once and finds the one row that is not in it. Replaces the typed rejection of the
    unknown movement of case 177."""
    movements = sorted({movement for movement, _ in rows})
    assume(absent not in movements)
    declared = list(rows) + [(absent, absent)]
    frame = _manifest_frame(declared)
    with pytest.raises(pandera.errors.SchemaErrors) as rejection:
        _manifest_schema(movements).validate(frame, lazy=True)
    npt.assert_array_equal(sorted({str(case) for case
                                   in rejection.value.failure_cases['failure_case']}), [absent])
    npt.assert_array_equal(pl.from_pandas(frame).filter(
        ~pl.col('movement').is_in(movements))['movement'].to_list(), [absent])
    with duckdb.connect() as connection:
        connection.execute('create table declared(movement VARCHAR primary key)')
        connection.executemany('insert into declared values (?)',
                               [[movement] for movement in movements])
        connection.execute('create table manifest(movement VARCHAR, package VARCHAR, '
                           'foreign key (movement) references declared(movement))')
        with pytest.raises(duckdb.ConstraintException):
            connection.executemany('insert into manifest values (?, ?)',
                                   [list(row) for row in declared])


# ---------------------------------------------------------------- a bound digest and a dated approval
SHA256_PHP_ORACLE = pathlib.Path(__file__).with_name('sha256_oracle.php')
SHA256_RUBY_ORACLE = pathlib.Path(__file__).with_name('sha256_oracle.rb')
ISO_DATE_RUBY_ORACLE = pathlib.Path(__file__).with_name('iso_date_oracle.rb')
ISO_DATE_PHP_ORACLE = pathlib.Path(__file__).with_name('iso_date_oracle.php')
ARTIFACT = st.binary(min_size=0, max_size=64)
DECOMPOSABLE = ''.join(letter for letter in map(chr, range(0xC0, 0x180))
                       if unicodedata.decomposition(letter)
                       and not unicodedata.decomposition(letter).startswith('<'))
ACCENTED_TEXT = st.text(alphabet=DECOMPOSABLE, min_size=1, max_size=8)
GATE_DATES = st.dates(min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2099, 12, 31))
GATE_YEAR = st.integers(min_value=1900, max_value=2099)
SINGLE_DIGIT_MONTH = st.integers(min_value=1, max_value=9)
TWO_DAYS = st.lists(st.integers(min_value=1, max_value=28), min_size=2, max_size=2,
                    unique=True).map(sorted)
TIME_OF_DAY = st.tuples(st.integers(min_value=0, max_value=23), st.integers(min_value=0, max_value=59),
                        st.integers(min_value=0, max_value=59))
OFFSET_HOURS = st.integers(min_value=-14, max_value=14).filter(lambda hours: hours != 0)
CASE_KEYS = st.lists(st.integers(min_value=0, max_value=12), min_size=1, max_size=8, unique=True)
APPROVAL_POSITIONS = st.lists(st.integers(min_value=0, max_value=40), min_size=1, max_size=10)


def _php_sha256(artifact):
    completed = subprocess.run(['php', str(SHA256_PHP_ORACLE), artifact.hex()],
                               capture_output=True, text=True, check=True)
    return completed.stdout.strip()


def _ruby_sha256(artifact):
    completed = subprocess.run(['ruby', str(SHA256_RUBY_ORACLE), artifact.hex()],
                               capture_output=True, text=True, check=True)
    return completed.stdout.strip()


def _ruby_calendar_day(text):
    """The calendar date Ruby reads out of one record and that date's Julian day number, as two lines."""
    completed = subprocess.run(['ruby', str(ISO_DATE_RUBY_ORACLE), text],
                               capture_output=True, text=True, check=True)
    return completed.stdout.split()


def _php_calendar_day(text):
    """The calendar date PHP reads out of the same record and the instant it counts, as two lines."""
    completed = subprocess.run(['php', str(ISO_DATE_PHP_ORACLE), text],
                               capture_output=True, text=True, check=True)
    return completed.stdout.split()


def _gate_frames(case_keys, positions):
    """One control case per generated key and one approval per position drawn from those keys, so the
    cases that carry no approval are generated rather than filtered for."""
    cases = pd.DataFrame({'case_id': case_keys, 'artifact': range(len(case_keys))})
    approved = sorted({case_keys[position % len(case_keys)] for position in positions})
    approvals = pd.DataFrame({'case_id': approved, 'approval': range(len(approved))})
    return cases, approvals


def _duckdb_case_ids(cases, approvals, query):
    """The same resolution in SQL. DuckDB is a third engine and shares no code with either dataframe
    library."""
    with duckdb.connect() as connection:
        connection.register('cases', cases)
        connection.register('approvals', approvals)
        return np.sort(np.array([row[0] for row in connection.execute(query).fetchall()]))


@pytest.mark.skipif(not (ruby_available and php_binary_available),
                    reason='the ruby and php runtimes are required for these oracles')
@given(ARTIFACT)
@ORACLE_PROCESS
def test_three_sha256_implementations_agree_on_the_digest_of_a_generated_artifact(artifact):
    """P199 binds evidence to a declared SHA-256 and blocks the gate when the artifact does not match it.
    hashlib.sha256 here is _hashlib.openssl_sha256, so it is OpenSSL's implementation and not CPython's
    own; the two runtime oracles are not. PHP's ext/hash carries its own SHA-256 in ext/hash/hash_sha.c at
    tag php-8.4.19, and Ruby's Digest::SHA256 is Aaron D. Gifford's implementation vendored at
    ext/digest/sha2/sha2.h at tag v3_3_6, which Digest::SHA256.ancestors confirms is in use here rather
    than OpenSSL::Digest. All three return the same digest for the same generated bytes, so what the next
    two tests record is a property of the binding and not of one library."""
    npt.assert_array_equal(hashlib.sha256(artifact).hexdigest(), _php_sha256(artifact))
    npt.assert_array_equal(hashlib.sha256(artifact).hexdigest(), _ruby_sha256(artifact))


@pytest.mark.skipif(not (ruby_available and php_binary_available),
                    reason='the ruby and php runtimes are required for these oracles')
@given(ARTIFACT)
@ORACLE_PROCESS
def test_the_bound_digest_is_one_number_that_two_transcriptions_of_it_do_not_compare_equal(artifact):
    """The gate compares the computed digest with the declared one as text. CPython documents hexdigest as
    returning "a string object of double length, containing only hexadecimal digits" (Doc/library/
    hashlib.rst at tag v3.11.15) and does not say which case, PHP documents hash as returning "the
    calculated message digest as lowercase hexits", and Ruby writes lowercase too, so the three agree on a
    convention that the format does not require. Transcribed in the other case the declared value is the
    same number -- bytes.fromhex reads it back to the bytes every runtime computed -- and no text
    comparison accepts it, hmac.compare_digest, the constant-time comparison CPython publishes for exactly
    this check, included. So the artifact clause of the gate refuses a correct declaration that was
    written in capitals. Replaces the typed 'blocked: artifact does not match the bound hash' of
    handoff_guards_v21.py case 199."""
    digest = hashlib.sha256(artifact).hexdigest()
    transcribed = digest.upper()
    assume(transcribed != digest)  # a digest of sixty-four decimal digits has no case to change
    npt.assert_array_equal(bytes.fromhex(transcribed), bytes.fromhex(_php_sha256(artifact)))
    npt.assert_array_equal(bytes.fromhex(transcribed), bytes.fromhex(_ruby_sha256(artifact)))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(transcribed, _php_sha256(artifact))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(hmac.compare_digest(digest, transcribed),
                               hmac.compare_digest(digest, digest))


@given(ACCENTED_TEXT)
@SLOW
def test_the_digest_binds_one_encoding_of_the_evidence_and_not_the_text_it_shows(text):
    """The other half of what the bound hash does not say. Composed and decomposed spellings of the same
    accented text are the same text: unicodedata folds each onto the other, and so does polars'
    str.normalize, whose docstring at tag py-1.44.1 says it "Returns the Unicode normal form of the string
    values" using "the forms described in Unicode Standard Annex 15", implemented in Rust and not through
    CPython's tables. Their digests are two different numbers. So an evidence file re-saved by an editor
    that normalizes, or typed on a keyboard that composes differently, fails the artifact clause while
    reading identically to every party to the approval."""
    composed = unicodedata.normalize('NFC', text)
    decomposed = unicodedata.normalize('NFD', text)
    plt.assert_series_not_equal(pl.Series([composed]), pl.Series([decomposed]))
    plt.assert_series_equal(pl.Series([composed]).str.normalize('NFC'),
                            pl.Series([decomposed]).str.normalize('NFC'))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(hashlib.sha256(composed.encode()).hexdigest(),
                               hashlib.sha256(decomposed.encode()).hexdigest())


@given(CASE_KEYS, APPROVAL_POSITIONS)
@SLOW
def test_the_one_to_one_check_refuses_a_second_approval_and_a_second_case_alike(case_keys, positions):
    """P199 resolves each case to its approval with merge(validate='one_to_one'). pandas documents
    "one_to_one" or "1:1": check if merge keys are unique in both left and right datasets
    (pandas/core/frame.py at tag v2.2.3) and polars documents 1:1 as "One-to-one. Checks if join keys are
    unique in both left and right datasets." (py-polars/src/polars/dataframe/frame.py at tag py-1.44.1).
    Executed, the two agree on both sides: each refuses a repeated case and each refuses a repeated
    approval, with MergeError and ComputeError. That is the one thing the chain's cardinality guard does
    establish. Replaces the typed g.rejects(pd.errors.MergeError, ...) of case 199."""
    cases, approvals = _gate_frames(case_keys, positions)
    repeated_cases = pd.concat([cases, cases.iloc[[0]]])
    repeated_approvals = pd.concat([approvals, approvals.iloc[[0]]])
    with pytest.raises(pd.errors.MergeError):
        repeated_cases.merge(approvals, on='case_id', validate='one_to_one')
    with pytest.raises(pl.exceptions.ComputeError):
        pl.from_pandas(repeated_cases).join(pl.from_pandas(approvals), on='case_id', how='inner',
                                            validate='1:1')
    with pytest.raises(pd.errors.MergeError):
        cases.merge(repeated_approvals, on='case_id', validate='one_to_one')
    with pytest.raises(pl.exceptions.ComputeError):
        pl.from_pandas(cases).join(pl.from_pandas(repeated_approvals), on='case_id', how='inner',
                                   validate='1:1')


@given(CASE_KEYS, APPROVAL_POSITIONS)
@SLOW
def test_the_cardinality_check_passes_over_the_case_that_has_no_approval_at_all(case_keys, positions):
    """The check is on the keys, not on the coverage. A control case with no approval row is dropped by the
    inner join and is not a cardinality failure in either engine or in DuckDB, so it reaches no gate, gets
    no blocked reason, and appears in no exception routing: the chain's actionable exception for an
    unapproved case is an absent row. What was lost is recoverable only from the outer join's indicator,
    which is the column pandas documents as carrying "left_only" for observations whose merge key only
    appears in the left DataFrame, or from a set difference in SQL; both name exactly the cases the
    validated join discarded. Replaces the typed len(joined) == 2 of case 199."""
    cases, approvals = _gate_frames(case_keys, positions)
    joined = cases.merge(approvals, on='case_id', validate='one_to_one', indicator=True)
    in_polars = pl.from_pandas(cases).join(pl.from_pandas(approvals), on='case_id', how='inner',
                                           validate='1:1')
    npt.assert_array_equal(np.sort(joined['case_id'].to_numpy()),
                           np.sort(in_polars['case_id'].to_numpy()))
    npt.assert_array_equal(np.sort(joined['case_id'].to_numpy()),
                           _duckdb_case_ids(cases, approvals,
                                            'select cases.case_id from cases join approvals '
                                            'on cases.case_id = approvals.case_id'))
    outer = cases.merge(approvals, on='case_id', how='outer', indicator=True)
    unapproved = outer.loc[outer['_merge'] == 'left_only', 'case_id'].to_numpy()
    npt.assert_array_equal(np.sort(np.concatenate([joined['case_id'].to_numpy(), unapproved])),
                           np.sort(cases['case_id'].to_numpy()))
    npt.assert_array_equal(np.sort(unapproved),
                           _duckdb_case_ids(cases, approvals,
                                            'select case_id from cases except '
                                            'select case_id from approvals'))


@given(CASE_KEYS, APPROVAL_POSITIONS, ABSENT_KEYS)
@SLOW
def test_both_engines_refuse_a_repeated_key_the_join_would_have_discarded(case_keys, positions,
                                                                         absent_keys):
    """The mirror of the same asymmetry. A case declared twice under a key no approval names cannot change
    what the join returns -- the unvalidated join over the widened frame returns exactly the validated join
    over the narrow one -- and both engines still refuse the merge. So the guard fires on rows the gate
    would never have seen and stays silent about the case the gate never sees, and the two failures a
    reader would most want distinguished, a duplicated approval and a missing one, are respectively an
    exception and nothing at all."""
    cases, approvals = _gate_frames(case_keys, positions)
    unbound = pd.DataFrame({'case_id': list(absent_keys) + list(absent_keys),
                            'artifact': range(2 * len(absent_keys))})
    widened = pd.concat([cases, unbound])
    npt.assert_array_equal(
        np.sort(widened.merge(approvals, on='case_id')['case_id'].to_numpy()),
        np.sort(cases.merge(approvals, on='case_id', validate='one_to_one')['case_id'].to_numpy()))
    with pytest.raises(pd.errors.MergeError):
        widened.merge(approvals, on='case_id', validate='one_to_one')
    with pytest.raises(pl.exceptions.ComputeError):
        pl.from_pandas(widened).join(pl.from_pandas(approvals), on='case_id', how='inner',
                                     validate='1:1')


@pytest.mark.skipif(not (ruby_available and php_binary_available),
                    reason='the ruby and php runtimes are required for these oracles')
@given(GATE_DATES, GATE_DATES)
@ORACLE_PROCESS
def test_a_zero_padded_iso_date_orders_as_text_the_way_three_runtimes_order_the_day(signed_on,
                                                                                   evaluated_at):
    """P199 decides whether an approval post-dates the evaluation time by comparing two date records as
    text. On the zero-padded form that ordering is the calendar ordering: CPython's date comparison,
    Ruby's Julian day number from Date.parse (ext/date/date_core.c at tag v3_3_6) and PHP's instant from
    DateTimeImmutable order every generated pair the same way the text does, and both runtimes read each
    record back as the same calendar day. This is the region in which the gate's time clause means what it
    says, and the two tests after it generate the regions in which it does not."""
    on, at = signed_on.isoformat(), evaluated_at.isoformat()
    ruby_on, ruby_at = _ruby_calendar_day(on), _ruby_calendar_day(at)
    php_on, php_at = _php_calendar_day(on), _php_calendar_day(at)
    npt.assert_array_equal([ruby_on[0], php_on[0]], [on, on])
    npt.assert_array_equal(on > at, signed_on > evaluated_at)
    npt.assert_array_equal(int(ruby_on[1]) > int(ruby_at[1]), signed_on > evaluated_at)
    npt.assert_array_equal(int(php_on[1]) > int(php_at[1]), signed_on > evaluated_at)


@pytest.mark.skipif(not (ruby_available and php_binary_available),
                    reason='the ruby and php runtimes are required for these oracles')
@given(GATE_YEAR, SINGLE_DIGIT_MONTH, TWO_DAYS)
@ORACLE_PROCESS
def test_a_date_written_without_zero_padding_reverses_the_order_the_runtimes_agree_on(year, month, days):
    """An approval recorded earlier in the same month, written without the leading zero on the month, sorts
    after the evaluation date as text and before it as a date. The region is generated rather than filtered
    for: a one-digit month puts a digit from one to nine where the padded record has a zero, so every pair
    the strategy draws diverges. Ruby's Date.parse and PHP's DateTimeImmutable both read the unpadded
    record as the same calendar day CPython's date does, and both order it before the evaluation date, so
    the disagreement is the gate's text comparison and not the record. What the gate returns for it is
    'blocked: approval post-dates the evaluation time' for an approval that precedes it."""
    signed_on, evaluated_at = datetime.date(year, month, days[0]), datetime.date(year, month, days[1])
    unpadded = '%d-%d-%d' % (year, month, days[0])
    at = evaluated_at.isoformat()
    ruby_on, ruby_at = _ruby_calendar_day(unpadded), _ruby_calendar_day(at)
    php_on, php_at = _php_calendar_day(unpadded), _php_calendar_day(at)
    npt.assert_array_equal([ruby_on[0], php_on[0]], [signed_on.isoformat(), signed_on.isoformat()])
    npt.assert_array_equal(int(ruby_on[1]) < int(ruby_at[1]), signed_on < evaluated_at)
    npt.assert_array_equal(int(php_on[1]) < int(php_at[1]), signed_on < evaluated_at)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(unpadded > at, signed_on > evaluated_at)


@pytest.mark.skipif(not (ruby_available and php_binary_available),
                    reason='the ruby and php runtimes are required for these oracles')
@given(GATE_DATES, TIME_OF_DAY)
@ORACLE_PROCESS
def test_an_approval_stamped_on_the_evaluation_day_reads_as_post_dating_it(evaluated_at, clock):
    """The same clause on the other kind of record. An approval carrying a timestamp is longer than the
    date it falls on and therefore greater as text at every hour of that day, including midnight. Ruby and
    PHP both read the stamp as the evaluation date itself, so all three readings agree the approval was
    signed on the day the gate is evaluated for, and the text comparison alone calls it later. The clause
    that is meant to catch an approval dated after the evaluation blocks every approval signed on the
    day."""
    at = evaluated_at.isoformat()
    stamped = '%sT%02d:%02d:%02d' % ((at,) + clock)
    npt.assert_array_equal([_ruby_calendar_day(stamped)[0], _php_calendar_day(stamped)[0]], [at, at])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(stamped > at, _php_calendar_day(stamped)[0] > at)


@given(GATE_YEAR, SINGLE_DIGIT_MONTH, TWO_DAYS)
@SLOW
def test_the_declared_date_validator_and_the_gate_comparison_cannot_both_be_used(year, month, days):
    """P199's chain declares that the time field is validated by a pydantic model before the gate reads it.
    Executed, the two steps exclude each other. pydantic 2.13.5's TypeAdapter for datetime.date returns a
    datetime.date for the padded record, and the gate's comparison of that value against the evaluation
    text is a TypeError and not a decision; while the unpadded record, the one the text comparison orders
    backwards, is refused by the validator. So the field is either validated, and then not comparable, or
    comparable, and then unvalidated, and the chain names both steps. Replaces the typed
    'blocked: approval post-dates the evaluation time' of handoff_guards_v21.py case 199."""
    adapter = pydantic.TypeAdapter(datetime.date)
    signed_on = datetime.date(year, month, days[0])
    validated = adapter.validate_python(signed_on.isoformat())
    npt.assert_array_equal(validated.isoformat(), signed_on.isoformat())
    with pytest.raises(TypeError):
        operator.gt(validated, datetime.date(year, month, days[1]).isoformat())
    with pytest.raises(pydantic.ValidationError):
        adapter.validate_python('%d-%d-%d' % (year, month, days[0]))


@given(GATE_DATES, st.times(min_value=datetime.time(0, 0, 1)))
@SLOW
def test_the_validator_refuses_the_same_day_stamp_at_every_time_but_midnight(day, clock):
    """The other record the text comparison gets wrong, an approval stamped with a clock time on the
    evaluation day, is refused by the same validator at every second of the day except one. pydantic
    documents the rule at v2.13.5 as "If the validation fails, the input can be validated as a datetime
    (including as numbers), provided that the time component is 0 and that it is naive."
    (docs/api/standard_library_types.md). Executed, that is what happens: every generated non-zero clock
    time is a ValidationError and midnight is accepted and returns the bare date, so the time the record
    carried is gone rather than compared."""
    adapter = pydantic.TypeAdapter(datetime.date)
    with pytest.raises(pydantic.ValidationError):
        adapter.validate_python('%sT%s' % (day.isoformat(), clock.isoformat()))
    npt.assert_array_equal(
        adapter.validate_python('%sT%s' % (day.isoformat(), datetime.time().isoformat())).isoformat(),
        day.isoformat())


@pytest.mark.skipif(not php_binary_available, reason='the php runtime is required for this oracle')
@given(GATE_DATES, OFFSET_HOURS)
@ORACLE_PROCESS
def test_the_validator_takes_an_offset_midnight_as_the_local_date_its_own_rule_excludes(day, offset):
    """The same rule, executed on the records it says it excludes. "provided that the time component is 0
    and that it is naive" is pydantic's documented condition, and a midnight stamp carrying an offset is
    not naive; executed, every generated offset from minus fourteen to plus fourteen hours is accepted and
    validates to the local calendar date the record was written with, the offset discarded. The same
    instant written in UTC, which PHP's DateTimeImmutable confirms is the same instant by counting it to
    the same second, is refused with date_from_datetime_inexact. So which day an approval is dated to is
    the offset its recorder chose, and the two spellings of one moment reach the gate as one date and one
    refusal."""
    adapter = pydantic.TypeAdapter(datetime.date)
    zone = datetime.timezone(datetime.timedelta(hours=offset))
    local = datetime.datetime.combine(day, datetime.time(), tzinfo=zone)
    in_utc = local.astimezone(datetime.timezone.utc)
    npt.assert_array_equal(_php_calendar_day(local.isoformat())[1],
                           _php_calendar_day(in_utc.isoformat())[1])
    npt.assert_array_equal(adapter.validate_python(local.isoformat()).isoformat(), day.isoformat())
    with pytest.raises(pydantic.ValidationError):
        adapter.validate_python(in_utc.isoformat())


# ---------------------------------------------------------------- declared membership and unknown quantity
MEMBERSHIP_START = st.dates(min_value=datetime.date(2000, 1, 1), max_value=datetime.date(2099, 1, 1))
SPAN_DAYS = st.integers(min_value=1, max_value=60)
KNOWN_NETS = st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=10)
UNKNOWN_POSITION = st.integers(min_value=0, max_value=20)
CLOSURE_NAMES = (('both', 'both'), ('left', 'left'), ('right', 'right'), ('neither', 'none'))


def _duckdb_dates(start, end, function):
    """The same date span from one of DuckDB's two range functions, which its documentation says differ
    only in whether the stop argument is included."""
    with duckdb.connect() as connection:
        rows = connection.execute("select unnest(%s(DATE '%s', DATE '%s', INTERVAL 1 DAY))"
                                  % (function, start.isoformat(), end.isoformat())).fetchall()
    return np.array([row[0].date() for row in rows], dtype='datetime64[D]')


def _shortfall_quantities(known, position):
    """One quantity per generated value plus one that is unknown, inserted at a generated position, so the
    unknown line is always present and is never authored as a fixture."""
    quantities = list(known)
    quantities.insert(position % (len(quantities) + 1), None)
    return quantities


def _duckdb_lines(quantities, query):
    """The same line list in SQL, with the unknown quantity carried across as a NULL."""
    with duckdb.connect() as connection:
        connection.register('lines', pd.DataFrame({'line': range(len(quantities)),
                                                   'net': pd.Series(quantities, dtype='Int64')}))
        return np.array([row[0] for row in connection.execute(query).fetchall()])


@given(MEMBERSHIP_START, SPAN_DAYS)
@SLOW
def test_the_date_range_default_includes_the_declared_end_date_in_three_engines(start, days):
    """P172 reads a membership window as start-inclusive and end-exclusive and builds it with
    pandas.date_range, whose parameter is documented at
    raw.githubusercontent.com/pandas-dev/pandas/v2.2.3/pandas/core/indexes/datetimes.py as
    'inclusive : {"both", "neither", "left", "right"}, default "both"'. polars' date_range carries the
    same default, 'closed: ClosedInterval = "both"' at tag py-1.44.1, and DuckDB's generate_series is
    documented as "Both the `start` and the `stop` parameters are inclusive." All three return the end
    date the chain declares excluded. Replaces the typed len(both) == 20 and both[-1] == '2026-09-20' of
    handoff_guards_v19.py case 172."""
    end = start + datetime.timedelta(days=days)
    in_pandas = pd.date_range(start, end).to_numpy().astype('datetime64[D]')
    npt.assert_array_equal(in_pandas, pl.date_range(start, end, eager=True).to_numpy())
    npt.assert_array_equal(in_pandas, _duckdb_dates(start, end, 'generate_series'))
    npt.assert_array_equal(in_pandas[-1], np.datetime64(end))


@given(MEMBERSHIP_START, SPAN_DAYS)
@SLOW
def test_the_end_exclusive_window_the_chain_declares_is_a_named_option_in_all_three(start, days):
    """The declared reading exists in every engine under a name. pandas takes inclusive='left', polars
    closed='left', and DuckDB's range is documented as "The `start` parameter is inclusive, while the
    `stop` parameter is exclusive." The three agree over generated spans, and the window the default
    returns is that window with the end date appended, which is the whole of the difference. Replaces the
    typed len(left) == 19, left[-1] == '2026-09-19' and len(both) - len(left) == 1 of case 172."""
    end = start + datetime.timedelta(days=days)
    in_pandas = pd.date_range(start, end, inclusive='left').to_numpy().astype('datetime64[D]')
    npt.assert_array_equal(in_pandas, pl.date_range(start, end, closed='left', eager=True).to_numpy())
    npt.assert_array_equal(in_pandas, _duckdb_dates(start, end, 'range'))
    npt.assert_array_equal(np.append(in_pandas, np.datetime64(end)),
                           pd.date_range(start, end).to_numpy().astype('datetime64[D]'))


@given(MEMBERSHIP_START, SPAN_DAYS)
@SLOW
def test_the_two_duckdb_range_functions_answer_the_same_question_differently(start, days):
    """One engine ships both readings under two names, which is what makes the closure a declaration
    rather than a default. DuckDB's own documentation says of the pair "The two functions' behavior is
    different regarding their `stop` argument."; executed over generated spans the two lists are never
    equal, and the inclusive one is the exclusive one with the end date appended."""
    end = start + datetime.timedelta(days=days)
    exclusive = _duckdb_dates(start, end, 'range')
    inclusive = _duckdb_dates(start, end, 'generate_series')
    with pytest.raises(AssertionError):
        npt.assert_array_equal(exclusive, inclusive)
    npt.assert_array_equal(np.append(exclusive, np.datetime64(end)), inclusive)


@given(MEMBERSHIP_START, SPAN_DAYS)
@SLOW
def test_the_two_membership_primitives_of_one_chain_close_opposite_ends(start, days):
    """P172 lists the days with date_range and holds the assignment window in a pandas.Interval, and the
    two defaults are opposites: date_range is documented default "both" and Interval is documented
    "closed : {'right', 'left', 'both', 'neither'}, default 'right'" in pandas/_libs/interval.pyx at tag
    v2.2.3. Over the same two bounds the default day list contains the start date and the default interval
    does not. portion 2.6.2 answers the two questions the same way for the closure pandas defaults to, so
    the exclusion is the closure and not pandas. Replaces the typed pd.Interval(0, 1).closed == 'right'
    of case 172."""
    end = start + datetime.timedelta(days=days)
    default_interval = pd.Interval(pd.Timestamp(start), pd.Timestamp(end))
    npt.assert_array_equal([pd.Timestamp(start) in default_interval, pd.Timestamp(end) in default_interval],
                           [start in portion.openclosed(start, end), end in portion.openclosed(start, end)])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(pd.Timestamp(start) in default_interval,
                               pd.Timestamp(start) in pd.date_range(start, end))


@given(MEMBERSHIP_START, SPAN_DAYS)
@SLOW
def test_a_left_closed_and_a_right_closed_window_never_agree_on_either_bound(start, days):
    """The declared window is start-inclusive and end-exclusive, which is Interval(closed='left'); the
    default is its mirror. Over generated bounds the two disagree about both endpoints and agree about
    every day strictly between them, and portion returns the same pair of answers for the same closure.
    Replaces the typed membership expectations of case 172, which asked the two closures about the two
    endpoints one date at a time."""
    end = start + datetime.timedelta(days=days)
    left = pd.Interval(pd.Timestamp(start), pd.Timestamp(end), closed='left')
    right = pd.Interval(pd.Timestamp(start), pd.Timestamp(end), closed='right')
    npt.assert_array_equal([pd.Timestamp(start) in left, pd.Timestamp(end) in left],
                           [start in portion.closedopen(start, end), end in portion.closedopen(start, end)])
    with pytest.raises(AssertionError):
        npt.assert_array_equal([pd.Timestamp(start) in left, pd.Timestamp(end) in left],
                               [pd.Timestamp(start) in right, pd.Timestamp(end) in right])
    inside = pd.date_range(start, end, inclusive='neither')
    npt.assert_array_equal([day in left for day in inside], [day in right for day in inside])


@given(MEMBERSHIP_START, SPAN_DAYS)
@SLOW
def test_each_of_the_four_closures_is_a_different_window_in_two_engines(start, days):
    """pandas and polars each offer four closures and agree closure by closure over generated spans, and
    the four windows are six pairwise different day lists. So the window a chain gets is entirely the
    argument it passes; there is no reading of the bounds that the libraries settle on, and the one the
    chain declares is not the one it gets by saying nothing."""
    end = start + datetime.timedelta(days=days)
    windows = []
    for in_pandas, in_polars in CLOSURE_NAMES:
        listed = pd.date_range(start, end, inclusive=in_pandas).to_numpy().astype('datetime64[D]')
        npt.assert_array_equal(listed, pl.date_range(start, end, closed=in_polars, eager=True).to_numpy())
        windows.append(listed)
    for first, second in itertools.combinations(windows, 2):
        with pytest.raises(AssertionError):
            npt.assert_array_equal(first, second)


@given(KNOWN_NETS, UNKNOWN_POSITION)
@SLOW
def test_an_unknown_quantity_compares_as_false_in_one_dtype_and_as_unknown_in_three_engines(known,
                                                                                           position):
    """P174 requires an unknown shortfall to stay unknown rather than become a zero request. Whether the
    comparison that sorts the lines keeps it unknown depends on the dtype the frame happens to carry.
    pandas' own missing-data guide at tag v2.2.3 says "In equality and comparison operations,
    :class:`NA` also propagates. This deviates from the behaviour of ``np.nan``, where comparisons with
    ``np.nan`` always return ``False``." Executed, that is the split: the float64 column answers False for
    the unknown line and names nothing, while the nullable Int64 column, polars and DuckDB all answer
    unknown and name the same line. DuckDB documents the rule as "Any comparison with a `NULL` value
    returns `NULL`, including `NULL = NULL`." Replaces the typed unknown[0]['requested'] is None of
    handoff_guards_v19.py case 174."""
    quantities = _shortfall_quantities(known, position)
    as_float = pd.Series(quantities, dtype='float64') > 0
    as_nullable = pd.Series(quantities, dtype='Int64') > 0
    npt.assert_array_equal(pd.isna(as_nullable).to_numpy(),
                           pl.Series(quantities).gt(0).is_null().to_numpy())
    npt.assert_array_equal(np.flatnonzero(pd.isna(as_nullable).to_numpy()),
                           _duckdb_lines(quantities,
                                         'select line from lines where (net > 0) is null order by line'))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(pd.isna(as_float).to_numpy(), pd.isna(as_nullable).to_numpy())


@given(KNOWN_NETS, UNKNOWN_POSITION)
@SLOW
def test_every_engine_totals_the_unknown_quantity_as_a_zero(known, position):
    """Whatever the comparison does, the total does the same thing in all four readings. pandas' sum skips
    the missing value by default in both dtypes, polars' sum ignores nulls and DuckDB's SUM ignores them,
    so the column total of a line list carrying one unknown shortfall is the total of the known lines
    alone. The unknown becomes a zero the moment anything is added up, which is the state P174's contract
    says must not happen."""
    quantities = _shortfall_quantities(known, position)
    npt.assert_array_equal(pd.Series(quantities, dtype='float64').sum(), sum(known))
    npt.assert_array_equal(pd.Series(quantities, dtype='Int64').sum(), sum(known))
    npt.assert_array_equal(pl.Series(quantities).sum(), sum(known))
    npt.assert_array_equal(_duckdb_lines(quantities, 'select sum(net) from lines'), sum(known))


@given(KNOWN_NETS, UNKNOWN_POSITION)
@SLOW
def test_the_requested_lines_are_the_same_rows_in_four_readings_and_the_unknown_is_in_none(known,
                                                                                          position):
    """The half that does agree. Selecting the lines whose net quantity is above zero returns the same
    rows in the float64 frame, the nullable frame, polars and DuckDB, and the unknown line is in none of
    them, because a filter keeps only what the comparison called true and neither False nor unknown is
    true. Replaces the typed [r['item'] for r in requested] == ['cable', 'desk'] of case 174."""
    quantities = _shortfall_quantities(known, position)
    lines = pd.DataFrame({'line': range(len(quantities))})
    as_float = pd.Series(quantities, dtype='float64')
    as_nullable = pd.Series(quantities, dtype='Int64')
    requested = lines['line'][(as_float > 0)].to_numpy()
    npt.assert_array_equal(requested, lines['line'][(as_nullable > 0)].to_numpy())
    npt.assert_array_equal(requested, pl.DataFrame({'line': np.arange(len(quantities)),
                                                    'net': pl.Series(quantities)})
                           .filter(pl.col('net') > 0)['line'].to_numpy())
    npt.assert_array_equal(requested, _duckdb_lines(
        quantities, 'select line from lines where net > 0 order by line'))


@given(KNOWN_NETS, UNKNOWN_POSITION)
@SLOW
def test_the_lines_that_are_not_requested_hold_the_unknown_in_one_reading_and_lose_it_in_three(known,
                                                                                              position):
    """The other half does not agree, and this is the finding. Negating the same comparison keeps the
    unknown line in the float64 frame, where it is indistinguishable from a line whose shortfall is a
    real zero, and drops it in the nullable frame, in polars and in DuckDB, where not unknown is unknown
    and unknown is not true. So in three of the four readings the unknown line is in neither the requested
    set nor its complement: the two queries a reader would write to cover every line cover every line but
    that one, and nothing reports it. Replaces the typed
    unknown[0]['requested'] == absent[0]['requested'] being False of case 174."""
    quantities = _shortfall_quantities(known, position)
    lines = pd.DataFrame({'line': range(len(quantities))})
    as_float = pd.Series(quantities, dtype='float64')
    as_nullable = pd.Series(quantities, dtype='Int64')
    float_rest = lines['line'][~(as_float > 0)].to_numpy()
    nullable_rest = lines['line'][~(as_nullable > 0)].to_numpy()
    npt.assert_array_equal(nullable_rest, pl.DataFrame({'line': np.arange(len(quantities)),
                                                        'net': pl.Series(quantities)})
                           .filter(~(pl.col('net') > 0))['line'].to_numpy())
    npt.assert_array_equal(nullable_rest, _duckdb_lines(
        quantities, 'select line from lines where not (net > 0) order by line'))
    npt.assert_array_equal(np.sort(np.append(nullable_rest, quantities.index(None))),
                           np.sort(float_rest))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(float_rest, nullable_rest)


# ---------------------------------------------------------------- normalization, offsets and edit scripts
NORMALIZE_RUBY_ORACLE = pathlib.Path(__file__).with_name('unicode_normalize_oracle.rb')
COMPATIBILITY = ''.join(letter for letter in map(chr, range(0xA0, 0x2100))
                        if unicodedata.decomposition(letter).startswith('<')
                        and unicodedata.normalize('NFC', letter) == letter
                        and unicodedata.normalize('NFKC', letter) != letter)
COMPATIBILITY_TEXT = st.text(alphabet=COMPATIBILITY, min_size=1, max_size=6)
LOWER_LETTER = st.characters(min_codepoint=ord('a'), max_codepoint=ord('z'))
UPPER_LETTER = st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z'))
DISTINCT_LETTERS = st.lists(LOWER_LETTER, min_size=1, max_size=12, unique=True).map(''.join)
TWO_LETTERS = st.lists(LOWER_LETTER, min_size=2, max_size=2, unique=True).map(''.join)
REPEAT_AND_POSITION = st.integers(min_value=5, max_value=60).flatmap(
    lambda count: st.tuples(st.just(count), st.integers(min_value=1, max_value=count - 1)))
LONG_REPEAT_AND_POSITION = st.integers(min_value=100, max_value=180).flatmap(
    lambda count: st.tuples(st.just(count), st.integers(min_value=1, max_value=count - 1)))


def _ruby_normalized(form, text):
    """The normalized text, its length in characters and its length in bytes, as Ruby's own pure-Ruby
    implementation computes them. Text crosses in and out as hex so nothing depends on a locale."""
    completed = subprocess.run(['ruby', str(NORMALIZE_RUBY_ORACLE), form, text.encode().hex()],
                               capture_output=True, text=True, check=True)
    printed = completed.stdout.split()
    return bytes.fromhex(printed[0]).decode(), int(printed[1]), int(printed[2])


def _edit_kinds(before, after, **options):
    """The kinds of change difflib reports, in order, with the equal runs left out."""
    return [opcode[0] for opcode in difflib.SequenceMatcher(a=before, b=after, **options).get_opcodes()
            if opcode[0] != 'equal']


def _rapidfuzz_kinds(before, after):
    """The same list read off rapidfuzz's own edit script."""
    return [opcode.tag for opcode in rf_levenshtein.opcodes(before, after) if opcode.tag != 'equal']


@pytest.mark.skipif(not ruby_available, reason='the ruby runtime is required for this oracle')
@given(ACCENTED_TEXT)
@ORACLE_PROCESS
def test_three_normalizers_agree_on_the_composed_form_of_generated_text(text):
    """P195 measures a clause before and after Unicode normalization and reports what moved. Three
    implementations of NFC that share no code agree on the composed form of every generated accented
    string: CPython's unicodedata, polars' str.normalize, which is the Rust unicode-normalization crate
    declared in crates/polars-ops/Cargo.toml at tag py-1.44.1 and documented as returning "the Unicode
    normal form of the string values" using "the forms described in Unicode Standard Annex 15", and
    Ruby's String#unicode_normalize, written in Ruby in lib/unicode_normalize/normalize.rb at tag v3_3_6
    by Ayumu Nojima and Martin J. Durst. What the next tests record is therefore a property of the
    normal form and not of one library."""
    decomposed = unicodedata.normalize('NFD', text)
    composed = unicodedata.normalize('NFC', decomposed)
    plt.assert_series_equal(pl.Series([composed]), pl.Series([decomposed]).str.normalize('NFC'))
    npt.assert_array_equal(composed, _ruby_normalized('nfc', decomposed)[0])


@pytest.mark.skipif(not ruby_available, reason='the ruby runtime is required for this oracle')
@given(ACCENTED_TEXT)
@ORACLE_PROCESS
def test_normalizing_changes_both_counts_an_offset_could_be_taken_in(text):
    """The measurement P195 asks for. The three implementations agree on how long the composed text is,
    in characters and in bytes, and both counts differ from the counts of the text the offsets were taken
    in. So a span recorded as a character range or as a byte range over the raw clause is a span of a
    different length in the normalized one. Replaces the typed raw_codepoints == 14, nfc_codepoints == 13,
    raw_bytes == 15 and nfc_bytes == 14 of handoff_guards_v21.py case 195."""
    decomposed = unicodedata.normalize('NFD', text)
    composed = unicodedata.normalize('NFC', decomposed)
    npt.assert_array_equal([len(composed), len(composed.encode())],
                           list(_ruby_normalized('nfc', decomposed)[1:]))
    in_polars = pl.Series([decomposed]).str.normalize('NFC')
    npt.assert_array_equal([len(composed), len(composed.encode())],
                           [in_polars.str.len_chars()[0], in_polars.str.len_bytes()[0]])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(len(decomposed), len(composed))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(len(decomposed.encode()), len(composed.encode()))


@given(ACCENTED_TEXT)
@SLOW
def test_an_offset_into_the_raw_text_does_not_index_the_normalized_one(text):
    """What the length difference costs. Every character of the generated text has a canonical
    decomposition, so the decomposed spelling is strictly longer, and the last offset that indexes it is
    past the end of the composed one: the primitive raises IndexError rather than returning a character.
    Below that, the two spellings do not agree character by character either, so an offset that is still
    in range selects something else. Replaces the typed length_preserved == False of case 195."""
    decomposed = unicodedata.normalize('NFD', text)
    composed = unicodedata.normalize('NFC', decomposed)
    with pytest.raises(IndexError):
        operator.getitem(composed, len(decomposed) - 1)
    inside = min(len(composed), len(decomposed))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(list(decomposed[:inside]), list(composed[:inside]))


@pytest.mark.skipif(not ruby_available, reason='the ruby runtime is required for this oracle')
@given(ACCENTED_TEXT)
@ORACLE_PROCESS
def test_two_spellings_that_compare_unequal_are_one_string_after_normalizing(text):
    """The other half of P195's claim. The composed and decomposed spellings of one clause are two
    different strings to polars' comparison, and one string once either is normalized, in CPython, in
    polars and in Ruby alike. So an equality test run after normalizing reports no change to a clause
    whose recorded bytes did change, and the change is invisible to exactly the check a chain would use
    to look for it. Replaces the typed composed == precomposed being False and
    unicodedata.normalize('NFC', composed) == precomposed being True of case 195."""
    composed = unicodedata.normalize('NFC', text)
    decomposed = unicodedata.normalize('NFD', text)
    plt.assert_series_not_equal(pl.Series([composed]), pl.Series([decomposed]))
    plt.assert_series_equal(pl.Series([composed]).str.normalize('NFC'),
                            pl.Series([decomposed]).str.normalize('NFC'))
    npt.assert_array_equal(_ruby_normalized('nfc', composed)[0], _ruby_normalized('nfc', decomposed)[0])


@pytest.mark.skipif(not ruby_available, reason='the ruby runtime is required for this oracle')
@given(ACCENTED_TEXT)
@ORACLE_PROCESS
def test_normalizing_twice_is_normalizing_once_in_three_implementations(text):
    """Idempotence is the property that makes a normalized record storable, and all three implementations
    have it over generated text: normalizing the composed form again returns it unchanged. It is also
    what makes the loss one-way, because the raw offsets cannot be recovered from the stored form."""
    composed = unicodedata.normalize('NFC', unicodedata.normalize('NFD', text))
    npt.assert_array_equal(unicodedata.normalize('NFC', composed), composed)
    plt.assert_series_equal(pl.Series([composed]).str.normalize('NFC'), pl.Series([composed]))
    npt.assert_array_equal(_ruby_normalized('nfc', composed)[0], composed)


@pytest.mark.skipif(not ruby_available, reason='the ruby runtime is required for this oracle')
@given(COMPATIBILITY_TEXT)
@ORACLE_PROCESS
def test_the_compatibility_form_rewrites_text_the_canonical_form_leaves_alone(text):
    """Which normal form a chain names is itself a decision, and the alphabet these examples are drawn
    from is built from the Unicode database rather than chosen here: every character in it carries a
    compatibility decomposition, is its own canonical form, and is not its own compatibility form. On
    that text NFC changes nothing and NFKC changes every character, in CPython, in polars and in Ruby.
    So a chain that says only "normalization" has not said whether the recorded clause survives."""
    npt.assert_array_equal(unicodedata.normalize('NFC', text), text)
    plt.assert_series_equal(pl.Series([text]).str.normalize('NFC'), pl.Series([text]))
    plt.assert_series_not_equal(pl.Series([text]).str.normalize('NFKC'), pl.Series([text]))
    npt.assert_array_equal(unicodedata.normalize('NFKC', text), _ruby_normalized('nfkc', text)[0])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(unicodedata.normalize('NFKC', text), text)


@given(DISTINCT_LETTERS, UPPER_LETTER, st.integers(min_value=0, max_value=20))
@SLOW
def test_two_edit_scripts_agree_on_one_insertion_deletion_or_replacement(base, marker, position):
    """P195 reports what kind of change was made between two versions of a clause, and reads the kinds off
    difflib's opcodes. Where the clause has no repeated character and the edit introduces one that is not
    in it, difflib and rapidfuzz 3.14.6's own edit script agree on all three kinds over generated bases
    and positions. Replaces the typed change_kinds(...) == ['insert'], ['replace'], ['delete'] and [] of
    case 195."""
    at = position % len(base)
    npt.assert_array_equal(_edit_kinds(base, base), _rapidfuzz_kinds(base, base))
    for after in (base[:at] + marker + base[at:], base[:at] + base[at + 1:],
                  base[:at] + marker + base[at + 1:]):
        npt.assert_array_equal(_edit_kinds(base, after), _rapidfuzz_kinds(base, after))


@given(TWO_LETTERS, UPPER_LETTER, REPEAT_AND_POSITION)
@SLOW
def test_the_two_edit_scripts_disagree_about_a_substitution_inside_a_repeating_run(letters, marker,
                                                                                  shape):
    """Where the clause repeats, they do not agree, and difflib says so about itself. Its documentation at
    raw.githubusercontent.com/python/cpython/v3.11.15/Doc/library/difflib.rst describes the algorithm as
    finding "the longest contiguous matching subsequence" recursively and warns "This does not yield
    minimal edit sequences, but does tend to yield matches that "look right" to people." Executed on a
    generated repeating run with one character replaced in its first half, rapidfuzz returns one operation,
    which is the edit distance it also reports, and difflib returns more than that, an insertion and a
    deletion where one substitution was made. So the kind of change a version report names depends on
    which differ ran."""
    count, at = shape
    base = letters * count
    after = base[:at] + marker + base[at + 1:]
    npt.assert_array_equal(len(_rapidfuzz_kinds(base, after)), rf_levenshtein.distance(base, after))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(len(_edit_kinds(base, after)), rf_levenshtein.distance(base, after))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_edit_kinds(base, after), _rapidfuzz_kinds(base, after))


@given(TWO_LETTERS, UPPER_LETTER, LONG_REPEAT_AND_POSITION)
@SLOW
def test_the_same_edit_gets_a_different_report_once_the_clause_is_long_enough(letters, marker, shape):
    """And the same differ reports the same edit two ways according to how long the surrounding text is.
    difflib documents the reason at the same tag: "If an item's duplicates (after the first one) account
    for more than 1% of the sequence and the sequence is at least 200 items long, this item is marked as
    "popular" and is treated as junk for the purpose of sequence matching. This heuristic can be turned
    off by setting the ``autojunk`` argument to ``False``". The generated runs here are at least two
    hundred characters, so the heuristic is on: difflib now agrees with rapidfuzz that one substitution
    was made, and disagrees with itself run with autojunk off, which returns what it returned for the
    shorter run. A change report is therefore a function of the length of the document it is taken in."""
    count, at = shape
    base = letters * count
    after = base[:at] + marker + base[at + 1:]
    npt.assert_array_equal(_edit_kinds(base, after), _rapidfuzz_kinds(base, after))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_edit_kinds(base, after), _edit_kinds(base, after, autojunk=False))


# ---------------------------------------------------------------- what the two parser families read back
PASSAGE_TEMPLATE = '<ul>{% for p in passages %}<li id="{{ p.id }}">{{ p.text }}</li>{% endfor %}</ul>'
SAFE_LETTERS = st.text(alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z')),
                       min_size=1, max_size=8)


def _rendered_page(texts, *, autoescape):
    """The chain's own page, rendered by jinja2 with escaping on or off, one list item per passage."""
    environment = jinja2.Environment(undefined=jinja2.StrictUndefined, autoescape=autoescape)
    return environment.from_string(PASSAGE_TEMPLATE).render(
        passages=[{'id': 'p%d' % index, 'text': text} for index, text in enumerate(texts)])


def _lxml_rows(markup):
    """The passage text libxml2's HTML parser reads back, one entry per list item."""
    return [node.text_content() for node in lxml_html.fromstring(markup).xpath('//li')]


def _html5lib_rows(markup):
    """The same list from html5lib 1.1, which its README at tag 1.1 calls "a pure-python library for
    parsing HTML" that "is designed to conform to the WHATWG HTML specification", and whose setup.py at
    that tag declares six and webencodings; lxml appears there only as an optional extra and the etree
    treebuilder asked for here does not reach it."""
    tree = html5lib.parse(markup, treebuilder='etree', namespaceHTMLElements=False)
    return [''.join(node.itertext()) for node in tree.iter('li')]


def _lxml_identifiers(markup):
    """The id attribute of every list item, as libxml2 reads them."""
    return [node.get('id') for node in lxml_html.fromstring(markup).xpath('//li')]


def _html5lib_identifiers(markup):
    """The same attributes from the second parser."""
    tree = html5lib.parse(markup, treebuilder='etree', namespaceHTMLElements=False)
    return [node.get('id') for node in tree.iter('li')]


def _both_xml_parsers_refuse(markup):
    """Whether both XML parsers refuse these bytes. Called once, at import, to read the region the tests
    generate in off the parsers rather than name it here."""
    for parse in (lxml_etree.fromstring, ElementTree.fromstring):
        try:
            parse(markup)
        except Exception:
            continue
        return False
    return True


XML_UNSAFE_CHARACTERS = [character for character in ESCAPABLE_CHARACTERS
                         if _both_xml_parsers_refuse(_rendered_page([character], autoescape=False))]
XML_UNSAFE_TEXT = st.text(alphabet=st.sampled_from(XML_UNSAFE_CHARACTERS), min_size=1, max_size=6)


@given(st.lists(ESCAPABLE_TEXT, min_size=1, max_size=4))
@SLOW
def test_two_html_parsers_read_the_same_passages_out_of_an_escaped_page(texts):
    """P181 renders authored passages into a page and reads them back with lxml's HTML parser. Two
    implementations of HTML parsing that share no code agree on what the escaped page says: libxml2's C
    parser through lxml 6.1.3, and html5lib 1.1, a pure-Python implementation of the WHATWG algorithm.
    Both return every generated passage exactly as it was written, which is the round trip the chain
    claims. Replaces the typed parsed_texts(escaped_page(...)) == [passages[0]['text']] of
    handoff_guards_v20.py case 181."""
    page = _rendered_page(texts, autoescape=True)
    npt.assert_array_equal(_lxml_rows(page), _html5lib_rows(page))
    npt.assert_array_equal(_lxml_rows(page), texts)


@given(st.lists(XML_UNSAFE_TEXT, min_size=1, max_size=4))
@SLOW
def test_the_unescaped_page_reads_back_correctly_in_html_and_is_refused_as_xml(texts):
    """The same passages rendered with escaping off produce bytes that are not XML, and the round trip
    still looks correct. Both HTML parsers return every passage exactly as written, so a check that reads
    the page back and compares finds nothing wrong; both XML parsers refuse the same bytes outright, lxml
    with XMLSyntaxError and the standard library's expat binding with ParseError. The characters this is
    generated from were read off the two XML parsers at import rather than named here. Replaces the typed
    g.rejects(etree.XMLSyntaxError, ...) of case 181."""
    page = _rendered_page(texts, autoescape=False)
    npt.assert_array_equal(_lxml_rows(page), _html5lib_rows(page))
    npt.assert_array_equal(_lxml_rows(page), texts)
    with pytest.raises(lxml_etree.XMLSyntaxError):
        lxml_etree.fromstring(page)
    with pytest.raises(ElementTree.ParseError):
        ElementTree.fromstring(page)
    escaped = _rendered_page(texts, autoescape=True)
    npt.assert_array_equal([node.text for node in lxml_etree.fromstring(escaped)],
                           [node.text for node in ElementTree.fromstring(escaped)])


@given(SAFE_LETTERS, SAFE_LETTERS)
@SLOW
def test_literal_markup_in_a_passage_is_consumed_with_the_row_count_unchanged(before, inside):
    """A passage that contains markup is not refused and does not change the shape of the page: both HTML
    parsers drop the tags, keep the text between them, and return as many rows as the escaped page does.
    So the one thing a chain counting rows would notice is exactly the thing that does not change, while
    the passage text it reads back is not the passage text it rendered. Replaces the typed
    parsed_texts(...) == ['see bold here'] and the unchanged element count of case 181."""
    marked = '%s<b>%s</b>' % (before, inside)
    page = _rendered_page([marked], autoescape=False)
    npt.assert_array_equal(_lxml_rows(page), _html5lib_rows(page))
    npt.assert_array_equal(_lxml_rows(page), [before + inside])
    npt.assert_array_equal(len(_lxml_rows(page)),
                           len(_lxml_rows(_rendered_page([marked], autoescape=True))))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_lxml_rows(page), [marked])


@given(SAFE_LETTERS, SAFE_LETTERS)
@SLOW
def test_an_unescaped_closing_tag_manufactures_a_second_row_in_both_html_parsers(first, second):
    """One passage carrying a closing tag becomes two rows, in libxml2 and in html5lib alike, and the two
    parsers split it in the same place. Escaping the same passage returns one row holding the text as
    written, so the count a reader sees is decided by a flag on the renderer and not by the number of
    passages. Replaces the typed len(parsed_texts(escaped_page(closing, autoescape=False))) == 2 and
    ['end', 'injected'] of case 181."""
    injected = '%s</li><li>%s' % (first, second)
    page = _rendered_page([injected], autoescape=False)
    npt.assert_array_equal(_lxml_rows(page), _html5lib_rows(page))
    npt.assert_array_equal(_lxml_rows(page), [first, second])
    npt.assert_array_equal(_lxml_rows(_rendered_page([injected], autoescape=True)), [injected])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(len(_lxml_rows(page)),
                               len(_lxml_rows(_rendered_page([injected], autoescape=True))))


@given(SAFE_LETTERS, SAFE_LETTERS)
@SLOW
def test_the_manufactured_row_carries_no_identifier_in_either_parser(first, second):
    """The identifier is what binds a row back to the passage it came from, and the manufactured row has
    none: both parsers report an id for the first row and nothing for the second. Dropping the rows
    without an id leaves exactly the identifiers the escaped page has, so the page carries one identifier
    and two rows, and a reader keyed on the identifier cannot see the second one at all."""
    injected = '%s</li><li>%s' % (first, second)
    page = _rendered_page([injected], autoescape=False)
    npt.assert_array_equal(_lxml_identifiers(page), _html5lib_identifiers(page))
    npt.assert_array_equal([identifier for identifier in _lxml_identifiers(page)
                            if identifier is not None],
                           _lxml_identifiers(_rendered_page([injected], autoescape=True)))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(len([identifier for identifier in _lxml_identifiers(page)
                                    if identifier is not None]), len(_lxml_rows(page)))


# ---------------------------------------------------------------- the bill of materials as a linear solve
ASSEMBLY_SIZE = st.integers(min_value=2, max_value=7)
QUANTITY = st.integers(min_value=1, max_value=5)
DEMAND_UNITS = st.integers(min_value=1, max_value=9)
ACYCLIC_BILL = ASSEMBLY_SIZE.flatmap(
    lambda size: st.lists(st.tuples(st.integers(min_value=0, max_value=size - 2),
                                    st.integers(min_value=1, max_value=size - 1), QUANTITY),
                          min_size=1, max_size=12, unique_by=lambda edge: edge[:2])
    .map(lambda edges: [(parent, child, qty) for parent, child, qty in edges if parent < child])
    .filter(bool))
CYCLE_LENGTH = st.integers(min_value=2, max_value=6)
LOOP_QUANTITY = st.integers(min_value=2, max_value=5)


def _requirement_matrix(edges):
    """The bill of materials as NetworkX builds it and as the chain hands it to a solver: the transpose of
    the weighted adjacency matrix, which is the Leontief input coefficient matrix."""
    graph = nx.DiGraph()
    for parent, child, quantity in edges:
        graph.add_edge(parent, child, qty=quantity)
    nodes = sorted(graph.nodes())
    matrix = nx.to_scipy_sparse_array(graph, nodelist=nodes, weight='qty', format='csc').T
    return graph, nodes, matrix


def _demand_vector(nodes, root, units):
    """The right-hand side, one entry per part, built by numpy."""
    wanted = np.zeros(len(nodes))
    wanted[nodes.index(root)] = units
    return wanted


def _sparse_totals(edges, root, units):
    """The primitive v18 named: SuperLU through scipy.sparse.linalg.spsolve on (I - A) x = d."""
    _, nodes, matrix = _requirement_matrix(edges)
    system = (scipy_sparse.identity(len(nodes), format='csc') - matrix).tocsc()
    return nodes, scipy_spsolve(system, _demand_vector(nodes, root, units))


def _dense_totals(edges, root, units):
    """The same system solved by LAPACK through numpy.linalg.solve, which is a different factorisation in
    a different library."""
    _, nodes, matrix = _requirement_matrix(edges)
    return nodes, np.linalg.solve(np.eye(len(nodes)) - matrix.toarray(),
                                  _demand_vector(nodes, root, units))


def _duckdb_totals(edges, root, units):
    """The same totals as a recursive expansion in SQL, which multiplies quantities along every path and
    adds them up. It is only ever asked about acyclic bills, because it does not terminate on the others."""
    frame = pd.DataFrame(edges, columns=['parent', 'child', 'qty'])
    with duckdb.connect() as connection:
        connection.register('edges', frame)
        rows = connection.execute(
            'with recursive expanded(item, units) as ('
            '  select ? as item, ?::DOUBLE as units'
            '  union all'
            '  select edges.child, expanded.units * edges.qty from expanded'
            '  join edges on edges.parent = expanded.item)'
            ' select item, sum(units) from expanded group by item order by item',
            [root, float(units)]).fetchall()
    return dict(rows)


def _solver_tolerance(edges, solution):
    """The forward-error bound numpy itself computes for this system: machine epsilon times the condition
    number times the size of the answer. A direct solver does not return exact zeros for the parts a
    demand does not reach, so the engines are compared inside this bound rather than exactly."""
    _, nodes, matrix = _requirement_matrix(edges)
    return (np.finfo(float).eps * np.linalg.cond(np.eye(len(nodes)) - matrix.toarray())
            * np.linalg.norm(solution, ord=np.inf))


@given(ACYCLIC_BILL, DEMAND_UNITS)
@SLOW
def test_three_engines_agree_on_the_total_requirement_of_a_generated_bill(edges, units):
    """v18 replaced two hand-written traversals with scipy.sparse.linalg.spsolve on the Leontief
    total-requirements system, and its v16.path_quantity case types the six cables a kit needs. Two more
    engines now answer the same question over generated acyclic bills: numpy.linalg.solve, which is LAPACK
    rather than SuperLU, and a DuckDB recursive expansion, which multiplies quantities along every path
    and adds them instead of solving anything. All three agree, so the recorded number is the bill\'s and
    not the solver\'s. Replaces the typed per_kit[\'cable\'] == 6.0, per_kit[\'display\'] == 2.0 and
    per_kit[\'kit\'] == 1.0 of handoff_guards_v18.py."""
    _, nodes, _ = _requirement_matrix(edges)
    root = nodes[0]
    solved_nodes, sparse_solution = _sparse_totals(edges, root, units)
    _, dense_solution = _dense_totals(edges, root, units)
    tolerance = _solver_tolerance(edges, sparse_solution)
    npt.assert_allclose(sparse_solution, dense_solution, atol=tolerance)
    expanded = _duckdb_totals(edges, root, units)
    npt.assert_allclose(sparse_solution, [expanded.get(node, 0.0) for node in solved_nodes],
                        atol=tolerance)


@given(ACYCLIC_BILL, DEMAND_UNITS)
@SLOW
def test_the_total_requirement_is_linear_in_the_demand_in_three_engines(edges, units):
    """Scaling the demand scales every total by the same factor, in all three engines, which is the
    property that lets a per-unit explosion be reused for an order. Replaces the typed
    total_requirements(edges, {\'kit\': 2})[\'cable\'] == 12.0 of handoff_guards_v18.py."""
    _, nodes, _ = _requirement_matrix(edges)
    root = nodes[0]
    _, one = _sparse_totals(edges, root, 1)
    _, many = _sparse_totals(edges, root, units)
    tolerance = _solver_tolerance(edges, many)
    npt.assert_allclose(many, one * units, atol=tolerance)
    _, dense_many = _dense_totals(edges, root, units)
    npt.assert_allclose(dense_many, one * units, atol=tolerance)
    expanded_one = _duckdb_totals(edges, root, 1)
    expanded_many = _duckdb_totals(edges, root, units)
    npt.assert_allclose([expanded_many[node] for node in sorted(expanded_many)],
                        [expanded_one[node] * units for node in sorted(expanded_one)], atol=tolerance)


@given(ACYCLIC_BILL, DEMAND_UNITS)
@SLOW
def test_a_part_with_nothing_under_it_demands_only_itself(edges, units):
    """A part that is the parent of nothing explodes to itself and to no other part. The recursive
    expansion says so exactly, reaching that part and no other; the solver says so only inside the error
    bound, because the entries it returns for the parts the demand does not reach are small rather than
    zero. Replaces the typed total_requirements(edges, {\'cable\': 1})[\'cable\'] == 1.0 of
    handoff_guards_v18.py."""
    graph, nodes, _ = _requirement_matrix(edges)
    leaf = max(nodes, key=lambda node: (graph.out_degree(node) == 0, node))
    assume(graph.out_degree(leaf) == 0)
    solved_nodes, solution = _sparse_totals(edges, leaf, units)
    tolerance = _solver_tolerance(edges, solution)
    npt.assert_allclose(solution[solved_nodes.index(leaf)], units, atol=tolerance)
    npt.assert_allclose(np.delete(solution, solved_nodes.index(leaf)),
                        np.zeros(len(solved_nodes) - 1), atol=tolerance)
    npt.assert_array_equal(sorted(_duckdb_totals(edges, leaf, units)), [leaf])


@given(CYCLE_LENGTH, LOOP_QUANTITY, DEMAND_UNITS)
@SLOW
def test_a_bill_that_loops_gets_a_negative_answer_from_both_solvers_and_no_refusal(length, quantity,
                                                                                  units):
    """The chain tests acyclicity before it solves, and the test is doing all the refusing. Handed a
    generated bill whose parts require each other around a loop, neither solver raises and neither warns:
    both return the same finite vector, and its smallest entry is negative, which is not a quantity of
    anything. NetworkX's is_directed_acyclic_graph is what says no. The recursive expansion in SQL is not
    asked, because on these bills it does not terminate. Replaces the typed
    g.rejects(g.Blocked, lambda: total_requirements(cyclic, ...)) of handoff_guards_v18.py."""
    edges = [(index, (index + 1) % length, quantity) for index in range(length)]
    graph, nodes, _ = _requirement_matrix(edges)
    npt.assert_array_equal(nx.is_directed_acyclic_graph(graph),
                           nx.is_directed_acyclic_graph(nx.DiGraph(graph.edges).reverse()))
    _, sparse_solution = _sparse_totals(edges, nodes[0], units)
    _, dense_solution = _dense_totals(edges, nodes[0], units)
    npt.assert_allclose(sparse_solution, dense_solution)
    npt.assert_array_equal(np.isfinite(sparse_solution), np.isfinite(dense_solution))
    with pytest.raises(AssertionError):
        npt.assert_allclose(np.min(sparse_solution), np.abs(np.min(sparse_solution)))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(nx.is_directed_acyclic_graph(graph),
                               nx.is_directed_acyclic_graph(nx.DiGraph()))


@given(CYCLE_LENGTH, DEMAND_UNITS)
@SLOW
def test_the_two_solvers_part_company_on_a_loop_that_returns_exactly_one_unit(length, units):
    """When each part in the loop takes exactly one of the next, the matrix is exactly singular, and the
    two solvers answer differently. numpy documents "LinAlgError: If `a` is singular or not square."
    (numpy/linalg/_linalg.py at tag v2.4.6) and raises. scipy warns and returns: its
    MatrixRankWarning is exported in scipy/sparse/linalg/_dsolve/linsolve.py at tag v1.17.1 and
    documented there as "Warning for exactly singular matrices.", and the same file's spsolve warns
    "Matrix is exactly singular" and then calls x.fill(np.nan). So a chain that catches solver exceptions
    sees nothing here, and the answer it carries forward is a vector with no finite entry in it."""
    edges = [(index, (index + 1) % length, 1) for index in range(length)]
    _, nodes, _ = _requirement_matrix(edges)
    with pytest.raises(np.linalg.LinAlgError):
        _dense_totals(edges, nodes[0], units)
    with pytest.warns(scipy_linsolve.MatrixRankWarning):
        _, solution = _sparse_totals(edges, nodes[0], units)
    npt.assert_array_equal(np.flatnonzero(np.isfinite(solution)),
                           np.flatnonzero(np.isfinite(np.full(len(nodes), np.nan))))


# ------------------------------------------- a package whose digest is supposed to stand for its content
ZIP_PACKAGE_ORACLE_JAVA = pathlib.Path(__file__).with_name('zip_package_oracle.java')
ZIP_STAMP_ORACLE_PHP = pathlib.Path(__file__).with_name('zip_stamp_oracle.php')
java_runtime_available = shutil.which('java') is not None
PART_NAME = st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=8)
PACKAGE_PARTS = st.dictionaries(PART_NAME, st.binary(max_size=48), min_size=1, max_size=4)
DOS_EPOCH_HALVES = st.integers(min_value=315532800 // 2, max_value=2145916800 // 2)
LATER_DOS_EPOCH_HALVES = st.integers(min_value=315532800 // 2 + 1, max_value=2145916800 // 2)
BEFORE_DOS_EPOCH = st.integers(min_value=0, max_value=315532800 - 1)
READER_ZONE = st.sampled_from(('America/New_York', 'America/Sao_Paulo', 'Asia/Kolkata',
                               'Asia/Tokyo', 'Europe/Berlin', 'Pacific/Auckland'))


def _reproducible_package(parts, order=None):
    """One package written by the primitive under test: repro_zipfile.ReproducibleZipFile, which its
    own source at v0.4.1 documents as a ZipFile that "overwrites file-modified timestamps and
    file/directory permissions modes in write mode in order to create a reproducible ZIP archive"."""
    buffer = io.BytesIO()
    with repro_zipfile.ReproducibleZipFile(buffer, 'w') as archive:
        for name in (sorted(parts) if order is None else order):
            archive.writestr(name, parts[name])
    return buffer.getvalue()


def _plain_package(parts):
    """The same parts through the standard library writer the primitive replaces."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        for name in sorted(parts):
            archive.writestr(name, parts[name])
    return buffer.getvalue()


def _java_package(package, zone='UTC'):
    """The same archive through the java.util.zip implementation in the OpenJDK class library: what
    that runtime reads out of it, and a second archive it writes from the entries it read, stored,
    under the same names in the same order with the same MS-DOS local date-times. The shim parses
    argv, calls the library and prints; the Python side writes the bytes out, runs it in the named
    zone and splits stdout."""
    with tempfile.TemporaryDirectory() as directory:
        given, written = pathlib.Path(directory) / 'given.zip', pathlib.Path(directory) / 'java.zip'
        given.write_bytes(package)
        completed = subprocess.run(['java', str(ZIP_PACKAGE_ORACLE_JAVA), str(given), str(written)],
                                   capture_output=True, encoding='utf-8', check=True,
                                   env=dict(os.environ, TZ=zone))
        rows = [line.split('\t') for line in completed.stdout.split('\n')[:-1]]
        return ([(bytes.fromhex(row[0]).decode(), [int(field) for field in row[1:7]],
                  int(row[7]), int(row[8]), int(row[9])) for row in rows], written.read_bytes())


def _libzip_instants(package, zone):
    """The last-modified instant PHP's zip extension (libzip 1.7.3) resolves each entry to, run in the
    named zone. The shim parses argv, calls the library and prints; the Python side splits stdout."""
    with tempfile.TemporaryDirectory() as directory:
        given = pathlib.Path(directory) / 'given.zip'
        given.write_bytes(package)
        completed = subprocess.run(['php', str(ZIP_STAMP_ORACLE_PHP), str(given)],
                                   capture_output=True, encoding='utf-8', check=True,
                                   env=dict(os.environ, TZ=zone))
        return [int(line.split('\t')[1]) for line in completed.stdout.split('\n')[:-1]]


@given(PACKAGE_PARTS)
@SLOW
def test_two_packages_written_from_the_same_parts_in_the_same_order_have_one_digest(parts):
    """The claim the primitive is there to support, in its README's own words at v0.4.1:
    ""Reproducible" or "deterministic" in this context means that the binary content of the ZIP
    archive is identical if you add files with identical binary content in the same order." On
    generated parts it holds exactly: the two packages are the same bytes, so the two digests are one
    digest. Replaces the typed digest equality and the typed `stamps(first) == stamps(second)` of
    handoff_guards_v18.py case a_deterministic_package_is_a_library_writer."""
    first, second = _reproducible_package(parts), _reproducible_package(parts)
    npt.assert_equal(hashlib.sha256(first).hexdigest(), hashlib.sha256(second).hexdigest())
    npt.assert_equal(hmac.compare_digest(first, second), hmac.compare_digest(first, first))
    with zipfile.ZipFile(io.BytesIO(first)) as archive:
        with zipfile.ZipFile(io.BytesIO(second)) as again:
            npt.assert_array_equal([info.date_time for info in archive.infolist()],
                                   [info.date_time for info in again.infolist()])


@given(PACKAGE_PARTS, st.data())
@SLOW
def test_the_same_parts_written_in_a_different_order_are_a_different_package(parts, source):
    """The README's own caveat, quoted at v0.4.1: "Note that files must be written to the archive in
    the same order to reproduce an identical archive." Generated parts written in a generated
    permutation come back out as the same mapping of name to bytes and hash to a different digest, so
    the digest answers a question about the writing, not only about the content."""
    assume(len(parts) > 1)
    order = source.draw(st.permutations(sorted(parts)))
    assume(order != sorted(parts))
    sorted_package, permuted = _reproducible_package(parts), _reproducible_package(parts, order)
    with zipfile.ZipFile(io.BytesIO(sorted_package)) as archive:
        with zipfile.ZipFile(io.BytesIO(permuted)) as other:
            npt.assert_equal({name: archive.read(name) for name in archive.namelist()},
                             {name: other.read(name) for name in other.namelist()})
    with pytest.raises(AssertionError):
        npt.assert_equal(hashlib.sha256(permuted).hexdigest(),
                         hashlib.sha256(sorted_package).hexdigest())


@pytest.mark.skipif(not java_runtime_available, reason='java is required for this oracle')
@given(PACKAGE_PARTS)
@JAVA_ORACLE
def test_a_second_writer_gives_the_same_parts_the_same_entries_and_a_different_digest(parts):
    """The finding. Handed the package, the java.util.zip writer in the OpenJDK class library writes
    the same names in the same order carrying the same bytes with the same MS-DOS local date-times,
    stored uncompressed as this one is, and the two archives are not the same bytes: the entry
    inventory and the contents match, the digests do not. Byte-level reproducibility is therefore a
    property of one writer rather than of the format, and the README's "you can reliably check
    equality of the contents of two ZIP archives by simply comparing checksums of the archive" holds
    only between packages written by that writer. Replaces the typed digest equality of case
    a_deterministic_package_is_a_library_writer, which asserted it of one writer twice."""
    package = _reproducible_package(parts)
    inventory, by_java = _java_package(package)
    npt.assert_array_equal([entry[0] for entry in inventory], sorted(parts))
    with zipfile.ZipFile(io.BytesIO(by_java)) as archive:
        npt.assert_equal({name: archive.read(name) for name in archive.namelist()}, parts)
        npt.assert_array_equal([info.date_time for info in archive.infolist()],
                               [entry[1] for entry in inventory])
    with pytest.raises(AssertionError):
        npt.assert_equal(hashlib.sha256(by_java).hexdigest(), hashlib.sha256(package).hexdigest())


@pytest.mark.skipif(not java_runtime_available, reason='java is required for this oracle')
@given(PACKAGE_PARTS)
@JAVA_ORACLE
def test_the_stamp_the_package_carries_is_the_one_the_library_publishes(parts):
    """`repro_zipfile.date_time()` is the package's published account of what it writes, documented at
    v0.4.1 as the value "used to force overwrite on all ZipInfo objects. Defaults to 1980-01-01
    00:00:00." Another runtime reading the archive's MS-DOS date and time fields, through
    `ZipEntry.getTimeLocal`, reports that same date-time for every entry. Replaces the typed
    `g.equal(stamps(first), {(1980, 1, 1, 0, 0, 0)})` of case
    a_deterministic_package_is_a_library_writer."""
    inventory, _ = _java_package(_reproducible_package(parts))
    npt.assert_array_equal([entry[1] for entry in inventory],
                           [list(repro_zipfile.date_time())] * len(parts))


@pytest.mark.skipif(not java_runtime_available, reason='java is required for this oracle')
@given(PACKAGE_PARTS, st.binary(max_size=48), st.data())
@JAVA_ORACLE
def test_changing_one_part_changes_the_package_digest(parts, replacement, source):
    """One generated part replaced by generated bytes that are not the bytes it had. The digest of the
    package changes, and so does the size and CRC-32 the second runtime reads for that entry, so the
    change is in the archive and not only in the hash. Replaces the typed
    `g.equal(sha256(changed) == sha256(first), False)` of case
    a_deterministic_package_is_a_library_writer."""
    name = source.draw(st.sampled_from(sorted(parts)))
    assume(parts[name] != replacement)
    package = _reproducible_package(parts)
    changed = _reproducible_package(dict(parts, **{name: replacement}))
    before, _ = _java_package(package)
    after, _ = _java_package(changed)
    with pytest.raises(AssertionError):
        npt.assert_equal(hashlib.sha256(changed).hexdigest(), hashlib.sha256(package).hexdigest())
    with pytest.raises(AssertionError):
        npt.assert_array_equal([entry[3:] for entry in before], [entry[3:] for entry in after])


@pytest.mark.skipif(not java_runtime_available, reason='java is required for this oracle')
@given(PACKAGE_PARTS)
@JAVA_ORACLE
def test_every_part_comes_back_out_of_the_package_under_its_own_name(parts):
    """The round trip, in both runtimes: every generated part is in the archive under the name it was
    written with, at the length it was written with, stored uncompressed, and reading it back gives
    the bytes that went in. Replaces the typed `sorted(archive.namelist()) == [...]` and
    `archive.read('word/document.xml') == b'<w:p/>'` of case
    a_deterministic_package_is_a_library_writer."""
    package = _reproducible_package(parts)
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        npt.assert_equal({name: archive.read(name) for name in archive.namelist()}, parts)
    inventory, _ = _java_package(package)
    npt.assert_array_equal([entry[0] for entry in inventory], sorted(parts))
    npt.assert_array_equal([entry[3] for entry in inventory],
                           [len(parts[name]) for name in sorted(parts)])
    npt.assert_array_equal([entry[2] for entry in inventory], [zipfile.ZIP_STORED] * len(parts))


@given(PACKAGE_PARTS)
@SLOW
def test_the_standard_library_writer_stamps_the_clock_where_the_reproducible_one_stamps_a_constant(parts):
    """The reason the primitive exists, stated by its README at v0.4.1: "ZIP archives are not normally
    reproducible even when containing files with identical content because of file metadata. In
    particular, the usual culprits are: 1. Last-modified timestamps". The standard library writer
    stamps every entry with the clock, so its archive does not carry the published fixed value; the
    replacement writer's does. Replaces the typed
    `g.equal(stamps(plain.getvalue()) == {(1980, 1, 1, 0, 0, 0)}, False)` of case
    a_deterministic_package_is_a_library_writer."""
    with zipfile.ZipFile(io.BytesIO(_reproducible_package(parts))) as archive:
        fixed = [info.date_time for info in archive.infolist()]
    with zipfile.ZipFile(io.BytesIO(_plain_package(parts))) as archive:
        clocked = [info.date_time for info in archive.infolist()]
    npt.assert_array_equal(fixed, [repro_zipfile.date_time()] * len(parts))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(clocked, fixed)


@pytest.mark.skipif(not java_runtime_available, reason='java is required for this oracle')
@given(DOS_EPOCH_HALVES, PACKAGE_PARTS)
@JAVA_ORACLE
def test_an_even_source_date_epoch_is_the_stamp_the_package_carries(half, parts):
    """`SOURCE_DATE_EPOCH` is the Reproducible Builds standard the README points at, and at v0.4.1
    `date_time()` returns `time.gmtime(int(source_date_epoch))[:6]` when it is set. For a generated
    epoch that falls on an even second inside the range the format can carry, the second runtime reads
    back exactly the date-time the library publishes."""
    with mock.patch.dict(os.environ, {'SOURCE_DATE_EPOCH': str(half * 2)}):
        package, published = _reproducible_package(parts), repro_zipfile.date_time()
    inventory, _ = _java_package(package)
    npt.assert_array_equal([entry[1] for entry in inventory], [list(published)] * len(parts))


@given(DOS_EPOCH_HALVES, PACKAGE_PARTS)
@SLOW
def test_an_odd_source_date_epoch_is_not_the_stamp_the_package_carries(half, parts):
    """The MS-DOS time field stores seconds in units of two -- libzip's own reader spells the decode
    out as `tm.tm_sec = (dtime << 1) & 62` -- so an odd `SOURCE_DATE_EPOCH` cannot be written down.
    `date_time()` still reports the odd second, and the archive carries the even one, so the value the
    library publishes as the fixed stamp is not the value in the file. Two epochs a second apart
    produce one archive, byte for byte, which is the same fact from the other side: a build cannot
    move its stamp by one second."""
    with mock.patch.dict(os.environ, {'SOURCE_DATE_EPOCH': str(half * 2 + 1)}):
        odd, published = _reproducible_package(parts), repro_zipfile.date_time()
    with mock.patch.dict(os.environ, {'SOURCE_DATE_EPOCH': str(half * 2)}):
        even = _reproducible_package(parts)
    with zipfile.ZipFile(io.BytesIO(odd)) as archive:
        carried = [info.date_time for info in archive.infolist()]
    npt.assert_equal(hashlib.sha256(odd).hexdigest(), hashlib.sha256(even).hexdigest())
    with pytest.raises(AssertionError):
        npt.assert_array_equal(carried, [published] * len(parts))


@given(BEFORE_DOS_EPOCH, PART_NAME, st.binary(max_size=48))
@SLOW
def test_a_source_date_epoch_before_the_format_begins_fails_the_pack_not_the_documented_check(epoch,
                                                                                             name,
                                                                                             content):
    """The Reproducible Builds standard puts no floor under `SOURCE_DATE_EPOCH`, and the ZIP format
    has one: the README calls 1980-01-01 "the earliest timestamp that is supported by the ZIP format
    specifications". CPython guards it -- `ZipInfo.__init__` raises `ValueError('ZIP does not support
    timestamps before 1980')` -- but the replacement writer assigns `zinfo.date_time` after the
    ZipInfo is constructed, so the guard never runs and the write dies inside `struct.pack` instead,
    with a message about an unsigned short. The build stops either way; what it says is not what the
    format documents."""
    with mock.patch.dict(os.environ, {'SOURCE_DATE_EPOCH': str(epoch)}):
        published = repro_zipfile.date_time()
        with pytest.raises(ValueError):
            zipfile.ZipInfo(name, date_time=published)
        with pytest.raises(struct.error):
            _reproducible_package({name: content})


@pytest.mark.skipif(not php_binary_available, reason='php is required for this oracle')
@given(PACKAGE_PARTS, READER_ZONE)
@ORACLE_PROCESS
def test_a_second_reader_dates_the_package_in_its_own_time_zone(parts, zone):
    """The MS-DOS date and time fields carry no zone, and libzip resolves them with `mktime`, which
    reads the reader's: its `_zip_d2u_time` fills a `struct tm` from the field bits, sets
    `tm.tm_isdst = -1` with the comment "let mktime decide if DST is in effect", and returns
    `mktime(&tm)`. Run in a generated zone, PHP's `ZipArchive::statIndex` reports exactly the instant
    zoneinfo gives for the published date-time read as local time there."""
    package = _reproducible_package(parts)
    stamp = repro_zipfile.date_time()
    local = datetime.datetime(*stamp, tzinfo=zoneinfo.ZoneInfo(zone)).timestamp()
    npt.assert_array_equal(_libzip_instants(package, zone), [local] * len(parts))


@pytest.mark.skipif(not php_binary_available, reason='php is required for this oracle')
@given(PACKAGE_PARTS, READER_ZONE)
@ORACLE_PROCESS
def test_two_readers_in_two_zones_disagree_about_when_the_package_was_written(parts, zone):
    """The README says of the fixed stamp that it is "1980-01-01 00:00 UTC". The archive does not say
    UTC: what it carries is the bare MS-DOS field, and a reader in any of these zones dates the same
    package to a different instant from a reader in UTC, by that zone's offset. The stamp is stable
    across machines only as a calendar reading, and any chain that turns it into an instant -- a
    retention window, an age check, an ordering against a wall-clock event -- gets a different answer
    on a differently configured machine."""
    package = _reproducible_package(parts)
    stamp = repro_zipfile.date_time()
    utc = datetime.datetime(*stamp, tzinfo=datetime.timezone.utc).timestamp()
    npt.assert_array_equal(_libzip_instants(package, 'UTC'), [utc] * len(parts))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_libzip_instants(package, zone), [utc] * len(parts))


@pytest.mark.skipif(not java_runtime_available, reason='java is required for this oracle')
@given(PACKAGE_PARTS, READER_ZONE)
@JAVA_ORACLE
def test_the_second_writer_is_not_reproducible_across_zones_at_the_stamp_the_format_begins_at(parts,
                                                                                             zone):
    """OpenJDK's `ZipEntry` encodes 1980-01-01 00:00:00 -- the primitive's default stamp, and the
    earliest the format admits -- as `(1 << 21) | (1 << 16)`, which is the same bit pattern it keeps
    as the sentinel `DOSTIME_BEFORE_1980`. `setTimeLocal` tests `xdostime != DOSTIME_BEFORE_1980`
    before it discards the modification time, so at exactly this stamp it keeps one, converting
    through `ZoneId.systemDefault()`; `ZipOutputStream` then writes an Info-ZIP extended timestamp
    extra field holding that instant. The same parts written by the same writer in two zones are
    therefore two different archives, and the one date the format's own floor names is the one date
    at which this writer is not reproducible."""
    package = _reproducible_package(parts)
    _, from_utc = _java_package(package, zone='UTC')
    _, from_zone = _java_package(package, zone=zone)
    with zipfile.ZipFile(io.BytesIO(from_zone)) as archive:
        npt.assert_equal({name: archive.read(name) for name in archive.namelist()}, parts)
    with pytest.raises(AssertionError):
        npt.assert_equal(hashlib.sha256(from_zone).hexdigest(),
                         hashlib.sha256(from_utc).hexdigest())


@pytest.mark.skipif(not java_runtime_available, reason='java is required for this oracle')
@given(PACKAGE_PARTS, READER_ZONE, LATER_DOS_EPOCH_HALVES)
@JAVA_ORACLE
def test_the_second_writer_is_reproducible_across_zones_at_every_later_stamp(parts, zone, half):
    """The agreeing region of the same comparison. Move the stamp off the sentinel with any generated
    `SOURCE_DATE_EPOCH` at a later even second, and `setTimeLocal` discards the modification time as
    it does everywhere else in the format's range, no extended timestamp is written, and the second
    writer produces one archive in both zones."""
    with mock.patch.dict(os.environ, {'SOURCE_DATE_EPOCH': str(half * 2)}):
        package = _reproducible_package(parts)
    _, from_utc = _java_package(package, zone='UTC')
    _, from_zone = _java_package(package, zone=zone)
    npt.assert_equal(hashlib.sha256(from_zone).hexdigest(), hashlib.sha256(from_utc).hexdigest())


# --------------------------------------------------- the month end a schedule is supposed to land on
MONTH_ANCHOR = st.dates(min_value=datetime.date(1901, 1, 1), max_value=datetime.date(2099, 12, 31))
PERIOD_COUNT = st.integers(min_value=2, max_value=18)
SHORTENING_MONTHS = tuple(month for month in range(1, 13)
                          if calendar.monthrange(2027, month)[1]
                          > calendar.monthrange(2027, month % 12 + 1)[1])


@given(st.lists(MONTH_ANCHOR, min_size=1, max_size=20))
@SLOW
def test_the_last_day_of_a_month_is_the_same_day_in_three_implementations(anchors):
    """P159's month walk and case v16.month_walk turn on where a month ends. pandas 2.2.3 answers it
    with `Period.end_time`, documented in pandas/_libs/tslibs/period.pyx at tag v2.2.3 as "Get the
    Timestamp for the end of the period." Two implementations that share none of that code answer the
    same question on generated dates: polars 1.44.1's `dt.month_end`, "Roll forward to the last day of
    the month", read in py-polars/src/polars/expr/datetime.py at tag py-1.44.1, and DuckDB 1.5.5's
    `last_day`, "The last day of the corresponding month in the date." All three agree on every
    generated date, leap Februaries included. Replaces the typed
    `[date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31)]` of handoff_guards_v18.py case
    month_ends_come_from_periods_not_from_repeated_addition."""
    frame = pl.DataFrame({'anchor': anchors})
    by_pandas = pl.Series('end', [pd.Period(anchor, freq='M').end_time.date() for anchor in anchors])
    plt.assert_series_equal(by_pandas, frame['anchor'].dt.month_end().rename('end'))
    with duckdb.connect() as connection:
        plt.assert_series_equal(by_pandas, connection.sql(
            'select last_day(anchor) as end from frame').pl()['end'])


@pytest.mark.skipif(not php_binary_available, reason='the php runtime is required for this oracle')
@given(MONTH_ANCHOR)
@ORACLE_PROCESS
def test_a_fourth_implementation_in_another_runtime_lands_on_the_same_last_day(anchor):
    """PHP 8.4.19's relative formats include "last day of", handled by timelib in C, and asking
    `DateTime::modify` for the last day of the anchor's own month gives the same date pandas gives as
    the end of the monthly period containing it, on every generated date. The month end is therefore a
    property of the calendar and not of the library, which is what makes the drift below a defect
    rather than a convention."""
    period = pd.Period(anchor, freq='M')
    npt.assert_equal(period.end_time.date(),
                     datetime.date.fromisoformat(_php_modify(anchor, 'last day of this month')))


@given(MONTH_ANCHOR, st.data())
@SLOW
def test_a_monthly_period_forgets_the_day_of_the_month_it_was_anchored_with(anchor, source):
    """A monthly period is the month, not the date it was built from: any other day of the same month
    gives the same period, the same text and the same end. This is why a period range cannot drift and
    a repeated offset can -- the day of the month is not carried from one step to the next, because it
    was never kept. Replaces the typed `str(periods[1]) == '2026-02'` and the typed
    `['2026-01', '2026-02', '2026-03']` of case
    month_ends_come_from_periods_not_from_repeated_addition."""
    other = anchor.replace(day=source.draw(st.integers(
        min_value=1, max_value=calendar.monthrange(anchor.year, anchor.month)[1])))
    npt.assert_equal(str(pd.Period(anchor, freq='M')), str(pd.Period(other, freq='M')))
    npt.assert_equal(pd.Period(anchor, freq='M').end_time, pd.Period(other, freq='M').end_time)
    npt.assert_equal(str(pd.Period(anchor, freq='M')), anchor.strftime('%Y-%m'))


@given(st.integers(min_value=1901, max_value=2098), st.sampled_from(SHORTENING_MONTHS),
       st.integers(min_value=3, max_value=18))
@SLOW
def test_repeated_month_addition_drifts_off_the_month_ends_a_period_range_keeps(year, month, count):
    """The defect v16 hit and v18 recorded: its hand-written step "reached 2026-03-28 instead". The
    months this runs from are the ones the calendar module reports as longer than the month after
    them, so the first step has somewhere to fall to. One step of `relativedelta(months=+1)` from the
    month end lands on the next month end, because clamping and the month end are the same date there;
    the second step carries that shortened day forward and never recovers it. One hop of two months
    from the same anchor does land on the right month end, so the drift is a property of stepping
    repeatedly rather than of the offset. Replaces the typed `ends[-1] == date(2026, 3, 31)` of case
    month_ends_come_from_periods_not_from_repeated_addition."""
    periods = pd.period_range(pd.Period(year=year, month=month, freq='M'), periods=count)
    ends = [period.end_time.date() for period in periods]
    npt.assert_equal(ends[0] + relativedelta(months=+1), ends[1])
    npt.assert_equal(ends[0] + relativedelta(months=+2), ends[2])
    with pytest.raises(AssertionError):
        npt.assert_equal(ends[0] + relativedelta(months=+1) + relativedelta(months=+1), ends[2])


@given(MONTH_ANCHOR)
@SLOW
def test_the_end_of_a_monthly_period_is_its_last_nanosecond_and_not_a_date(anchor):
    """`end_time` is not the last day: it is the last instant of the period, and the gap between it and
    the start of the next period is exactly `Timestamp.resolution`, the smallest step pandas can
    represent. Taking `.date()` off it, as the chain does, discards a time of 23:59:59.999999999, so a
    deadline compared as a date admits nothing after midnight while the same deadline compared as the
    period's own end admits the whole last day. Replaces the typed
    `g.equal(periods[1].end_time.date() != periods[1].end_time, True)` of case
    month_ends_come_from_periods_not_from_repeated_addition."""
    period = pd.Period(anchor, freq='M')
    npt.assert_equal((period + 1).start_time - period.end_time, pd.Timestamp.resolution)
    npt.assert_array_less(pd.Timestamp(period.end_time.date()).value, period.end_time.value)
    with pytest.raises(AssertionError):
        npt.assert_equal(pd.Timestamp(period.end_time.date()), period.end_time)


@given(st.lists(MONTH_ANCHOR, min_size=1, max_size=20))
@SLOW
def test_the_number_of_days_in_a_month_agrees_across_three_implementations(anchors):
    """`Period.days_in_month` against the standard library's own `calendar.monthrange`, which is pure
    Python and unrelated to pandas' C extension, and against the day component of polars' month end.
    All three agree on every generated month, and each equals the day of the month the period ends on.
    Replaces the typed `pd.Period('2026-02', freq='M').days_in_month == 28` of case
    month_ends_come_from_periods_not_from_repeated_addition."""
    periods = [pd.Period(anchor, freq='M') for anchor in anchors]
    npt.assert_array_equal([period.days_in_month for period in periods],
                           [calendar.monthrange(anchor.year, anchor.month)[1] for anchor in anchors])
    npt.assert_array_equal([period.days_in_month for period in periods],
                           [period.end_time.day for period in periods])
    plt.assert_series_equal(pl.Series('day', [period.days_in_month for period in periods],
                                      dtype=pl.Int8),
                            pl.Series('anchor', anchors).dt.month_end().dt.day().rename('day'))


@given(MONTH_ANCHOR, PERIOD_COUNT)
@SLOW
def test_the_word_for_monthly_is_deprecated_in_one_pandas_api_and_refused_in_the_other(anchor, count):
    """The same letter means monthly in both halves of pandas 2.2.3 and only one of them will still
    take it. `to_offset` in pandas/_libs/tslibs/offsets.pyx at tag v2.2.3 warns for a date range --
    "'M' is deprecated and will be removed in a future version, please use 'ME' instead." -- and in the same
    branch of the same function, twenty-two lines further down, raises for a period range, "for Period, please use 'M' instead of 'ME'". So a
    schedule written with one spelling warns and a schedule written with the other raises, and no
    single spelling is accepted by both calls. The two calls do agree on the dates: the deprecated
    month-end offset walks exactly the ends of the periods the period range names."""
    with pytest.warns(FutureWarning):
        deprecated = pd.date_range(anchor, periods=count, freq='M')
    npt.assert_array_equal(deprecated.date, pd.date_range(anchor, periods=count, freq='ME').date)
    npt.assert_array_equal(deprecated.date,
                           [period.end_time.date()
                            for period in pd.period_range(anchor, periods=count, freq='M')])
    with pytest.raises(ValueError):
        pd.period_range(anchor, periods=count, freq='ME')


@given(MONTH_ANCHOR, PERIOD_COUNT)
@SLOW
def test_a_period_range_covers_every_month_between_its_ends_with_no_gap_and_no_overlap(anchor, count):
    """A period range named by a count and the same range named by its first and last period are the
    same months, and each period's last instant is one resolution step before the next period's first,
    so the months tile the interval exactly. Replaces the typed `len(periods) == 3` of case
    month_ends_come_from_periods_not_from_repeated_addition."""
    periods = pd.period_range(anchor, periods=count, freq='M')
    npt.assert_array_equal([str(period) for period in periods],
                           [str(period) for period in
                            pd.period_range(start=periods[0], end=periods[-1], freq='M')])
    npt.assert_array_equal([period.end_time + pd.Timestamp.resolution for period in periods[:-1]],
                           [period.start_time for period in periods[1:]])


# ------------------------------------------------------ a bar on a chart, and a table in a workbook
BAR_DAY = st.dates(min_value=datetime.date(1971, 1, 1), max_value=datetime.date(2099, 12, 31))
BAR_LENGTH = st.integers(min_value=0, max_value=400)
TABLE_COLUMN = st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=8)
TABLE_CELL = st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789-', min_size=1, max_size=10)
BEYOND_THE_SHEET = st.integers(min_value=1048576, max_value=2000000)


@st.composite
def _schedule_table(draw):
    """One schedule as a header row of distinct column names and a body with a cell under each."""
    columns = draw(st.lists(TABLE_COLUMN, min_size=1, max_size=5, unique=True))
    rows = draw(st.lists(st.lists(TABLE_CELL, min_size=len(columns), max_size=len(columns)),
                         min_size=1, max_size=4))
    return columns, rows


def _drawn_bar(start, width):
    """The rectangle matplotlib actually draws for one bar: the extents of the path `broken_barh`
    returns, as its two edges and its width."""
    figure, axes = matplotlib_pyplot.subplots()
    try:
        extents = axes.broken_barh([(start, width)], (0, 1)).get_paths()[0].get_extents()
        return [float(extents.x0), float(extents.x1), float(extents.width)]
    finally:
        matplotlib_pyplot.close(figure)


def _schedule_workbook(columns, rows, *, declare):
    """One workbook holding the header row and the body, with an Excel table over the same range.
    `declare` passes the columns to `add_table` or leaves the options out, which is the whole
    difference between the two readings below."""
    buffer = io.BytesIO()
    book = xlsxwriter.Workbook(buffer, {'in_memory': True})
    sheet = book.add_worksheet('schedule')
    sheet.write_row(0, 0, columns)
    for index, row in enumerate(rows, start=1):
        sheet.write_row(index, 0, row)
    sheet.add_table(0, 0, len(rows), len(columns) - 1,
                    {'columns': [{'header': column} for column in columns]} if declare else None)
    book.close()
    return buffer.getvalue()


def _openpyxl_grid(data):
    sheet = openpyxl.load_workbook(io.BytesIO(data))['schedule']
    return [[cell.value for cell in row] for row in sheet.iter_rows()]


def _calamine_grid(data):
    return CalamineWorkbook.from_filelike(io.BytesIO(data)).get_sheet_by_name('schedule').to_python()


@given(st.lists(BAR_DAY, min_size=2, max_size=30))
@SLOW
def test_a_chart_day_number_and_the_standard_library_ordinal_differ_by_one_constant(days):
    """P141 draws a schedule with matplotlib, which turns a date into "Number of days since the epoch",
    documented in lib/matplotlib/dates.py at tag v3.11.1 and defaulting to 1970-01-01. The standard
    library's `date.toordinal` counts days from a different origin and is not matplotlib's code. Over
    generated dates the two differ by one constant, and the gaps between consecutive dates are
    identical, so the chart axis is a day count and nothing about it is matplotlib's own arithmetic.
    Replaces the typed 20706.0 day number of handoff_guards_v15.py case
    a_bar_takes_a_width_not_an_end_date."""
    offsets = [day.toordinal() - matplotlib_dates.date2num(day) for day in days]
    npt.assert_array_equal(offsets, [offsets[0]] * len(offsets))
    npt.assert_array_equal(np.diff([matplotlib_dates.date2num(day) for day in sorted(days)]),
                           np.diff([day.toordinal() for day in sorted(days)]))


@pytest.mark.skipif(not ruby_available, reason='the ruby runtime is required for this oracle')
@given(BAR_DAY, BAR_LENGTH)
@ORACLE_PROCESS
def test_another_runtime_counts_the_same_days_between_the_two_ends_of_a_bar(start, length):
    """Ruby's `Date#jd`, documented in ext/date/date_core.c at tag v3_3_6 as returning "the Julian day
    number", is a third origin again and a C implementation in another runtime. The number of days
    between the two ends of a generated bar is the same in matplotlib's numbering and in Ruby's, which
    is what the width of the bar is supposed to be."""
    finish = start + datetime.timedelta(days=length)
    npt.assert_equal(matplotlib_dates.date2num(finish) - matplotlib_dates.date2num(start),
                     int(_ruby_calendar_day(finish.isoformat())[1])
                     - int(_ruby_calendar_day(start.isoformat())[1]))


@given(BAR_DAY, BAR_LENGTH)
@SLOW
def test_the_width_of_a_bar_is_the_length_of_the_interval_and_not_the_second_date(start, length):
    """`broken_barh` takes, in its own signature, a sequence of `(xmin, xwidth)` pairs. Handed the
    generated interval's length it draws a bar exactly that many days wide. Handed the finish date's
    day number where the width belongs -- the same two values, passed the way a reader of the call
    might expect -- it draws a bar as wide as the whole span from the epoch, tens of thousands of days,
    and reports no error at all. Replaces the typed `right == [2.0, 0.0]`, the typed 20706.0 and the
    typed `wrong[0] > right[0] * 10000` of case a_bar_takes_a_width_not_an_end_date."""
    finish = start + datetime.timedelta(days=length)
    first, last = matplotlib_dates.date2num(start), matplotlib_dates.date2num(finish)
    npt.assert_equal(_drawn_bar(first, last - first)[2], float(length))
    npt.assert_equal(_drawn_bar(first, last)[2], last)
    with pytest.raises(AssertionError):
        npt.assert_equal(_drawn_bar(first, last)[2], _drawn_bar(first, last - first)[2])


@given(BAR_DAY, st.integers(min_value=1, max_value=400))
@SLOW
def test_a_finish_before_the_start_draws_exactly_the_bar_a_correct_interval_draws(start, length):
    """The guard module refuses a finish that precedes its start, and that refusal is its own code:
    matplotlib does not object. Handed the reversed pair, `broken_barh` draws a rectangle with the same
    two edges and the same width as the correct one, so the two are the same bar on the page and a
    chart cannot show the error. Replaces the typed
    `g.rejects(g.Blocked, lambda: bar_spans(...))` of case a_bar_takes_a_width_not_an_end_date."""
    finish = start + datetime.timedelta(days=length)
    first, last = matplotlib_dates.date2num(start), matplotlib_dates.date2num(finish)
    npt.assert_array_equal(_drawn_bar(first, last - first), _drawn_bar(last, first - last))


@given(BAR_DAY)
@SLOW
def test_the_day_number_comes_back_as_an_instant_in_a_zone_and_not_as_a_date(day):
    """`num2date` is documented at the same tag as returning `datetime.datetime` objects, "returned in
    timezone *tz*", and the default zone is configured rather than absent. So the round trip through
    the chart's numbering does not return what went into it: it returns midnight of that day in a zone,
    which equals the date only after `.date()` is taken, and comparing it with the naive datetime of
    the same day raises TypeError instead of answering. Replaces the typed
    `isinstance(back, datetime.datetime)`, `str(back.tzinfo) == 'UTC'` and `back.date() == day` of case
    a_bar_takes_a_width_not_an_end_date."""
    back = matplotlib_dates.num2date(matplotlib_dates.date2num(day))
    npt.assert_equal(back.date(), day)
    npt.assert_equal(back, datetime.datetime.combine(day, datetime.time(), tzinfo=back.tzinfo))
    with pytest.raises(TypeError):
        back < datetime.datetime.combine(day, datetime.time())


@given(_schedule_table(), st.data())
@SLOW
def test_a_table_added_without_declared_columns_overwrites_the_header_row_that_was_written(table,
                                                                                          source):
    """XlsxWriter 3.2.9 gives every column of a table a default name, `"Column" + str(col_id)` in
    xlsxwriter/worksheet.py at tag RELEASE_3.2.9, and writes it into the sheet under the comment
    "Write the column headers to the worksheet." unless the call declared a header for that column.
    The header row the workbook already held is gone, and what replaces it does not depend on it: two
    schedules whose column names differ come back with the same first row. Two independent readers
    agree on the whole grid, openpyxl and the Rust calamine reader, so this is in the file rather than
    in one reader. Replaces the typed `silent[0] == ['Column1', 'Column2', 'Column3']` of case
    a_bar_takes_a_width_not_an_end_date."""
    columns, rows = table
    others = source.draw(st.lists(TABLE_COLUMN, min_size=len(columns), max_size=len(columns),
                                  unique=True))
    assume(others != columns)
    written = _schedule_workbook(columns, rows, declare=False)
    npt.assert_array_equal(_openpyxl_grid(written), _calamine_grid(written))
    npt.assert_array_equal(_openpyxl_grid(written)[0],
                           _openpyxl_grid(_schedule_workbook(others, rows, declare=False))[0])
    npt.assert_array_equal(_openpyxl_grid(written)[1:], rows)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_openpyxl_grid(written)[0], columns)


@given(_schedule_table())
@SLOW
def test_declaring_the_columns_keeps_the_headers_the_workbook_was_written_with(table):
    """The same call with the headers declared keeps them: both readers return the generated column
    names as the first row and the generated body under them. The difference between a schedule that
    reads back and one that does not is one option on one call, and nothing in the file records which
    was used. Replaces the typed `declared[0] == columns` and
    `declared[1] == ['v20', '2026-09-08', '2026-09-10']` of case
    a_bar_takes_a_width_not_an_end_date."""
    columns, rows = table
    written = _schedule_workbook(columns, rows, declare=True)
    npt.assert_array_equal(_openpyxl_grid(written), _calamine_grid(written))
    npt.assert_array_equal(_openpyxl_grid(written)[0], columns)
    npt.assert_array_equal(_openpyxl_grid(written)[1:], rows)


@given(_schedule_table(), BEYOND_THE_SHEET)
@SLOW
def test_a_table_reports_one_refusal_by_a_return_code_and_another_by_raising(table, beyond):
    """`add_table` is documented at tag RELEASE_3.2.9 as returning 0 for success and -1, -2 or -3 for
    the three ways it can fail, so a caller that does not read the return value is told nothing. That
    is only half of it: a range that runs off the end of the sheet comes back as a code, and a range
    that overlaps a table already added raises `OverlappingRange` instead. One call has two failure
    channels, and the guard module's own `if code != 0` sees only one of them."""
    columns, rows = table
    buffer = io.BytesIO()
    book = xlsxwriter.Workbook(buffer, {'in_memory': True})
    sheet = book.add_worksheet('schedule')
    accepted = sheet.add_table(0, 0, len(rows), len(columns) - 1, None)
    refused = sheet.add_table(len(rows) + 2, 0, beyond, len(columns) - 1, None)
    with pytest.raises(xlsxwriter.exceptions.OverlappingRange):
        sheet.add_table(0, 0, len(rows), len(columns) - 1, None)
    book.close()
    with pytest.raises(AssertionError):
        npt.assert_equal(refused, accepted)


# ------------------------------------------------- a day that no one worked, and an effort split over days
EFFORT_HOURS = st.integers(min_value=1, max_value=400)
SPLIT_DAYS = st.integers(min_value=1, max_value=200)
SPLIT_LOSES_THE_TOTAL = tuple((hours, days) for hours in range(1, 20) for days in range(2, 60)
                              if sum([hours / days] * days) != float(hours))
SPLIT_KEEPS_THE_TOTAL = tuple((hours, days) for hours in range(1, 20) for days in range(2, 60)
                              if sum([hours / days] * days) == float(hours))


@st.composite
def _assignments(draw, minimum=1):
    """One assignment per generated identifier, each carrying the days it was booked against. The list
    may be empty and it may be missing altogether, so both cases come out of the strategy."""
    size = draw(st.integers(min_value=minimum, max_value=6))
    booked = draw(st.lists(st.one_of(st.none(),
                                     st.lists(st.text(alphabet='abcdefghij', min_size=1, max_size=4),
                                              max_size=3)),
                           min_size=size, max_size=size))
    return [str(index) for index in range(size)], booked


@st.composite
def _assignments_with_an_empty_booking(draw):
    """The same assignments with one drawn position booked against no days, so the case the engines
    disagree about is generated rather than filtered for."""
    identifiers, booked = draw(_assignments())
    booked = list(booked)
    booked[draw(st.integers(min_value=0, max_value=len(booked) - 1))] = []
    return identifiers, booked


@st.composite
def _assignments_with_an_empty_and_a_missing_booking(draw):
    """The same again with one drawn position booked against no days and another with no booking at
    all, which are the two records the libraries hold apart differently."""
    identifiers, booked = draw(_assignments(minimum=2))
    booked = list(booked)
    first, second = draw(st.lists(st.integers(min_value=0, max_value=len(booked) - 1),
                                  min_size=2, max_size=2, unique=True))
    booked[first], booked[second] = [], None
    return identifiers, booked


def _polars_assignments(identifiers, booked):
    return pl.DataFrame({'id': identifiers, 'days': booked},
                        schema={'id': pl.String, 'days': pl.List(pl.String)})


def _duckdb_unnested(identifiers, booked):
    """The same assignments through DuckDB's UNNEST, which is a third implementation of the same
    reshaping and shares nothing with either dataframe library."""
    frame = _polars_assignments(identifiers, booked)
    with duckdb.connect() as connection:
        return connection.sql('select id, unnest(days) as day from frame').pl().to_dicts()


@given(_assignments())
@SLOW
def test_an_empty_day_list_becomes_a_row_in_one_engine_and_no_row_in_another(assignments):
    """P145 explodes the booked days and counts the rows. pandas 2.2.3 documents explode as
    "Transform each element of a list-like to a row, replicating index values" and its own example in
    pandas/core/frame.py at tag v2.2.3 shows a row whose value is `[]` coming back as NaN, so an
    assignment booked against no days still produces a row. DuckDB 1.5.5's UNNEST produces none. The
    two row counts differ by exactly the number of assignments that named no day, which is a count of
    the generated input rather than a number anyone typed. Replaces the typed `len(exploded) == 3` and
    `int(exploded['days'].isna().sum()) == 1` of handoff_guards_v15.py case
    an_empty_day_list_becomes_a_phantom_day."""
    identifiers, booked = assignments
    exploded = pd.DataFrame({'id': identifiers, 'days': booked}).explode('days')
    unnested = _duckdb_unnested(identifiers, booked)
    empty_or_missing = sum(1 for days in booked if not days)
    npt.assert_equal(len(exploded) - len(unnested), empty_or_missing)
    npt.assert_equal(int(exploded['days'].isna().sum()), empty_or_missing)


@given(_assignments())
@SLOW
def test_the_option_that_decides_whether_that_row_appears_is_named_in_the_second_implementation(
        assignments):
    """polars 1.44.1 makes the same decision an argument and documents both halves of it in
    py-polars/src/polars/dataframe/frame.py at tag py-1.44.1: `empty_as_null` is "Explode an empty
    list/array into a `null`" and `keep_nulls` is "Explode a `null` list/array into a `null`". Asked
    with both on it returns the rows pandas returns; asked with both off it returns the rows DuckDB
    returns. The disagreement between the two engines is therefore one documented option, and the
    chain that counts rows after an explode has not said which side of it the count was taken on."""
    identifiers, booked = assignments
    exploded = pd.DataFrame({'id': identifiers, 'days': booked}).explode('days')
    frame = _polars_assignments(identifiers, booked)
    as_pandas = frame.explode('days', empty_as_null=True, keep_nulls=True)
    as_duckdb = frame.explode('days', empty_as_null=False, keep_nulls=False)
    npt.assert_array_equal(as_pandas['id'].to_list(), list(exploded['id']))
    npt.assert_array_equal([row['id'] for row in as_duckdb.to_dicts()],
                           [row['id'] for row in _duckdb_unnested(identifiers, booked)])
    npt.assert_array_equal([row['day'] for row in _duckdb_unnested(identifiers, booked)],
                           as_duckdb['days'].to_list())


@given(_assignments_with_an_empty_booking())
@SLOW
def test_the_second_implementation_warns_that_the_default_deciding_this_is_changing(assignments):
    """Called without the option, polars 1.44.1 raises a DeprecationWarning saying the default is
    about to move, and the two answers it is moving between are the two engines' answers. So the row
    count after an explode is not only a question of which library ran but of which version of one of
    them, and the library says so at the call site."""
    identifiers, booked = assignments
    frame = _polars_assignments(identifiers, booked)
    with pytest.warns(DeprecationWarning):
        undecided = frame.explode('days')
    npt.assert_array_equal(undecided['id'].to_list(),
                           frame.explode('days', empty_as_null=True)['id'].to_list())
    with pytest.raises(AssertionError):
        npt.assert_array_equal(undecided['id'].to_list(),
                               frame.explode('days', empty_as_null=False)['id'].to_list())


@given(_assignments_with_an_empty_and_a_missing_booking())
@SLOW
def test_a_missing_day_list_and_an_empty_one_are_one_row_after_the_explode(assignments):
    """An assignment booked against no days and an assignment whose booking is missing altogether are
    two different records, and pandas' explode returns a missing value for both, so `isna` cannot tell
    them apart afterwards and a chain that drops the nulls drops both. polars keeps the two questions
    separate: with `empty_as_null` off and `keep_nulls` on, the empty booking loses its row and the
    missing booking keeps one, which is a distinction pandas' explode has no argument for."""
    identifiers, booked = assignments
    exploded = pd.DataFrame({'id': identifiers, 'days': booked}).explode('days')
    frame = _polars_assignments(identifiers, booked)
    missing = [identifier for identifier, days in zip(identifiers, booked) if days is None]
    npt.assert_array_equal(sorted(set(exploded.loc[exploded['days'].isna(), 'id'])),
                           sorted(identifier for identifier, days in zip(identifiers, booked)
                                  if not days))
    npt.assert_array_equal(
        sorted(set(frame.explode('days', empty_as_null=False, keep_nulls=True)
                   .filter(pl.col('days').is_null())['id'].to_list())),
        sorted(missing))


@given(_assignments())
@SLOW
def test_dropping_the_rows_an_empty_list_produced_leaves_the_days_that_were_declared(assignments):
    """What survives the drop is exactly the days the assignments named, in order, in all three
    engines. The phantom rows are therefore removable and the question is only whether anyone
    removed them; nothing else about the reshaping differs. Replaces the typed `len(real) == 2` of
    case an_empty_day_list_becomes_a_phantom_day."""
    identifiers, booked = assignments
    declared = [day for days in booked if days for day in days]
    exploded = pd.DataFrame({'id': identifiers, 'days': booked}).explode('days')
    npt.assert_array_equal(list(exploded.dropna(subset=['days'])['days']), declared)
    npt.assert_array_equal([row['day'] for row in _duckdb_unnested(identifiers, booked)], declared)
    npt.assert_array_equal(
        _polars_assignments(identifiers, booked)
        .explode('days', empty_as_null=False, keep_nulls=False)['days'].to_list(), declared)


@given(EFFORT_HOURS, SPLIT_DAYS)
@SLOW
def test_an_exact_split_of_effort_adds_back_to_the_effort_that_was_declared(hours, days):
    """The daily share as an exact rational: the shares always add back to the declared effort, for
    every generated pair, because Fraction divides exactly. Replaces the typed `exact_share('16', 2)
    == Fraction(8)` and `sum([exact_share('8', 6)] * 6) == Fraction(8)` of case
    an_empty_day_list_becomes_a_phantom_day."""
    share = Fraction(hours) / days
    npt.assert_array_equal(sum([share] * days), Fraction(hours))
    npt.assert_array_equal(share * days, Fraction(hours))


@given(st.sampled_from(SPLIT_LOSES_THE_TOTAL), st.sampled_from(SPLIT_KEEPS_THE_TOTAL))
@SLOW
def test_the_same_split_in_floats_stays_close_and_does_not_always_add_back(losing, keeping):
    """The two regions are read off IEEE arithmetic itself at import rather than chosen: every
    (effort, days) pair below sixty days is sorted by whether the float shares add back to the effort.
    Both are non-empty, the losing one is nearly three times the larger, and on both the float total is
    within numpy's default tolerance of the exact one, so nothing here is visibly wrong. Which side a
    pair falls on is not a property of the day count: forty-one of the day counts appear on both sides,
    so the same schedule split over the same number of days conserves one effort and loses another.
    Replaces the typed
    `sum([8 / 6] * 6) == 7.999999999999999` and `sum([10 / 3] * 3) == 10.0` of case
    an_empty_day_list_becomes_a_phantom_day."""
    for hours, days in (losing, keeping):
        npt.assert_allclose(sum([hours / days] * days), float(Fraction(hours)))
    npt.assert_array_equal(sum([keeping[0] / keeping[1]] * keeping[1]), float(keeping[0]))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(sum([losing[0] / losing[1]] * losing[1]), float(losing[0]))


@given(EFFORT_HOURS)
@SLOW
def test_effort_declared_against_no_days_is_a_refusal_in_one_arithmetic_and_an_infinity_in_another(
        hours):
    """The guard module blocks a split over zero days with its own check. The primitives do not agree
    on what that is. Fraction and the built-in float division both raise ZeroDivisionError, so the
    refusal is the library's; numpy's float division returns inf and only warns, so the same
    quantity divided the same way becomes a number that will pass every later comparison. Replaces the
    typed `g.rejects(g.Blocked, lambda: exact_share('4', 0))` of case
    an_empty_day_list_becomes_a_phantom_day."""
    with pytest.raises(ZeroDivisionError):
        Fraction(hours) / 0
    with pytest.raises(ZeroDivisionError):
        hours / 0
    with pytest.warns(RuntimeWarning):
        npt.assert_equal(np.float64(hours) / np.float64(0), np.inf)


# --------------------------------------------------- a responsibility matrix, and the cells nobody filled
TASK_NAME = st.text(alphabet='abcdefgh', min_size=1, max_size=6)
ROLE_NAME = st.text(alphabet='ijklmnop', min_size=1, max_size=6)
RESPONSIBILITY_CODE = st.text(alphabet='ACIR', min_size=1, max_size=1)
UNDECLARED_ROLE_NAME = st.text(alphabet='qrstuv', min_size=1, max_size=6)


@st.composite
def _responsibility_cells(draw, minimum_roles=1):
    """A declared inventory of tasks and roles, and one cell for a drawn subset of the pairs, so the
    pairs nobody filled in come out of the strategy rather than being authored."""
    tasks = draw(st.lists(TASK_NAME, min_size=1, max_size=4, unique=True))
    roles = draw(st.lists(ROLE_NAME, min_size=minimum_roles, max_size=4, unique=True))
    pairs = draw(st.lists(st.tuples(st.sampled_from(tasks), st.sampled_from(roles)),
                          min_size=1, max_size=len(tasks) * len(roles), unique=True))
    codes = draw(st.lists(RESPONSIBILITY_CODE, min_size=len(pairs), max_size=len(pairs)))
    return tasks, roles, [{'task': task, 'role': role, 'code': code}
                          for (task, role), code in zip(pairs, codes)]


@st.composite
def _responsibility_cells_with_an_unmentioned_role(draw):
    """The same inventory with the cells drawn only from the roles other than one, so a declared role
    the data never names is generated rather than filtered for."""
    tasks = draw(st.lists(TASK_NAME, min_size=1, max_size=4, unique=True))
    roles = draw(st.lists(ROLE_NAME, min_size=2, max_size=4, unique=True))
    absent = draw(st.sampled_from(roles))
    named = [role for role in roles if role != absent]
    pairs = draw(st.lists(st.tuples(st.sampled_from(tasks), st.sampled_from(named)),
                          min_size=1, max_size=len(tasks) * len(named), unique=True))
    codes = draw(st.lists(RESPONSIBILITY_CODE, min_size=len(pairs), max_size=len(pairs)))
    return tasks, roles, [{'task': task, 'role': role, 'code': code}
                          for (task, role), code in zip(pairs, codes)], absent


def _pandas_matrix(cells):
    return pd.DataFrame(cells).pivot(index='task', columns='role', values='code')


def _polars_matrix(cells):
    return pl.DataFrame(cells).pivot(on='role', index='task', values='code')


def _duckdb_matrix(cells):
    frame = pl.DataFrame(cells)
    with duckdb.connect() as connection:
        return connection.sql('pivot frame on role using first(code) group by task').pl()


def _reindexed(cells, tasks, roles):
    return _pandas_matrix(cells).reindex(index=tasks, columns=roles)


def _filled(wide):
    """The cells a pandas wide table holds, as a mapping from the pair to the code. Row and column
    order do not survive this, which is what lets the three engines be compared at all."""
    return {(task, role): code for task, row in wide.iterrows() for role, code in row.items()
            if pd.notna(code)}


def _filled_frame(wide):
    """The same reading of a polars wide table, whichever engine produced it."""
    return {(row['task'], role): row[role] for row in wide.to_dicts()
            for role in wide.columns if role != 'task' and row[role] is not None}


@given(_responsibility_cells())
@SLOW
def test_three_engines_pivot_the_same_cells_into_the_same_matrix(inventory):
    """P146 builds a responsibility matrix with pandas' pivot. Two independent implementations of the
    same reshaping produce the same cells on generated inputs: polars 1.44.1's pivot and DuckDB 1.5.5's
    PIVOT statement, which shares nothing with either dataframe library. All three hold exactly the
    pairs the generated cells named, and each cell holds the code that cell carried. Replaces the typed
    `matrix.loc['t1', 'ops'] == 'A'` and `matrix.loc['t2', 'ops'] == 'R'` of handoff_guards_v15.py case
    a_blank_matrix_cell_needs_an_explicit_state."""
    _, _, cells = inventory
    declared = {(cell['task'], cell['role']): cell['code'] for cell in cells}
    npt.assert_equal(_filled(_pandas_matrix(cells)), declared)
    npt.assert_equal(_filled_frame(_polars_matrix(cells)), declared)
    npt.assert_equal(_filled_frame(_duckdb_matrix(cells)), declared)


@given(st.lists(TASK_NAME, min_size=1, max_size=3, unique=True),
       st.lists(ROLE_NAME, min_size=2, max_size=4, unique=True),
       st.lists(RESPONSIBILITY_CODE, min_size=4, max_size=4))
@SLOW
def test_the_engines_put_the_columns_of_the_matrix_in_two_different_orders(tasks, roles, codes):
    """The cells are written with the roles in the reverse of their sorted order, so first appearance
    and sorted order disagree by construction. pandas and DuckDB both sort the pivoted columns; polars
    keeps the order the roles first appeared in. A matrix read by position rather than by name is
    therefore a different matrix in the two libraries, and only naming the columns -- which is what the
    reindex against the declared roles does -- makes them agree."""
    ordered = sorted(roles, reverse=True)
    cells = [{'task': tasks[0], 'role': role, 'code': code}
             for role, code in zip(ordered, itertools.cycle(codes))]
    npt.assert_array_equal(list(_pandas_matrix(cells).columns), sorted(roles))
    npt.assert_array_equal([column for column in _duckdb_matrix(cells).columns if column != 'task'],
                           sorted(roles))
    npt.assert_array_equal([column for column in _polars_matrix(cells).columns if column != 'task'],
                           ordered)
    with pytest.raises(AssertionError):
        npt.assert_array_equal([column for column in _polars_matrix(cells).columns
                                if column != 'task'], sorted(roles))


@given(_responsibility_cells_with_an_unmentioned_role())
@SLOW
def test_a_declared_role_no_cell_names_is_in_no_pivot_and_appears_only_after_the_reindex(inventory):
    """A pivot carries the roles the data mentions and no others, in all three engines. The role that
    no cell named is not an empty column anywhere: it is absent, and the matrix cannot be asked about
    it. It appears only when the wide table is reindexed against the declared inventory, so the blank
    cell the case records is produced by the declared list and not by the data. Replaces the typed
    `pd.isna(matrix.loc['t2', 'legal'])` of case a_blank_matrix_cell_needs_an_explicit_state."""
    tasks, roles, cells, _ = inventory
    mentioned = sorted({cell['role'] for cell in cells})
    npt.assert_array_equal(sorted(_pandas_matrix(cells).columns), mentioned)
    npt.assert_array_equal(sorted(column for column in _polars_matrix(cells).columns
                                  if column != 'task'), mentioned)
    npt.assert_array_equal(sorted(column for column in _duckdb_matrix(cells).columns
                                  if column != 'task'), mentioned)
    npt.assert_array_equal(list(_reindexed(cells, tasks, roles).columns), roles)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(mentioned, sorted(roles))


@given(_responsibility_cells(), st.data())
@SLOW
def test_a_task_and_role_named_twice_is_refused_by_two_engines_and_answered_by_the_third(inventory,
                                                                                        source):
    """The same pair given two codes. pandas raises ValueError, because reshaping needs the pair to be
    unique; polars raises ComputeError, saying its aggregation expected one value and got two. DuckDB
    is asked the same question through an aggregate and answers with one of the two codes, silently,
    which is the shape of every PIVOT statement: the aggregate is mandatory and choosing it chooses
    what a duplicate means. Replaces the typed
    `g.rejects(ValueError, lambda: raci_matrix(duplicate, ...))` of case
    a_blank_matrix_cell_needs_an_explicit_state."""
    _, _, cells = inventory
    repeated = source.draw(st.sampled_from(cells))
    second = source.draw(RESPONSIBILITY_CODE)
    duplicated = cells + [dict(repeated, code=second)]
    with pytest.raises(ValueError):
        _pandas_matrix(duplicated)
    with pytest.raises(pl.exceptions.ComputeError):
        _polars_matrix(duplicated)
    answered = _filled_frame(_duckdb_matrix(duplicated))
    npt.assert_array_equal(sorted(answered), sorted(_filled_frame(_duckdb_matrix(cells))))
    npt.assert_array_equal(
        sorted({answered[(repeated['task'], repeated['role'])]} | {repeated['code'], second}),
        sorted({repeated['code'], second}))


@given(_responsibility_cells())
@SLOW
def test_the_unassigned_cells_are_exactly_the_declared_pairs_no_cell_named(inventory):
    """After the reindex the matrix has a cell for every declared pair, and the ones holding nothing
    are exactly the pairs the generated cells did not name, which itertools computes as the difference
    between the Cartesian product and the pairs. Replaces the typed
    `sum(v == 'assigned' ...) == 3` and `sum(v == 'unassigned' ...) == 1` of case
    a_blank_matrix_cell_needs_an_explicit_state."""
    tasks, roles, cells = inventory
    reindexed = _reindexed(cells, tasks, roles)
    blank = sorted((task, role) for task, row in reindexed.iterrows()
                   for role, code in row.items() if pd.isna(code))
    npt.assert_array_equal(blank,
                           sorted(set(itertools.product(tasks, roles))
                                  - {(cell['task'], cell['role']) for cell in cells}))
    npt.assert_equal(int(reindexed.notna().sum().sum()), len(cells))


@given(_responsibility_cells(), UNDECLARED_ROLE_NAME)
@SLOW
def test_how_many_cells_are_unassigned_is_a_property_of_the_declared_inventory(inventory, extra):
    """The count of blank cells is not in the data. Reindexing the same cells against a longer list of
    declared roles produces more of them, by exactly the number of tasks, and nothing about the cells
    changed. A chain that reports how much of a responsibility matrix is unassigned is reporting on the
    list it was handed as much as on the assignments."""
    tasks, roles, cells = inventory
    npt.assert_equal(int(_reindexed(cells, tasks, roles).isna().sum().sum()),
                     len(tasks) * len(roles) - len(cells))
    npt.assert_equal(int(_reindexed(cells, tasks, roles + [extra]).isna().sum().sum()),
                     len(tasks) * (len(roles) + 1) - len(cells))
    with pytest.raises(AssertionError):
        npt.assert_equal(int(_reindexed(cells, tasks, roles + [extra]).isna().sum().sum()),
                         int(_reindexed(cells, tasks, roles).isna().sum().sum()))


@given(_responsibility_cells(), st.data())
@SLOW
def test_the_matrix_names_the_tasks_that_carry_no_accountable_role(inventory, source):
    """One of the codes the generated cells used is drawn as the accountable one, and the tasks whose
    row does not carry it are exactly the tasks no cell gave it to. The matrix can answer that question
    only because the reindex put every declared task in it: a task with no cell at all is a row of
    blanks rather than a missing row. Replaces the typed `accountable['t1'] == ['ops']` and
    `accountable['t2'] == []` of case a_blank_matrix_cell_needs_an_explicit_state."""
    tasks, roles, cells = inventory
    accountable = source.draw(st.sampled_from(sorted({cell['code'] for cell in cells})))
    reindexed = _reindexed(cells, tasks, roles)
    npt.assert_array_equal(
        sorted(task for task in tasks if not (reindexed.loc[task] == accountable).any()),
        sorted(set(tasks) - {cell['task'] for cell in cells if cell['code'] == accountable}))
    npt.assert_array_equal(sorted(reindexed.index), sorted(tasks))


# ---------------------------------------------------------------- a chart saved twice
GLYPH_INDEX_ORACLE_JS = pathlib.Path(__file__).with_name('glyph_index_oracle.js')
OPENTYPE_DIRECTORY = pathlib.Path(os.environ.get('OPENTYPE_DIR', str(pathlib.Path.home() / 'opentype-oracle')))
opentype_available = (shutil.which('node') is not None
                      and (OPENTYPE_DIRECTORY / 'node_modules' / 'opentype.js').is_dir())
SVG_NAMESPACE = '{http://www.w3.org/2000/svg}'
XLINK_NAMESPACE = '{http://www.w3.org/1999/xlink}'
DUBLIN_CORE_NAMESPACE = '{http://purl.org/dc/elements/1.1/}'
CHART_CELL_ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789 -'
CHART_CELL = st.text(alphabet=CHART_CELL_ALPHABET, min_size=1, max_size=6)
CHART_SALT = st.text(alphabet='0123456789abcdef', min_size=1, max_size=8)
CHART_SERIES = st.lists(st.integers(min_value=-100, max_value=100), min_size=2, max_size=8)
DEJAVU_SANS = matplotlib_font_manager.findfont(
    matplotlib_font_manager.FontProperties(family='DejaVu Sans'))


def _generated_chart_table():
    """A table of generated cells: one row of column labels and one to three body rows of that width."""
    return st.integers(min_value=1, max_value=3).flatmap(
        lambda width: st.tuples(st.lists(CHART_CELL, min_size=width, max_size=width),
                                st.lists(st.lists(CHART_CELL, min_size=width, max_size=width),
                                         min_size=1, max_size=3)))


def _table_graphic(columns, rows, image_format, *, salt=None, dated=False, fonttype=None):
    """One table drawn by matplotlib and saved. Only rcParams and `savefig`'s own `metadata` argument
    change between calls; nothing here computes a value."""
    overrides = {}
    if salt is not None:
        overrides['svg.hashsalt'] = salt
    if fonttype is not None:
        overrides['svg.fonttype'] = fonttype
    with matplotlib.rc_context(overrides):
        figure, axes = matplotlib_pyplot.subplots(figsize=(6, 2))
        axes.axis('off')
        axes.table(cellText=rows, colLabels=columns, loc='center')
        buffer = io.BytesIO()
        figure.savefig(buffer, format=image_format,
                       metadata=None if dated or image_format != 'svg' else {'Date': None})
        matplotlib_pyplot.close(figure)
        return buffer.getvalue()


def _plot_graphic(values, *, salt=None):
    """The same figure with a line drawn inside the axes, which is what puts a clip path in the file."""
    overrides = {'svg.hashsalt': salt} if salt is not None else {}
    with matplotlib.rc_context(overrides):
        figure, axes = matplotlib_pyplot.subplots(figsize=(3, 2))
        axes.plot(values)
        buffer = io.BytesIO()
        figure.savefig(buffer, format='svg', metadata={'Date': None})
        matplotlib_pyplot.close(figure)
        return buffer.getvalue()


def _svg_text_nodes(data):
    """The text of every <text> element, read twice: by libxml2 through lxml and by expat through
    ElementTree. Every test below compares the two readings before it uses either."""
    return ([node.text for node in lxml_etree.fromstring(data).iter(SVG_NAMESPACE + 'text')],
            [node.text for node in ElementTree.fromstring(data).iter(SVG_NAMESPACE + 'text')])


def _svg_dates(data):
    """The Dublin Core date the SVG carries, read by the same two parsers."""
    return ([node.text for node in lxml_etree.fromstring(data).iter(DUBLIN_CORE_NAMESPACE + 'date')],
            [node.text for node in ElementTree.fromstring(data).iter(DUBLIN_CORE_NAMESPACE + 'date')])


def _svg_clip_paths(data):
    """How many <clipPath> elements the file holds, read by the same two parsers."""
    return (len(list(lxml_etree.fromstring(data).iter(SVG_NAMESPACE + 'clipPath'))),
            len(list(ElementTree.fromstring(data).iter(SVG_NAMESPACE + 'clipPath'))))


def _glyph_index(reference):
    """The number matplotlib put in one glyph reference. Splitting a string is all that happens here."""
    return int(reference.rsplit('-', 1)[1], 16)


def _svg_glyph_references(data):
    """The glyph every <use> element points at, in document order, read by the same two parsers."""
    return ([_glyph_index(node.get(XLINK_NAMESPACE + 'href'))
             for node in lxml_etree.fromstring(data).iter(SVG_NAMESPACE + 'use')],
            [_glyph_index(node.get(XLINK_NAMESPACE + 'href'))
             for node in ElementTree.fromstring(data).iter(SVG_NAMESPACE + 'use')])


@functools.lru_cache(maxsize=1)
def _dejavu_glyph_indices():
    """The font matplotlib drew with, read by fontTools instead of by FreeType: the glyph order and the
    best cmap are that library's own accessors, and the glyph index of a character is its position in
    the glyph order, which is what `enumerate` over that list says."""
    font = TTFont(DEJAVU_SANS, lazy=True)
    positions = {name: index for index, name in enumerate(font.getGlyphOrder())}
    return {chr(codepoint): positions[name] for codepoint, name in font.getBestCmap().items()
            if name in positions}


def _fonttools_glyph_indices(text):
    return [_dejavu_glyph_indices()[character] for character in text]


@functools.lru_cache(maxsize=1)
def _dejavu_ligature_candidates():
    """Every character this font has a glyph for that the Unicode database decomposes into two
    characters of the cell alphabet. `unicodedata.decomposition` is CPython's own reading of the
    database's compatibility decompositions and the font's own cmap says which of those characters
    DejaVu Sans carries, so neither the pairs nor the ligature characters are typed here."""
    indices = _dejavu_glyph_indices()
    candidates = {}
    for character in indices:
        parts = unicodedata.decomposition(character).split()
        if parts[:1] == ['<compat>'] and len(parts) == 3:
            components = ''.join(chr(int(part, 16)) for part in parts[1:])
            if all(component in CHART_CELL_ALPHABET for component in components):
                candidates[components] = character
    return candidates


def _ligated(text):
    """The same text with every pair this font ligates replaced by the single Unicode character that
    names that ligature. `str.replace` is the only operation; which pairs to replace is read off
    matplotlib at import and which character replaces them off the Unicode database."""
    for pair in CHART_LIGATED:
        text = text.replace(pair, _dejavu_ligature_candidates()[pair])
    return text


def _node_glyph_indices(text):
    """The same mapping in another runtime. The shim parses argv, calls opentype.js and prints one index
    per line; the Python side runs subprocess and splits stdout."""
    completed = subprocess.run(
        ['node', str(GLYPH_INDEX_ORACLE_JS), DEJAVU_SANS, text.encode('utf-8').hex()],
        capture_output=True, encoding='utf-8', check=True,
        env={**os.environ, 'NODE_PATH': str(OPENTYPE_DIRECTORY / 'node_modules')})
    return [int(line) for line in completed.stdout.split()]


CHART_LIGATED = tuple(pair for pair in _dejavu_ligature_candidates()
                      if _svg_glyph_references(_table_graphic([pair], [[pair]], 'svg'))[0]
                      != _fonttools_glyph_indices(pair + pair))
CHART_SAFE_ALPHABET = ''.join(character for character in CHART_CELL_ALPHABET
                              if all(character not in pair for pair in CHART_LIGATED))
CHART_SAFE_CELL = st.text(alphabet=CHART_SAFE_ALPHABET, min_size=1, max_size=6)
CHART_LIGATURE_CELL = st.tuples(st.text(alphabet=CHART_SAFE_ALPHABET, max_size=3),
                                st.sampled_from(CHART_LIGATED),
                                st.text(alphabet=CHART_SAFE_ALPHABET, max_size=3)).map(''.join)


def _generated_table_of(cell):
    """The same table shape as above over a given cell strategy: one row of column labels and one to
    three body rows of that width."""
    return st.integers(min_value=1, max_value=3).flatmap(
        lambda width: st.tuples(st.lists(cell, min_size=width, max_size=width),
                                st.lists(st.lists(cell, min_size=width, max_size=width),
                                         min_size=1, max_size=3)))


@given(_generated_chart_table())
@SLOW
def test_the_same_chart_saved_twice_is_two_different_files(table):
    """P133 saves a table of records as SVG and finds that saving it again gives different bytes. That
    reproduces on every generated table: matplotlib 3.11.1 writes a Dublin Core date into the file and,
    with no `SOURCE_DATE_EPOCH` set, takes it from `datetime.datetime.today().isoformat()` in
    `lib/matplotlib/backends/backend_svg.py` at tag v3.11.1, which carries microseconds. Replaces the
    typed `g.equal(loose_a == loose_b, False)` of handoff_guards_v14.py case
    matplotlib_svg_needs_a_fixed_hashsalt."""
    columns, rows = table
    with pytest.raises(AssertionError):
        npt.assert_array_equal(
            hashlib.sha256(_table_graphic(columns, rows, 'svg', dated=True)).hexdigest(),
            hashlib.sha256(_table_graphic(columns, rows, 'svg', dated=True)).hexdigest())


@given(_generated_chart_table())
@SLOW
def test_suppressing_the_timestamp_alone_makes_that_chart_reproducible(table):
    """The proof's remedy is `svg.hashsalt` together with a suppressed date. Only the second half of it
    does anything here: with `metadata={'Date': None}` and the shipped `svg.hashsalt: None` still in
    force, the same generated table saves to the same bytes twice. Replaces the typed
    `g.equal(fixed_a == fixed_b, True)` of case matplotlib_svg_needs_a_fixed_hashsalt, which set both
    and could not say which one mattered."""
    columns, rows = table
    npt.assert_array_equal(hashlib.sha256(_table_graphic(columns, rows, 'svg')).hexdigest(),
                           hashlib.sha256(_table_graphic(columns, rows, 'svg')).hexdigest())


@given(_generated_chart_table(), st.lists(CHART_SALT, min_size=2, max_size=2, unique=True))
@SLOW
def test_the_hash_salt_the_proof_fixes_changes_nothing_in_that_chart(table, salts):
    """Two different salts produce the same file, byte for byte, so the setting the proof relies on is
    inert for the figure the proof draws. matplotlib's own `matplotlibrc` at tag v3.11.1 documents it as
    "If not None, use this string as hash salt instead of uuid4", and `_make_id` in `backend_svg.py`
    is the only reader of it; a table on an axes with `axis('off')` never reaches that call."""
    columns, rows = table
    first, second = salts
    npt.assert_array_equal(hashlib.sha256(_table_graphic(columns, rows, 'svg', salt=first)).hexdigest(),
                           hashlib.sha256(_table_graphic(columns, rows, 'svg', salt=second)).hexdigest())


@given(_generated_chart_table(), CHART_SERIES)
@SLOW
def test_the_clip_path_the_salt_names_is_absent_from_a_table_and_present_in_a_plot(table, values):
    """What the salt names is the identifier of a clip path: the docstring of `_get_clippath_id` in
    `backend_svg.py` at tag v3.11.1 says it "allows plots that include custom clip paths to produce
    identical SVG output on each render, provided that the :rc:`svg.hashsalt` config setting and the
    ``SOURCE_DATE_EPOCH`` build-time environment variable are set to fixed values." The generated table
    holds fewer clip paths than a figure with a line drawn in its axes, which is why the salt does
    nothing to it and everything to the other. Both parsers count the same."""
    columns, rows = table
    table_counts = _svg_clip_paths(_table_graphic(columns, rows, 'svg'))
    plot_counts = _svg_clip_paths(_plot_graphic(values))
    npt.assert_array_equal(table_counts[0], table_counts[1])
    npt.assert_array_equal(plot_counts[0], plot_counts[1])
    npt.assert_array_equal(table_counts[0] < plot_counts[0], True)


@given(CHART_SERIES, st.lists(CHART_SALT, min_size=2, max_size=2, unique=True))
@SLOW
def test_a_chart_with_data_needs_the_salt_and_then_depends_on_which_salt(values, salts):
    """The same suppressed date that is enough for the table is not enough for a figure that draws
    inside its axes: the clip path takes a fresh `uuid4` on every render and the two files differ. A
    fixed salt makes that figure reproducible, and two different salts make it two different files, so
    the byte identity is a property of the salt a reader happens to configure and not of the chart.
    Replaces the typed `g.equal(b'<use ' in fixed_a, True)` reading of what the salt was doing."""
    first, second = salts
    with pytest.raises(AssertionError):
        npt.assert_array_equal(hashlib.sha256(_plot_graphic(values)).hexdigest(),
                               hashlib.sha256(_plot_graphic(values)).hexdigest())
    npt.assert_array_equal(hashlib.sha256(_plot_graphic(values, salt=first)).hexdigest(),
                           hashlib.sha256(_plot_graphic(values, salt=first)).hexdigest())
    with pytest.raises(AssertionError):
        npt.assert_array_equal(hashlib.sha256(_plot_graphic(values, salt=first)).hexdigest(),
                               hashlib.sha256(_plot_graphic(values, salt=second)).hexdigest())


@given(_generated_chart_table())
@SLOW
def test_the_raster_of_the_same_chart_is_reproducible_with_no_setting_at_all(table):
    """The PNG of the same generated table saves to the same bytes twice with the date left alone and no
    salt set, because the raster carries no timestamp and no identifier. Replaces the typed
    `g.equal(png_a == png_b, True)` of case matplotlib_svg_needs_a_fixed_hashsalt."""
    columns, rows = table
    npt.assert_array_equal(
        hashlib.sha256(_table_graphic(columns, rows, 'png', dated=True)).hexdigest(),
        hashlib.sha256(_table_graphic(columns, rows, 'png', dated=True)).hexdigest())


@given(_generated_chart_table(), st.integers(min_value=0, max_value=2_000_000_000))
@SLOW
def test_the_timestamp_comes_from_the_reproducible_builds_variable_when_it_is_set(table, epoch):
    """`backend_svg.py` at tag v3.11.1 reads `SOURCE_DATE_EPOCH` before it reaches the clock, citing
    https://reproducible-builds.org/specs/source-date-epoch/ -- the same variable the deterministic
    package cluster above turns on. With it set the chart is reproducible without touching `savefig`'s
    metadata, and the instant written into the file is the one pandas resolves that epoch to in UTC,
    which is a second implementation of the conversion and not matplotlib's line. Both parsers read the
    same date."""
    columns, rows = table
    with mock.patch.dict(os.environ, {'SOURCE_DATE_EPOCH': str(epoch)}):
        first = _table_graphic(columns, rows, 'svg', dated=True)
        second = _table_graphic(columns, rows, 'svg', dated=True)
    npt.assert_array_equal(hashlib.sha256(first).hexdigest(), hashlib.sha256(second).hexdigest())
    lxml_dates, expat_dates = _svg_dates(first)
    npt.assert_array_equal(lxml_dates, expat_dates)
    npt.assert_array_equal(lxml_dates, [pd.Timestamp(epoch, unit='s', tz='UTC').isoformat()])


@given(_generated_chart_table())
@SLOW
def test_the_shipped_font_default_leaves_no_readable_text_in_the_chart(table):
    """`matplotlibrc` at tag v3.11.1 ships `#svg.fonttype: path`, documented there as "path: Embed
    characters as paths". Under it the file both parsers read holds no <text> element at all, so a
    reader searching the chart for one of its own cells finds nothing, while the same table saved with
    the font named holds one <text> element per generated cell. Replaces the typed
    `g.equal(mpl.rcParams['svg.fonttype'], 'path')` and `g.equal(svg_text(fixed_a), [])` of case
    matplotlib_svg_needs_a_fixed_hashsalt."""
    columns, rows = table
    outlined, expat_outlined = _svg_text_nodes(_table_graphic(columns, rows, 'svg'))
    named, expat_named = _svg_text_nodes(_table_graphic(columns, rows, 'svg', fonttype='none'))
    npt.assert_array_equal(outlined, expat_outlined)
    npt.assert_array_equal(named, expat_named)
    npt.assert_array_equal(len(outlined), 0)
    npt.assert_array_equal(len(named), len(list(itertools.chain(columns, *rows))))


@given(_generated_chart_table())
@SLOW
def test_naming_the_font_recovers_every_cell_in_the_order_the_table_draws_them(table):
    """With `svg.fonttype` set to 'none' -- "Assume fonts are installed on the machine where the SVG
    will be viewed", in the same `matplotlibrc` -- the text nodes are exactly the generated column
    labels followed by the generated body cells. That order is matplotlib's own: `Table.draw` in
    `lib/matplotlib/table.py` at tag v3.11.1 iterates `for key in sorted(self._cells)` and `table()`
    adds the column labels at row 0 and the body at `row + offset`. Replaces the typed
    `g.equal(text, ['meeting', 'present', 'tsc-2023-11-08', '6', 'tsc-2023-12-06', '10'])`."""
    columns, rows = table
    named, expat_named = _svg_text_nodes(_table_graphic(columns, rows, 'svg', fonttype='none'))
    npt.assert_array_equal(named, expat_named)
    npt.assert_array_equal(named, list(itertools.chain(columns, *rows)))


@given(_generated_chart_table())
@SLOW
def test_naming_the_font_keeps_the_chart_reproducible(table):
    """Recovering the text costs nothing in reproducibility: with the date suppressed the readable file
    saves to the same bytes twice as well. Replaces the typed
    `g.equal(readable == table_graphic(...), True)` of case matplotlib_svg_needs_a_fixed_hashsalt."""
    columns, rows = table
    npt.assert_array_equal(
        hashlib.sha256(_table_graphic(columns, rows, 'svg', fonttype='none')).hexdigest(),
        hashlib.sha256(_table_graphic(columns, rows, 'svg', fonttype='none')).hexdigest())


@given(_generated_table_of(CHART_SAFE_CELL))
@SLOW
def test_the_default_file_holds_the_cells_only_as_glyph_indices_of_one_font(table):
    """What the default file does hold is one <use> element per character of the table, in the drawing
    order, each pointing at a glyph identifier that `TextToPath._get_glyph_repr` in
    `lib/matplotlib/textpath.py` at tag v3.11.1 builds as
    `urllib.parse.quote(f"{font.postscript_name}-{glyph:x}")` from a glyph index FreeType gave it
    through `matplotlib.ft2font`. fontTools 4.64.0 reads the same DejaVuSans.ttf a second way, in pure
    Python and without FreeType, and its glyph order and best cmap put every generated character at
    exactly that index. So the cells are in the file as positions in one font's glyph table, not as
    text. One character per glyph holds only away from the pairs this font ligates, which are taken out
    of this alphabet by execution rather than by hand and are the subject of the test below.
    Replaces the typed `g.equal(b'<use ' in fixed_a, True)` of case
    matplotlib_svg_needs_a_fixed_hashsalt."""
    columns, rows = table
    references, expat_references = _svg_glyph_references(_table_graphic(columns, rows, 'svg'))
    npt.assert_array_equal(references, expat_references)
    npt.assert_array_equal(references, _fonttools_glyph_indices(''.join(itertools.chain(columns, *rows))))


@pytest.mark.skipif(not opentype_available, reason='node and an opentype.js checkout are required')
@given(_generated_table_of(CHART_SAFE_CELL))
@ORACLE_PROCESS
def test_a_second_runtime_reads_the_same_glyph_indices_out_of_the_font_file(table):
    """A third implementation of the same mapping, in another runtime: opentype.js 2.0.0 under node
    v22.22.2 parses DejaVuSans.ttf itself and answers `charToGlyphIndex` for every generated character.
    It agrees with the indices matplotlib wrote, which is what makes the previous test a property of the
    font file rather than of fontTools. Only the mapping is a third implementation: asked to shape a
    string instead of to map a character, the same library refuses this font outright, and
    `stringToGlyphs` raises `Error: substitutionType : 62 lookupType: 6 - substFormat: 2 is not yet
    supported` on any text at all, so the ligature below has no witness in that runtime."""
    columns, rows = table
    npt.assert_array_equal(_svg_glyph_references(_table_graphic(columns, rows, 'svg'))[0],
                           _node_glyph_indices(''.join(itertools.chain(columns, *rows))))



@given(_generated_table_of(CHART_LIGATURE_CELL))
@SLOW
def test_a_pair_the_font_ligates_leaves_one_glyph_where_two_characters_were(table):
    """The one-glyph-per-character reading holds only where the font has no ligature for the pair. Which
    pairs those are is read off matplotlib at import over the candidates the Unicode database names: of
    the thirteen characters DejaVu Sans carries that decompose into two characters of this alphabet,
    three are substituted when the table is drawn and ten -- including the st ligature the font also
    carries -- are not. On a cell holding one of the three, the file has one <use> element where the
    text has two characters, so a reader resolving the file against the font character by character is
    wrong about the length of the cell before it is wrong about its text. What is written is not a
    glyph no character maps to: it is exactly the index the font's own cmap gives the single Unicode
    character that names that ligature, which is where the expected value here comes from."""
    columns, rows = table
    text = ''.join(itertools.chain(columns, *rows))
    references, expat_references = _svg_glyph_references(_table_graphic(columns, rows, 'svg'))
    npt.assert_array_equal(references, expat_references)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(references, _fonttools_glyph_indices(text))
    npt.assert_array_equal(references, _fonttools_glyph_indices(_ligated(text)))

# ---------------------------------------------------------------- a code that decodes to its url
QR_PAYLOAD = st.text(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~:/?#@!$&*+,;=',
                     min_size=1, max_size=60)
QR_FAMILY = tuple('https://example.org/packs/minutes/tsc-2024-%02d-%02d.md' % (month, day)
                  for month in range(1, 4) for day in range(1, 29))
QR_SCALE = 8
QR_SMALLER_SCALE = 4


def _qr_image(payload, scale=QR_SCALE):
    """One code written by segno at the error correction level the proof uses, decoded into the
    grayscale array both readers take. segno chooses the symbol: `make` is documented at tag 1.6.6 as
    producing "an optimal (minimal) (Micro) QR code with a maximal error correction level"."""
    buffer = io.BytesIO()
    segno.make(payload, error='h').save(buffer, kind='png', scale=scale, border=4)
    return cv2.imdecode(np.frombuffer(buffer.getvalue(), np.uint8), cv2.IMREAD_GRAYSCALE)


def _legacy_reading(image):
    """OpenCV's `QRCodeDetector`, whose whole documentation at tag 5.0.0 is "QR code detector."."""
    return cv2.QRCodeDetector().detectAndDecode(image)[0]


def _aruco_reading(image):
    """OpenCV's other detector, "QR code detector based on Aruco markers detection code." at the same
    tag. It is the one the chain calls."""
    return cv2.QRCodeDetectorAruco().detectAndDecode(image)[0]


def _zxing_readings(image):
    """Every barcode zxing-cpp reports in one image, as text. An image it finds nothing in gives an
    empty list rather than an empty string, which is a distinction OpenCV's return type cannot make."""
    return [barcode.text for barcode in zxingcpp.read_barcodes(image)]


def _zxing_symbol(payload, **options):
    """The same payload written by the other implementation, as the array of modules it draws."""
    barcode = zxingcpp.create_barcode(payload, zxingcpp.BarcodeFormat.QRCode, ec_level='H')
    return np.array(zxingcpp.write_barcode_to_image(barcode, **options))


def _zxing_modules(payload):
    """The side of the symbol the other implementation draws, in modules, with no quiet zone."""
    return _zxing_symbol(payload, scale=1, add_quiet_zones=False).shape


def _segno_modules(payload):
    """The same measurement from segno, whose `symbol_size` "Returns the symbol size (width x height)
    with the provided border and scaling factor"."""
    return segno.make(payload, error='h').symbol_size(border=0)


QR_MODE_ALPHABETS = ('0123456789', '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:',
                     'abcdefghijklmnopqrstuvwxyz')
QR_SINGLE_MODE_PAYLOAD = st.sampled_from(QR_MODE_ALPHABETS).flatmap(
    lambda alphabet: st.text(alphabet=alphabet, min_size=1, max_size=25))
QR_MIXED_PAYLOAD = st.tuples(st.text(alphabet='0123456789', min_size=7, max_size=11),
                             st.sampled_from('abcdefghijklmnopqrstuvwxyz_~?#@!&,;=')).map(''.join)


LEGACY_READING = {url: _legacy_reading(_qr_image(url)) for url in QR_FAMILY}
LEGACY_MISSES = tuple(url for url in QR_FAMILY if LEGACY_READING[url] != url)
LEGACY_HITS = tuple(url for url in QR_FAMILY if LEGACY_READING[url] == url)
LEGACY_RECOVERED_BY_SHRINKING = tuple(
    url for url in LEGACY_MISSES if _legacy_reading(_qr_image(url, QR_SMALLER_SCALE)) == url)


@given(QR_PAYLOAD)
@SLOW
def test_every_generated_payload_survives_the_code_round_trip(payload):
    """P138 records that every code decodes to its recorded URL and checks it with OpenCV, which is the
    only reader in the chain and wrote none of the codes. zxing-cpp 3.1.1 is a second implementation of
    the format: its own README at tag v3.1.1 calls ZXing-C++ "an open-source, multi-format
    linear/matrix barcode image processing library implemented in C++" with "no third-party
    dependencies (for the library itself)", and its `pyproject.toml` at that tag declares no runtime
    dependencies at all, so none of segno or OpenCV is under it. It reads back exactly the payload
    segno 1.6.6 encoded, for every generated payload. Replaces the typed `g.equal(decode_qr(png), url)`
    of handoff_guards_v14.py case every_code_decodes_to_its_recorded_url."""
    npt.assert_array_equal(_zxing_readings(_qr_image(payload)), [payload])


@given(QR_PAYLOAD)
@SLOW
def test_the_other_implementation_writes_a_code_the_chains_reader_reads(payload):
    """The round trip the other way round, which the case never runs: zxing-cpp writes the symbol and
    the Aruco detector the chain calls reads the same payload out of it. Since version 3.0 that writer
    is the zint library, named as the "default writing backend" in the same README, so this direction
    shares neither the encoder nor the decoder with the chain."""
    npt.assert_array_equal(_aruco_reading(_zxing_symbol(payload, scale=QR_SCALE)), payload)


@given(st.sampled_from(QR_FAMILY))
@SLOW
def test_both_encoders_draw_the_same_symbol_for_every_url_the_chain_records(url):
    """The case types that both of its URLs are version 6. Nothing here types a version: segno's `make`
    chooses "the minimal version which fits for the input data" and `symbol_size` "Returns the symbol
    size (width x height) with the provided border and scaling factor", both documented in
    raw.githubusercontent.com/heuer/segno/1.6.6/segno/__init__.py. Asked for any URL of the family at the
    same error correction level, the other implementation draws a symbol of exactly the same number of
    modules, so the version those two URLs share is a fact about the format rather than a choice segno
    made. Replaces `g.equal(segno.make(a).version, segno.make(b).version)`."""
    npt.assert_array_equal(_zxing_modules(url), _segno_modules(url))


@given(QR_SINGLE_MODE_PAYLOAD)
@SLOW
def test_two_encoders_choose_the_same_symbol_for_a_single_mode_payload(payload):
    """Where the whole payload belongs to one QR encoding mode the two encoders agree exactly. The three
    alphabets are the three modes themselves: the digits of numeric mode; the alphanumeric set, which is
    character for character segno's own `ALPHANUMERIC_CHARS` in segno/consts.py at 1.6.6, sitting beside
    the mode indicators the same file cites to "ISO/IEC 18004:2015(E) -- Table 2"; and lower-case
    letters, which fall outside that set and so are byte mode."""
    npt.assert_array_equal(_zxing_modules(payload), _segno_modules(payload))


@given(QR_PAYLOAD)
@SLOW
def test_the_encoder_that_segments_never_draws_the_larger_symbol(payload):
    """Over the whole generated payload region the two encoders are not interchangeable, but they are
    ordered: zint's symbol is never larger than segno's. `numpy.minimum` picks the smaller of the two
    side lengths and it is always zint's, which is the invariant that makes the divergence below
    one-sided."""
    npt.assert_array_equal(np.minimum(_zxing_modules(payload), _segno_modules(payload)),
                           _zxing_modules(payload))


@given(QR_MIXED_PAYLOAD)
@SLOW
def test_a_numeric_run_with_one_byte_character_gets_a_larger_symbol_from_segno(payload):
    """segno's own claim for `make` is that "an optimal (minimal) (Micro) QR code with a maximal error
    correction level is generated", and for a payload of one mode it is. For a run of seven to eleven
    digits followed by one character outside the alphanumeric set it is not: zint splits the payload
    into a numeric segment and a byte segment and fits a smaller symbol, while segno encodes the whole
    message in one mode and needs the next version up. Its own encoder says why -- `prepare_data` in
    raw.githubusercontent.com/heuer/segno/1.6.6/segno/encoder.py is documented as "If `content` is a
    string, an integer, or bytes, the returned tuple will have a single item", so a string is one
    segment and the segmentation is left to the caller. The region is a strategy bound, not a filter:
    every payload of that shape diverges."""
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_zxing_modules(payload), _segno_modules(payload))
    npt.assert_array_less(_zxing_modules(payload), _segno_modules(payload))


@given(QR_PAYLOAD)
@SLOW
def test_the_independent_reader_reports_the_error_level_the_writer_declared(payload):
    """The error correction level is written into the symbol and read back out of it: segno's `error`
    property is "Error correction level; either a string ("L", "M", "Q", "H")" and zxing-cpp's decoded
    barcode reports the same letter for every generated payload, which is what makes the level the
    chain asks for a fact about the file rather than an argument nobody checked."""
    npt.assert_array_equal([barcode.ec_level for barcode in zxingcpp.read_barcodes(_qr_image(payload))],
                           [segno.make(payload, error='h').error])


@given(st.sampled_from(LEGACY_MISSES))
@SLOW
def test_the_detector_most_examples_reach_for_reads_nothing_from_a_valid_code(url):
    """The case found one URL that `cv2.QRCodeDetector` silently fails on. Over a family of eighty-four URLs
    that differ only in a month and a day, the failures are read off the detector itself at import
    rather than chosen: sixteen of them come back as nothing. Every one of those codes is read
    correctly by the Aruco detector in the same library and by zxing-cpp, so the code is sound and the
    reading is not.
    Replaces the typed `g.equal(legacy[entries[1]['url']], '')`."""
    image = _qr_image(url)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_legacy_reading(image), url)
    npt.assert_array_equal(_aruco_reading(image), url)
    npt.assert_array_equal(_zxing_readings(image), [url])


@given(st.sampled_from(LEGACY_MISSES), st.sampled_from(LEGACY_HITS))
@SLOW
def test_the_codes_it_misses_are_the_same_symbol_as_the_codes_it_reads(missed, read):
    """What separates the two regions is not the size of the code. A URL the detector misses and a URL
    it reads produce the same version and the same symbol size, so nothing about the symbol predicts
    which side a record falls on, and a chain cannot check the size to know whether its code will be
    read. Replaces the typed `g.equal(segno.make(a).version, segno.make(b).version)` read as a claim
    about the two URLs of the case."""
    npt.assert_array_equal(segno.make(missed, error='h').version, segno.make(read, error='h').version)
    npt.assert_array_equal(segno.make(missed, error='h').symbol_size(),
                           segno.make(read, error='h').symbol_size())


@given(st.sampled_from(LEGACY_RECOVERED_BY_SHRINKING))
@SLOW
def test_a_smaller_image_of_the_same_code_is_the_one_the_legacy_detector_reads(url):
    """The case rescales its one failing code up through scales 4, 8 and 12, finds the legacy detector
    still blind at every one, and concludes that "the payload is what decides". It is not only the
    payload: of the sixteen URLs the detector misses at the scale the chain writes, fifteen are read
    correctly from the smaller image of the same code, and the sixteenth is the URL the case happened
    to pick. This region is read off the detector at import rather than chosen, and in it making a code
    bigger is what makes it unreadable. The other two readers read both sizes. Replaces the typed `g.equal(decode_qr_legacy(buf.getvalue()), '')` over the scale loop."""
    npt.assert_array_equal(_legacy_reading(_qr_image(url, QR_SMALLER_SCALE)), url)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_legacy_reading(_qr_image(url, QR_SCALE)), url)
    npt.assert_array_equal(_aruco_reading(_qr_image(url, QR_SCALE)), url)
    npt.assert_array_equal(_zxing_readings(_qr_image(url, QR_SMALLER_SCALE)), [url])


@given(st.integers(min_value=100, max_value=400))
@SLOW
def test_an_empty_payload_is_written_as_a_code_no_reader_reports(size):
    """segno accepts the empty string and writes a symbol for it, and the image it writes is not a blank
    page: the two do not even hold the same set of pixel values. No reader here reports a code in it.
    Both OpenCV detectors return the empty string, which is the same value they return for a blank page
    of any generated size, so nothing in that return type separates a code that was read from a code
    that was missed from no code at all; zxing-cpp returns no barcode for either, which at least does
    not name a payload. Replaces the typed `g.equal(decode_qr_legacy(blank_png()), '')` and the guard
    module's own Blocked wrapper around a blank page."""
    empty = _qr_image('')
    blank = np.full((size, size), 255, dtype=np.uint8)
    npt.assert_array_equal(_legacy_reading(empty), _legacy_reading(blank))
    npt.assert_array_equal(_aruco_reading(empty), _aruco_reading(blank))
    npt.assert_array_equal(_zxing_readings(empty), _zxing_readings(blank))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(np.unique(empty), np.unique(blank))


# ---------------------------------------------------------------- charts embedded in a brief
BRIEF_PAGE = (400, 400)
BRIEF_IMAGE = hyp_np.arrays(np.uint8, (8, 12), elements=st.integers(min_value=0, max_value=255))
BRIEF_IMAGES = st.lists(BRIEF_IMAGE, min_size=2, max_size=4)


def _brief_pdf(arrays, *, upward=False):
    """The chain's own writer: reportlab draws each generated image below the last on one page, at one
    point per pixel. Only library calls happen here -- OpenCV encodes the PNG, reportlab places it.
    With `upward` the same charts are drawn from the foot of the page up, so that the order they are
    drawn in is the reverse of the order a reader meets them going down the page."""
    written = io.BytesIO()
    page = rl_canvas.Canvas(written, pagesize=BRIEF_PAGE)
    for index, array in enumerate(arrays):
        step = (index + 1) * (array.shape[0] + 10)
        page.drawImage(ImageReader(io.BytesIO(cv2.imencode('.png', array)[1].tobytes())),
                       20, step if upward else BRIEF_PAGE[1] - 20 - step,
                       width=array.shape[1], height=array.shape[0])
    page.showPage()
    page.save()
    return written.getvalue()


def _mupdf_displayed_by_box(pdf):
    """The same displayed images put in the case's own order: sorted by the top of the bounding box,
    with CPython's `sorted` doing the sorting."""
    document = pymupdf.open(stream=pdf, filetype='pdf')
    placed = sorted(document[0].get_image_info(xrefs=True), key=lambda item: item['bbox'][1])
    return [_pdf_image(document.extract_image(item['xref'])['image']) for item in placed]


def _pdf_image(payload):
    return cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_UNCHANGED)


def _mupdf_referenced(pdf):
    """The images `Page.get_images` reports, in the order it reports them, extracted by xref."""
    document = pymupdf.open(stream=pdf, filetype='pdf')
    return [_pdf_image(document.extract_image(item[0])['image'])
            for item in document[0].get_images(full=True)]


def _mupdf_referenced_names(pdf):
    """The symbolic name of each of those, which is item[7] of the same tuple."""
    document = pymupdf.open(stream=pdf, filetype='pdf')
    return [item[7] for item in document[0].get_images(full=True)]


def _mupdf_displayed(pdf):
    """The images `Page.get_image_info(xrefs=True)` reports, in the order it reports them."""
    document = pymupdf.open(stream=pdf, filetype='pdf')
    return [_pdf_image(document.extract_image(item['xref'])['image'])
            for item in document[0].get_image_info(xrefs=True)]


def _mupdf_displayed_digests(pdf):
    """The MD5 hashcode the same call computes for each displayed image when asked for hashes."""
    document = pymupdf.open(stream=pdf, filetype='pdf')
    return [item['digest'] for item in document[0].get_image_info(hashes=True)]


def _pdfium_drawn(pdf):
    """The bitmap of every image object PDFium finds on the page, in the page's own object order."""
    page = pypdfium2.PdfDocument(io.BytesIO(pdf))[0]
    return [obj.get_bitmap().to_numpy() for obj in page.get_objects()
            if isinstance(obj, pypdfium2.PdfImage)]


def _pypdf_images(pdf):
    """The same page read by a pure-Python implementation of the PDF object model."""
    return [np.asarray(image.image) for image in pypdf.PdfReader(io.BytesIO(pdf)).pages[0].images]


@given(BRIEF_IMAGES)
@SLOW
def test_a_second_engine_reads_back_every_embedded_pixel_in_the_order_drawn(arrays):
    """handoff_guards_v14.py's case embedded_chart_images_keep_every_pixel types six comparisons about
    two charts placed in a brief. Nothing is typed here and the expected pixels are the generated input
    itself. PDFium, through pypdfium2 5.13.0 -- whose pyproject.toml at that tag declares no runtime
    dependencies at all, only build and optional groups -- walks the page's own object list, which
    `get_objects` documents at that tag as "Iterate through the pageobjects on this page", and each
    image object's bitmap read as an array (`to_numpy`, "Get a numpy array view of the bitmap") is
    exactly the array the strategy generated, in the order reportlab drew them. So the embedding loses
    no pixel and the page's object order is the drawing order. Replaces the typed `g.equal(placed,
    expected)`."""
    npt.assert_array_equal(_pdfium_drawn(_brief_pdf(arrays)), arrays)


@given(BRIEF_IMAGES)
@SLOW
def test_the_displayed_image_list_pairs_each_chart_with_its_source(arrays):
    """The case's own remedy, executed on generated input. PyMuPDF 1.28.2's `get_image_info` is
    documented in docs/page.rst at tag 1.28.2 as returning "a list of meta information dictionaries for
    all images displayed by the page", "for **exactly those** images, that are shown on the page", and
    with `xrefs=True` it will "Try to find the xref for each image". Extracted through those xrefs the
    images come back in the drawn order and pixel for pixel identical to what the strategy generated,
    which is the same answer PDFium gives. The case reached that pairing by sorting the bounding boxes
    of the same list; on a brief laid out down the page the list is already in that order, and the test
    below is what happens when it is not. Replaces the second half of `g.equal(placed, expected)`."""
    npt.assert_array_equal(_mupdf_displayed(_brief_pdf(arrays)), arrays)


@given(BRIEF_IMAGES)
@SLOW
def test_reversing_the_page_leaves_the_referenced_image_list_unchanged(arrays):
    """The finding, put where no ordering has to be assumed. Drawing the same generated charts in the
    reverse order changes the page: PDFium's object list comes back reversed. It does not change
    `get_images` at all -- the same images in the same order for both pages -- so that list carries no
    information about which chart is where, and for one of any two orderings a chain that pairs charts
    with captions by it is wrong. PyMuPDF's own documentation says so before the fact: `get_page_images`
    at tag 1.28.2 warns "In general, this is not the list of images that are **actually displayed**.
    This method only parses several PDF objects to collect references to embedded images. It does not
    analyse the page's contents, where all the actual image display commands are defined." Replaces
    `g.equal(resource == expected, False)` and the sorted-multiset comparison beside it."""
    assume(len({array.tobytes() for array in arrays}) == len(arrays))
    forward, backward = _brief_pdf(arrays), _brief_pdf(arrays[::-1])
    npt.assert_array_equal(_mupdf_referenced(forward), _mupdf_referenced(backward))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_pdfium_drawn(forward), _pdfium_drawn(backward))


@given(BRIEF_IMAGES)
@SLOW
def test_a_second_reader_of_the_object_model_returns_the_same_referenced_order(arrays):
    """The mispairing is in the file rather than in one library. pypdf 6.17.0 is pure Python -- its
    pyproject.toml at that tag declares typing_extensions below 3.11 and nothing else at run time, with
    Pillow only in the optional `image` extra -- and its `images` property, "Read-only property
    emulating a list of images on a page", is built by `_get_ids_image`, which walks the page's
    resources under the comment "# Iterate through all XObject resources". It returns the same images in
    the same order as MuPDF's list, so both libraries report the resource dictionary and neither reports
    the page."""
    pdf = _brief_pdf(arrays)
    npt.assert_array_equal(_pypdf_images(pdf), _mupdf_referenced(pdf))


@given(BRIEF_IMAGES)
@SLOW
def test_the_referenced_order_is_the_sorted_order_of_the_digests_of_the_pixels(arrays):
    """What the order is instead. reportlab 5.0.1's `drawImage`, in src/reportlab/pdfgen/canvas.py of
    the sdist published for that version, begins "# first, generate a unique name/signature for the
    image. If ANYTHING is different, even the mask, this should be different." and sets
    `name = _digester(rawdata+mdata)`, which src/reportlab/lib/utils.py defines as an md5 hexdigest.
    The names MuPDF reports come back in exactly the order CPython's `sorted` puts them in, so which
    chart is first in the referenced list is decided by an md5 digest of its own pixels: change one
    pixel of one chart and the pairing a chain makes from that list can swap."""
    names = _mupdf_referenced_names(_brief_pdf(arrays))
    npt.assert_array_equal(names, sorted(names))


@given(BRIEF_IMAGES)
@SLOW
def test_the_same_chart_twice_is_one_referenced_image_and_two_displayed(arrays):
    """A count taken from the referenced list is not a count of the charts on the page. Drawing every
    generated chart twice leaves as many entries in `get_images` as there are distinct charts and twice
    as many in `get_image_info`, and PDFium draws all of them; the two halves have equal MD5 hashcodes,
    which is the duplicate detection `get_image_info` documents as "Multiple occurrences of the same
    image are always reported. You can detect duplicates by comparing their `digest` values." reportlab
    documents its half too: drawImage "creates 'external images' which are only stored once in the PDF
    file but can be drawn many times", and with an ImageReader "it tests whether the image content has
    changed before deciding whether to reuse it". Replaces the typed `g.equal(len(resource), 2)`."""
    assume(len({array.tobytes() for array in arrays}) == len(arrays))
    pdf = _brief_pdf(list(arrays) + list(arrays))
    npt.assert_array_equal(len(_mupdf_referenced(pdf)), len(arrays))
    npt.assert_array_equal(len(_mupdf_displayed(pdf)), 2 * len(arrays))
    npt.assert_array_equal(_pdfium_drawn(pdf), list(arrays) + list(arrays))
    digests = _mupdf_displayed_digests(pdf)
    npt.assert_array_equal(digests[:len(arrays)], digests[len(arrays):])


@given(BRIEF_IMAGES)
@SLOW
def test_the_displayed_list_follows_the_content_stream_and_not_the_page(arrays):
    """The case's remedy is not the same operation as the library call it is built on, and the brief it
    was tested on hides the difference. Drawn from the foot of the page up, the displayed list still
    comes back in the order the charts were drawn -- the same order PDFium reports and pixel for pixel
    the generated input -- while sorting that list by the top of the bounding box, which is what the
    case does to pair charts with sources, returns them reversed. So `get_image_info` reports the
    content stream and the case reports the geometry, and the two agree only for a page whose drawing
    order runs down it. Nothing about a PDF requires that."""
    pdf = _brief_pdf(arrays, upward=True)
    npt.assert_array_equal(_mupdf_displayed(pdf), arrays)
    npt.assert_array_equal(_pdfium_drawn(pdf), arrays)
    npt.assert_array_equal(_mupdf_displayed_by_box(pdf), arrays[::-1])


# ---------------------------------------------------------------- a checklist form and its choices
FORM_PAGE = (595, 842)
FORM_FIELD_NAME = st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=8)
FORM_CHOICE = st.text(alphabet='abcdefghijklmnopqrstuvwxyz_', min_size=1, max_size=12)
FORM_CHOICES = st.lists(FORM_CHOICE, min_size=2, max_size=5, unique=True)
FORM_NAMES = st.lists(FORM_FIELD_NAME, min_size=1, max_size=3, unique=True)


def _checklist_form(names, choices, value=None, repeat=1):
    """The chain's own writer: reportlab's AcroForm puts one combo box and one text field on the page for
    each action. `choice` is handed the option list and an initial value and nothing else here touches
    the file."""
    written = io.BytesIO()
    page = rl_canvas.Canvas(written, pagesize=FORM_PAGE)
    form = page.acroForm
    for index, name in enumerate(list(names) * repeat):
        top = 780 - index * 120
        form.choice(name='status_' + name, options=list(choices),
                    value=choices[0] if value is None else value,
                    x=40, y=top - 45, width=150, height=20)
        form.textfield(name='owner_' + name, value='', x=200, y=top - 45, width=150, height=20)
    page.showPage()
    page.save()
    return written.getvalue()


def _pypdf_fields(pdf):
    """Every interactive field pypdf finds. `get_fields` is documented at tag 6.17.0 as returning "A
    dictionary where each key is a field name, and each value is a `Field` object"."""
    return pypdf.PdfReader(io.BytesIO(pdf)).get_fields()


def _mupdf_widgets(pdf):
    """The same page's widgets through MuPDF, in the order that library reports them."""
    return list(pymupdf.open(stream=pdf, filetype='pdf')[0].widgets())


def _form_answered(pdf, name, value):
    """The value of the first widget of that name set by the other library, and the file written out
    again. Only `Widget.field_value` and `Widget.update` are used."""
    document = pymupdf.open(stream=pdf, filetype='pdf')
    for widget in document[0].widgets():
        if widget.field_name == name:
            widget.field_value = value
            widget.update()
            break
    return document.tobytes()


@given(FORM_NAMES, FORM_CHOICES)
@SLOW
def test_both_readers_report_the_field_names_and_the_declared_choices(names, choices):
    """handoff_guards_v14.py's case form_choices_match_the_declared_contract types the six field names of
    its two actions, the three status choices and the initial value. Here the names and the choices are
    generated and read back by two implementations that share nothing: pypdf 6.17.0 parses the object
    model in pure Python, and MuPDF through PyMuPDF 1.28.2 reports the same page as widgets, whose
    `choice_values` docs/widget.rst at tag 1.28.2 calls a "Python sequence of strings defining the valid
    choices of list boxes and combo boxes". Both return exactly the generated option list for every
    field, and pypdf's key set is exactly the names reportlab was given. Replaces the typed
    `g.equal(sorted(fields), [...])` and `g.equal(list(fields['status_0'].get('/Opt')), STATUS_CHOICES)`."""
    pdf = _checklist_form(names, choices)
    fields = _pypdf_fields(pdf)
    npt.assert_array_equal(sorted(fields),
                           sorted(['owner_' + name for name in names] + ['status_' + name for name in names]))
    widgets = {widget.field_name: widget for widget in _mupdf_widgets(pdf)}
    for name in names:
        npt.assert_array_equal(list(fields['status_' + name]['/Opt']), choices)
        npt.assert_array_equal(list(widgets['status_' + name].choice_values), choices)
        npt.assert_array_equal(fields['status_' + name]['/V'], choices[0])
        npt.assert_array_equal(widgets['status_' + name].field_value, choices[0])


@given(FORM_NAMES, FORM_CHOICES, FORM_CHOICE)
@SLOW
def test_the_writer_refuses_an_initial_value_outside_its_own_option_list(names, choices, intruder):
    """Where the contract is actually enforced. reportlab 5.0.1 checks the initial value against the
    options as it writes: `_textfield` in src/reportlab/pdfbase/acroform.py of the sdist published for
    that version raises `ValueError('%s value %r is not in option\\nvalues %r\\nor labels %r')`, and it
    does so for every generated value outside the generated list."""
    assume(intruder not in choices)
    with pytest.raises(ValueError):
        _checklist_form(names, choices, value=intruder)


@given(FORM_NAMES, FORM_CHOICES, FORM_CHOICE)
@SLOW
def test_a_value_outside_the_declared_choices_survives_in_the_file(names, choices, intruder):
    """And where it is not enforced. The check above lives in the writer and not in the artefact: the
    same value the writer refused can be put into the same field afterwards through MuPDF's
    `Widget.field_value`, and both readers then return it beside an option list that still excludes it.
    So a form whose choices were declared once carries no record that they were a constraint, and the
    declared list and the stored value can disagree in a file both libraries read without complaint."""
    assume(intruder not in choices)
    answered = _form_answered(_checklist_form(names, choices), 'status_' + names[0], intruder)
    fields = _pypdf_fields(answered)
    widgets = {widget.field_name: widget for widget in _mupdf_widgets(answered)}
    npt.assert_array_equal(fields['status_' + names[0]]['/V'], intruder)
    npt.assert_array_equal(widgets['status_' + names[0]].field_value, intruder)
    npt.assert_array_equal(list(fields['status_' + names[0]]['/Opt']), choices)


@given(FORM_NAMES, FORM_CHOICES, FORM_CHOICE)
@SLOW
def test_the_declared_contract_holds_only_in_the_validator(names, choices, intruder):
    """The case reads the same field into a pydantic model whose status is a `Literal` of the three
    declared choices, and the model is where the contract is. Built dynamically over the generated
    options -- `create_model` is documented at v2.13.5 as a function that "dynamically creates a subclass
    of `BaseModel`" -- it accepts the value the form was written with and rejects the one the file
    happily returned, so the two halves of the chain disagree about the same file and only the second
    half says so. Replaces `g.rejects(ValidationError, ...)` for an undeclared status."""
    assume(intruder not in choices)
    answered = _form_answered(_checklist_form(names, choices), 'status_' + names[0], intruder)
    declared = pydantic.create_model('Progress', status=(Literal[tuple(choices)], ...))
    npt.assert_array_equal(declared.model_validate({'status': choices[0]}).status, choices[0])
    stored = _pypdf_fields(answered)['status_' + names[0]]['/V']
    with pytest.raises(pydantic.ValidationError):
        declared.model_validate({'status': stored})


@given(FORM_NAMES, FORM_CHOICES)
@SLOW
def test_two_fields_of_one_name_answer_differently_and_only_one_is_read(names, choices):
    """Field names are not required to be unique and nothing checks them: PyMuPDF documents `field_name`
    at tag 1.28.2 as "A mandatory string defining the field's name. No checking for duplicates takes
    place." Written twice under one name, the two widgets are two independent answers -- setting the
    first leaves the second at the value it was written with, which MuPDF reports -- while pypdf's
    dictionary keyed by name has one entry for both, and the value in it is the second widget's. So the
    answer recorded in the form is not the answer the read-back returns, and no error is raised on either
    side."""
    pdf = _checklist_form(names, choices, repeat=2)
    answered = _form_answered(pdf, 'status_' + names[0], choices[1])
    values = [widget.field_value for widget in _mupdf_widgets(answered)
              if widget.field_name == 'status_' + names[0]]
    npt.assert_array_equal(values, [choices[1], choices[0]])
    fields = _pypdf_fields(answered)
    npt.assert_array_equal(sorted(fields),
                           sorted(['owner_' + name for name in names] + ['status_' + name for name in names]))
    npt.assert_array_equal(fields['status_' + names[0]]['/V'], values[-1])
    with pytest.raises(AssertionError):
        npt.assert_array_equal(fields['status_' + names[0]]['/V'], choices[1])


# ---------------------------------------------------------------- a month grid and where a day sits in it
WEEK_GRID_ORACLE_JAVA = pathlib.Path(__file__).with_name('week_grid_oracle.java')
WEEK_GRID_ORACLE_PHP = pathlib.Path(__file__).with_name('week_grid_oracle.php')
java_available = shutil.which('java') is not None
intl_available = shutil.which('php') is not None and subprocess.run(
    ['php', '-r', 'echo class_exists("IntlCalendar") ? "yes" : "no";'],
    capture_output=True, encoding='utf-8').stdout == 'yes'
GRID_YEAR = st.integers(min_value=1900, max_value=2400)
GRID_MONTH = st.integers(min_value=1, max_value=12)
GRID_FIRST_WEEKDAY = st.integers(min_value=calendar.MONDAY, max_value=calendar.SUNDAY)
TWO_DECLARED_STARTS = st.lists(GRID_FIRST_WEEKDAY, min_size=2, max_size=2, unique=True)
GRID_BEFORE_THE_CUTOVER = st.integers(min_value=1501, max_value=1581)
FIRST_WEEK_HOLDS_THE_WHOLE_MONTH = 1


def _cpython_cells(year, month, first_weekday):
    """Where CPython's calendar puts every day of one month, read off the matrix itself: the row and the
    column of each day in order, both counted from one. `monthdayscalendar` is documented at v3.11.15 as
    returning "a matrix representing a month's calendar. Each row represents a week; days outside this
    month are zero", so the days of the month are exactly its non-zero entries."""
    grid = calendar.Calendar(firstweekday=first_weekday).monthdayscalendar(year, month)
    placed = {day: (row + 1, column + 1)
              for row, week in enumerate(grid) for column, day in enumerate(week) if day}
    return [placed[day] for day in sorted(placed)]


def _first_week_length(year, month, first_weekday):
    """How many days of the month fall in the matrix's first row, read off that row."""
    return len([day for day in
                calendar.Calendar(firstweekday=first_weekday).monthdayscalendar(year, month)[0] if day])


def _oracle_cells(runtime, shim, months):
    """The same months laid out by an independent runtime. The shim parses argv, calls the library and
    prints one line per month: the length of the month, then one field per day carrying the week of the
    month and the day of the week. Nothing here but subprocess and split."""
    arguments = [str(value) for month in months for value in month]
    completed = subprocess.run([runtime, str(shim)] + arguments,
                               capture_output=True, encoding='utf-8', check=True)
    lines = completed.stdout.split('\n')[:-1]
    return [(int(line.split('\t')[0]),
             [tuple(int(part) for part in field.split(',')) for field in line.split('\t')[1:]])
            for line in lines]


@pytest.mark.skipif(not (java_available and intl_available),
                    reason='java and php with the intl extension are required for these oracles')
@given(GRID_YEAR, GRID_MONTH, GRID_FIRST_WEEKDAY)
@JAVA_ORACLE
def test_two_runtimes_put_every_day_in_the_row_cpython_does_and_java_in_the_column(year, month,
                                                                                  first_weekday):
    """handoff_guards_v12.py's case the_month_grid_needs_a_declared_week_start types the first row of
    January 2024 twice, once for each of two week starts. Here the month and the week start are
    generated and the layout is checked against two implementations that share nothing with CPython's
    calendar module: java.time.temporal.WeekFields under OpenJDK 21.0.10, whose class documentation at
    tag jdk-21.0.10-ga says a week is defined by "The first day-of-week" and "The minimal number of days
    in the first week", and ICU 74.2's calendar through PHP's intl extension. With the minimum set to
    one day, so that the first week is simply the week holding the first of the month, both runtimes
    report the same number of days and put every one of them in the row CPython does. Java's
    `dayOfWeek()`, documented as numbering the days "from 1 to 7 where the getFirstDayOfWeek() first
    day-of-week is assigned the value 1", is also the column CPython's matrix uses."""
    months = [(year, month, first_weekday, FIRST_WEEK_HOLDS_THE_WHOLE_MONTH)]
    cells = _cpython_cells(year, month, first_weekday)
    (java_length, java_cells), = _oracle_cells('java', WEEK_GRID_ORACLE_JAVA, months)
    (icu_length, icu_cells), = _oracle_cells('php', WEEK_GRID_ORACLE_PHP, months)
    npt.assert_array_equal([java_length, icu_length], [len(cells), len(cells)])
    npt.assert_array_equal([row for row, column in java_cells], [row for row, column in cells])
    npt.assert_array_equal([row for row, column in icu_cells], [row for row, column in cells])
    npt.assert_array_equal([column for row, column in java_cells],
                           [column for row, column in cells])


@pytest.mark.skipif(not intl_available, reason='php with the intl extension is required for this oracle')
@given(GRID_YEAR, GRID_MONTH)
@ORACLE_PROCESS
def test_icu_numbers_the_weekday_from_sunday_and_so_matches_the_column_only_then(year, month):
    """The two libraries do not mean the same thing by a day of the week. ICU's field is absolute -- its
    `EDaysOfWeek` enum in icu4c/source/i18n/unicode/calendar.h at tag release-74-2 sets `SUNDAY = 1` --
    while the column of CPython's matrix counts from whichever weekday was declared. When the declared
    start is Sunday the two numberings coincide, and every day of every generated month lands on the
    same number in both."""
    cells = _cpython_cells(year, month, calendar.SUNDAY)
    (icu_length, icu_cells), = _oracle_cells(
        'php', WEEK_GRID_ORACLE_PHP,
        [(year, month, calendar.SUNDAY, FIRST_WEEK_HOLDS_THE_WHOLE_MONTH)])
    npt.assert_array_equal(icu_length, len(cells))
    npt.assert_array_equal([weekday for row, weekday in icu_cells],
                           [column for row, column in cells])


@pytest.mark.skipif(not intl_available, reason='php with the intl extension is required for this oracle')
@given(GRID_YEAR, GRID_MONTH,
       st.integers(min_value=calendar.MONDAY, max_value=calendar.SATURDAY))
@ORACLE_PROCESS
def test_icus_weekday_disagrees_with_the_column_for_every_other_declared_start(year, month,
                                                                              first_weekday):
    """And for the other six starts they never coincide, on any day of any generated month, because the
    whole column is shifted by the distance between Sunday and the declared start: not one day of any
    generated month is given the same number by both. So a grid position read out of one library and a
    weekday read out of the other are not the same quantity, and the row they agree about is the only
    part of the position that travels."""
    cells = _cpython_cells(year, month, first_weekday)
    (icu_length, icu_cells), = _oracle_cells(
        'php', WEEK_GRID_ORACLE_PHP,
        [(year, month, first_weekday, FIRST_WEEK_HOLDS_THE_WHOLE_MONTH)])
    npt.assert_array_equal(icu_length, len(cells))
    npt.assert_array_less(0, np.abs(np.array([weekday for row, weekday in icu_cells])
                                    - np.array([column for row, column in cells])))


@st.composite
def _a_month_whose_first_week_meets_the_minimum(draw):
    """A month, a declared week start, and a minimum drawn from one up to the number of days the matrix
    itself puts in its first row, so the region where the three implementations agree is generated
    rather than filtered for."""
    year, month = draw(GRID_YEAR), draw(GRID_MONTH)
    first_weekday = draw(GRID_FIRST_WEEKDAY)
    length = _first_week_length(year, month, first_weekday)
    return year, month, first_weekday, draw(st.integers(min_value=1, max_value=length))


@st.composite
def _a_month_whose_first_week_misses_the_minimum(draw):
    """The same, with the minimum drawn above that number instead. A first row of seven days meets every
    minimum, so those months cannot enter this region and the row length is drawn short of seven."""
    year, month = draw(GRID_YEAR), draw(GRID_MONTH)
    first_weekday = draw(GRID_FIRST_WEEKDAY)
    length = _first_week_length(year, month, first_weekday)
    assume(length < 7)
    return year, month, first_weekday, draw(st.integers(min_value=length + 1, max_value=7))


@pytest.mark.skipif(not (java_available and intl_available),
                    reason='java and php with the intl extension are required for these oracles')
@given(_a_month_whose_first_week_meets_the_minimum())
@JAVA_ORACLE
def test_the_rows_agree_while_the_first_week_meets_the_declared_minimum(month):
    """Both oracles carry a second setting CPython's calendar has no equivalent for: how many days the
    first week must hold before it counts as the first week. Java's factory documentation at
    jdk-21.0.10-ga says the minimum "defines how many days must be present in a month or year, starting
    from the first day-of-week, before the week is counted as the first week", and ICU's
    `setMinimalDaysInFirstWeek` at release-74-2 says to "call the method with value 1" if "the first
    week is defined as one that contains the first day of the first month of a year". While the first
    row of CPython's matrix is long enough to meet the generated minimum, both runtimes number the rows
    exactly as that matrix does."""
    year, month_of_year, first_weekday, minimum = month
    rows = [row for row, column in _cpython_cells(year, month_of_year, first_weekday)]
    months = [(year, month_of_year, first_weekday, minimum)]
    (java_length, java_cells), = _oracle_cells('java', WEEK_GRID_ORACLE_JAVA, months)
    (icu_length, icu_cells), = _oracle_cells('php', WEEK_GRID_ORACLE_PHP, months)
    npt.assert_array_equal([java_length, icu_length], [len(rows), len(rows)])
    npt.assert_array_equal([row for row, column in java_cells], rows)
    npt.assert_array_equal([row for row, column in icu_cells], rows)


@pytest.mark.skipif(not (java_available and intl_available),
                    reason='java and php with the intl extension are required for these oracles')
@given(_a_month_whose_first_week_misses_the_minimum())
@JAVA_ORACLE
def test_a_minimum_the_first_week_misses_renumbers_every_row_of_the_month(month):
    """And where the first row is shorter than the generated minimum, both runtimes renumber the whole
    month and CPython cannot follow, because it has no such setting to declare: Java's `weekOfMonth()`
    documentation says "If the first week starts after the start of the month then the period before is
    week zero (0)", and ICU does the same. The two oracles still agree with each other exactly, so the
    disagreement is not between them but between a grid that carries the rule and a matrix that has no
    place to record it. `WeekFields.ISO`, declared at that tag as `WeekFields.of(DayOfWeek.MONDAY, 4)`,
    is inside this region for every month whose first Monday-week is shorter than four days."""
    year, month_of_year, first_weekday, minimum = month
    rows = [row for row, column in _cpython_cells(year, month_of_year, first_weekday)]
    months = [(year, month_of_year, first_weekday, minimum)]
    (java_length, java_cells), = _oracle_cells('java', WEEK_GRID_ORACLE_JAVA, months)
    (icu_length, icu_cells), = _oracle_cells('php', WEEK_GRID_ORACLE_PHP, months)
    npt.assert_array_equal([java_length, icu_length], [len(rows), len(rows)])
    npt.assert_array_equal([row for row, column in java_cells],
                           [row for row, column in icu_cells])
    with pytest.raises(AssertionError):
        npt.assert_array_equal([row for row, column in java_cells], rows)


@pytest.mark.skipif(not (java_available and intl_available),
                    reason='java and php with the intl extension are required for these oracles')
@given(GRID_BEFORE_THE_CUTOVER, GRID_MONTH, GRID_FIRST_WEEKDAY)
@JAVA_ORACLE
def test_icu_reads_a_month_before_1582_from_the_julian_calendar_and_java_does_not(year, month,
                                                                                 first_weekday):
    """The grid also depends on something neither the week start nor the minimum can express. CPython's
    calendar and java.time are both proleptic Gregorian and place every day of these months identically,
    row and column alike. ICU's Gregorian calendar reverts to the Julian calendar before its default
    cutover of 15 October 1582, so for every generated month of the eighty years before that date it
    reports the same number of days in a different arrangement: the weekday of the first of the month
    differs by however far the two calendars had drifted apart by then, and every row moves with it. Its
    own header at release-74-2 states the cutover -- "Default is 00:00:00 local time, October 15, 1582.
    Previous to this time and date will be Julian dates." """
    months = [(year, month, first_weekday, FIRST_WEEK_HOLDS_THE_WHOLE_MONTH)]
    cells = _cpython_cells(year, month, first_weekday)
    (java_length, java_cells), = _oracle_cells('java', WEEK_GRID_ORACLE_JAVA, months)
    (icu_length, icu_cells), = _oracle_cells('php', WEEK_GRID_ORACLE_PHP, months)
    npt.assert_array_equal([java_length, icu_length], [len(cells), len(cells)])
    npt.assert_array_equal(java_cells, cells)
    with pytest.raises(AssertionError):
        npt.assert_array_equal([row for row, column in icu_cells],
                               [row for row, column in cells])


@given(GRID_YEAR, GRID_MONTH, TWO_DECLARED_STARTS)
@SLOW
def test_the_declared_start_moves_the_rows_but_never_the_days_of_the_month(year, month, starts):
    """The case types both grids to show that the same month lays out differently, and then that the
    days themselves are the same. Both halves are invariants of the output rather than values anyone
    needs to know, and hold for any two distinct generated week starts: the non-zero entries of the two
    matrices are one list, that list is every day of the month once and in order -- an invariant read
    off the output's own length -- and the two placements are not the same placement. Nothing is typed
    and no oracle is needed for any of the three."""
    first_weekday, other = starts
    grid = calendar.Calendar(firstweekday=first_weekday).monthdayscalendar(year, month)
    alternative = calendar.Calendar(firstweekday=other).monthdayscalendar(year, month)
    days = sorted(day for week in grid for day in week if day)
    npt.assert_array_equal(days, sorted(day for week in alternative for day in week if day))
    npt.assert_array_equal(days, list(range(1, len(days) + 1)))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_cpython_cells(year, month, first_weekday),
                               _cpython_cells(year, month, other))


@given(GRID_YEAR, GRID_MONTH, TWO_DECLARED_STARTS)
@SLOW
def test_the_module_grid_reads_process_state_that_the_object_grid_declares(year, month, starts):
    """What the case calls process-global state, executed. At v3.11.15 the calendar module ends with
    `c = TextCalendar()` and binds `monthcalendar = c.monthdayscalendar` and `firstweekday =
    c.getfirstweekday`, so the module-level grid is one shared object's grid and `setfirstweekday`
    rebinds it for every caller in the process. Whatever generated start is set, the module function
    returns the matrix an object built with that start returns, and it stops agreeing with an object
    built with any other. Neither oracle has an equivalent: Java's `WeekFields` and ICU's calendar carry
    the start on the instance, so there is nothing a distant import could change under them."""
    first_weekday, other = starts
    was = calendar.firstweekday()
    try:
        calendar.setfirstweekday(first_weekday)
        npt.assert_array_equal(calendar.firstweekday(), first_weekday)
        npt.assert_array_equal(calendar.monthcalendar(year, month),
                               calendar.Calendar(firstweekday=first_weekday)
                               .monthdayscalendar(year, month))
        with pytest.raises(AssertionError):
            npt.assert_array_equal(calendar.monthcalendar(year, month),
                                   calendar.Calendar(firstweekday=other)
                                   .monthdayscalendar(year, month))
    finally:
        calendar.setfirstweekday(was)


# ---------------------------------------------------------------- an index, a query language and a rank
FTS_SCHEMA = "CREATE VIRTUAL TABLE docs USING fts5(document, block_id, body, tokenize='unicode61')"
FTS_WORD = st.text(alphabet='abcdefgh', min_size=3, max_size=6)
FTS_BODY = st.lists(FTS_WORD, min_size=1, max_size=8)
FTS_BODIES = st.lists(FTS_BODY, min_size=2, max_size=6)
FTS_OPERATOR = st.sampled_from(('AND', 'OR', 'NOT'))
FTS_PHRASE = st.lists(FTS_WORD, min_size=2, max_size=3)
FILLER_LENGTHS = st.lists(st.integers(min_value=1, max_value=30), min_size=4, max_size=8, unique=True)


def _fts5_index(bodies):
    """The chain's own index: one FTS5 virtual table in memory, one row per block, declaring the same
    unicode61 tokenizer the case records."""
    connection = sqlite3.connect(':memory:')
    connection.execute(FTS_SCHEMA)
    connection.executemany('INSERT INTO docs(document, block_id, body) VALUES (?,?,?)',
                           [('d', 'b%d' % number, ' '.join(body)) for number, body in enumerate(bodies)])
    return connection


def _fts5_hits(connection, query):
    """The chain's own query, block by block: the identifier, the rank and the snippet, ordered as the
    case orders them."""
    return connection.execute(
        "SELECT block_id, bm25(docs), snippet(docs, 2, '[', ']', '...', 6) "
        'FROM docs WHERE docs MATCH ? ORDER BY bm25(docs)', (query,)).fetchall()


def _fts5_literal(text):
    """The escape the chain applies, which FTS5's own documented phrase syntax asks for: the phrase in
    double quotes with any embedded quote doubled."""
    return '"' + text.replace('"', '""') + '"'


def _tantivy_index(bodies):
    """The same blocks in tantivy 0.26.0, a Rust search engine whose Python wrapper declares no runtime
    dependencies at all and whose Cargo.toml at tag 0.26.0 names the tantivy crate and no SQLite, so
    nothing of FTS5 is beneath it."""
    builder = tantivy.SchemaBuilder()
    for field in ('document', 'block_id', 'body'):
        builder.add_text_field(field, stored=True)
    index = tantivy.Index(builder.build())
    writer = index.writer()
    for number, body in enumerate(bodies):
        writer.add_document(tantivy.Document(document=['d'], block_id=['b%d' % number],
                                             body=[' '.join(body)]))
    writer.commit()
    index.reload()
    return index


def _tantivy_hits(index, query):
    """The same query through tantivy's own parser and searcher, best first as that library orders it."""
    searcher = index.searcher()
    parsed = index.parse_query(query, ['body'])
    return [(searcher.doc(address)['block_id'][0], score)
            for score, address in searcher.search(parsed, 50).hits]


@given(FTS_BODIES, FTS_OPERATOR)
@SLOW
def test_both_engines_refuse_a_bare_boolean_operator(bodies, operator):
    """handoff_guards_v13.py's case a_literal_query_must_be_quoted types seven expectations about a
    search over three typed blocks. The first reproduces in a second engine that shares nothing with the
    first: for every generated corpus, a bare AND, OR or NOT is a syntax error to SQLite's FTS5 parser
    and to tantivy's, so a phrase a reader typed is refused by both rather than searched for. The
    operator names are the query language's own, not values anybody expects back."""
    with pytest.raises(sqlite3.OperationalError):
        _fts5_hits(_fts5_index(bodies), operator)
    with pytest.raises(ValueError):
        _tantivy_index(bodies).parse_query(operator, ['body'])


@given(FTS_BODIES, FTS_WORD, FTS_WORD)
@SLOW
def test_the_hyphen_fts5_reads_as_a_column_filter_is_an_ordinary_term_to_tantivy(bodies, left, right):
    """The second expectation does not travel. FTS5's grammar in ext/fts5/fts5parse.y at tag
    version-3.45.1 has the rule `colset(A) ::= MINUS STRING(X).`, so a minus sign followed by a bareword
    is a column set, and `sqlite3Fts5ParseError(pParse, "no such column: %s", z)` in fts5_expr.c is what
    a reader gets for a hyphenated term. tantivy parses the same string without complaint and returns
    the block that holds it. So the escaping the chain performs is not a general precaution against
    hyphens; it is one engine's grammar, and the same unescaped query is a search in the other."""
    hyphenated = left + '-' + right
    bodies = [body for body in bodies if not {left, right} & set(body)] + [[hyphenated]]
    with pytest.raises(sqlite3.OperationalError):
        _fts5_hits(_fts5_index(bodies), hyphenated)
    npt.assert_array_equal([block for block, score in
                            _tantivy_hits(_tantivy_index(bodies), hyphenated)],
                           ['b%d' % (len(bodies) - 1)])


@given(FTS_BODIES, FTS_WORD, FTS_WORD)
@SLOW
def test_quoting_makes_both_engines_read_a_hyphenated_term_literally(bodies, left, right):
    """Quoted, the two engines agree again. The generated hyphenated term is placed in a block of its
    own and quoted for each engine, and both return that block and no other, so the case's third and
    fourth expectations hold in a second implementation."""
    hyphenated = left + '-' + right
    bodies = [body for body in bodies if not {left, right} & set(body)] + [[hyphenated]]
    wanted = 'b%d' % (len(bodies) - 1)
    quoted = _fts5_literal(hyphenated)
    npt.assert_array_equal([block for block, rank, snippet in _fts5_hits(_fts5_index(bodies), quoted)],
                           [wanted])
    npt.assert_array_equal([block for block, score in _tantivy_hits(_tantivy_index(bodies), quoted)],
                           [wanted])


@given(FTS_BODIES, FTS_PHRASE)
@SLOW
def test_the_escape_fts5_needs_for_an_embedded_quote_is_a_syntax_error_to_tantivy(bodies, phrase):
    """The case's sixth expectation types the escape itself, that an embedded quote is doubled rather
    than dropped. Executed against a second engine it is worse than untypeable: the string the chain
    hands FTS5 for a phrase carrying a quote is parsed by FTS5, matches the block, and is a syntax error
    to tantivy, whose parser does not read a doubled quote as an escape at all. So `literal_query` does not
    make a query literal, it makes it literal to one engine, and the same call that protects a reader
    from FTS5's grammar hands another engine something it will not parse at all."""
    quoted_text = '"'.join(phrase)
    bodies = [body for body in bodies if not set(phrase) & set(body)] + [[quoted_text]]
    query = _fts5_literal(quoted_text)
    npt.assert_array_equal([block for block, rank, snippet in _fts5_hits(_fts5_index(bodies), query)],
                           ['b%d' % (len(bodies) - 1)])
    with pytest.raises(ValueError):
        _tantivy_index(bodies).parse_query(query, ['body'])


@given(FILLER_LENGTHS, FTS_WORD)
@SLOW
def test_the_two_engines_order_the_hits_alike_and_sign_the_ranks_oppositely(lengths, term):
    """The case records only that every rank is a float. What a rank is differs between the engines by
    exactly a sign: `sqlite3_result_double(pCtx, -1.0 * score)` is the last line of fts5Bm25Function in
    ext/fts5/fts5_aux.c at version-3.45.1, so every FTS5 rank is negative and `ORDER BY bm25(docs)`
    ascending is best-first, while every tantivy score is positive and its searcher returns best first.
    Over generated corpora holding the term in documents of distinct lengths the two orders are the same
    order, so the ranking agrees and only the convention differs -- which is what makes the chain's
    `ORDER BY` correct here and backwards against any engine that scores upward."""
    bodies = [[term] + ['f%d' % position for position in range(length)] for length in lengths]
    ranked = _fts5_hits(_fts5_index(bodies), _fts5_literal(term))
    scored = _tantivy_hits(_tantivy_index(bodies), _fts5_literal(term))
    npt.assert_array_equal([block for block, rank, snippet in ranked],
                           [block for block, score in scored])
    npt.assert_array_less([rank for block, rank, snippet in ranked], 0.0)
    npt.assert_array_less(0.0, [score for block, score in scored])


@given(FILLER_LENGTHS, FTS_WORD)
@SLOW
def test_rounding_the_rank_to_six_places_merges_hits_that_both_engines_separate(lengths, term):
    """And the rank the chain records is not the rank the engine computed. FTS5's bm25 in that same file
    carries the comment that "The problem with this is that if (N < 2*nHit), the IDF is negative. Which
    is undesirable. So the mimimum allowable IDF is (1e-6) - roughly the same as a term that appears in
    just over half of set of 5,000,000 documents", and the line beneath it is `if( idf<=0.0 ) idf =
    1e-6;`. For a term in every document of a small corpus that floor is what is used, so the ranks come
    back around a millionth apart and `round(r[3], 6)`, which is how the case records them, merges hits
    the engine had separated. tantivy's idf in src/query/bm25.rs at tag 0.26.0 is `(1.0 + x).ln()` with
    no floor, so its scores stay apart through the same rounding: the collapse is the recording, not the
    ranking."""
    bodies = [[term] + ['f%d' % position for position in range(length)] for length in lengths]
    ranks = [rank for block, rank, snippet in _fts5_hits(_fts5_index(bodies), _fts5_literal(term))]
    scores = [score for block, score in _tantivy_hits(_tantivy_index(bodies), _fts5_literal(term))]
    npt.assert_array_less(len(set(round(rank, 6) for rank in ranks)), len(set(ranks)))
    npt.assert_array_equal(len(set(round(score, 6) for score in scores)), len(set(scores)))


@given(FTS_BODIES, FTS_PHRASE)
@SLOW
def test_the_snippet_marks_the_whole_phrase_where_tantivy_marks_each_word_of_it(bodies, phrase):
    """The case's remaining expectation is that the snippet marks the matched span in the source text.
    It does, and the span it marks is the phrase: the text between the two markers FTS5 was handed is
    exactly the generated phrase, so nothing about it needs typing. tantivy highlights the same match
    word by word instead -- its snippet returns one bold run per term -- so "the matched span" is not one
    thing across engines, and a reader shown a highlighted result learns which words matched from one
    and which phrase matched from the other."""
    bodies = [body for body in bodies if not set(phrase) & set(body)] + [list(phrase)]
    query = _fts5_literal(' '.join(phrase))
    (block, rank, snippet), = _fts5_hits(_fts5_index(bodies), query)
    npt.assert_array_equal(snippet.split('[')[1].split(']')[0], ' '.join(phrase))
    index = _tantivy_index(bodies)
    searcher = index.searcher()
    parsed = index.parse_query(query, ['body'])
    generator = tantivy.SnippetGenerator.create(searcher, parsed, index.schema, 'body')
    score, address = searcher.search(parsed, 5).hits[0]
    marked = generator.snippet_from_doc(searcher.doc(address)).to_html()
    npt.assert_array_equal([run.split('</b>')[0] for run in marked.split('<b>')[1:]], list(phrase))


# ---------------------------------------------------------------- a slide placed in a box on a handout
RENDER = settings(max_examples=25, deadline=None)
RENDER_SCALE = 2
HANDOUT_PAGE = (595, 842)
SLIDE_WIDE = st.integers(min_value=400, max_value=800)
SLIDE_TALL = st.integers(min_value=200, max_value=350)
BOX_EDGE = st.integers(min_value=10, max_value=50)
BOX_WIDE = st.integers(min_value=200, max_value=350)
BOX_TALL = st.integers(min_value=400, max_value=700)


def _inked_slide(width, height):
    """A source page of the generated size with every point of it inked, so that what a reader measures
    on the handout is the placed page itself and not the text that happens to be on it."""
    written = io.BytesIO()
    page = rl_canvas.Canvas(written, pagesize=(width, height))
    page.setFillGray(0)
    page.rect(0, 0, width, height, stroke=0, fill=1)
    page.showPage()
    page.save()
    return written.getvalue()


def _shown_on_a_handout(slide, box, **options):
    """The chain's own placement: one handout page, one call to show_pdf_page with the generated
    rectangle. Any option named here is passed straight to that call."""
    handout = pymupdf.open()
    page = handout.new_page(width=HANDOUT_PAGE[0], height=HANDOUT_PAGE[1])
    with pymupdf.open(stream=slide, filetype='pdf') as source:
        page.show_pdf_page(box, source, 0, **options)
    return handout.tobytes()


def _mupdf_ink(pdf):
    """The bounding box of everything drawn on the page, from MuPDF's own raster: the extreme rows and
    columns numpy finds below the mid grey."""
    pixmap = pymupdf.open(stream=pdf, filetype='pdf')[0].get_pixmap(dpi=72 * RENDER_SCALE)
    raster = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, pixmap.n)
    rows, columns = np.nonzero(raster[:, :, 0] < 128)
    return np.array([columns.min(), rows.min(), columns.max(), rows.max()])


def _pdfium_ink(pdf):
    """The same bounding box from PDFium's raster, through pypdfium2, which declares no dependencies at
    all and shares no code with MuPDF."""
    raster = np.asarray(pypdfium2.PdfDocument(io.BytesIO(pdf))[0].render(scale=RENDER_SCALE)
                        .to_pil().convert('L'))
    rows, columns = np.nonzero(raster < 128)
    return np.array([columns.min(), rows.min(), columns.max(), rows.max()])


def _drawn_ratio(box):
    """The width-to-height ratio of a measured ink box."""
    return (box[2] - box[0]) / (box[3] - box[1])


@given(SLIDE_WIDE, SLIDE_TALL, BOX_EDGE, BOX_EDGE, BOX_WIDE, BOX_TALL)
@RENDER
def test_two_renderers_measure_the_same_drawing_on_the_handout(width, height, left, top,
                                                              box_width, box_height):
    """handoff_guards_v12.py's case show_pdf_page_does_not_preserve_aspect makes four typed comparisons
    and one typed requirement about slides placed on a handout, and the ones about the placement compare
    numbers the chain computed before the call rather than anything on the page. Before reading the page,
    the reading is checked itself: the
    bounding box of the ink, measured by MuPDF's raster and by PDFium's through pypdfium2, agrees to
    within one pixel of the generated placement, so nothing that follows is one library's artefact."""
    slide = _inked_slide(width, height)
    box = pymupdf.Rect(left, top, left + box_width, top + box_height)
    placed = _shown_on_a_handout(slide, box)
    npt.assert_allclose(_mupdf_ink(placed), _pdfium_ink(placed), atol=1)


@given(SLIDE_WIDE, SLIDE_TALL, BOX_EDGE, BOX_EDGE, BOX_WIDE, BOX_TALL)
@RENDER
def test_the_drawing_keeps_the_source_proportions_and_not_the_rectangles(width, height, left, top,
                                                                        box_width, box_height):
    """The case's first claim is that an unfitted placement stretches the slide, and it is not true of
    the page. `show_pdf_page` is documented at tag 1.28.2 with the signature `show_pdf_page(rect,
    docsrc, pno=0, keep_proportion=True, overlay=True, oc=0, rotate=0, clip=None)` and the parameter
    line "whether to maintain the width-height-ratio (default)", and the chain never passes that
    argument in either branch. Measured on the page, the drawing has the generated slide's ratio and
    not the generated rectangle's -- the source is always landscape here and the rectangle always
    portrait, so the two can never coincide -- and the case's own threshold of a tenth would have
    caught it had it measured the drawing instead of the rectangle it asked for."""
    slide = _inked_slide(width, height)
    box = pymupdf.Rect(left, top, left + box_width, top + box_height)
    drawn = _drawn_ratio(_mupdf_ink(_shown_on_a_handout(slide, box)))
    npt.assert_allclose(drawn, width / height, rtol=0.03)
    with pytest.raises(AssertionError):
        npt.assert_allclose(drawn, box_width / box_height, rtol=0.03)


@given(SLIDE_WIDE, SLIDE_TALL, BOX_EDGE, BOX_EDGE, BOX_WIDE, BOX_TALL)
@RENDER
def test_only_keep_proportion_false_stretches_the_drawing_to_the_rectangle(width, height, left, top,
                                                                          box_width, box_height):
    """The stretch the case describes is a real behaviour of the library, reached by the argument the
    chain does not pass: with `keep_proportion=False`, documented at that tag as "If false, all 4
    corners are always positioned on the border of the target rectangle -- whatever the rotation value.
    In general, this will deliver distorted and /or non-rectangular images", the ink fills the generated
    rectangle and takes its ratio instead of the slide's. So the two branches the case calls fitted and
    unfitted differ in the number it records and not in the option that decides this."""
    slide = _inked_slide(width, height)
    box = pymupdf.Rect(left, top, left + box_width, top + box_height)
    drawn = _drawn_ratio(_mupdf_ink(_shown_on_a_handout(slide, box, keep_proportion=False)))
    npt.assert_allclose(drawn, box_width / box_height, rtol=0.03)
    with pytest.raises(AssertionError):
        npt.assert_allclose(drawn, width / height, rtol=0.03)


@given(SLIDE_WIDE, SLIDE_TALL, BOX_EDGE, BOX_EDGE, BOX_WIDE, BOX_TALL, BOX_WIDE, BOX_TALL)
@RENDER
def test_the_drawn_proportions_do_not_depend_on_the_rectangle_they_were_given(width, height, left, top,
                                                                             box_width, box_height,
                                                                             other_width, other_height):
    """Which settles what the chain's own fitting is worth. Shown in two independently generated
    rectangles with the argument left alone, one slide is drawn at one ratio, its own, in both, so no
    rectangle handed to that call changes the proportions the slide appears at. A rectangle computed to
    carry the source ratio therefore cannot change them either, and the fitted and unfitted branches of
    the handout differ in the pair of numbers the case rounds and compares -- read off the rectangle
    before the call and never off the result -- and not in the shape of the slide on the page."""
    slide = _inked_slide(width, height)
    box = pymupdf.Rect(left, top, left + box_width, top + box_height)
    other = pymupdf.Rect(left, top, left + other_width, top + other_height)
    here = _drawn_ratio(_mupdf_ink(_shown_on_a_handout(slide, box)))
    there = _drawn_ratio(_mupdf_ink(_shown_on_a_handout(slide, other)))
    npt.assert_allclose([here, there], [width / height, width / height], rtol=0.03)


# --------------------------------------------------------------------------------------------------
# handoff_guards_v11.py, case binder_bookmarks_point_at_real_pages: the outline of an assembled binder
# --------------------------------------------------------------------------------------------------
BINDER_TITLE = st.text(alphabet=st.characters(min_codepoint=65, max_codepoint=90), min_size=3, max_size=7)
BINDER_TITLES = st.lists(BINDER_TITLE, min_size=1, max_size=5, unique=True)
BINDER_SECTIONS = st.lists(st.tuples(BINDER_TITLE, st.sampled_from([1, 2])), min_size=2, max_size=5,
                           unique_by=lambda pair: pair[0])
BINDER_AND_ANY_ROW = st.lists(BINDER_TITLE, min_size=2, max_size=5, unique=True).flatmap(
    lambda titles: st.tuples(st.just(titles), st.integers(min_value=0, max_value=len(titles) - 1)))
BINDER_AND_EARLIER_ROW = st.lists(BINDER_TITLE, min_size=2, max_size=5, unique=True).flatmap(
    lambda titles: st.tuples(st.just(titles), st.integers(min_value=0, max_value=len(titles) - 2)))
OVERSHOOT = st.integers(min_value=1, max_value=60)
BINDER_OUTLINE = settings(max_examples=50, deadline=None)


def _one_page(word):
    """One page carrying one generated word, written by PyMuPDF itself."""
    document = pymupdf.open()
    document.new_page().insert_text((72, 72), word)
    return document.tobytes()


def _sections(titles):
    """A binder assembled the way the case assembles one, with the case's own glue removed: one page a
    section, each section inserted by `Document.insert_pdf`."""
    binder = pymupdf.open()
    for title in titles:
        with pymupdf.open(stream=_one_page(title), filetype='pdf') as part:
            binder.insert_pdf(part)
    return binder


def _flat_outline(titles):
    """The outline the case writes: one level-1 entry a section, pointing at the page it went on.
    `set_toc` documents its item format at tag 1.28.2 as "[lvl, title, page [, dest]]" where "**page**
    (int) is the target page number **(attention: 1-based)**", so `enumerate` numbering from one is the
    page each single-page section occupies."""
    return [[1, title, number] for number, title in enumerate(titles, start=1)]


def _mupdf_outline(data):
    """PyMuPDF's own reading. docs/document.rst at tag 1.28.2 documents each `get_toc` entry as
    "*[lvl, title, page, dest]*" whose page is the "1-based source page number (*int*). `-1` if no
    destination or outside document"."""
    return pymupdf.open(stream=data, filetype='pdf').get_toc()


def _pypdf_outline(data):
    """The same outline through pypdf 6.17.0, a pure-Python reader of the PDF object model whose
    `outline` property is documented at tag 6.17.0 as "the outline present in the document (i.e., a
    collection of 'outline items' which are also known as 'bookmarks')" and whose
    `get_destination_page_number` returns "The page number or None if page is not found" -- an index
    counted from zero. Called only on flat outlines, where pypdf returns no nested lists."""
    reader = pypdf.PdfReader(io.BytesIO(data))
    return [(item.title, reader.get_destination_page_number(item)) for item in reader.outline]


def _pdfium_outline(data):
    """And through PDFium, whose `PdfDocument.get_toc` at tag 5.13.0 iterates "through the bookmarks in
    the document's table of contents (TOC)", each carrying a `level` that is "The bookmark's nesting
    level in the TOC tree (zero-based)" and a destination whose `get_index` is the "Zero-based index of
    the page the dest points to, or None on failure" -- PDFium's own negative sentinel, which the
    binding turns into None with `return val if val >= 0 else None`."""
    document = pypdfium2.PdfDocument(io.BytesIO(data))
    out = []
    for bookmark in document.get_toc():
        destination = bookmark.get_dest()
        out.append((bookmark.get_title(), bookmark.level,
                    None if destination is None else destination.get_index()))
    return out


def _mupdf_page_words(data, numbers):
    """The text of each page an outline entry points at, read by MuPDF. `get_toc` numbers pages from
    one and `Document.__getitem__` indexes them from zero, so the entry's number is the index one
    further on; `insert_text` wrote one line, and each extractor terminates that line its own way."""
    document = pymupdf.open(stream=data, filetype='pdf')
    return [document[number - 1].get_text().strip() for number in numbers]


def _pypdf_page_words(data, indices):
    reader = pypdf.PdfReader(io.BytesIO(data))
    return [reader.pages[index].extract_text().strip() for index in indices]


def _pdfium_page_words(data, indices):
    document = pypdfium2.PdfDocument(io.BytesIO(data))
    return [document[index].get_textpage().get_text_bounded().strip() for index in indices]


@given(BINDER_TITLES)
@BINDER_OUTLINE
def test_three_outline_readers_return_the_same_bookmark_titles_in_the_same_order(titles):
    """handoff_guards_v11.py's case binder_bookmarks_point_at_real_pages types the page count, the
    section count and the whole table of contents as a nested list. Nothing is typed here: the titles
    are generated and three implementations that share no code read them back. MuPDF through PyMuPDF
    1.28.2, pypdf 6.17.0 -- whose only declared dependency at that tag is typing_extensions below
    Python 3.11 -- and PDFium through pypdfium2 5.13.0, whose pyproject.toml at that tag declares no
    runtime dependency at all, agree on the titles and on their order."""
    data = _sections(titles).tobytes()
    with pymupdf.open(stream=data, filetype='pdf') as binder:
        binder.set_toc(_flat_outline(titles))
        data = binder.tobytes()
    npt.assert_array_equal([entry[1] for entry in _mupdf_outline(data)], titles)
    npt.assert_array_equal([title for title, _ in _pypdf_outline(data)], titles)
    npt.assert_array_equal([title for title, _, _ in _pdfium_outline(data)], titles)


@given(BINDER_TITLES)
@BINDER_OUTLINE
def test_every_bookmark_resolves_to_the_page_that_carries_its_own_section(titles):
    """The claim the case's name makes, executed rather than typed. Each generated title is written on
    its own page and is also the bookmark's title, so the text of the page each reader's destination
    resolves to is the title itself -- an invariant of the generated input, not an expected value. All
    three readers land on that page, so the destinations survive the write and are the same
    destinations under three independent resolutions of the PDF's own name tree."""
    data = _sections(titles).tobytes()
    with pymupdf.open(stream=data, filetype='pdf') as binder:
        binder.set_toc(_flat_outline(titles))
        data = binder.tobytes()
    npt.assert_array_equal(_mupdf_page_words(data, [entry[2] for entry in _mupdf_outline(data)]), titles)
    npt.assert_array_equal(_pypdf_page_words(data, [page for _, page in _pypdf_outline(data)]), titles)
    npt.assert_array_equal(_pdfium_page_words(data, [page for _, _, page in _pdfium_outline(data)]), titles)


@given(BINDER_SECTIONS)
@BINDER_OUTLINE
def test_a_nesting_level_survives_the_write_and_both_engines_report_the_same_one(sections):
    """The case's outline is flat and it types the flatness into the expected list. Generated here is a
    two-level outline: `set_toc` documents that the level "**must be 1** for the first item and at most
    1 larger than the previous one", so a first entry at level 1 followed by any sequence of ones and
    twos is a valid tree by construction and needs no filtering. MuPDF's levels count from one and
    PDFium's `level` is documented as the nesting level "(zero-based)" -- the same tree in two
    vocabularies."""
    titles = [title for title, _ in sections]
    levels = [1, *[level for _, level in sections[1:]]]
    with _sections(titles) as binder:
        binder.set_toc([[level, title, number]
                        for level, (number, title) in zip(levels, enumerate(titles, start=1))])
        data = binder.tobytes()
    npt.assert_array_equal([entry[0] for entry in _mupdf_outline(data)], levels)
    npt.assert_array_equal([level + 1 for _, level, _ in _pdfium_outline(data)], levels)


@given(BINDER_AND_ANY_ROW)
@BINDER_OUTLINE
def test_the_two_index_readers_agree_exactly_about_a_bookmark_whose_page_was_deleted(binder_and_row):
    """A binder is not finished when its outline is written. Delete any one of the generated pages
    afterwards with `Document.delete_page` and its bookmark stays in the outline with nothing behind
    it. pypdf, which returns "The page number or None if page is not found", and PDFium, whose index is
    "Zero-based index of the page the dest points to, or None on failure", report the same list for the
    edited binder, entry for entry, including which single entry has no destination left."""
    titles, dropped = binder_and_row
    with _sections(titles) as binder:
        binder.set_toc(_flat_outline(titles))
        binder.delete_page(dropped)
        data = binder.tobytes()
    npt.assert_array_equal(np.array([page for _, page in _pypdf_outline(data)], dtype=object),
                           np.array([page for _, _, page in _pdfium_outline(data)], dtype=object))


@given(BINDER_AND_ANY_ROW)
@BINDER_OUTLINE
def test_the_orphaned_bookmark_sits_below_the_first_page_rather_than_above_the_last(binder_and_row):
    """And this is what the case's own requirement is worth. It requires that `entry[2] <= out['pages']`
    for every entry, calling that "every bookmark points inside the binder". MuPDF reports the orphan's
    page as the value docs/document.rst at tag 1.28.2 documents for it -- "`-1` if no destination or
    outside document" -- which is below one, below the first page of any binder, and therefore below
    the page count as well. The one outline entry that points at nothing satisfies the requirement more
    comfortably than the entries that point at real pages."""
    titles, dropped = binder_and_row
    with _sections(titles) as binder:
        binder.set_toc(_flat_outline(titles))
        binder.delete_page(dropped)
        data = binder.tobytes()
    with pymupdf.open(stream=data, filetype='pdf') as edited:
        npt.assert_array_less(_mupdf_outline(data)[dropped][2], 1)
        npt.assert_array_less(_mupdf_outline(data)[dropped][2], edited.page_count)


@given(BINDER_AND_EARLIER_ROW, OVERSHOOT)
@BINDER_OUTLINE
def test_set_toc_refuses_a_page_number_past_the_end_in_any_row_but_the_last(binder_and_row, overshoot):
    """`set_toc` documents that the page "Must be in valid range if positive", and for every row it
    checks, it enforces exactly that: a generated overshoot in any row before the last is refused."""
    titles, row = binder_and_row
    outline = _flat_outline(titles)
    outline[row][2] = len(titles) + overshoot
    with _sections(titles) as binder, pytest.raises(ValueError):
        binder.set_toc(outline)


@given(BINDER_TITLES, OVERSHOOT)
@BINDER_OUTLINE
def test_the_last_row_escapes_that_check_and_its_destination_is_moved_onto_the_last_page(titles, overshoot):
    """The last row is never reached by it. The check in `set_toc` at 1.28.2 reads `for i in
    list(range(toclen - 1)):` and then tests `toc[i]`, so the final entry's page number is the one entry
    never validated, and a single-entry outline is never validated at all. The value is not rejected and
    not preserved either: written out, the destination has been moved onto a real page, and all three
    readers resolve it to the page carrying the last generated section. So the case's requirement that
    every bookmark point inside the binder cannot fail on a freshly written outline -- every row it
    could have caught was refused before it ran, and the one row that escapes was repaired before it
    ran."""
    outline = _flat_outline(titles)
    outline[-1][2] = len(titles) + overshoot
    with _sections(titles) as binder:
        binder.set_toc(outline)
        data = binder.tobytes()
    npt.assert_array_equal(_mupdf_page_words(data, [_mupdf_outline(data)[-1][2]]), titles[-1:])
    npt.assert_array_equal(_pypdf_page_words(data, [_pypdf_outline(data)[-1][1]]), titles[-1:])
    npt.assert_array_equal(_pdfium_page_words(data, [_pdfium_outline(data)[-1][2]]), titles[-1:])


@given(BINDER_TITLES, st.integers(max_value=-2))
@BINDER_OUTLINE
def test_a_last_destination_below_minus_one_is_written_out_as_no_destination_at_all(titles, page):
    """The other side of the same unchecked row. `set_toc` documents "-1 if there is no target, or the
    target is external"; a generated value below that is neither refused nor kept, and what reaches the
    file is the no-destination sentinel. MuPDF reports a number below one and the two index readers
    agree with each other, entry for entry, that the last bookmark resolves to nothing."""
    outline = _flat_outline(titles)
    outline[-1][2] = page
    with _sections(titles) as binder:
        binder.set_toc(outline)
        data = binder.tobytes()
    npt.assert_array_less(_mupdf_outline(data)[-1][2], 1)
    npt.assert_array_equal(np.array([page for _, page in _pypdf_outline(data)], dtype=object),
                           np.array([page for _, _, page in _pdfium_outline(data)], dtype=object))


@given(BINDER_TITLES, st.integers(min_value=2, max_value=8))
@BINDER_OUTLINE
def test_set_toc_does_enforce_the_hierarchy_rule_it_documents_for_the_first_entry(titles, level):
    """One of the two documented constraints is enforced everywhere. The level "**must be 1** for the
    first item", and any generated level above one in that position is refused."""
    outline = _flat_outline(titles)
    outline[0][0] = level
    with _sections(titles) as binder, pytest.raises(ValueError):
        binder.set_toc(outline)


@given(BINDER_AND_EARLIER_ROW, st.integers(min_value=3, max_value=9))
@BINDER_OUTLINE
def test_set_toc_refuses_a_level_that_jumps_by_more_than_one(binder_and_row, level):
    """And "at most 1 larger than the previous one" is enforced in every row after the first, including
    the last -- the row whose page number nothing checks."""
    titles, row = binder_and_row
    outline = _flat_outline(titles)
    outline[row + 1][0] = level
    with _sections(titles) as binder, pytest.raises(ValueError):
        binder.set_toc(outline)


@given(BINDER_TITLE)
@BINDER_OUTLINE
def test_the_zero_page_refusal_belongs_to_one_writer_and_not_to_the_format(title):
    """The case also asserts that `pymupdf.open().tobytes()` raises, with the comment that "a
    zero-page document cannot even be serialized". The refusal is real and it is MuPDF's. pypdf writes a
    zero-page PDF without complaint, carrying the generated title; MuPDF opens that file and hands the
    title back, and refuses only when asked to write it out again; PDFium will not open it at all. Three
    libraries, three policies, and the guarantee the case reads off the exception is a property of the
    writer it happened to use."""
    writer = pypdf.PdfWriter()
    writer.add_metadata({'/Title': title})
    written = io.BytesIO()
    writer.write(written)
    data = written.getvalue()
    with pymupdf.open(stream=data, filetype='pdf') as empty:
        npt.assert_equal(empty.metadata['title'], title)
        with pytest.raises(ValueError):
            empty.tobytes()
    with pytest.raises(pypdfium2.PdfiumError):
        pypdfium2.PdfDocument(io.BytesIO(data))



# --------------------------------------------------------------------------------------------------
# handoff_guards_v10.py, case sparse_matrix_sums_duplicates_silently: accumulating duplicate pairs
# --------------------------------------------------------------------------------------------------
RESOURCE_SHAPE = (4, 4)
RESOURCE_INDEX = st.integers(min_value=0, max_value=RESOURCE_SHAPE[0] - 1)
RESOURCE_COORD = st.tuples(RESOURCE_INDEX, RESOURCE_INDEX)
EXACT_WEIGHT = st.integers(min_value=-1000, max_value=1000).map(float)
HANDOVER_WEIGHT = st.floats(min_value=-1e3, max_value=1e3, allow_nan=False, allow_infinity=False)
EXACT_PAIRS = st.lists(st.tuples(RESOURCE_INDEX, RESOURCE_INDEX, EXACT_WEIGHT), min_size=1, max_size=12)
HANDOVER_PAIRS = st.lists(st.tuples(RESOURCE_INDEX, RESOURCE_INDEX, HANDOVER_WEIGHT),
                          min_size=1, max_size=12)
HANDOVER_COORDS = st.lists(RESOURCE_COORD, min_size=1, max_size=12)
REPEAT_COUNT = st.integers(min_value=2, max_value=8)
ABSORBING_SCALE = st.integers(min_value=80, max_value=200).map(lambda power: 2.0 ** power)
ABSORBED_WEIGHT = st.floats(min_value=1.0, max_value=1e3, allow_nan=False, allow_infinity=False)


def _empty_resource_matrix(dtype):
    """scipy's own empty constructor, `coo_matrix(shape, dtype)`, the first form its docstring shows."""
    return scipy_sparse.coo_matrix(RESOURCE_SHAPE, dtype=dtype)


def _scipy_canonical(rows, cols, weights):
    """scipy's explicit accumulation. `sum_duplicates` is documented in scipy/sparse/_coo.py at tag
    v1.17.1 as "Eliminate duplicate entries by adding them together", "an *in place* operation", and
    the canonical format it produces has "Entries and coordinates sorted by row, then column". Its
    implementation there sorts with `np.lexsort` and reduces each run with `np.add.reduceat`."""
    matrix = scipy_sparse.coo_matrix((list(weights), (list(rows), list(cols))), shape=RESOURCE_SHAPE)
    matrix.sum_duplicates()
    return matrix.row, matrix.col, matrix.data


def _duckdb_grouped(rows, cols, weights):
    """The same accumulation as a relational one. DuckDB 1.5.5 documents `sum(arg)` as "Calculates the
    sum of all non-null values in `arg`"."""
    return duckdb.sql('select r, c, sum(w) as total from '
                      '(select unnest(?::INTEGER[]) as r, unnest(?::INTEGER[]) as c, '
                      'unnest(?::DOUBLE[]) as w) group by r, c order by r, c',
                      params=[list(rows), list(cols), list(weights)]).fetchall()


def _duckdb_distinct_cells(rows, cols):
    return duckdb.sql('select count(*) from (select distinct r, c from '
                      '(select unnest(?::INTEGER[]) as r, unnest(?::INTEGER[]) as c))',
                      params=[list(rows), list(cols)]).fetchone()[0]


def _numpy_accumulated(rows, cols, weights):
    """And as numpy's own unbuffered scatter-add. `ufunc.at` is documented at tag v2.4.6 as an
    "unbuffered in place operation on operand 'a' for elements specified by 'indices'", which for
    addition "is equivalent to ``a[indices] += b``, except that results are accumulated for elements
    that are indexed more than once"."""
    dense = np.zeros(RESOURCE_SHAPE)
    np.add.at(dense, (np.array(list(rows), dtype=int), np.array(list(cols), dtype=int)),
              np.array(list(weights), dtype=float))
    return dense


def _scipy_dense_cell(weights):
    """One cell reached the way the chain reaches it, through `toarray`. The C++ routine behind it,
    coo_todense in scipy/sparse/sparsetools/coo.h at v1.17.1, is one pass over the stored entries in
    the order they were listed: `for(npy_int64 n = 0; n < nnz; n++){ Bx[ (npy_intp)n_col * Ai[n] +
    Aj[n] ] += Ax[n]; }`."""
    zeros = [0] * len(weights)
    return scipy_sparse.coo_matrix((list(weights), (zeros, zeros)), shape=(1, 1)).toarray()[0][0]


def _scipy_canonical_cell(weights):
    """The same cell reached through the operation scipy names, `sum_duplicates`."""
    zeros = [0] * len(weights)
    matrix = scipy_sparse.coo_matrix((list(weights), (zeros, zeros)), shape=(1, 1))
    matrix.sum_duplicates()
    return matrix.data[0]


def _numpy_cell(weights):
    cell = np.zeros((1, 1))
    np.add.at(cell, (np.zeros(len(weights), dtype=int), np.zeros(len(weights), dtype=int)),
              np.array(list(weights), dtype=float))
    return cell[0][0]


def _duckdb_cell(weights):
    return duckdb.sql('select sum(w) from (select unnest(?::DOUBLE[]) as w)',
                      params=[list(weights)]).fetchone()[0]


def _duckdb_compensated_cell(weights):
    """DuckDB's own more accurate summation: `fsum`, documented as calculating "the sum using a more
    accurate floating point summation (Kahan Sum)", with aliases `sumkahan` and `kahan_sum`."""
    return duckdb.sql('select fsum(w) from (select unnest(?::DOUBLE[]) as w)',
                      params=[list(weights)]).fetchone()[0]


def _duckdb_true_count(repeats):
    return duckdb.sql('select sum(present) from (select unnest(?::BOOLEAN[]) as present)',
                      params=[[True] * repeats]).fetchone()[0]


def _scipy_mask(coords):
    """The presence mask as one constructor call, at the dtype a mask wants."""
    rows = [row for row, _ in coords]
    cols = [col for _, col in coords]
    return scipy_sparse.coo_matrix((np.ones(len(coords), dtype=bool), (rows, cols)),
                                   shape=RESOURCE_SHAPE).toarray()


def _numpy_mask(coords):
    """The same mask through numpy's own logical-or scatter."""
    mask = np.zeros(RESOURCE_SHAPE, dtype=bool)
    np.logical_or.at(mask, (np.array([row for row, _ in coords], dtype=int),
                            np.array([col for _, col in coords], dtype=int)), True)
    return mask


@given(EXACT_PAIRS)
@SLOW
def test_scipy_duckdb_and_numpy_accumulate_a_pair_list_identically_when_every_sum_is_exact(pairs):
    """handoff_guards_v10.py's case sparse_matrix_sums_duplicates_silently makes six typed comparisons
    about a resource matrix, the first two of them about what coo_matrix does with duplicate
    coordinates. scipy documents that in scipy/sparse/_coo.py at tag v1.17.1: "By default when
    converting to CSR or CSC format, duplicate (i,j) entries will be summed together", and "Duplicate
    coordinates are maintained until implicitly or explicitly summed". Where the weights are whole
    numbers small enough that every partial sum is exact, the behaviour reproduces in three
    implementations at once: scipy's canonical form, a DuckDB 1.5.5 GROUP BY and numpy's own `add.at`
    scatter-add return the same cells with the same totals. The weights are generated as whole numbers
    for a reason that the next two tests give."""
    rows = [row for row, _, _ in pairs]
    cols = [col for _, col, _ in pairs]
    weights = [weight for _, _, weight in pairs]
    scipy_rows, scipy_cols, scipy_data = _scipy_canonical(rows, cols, weights)
    grouped = _duckdb_grouped(rows, cols, weights)
    npt.assert_array_equal(scipy_rows, [row for row, _, _ in grouped])
    npt.assert_array_equal(scipy_cols, [col for _, col, _ in grouped])
    npt.assert_array_equal(scipy_data, [total for _, _, total in grouped])
    npt.assert_array_equal(
        scipy_sparse.coo_matrix((weights, (rows, cols)), shape=RESOURCE_SHAPE).toarray(),
        _numpy_accumulated(rows, cols, weights))


@given(ABSORBING_SCALE, ABSORBED_WEIGHT)
@SLOW
def test_the_dense_and_the_canonical_summation_of_one_cell_disagree(scale, weight):
    """The reason, and the finding. scipy has two routes to the weight of a cell and they are two
    different summations. `toarray` goes through coo_todense, one pass over the entries in the order
    they were listed; `sum_duplicates` goes through `np.lexsort` -- an "indirect stable sort", so the
    listed order is kept -- and then `np.add.reduceat`, which groups the run differently. Over a
    generated scale and a generated weight far enough below it that a single addition absorbs the
    weight exactly, the two routes return different numbers for the same three entries, in either
    order. The divergence is generated directly rather than filtered for."""
    cancel_first = [scale, -scale, weight]
    cancel_last = [weight, scale, -scale]
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_scipy_dense_cell(cancel_first), _scipy_canonical_cell(cancel_first))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_scipy_dense_cell(cancel_last), _scipy_canonical_cell(cancel_last))


@given(ABSORBING_SCALE, ABSORBED_WEIGHT)
@SLOW
def test_which_of_the_two_summations_keeps_the_weight_depends_on_the_order_it_was_listed(scale, weight):
    """And neither route is the accurate one. With the cancelling pair listed first the dense route
    keeps the generated weight and the canonical route loses it; with the same three entries listed the
    other way round they swap, exactly. So the weight P93's resource matrix records for a cell is
    decided by two things the chain never states: the order its pairs were listed in, and which of
    scipy's two summations was asked for the answer."""
    cancel_first = [scale, -scale, weight]
    cancel_last = [weight, scale, -scale]
    npt.assert_allclose(_scipy_dense_cell(cancel_first), weight)
    npt.assert_allclose(_scipy_canonical_cell(cancel_last), weight)
    with pytest.raises(AssertionError):
        npt.assert_allclose(_scipy_canonical_cell(cancel_first), weight)
    with pytest.raises(AssertionError):
        npt.assert_allclose(_scipy_dense_cell(cancel_last), weight)


@given(ABSORBING_SCALE, ABSORBED_WEIGHT)
@SLOW
def test_no_accumulator_recovers_the_weight_a_middle_listing_absorbs(scale, weight):
    """With the weight listed between the two halves of the cancelling pair, every IEEE accumulator
    loses it and they all lose it together: both of scipy's routes, numpy's scatter-add, DuckDB's SUM,
    and DuckDB's own more accurate aggregate `fsum`, "the sum using a more accurate floating point
    summation (Kahan Sum)", whose compensation term is itself below the scale it would have to correct.
    Only exact arithmetic keeps it, and summing the same three entries as fractions.Fraction returns
    the generated weight. DuckDB documents the general form itself, marking `sum(arg)` as one of the
    functions whose "floating-point versions ... are affected by ordering"."""
    absorbed = [scale, weight, -scale]
    dropped = _scipy_dense_cell(absorbed)
    npt.assert_allclose([_scipy_canonical_cell(absorbed), _numpy_cell(absorbed),
                         _duckdb_cell(absorbed), _duckdb_compensated_cell(absorbed)],
                        [dropped, dropped, dropped, dropped])
    npt.assert_allclose(float(sum(map(Fraction, absorbed))), weight)
    with pytest.raises(AssertionError):
        npt.assert_allclose(dropped, weight)


@given(HANDOVER_COORDS)
@SLOW
def test_the_presence_mask_the_case_builds_by_hand_is_one_constructor_call(coords):
    """The case builds its presence mask with a Python loop, `for r, c in zip(rows, cols): present[r,
    c] = True`, under the comment "a boolean mask cannot be built by summing". It can. At boolean dtype
    the duplicate summation scipy documents is a logical or, so the constructor the case already calls
    returns the mask it writes the loop for, and numpy's own `logical_or.at` scatter returns the same
    array over generated coordinates. The loop is a hand-written implementation of a primitive that was
    one dtype away."""
    npt.assert_array_equal(_scipy_mask(coords), _numpy_mask(coords))


@given(RESOURCE_COORD, REPEAT_COUNT)
@SLOW
def test_duckdb_counts_the_booleans_that_scipy_ors(coord, repeats):
    """The two implementations part company at that dtype, and DuckDB says so in advance: its
    `sum(arg)` "Calculates the sum of all non-null values in `arg` / counts `true` values when `arg` is
    boolean". So over one generated coordinate repeated a generated number of times, scipy's boolean
    matrix is the matrix of that coordinate listed once, while the relational sum of the same column of
    true values is the number of repeats. "Summing the duplicates" names two different operations in
    the two libraries, and the case's second typed expectation -- that a presence mask built the same
    way becomes a count -- is true of the integer dtype it chose and of DuckDB at every dtype, and
    false of scipy at the dtype a mask wants."""
    npt.assert_array_equal(_scipy_mask([coord] * repeats), _scipy_mask([coord]))
    npt.assert_array_equal(_duckdb_true_count(repeats), repeats)


@given(HANDOVER_COORDS)
@SLOW
def test_the_same_pairs_at_integer_dtype_are_the_duckdb_count_of_each_cell(coords):
    """At integer dtype the two agree again, and the count the case types is reproduced by a second
    engine: a matrix of ones summed by scipy holds, in every cell, the number of generated pairs
    DuckDB's GROUP BY counts there."""
    rows = [row for row, _ in coords]
    cols = [col for _, col in coords]
    counted = scipy_sparse.coo_matrix((np.ones(len(coords), dtype=np.int64), (rows, cols)),
                                      shape=RESOURCE_SHAPE).toarray()
    grouped = duckdb.sql('select r, c, count(*) as n from '
                         '(select unnest(?::INTEGER[]) as r, unnest(?::INTEGER[]) as c) '
                         'group by r, c order by r, c', params=[rows, cols]).fetchall()
    npt.assert_array_equal([counted[row][col] for row, col, _ in grouped],
                           [n for _, _, n in grouped])


@given(HANDOVER_PAIRS)
@SLOW
def test_nnz_counts_stored_entries_until_sum_duplicates_makes_it_count_cells(pairs):
    """The count the case reaches by summing its hand-built mask is carried by the object itself, and
    it means two different things before and after the operation scipy names. Freshly constructed, nnz
    is the number of generated pairs, because "Duplicate coordinates are maintained until implicitly or
    explicitly summed"; after `sum_duplicates` it is the number of distinct cells, which is what DuckDB
    counts with COUNT over a DISTINCT projection."""
    rows = [row for row, _, _ in pairs]
    cols = [col for _, col, _ in pairs]
    weights = [weight for _, _, weight in pairs]
    matrix = scipy_sparse.coo_matrix((weights, (rows, cols)), shape=RESOURCE_SHAPE)
    npt.assert_array_equal(matrix.nnz, len(pairs))
    matrix.sum_duplicates()
    npt.assert_array_equal(matrix.nnz, _duckdb_distinct_cells(rows, cols))


@given(HANDOVER_COORDS)
@SLOW
def test_a_recorded_zero_weight_is_stored_and_still_invisible_in_the_dense_matrix(coords):
    """The case's third claim, executed. Every generated pair is recorded with a zero weight, and the
    dense matrix is then indistinguishable from the matrix of a binder with no pairs at all, built by
    scipy's own empty constructor. The distinction the case wants survives in two places the case does
    not look: the canonical format is documented to allow it, "Data arrays MAY have explicit zeros", so
    nnz still counts the recorded pairs, and the boolean matrix built from the same coordinates still
    marks them present where the empty one does not."""
    rows = [row for row, _ in coords]
    cols = [col for _, col in coords]
    recorded = scipy_sparse.coo_matrix(([0.0] * len(coords), (rows, cols)), shape=RESOURCE_SHAPE)
    npt.assert_array_equal(recorded.toarray(), _empty_resource_matrix(float).toarray())
    npt.assert_array_equal(recorded.nnz, len(coords))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(_scipy_mask(coords), _empty_resource_matrix(bool).toarray())


@given(RESOURCE_INDEX, RESOURCE_INDEX, HANDOVER_WEIGHT)
@SLOW
def test_two_weights_that_cancel_leave_one_stored_zero_until_eliminate_zeros_runs(row, col, weight):
    """And the same cell reached the other way. Two generated weights that cancel are two stored
    entries; `sum_duplicates` makes them one, which DuckDB's DISTINCT count agrees is one cell, and its
    dense matrix is again the empty one; `eliminate_zeros`, "Remove zero entries from the
    array/matrix", then removes the entry altogether and nnz falls to what an empty matrix reports. So
    whether a recorded pair is present in the sparse object depends on which of scipy's clean-up
    primitives has been called, and the dense matrix the chain hands on has forgotten the difference
    before any of them runs."""
    cancelling = [weight, -weight]
    matrix = scipy_sparse.coo_matrix((cancelling, ([row, row], [col, col])), shape=RESOURCE_SHAPE)
    npt.assert_array_equal(matrix.nnz, len(cancelling))
    matrix.sum_duplicates()
    npt.assert_array_equal(matrix.nnz, _duckdb_distinct_cells([row, row], [col, col]))
    npt.assert_array_equal(matrix.toarray(), _empty_resource_matrix(float).toarray())
    matrix.eliminate_zeros()
    npt.assert_array_equal(matrix.nnz, _empty_resource_matrix(float).nnz)


# --------------------------------------------------------------------------------------------------
# handoff_guards_v9.py, case formula_caches_must_be_computed_not_defaulted: caches and blank cells
# --------------------------------------------------------------------------------------------------
EXCEL_CELL_ORACLE_JAVA = pathlib.Path(__file__).with_name('excel_cell_oracle.java')
MEASURE_NAME = st.text(alphabet=st.characters(min_codepoint=65, max_codepoint=90), min_size=2, max_size=6)
MEASURE_VALUE = st.integers(min_value=0, max_value=100000)
CACHED_TOTAL = st.integers(min_value=-100000, max_value=100000)
MEASURE_ROWS = st.lists(st.tuples(MEASURE_NAME, MEASURE_VALUE), min_size=2, max_size=5,
                        unique_by=lambda pair: pair[0])
MEASURE_ROWS_AND_BLANK = MEASURE_ROWS.flatmap(
    lambda rows: st.tuples(st.just(rows), st.integers(min_value=1, max_value=len(rows))))
WRITE_FORMULA_DEFAULT_CACHE = inspect.signature(
    xlsxwriter.worksheet.Worksheet.write_formula).parameters['value'].default


def _measures_workbook(rows, *, cache=None, blank=None, blank_format=False, omit=False):
    """The case's own writer, XlsxWriter 3.2.9. Its `write_formula` signature at tag RELEASE_3.2.9
    carries `value=0` with the parameter line "value: An optional value for the formula. Default is
    0.", and `write_blank` there is "Write a blank cell with formatting to a worksheet cell. The blank
    token is ignored and the format only is written to the cell." With `omit` the blank row's second
    cell is not written at all, which is the comparison the next test needs."""
    buffer = io.BytesIO()
    book = xlsxwriter.Workbook(buffer, {'in_memory': True})
    sheet = book.add_worksheet('measures')
    sheet.write_row(0, 0, ['activity', 'events'])
    for number, (name, value) in enumerate(rows, start=1):
        sheet.write(number, 0, name)
        if number == blank:
            if not omit:
                sheet.write_blank(number, 1, None,
                                  book.add_format({'bold': True}) if blank_format else None)
        else:
            sheet.write_number(number, 1, value)
    formula = '=SUM(B2:B%d)' % (len(rows) + 1)
    if cache is None:
        sheet.write_formula(len(rows) + 1, 1, formula)
    else:
        sheet.write_formula(len(rows) + 1, 1, formula, None, cache)
    book.close()
    return buffer.getvalue()


def _openpyxl_column(data, *, cached):
    """openpyxl 3.1.5 reading the events column, with and without `data_only`."""
    sheet = openpyxl.load_workbook(io.BytesIO(data), data_only=cached).active
    return [cell.value for row in sheet.iter_rows(min_col=2, max_col=2) for cell in row]


def _calamine_column(data):
    """The Rust calamine reader on the same column."""
    sheet = CalamineWorkbook.from_filelike(io.BytesIO(data)).get_sheet_by_index(0)
    return [row[1] for row in sheet.to_python(skip_empty_area=False)]


def _sheet_xml(data):
    """The sheet part itself, out of the package, as a third witness."""
    return zipfile.ZipFile(io.BytesIO(data)).read('xl/worksheets/sheet1.xml')


def _stored_formula(data):
    """And the formula as the file records it, read with expat through ElementTree."""
    tree = ElementTree.fromstring(_sheet_xml(data))
    return [node.text for node in tree.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')]


def _poi_column(data, policy):
    """The same column read by Apache POI 5.4.1 under Java. The shim parses argv, calls the library and
    prints one line per cell for each of the three values of POI's `Row.MissingCellPolicy`; POI numbers
    columns from zero where openpyxl numbers them from one, which is the only translation involved."""
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / 'measures.xlsx'
        path.write_bytes(data)
        completed = subprocess.run(
            ['java', '-Dlog4j2.statusLoggerLevel=OFF', '-cp', str(POI_DIRECTORY / 'jars' / '*'),
             str(EXCEL_CELL_ORACLE_JAVA), str(path), '1'],
            capture_output=True, encoding='utf-8', check=True)
    return [line.split('\t')[1:] for line in completed.stdout.split('\n')[:-1]
            if line.startswith(policy + '\t')]


@pytest.mark.skipif(not poi_available, reason='java and the Apache POI jars are required for this oracle')
@given(MEASURE_ROWS)
@JAVA_ORACLE
def test_the_default_formula_cache_is_the_zero_the_writer_signature_names(rows):
    """handoff_guards_v9.py's case formula_caches_must_be_computed_not_defaulted makes six typed
    comparisons about a workbook of measures, the first being that a formula written without a value
    reads back as 0, "the default cache is a zero nobody computed". The zero is not typed here: it is
    read off XlsxWriter's own signature, whose `value` parameter defaults to 0 at tag RELEASE_3.2.9,
    and three readers that share nothing hand it back -- openpyxl 3.1.5 with `data_only`, the Rust
    calamine reader, and Apache POI 5.4.1 under Java, whose `getNumericCellValue` on a formula cell
    returns the cached number. So the default is not a gap one reader papers over; every reader of the
    file believes it, and nothing in the file says the total was never computed."""
    data = _measures_workbook(rows)
    npt.assert_array_equal(_openpyxl_column(data, cached=True)[-1], WRITE_FORMULA_DEFAULT_CACHE)
    npt.assert_array_equal(_calamine_column(data)[-1], WRITE_FORMULA_DEFAULT_CACHE)
    npt.assert_array_equal(float(_poi_column(data, 'RETURN_NULL_AND_BLANK')[-1][3]),
                           WRITE_FORMULA_DEFAULT_CACHE)


@pytest.mark.skipif(not poi_available, reason='java and the Apache POI jars are required for this oracle')
@given(MEASURE_ROWS, CACHED_TOTAL)
@JAVA_ORACLE
def test_three_readers_return_the_cache_the_writer_chose_and_none_recomputes_it(rows, cache):
    """And supplying a value does not make the cache a total. The cached number is generated
    independently of the column the formula sums, and all three readers return that number rather than
    the sum of the cells above it. So "computed" in the case's own vocabulary means only that the
    writer passed a value: no reader of the file checks it against the formula, and a workbook whose
    cache disagrees with its own cells is read back without complaint by every one of them."""
    data = _measures_workbook(rows, cache=cache)
    npt.assert_array_equal(_openpyxl_column(data, cached=True)[-1], cache)
    npt.assert_array_equal(_calamine_column(data)[-1], cache)
    npt.assert_array_equal(float(_poi_column(data, 'RETURN_NULL_AND_BLANK')[-1][3]), cache)


@pytest.mark.skipif(not poi_available, reason='java and the Apache POI jars are required for this oracle')
@given(MEASURE_ROWS, CACHED_TOTAL)
@JAVA_ORACLE
def test_the_equals_sign_the_case_types_is_not_in_the_file(rows, cache):
    """The case types the formula as `'=SUM(B2:B4)'`. The file does not hold that string. The `f`
    element read out of the sheet part with expat carries the expression without a leading equals sign,
    and so does POI, whose `getCellFormula` is documented at tag REL_5_4_1 as returning "a formula for
    the cell, for example, <code>SUM(C4:E4)</code>". openpyxl is the reader that puts the sign back,
    and the typed expectation is a property of that reader rather than of the workbook."""
    data = _measures_workbook(rows, cache=cache)
    stored = _stored_formula(data)
    npt.assert_array_equal(stored, [_poi_column(data, 'RETURN_NULL_AND_BLANK')[-1][2]])
    npt.assert_array_equal(_openpyxl_column(data, cached=False)[-1], '=' + stored[0])


@given(MEASURE_ROWS_AND_BLANK, CACHED_TOTAL)
@SLOW
def test_write_blank_without_a_format_leaves_the_sheet_exactly_as_if_it_were_never_called(rows_and_blank,
                                                                                          cache):
    """What the case's "a missing source cell stays blank, never zero" rests on. XlsxWriter's
    `_write_blank` at tag RELEASE_3.2.9 opens `# Don't write a blank cell unless it has a format.` and
    returns 0 when `cell_format is None`, and the sheet part it produces is byte for byte the part
    produced when the call is left out altogether. So the workbook records no blank cell for that row;
    it records no cell at all, and the call the chain makes to mark the gap is a call that writes
    nothing."""
    rows, blank = rows_and_blank
    written = _measures_workbook(rows, cache=cache, blank=blank)
    omitted = _measures_workbook(rows, cache=cache, blank=blank, omit=True)
    npt.assert_array_equal(_sheet_xml(written), _sheet_xml(omitted))


@given(MEASURE_ROWS_AND_BLANK, CACHED_TOTAL)
@SLOW
def test_the_two_python_readers_disagree_about_the_cell_that_was_never_written(rows_and_blank, cache):
    """The case records that disagreement as a finding and types both halves of it, openpyxl's None
    against calamine's empty string. Executed over generated rows and a generated gap, the two readers
    return columns that differ, and they differ only there: with no gap in the workbook the same two
    columns are equal."""
    rows, blank = rows_and_blank
    with_gap = _measures_workbook(rows, cache=cache, blank=blank)
    without_gap = _measures_workbook(rows, cache=cache)
    npt.assert_array_equal(np.array(_openpyxl_column(without_gap, cached=True), dtype=object),
                           np.array(_calamine_column(without_gap), dtype=object))
    with pytest.raises(AssertionError):
        npt.assert_array_equal(np.array(_openpyxl_column(with_gap, cached=True), dtype=object),
                               np.array(_calamine_column(with_gap), dtype=object))


@pytest.mark.skipif(not poi_available, reason='java and the Apache POI jars are required for this oracle')
@given(MEASURE_ROWS_AND_BLANK, CACHED_TOTAL)
@JAVA_ORACLE
def test_only_the_third_reader_tells_an_absent_cell_from_a_blank_one(rows_and_blank, cache):
    """And the question the two Python readers are disagreeing about has a third answer neither of them
    can give. Writing the same gap with a format produces a workbook that does hold a cell there, and
    openpyxl and calamine return exactly the same column for both files -- neither can tell the two
    apart. POI can: its cell types differ between the two, because `Row.MissingCellPolicy` makes the
    question explicit and its default, documented as "If you ask for a cell that is not defined....you
    get a null.", is not the only answer it offers."""
    rows, blank = rows_and_blank
    absent = _measures_workbook(rows, cache=cache, blank=blank)
    present = _measures_workbook(rows, cache=cache, blank=blank, blank_format=True)
    npt.assert_array_equal(np.array(_openpyxl_column(absent, cached=True), dtype=object),
                           np.array(_openpyxl_column(present, cached=True), dtype=object))
    npt.assert_array_equal(np.array(_calamine_column(absent), dtype=object),
                           np.array(_calamine_column(present), dtype=object))
    with pytest.raises(AssertionError):
        npt.assert_array_equal([cell[1] for cell in _poi_column(absent, 'RETURN_NULL_AND_BLANK')],
                               [cell[1] for cell in _poi_column(present, 'RETURN_NULL_AND_BLANK')])


@pytest.mark.skipif(not poi_available, reason='java and the Apache POI jars are required for this oracle')
@given(MEASURE_ROWS_AND_BLANK, CACHED_TOTAL)
@JAVA_ORACLE
def test_the_third_readers_own_policies_disagree_with_each_other_about_the_same_file(rows_and_blank,
                                                                                    cache):
    """Which is the reading the case cannot reach at all, because it has only two readers and they
    return one answer each. POI returns two different answers for one workbook depending on which of
    its three documented policies is asked: under the default the missing cell is a null, and under
    `CREATE_NULL_AS_BLANK` it is a cell of blank type. The question "is that cell blank" has no answer
    in the file, and a chain that reconciles two readers has settled a disagreement that a third reader
    keeps open on purpose."""
    rows, blank = rows_and_blank
    data = _measures_workbook(rows, cache=cache, blank=blank)
    with pytest.raises(AssertionError):
        npt.assert_array_equal([cell[1] for cell in _poi_column(data, 'RETURN_NULL_AND_BLANK')],
                               [cell[1] for cell in _poi_column(data, 'CREATE_NULL_AS_BLANK')])


# --------------------------------------------------------------------------------------------------
# handoff_guards_v9.py, case python_docx_cannot_paginate: what a .docx says about its own pagination
# --------------------------------------------------------------------------------------------------
DOCX_PROPERTIES_ORACLE_JAVA = pathlib.Path(__file__).with_name('docx_properties_oracle.java')
DOCX_TEMPLATE = pathlib.Path(docx.__file__).with_name('templates') / 'default.docx'
WORDPROCESSING_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
EXTENDED_PROPERTIES_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'
PAGE_BREAK_PATH = ".//{%s}br[@{%s}type='page']" % (WORDPROCESSING_NS, WORDPROCESSING_NS)
DOCX_LINE = st.text(alphabet=st.characters(min_codepoint=65, max_codepoint=90), min_size=2, max_size=8)
DOCX_LINES = st.lists(DOCX_LINE, min_size=1, max_size=6)
DOCX_BREAKS = st.integers(min_value=0, max_value=4)


def _paginated_document(lines, breaks):
    """A document written the way the case writes one. python-docx 1.2.0's `Document()` is documented
    at tag v1.2.0 as loading "the built-in default document "template"" when called with no argument,
    and `add_page_break` as returning a "newly |Paragraph| object containing only a page break", which
    its body confirms: `add_paragraph()` and then a run carrying `WD_BREAK.PAGE`."""
    document = docx.Document()
    for line in lines:
        document.add_paragraph(line)
    for _ in range(breaks):
        document.add_page_break()
    written = io.BytesIO()
    document.save(written)
    return written.getvalue()


def _stated_property(data, name):
    """One element of docProps/app.xml, read with expat through ElementTree."""
    tree = ElementTree.fromstring(zipfile.ZipFile(io.BytesIO(data)).read('docProps/app.xml'))
    return [node.text for node in tree.iter('{%s}%s' % (EXTENDED_PROPERTIES_NS, name))]


def _page_breaks(data, parser):
    """The explicit page breaks in word/document.xml, counted by whichever XML implementation is
    handed in -- libxml2 through lxml, or expat through ElementTree."""
    body = parser.fromstring(zipfile.ZipFile(io.BytesIO(data)).read('word/document.xml'))
    return len(body.findall(PAGE_BREAK_PATH))


def _poi_document_properties(data):
    """The same document read by Apache POI 5.4.1 under Java. The shim parses argv, calls the library
    and prints the extended properties POIXMLProperties.ExtendedProperties returns, then the size of
    the list XWPFDocument.getParagraphs() returns."""
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / 'document.docx'
        path.write_bytes(data)
        completed = subprocess.run(
            ['java', '-Dlog4j2.statusLoggerLevel=OFF', '-cp', str(POI_DIRECTORY / 'jars' / '*'),
             str(DOCX_PROPERTIES_ORACLE_JAVA), str(path)],
            capture_output=True, encoding='utf-8', check=True)
    return dict(line.split('\t') for line in completed.stdout.split('\n')[:-1])


@given(DOCX_LINES, DOCX_BREAKS)
@SLOW
def test_the_page_count_the_package_states_is_the_templates_and_never_moves(lines, breaks):
    """handoff_guards_v9.py's case python_docx_cannot_paginate makes five typed comparisons, the first
    two being that `page_count_available` is False, under the comment "python-docx exposes no page
    count; pagination belongs to a renderer", and that one explicit page break is found, under the
    comment "only the explicit break is knowable from the file". The first is true of the library and false of the file. Every document python-docx writes is
    written from the .docx its own api.py names, `os.path.join(_thisdir, "templates", "default.docx")`,
    and that package states a page count in docProps/app.xml. Over generated paragraphs and a generated
    number of page breaks the number written out is the template's own, unchanged."""
    data = _paginated_document(lines, breaks)
    npt.assert_array_equal(_stated_property(data, 'Pages'),
                           _stated_property(DOCX_TEMPLATE.read_bytes(), 'Pages'))


@pytest.mark.skipif(not poi_available, reason='java and the Apache POI jars are required for this oracle')
@given(DOCX_LINES, DOCX_BREAKS)
@JAVA_ORACLE
def test_a_second_implementation_of_the_format_hands_that_number_back_as_the_page_count(lines, breaks):
    """And a library that does expose a page count for a .docx returns it. Apache POI 5.4.1's
    `POIXMLProperties.ExtendedProperties.getPages`, whose body at tag REL_5_4_1 returns the stored
    value and `-1` only when the element is unset, hands back the template's number for every generated
    document. So "pagination belongs to a renderer" describes python-docx's API rather than the format:
    another implementation of the same format answers the question, and its answer came from whoever
    made the template."""
    data = _paginated_document(lines, breaks)
    npt.assert_array_equal(int(_poi_document_properties(data)['PAGES']),
                           int(_stated_property(DOCX_TEMPLATE.read_bytes(), 'Pages')[0]))


@pytest.mark.skipif(not poi_available, reason='java and the Apache POI jars are required for this oracle')
@given(DOCX_LINES, DOCX_BREAKS)
@JAVA_ORACLE
def test_the_word_and_character_counts_the_package_states_are_the_templates_too(lines, breaks):
    """The page count is not alone. The word count and the character count the package states are the
    template's as well, whatever text the document carries, and the second implementation returns those
    too."""
    data = _paginated_document(lines, breaks)
    properties = _poi_document_properties(data)
    template = DOCX_TEMPLATE.read_bytes()
    npt.assert_array_equal([int(properties['WORDS']), int(properties['CHARACTERS'])],
                           [int(_stated_property(template, 'Words')[0]),
                            int(_stated_property(template, 'Characters')[0])])


@pytest.mark.skipif(not poi_available, reason='java and the Apache POI jars are required for this oracle')
@given(DOCX_LINES, DOCX_BREAKS)
@JAVA_ORACLE
def test_the_paragraphs_the_second_reader_counts_move_where_the_stated_ones_do_not(lines, breaks):
    """Which separates the two kinds of number a package carries. Asked to count rather than to report,
    the same library tracks the content exactly: the paragraphs POI walks are the generated lines plus
    one for each generated page break, because `add_page_break` puts each break in a paragraph of its
    own. The paragraph count the package states never moves at all, so the two disagree for every
    document with anything in it."""
    data = _paginated_document(lines, breaks)
    counted = int(_poi_document_properties(data)['COUNTED_PARAGRAPHS'])
    npt.assert_array_equal(counted, len(lines) + breaks)
    with pytest.raises(AssertionError):
        npt.assert_array_equal(counted, int(_stated_property(data, 'Paragraphs')[0]))


@given(DOCX_LINES, DOCX_BREAKS)
@SLOW
def test_the_explicit_break_count_is_the_number_that_does_track_the_content(lines, breaks):
    """The case's other claim holds. The `w:br` elements carrying `w:type="page"` are exactly the breaks
    the document was given, counted the same way by libxml2 through lxml and by expat through
    ElementTree, so the one structural signal the case relies on is in the file and is read alike by two
    XML implementations."""
    data = _paginated_document(lines, breaks)
    npt.assert_array_equal([_page_breaks(data, lxml_etree), _page_breaks(data, ElementTree)],
                           [breaks, breaks])


@given(DOCX_LINES, DOCX_BREAKS)
@SLOW
def test_every_document_carries_the_templates_part_list_and_its_thumbnail(lines, breaks):
    """And what else travels with it. The package python-docx writes has the template's part list, part
    for part, and carries the template's own docProps/thumbnail.jpeg unchanged -- a picture of a
    document nobody in the chain wrote. A chain that fingerprints the package, as P83's does, is
    fingerprinting that image along with its own text."""
    data = _paginated_document(lines, breaks)
    written = zipfile.ZipFile(io.BytesIO(data))
    template = zipfile.ZipFile(io.BytesIO(DOCX_TEMPLATE.read_bytes()))
    npt.assert_array_equal(sorted(written.namelist()), sorted(template.namelist()))
    npt.assert_array_equal(written.read('docProps/thumbnail.jpeg'),
                           template.read('docProps/thumbnail.jpeg'))
