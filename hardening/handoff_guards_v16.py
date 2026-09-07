"""Sixteenth bounded adapter suite: P151-P160, document templating, purchasing, stock, reconciliation, ledger,
billing, depreciation, pipeline, risk and material handoffs. Requires handoff_guards_v1.py from this TXT. Every
template render, join, cumulative aggregation, graph operation, journal load, decimal rounding, calendar step,
binning and path expansion below is a library primitive call; local code declares fixtures and policies and turns a
primitive result into a Blocked outcome. All runtime inputs are authored fixtures. No model client and no network.
Run: python handoff_guards_v16.py --report report.json
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, io, json, logging, math, traceback, warnings, zipfile
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
from fractions import Fraction
from pathlib import Path
import beancount
import docxtpl
import networkx as nx
import numpy as np
import pandas as pd
import pymupdf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from beancount import loader
from beancount.core import data as bc_data, realization
from dateutil.relativedelta import relativedelta
from docx import Document
from jinja2 import Environment, StrictUndefined, UndefinedError
import handoff_guards_v1 as g
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

CENT = Decimal('0.01')

# ---------------------------------------------------------------- P151
def meeting_template() -> bytes:
    """One authored DOCX carrying Jinja placeholders in a paragraph and in a fixed 1x2 table."""
    d = Document()
    d.add_paragraph('Meeting: {{ meeting_id }}')
    d.add_paragraph('Topic: {{ topic }}')
    t = d.add_table(rows=1, cols=2)
    t.cell(0, 0).text = '{{ flag }}'
    t.cell(0, 1).text = '{{ count }}'
    buf = io.BytesIO(); d.save(buf); return buf.getvalue()


def bind(template: bytes, context: dict, *, escaping: str) -> bytes:
    """escaping='argument' passes render(autoescape=True); 'environment' sets it on the Environment;
    'strict_only' passes a StrictUndefined Environment and relies on docxtpl's default, which is autoescape=False;
    'default' calls render(context) with no environment at all."""
    doc = docxtpl.DocxTemplate(io.BytesIO(template))
    if escaping == 'argument':
        doc.render(context, jinja_env=Environment(undefined=StrictUndefined), autoescape=True)
    elif escaping == 'environment':
        doc.render(context, jinja_env=Environment(undefined=StrictUndefined, autoescape=True))
    elif escaping == 'strict_only':
        doc.render(context, jinja_env=Environment(undefined=StrictUndefined))
    elif escaping == 'default':
        doc.render(context)
    else:
        raise g.Blocked('unknown escaping mode %r' % escaping)
    buf = io.BytesIO(); doc.save(buf); return buf.getvalue()


def read_back(document: bytes) -> dict:
    d = Document(io.BytesIO(document))
    return {'paragraphs': [p.text for p in d.paragraphs],
            'cells': [c.text for row in d.tables[0].rows for c in row.cells]}


def part_digests(document: bytes) -> dict:
    """Content-address the package parts, ignoring the container's own metadata."""
    with zipfile.ZipFile(io.BytesIO(document)) as archive:
        return {name: hashlib.sha256(archive.read(name)).hexdigest() for name in sorted(archive.namelist())}


def stamp_dates(document: bytes) -> set:
    with zipfile.ZipFile(io.BytesIO(document)) as archive:
        return {info.date_time[:3] for info in archive.infolist()}


def normalized_package(document: bytes) -> bytes:
    """Rewrite the container with a fixed stamp so the bytes depend only on the parts."""
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(document)) as archive:
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as fixed:
            for name in sorted(archive.namelist()):
                fixed.writestr(zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)), archive.read(name))
    return out.getvalue()


def placed_text(fragments: list[tuple[float, float, str]], *, sort: bool) -> list[str]:
    """Write text fragments into a PDF in list order and read them back with PyMuPDF."""
    doc = pymupdf.open(); page = doc.new_page()
    for x, y, text in fragments:
        page.insert_text((x, y), text)
    reread = pymupdf.open('pdf', doc.tobytes())[0]
    return [line for line in reread.get_text(sort=sort).splitlines() if line.strip()]


# ---------------------------------------------------------------- P152
def match_invoices(invoices: pd.DataFrame, orders: pd.DataFrame, *, how: str) -> pd.DataFrame:
    """The chain's cited call is merge(validate='many_to_one', indicator=True); how is made explicit here."""
    return invoices.merge(orders, on='order_line', how=how, validate='many_to_one', indicator=True)


def cumulative_billed(invoices: pd.DataFrame) -> dict:
    return {k: v for k, v in invoices.groupby('order_line')['qty'].sum().items()}


def decimal_totals(rows: list[dict], *, key: str) -> dict:
    frame = pd.DataFrame(rows)
    return {k: v for k, v in frame.groupby(key)['amount'].sum().items()}


def within_tolerance(ordered: Decimal, billed: Decimal, tolerance: Decimal) -> bool:
    return abs(ordered - billed) <= tolerance


# ---------------------------------------------------------------- P153
def running_stock(events: list[dict], *, order_by: str | None) -> list:
    frame = pd.DataFrame(events)
    if order_by is not None:
        frame = frame.sort_values(order_by)
    return list(frame.groupby('item')['qty'].cumsum())


def tie_order(rows: list[dict], *, kind: str) -> list[int]:
    frame = pd.DataFrame(rows)
    return list(frame.sort_values('date', kind=kind)['seq'])


