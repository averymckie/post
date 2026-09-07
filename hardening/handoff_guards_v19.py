"""Eighteenth bounded adapter suite: P171-P180, leave balances, workforce membership, onboarding dates, requisitions,
pack-aware quotes, installment allocation, packing conservation, amortization, appraisal and roster overlap.
Requires handoff_guards_v1.py from this TXT.

Every meaningful operation below is a library primitive call. Working days are a numpy business-day calendar,
membership is a pandas date_range or Interval with its closure declared, overlap is pandas Interval.overlaps,
conservation and uniqueness are pandera schema constraints, whole-pack rounding is math.ceil over an exact Fraction,
the installment split is largest_remainder, and the loan and appraisal figures are numpy_financial. Local code
declares fixtures and policies and turns a primitive result into a Blocked outcome; it does not reimplement an
operation a library performs. All runtime inputs are authored fixtures. No model client and no network.
Run: python handoff_guards_v19.py --report report.json
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, io, json, logging, math, traceback, warnings
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path
import numpy as np
import numpy_financial as npf
import pandas as pd
import pandera.pandas as pandera
from largest_remainder import LargestRemainder
import handoff_guards_v1 as g
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

CENT = Decimal('0.01')
HOLIDAYS = ['2026-09-07']
CALENDAR = np.busdaycalendar(weekmask='Mon Tue Wed Thu Fri', holidays=HOLIDAYS)


def cents(value) -> Decimal:
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------- P171
def working_days(start: str, finish: str, *, inclusive: bool) -> int:
    end = np.datetime64(finish) + np.timedelta64(1, 'D') if inclusive else np.datetime64(finish)
    return int(np.busday_count(np.datetime64(start), end, busdaycal=CALENDAR))


def working_dates(start: str, finish: str) -> list[str]:
    span = np.arange(np.datetime64(start), np.datetime64(finish) + np.timedelta64(1, 'D'), dtype='datetime64[D]')
    return [str(d) for d in span[np.is_busday(span, busdaycal=CALENDAR)]]


def half_day_slots(dates: list[str]) -> list[tuple[str, str]]:
    return [(day, half) for day in dates for half in ('AM', 'PM')]


def day_totals(rows: list[dict], *, dropna: bool) -> dict:
    frame = pd.DataFrame(rows)
    return {k: v for k, v in frame.groupby('employee', dropna=dropna)['days'].sum().items()}


# ---------------------------------------------------------------- P172
def membership_dates(start: str, finish: str, *, inclusive: str) -> list[str]:
    return [str(d.date()) for d in pd.date_range(start, finish, freq='D', inclusive=inclusive)]


def assignment_interval(start: str, finish: str, *, closed: str) -> pd.Interval:
    return pd.Interval(pd.Timestamp(start), pd.Timestamp(finish), closed=closed)


# ---------------------------------------------------------------- P173
def offset_working_days(anchor: str, days: int, *, roll: str) -> str:
    return str(np.busday_offset(np.datetime64(anchor), days, roll=roll, busdaycal=CALENDAR))


# ---------------------------------------------------------------- P174
def requested_lines(rows: list[dict]) -> list[dict]:
    """A null shortfall stays an exception; only a known positive quantity becomes a request line."""
    out = []
    for row in rows:
        if row['net'] is None:
            out.append({'item': row['item'], 'requested': None, 'state': 'unknown shortfall'})
        elif row['net'] > 0:
            out.append({'item': row['item'], 'requested': row['net'], 'state': 'requested'})
        else:
            out.append({'item': row['item'], 'requested': 0, 'state': 'no shortfall'})
    return out


# ---------------------------------------------------------------- P175
def whole_packs(required: int, pack_size: int) -> tuple[int, int, int]:
    """Exact rational ceiling; no integer-division rounding rule written here."""
    if pack_size <= 0:
        raise g.Blocked('pack size must be positive')
    packs = math.ceil(Fraction(required, pack_size))
    units = packs * pack_size
    return packs, units, units - required


def converted(amount: str, rate: str) -> Decimal:
    return cents(Decimal(amount) * Decimal(rate))


def eligible(quote: dict, *, order_date: str) -> str:
    expiry = pd.Timestamp(quote['expires'])
    if expiry < pd.Timestamp(order_date):
        return 'expired'
    if quote['freight'] is None or quote['lines_quoted'] != quote['lines_required']:
        return 'incomplete'
    return 'eligible'


# ---------------------------------------------------------------- P176
def installments(total_cents: int, fractions: list[str]) -> list[int]:
    """The residual adjustment is the largest-remainder library's, not a local rule."""
    weights = [Fraction(f) for f in fractions]
    if sum(weights) != 1:
        raise g.Blocked('declared fractions do not total one')
    if total_cents < 0:
        raise g.Blocked('no researched primitive conserves a negative total')
    return LargestRemainder.round([float(w) for w in weights], total=total_cents)


