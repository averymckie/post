"""Nineteenth bounded adapter suite: P181-P190, passage rendering, maintenance recurrence, training expiry,
unit-aware inspection, renewal terms, as-of progress selection, earned value, reporting hierarchy, acceptance
binding and status composition. Requires handoff_guards_v1.py from this TXT.

Every meaningful operation below is a library primitive call. Recurrence is dateutil.rrule, unit conversion is Pint
with an exact rational magnitude, temporal selection is pandas.merge_asof, hierarchy validation is NetworkX,
exact money is DuckDB DECIMAL with fractions.Fraction for ratios, escaping is a Jinja2 autoescaping Environment
checked through lxml, and native shape and chart binding is python-pptx. Local code declares fixtures and policies
and turns a primitive result into a Blocked outcome. All runtime inputs are authored fixtures. No model client and
no network.
Run: python handoff_guards_v20.py --report report.json
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, io, json, logging, re, traceback, warnings
from datetime import date, datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import duckdb
import networkx as nx
import pandas as pd
import pint
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, WEEKLY, rrule
from jinja2 import Environment, StrictUndefined
from lxml import etree, html as lxml_html
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.util import Inches
import handoff_guards_v1 as g
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

UNITS = pint.UnitRegistry(non_int_type=Fraction)
Q = UNITS.Quantity


# ---------------------------------------------------------------- P181
def escaped_page(passages: list[dict], *, autoescape: bool) -> str:
    env = Environment(undefined=StrictUndefined, autoescape=autoescape)
    template = env.from_string('<ul>{% for p in passages %}<li id="{{ p.id }}">{{ p.text }}</li>{% endfor %}</ul>')
    return template.render(passages=passages)


def parsed_texts(markup: str) -> list[str]:
    return [node.text_content() for node in lxml_html.fromstring(markup).xpath('//li')]


# ---------------------------------------------------------------- P182
def occurrences(anchor: str, count: int, *, rule: str) -> list[str]:
    start = datetime.fromisoformat(anchor)
    if rule == 'monthly_literal_day':
        series = rrule(MONTHLY, dtstart=start, count=count, bymonthday=start.day)
    elif rule == 'monthly_month_end':
        series = rrule(MONTHLY, dtstart=start, count=count, bymonthday=-1)
    elif rule == 'quarterly':
        series = rrule(MONTHLY, dtstart=start, count=count, interval=3)
    elif rule == 'two_weekly':
        series = rrule(WEEKLY, dtstart=start, count=count, interval=2)
    else:
        raise g.Blocked('unknown recurrence rule %r' % rule)
    return [d.date().isoformat() for d in series]


def until_occurrences(anchor: str, until: str) -> list[str]:
    return [d.date().isoformat() for d in
            rrule(MONTHLY, dtstart=datetime.fromisoformat(anchor), until=datetime.fromisoformat(until))]


# ---------------------------------------------------------------- P183
def expiry(completed: str, months: int) -> date:
    return date.fromisoformat(completed) + relativedelta(months=months)


RESULT_SCHEMA_KEYS = ['result', 'session']


def joined_results(results: list[dict], sessions: list[dict], *, how: str) -> pd.DataFrame:
    return pd.DataFrame(results).merge(pd.DataFrame(sessions), on='session', how=how,
                                       validate='many_to_one', indicator=True)


# ---------------------------------------------------------------- P184
def reading(value: str, unit: str) -> object:
    return Q(Fraction(value), unit)


def converted_reading(value: str, unit: str, target: str) -> object:
    return reading(value, unit).to(target)


def uncertainty(value: str, unit: str, target: str, *, as_delta: bool) -> object:
    """as_delta=False converts the uncertainty as an absolute temperature, the common error."""
    source = 'delta_' + unit if as_delta else unit
    goal = 'delta_' + target if as_delta else target
    return Q(Fraction(value), source).to(goal)


def acceptance(nominal, spread, *, upper: str) -> str:
    limit = Fraction(upper)
    low, high = nominal.magnitude - spread.magnitude, nominal.magnitude + spread.magnitude
    if high <= limit:
        return 'pass'
    if low > limit:
        return 'fail'
    return 'review'


# ---------------------------------------------------------------- P185
def term_status(start: str, finish: str, cutoff: str) -> str:
    begin, end, today = (date.fromisoformat(x) for x in (start, finish, cutoff))
    if today < begin:
        return 'future'
    return 'active' if today <= end else 'expired'


def notice_deadline(finish: str, notice_days: int) -> date:
    return date.fromisoformat(finish) - timedelta(days=notice_days)


def next_term(finish: str, months: int) -> tuple[str, str]:
    begin = date.fromisoformat(finish) + timedelta(days=1)
    return begin.isoformat(), (begin + relativedelta(months=months) - timedelta(days=1)).isoformat()


# ---------------------------------------------------------------- P186
def as_of(updates: list[dict], cutoffs: list[dict], *, exact: bool) -> list[dict]:
    left = pd.DataFrame(cutoffs).assign(when=lambda d: pd.to_datetime(d['when'])).sort_values('when')
    right = pd.DataFrame(updates).assign(when=lambda d: pd.to_datetime(d['when'])).sort_values('when')
    merged = pd.merge_asof(left, right, on='when', by='task', direction='backward',
                           allow_exact_matches=exact)
    return [{'task': r['task'], 'pct': None if pd.isna(r['pct']) else r['pct']}
            for r in merged.to_dict('records')]


def unsorted_as_of(updates: list[dict], cutoffs: list[dict]) -> list[dict]:
    left = pd.DataFrame(cutoffs).assign(when=lambda d: pd.to_datetime(d['when'])).sort_values('when')
    right = pd.DataFrame(updates).assign(when=lambda d: pd.to_datetime(d['when']))
    return pd.merge_asof(left, right, on='when', by='task', direction='backward').to_dict('records')


# ---------------------------------------------------------------- P187
def cost_through(records: list[dict], cutoff: str) -> dict:
    con = duckdb.connect()
    con.execute('CREATE TABLE cost(task VARCHAR, spent_on DATE, amount DECIMAL(18,2))')
    con.executemany('INSERT INTO cost VALUES (?, ?, ?)',
                    [(r['task'], r['spent_on'], Decimal(r['amount'])) for r in records])
    rows = con.execute('SELECT task, sum(amount) FROM cost WHERE spent_on <= ? GROUP BY task ORDER BY task',
                       [cutoff]).fetchall()
    con.close()
    return {task: total for task, total in rows}


def indices(planned: str, earned: str, actual: str) -> dict:
    pv, ev, ac = (Fraction(x) for x in (planned, earned, actual))
    return {'cost_variance': ev - ac, 'schedule_variance': ev - pv,
            'cpi': None if ac == 0 else Fraction(ev, ac), 'spi': None if pv == 0 else Fraction(ev, pv)}


def estimate_at_completion(budget: str, actual: str, earned: str, *, assumption: str) -> Fraction:
    bac, ac, ev = (Fraction(x) for x in (budget, actual, earned))
    if assumption == 'remaining_at_budget':
        return ac + (bac - ev)
    if assumption == 'budget_plus_variance':
        return bac + (ac - ev)
    if assumption == 'remaining_at_current_efficiency':
        if ev == 0:
            raise g.Blocked('no earned value, so current efficiency is undefined')
        return ac + (bac - ev) * Fraction(ac, ev)
    raise g.Blocked('unknown completion assumption %r' % assumption)


# ---------------------------------------------------------------- P188
def hierarchy(edges: list[tuple[str, str]]) -> nx.DiGraph:
    graph = nx.DiGraph(edges)
    if not nx.is_arborescence(graph):
        raise g.Blocked('reporting structure is not a single rooted tree')
    return graph


def levels(graph: nx.DiGraph) -> list[list[str]]:
    return [sorted(generation) for generation in nx.topological_generations(graph)]


def org_deck(edges: list[tuple[str, str]]) -> bytes:
    deck = Presentation(); slide = deck.slides.add_slide(deck.slide_layouts[6])
    boxes = {}
    for row, name in enumerate(sorted({n for e in edges for n in e})):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1 + row), Inches(2), Inches(0.8))
        shape.text_frame.text = name
        boxes[name] = shape
    for parent, child in edges:
        line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(2), Inches(2), Inches(2), Inches(3))
        line.begin_connect(boxes[parent], 2); line.end_connect(boxes[child], 0)
    buf = io.BytesIO(); deck.save(buf); return buf.getvalue()


def connector_bindings(deck: bytes) -> list[list[str]]:
    slide = Presentation(io.BytesIO(deck)).slides[0]
    out = []
    for shape in slide.shapes:
        if 'Connector' in type(shape).__name__:
            out.append(re.findall(r'(?:st|end)Cxn id="(\d+)"', shape._element.xml))
    return out


def shape_ids(deck: bytes) -> dict:
    slide = Presentation(io.BytesIO(deck)).slides[0]
    return {s.text_frame.text: s.shape_id for s in slide.shapes if s.has_text_frame and s.text_frame.text}


# ---------------------------------------------------------------- P189
def evidence(artifact: bytes, declared_sha: str) -> str:
    actual = hashlib.sha256(artifact).hexdigest()
    if actual != declared_sha:
        raise g.Blocked('artifact bytes do not match the declared evidence hash')
    return actual


def acceptance_state(criteria: list[dict], signoff: dict | None, *, cutoff: str) -> str:
    if any(c['result'] == 'not_run' for c in criteria):
        return 'incomplete: a criterion was not executed'
    if any(c['result'] == 'failed' for c in criteria):
        return 'not accepted: a criterion failed'
    if signoff is None or signoff['state'] != 'signed':
        return 'not accepted: no signed record'
    if date.fromisoformat(signoff['on']) > date.fromisoformat(cutoff):
        return 'not accepted: the record post-dates the cutoff'
    return 'accepted'


# ---------------------------------------------------------------- P190
def status_deck(values: tuple[float, ...]) -> bytes:
    deck = Presentation(); slide = deck.slides.add_slide(deck.slide_layouts[6])
    data = CategoryChartData(); data.categories = ['PV', 'EV', 'AC']; data.add_series('Sep 17', values)
    slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(1), Inches(1), Inches(6), Inches(4), data)
    buf = io.BytesIO(); deck.save(buf); return buf.getvalue()


def edited_copy(deck: bytes, values: tuple[float, ...]) -> bytes:
    copy = Presentation(io.BytesIO(deck))
    data = CategoryChartData(); data.categories = ['PV', 'EV', 'AC']; data.add_series('Sep 17', values)
    copy.slides[0].shapes[0].chart.replace_data(data)
    buf = io.BytesIO(); copy.save(buf); return buf.getvalue()


def chart_values(deck: bytes) -> list:
    return list(Presentation(io.BytesIO(deck)).slides[0].shapes[0].chart.series[0].values)


C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(181)
def the_html_parser_hides_the_escaping_the_xml_parser_rejects():
    literal = [{'id': 'p1', 'text': 'A & B < 5 > 2'}]
    markup = [{'id': 'p1', 'text': 'see <b>bold</b> here'}]
    closing = [{'id': 'p1', 'text': 'end</li><li>injected'}]
    g.equal(Environment(undefined=StrictUndefined).autoescape, False)
    for passages in (literal, markup, closing):
        g.equal(parsed_texts(escaped_page(passages, autoescape=True)), [passages[0]['text']])
        g.equal(len(parsed_texts(escaped_page(passages, autoescape=True))), 1)
    g.equal(parsed_texts(escaped_page(literal, autoescape=False)), ['A & B < 5 > 2'])
    g.equal(parsed_texts(escaped_page(literal, autoescape=False))
            == parsed_texts(escaped_page(literal, autoescape=True)), True)  # the HTML parser recovers it
    g.rejects(etree.XMLSyntaxError, lambda: etree.fromstring(escaped_page(literal, autoescape=False)))
    g.equal(etree.fromstring(escaped_page(literal, autoescape=True)) is not None, True)
    g.equal(parsed_texts(escaped_page(markup, autoescape=False)), ['see bold here'])  # the tags are consumed
    g.equal(parsed_texts(escaped_page(markup, autoescape=False))[0] == markup[0]['text'], False)
    g.equal(len(parsed_texts(escaped_page(markup, autoescape=False))), 1)  # and the element count is unchanged
    g.equal(len(parsed_texts(escaped_page(closing, autoescape=False))), 2)  # one passage became two reading rows
    g.equal(parsed_texts(escaped_page(closing, autoescape=False)), ['end', 'injected'])
    g.rejects(Exception, lambda: escaped_page([{'id': 'p1'}], autoescape=True))
    return {'autoescape_is_off_by_default': True,
            'html_parser_recovers_the_unescaped_literal': True,
            'xml_parser_rejects_the_same_bytes': True,
            'literal_markup_is_consumed_with_the_count_unchanged': True,
            'a_closing_tag_manufactures_a_second_passage': True}


@case(182)
def a_monthly_rule_anchored_on_the_31st_skips_three_months():
    literal = occurrences('2026-01-31', 8, rule='monthly_literal_day')
    g.equal(literal[:3], ['2026-01-31', '2026-03-31', '2026-05-31'])
    g.equal(sorted({int(d[5:7]) for d in literal if d[:4] == '2026'}), [1, 3, 5, 7, 8, 10, 12])
    g.equal('2026-02-28' in literal, False)  # February produces no occurrence at all
    g.equal(literal[-1], '2027-01-31')  # eight occurrences span thirteen months
    month_end = occurrences('2026-01-31', 8, rule='monthly_month_end')
    g.equal(month_end[:4], ['2026-01-31', '2026-02-28', '2026-03-31', '2026-04-30'])
    g.equal(len(month_end), 8); g.equal(month_end[-1], '2026-08-31')  # eight occurrences span eight months
    g.equal(occurrences('2028-01-31', 3, rule='monthly_month_end')[1], '2028-02-29')  # leap year
    g.equal(occurrences('2026-09-01', 4, rule='quarterly'),
            ['2026-09-01', '2026-12-01', '2027-03-01', '2027-06-01'])
    g.equal(occurrences('2026-09-01', 4, rule='two_weekly'),
            ['2026-09-01', '2026-09-15', '2026-09-29', '2026-10-13'])
    g.rejects(g.Blocked, lambda: occurrences('2026-09-01', 4, rule='fortnightly'))
    g.equal(until_occurrences('2026-09-01', '2026-12-01')[-1], '2026-12-01')  # until is inclusive
    g.equal(len(until_occurrences('2026-09-01', '2026-12-01')), 4)
    return {'literal_day_rule_skips_short_months': True, 'skipped_months': [2, 4, 6],
            'month_end_rule_covers_every_month': True, 'until_is_inclusive': True}


@case(183)
def an_expiry_is_the_first_invalid_date_not_the_last_valid_one():
    g.equal(expiry('2025-09-30', 12), date(2026, 9, 30))
    g.equal(expiry('2025-09-30', 12) - timedelta(days=1), date(2026, 9, 29))
    g.equal(date(2026, 9, 29) < expiry('2025-09-30', 12), True)  # the day before is still current
    g.equal(date(2026, 9, 30) < expiry('2025-09-30', 12), False)  # the expiry date itself is not
    g.equal(expiry('2024-02-29', 12), date(2025, 2, 28))  # a leap day clamps
    g.equal(expiry('2025-02-28', 12), date(2026, 2, 28))
    results = [{'result': 'R1', 'session': 'S1'}, {'result': 'R2', 'session': 'S1'}, {'result': 'R3', 'session': 'S9'}]
    sessions = [{'session': 'S1', 'course': 'safety'}]
    inner = joined_results(results, sessions, how='inner')
    g.equal(len(inner), 2); g.equal(sorted(inner['_merge'].astype(str).unique()), ['both'])
    outer = joined_results(results, sessions, how='left')
    g.equal(len(outer), 3); g.equal(int((outer['_merge'] == 'left_only').sum()), 1)
    g.equal(sorted(outer[outer['_merge'] == 'left_only']['result']), ['R3'])
    duplicated = sessions + [{'session': 'S1', 'course': 'other'}]
    g.rejects(pd.errors.MergeError, lambda: joined_results(results, duplicated, how='left'))
    return {'expiry_is_the_first_invalid_date': True, 'leap_day_completion_clamps': True,
            'inner_join_hides_the_unmatched_result': True}


@case(184)
def an_uncertainty_converted_as_a_temperature_is_off_by_seventeen_degrees():
    nominal = converted_reading('85.64', 'degF', 'degC')
    g.equal(nominal.magnitude, Fraction(149, 5))
    g.equal(float(nominal.magnitude), 29.8)
    spread = uncertainty('0.9', 'degF', 'degC', as_delta=True)
    g.equal(spread.magnitude, Fraction(1, 2)); g.equal(float(spread.magnitude), 0.5)
    wrong = uncertainty('0.9', 'degF', 'degC', as_delta=False)
    g.equal(round(float(wrong.magnitude), 6), -17.277778)  # an absolute conversion of an uncertainty
    g.equal(float(wrong.magnitude) < 0, True)
    g.equal(round(float(spread.magnitude - wrong.magnitude), 6), 17.777778)
    g.equal(acceptance(nominal, spread, upper='30'), 'review')  # the interval crosses the limit
    g.equal(float(nominal.magnitude) <= 30.0, True)  # while the nominal value alone passes
    g.equal(acceptance(nominal, Q(Fraction(0), 'delta_degC'), upper='30'), 'pass')
    g.equal(acceptance(Q(Fraction(31), 'degC'), Q(Fraction(0), 'delta_degC'), upper='30'), 'fail')
    g.rejects(pint.errors.OffsetUnitCalculusError, lambda: Q(Fraction(1), 'degC') + Q(Fraction(1), 'degC'))
    g.equal((Q(Fraction(1), 'degC') + Q(Fraction(1), 'delta_degC')).magnitude, Fraction(2))
    g.rejects(pint.errors.DimensionalityError, lambda: Q(Fraction(1), 'degC').to('psi'))
    pressure = converted_reading('14.7', 'psi', 'kPa')
    exact = Fraction('14.7') * (Fraction(45359237, 100000000) * Fraction(980665, 100000)) / (Fraction(254, 10000) ** 2) / 1000
    g.equal(pressure.magnitude, exact)  # exact rational agreement with the independent definition
    g.equal(isinstance(pressure.magnitude, Fraction), True)
    return {'delta_units_are_required_for_an_uncertainty': True, 'absolute_conversion_error_degc': -17.277778,
            'nominal_alone_passes_while_the_interval_does_not': True,
            'offset_unit_addition_is_refused': True}


@case(185)
def an_inclusive_term_and_its_notice_deadline_are_separate_dates():
    g.equal(term_status('2026-09-01', '2027-08-31', '2027-08-15'), 'active')
    g.equal(term_status('2026-09-01', '2027-08-31', '2027-08-31'), 'active')  # the end date is inside the term
    g.equal(term_status('2026-09-01', '2027-08-31', '2027-09-01'), 'expired')
    g.equal(term_status('2026-09-01', '2027-08-31', '2026-08-31'), 'future')
    g.equal((date.fromisoformat('2027-08-31') - date.fromisoformat('2027-08-15')).days, 16)
    g.equal(notice_deadline('2027-08-31', 30), date(2027, 8, 1))
    g.equal(notice_deadline('2027-08-31', 30) < date.fromisoformat('2027-08-15'), True)  # missed by 14 days
    g.equal((date.fromisoformat('2027-08-15') - notice_deadline('2027-08-31', 30)).days, 14)
    g.equal(notice_deadline('2027-09-15', 30), date(2027, 8, 16))
    g.equal((notice_deadline('2027-09-15', 30) - date.fromisoformat('2027-08-15')).days, 1)  # one day away
    g.equal(next_term('2027-08-31', 12), ('2027-09-01', '2028-08-31'))
    g.equal(next_term('2027-08-31', 1), ('2027-09-01', '2027-09-30'))
    g.equal(next_term('2028-02-29', 12), ('2028-03-01', '2029-02-28'))
    known = [Decimal('99.00'), Decimal('50.00')]
    g.equal(sum(known), Decimal('149.00'))
    g.equal(len(known) < 3, True)  # a third price is missing, so the full total stays unknown
    return {'inclusive_end_date_is_inside_the_term': True, 'notice_deadline_is_a_separate_date': True,
            'next_term_starts_the_day_after': True}


@case(186)
def whether_the_cutoff_update_counts_is_one_default_flag():
    updates = [{'task': 'T1', 'when': '2026-09-10', 'pct': 0.25},
               {'task': 'T1', 'when': '2026-09-17', 'pct': 0.60},
               {'task': 'T2', 'when': '2026-09-12', 'pct': 0.50},
               {'task': 'T2', 'when': '2026-09-18', 'pct': 0.90}]
    cutoffs = [{'task': 'T1', 'when': '2026-09-17'}, {'task': 'T2', 'when': '2026-09-17'}]
    inclusive = as_of(updates, cutoffs, exact=True)
    g.equal(inclusive, [{'task': 'T1', 'pct': 0.60}, {'task': 'T2', 'pct': 0.50}])
    exclusive = as_of(updates, cutoffs, exact=False)
    g.equal(exclusive, [{'task': 'T1', 'pct': 0.25}, {'task': 'T2', 'pct': 0.50}])
    g.equal(inclusive[0]['pct'] == exclusive[0]['pct'], False)  # one flag, two reported percentages
    g.equal(as_of(updates, cutoffs, exact=True)[1]['pct'], 0.50)  # the September 18 update stays out of both
    early = as_of(updates, [{'task': 'T1', 'when': '2026-09-01'}], exact=True)
    g.equal(early, [{'task': 'T1', 'pct': None}])  # unknown, not zero
    g.equal(early[0]['pct'] is None, True)
    g.rejects(ValueError, lambda: unsorted_as_of(
        [updates[1], updates[0], updates[2], updates[3]], cutoffs))  # the primitive refuses unsorted keys
    return {'allow_exact_matches_defaults_true': True, 'flag_changes_the_reported_progress': True,
            'cutoff_before_the_first_record_is_null': True, 'unsorted_input_is_refused': True}


@case(187)
def exact_ratios_stay_rational_and_a_zero_denominator_is_declared():
    records = [{'task': 'T01', 'spent_on': '2026-09-10', 'amount': '1200.25'},
               {'task': 'T01', 'spent_on': '2026-09-20', 'amount': '500.00'},
               {'task': 'T02', 'spent_on': '2026-09-15', 'amount': '939.75'},
               {'task': 'T02', 'spent_on': '2026-09-16', 'amount': '-50.00'}]
    through = cost_through(records, '2026-09-17')
    g.equal(through['T01'], Decimal('1200.25'))  # the September 20 record is excluded
    g.equal(through['T02'], Decimal('889.75'))  # the credit reduces its task cost
    g.equal(sum(through.values()), Decimal('2090.00'))
    g.equal(len(cost_through(records, '2026-09-09')), 0)
    metrics = indices('2350.00', '1900.00', '2090.00')
    g.equal(metrics['cost_variance'], Fraction(-190))
    g.equal(metrics['schedule_variance'], Fraction(-450))
    g.equal(metrics['cpi'], Fraction(10, 11)); g.equal(metrics['spi'], Fraction(38, 47))
    g.equal(float(metrics['cpi']) == 10 / 11, True)
    g.equal(metrics['cpi'] * 11, Fraction(10))  # exact, unlike the float
    g.equal(indices('0.00', '0.00', '0.00')['cpi'] is None, True)
    g.equal(estimate_at_completion('3000.00', '2090.00', '1900.00', assumption='remaining_at_budget'), Fraction(3190))
    g.equal(estimate_at_completion('3000.00', '2090.00', '1900.00', assumption='budget_plus_variance'), Fraction(3190))
    efficiency = estimate_at_completion('3000.00', '2090.00', '1900.00', assumption='remaining_at_current_efficiency')
    g.equal(round(float(efficiency), 2), 3300.0)
    g.equal(efficiency, Fraction(2090) + Fraction(1100) * Fraction(2090, 1900))
    g.rejects(g.Blocked, lambda: estimate_at_completion('3000.00', '2090.00', '0.00',
                                                        assumption='remaining_at_current_efficiency'))
    g.rejects(g.Blocked, lambda: estimate_at_completion('3000.00', '2090.00', '1900.00', assumption='optimistic'))
    return {'decimal_sum_is_exact': True, 'credit_reduces_the_task_cost': True,
            'cpi_stays_rational': '10/11', 'zero_denominators_are_declared': True}


@case(188)
def a_reporting_tree_is_a_graph_predicate_and_the_connectors_carry_ids():
    edges = [('CEO', 'Ops'), ('CEO', 'Sales'), ('Ops', 'A'), ('Ops', 'B'), ('Sales', 'C')]
    tree = hierarchy(edges)
    g.equal(levels(tree), [['CEO'], ['Ops', 'Sales'], ['A', 'B', 'C']])
    g.equal(sorted(nx.descendants(tree, 'Ops')), ['A', 'B'])
    g.equal(sorted(n for n in tree if tree.out_degree(n) == 0), ['A', 'B', 'C'])
    g.equal(tree.out_degree('Ops'), 2)
    g.rejects(g.Blocked, lambda: hierarchy(edges + [('Sales', 'A')]))  # a second parent
    g.equal(nx.is_directed_acyclic_graph(nx.DiGraph(edges + [('Sales', 'A')])), True)  # which is still a DAG
    g.rejects(g.Blocked, lambda: hierarchy([('A', 'B'), ('B', 'A')]))
    g.rejects(g.Blocked, lambda: hierarchy([('R1', 'A'), ('R2', 'B')]))  # two roots
    g.equal(nx.is_forest(nx.DiGraph([('R1', 'A'), ('R2', 'B')])), True)  # which is a forest
    g.rejects(nx.NetworkXUnfeasible, lambda: list(nx.topological_generations(nx.DiGraph([('A', 'B'), ('B', 'A')]))))
    deck = org_deck([('CEO', 'Ops'), ('CEO', 'Sales')])
    ids = shape_ids(deck)
    bindings = connector_bindings(deck)
    g.equal(len(bindings), 2)
    g.equal(sorted(bindings[0]), sorted([str(ids['CEO']), str(ids['Ops'])]))
    g.equal(sorted(bindings[1]), sorted([str(ids['CEO']), str(ids['Sales'])]))
    g.equal(all(len(b) == 2 for b in bindings), True)
    return {'arborescence_rejects_a_second_parent_a_dag_accepts': True,
            'two_roots_are_a_forest_not_an_arborescence': True,
            'connectors_carry_the_exact_shape_ids': True}


@case(189)
def acceptance_needs_a_hash_match_and_an_executed_criterion():
    artifact = b'workbook bytes'
    declared = hashlib.sha256(artifact).hexdigest()
    g.equal(evidence(artifact, declared), declared)
    g.rejects(g.Blocked, lambda: evidence(artifact + b'.', declared))
    g.rejects(g.Blocked, lambda: evidence(artifact, '0' * 64))
    passing = [{'id': 'C%d' % n, 'result': 'passed'} for n in range(5)]
    signed = {'state': 'signed', 'on': '2026-09-17'}
    g.equal(acceptance_state(passing, signed, cutoff='2026-09-18'), 'accepted')
    g.equal(acceptance_state(passing, signed, cutoff='2026-09-16'), 'not accepted: the record post-dates the cutoff')
    g.equal(acceptance_state(passing, None, cutoff='2026-09-18'), 'not accepted: no signed record')
    g.equal(acceptance_state(passing, {'state': 'draft', 'on': '2026-09-17'}, cutoff='2026-09-18'),
            'not accepted: no signed record')
    g.equal(acceptance_state(passing, {'state': 'withdrawn', 'on': '2026-09-17'}, cutoff='2026-09-18'),
            'not accepted: no signed record')
    not_run = passing + [{'id': 'C7', 'result': 'not_run'}]
    g.equal(acceptance_state(not_run, signed, cutoff='2026-09-18'), 'incomplete: a criterion was not executed')
    g.equal(acceptance_state(not_run, signed, cutoff='2026-09-18') != 'accepted', True)  # a signoff cannot fill the gap
    failed = passing + [{'id': 'C8', 'result': 'failed'}]
    g.equal(acceptance_state(failed, signed, cutoff='2026-09-18'), 'not accepted: a criterion failed')
    g.equal(acceptance_state(not_run, signed, cutoff='2026-09-18')
            != acceptance_state(failed, signed, cutoff='2026-09-18'), True)  # not run is not the same as failed
    return {'changed_bytes_break_the_evidence_binding': True,
            'a_signoff_cannot_cover_an_unexecuted_criterion': True,
            'not_run_and_failed_stay_distinct': True}


@case(190)
def an_in_memory_edit_leaves_the_source_presentation_alone():
    source = status_deck((2350.0, 1900.0, 2090.0))
    g.equal(chart_values(source), [2350.0, 1900.0, 2090.0])
    before = hashlib.sha256(source).hexdigest()
    edited = edited_copy(source, (2350.0, 1900.0, 9999.0))
    g.equal(chart_values(edited), [2350.0, 1900.0, 9999.0])
    g.equal(chart_values(source), [2350.0, 1900.0, 2090.0])  # the source is untouched
    g.equal(hashlib.sha256(source).hexdigest(), before)
    g.equal(hashlib.sha256(edited).hexdigest() == before, False)
    unknown = edited_copy(source, (2350.0, None, None))
    g.equal(chart_values(unknown), [2350.0, None, None])  # unknown current values stay unknown
    g.equal(chart_values(unknown)[1] is None, True)
    g.equal(chart_values(unknown)[0], 2350.0)  # while the labelled earlier snapshot stays visible
    return {'edit_is_isolated_to_the_copy': True, 'unknown_values_survive_as_none': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['duckdb', 'Jinja2', 'lxml', 'networkx', 'pandas', 'Pint', 'python-dateutil', 'python-pptx']
    here = Path(__file__).resolve().parent
    return {'scope': 'Bounded authored passage, maintenance, training, inspection, renewal, progress, earned-value, hierarchy, acceptance and status fixtures and reproduced library defaults; the original P181-P190 chains and their artifacts were not rerun.',
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