def unique_receipts(references: list[dict], *, checked: bool) -> list[dict]:
    """checked=True refuses references that share an ID but disagree on payload."""
    frame = pd.DataFrame(references)
    if checked:
        conflicts = frame.groupby('receipt_id')['qty'].nunique()
        bad = sorted(conflicts[conflicts > 1].index)
        if bad:
            raise g.Blocked('receipt references disagree on quantity: %s' % ', '.join(bad))
    return frame.drop_duplicates(subset=['receipt_id']).to_dict('records')


# ---------------------------------------------------------------- P154
def candidate_graph(edges: list[tuple[str, str]]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_edges_from(edges)
    return graph


def components(graph: nx.Graph) -> list[list[str]]:
    return sorted(sorted(component) for component in nx.connected_components(graph))


def normalized_keys(refs: list[str | None]) -> list:
    return list(pd.Series(refs, dtype='object').str.strip().str.casefold())


def candidate_pairs(book: list[dict], bank: list[dict], *, drop_blank: bool) -> list[tuple[str, str]]:
    left = pd.DataFrame(book); right = pd.DataFrame(bank)
    for frame in (left, right):
        frame['key'] = frame['ref'].str.strip().str.casefold()
    left = left.dropna(subset=['key']); right = right.dropna(subset=['key'])
    if drop_blank:
        left = left[left['key'] != '']; right = right[right['key'] != '']
    joined = left.merge(right, on='key', suffixes=('_book', '_bank'))
    return [(r['id_book'], r['id_bank']) for r in joined.to_dict('records')]


# ---------------------------------------------------------------- P155
JOURNAL = """
2026-01-01 open Assets:Bank
2026-01-01 open Assets:Idle
2026-01-01 open Equity:Opening-Balances
2026-01-05 * "opening"
  Assets:Bank              100.00 USD
  Equity:Opening-Balances -100.00 USD
"""


def load_journal(text: str, *, checked: bool):
    entries, errors, options = loader.load_string(text)
    if checked and errors:
        raise g.Blocked('journal reported %d error(s): %s' % (len(errors), type(errors[0]).__name__))
    return entries, errors


def assertion_errors(asserted: str) -> list[str]:
    text = JOURNAL + '2026-01-06 balance Assets:Bank  %s\n' % asserted
    entries, errors, options = loader.load_string(text)
    return [type(e).__name__ for e in errors]


def interpolated_postings(text: str) -> list[tuple[str, str]]:
    entries, errors, options = loader.load_string(text)
    txns = [e for e in entries if isinstance(e, bc_data.Transaction)]
    return [(p.account, str(p.units)) for p in txns[-1].postings]


def account_node(entries, account: str):
    return realization.get(realization.realize(entries), account)


# ---------------------------------------------------------------- P156
def money(value: str) -> Decimal:
    return Decimal(value)


def round_cents(value: Decimal, *, mode) -> Decimal:
    return value.quantize(CENT, rounding=mode)


def billed(minutes: int, hourly: str, *, granularity: str, mode=ROUND_HALF_UP) -> Decimal:
    """granularity='entry' rounds each entry before aggregation; 'group' rounds the aggregate."""
    exact = Decimal(hourly) * Decimal(minutes) / Decimal(60)
    if granularity == 'entry':
        return round_cents(exact, mode=mode)
    if granularity == 'group':
        return exact
    raise g.Blocked('unknown granularity %r' % granularity)


def parse_stamp(text: str, *, require_offset: bool) -> datetime:
    stamp = datetime.fromisoformat(text)
    if require_offset and stamp.tzinfo is None:
        raise g.Blocked('timestamp carries no UTC offset: %r' % text)
    return stamp


def overlaps(first: tuple[datetime, datetime], second: tuple[datetime, datetime], *, closed: bool) -> bool:
    return first[1] >= second[0] if closed else first[1] > second[0]


# ---------------------------------------------------------------- P157
def month_walk(start: date, count: int, *, method: str) -> list[date]:
    """method='step' adds one month at a time; 'offset' adds n months to the anchor."""
    if method == 'step':
        out = [start]
        for _ in range(count - 1):
            out.append(out[-1] + relativedelta(months=1))
        return out
    if method == 'offset':
        return [start + relativedelta(months=n) for n in range(count)]
    raise g.Blocked('unknown month walk %r' % method)


def schedule_periods(anchor: str, count: int) -> list[str]:
    return [str(p) for p in pd.period_range(anchor, periods=count, freq='M')]


def period_end(period: str):
    return pd.Period(period, freq='M').end_time


def straight_line(cost: str, residual: str, months: int, *, force_remainder: bool) -> list[Decimal]:
    base = Decimal(cost) - Decimal(residual)
    if months <= 0:
        raise g.Blocked('useful life must be positive')
    each = round_cents(base / months, mode=ROUND_HALF_UP)
    charges = [each] * months
    if force_remainder:
        charges[-1] = base - each * (months - 1)
    return charges


def annual_rollup(rows: list[dict], *, min_count: int) -> dict:
    frame = pd.DataFrame(rows)
    grouped = frame.groupby(['asset', 'year'])['charge'].sum(min_count=min_count)
    return {'%s/%s' % k: v for k, v in grouped.items()}


# ---------------------------------------------------------------- P158
STAGES = ['Qualify', 'Propose', 'Negotiate', 'Won', 'Lost']


def staged(rows: list[dict], *, checked: bool) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    coded = pd.Categorical(frame['stage'], categories=STAGES, ordered=True)
    if checked:
        unmapped = sorted({s for s, c in zip(frame['stage'], coded) if pd.isna(c)})
        if unmapped:
            raise g.Blocked('stage labels outside the declared catalog: %s' % ', '.join(unmapped))
    frame['coded'] = coded
    return frame


def stage_totals(frame: pd.DataFrame, *, observed: bool) -> dict:
    return {str(k): float(v) for k, v in frame.groupby('coded', observed=observed)['amt'].sum().items()}


def bar_labels(values: list[float], fmt: str | None) -> tuple[list[str], list[float]]:
    figure, axes = plt.subplots()
    bars = axes.barh([str(i) for i in range(len(values))], values)
    labels = axes.bar_label(bars) if fmt is None else axes.bar_label(bars, fmt=fmt)
    widths = [float(b.get_width()) for b in bars]
    texts = [t.get_text() for t in labels]
    plt.close(figure)
    return texts, widths


# ---------------------------------------------------------------- P159
def score_bands(scores: list[int], edges: list[int], *, right: bool, include_lowest: bool) -> list[str]:
    banded = pd.cut(pd.Series(scores), bins=edges, right=right, include_lowest=include_lowest)
    return [str(b) for b in banded]


def matrix_counts(likelihood: list, impact: list, *, edges) -> np.ndarray:
    counted, _, _ = np.histogram2d(likelihood, impact, bins=[edges, edges])
    return counted


def assessed(rows: list[dict], *, checked: bool) -> tuple[list, list]:
    levels = set(range(1, 6))
    likelihood = [r['likelihood'] for r in rows]
    impact = [r['impact'] for r in rows]
    if checked:
        outside = sorted({v for v in likelihood + impact if v is not None and v not in levels})
        if outside:
            raise g.Blocked('ordinal values outside the declared 1-5 scale: %s' % outside)
    return ([np.nan if v is None else v for v in likelihood],
            [np.nan if v is None else v for v in impact])


def matrix_origin(origin: str) -> tuple[float, float]:
    figure, axes = plt.subplots()
    axes.imshow(np.zeros((5, 5)), origin=origin)
    limits = tuple(float(v) for v in axes.get_ylim())
    plt.close(figure)
    return limits


# ---------------------------------------------------------------- P160
def bom_graph(edges: list[dict], *, checked: bool) -> nx.DiGraph:
    if checked:
        pairs = [(e['parent'], e['child']) for e in edges]
        if len(set(pairs)) != len(pairs):
            raise g.Blocked('duplicate bill-of-materials edge')
    graph = nx.DiGraph()
    for e in edges:
        graph.add_edge(e['parent'], e['child'], qty=e['qty'])
    return graph


def acyclic(graph: nx.DiGraph, *, method: str) -> bool:
    """method='predicate' calls is_directed_acyclic_graph; 'generator' only builds the topological_sort iterator;
    'consumed' exhausts it, which is where NetworkXUnfeasible is raised."""
    if method == 'predicate':
        return nx.is_directed_acyclic_graph(graph)
    if method == 'generator':
        nx.topological_sort(graph)
        return True
    if method == 'consumed':
        list(nx.topological_sort(graph))
        return True
    raise g.Blocked('unknown acyclicity method %r' % method)


def path_quantity(graph: nx.DiGraph, source: str, target: str) -> list[tuple[list[str], int]]:
    out = []
    for path in nx.all_simple_paths(graph, source, target):
        out.append((path, math.prod(graph.edges[path[i], path[i + 1]]['qty'] for i in range(len(path) - 1))))
    return out


def gross_requirement(graph: nx.DiGraph, source: str, target: str, demand: int, *, checked: bool) -> int:
    if checked and source == target:
        raise g.Blocked('an item cannot be its own requirement')
    return demand * sum(q for _, q in path_quantity(graph, source, target))


C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(151)
def template_binding_escapes_nothing_by_default():
    template = meeting_template()
    literal = 'A & B < 5 > 2'
    context = {'meeting_id': 'tsc-2024-01-17', 'topic': literal, 'flag': 'reachable', 'count': '3'}
    plain = read_back(bind(template, context, escaping='default'))
    g.equal(plain['paragraphs'][1], 'Topic: A  B  5 > 2')  # the & and < fragments are gone
    g.equal(literal in plain['paragraphs'][1], False)
    g.equal(plain['paragraphs'][0], 'Meeting: tsc-2024-01-17')  # the document still opens and reads clean
    strict = read_back(bind(template, context, escaping='strict_only'))
    g.equal(strict['paragraphs'][1], 'Topic: A  B  5 > 2')  # a StrictUndefined environment does not turn escaping on
    g.equal(Environment(undefined=StrictUndefined).autoescape, False)
    for mode in ('argument', 'environment'):
        kept = read_back(bind(template, context, escaping=mode))
        g.equal(kept['paragraphs'][1], 'Topic: ' + literal)
        g.equal(kept['cells'], ['reachable', '3'])
    g.rejects(UndefinedError, lambda: bind(template, {'meeting_id': 'm', 'topic': 't', 'flag': 'f'}, escaping='environment'))
    silent = read_back(bind(template, {'meeting_id': 'm', 'topic': 't', 'flag': 'f'}, escaping='default'))
    g.equal(silent['cells'], ['f', ''])  # the default Undefined renders a missing variable as an empty cell
    first = bind(template, dict(context, meeting_id='tsc-2023-11-08'), escaping='environment')
    second = bind(template, dict(context, meeting_id='tsc-2025-03-05'), escaping='environment')
    g.equal(read_back(first)['paragraphs'][0], 'Meeting: tsc-2023-11-08')
    g.equal(read_back(second)['paragraphs'][0], 'Meeting: tsc-2025-03-05')
    first = io.BytesIO(); Document(io.BytesIO(template)).save(first)
    second = io.BytesIO(); Document(io.BytesIO(template)).save(second)
    g.equal(part_digests(first.getvalue()), part_digests(template))  # every part is byte-identical
    g.equal(part_digests(second.getvalue()), part_digests(template))
    stamped = stamp_dates(first.getvalue())
    g.equal(len(stamped), 1); g.equal(stamped, stamp_dates(second.getvalue()))
    g.equal((1980, 1, 1) in stamped, False)  # the container carries a clock reading, not a fixed epoch
    g.equal(date(*next(iter(stamped))) >= date(2026, 1, 1), True)
    g.equal(normalized_package(first.getvalue()), normalized_package(second.getvalue()))
    g.equal(hashlib.sha256(normalized_package(first.getvalue())).hexdigest(),
            hashlib.sha256(normalized_package(template)).hexdigest())
    g.rejects(g.Blocked, lambda: bind(template, context, escaping='none'))
    fragments = [(72.0, 500.0, 'Third paragraph'), (72.0, 100.0, 'First paragraph'), (72.0, 300.0, 'Second paragraph')]
    g.equal(placed_text(fragments, sort=False), ['Third paragraph', 'First paragraph', 'Second paragraph'])
    g.equal(placed_text(fragments, sort=True), ['First paragraph', 'Second paragraph', 'Third paragraph'])
    return {'docxtpl_render_autoescape_default': False, 'unescaped_literal_silently_truncated': True,
            'strict_undefined_alone_does_not_escape': True, 'default_undefined_renders_empty': True,
            'save_stamps_the_container_with_the_wall_clock': True, 'pdf_text_default_order_is_insertion_order': True}


@case(152)
def a_checked_join_does_not_retain_unmatched_lines():
    orders = pd.DataFrame({'order_line': ['PO1-1', 'PO1-2', 'PO2-1', 'PO3-1'], 'qty': [3, 1, 2, 5]})
    invoices = pd.DataFrame({'invoice_line': ['I1', 'I2', 'I3', 'I4', 'I5', 'I6'],
                             'order_line': ['PO1-1', 'PO1-1', 'PO1-2', 'PO2-1', 'PO9-1', 'PO3-1'],
                             'qty': [1, 2, 1, 2, 1, 5]})
    inner = match_invoices(invoices, orders, how='inner')
    g.equal(len(inner), 5); g.equal(len(invoices), 6)
    g.equal(sorted(inner['_merge'].astype(str).unique()), ['both'])  # the indicator is a constant on an inner join
    g.equal('I5' in set(inner['invoice_line']), False)  # the unmatched order ID is gone, unflagged
    outer = match_invoices(invoices, orders, how='outer')
    g.equal(int((outer['_merge'] == 'left_only').sum()), 1)
    g.equal(sorted(outer[outer['_merge'] == 'left_only']['invoice_line']), ['I5'])
    duplicated = pd.concat([orders, orders.iloc[[0]]])
    g.rejects(pd.errors.MergeError, lambda: match_invoices(invoices, duplicated, how='inner'))
    g.rejects(ValueError, lambda: match_invoices(invoices.assign(_merge='x'), orders, how='outer'))
    g.equal(cumulative_billed(invoices)['PO1-1'], 3)  # both invoices against one order line accumulate
    g.equal(cumulative_billed(invoices)['PO1-1'] > int(orders.set_index('order_line').loc['PO1-1', 'qty']), False)
    rows = [{'k': 'a', 'amount': Decimal('10.00')}, {'k': 'a', 'amount': None}, {'k': 'b', 'amount': Decimal('5.50')}]
    g.equal(decimal_totals(rows, key='k')['a'], Decimal('10.00'))  # the missing amount is dropped, not raised
    g.equal(decimal_totals(rows, key='k')['b'], Decimal('5.50'))
    empty = pd.DataFrame({'k': [], 'amount': []})['amount'].sum()
    g.equal(empty, 0); g.equal(type(empty).__name__ in ('int', 'float64'), True)  # not Decimal('0.00')
    g.equal(within_tolerance(Decimal('10.00'), Decimal('10.25'), Decimal('0.25')), True)
    g.equal(within_tolerance(Decimal('10.00'), Decimal('9.75'), Decimal('0.25')), True)
    g.equal(within_tolerance(Decimal('10.00'), Decimal('10.26'), Decimal('0.25')), False)
    g.equal(Decimal('0.25') == 0.25, True); g.equal(Decimal('0.1') == 0.1, False)
    return {'indicator_on_an_inner_join_is_constant': True, 'unmatched_left_rows_dropped': 1,
            'validate_many_to_one_checks_the_right_side_only': True,
            'decimal_group_sum_drops_nulls': True, 'empty_sum_returns_int_zero': True}


@case(153)
def a_running_balance_follows_row_order_not_the_posting_contract():
    events = [{'item': 'desk', 'date': '2026-03-01', 'qty': 5},
              {'item': 'desk', 'date': '2026-01-01', 'qty': -2},
              {'item': 'desk', 'date': '2026-02-01', 'qty': -4}]
    unsorted_run = running_stock(events, order_by=None)
    sorted_run = running_stock(events, order_by='date')
    g.equal(unsorted_run, [5, 3, -1]); g.equal(sorted_run, [-2, -6, -1])
    g.equal(unsorted_run[-1], sorted_run[-1])  # the closing balance agrees
    g.equal(min(unsorted_run) < 0, True); g.equal(min(sorted_run) < 0, True)
    g.equal(any(v < -4 for v in unsorted_run), False)  # the unsorted run never reaches -6
    g.equal(any(v < -4 for v in sorted_run), True)  # so a negative-stock rejection depends on a sort the primitive omits
    gapped = [{'item': 'desk', 'date': '2026-01-01', 'qty': 5.0},
              {'item': 'desk', 'date': '2026-02-01', 'qty': float('nan')},
              {'item': 'desk', 'date': '2026-03-01', 'qty': -4.0}]
    run = running_stock(gapped, order_by='date')
    g.equal(math.isnan(run[1]), True); g.equal(run[2], 1.0)  # the balance resumes as if the gap were zero
    tied = [{'date': '2026-01-05' if i < 20 else '2026-01-06', 'seq': i} for i in range(40)]
    shuffled = [tied[i] for i in (list(range(19, -1, -1)) + list(range(20, 40)))]
    g.equal(tie_order(shuffled, kind='stable') == [r['seq'] for r in shuffled], True)
    g.equal(tie_order(shuffled, kind='quicksort') == tie_order(shuffled, kind='stable'), False)
    g.equal(sorted(tie_order(shuffled, kind='quicksort')), sorted(tie_order(shuffled, kind='stable')))
    references = [{'receipt_id': 'R1', 'qty': 2}, {'receipt_id': 'R1', 'qty': 7}, {'receipt_id': 'R2', 'qty': 1}]
    loose = unique_receipts(references, checked=False)
    g.equal(len(loose), 2); g.equal([r['qty'] for r in loose], [2, 1])  # quantity 7 is discarded without a signal
    g.rejects(g.Blocked, lambda: unique_receipts(references, checked=True))
    agreeing = [{'receipt_id': 'R1', 'qty': 2}, {'receipt_id': 'R1', 'qty': 2}, {'receipt_id': 'R2', 'qty': 1}]
    g.equal(len(unique_receipts(agreeing, checked=True)), 2)
    return {'grouped_cumsum_uses_row_order': True, 'sort_values_default_is_not_stable': True,
            'grouped_cumsum_skips_nulls': True, 'drop_duplicates_hides_conflicting_payloads': True}


@case(154)
def one_shared_identifier_collapses_two_sides_of_the_match():
    collided = candidate_graph([('B01', 'K01'), ('B02', 'B01')])  # a bank row happens to be named B01
    g.equal(sorted(collided.nodes()), ['B01', 'B02', 'K01'])  # three nodes for four rows
    g.equal(nx.is_bipartite(collided), True)  # the collision does not disturb bipartiteness
    g.equal(components(collided), [['B01', 'B02', 'K01']])  # one component of three, so nothing is selected
    prefixed = candidate_graph([('book:B01', 'bank:K01'), ('book:B02', 'bank:K01')])
    g.equal(nx.is_bipartite(prefixed), True)
    g.equal(len(components(prefixed)[0]), 3)
    same_side = prefixed.copy(); same_side.add_edge('book:B01', 'book:B02')
    g.equal(nx.is_bipartite(same_side), False)  # is_bipartite only reacts to an edge the builder never emits
    g.equal(isinstance(next(iter(nx.connected_components(prefixed))), set), True)
    g.equal([n for n in prefixed if prefixed.degree(n) == 0], [])  # unresolved rows never enter the graph
    g.equal('STRASSE'.casefold() == 'straße'.casefold(), True)
    g.equal('STRASSE'.lower() == 'straße'.lower(), False)  # casefold merges keys that lower keeps apart
    keys = normalized_keys(['INV-1', '  ', None])
    g.equal(keys[0], 'inv-1'); g.equal(keys[1], ''); g.equal(keys[2] is None, True)
    book = [{'id': 'B1', 'ref': 'INV-1'}, {'id': 'B2', 'ref': '  '}, {'id': 'B3', 'ref': None}]
    bank = [{'id': 'K1', 'ref': 'inv-1'}, {'id': 'K2', 'ref': ''}, {'id': 'K3', 'ref': None}]
    loose = candidate_pairs(book, bank, drop_blank=False)
    g.equal(sorted(loose), [('B1', 'K1'), ('B2', 'K2')])  # a whitespace-only reference matched an empty one
    tight = candidate_pairs(book, bank, drop_blank=True)
    g.equal(sorted(tight), [('B1', 'K1')])
    return {'identifier_collision_merges_nodes': True, 'is_bipartite_is_true_by_construction': True,
            'components_are_unordered_sets': True, 'blank_keys_survive_dropna_and_match': True,
            'casefold_merges_sharp_s': True}


@case(155)
def a_journal_loader_reports_errors_it_does_not_raise():
    entries, errors = load_journal(JOURNAL, checked=True)
    g.equal(len(errors), 0)
    unbalanced = JOURNAL.replace('-100.00 USD', '-99.99 USD')
    entries, errors = load_journal(unbalanced, checked=False)
    g.equal(len(errors), 1)  # returned in a list, never raised
    g.equal(any(isinstance(e, bc_data.Transaction) for e in entries), True)  # the bad transaction is still handed on
    g.rejects(g.Blocked, lambda: load_journal(unbalanced, checked=True))
    missing = JOURNAL.replace('  Equity:Opening-Balances -100.00 USD', '  Equity:Opening-Balances')
    entries, errors = load_journal(missing, checked=True)
    g.equal(len(errors), 0)  # a missing amount is interpolated, not rejected
    g.equal(interpolated_postings(missing), [('Assets:Bank', '100.00 USD'), ('Equity:Opening-Balances', '-100.00 USD')])
    g.equal(assertion_errors('100.00 USD'), [])
    g.equal(assertion_errors('100.01 USD'), [])  # one cent wrong and the loader is silent
    g.equal(assertion_errors('100.010 USD'), ['BalanceError'])  # the same number, one more decimal digit, rejected
    g.equal(assertion_errors('100.005 USD'), ['BalanceError'])
    g.equal(assertion_errors('100.10 USD'), ['BalanceError'])
    g.equal(Decimal('100.01') == Decimal('100.010'), True)  # the two assertions are numerically identical
    entries, errors = load_journal(JOURNAL, checked=True)
    bank = account_node(entries, 'Assets:Bank')
    idle = account_node(entries, 'Assets:Idle')
    g.equal(bank is not None, True); g.equal(idle is not None, True)
    g.equal(account_node(entries, 'Assets:Nope') is None, True)
    g.equal(str(bank.balance.get_currency_units('USD')), '100.00 USD')
    g.equal(bool(bank), False)  # RealAccount is a dict of children, so a posting-bearing leaf is falsy
    g.equal(bool(account_node(entries, 'Assets')), True)  # while an empty parent is truthy
    g.equal(str(account_node(entries, 'Assets').balance.get_currency_units('USD')), '0 USD')
    return {'load_string_returns_errors_without_raising': True, 'missing_amount_is_interpolated': True,
            'one_cent_assertion_accepted_at_two_decimals': True, 'trailing_zero_changes_the_tolerance': True,
            'leaf_realaccount_is_falsy': True}


@case(156)
def rounding_mode_and_granularity_each_move_the_cent():
    g.equal(round_cents(Decimal('1.005'), mode=ROUND_HALF_EVEN), Decimal('1.00'))
    g.equal(round_cents(Decimal('1.005'), mode=ROUND_HALF_UP), Decimal('1.01'))
    g.equal(round_cents(Decimal('0.125'), mode=ROUND_HALF_EVEN), Decimal('0.12'))
    g.equal(round_cents(Decimal('0.125'), mode=ROUND_HALF_UP), Decimal('0.13'))
    g.equal(round_cents(Decimal('1.665'), mode=ROUND_HALF_EVEN), Decimal('1.66'))
    g.equal(round_cents(Decimal('1.665'), mode=ROUND_HALF_UP), Decimal('1.67'))
    g.equal(round_cents(Decimal(1.665), mode=ROUND_HALF_UP), Decimal('1.67'))
    g.equal(str(Decimal(1.005))[:6], '1.0049')  # a float source rounds down under either mode
    g.equal(round_cents(Decimal(1.005), mode=ROUND_HALF_UP), Decimal('1.00'))
    per_entry = billed(1, '100.00', granularity='entry') + billed(1, '100.00', granularity='entry')
    per_group = round_cents(billed(2, '100.00', granularity='group'), mode=ROUND_HALF_UP)
    g.equal(per_entry, Decimal('3.34')); g.equal(per_group, Decimal('3.33'))
    g.equal(per_entry - per_group, Decimal('0.01'))
    g.equal(Fraction(100) * Fraction(2, 60), Fraction(10, 3))  # neither figure is the exact amount
    g.rejects(g.Blocked, lambda: billed(1, '100.00', granularity='hour'))
    for naive in ('2026-09-07T09:00:00', '20260907T090000', '2026-09-07 09:00:00', '2026-09-07'):
        g.equal(parse_stamp(naive, require_offset=False).tzinfo is None, True)
        g.rejects(g.Blocked, lambda s=naive: parse_stamp(s, require_offset=True))
    g.equal(parse_stamp('2026-09-07T09:00:00Z', require_offset=True).tzinfo, timezone.utc)
    g.equal(parse_stamp('2026-09-07T09:00:00+00:00:00', require_offset=True).tzinfo, timezone.utc)
    g.equal(parse_stamp('2026-09-07T09:00:00.123456789', require_offset=False).microsecond, 123456)  # truncated
    first = (parse_stamp('2026-09-07T09:00:00Z', require_offset=True), parse_stamp('2026-09-07T10:00:00Z', require_offset=True))
    second = (parse_stamp('2026-09-07T10:00:00Z', require_offset=True), parse_stamp('2026-09-07T11:00:00Z', require_offset=True))
    g.equal(overlaps(first, second, closed=False), False)
    g.equal(overlaps(first, second, closed=True), True)  # back-to-back entries are legal or not by the chosen predicate
    overnight = (parse_stamp('2026-09-07T23:30:00Z', require_offset=True), parse_stamp('2026-09-08T01:00:00Z', require_offset=True))
    g.equal(int((overnight[1] - overnight[0]).total_seconds() // 60), 90)
    return {'default_decimal_rounding_is_half_even': True, 'float_source_defeats_half_up': True,
            'per_entry_and_per_group_differ_by_one_cent': True, 'fromisoformat_accepts_naive_input': True,
            'subsecond_precision_truncated': True, 'touching_intervals_need_a_declared_predicate': True}


@case(157)
def stepping_a_month_at_a_time_drifts_off_the_month_end():
    anchor = date(2026, 1, 31)
    g.equal(month_walk(anchor, 3, method='step'), [date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 28)])
    g.equal(month_walk(anchor, 3, method='offset'), [date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31)])
    g.equal(month_walk(anchor, 3, method='step') == month_walk(anchor, 3, method='offset'), False)
    g.equal(anchor + relativedelta(months=1) - relativedelta(months=1), date(2026, 1, 28))  # not a round trip
    g.rejects(g.Blocked, lambda: month_walk(anchor, 3, method='calendar'))
    g.equal(schedule_periods('2026-01', 3), ['2026-01', '2026-02', '2026-03'])
    g.equal(str(period_end('2026-02')), '2026-02-28 23:59:59.999999999')
    g.equal(period_end('2026-02') == pd.Timestamp('2026-02-28'), False)  # a month end never equals its own date
    g.equal(period_end('2026-02').date(), date(2026, 2, 28))
    g.equal([str(d.date()) for d in pd.date_range('2026-01-15', periods=3, freq='ME')],
            ['2026-01-31', '2026-02-28', '2026-03-31'])  # the declared first period date is snapped away
    naive = straight_line('100.00', '0.00', 3, force_remainder=False)
    forced = straight_line('100.00', '0.00', 3, force_remainder=True)
    g.equal(naive, [Decimal('33.33')] * 3); g.equal(sum(naive), Decimal('99.99'))
    g.equal(forced, [Decimal('33.33'), Decimal('33.33'), Decimal('33.34')]); g.equal(sum(forced), Decimal('100.00'))
    g.rejects(g.Blocked, lambda: straight_line('100.00', '0.00', 0, force_remainder=True))
    rows = [{'asset': 'A1', 'year': 2026, 'charge': Decimal('33.33')},
            {'asset': 'A1', 'year': 2027, 'charge': Decimal('66.67')},
            {'asset': 'A2', 'year': 2026, 'charge': None}]
    g.equal(annual_rollup(rows, min_count=0)['A2/2026'], 0)  # the unresolved life rolls up as a hard zero
    g.equal(pd.isna(annual_rollup(rows, min_count=1)['A2/2026']), True)  # min_count=1 keeps it unknown
    g.equal(annual_rollup(rows, min_count=1)['A1/2027'], Decimal('66.67'))
    return {'relativedelta_month_steps_are_not_associative': True, 'period_end_time_is_not_a_date': True,
            'month_end_frequency_snaps_the_anchor': True, 'naive_split_underallocates_one_cent': True,
            'null_charge_sums_to_zero_by_default': True}


@case(158)
def an_unmapped_stage_label_leaves_the_totals_looking_consistent():
    rows = [{'stage': 'Qualify', 'amt': 1000.0}, {'stage': 'Propose', 'amt': 15500.0},
            {'stage': 'Propose', 'amt': 4500.0}, {'stage': 'Negotiate', 'amt': 250.0},
            {'stage': 'Qualifyy', 'amt': 3000.0}]
    frame = staged(rows, checked=False)
    g.equal(int(frame['coded'].isna().sum()), 1)  # the typo became NaN with no error
    observed = stage_totals(frame, observed=True)
    declared = stage_totals(frame, observed=False)
    g.equal(sorted(observed), ['Negotiate', 'Propose', 'Qualify'])
    g.equal(sorted(declared), ['Lost', 'Negotiate', 'Propose', 'Qualify', 'Won'])
    g.equal(len(observed), 3); g.equal(len(declared), 5)  # three bars or five, from one frame
    g.equal(declared['Won'], 0.0); g.equal(declared['Lost'], 0.0)  # stages with no opportunity read as measured zeros
    g.equal(sum(observed.values()), 21250.0)
    g.equal(sum(declared.values()), 21250.0)
    g.equal(float(pd.DataFrame(rows)['amt'].sum()), 24250.0)  # the source total is 3,000.00 higher
    g.equal(sum(observed.values()) == float(pd.DataFrame(rows)['amt'].sum()), False)
    g.rejects(g.Blocked, lambda: staged(rows, checked=True))
    g.equal(int(staged(rows[:4], checked=True)['coded'].isna().sum()), 0)
    texts, widths = bar_labels([15500.0, 4500.0, 250.0, 0.0], None)
    g.equal(texts, ['15500', '4500', '250', '0'])  # the default label drops the cents from a USD amount
    g.equal(widths[3], 0.0); g.equal(len(widths), 4)  # the zero-value bar is drawn with no extent but is still labelled
    cents, _ = bar_labels([15500.0, 4500.0, 250.0, 0.0], '%.2f')
    g.equal(cents, ['15500.00', '4500.00', '250.00', '0.00'])
    return {'unknown_category_becomes_nan_silently': True, 'unmapped_amount': 3000.0,
            'observed_flag_changes_the_bar_count': True, 'empty_categories_read_as_zero': True,
            'bar_label_default_drops_cents': True}


@case(159)
def a_matrix_silently_omits_what_it_cannot_place():
    edges = np.arange(0.5, 6, 1)
    counted = matrix_counts([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], edges=edges)
    g.equal(list(np.diag(counted)), [1.0] * 5); g.equal(counted.sum(), 5.0)
    g.equal(counted.dtype.name, 'float64')  # a count is a float
    outside = matrix_counts([1, 2, 3, 4, 5, 6, 0], [1, 2, 3, 4, 5, 2, 2], edges=edges)
    g.equal(outside.sum(), 5.0)  # seven rows in, five counted, no error and no warning
    with_gap = matrix_counts([1, 2, np.nan], [1, 2, 3], edges=edges)
    g.equal(with_gap.sum(), 2.0)
    g.equal(outside.sum() < 7.0 and with_gap.sum() < 3.0, True)  # unassessed and out-of-scale look identical
    rows = [{'likelihood': 1, 'impact': 2}, {'likelihood': 6, 'impact': 2}]
    g.rejects(g.Blocked, lambda: assessed(rows, checked=True))
    unknown = [{'likelihood': None, 'impact': 2}, {'likelihood': 4, 'impact': 4}]
    likelihood, impact = assessed(unknown, checked=True)
    g.equal(math.isnan(likelihood[0]), True); g.equal(matrix_counts(likelihood, impact, edges=edges).sum(), 1.0)
    bands = [1, 5, 10, 15, 25]
    right_closed = score_bands([1, 5, 6, 15, 16, 25], bands, right=True, include_lowest=False)
    g.equal(right_closed[0], 'nan')  # the lowest declared score falls outside every band
    g.equal(right_closed[1], '(1.0, 5.0]'); g.equal(right_closed[5], '(15.0, 25.0]')
    lowest = score_bands([1, 5, 6, 15, 16, 25], bands, right=True, include_lowest=True)
    g.equal(lowest.count('nan'), 0); g.equal(lowest[0], '(0.999, 5.0]')
    left_closed = score_bands([1, 5, 6, 15, 16, 25], bands, right=False, include_lowest=False)
    g.equal(left_closed.count('nan'), 1); g.equal(left_closed[5], 'nan')  # the loss moves to the top score
    g.equal(left_closed[1], '[5.0, 10.0)')  # and score 5 changes band
    g.equal(right_closed[1] == left_closed[1], False)
    g.equal(list(np.diag(np.outer(np.arange(1, 6), np.arange(1, 6)))), [1, 4, 9, 16, 25])
    g.equal(matrix_origin('upper')[0] > matrix_origin('upper')[1], True)  # row 0 is drawn at the top by default
    g.equal(matrix_origin('lower')[0] < matrix_origin('lower')[1], True)
    return {'histogram2d_drops_out_of_range_rows': True, 'dropped_rows': 2,
            'unassessed_and_out_of_scale_indistinguishable': True,
            'cut_boundary_membership_depends_on_two_defaults': True, 'imshow_origin_default_is_upper': True}


@case(160)
def a_duplicate_bill_of_materials_edge_replaces_the_first():
    edges = [{'parent': 'kit', 'child': 'cable', 'qty': 2}, {'parent': 'kit', 'child': 'cable', 'qty': 3}]
    loose = bom_graph(edges, checked=False)
    g.equal(loose.number_of_edges(), 1)  # two declared edges, one stored
    g.equal(loose['kit']['cable']['qty'], 3)  # the second quantity replaced the first, silently
    g.rejects(g.Blocked, lambda: bom_graph(edges, checked=True))
    declared = [{'parent': 'kit', 'child': 'display', 'qty': 2}, {'parent': 'display', 'child': 'cable', 'qty': 2},
                {'parent': 'kit', 'child': 'cable', 'qty': 2}]
    graph = bom_graph(declared, checked=True)
    g.equal(graph.number_of_edges(), 3)
    paths = path_quantity(graph, 'kit', 'cable')
    g.equal(sorted(len(p) for p, _ in paths), [2, 3])
    g.equal(sorted(q for _, q in paths), [2, 4])  # the nested assembly multiplies along its path
    g.equal(gross_requirement(graph, 'kit', 'cable', 1, checked=True), 6)
    g.equal(gross_requirement(graph, 'kit', 'cable', 2, checked=True), 12)
    cyclic = nx.DiGraph([('a', 'b'), ('b', 'c'), ('c', 'a')])
    g.equal(acyclic(cyclic, method='predicate'), False)
    g.equal(acyclic(cyclic, method='generator'), True)  # building the iterator validates nothing
    g.rejects(nx.NetworkXUnfeasible, lambda: acyclic(cyclic, method='consumed'))
    g.equal(acyclic(graph, method='consumed'), True)
    g.rejects(g.Blocked, lambda: acyclic(graph, method='dfs'))
    self_loop = nx.DiGraph(); self_loop.add_edge('kit', 'kit', qty=1)
    g.equal(acyclic(self_loop, method='predicate'), False)
    g.equal(math.prod([]), 1)  # an empty edge sequence is a quantity, not an error
    g.equal(path_quantity(graph, 'kit', 'kit'), [(['kit'], 1)])  # the trivial path invents one unit of the assembly
    g.equal(gross_requirement(graph, 'kit', 'kit', 4, checked=False), 4)
    g.rejects(g.Blocked, lambda: gross_requirement(graph, 'kit', 'kit', 4, checked=True))
    g.equal(path_quantity(graph, 'kit', 'absent'), [])  # an unknown target is silently empty
    g.rejects(nx.NodeNotFound, lambda: path_quantity(graph, 'absent', 'cable'))  # an unknown source raises
    attributed = nx.DiGraph(); attributed.add_node('cable', kind='part')
    attributed.add_edge('kit', 'cable', qty=1)
    g.equal(attributed.nodes['cable'], {'kind': 'part'})
    g.equal(attributed.nodes['kit'], {})  # the invented parent carries no declared attributes
    return {'duplicate_edge_overwrites_silently': True, 'topological_sort_validates_only_when_consumed': True,
            'empty_product_is_one': True, 'trivial_self_path_invents_a_requirement': True,
            'unknown_source_and_target_fail_differently': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['beancount', 'docxtpl', 'Jinja2', 'matplotlib', 'networkx', 'numpy', 'pandas',
                'PyMuPDF', 'python-dateutil', 'python-docx']
    here = Path(__file__).resolve().parent
    return {'scope': 'Bounded authored document, purchasing, stock, reconciliation, journal, billing, asset, pipeline, risk and material fixtures and reproduced library defaults; the original P151-P160 chains and their artifacts were not rerun.',
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