# ---------------------------------------------------------------- P177
def manifest_schema(events: dict) -> pandera.DataFrameSchema:
    declared = pd.Series(events, dtype='int64').sort_index()
    return pandera.DataFrameSchema(
        {'movement': pandera.Column(str, pandera.Check.isin(list(events))),
         'package': pandera.Column(str),
         'qty': pandera.Column(int, pandera.Check.gt(0))},
        checks=pandera.Check(
            lambda df: df.groupby('movement')['qty'].sum().reindex(declared.index).fillna(-1).astype('int64').equals(declared),
            error='allocations do not conserve every declared movement quantity'),
        unique=['movement', 'package'])


def validated_manifest(frame: pd.DataFrame, events: dict, *, reset_index: bool) -> pd.DataFrame:
    checked = frame.reset_index(drop=True) if reset_index else frame
    try:
        return manifest_schema(events).validate(checked, lazy=True)
    except pandera.errors.SchemaErrors as failure:
        raise g.Blocked('manifest rejected: %s'
                        % sorted({str(c) for c in failure.failure_cases['check']}))


# ---------------------------------------------------------------- P178
def payment(principal: str, annual_rate: str, periods: int) -> Decimal:
    rate = float(Decimal(annual_rate) / 12)
    return cents(-npf.pmt(rate, periods, float(Decimal(principal))))


def interest_from_schedule(principal: str, annual_rate: str, periods: int) -> Decimal:
    return payment(principal, annual_rate, periods) * periods - Decimal(principal)


def interest_from_library(principal: str, annual_rate: str, periods: int) -> Decimal:
    rate = float(Decimal(annual_rate) / 12)
    return cents(-sum(npf.ipmt(rate, k, periods, float(Decimal(principal))) for k in range(1, periods + 1)))


def components(principal: str, annual_rate: str, periods: int, period: int) -> tuple[float, float]:
    rate = float(Decimal(annual_rate) / 12)
    return (npf.ipmt(rate, period, periods, float(Decimal(principal))),
            npf.ppmt(rate, period, periods, float(Decimal(principal))))


# ---------------------------------------------------------------- P179
def net_present_value(rate: float, flows: list[float]) -> float:
    return float(npf.npv(rate, flows))


def discounted_from(rate: float, flows: list[float], *, first_period: int) -> float:
    return float(sum(v / (1 + rate) ** (t + first_period) for t, v in enumerate(flows)))


def sign_changes(flows: list[float]) -> int:
    nonzero = [v for v in flows if v != 0]
    return int(np.sum(np.diff(np.sign(nonzero)) != 0))


def internal_rate(flows: list[float]) -> float:
    if sign_changes(flows) != 1:
        raise g.Blocked('internal rate is defined here only for one sign change, found %d' % sign_changes(flows))
    if any(math.isnan(v) for v in flows):
        raise g.Blocked('cash flows contain an unknown value')
    return float(npf.irr(flows))


# ---------------------------------------------------------------- P180
def booking(start: str, finish: str, *, closed: str) -> pd.Interval:
    return pd.Interval(pd.Timestamp(start, tz='UTC'), pd.Timestamp(finish, tz='UTC'), closed=closed)


def conflicts(bookings: list[pd.Interval], probe: pd.Interval, *, drop_self: bool) -> int:
    index = pd.IntervalIndex(bookings)
    hits = index.overlaps(probe)
    if drop_self:
        hits = [h and iv != probe for h, iv in zip(hits, bookings)]
    return int(sum(bool(h) for h in hits))


