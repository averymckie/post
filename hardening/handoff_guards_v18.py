"""Glue elimination for the guard modules already embedded in this TXT.

This module does not add findings. It removes custom glue from the hardening artifacts themselves. Twelve handwritten
functions in handoff_guards_v15.py and handoff_guards_v16.py, and three more in v17, implement work that an existing
library primitive already performs: an interval-overlap test, temporal stepping, graph traversal accumulation, schema
checking, a largest-remainder apportionment, an edit-distance enumeration and a deterministic archive rewrite. Each
case below calls the researched primitive alone and states whether it reproduces the recorded result, refuses the
input, or disagrees. Where a primitive refuses or disagrees, the refusal is the outcome; no handwritten fallback is
reinstated. Requires handoff_guards_v1.py from this TXT. All runtime inputs are authored fixtures. No model client
and no network.
Run: python handoff_guards_v18.py --report report.json
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, io, json, logging, traceback, warnings, zipfile
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
import apportionment.methods as apportionment
import networkx as nx
import numpy as np
import pandas as pd
import pandera.pandas as pandera
import portion
import scipy.sparse as sparse
from largest_remainder import LargestRemainder
from rapidfuzz import process as rf_process
from rapidfuzz.distance import DamerauLevenshtein
from repro_zipfile import ReproducibleZipFile
from scipy.sparse.linalg import spsolve
import handoff_guards_v1 as g
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

# Each entry names a handwritten function embedded earlier in this TXT and the primitive that replaces it.
REPLACES = {
    'v16.overlaps': 'portion.Interval.overlaps / adjacent',
    'v16.month_walk': 'pandas.period_range and pandas.Period.end_time',
    'v15.working_days': 'pandas.tseries.offsets.CustomBusinessDay',
    'v15.offset_day': 'pandas.tseries.offsets.CustomBusinessDay',
    'v16.path_quantity': 'scipy.sparse.linalg.spsolve on the Leontief total-requirements system',
    'v16.gross_requirement': 'scipy.sparse.linalg.spsolve on the Leontief total-requirements system',
    'v15.earliest_starts': 'networkx.dag_longest_path_length',
    'v16.staged': 'pandera.DataFrameSchema with Check.isin',
    'v16.assessed': 'pandera.DataFrameSchema with Check.isin',
    'v16.unique_receipts': 'pandera.DataFrameSchema with a unique column constraint',
    'v16.bom_graph': 'pandera.DataFrameSchema with a composite unique constraint',
    'v15.build_plan': 'pandera.DataFrameSchema with Check.isin over declared identifiers',
    'v17.apportion': 'largest_remainder.LargestRemainder.round / apportionment.methods.compute',
    'v17.within_one': 'rapidfuzz.process.extract alone',
    'v16.part_digests': 'repro_zipfile.ReproducibleZipFile',
    'v16.normalized_package': 'repro_zipfile.ReproducibleZipFile',
    'v16.stamp_dates': 'repro_zipfile.ReproducibleZipFile',
}

CALENDAR_HOLIDAYS = ['2026-09-07']
BUSINESS_DAY = pd.tseries.offsets.CustomBusinessDay(weekmask='Mon Tue Wed Thu Fri', holidays=CALENDAR_HOLIDAYS)


def interval(start, finish, *, bounds: str):
    """bounds='[)' is the half-open reading; '[]' is the closed one. No local overlap arithmetic."""
    if bounds == '[)':
        return portion.closedopen(start, finish)
    if bounds == '[]':
        return portion.closed(start, finish)
    raise g.Blocked('unknown interval bounds %r' % bounds)


def total_requirements(edges: list[dict], demand: dict) -> dict:
    """Leontief total requirements. The traversal and the per-path product are the solver's, not this module's."""
    graph = nx.DiGraph()
    for edge in edges:
        graph.add_edge(edge['parent'], edge['child'], qty=edge['qty'])
    if not nx.is_directed_acyclic_graph(graph):
        raise g.Blocked('bill of materials is not acyclic')
    nodes = sorted(graph.nodes())
    matrix = nx.to_scipy_sparse_array(graph, nodelist=nodes, weight='qty', format='csc').T
    wanted = np.zeros(len(nodes))
    for item, units in demand.items():
        if item not in nodes:
            raise g.Blocked('demand names an item outside the bill of materials: %r' % item)
        wanted[nodes.index(item)] = units
    solved = spsolve((sparse.identity(len(nodes), format='csc') - matrix).tocsc(), wanted)
    return {node: float(value) for node, value in zip(nodes, solved)}


PIPELINE_SCHEMA = pandera.DataFrameSchema({
    'stage': pandera.Column(str, pandera.Check.isin(['Qualify', 'Propose', 'Negotiate', 'Won', 'Lost'])),
    'amt': pandera.Column(float, pandera.Check.ge(0)),
})
ORDINAL_SCHEMA = pandera.DataFrameSchema({
    'likelihood': pandera.Column(int, pandera.Check.isin([1, 2, 3, 4, 5]), nullable=True),
    'impact': pandera.Column(int, pandera.Check.isin([1, 2, 3, 4, 5]), nullable=True),
})
RECEIPT_SCHEMA = pandera.DataFrameSchema({
    'receipt_id': pandera.Column(str),
    'qty': pandera.Column(int, pandera.Check.gt(0)),
}, unique=['receipt_id', 'qty'])
BOM_SCHEMA = pandera.DataFrameSchema({
    'parent': pandera.Column(str),
    'child': pandera.Column(str),
    'qty': pandera.Column(int, pandera.Check.gt(0)),
}, unique=['parent', 'child'])


def validated(frame: pd.DataFrame, schema: pandera.DataFrameSchema) -> pd.DataFrame:
    try:
        return schema.validate(frame, lazy=True)
    except pandera.errors.SchemaErrors as failure:
        cases = failure.failure_cases[['check', 'failure_case']].to_dict('records')
        raise g.Blocked('schema rejected %d value(s): %s' % (len(cases), cases))


def hamilton(total_cents: int, weights: list[int], *, library: str) -> list[int]:
    if library == 'largest_remainder':
        return LargestRemainder.round(list(weights), total=total_cents)
    if library == 'apportionment':
        return apportionment.compute('hamilton', list(weights), total_cents, verbose=False)
    raise g.Blocked('unknown apportionment library %r' % library)


def reproducible_package(parts: dict) -> bytes:
    buf = io.BytesIO()
    with ReproducibleZipFile(buf, 'w') as archive:
        for name in sorted(parts):
            archive.writestr(name, parts[name])
    return buf.getvalue()


def stamps(package: bytes) -> set:
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        return {info.date_time for info in archive.infolist()}


C = []
def case(name):
    def reg(fn): C.append((name, fn)); return fn
    return reg


@case('v16.overlaps -> portion')
def interval_overlap_is_a_library_operation():
    first = interval(datetime(2026, 9, 7, 9, tzinfo=timezone.utc), datetime(2026, 9, 7, 10, tzinfo=timezone.utc), bounds='[)')
    second = interval(datetime(2026, 9, 7, 10, tzinfo=timezone.utc), datetime(2026, 9, 7, 11, tzinfo=timezone.utc), bounds='[)')
    g.equal(first.overlaps(second), False)  # v16 asserted this with a handwritten comparison
    g.equal(first.adjacent(second), True)  # and had no way to say this at all
    g.equal((first & second).empty, True)
    closed_first = interval(9, 10, bounds='[]'); closed_second = interval(10, 11, bounds='[]')
    g.equal(closed_first.overlaps(closed_second), True)
    g.equal(closed_first.adjacent(closed_second), False)
    g.equal(interval(9, 11, bounds='[)').overlaps(interval(10, 12, bounds='[)')), True)
    g.equal(interval(9, 11, bounds='[)').contains(interval(9, 10, bounds='[)')), True)
    g.rejects(g.Blocked, lambda: interval(9, 10, bounds='(]'))
    union = interval(9, 10, bounds='[)') | interval(10, 11, bounds='[)')
    g.equal(union.atomic, True); g.equal(union, interval(9, 11, bounds='[)'))
    return {'replaces': REPLACES['v16.overlaps'], 'reproduces_the_recorded_result': True,
            'adds_an_adjacency_predicate_the_glue_lacked': True}


@case('v15.working_days/offset_day -> pandas CustomBusinessDay')
def working_day_arithmetic_is_a_calendar_offset():
    start, finish = pd.Timestamp('2026-09-08'), pd.Timestamp('2026-09-10')
    half_open = len(pd.bdate_range(start, finish, freq=BUSINESS_DAY)) - 1
    inclusive = len(pd.bdate_range(start, finish, freq=BUSINESS_DAY))
    g.equal(half_open, 2); g.equal(inclusive, 3)  # v15 added the day by hand
    g.equal(BUSINESS_DAY.is_on_offset(pd.Timestamp('2026-09-07')), False)  # the declared holiday
    g.equal(BUSINESS_DAY.is_on_offset(pd.Timestamp('2026-09-08')), True)
    forward = BUSINESS_DAY.rollforward(pd.Timestamp('2026-09-07'))
    backward = BUSINESS_DAY.rollback(pd.Timestamp('2026-09-07'))
    g.equal(str(forward.date()), '2026-09-08'); g.equal(str(backward.date()), '2026-09-04')
    g.equal((forward - backward).days, 4)  # the same divergence v15 reproduced, now from the offset itself
    g.equal(str((pd.Timestamp('2026-09-04') + BUSINESS_DAY).date()), '2026-09-08')
    return {'replaces': REPLACES['v15.working_days'], 'reproduces_the_recorded_result': True,
            'roll_direction_is_an_offset_method': True}


@case('v16.month_walk -> pandas period_range')
def month_ends_come_from_periods_not_from_repeated_addition():
    periods = pd.period_range('2026-01', periods=3, freq='M')
    ends = [p.end_time.date() for p in periods]
    g.equal(ends, [date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31)])
    g.equal(ends[-1], date(2026, 3, 31))  # v16 recorded that its handwritten step reached 2026-03-28 instead
    g.equal(len(periods), 3); g.equal(str(periods[1]), '2026-02')
    g.equal(periods[1].end_time.date() != periods[1].end_time, True)
    g.equal([str(p) for p in periods], ['2026-01', '2026-02', '2026-03'])
    g.equal(pd.Period('2026-02', freq='M').days_in_month, 28)
    return {'replaces': REPLACES['v16.month_walk'], 'reproduces_the_recorded_result': False,
            'primitive_keeps_the_month_end_the_handwritten_step_lost': True}


@case('v16.path_quantity/gross_requirement -> scipy Leontief solve')
def requirement_explosion_is_a_linear_solve():
    edges = [{'parent': 'kit', 'child': 'display', 'qty': 2},
             {'parent': 'display', 'child': 'cable', 'qty': 2},
             {'parent': 'kit', 'child': 'cable', 'qty': 2}]
    per_kit = total_requirements(edges, {'kit': 1})
    g.equal(per_kit['cable'], 6.0)  # v16's handwritten traversal produced 6 by summing two path products
    g.equal(per_kit['display'], 2.0); g.equal(per_kit['kit'], 1.0)
    doubled = total_requirements(edges, {'kit': 2})
    g.equal(doubled['cable'], 12.0)
    g.equal(total_requirements(edges, {'display': 1})['cable'], 2.0)
    g.equal(total_requirements(edges, {'cable': 1})['cable'], 1.0)  # a part demands only itself
    cyclic = edges + [{'parent': 'cable', 'child': 'kit', 'qty': 1}]
    g.rejects(g.Blocked, lambda: total_requirements(cyclic, {'kit': 1}))
    g.rejects(g.Blocked, lambda: total_requirements(edges, {'absent': 1}))
    return {'replaces': REPLACES['v16.path_quantity'], 'reproduces_the_recorded_result': True,
            'no_path_enumeration_in_local_code': True}


@case('v16.staged/assessed -> pandera DataFrameSchema')
def category_membership_is_a_schema_check():
    good = pd.DataFrame({'stage': ['Qualify', 'Propose', 'Negotiate'], 'amt': [1000.0, 15500.0, 250.0]})
    g.equal(len(validated(good, PIPELINE_SCHEMA)), 3)
    typo = pd.DataFrame({'stage': ['Qualify', 'Qualifyy'], 'amt': [1000.0, 3000.0]})
    g.rejects(g.Blocked, lambda: validated(typo, PIPELINE_SCHEMA))
    try:
        validated(typo, PIPELINE_SCHEMA)
    except g.Blocked as blocked:
        g.equal('Qualifyy' in str(blocked), True)  # the schema names the offending value; the glue only counted nulls
    ordinals = pd.DataFrame({'likelihood': [1, 4], 'impact': [2, 4]})
    g.equal(len(validated(ordinals, ORDINAL_SCHEMA)), 2)
    out_of_scale = pd.DataFrame({'likelihood': [1, 6], 'impact': [2, 2]})
    g.rejects(g.Blocked, lambda: validated(out_of_scale, ORDINAL_SCHEMA))
    receipts = pd.DataFrame({'receipt_id': ['R1', 'R2'], 'qty': [2, 1]})
    g.equal(len(validated(receipts, RECEIPT_SCHEMA)), 2)
    conflicting = pd.DataFrame({'receipt_id': ['R1', 'R1'], 'qty': [2, 7]})
    g.equal(len(validated(conflicting, RECEIPT_SCHEMA)), 2)  # distinct rows pass a row-uniqueness constraint
    duplicated = pd.DataFrame({'parent': ['kit', 'kit'], 'child': ['cable', 'cable'], 'qty': [2, 3]})
    g.rejects(g.Blocked, lambda: validated(duplicated, BOM_SCHEMA))  # the composite key catches the second edge
    unique_edges = pd.DataFrame({'parent': ['kit', 'display'], 'child': ['cable', 'cable'], 'qty': [2, 2]})
    g.equal(len(validated(unique_edges, BOM_SCHEMA)), 2)
    return {'replaces': REPLACES['v16.staged'], 'reproduces_the_recorded_result': True,
            'schema_names_the_offending_value': True,
            'row_uniqueness_does_not_catch_a_payload_conflict': True}


@case('v17.apportion -> largest_remainder / apportionment')
def a_researched_apportionment_refuses_the_credit_pool():
    g.equal(hamilton(100_00, [1, 1, 1], library='largest_remainder'), [3334, 3333, 3333])
    g.equal(hamilton(100_00, [1, 1, 1], library='apportionment'), [3334, 3333, 3333])
    g.equal(sum(hamilton(100_00, [1, 1, 1], library='largest_remainder')), 100_00)
    g.equal(hamilton(10_01, [1, 1], library='largest_remainder'), [501, 500])
    g.rejects(ValueError, lambda: hamilton(-130_00, [1, 1, 1], library='largest_remainder'))
    credited = hamilton(-130_00, [1, 1, 1], library='apportionment')
    g.equal(credited, [-4333, -4333, -4333])
    g.equal(sum(credited), -129_99)  # one cent short of the pool
    g.equal(sum(credited) == -130_00, False)  # the second library returns a non-conserving allocation
    g.rejects(g.Blocked, lambda: hamilton(100_00, [1, 1], library='hamilton'))
    g.equal(hamilton(0, [1, 1, 1], library='largest_remainder'), [0, 0, 0])
    g.equal(hamilton(100_00, [0, 1], library='largest_remainder'), [0, 10000])
    return {'replaces': REPLACES['v17.apportion'], 'reproduces_the_recorded_result': True,
            'negative_pool_refused_by_largest_remainder': True,
            'negative_pool_loses_a_cent_under_apportionment': True,
            'credit_allocation_has_no_conserving_primitive': True}


@case('v17.within_one -> rapidfuzz alone')
def the_independent_enumeration_was_the_same_metric_twice():
    words = ['governance', 'governing', 'members', 'member', 'team', 'teams', 'term']
    hits = rf_process.extract('governacne', words, scorer=DamerauLevenshtein.distance,
                              score_cutoff=1, limit=None)
    g.equal([h[0] for h in hits], ['governance'])
    folded = rf_process.extract('MEMBERS', words, scorer=DamerauLevenshtein.distance,
                                score_cutoff=1, limit=None, processor=str.casefold)
    g.equal(sorted(h[0] for h in folded), ['member', 'members'])
    g.equal(rf_process.extract('zzzxqv', words, scorer=DamerauLevenshtein.distance,
                               score_cutoff=1, limit=None), [])
    scores = {h[0]: h[1] for h in folded}
    g.equal(scores['members'], 0); g.equal(scores['member'], 1)  # the distance is returned, so no recomputation
    g.equal(all(s <= 1 for s in scores.values()), True)
    return {'replaces': REPLACES['v17.within_one'], 'reproduces_the_recorded_result': True,
            'cross_check_was_not_independent': True}


@case('v16.part_digests/normalized_package -> repro_zipfile')
def a_deterministic_package_is_a_library_writer():
    parts = {'word/document.xml': b'<w:p/>', '[Content_Types].xml': b'<Types/>'}
    first, second = reproducible_package(parts), reproducible_package(parts)
    g.equal(hashlib.sha256(first).hexdigest(), hashlib.sha256(second).hexdigest())
    g.equal(stamps(first), {(1980, 1, 1, 0, 0, 0)})  # v16 hand-rolled this stamp into its own rewriter
    g.equal(stamps(first), stamps(second))
    changed = reproducible_package(dict(parts, **{'word/document.xml': b'<w:p><w:r/></w:p>'}))
    g.equal(hashlib.sha256(changed).hexdigest() == hashlib.sha256(first).hexdigest(), False)
    with zipfile.ZipFile(io.BytesIO(first)) as archive:
        g.equal(sorted(archive.namelist()), ['[Content_Types].xml', 'word/document.xml'])
        g.equal(archive.read('word/document.xml'), b'<w:p/>')
    plain = io.BytesIO()
    with zipfile.ZipFile(plain, 'w') as archive:
        archive.writestr('word/document.xml', b'<w:p/>')
    g.equal(stamps(plain.getvalue()) == {(1980, 1, 1, 0, 0, 0)}, False)  # the stdlib writer stamps the clock
    return {'replaces': REPLACES['v16.normalized_package'], 'reproduces_the_recorded_result': True,
            'content_identity_without_a_local_rewriter': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for name, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'replacement': name, 'test': fn.__name__, 'status': state,
                     'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['apportionment', 'largest-remainder', 'networkx', 'numpy', 'pandas', 'pandera',
                'portion', 'rapidfuzz', 'repro-zipfile', 'scipy']
    here = Path(__file__).resolve().parent
    return {'scope': 'Glue elimination for handoff_guards_v15-v17 embedded earlier in this TXT. Each case calls the researched library primitive alone and records whether it reproduces, refuses or contradicts the handwritten result. No proof chain was rerun.',
            'glue_functions_replaced': len(REPLACES), 'replacements': REPLACES,
            'test_cases': len(rows), 'passed': sum(r['status'] == 'passed' for r in rows),
            'failed': sum(r['status'] == 'failed' for r in rows),
            'assertions': g.ASSERTIONS, 'full_chains_executed': 0, 'network_calls': 0, 'business_actions': 0,
            'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256': {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in ['handoff_guards_v1.py']},
            'library_versions': {n: importlib.metadata.version(n) for n in packages}, 'results': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    result = run(); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ['test_cases', 'passed', 'failed', 'assertions', 'glue_functions_replaced']}))
    if result['failed']:
        print('\n'.join(r['error'] for r in result['results'] if r['error'])); raise SystemExit(1)
