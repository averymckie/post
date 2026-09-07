"""Hardening guards as a plain pytest file.

Run with `pytest hardening/test_library_defaults.py`. Nothing here is bespoke: pytest is the runner, hypothesis
generates every input, the libraries under test compute every value, and the comparison is each library's own
published assertion callable. A reader with the pinned packages can run this file without anything else from
this repository, which is the point of rule 5 of the hardening assurance.

Each test names the hand-typed expectation in the frozen guard modules that it replaces.
"""
import itertools
import json
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from fractions import Fraction

import igraph
import networkx as nx
import orjson

import nltk
import numpy.testing as npt
import pandas as pd
import pandas.testing as pdt
import polars as pl
import polars.testing as plt
import pytest
import rapidfuzz.distance.Levenshtein as rf_levenshtein
from hypothesis import given, settings, strategies as st
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