C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(171)
def working_slots_come_from_the_calendar_not_from_a_span():
    september = working_dates('2026-09-01', '2026-09-30')
    g.equal(len(september), 21)
    g.equal('2026-09-07' in september, False)  # the declared holiday
    g.equal('2026-09-05' in september, False)  # a Saturday
    g.equal(bool(np.is_busday(np.datetime64('2026-09-08'), busdaycal=CALENDAR)), True)
    g.equal(working_days('2026-09-01', '2026-09-30', inclusive=False), 20)
    g.equal(working_days('2026-09-01', '2026-09-30', inclusive=True), 21)
    g.equal(working_days('2026-09-01', '2026-09-30', inclusive=True)
            - working_days('2026-09-01', '2026-09-30', inclusive=False), 1)
    g.equal(len(half_day_slots(september)), 42)
    g.equal(half_day_slots(september)[:2], [('2026-09-01', 'AM'), ('2026-09-01', 'PM')])
    g.equal(len(half_day_slots(september)) % 2, 0)
    rows = [{'employee': 'A', 'days': Decimal('3.50')}, {'employee': 'B', 'days': Decimal('0.50')},
            {'employee': None, 'days': Decimal('1.00')}]
    g.equal(day_totals(rows, dropna=True), {'A': Decimal('3.50'), 'B': Decimal('0.50')})
    g.equal(sum(day_totals(rows, dropna=True).values()), Decimal('4.00'))
    g.equal(sum(day_totals(rows, dropna=False).values()), Decimal('5.00'))  # the unattributed day only appears here
    g.equal(len(day_totals(rows, dropna=False)), 3)
    return {'holiday_and_weekend_excluded_by_the_calendar': True,
            'inclusive_span_is_one_more_than_the_half_open_count': True,
            'unattributed_days_vanish_under_the_groupby_default': True}


@case(172)
def two_membership_primitives_default_against_the_declared_contract():
    both = membership_dates('2026-09-01', '2026-09-20', inclusive='both')
    left = membership_dates('2026-09-01', '2026-09-20', inclusive='left')
    g.equal(len(both), 20); g.equal(both[-1], '2026-09-20')  # date_range includes the end by default
    g.equal(len(left), 19); g.equal(left[-1], '2026-09-19')  # the declared end-exclusive reading
    g.equal(len(both) - len(left), 1)
    g.equal(pd.Interval(0, 1).closed, 'right')  # and Interval defaults to the opposite closure
    span = assignment_interval('2026-09-01', '2026-09-18', closed='left')
    g.equal(pd.Timestamp('2026-09-17') in span, True)
    g.equal(pd.Timestamp('2026-09-18') in span, False)  # the declared exclusive end date
    g.equal(pd.Timestamp('2026-09-01') in span, True)
    default_closed = assignment_interval('2026-09-01', '2026-09-18', closed='right')
    g.equal(pd.Timestamp('2026-09-18') in default_closed, True)
    g.equal(pd.Timestamp('2026-09-01') in default_closed, False)  # and it drops the declared start instead
    g.equal((pd.Timestamp('2026-09-18') in span) == (pd.Timestamp('2026-09-18') in default_closed), False)
    return {'date_range_includes_both_ends_by_default': True,
            'interval_defaults_to_right_closed': True,
            'both_defaults_contradict_the_declared_contract': True}


@case(173)
def a_due_date_before_a_holiday_weekend_is_a_calendar_offset():
    g.equal(offset_working_days('2026-09-10', -3, roll='raise'), '2026-09-04')  # crosses the weekend and the holiday
    g.equal(offset_working_days('2026-09-22', -3, roll='raise'), '2026-09-17')
    g.equal(offset_working_days('2026-09-04', 3, roll='raise'), '2026-09-10')
    g.rejects(ValueError, lambda: offset_working_days('2026-09-07', -3, roll='raise'))  # the holiday itself
    g.equal(offset_working_days('2026-09-07', 0, roll='forward'), '2026-09-08')
    g.equal(offset_working_days('2026-09-07', 0, roll='backward'), '2026-09-04')
    forward = np.datetime64(offset_working_days('2026-09-07', 0, roll='forward'))
    backward = np.datetime64(offset_working_days('2026-09-07', 0, roll='backward'))
    g.equal(int((forward - backward) / np.timedelta64(1, 'D')), 4)
    g.equal(offset_working_days('2026-09-10', 0, roll='raise'), '2026-09-10')
    return {'offset_crosses_the_holiday_weekend': True,
            'roll_raise_refuses_a_non_working_anchor': True,
            'forward_and_backward_are_four_days_apart': True}


@case(174)
def an_unknown_shortfall_is_not_a_zero_request():
    rows = [{'item': 'cable', 'net': 6}, {'item': 'chair', 'net': 0},
            {'item': 'desk', 'net': 1}, {'item': 'monitor', 'net': None}]
    lines = requested_lines(rows)
    requested = [r for r in lines if r['state'] == 'requested']
    g.equal([r['item'] for r in requested], ['cable', 'desk'])
    g.equal([r['requested'] for r in requested], [6, 1])
    unknown = [r for r in lines if r['state'] == 'unknown shortfall']
    g.equal([r['item'] for r in unknown], ['monitor'])
    g.equal(unknown[0]['requested'] is None, True)  # not zero
    absent = [r for r in lines if r['state'] == 'no shortfall']
    g.equal([r['item'] for r in absent], ['chair']); g.equal(absent[0]['requested'], 0)
    g.equal(unknown[0]['requested'] == absent[0]['requested'], False)
    g.equal(len(lines), 4); g.equal(len(requested) + len(unknown) + len(absent), 4)
    return {'unknown_shortfall_stays_unknown': True, 'zero_shortfall_is_a_separate_state': True}


@case(175)
def a_pack_size_decides_the_cost_not_the_unit_count():
    packs, units, surplus = whole_packs(6, 5)
    g.equal((packs, units, surplus), (2, 10, 4))  # six cables need two five-packs
    g.equal(whole_packs(10, 5), (2, 10, 0))
    g.equal(whole_packs(1, 5), (1, 5, 4))
    g.equal(whole_packs(6, 1), (6, 6, 0))
    g.rejects(g.Blocked, lambda: whole_packs(6, 0))
    g.equal(math.ceil(Fraction(6, 5)), 2); g.equal(math.ceil(Fraction(10, 5)), 2)
    g.equal(converted('220.00', '1.155'), Decimal('254.10'))
    g.equal(converted('0.005', '1.00'), Decimal('0.01'))  # the declared half-cent rounds up
    quotes = {'A': {'expires': '2026-09-30', 'freight': '15.00', 'lines_quoted': 3, 'lines_required': 3},
              'B': {'expires': '2026-09-30', 'freight': None, 'lines_quoted': 3, 'lines_required': 3},
              'C': {'expires': '2026-09-23', 'freight': '10.00', 'lines_quoted': 2, 'lines_required': 3}}
    states = {k: eligible(v, order_date='2026-09-24') for k, v in quotes.items()}
    g.equal(states, {'A': 'eligible', 'B': 'incomplete', 'C': 'expired'})
    g.equal(eligible(quotes['C'], order_date='2026-09-23'), 'incomplete')  # expiry on the order date is not expired
    g.equal(len([k for k, v in states.items() if v == 'eligible']), 1)
    return {'whole_pack_ceiling_is_an_exact_rational': True, 'surplus_units': 4,
            'expiry_on_the_order_date_is_not_expired': True}


@case(176)
def the_installment_residual_belongs_to_the_apportionment_library():
    g.equal(installments(459_00, ['1/2', '1/2']), [22950, 22950])
    g.equal(sum(installments(459_00, ['1/2', '1/2'])), 459_00)
    g.equal(cents(installments(459_00, ['1/2', '1/2'])[0] / 100), Decimal('229.50'))
    g.equal(installments(1, ['1/2', '1/2']), [1, 0])  # a one-cent total conserves exactly
    g.equal(sum(installments(1, ['1/2', '1/2'])), 1)
    g.equal(installments(100_01, ['1/3', '1/3', '1/3']), [3334, 3334, 3333])
    g.equal(sum(installments(100_01, ['1/3', '1/3', '1/3'])), 100_01)
    g.rejects(g.Blocked, lambda: installments(459_00, ['1/2', '1/3']))
    g.rejects(g.Blocked, lambda: installments(-459_00, ['1/2', '1/2']))
    g.equal(sum(Fraction(f) for f in ['1/2', '1/2']), 1)
    return {'residual_is_the_library_method': True, 'one_cent_total_conserves': True,
            'fractions_that_miss_one_are_blocked': True}


@case(177)
def a_conservation_check_is_a_schema_and_a_duplicate_index_defeats_it():
    events = {'M1': 3, 'M2': 4, 'M3': 12, 'M4': 1, 'M5': 1}
    conserving = pd.DataFrame({'movement': ['M1', 'M1', 'M2', 'M3', 'M4', 'M5'],
                               'package': ['A1', 'A2', 'A1', 'A1', 'A2', 'B1'],
                               'qty': [2, 1, 4, 12, 1, 1]})
    checked = validated_manifest(conserving, events, reset_index=True)
    g.equal(len(checked), 6); g.equal(int(checked['qty'].sum()), 21)
    g.rejects(g.Blocked, lambda: validated_manifest(conserving.assign(qty=[3, 1, 4, 12, 1, 1]), events, reset_index=True))
    g.rejects(g.Blocked, lambda: validated_manifest(conserving.assign(qty=[1, 1, 4, 12, 1, 1]), events, reset_index=True))
    g.rejects(g.Blocked, lambda: validated_manifest(conserving.iloc[:5], events, reset_index=True))
    unknown_movement = conserving.assign(movement=['M9'] + list(conserving['movement'][1:]))
    g.rejects(g.Blocked, lambda: validated_manifest(unknown_movement, events, reset_index=True))
    duplicated = pd.concat([conserving, conserving.iloc[[0]]])
    g.equal(list(duplicated.index), [0, 1, 2, 3, 4, 5, 0])  # concat repeats the index label
    g.rejects(ValueError, lambda: validated_manifest(duplicated, events, reset_index=False))
    g.rejects(g.Blocked, lambda: validated_manifest(duplicated, events, reset_index=True))
    try:
        validated_manifest(duplicated, events, reset_index=True)
    except g.Blocked as blocked:
        g.equal('multiple_fields_uniqueness' in str(blocked), True)
    return {'conservation_is_a_dataframe_level_check': True,
            'duplicate_index_crashes_the_uniqueness_report': True,
            'reset_index_restores_the_rejection': True}


@case(178)
def the_rounded_schedule_and_the_library_disagree_by_two_cents():
    g.equal(payment('459.00', '0.12', 12), Decimal('40.78'))
    g.equal(payment('459.00', '0.12', 12) * 12, Decimal('489.36'))
    g.equal(interest_from_schedule('459.00', '0.12', 12), Decimal('30.36'))
    g.equal(interest_from_library('459.00', '0.12', 12), Decimal('30.38'))
    g.equal(interest_from_library('459.00', '0.12', 12)
            - interest_from_schedule('459.00', '0.12', 12), Decimal('0.02'))
    g.equal(payment('459.00', '0.00', 12), Decimal('38.25'))
    g.equal(payment('459.00', '0.00', 12) * 12, Decimal('459.00'))
    g.equal(interest_from_schedule('459.00', '0.00', 12), Decimal('0.00'))
    rate = 0.12 / 12
    for period in (1, 6, 12):
        interest, principal = components('459.00', '0.12', 12, period)
        g.equal(abs(interest + principal - npf.pmt(rate, 12, 459.0)) < 1e-9, True)
    g.equal(npf.pmt(rate, 12, 459.0) < 0, True)  # the library signs a payment as cash out
    g.equal(type(npf.ipmt(rate, 1, 12, 459.0)).__name__, 'ndarray')  # a scalar call returns a 0-d array
    g.rejects(TypeError, lambda: round(npf.ipmt(rate, 1, 12, 459.0), 2))
    g.equal(float(npf.ipmt(rate, 13, 12, 459.0)), -0.0)  # a period past the term returns a number
    g.equal(math.isnan(float(npf.ipmt(rate, 0, 12, 459.0))), False)  # so does period zero
    g.equal(round(float(npf.ipmt(rate, 0, 12, 459.0)), 6), -4.948333)
    return {'schedule_interest': '30.36', 'library_interest': '30.38', 'gap_cents': 2,
            'out_of_range_periods_return_numbers': True, 'scalar_call_returns_a_zero_d_array': True, 'payment_is_signed_negative': True}


@case(179)
def one_nan_carries_three_different_reasons_and_one_raises():
    base = [-459.00, 200.00, 250.00, 300.00]
    g.equal(round(net_present_value(0.08, base), 6), 178.669563)
    g.equal(abs(net_present_value(0.08, base) - discounted_from(0.08, base, first_period=0)) < 1e-9, True)
    excel_style = discounted_from(0.08, base, first_period=1)
    g.equal(round(excel_style, 6), 165.43478)
    g.equal(round(net_present_value(0.08, base) / excel_style, 6), 1.08)  # one whole period of discounting apart
    g.equal(round(cents(net_present_value(0.08, base)), 2), Decimal('178.67'))
    g.equal(sign_changes(base), 1)
    g.equal(round(internal_rate(base), 6), 0.269913)
    g.equal(sign_changes([-459.00, 900.00, -500.00]), 2)
    g.rejects(g.Blocked, lambda: internal_rate([-459.00, 900.00, -500.00]))
    g.equal(math.isnan(npf.irr([-459.00, 900.00, -500.00])), True)
    g.equal(sign_changes([100.0, 200.0, 300.0]), 0)
    g.rejects(g.Blocked, lambda: internal_rate([100.0, 200.0, 300.0]))
    g.equal(math.isnan(npf.irr([100.0, 200.0, 300.0])), True)
    g.equal(math.isnan(npf.irr([0.0, 0.0, 0.0])), True)  # three reasons, one return value
    g.equal(math.isnan(net_present_value(0.08, [-459.0, float('nan'), 250.0])), True)
    g.rejects(np.linalg.LinAlgError, lambda: npf.irr([-459.0, float('nan'), 250.0]))  # not nan, an exception
    g.rejects(g.Blocked, lambda: internal_rate([-459.0, float('nan'), 250.0]))
    return {'npv_leaves_the_first_flow_undiscounted': True, 'excel_convention_ratio': 1.08,
            'irr_returns_nan_for_three_distinct_reasons': True,
            'irr_raises_linalgerror_on_a_missing_flow': True}


@case(180)
def whether_two_bookings_touch_depends_on_how_each_was_built():
    desk = booking('2026-09-23 13:00', '2026-09-23 15:00', closed='left')
    training = booking('2026-09-23 14:00', '2026-09-23 16:00', closed='left')
    later = booking('2026-09-23 15:00', '2026-09-23 17:00', closed='left')
    g.equal(desk.overlaps(training), True)  # the shared 13:00-15:00 window
    g.equal(desk.overlaps(later), False)  # a booking ending when another starts is not an overlap
    both_desk = booking('2026-09-23 13:00', '2026-09-23 15:00', closed='both')
    both_later = booking('2026-09-23 15:00', '2026-09-23 17:00', closed='both')
    g.equal(both_desk.overlaps(both_later), True)  # the same two clock times, the other closure
    right_desk = booking('2026-09-23 13:00', '2026-09-23 15:00', closed='right')
    g.equal(right_desk.overlaps(later), True)  # mixed closures answer without any error
    g.equal(right_desk.overlaps(both_later), True)
    g.equal(desk.overlaps(both_later), False)
    g.equal(desk.overlaps(later) == both_desk.overlaps(both_later), False)
    g.equal(conflicts([desk, training, later], desk, drop_self=False), 2)  # the probe matches itself
    g.equal(conflicts([desk, training, later], desk, drop_self=True), 1)
    g.equal(conflicts([desk, training, later], later, drop_self=True), 1)
    g.equal(conflicts([desk, later], desk, drop_self=True), 0)  # removing the overlap clears the conflict
    return {'touching_bookings_depend_on_the_declared_closure': True,
            'mixed_closures_compare_without_error': True,
            'intervalindex_overlaps_includes_the_probe_itself': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['largest-remainder', 'numpy', 'numpy-financial', 'pandas', 'pandera']
    here = Path(__file__).resolve().parent
    return {'scope': 'Bounded authored leave, workforce, onboarding, requisition, quote, installment, packing, loan, appraisal and roster fixtures and reproduced library defaults; the original P171-P180 chains and their artifacts were not rerun.',
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
