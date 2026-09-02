"""Invariants of the FOIA pack: properties that must never break, searched with
Hypothesis under the deterministic profile, plus the confirmed examples as
permanent tests."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from hypothesis import example, given, settings
from hypothesis import strategies as st

from compiled_ai.model import Proof, Reasons
from compiled_ai.pack import load_manifest, load_record_type, load_rules
from compiled_ai.runtime import Runtime
from packs.foia.calendar import add_working_days, is_working_day, legal_public_holidays, working_days_between
from packs.foia.record import Notice, Record, Withholding
from packs.foia.rules import determination_deadline

PACK = Path(__file__).resolve().parents[1]


def runtime() -> Runtime:
    return Runtime(load_manifest(PACK / "build" / "manifest.json"), load_rules(PACK), load_record_type(PACK))


# ------------------------------------------------------------------ calendar


def test_observed_holidays_2026() -> None:
    h = legal_public_holidays(2026)
    assert date(2026, 1, 1) in h  # New Year's Day, Thursday
    assert date(2026, 1, 19) in h  # Birthday of Martin Luther King, Jr., third Monday
    assert date(2026, 2, 16) in h  # Washington's Birthday, third Monday
    assert date(2026, 5, 25) in h  # Memorial Day, last Monday
    assert date(2026, 6, 19) in h  # Juneteenth, Friday
    assert date(2026, 7, 3) in h and date(2026, 7, 4) not in h  # Independence Day on a Saturday is observed Friday
    assert date(2026, 9, 7) in h  # Labor Day, first Monday
    assert date(2026, 10, 12) in h  # Columbus Day, second Monday
    assert date(2026, 11, 11) in h  # Veterans Day, Wednesday
    assert date(2026, 11, 26) in h  # Thanksgiving, fourth Thursday
    assert date(2026, 12, 25) in h  # Christmas, Friday


def test_twenty_working_days_after_a_monday_skips_a_holiday() -> None:
    # 2026-01-05 is a Monday; 2026-01-19 is a holiday; twenty working days land on 2026-02-03.
    assert add_working_days(date(2026, 1, 5), 20) == date(2026, 2, 3)
    assert add_working_days(date(2026, 3, 2), 20) == date(2026, 3, 30)


@given(st.dates(min_value=date(2025, 1, 1), max_value=date(2027, 12, 1)), st.integers(min_value=0, max_value=40))
def test_working_day_arithmetic_is_consistent(start: date, n: int) -> None:
    end = add_working_days(start, n)
    assert working_days_between(start, end) == n
    assert n == 0 or is_working_day(end)
    assert end >= start


# ----------------------------------------------------------------- invariants

dates = st.dates(min_value=date(2025, 1, 5), max_value=date(2027, 12, 1))


def notice(**kw: object) -> Notice:
    base: dict[str, object] = dict(
        sent_on=date(2026, 3, 25), states_determination=True, states_reasons=True, states_liaison_assistance=True,
        states_appeal_right=True, appeal_period_days=90, states_dispute_resolution=True,
        names_and_titles_of_responsible_persons=("J. Smith, FOIA Officer",),
    )
    base.update(kw)
    return Notice(**base)  # type: ignore[arg-type]


@given(received=dates, delay_working_days=st.integers(min_value=21, max_value=80))
@example(received=date(2026, 1, 5), delay_working_days=21)
def test_a_determination_after_the_period_never_yields_a_proof(received: date, delay_working_days: int) -> None:
    determined = add_working_days(received, delay_working_days)
    rec = Record(
        as_of=determined + timedelta(days=1),
        received_by_designated_component_on=received,
        received_by_appropriate_component_on=received,
        determination="comply",
        determination_on=determined,
        determination_notice=notice(sent_on=determined),
        records_made_available_on=determined,
    )
    assert determined > determination_deadline(rec)
    result = runtime().evaluate(rec)
    assert isinstance(result, Reasons)
    assert "DETERMINATION_LATE" in {r.code for r in result.reasons}


@given(received=dates, delay_working_days=st.integers(min_value=0, max_value=20))
@example(received=date(2026, 3, 2), delay_working_days=17)
def test_a_timely_complete_grant_is_a_proof(received: date, delay_working_days: int) -> None:
    determined = add_working_days(received, delay_working_days)
    rec = Record(
        as_of=determined + timedelta(days=1),
        received_by_designated_component_on=received,
        received_by_appropriate_component_on=received,
        determination="comply",
        determination_on=determined,
        determination_notice=notice(sent_on=determined),
        records_made_available_on=determined,
    )
    result = runtime().evaluate(rec)
    assert isinstance(result, Proof), [r.model_dump() for r in result.reasons]
    assert not result.routes


@given(names=st.lists(st.text(min_size=1, max_size=20), max_size=2), determination=st.sampled_from(["deny", "partial"]))
@example(names=[], determination="deny")
def test_no_denial_without_names_is_ever_a_proof(names: list[str], determination: str) -> None:
    rec = Record(
        as_of=date(2026, 4, 1),
        received_by_designated_component_on=date(2026, 3, 2),
        determination=determination,  # type: ignore[arg-type]
        determination_on=date(2026, 3, 20),
        determination_notice=notice(sent_on=date(2026, 3, 20), names_and_titles_of_responsible_persons=tuple(names)),
        records_made_available_on=date(2026, 3, 20),
        withholdings=(Withholding(exemption="(b)(4)", exemption_conditions_found=True, harm_finding_recorded=True, amount_deleted_indicated=True),),
        full_disclosure_possible=False,
        partial_disclosure_considered=True,
        segregability_review_recorded=True,
    )
    result = runtime().evaluate(rec)
    if names:
        assert isinstance(result, Proof), [r.model_dump() for r in result.reasons]
    else:
        assert isinstance(result, Reasons)
        assert "DENIAL_WITHOUT_NAMES" in {r.code for r in result.reasons}


@given(exemption=st.text(min_size=1, max_size=8))
@example(exemption="(b)(10)")
@example(exemption="b6")
def test_an_exemption_outside_the_nine_is_never_accepted(exemption: str) -> None:
    rec = Record(
        as_of=date(2026, 4, 1),
        received_by_designated_component_on=date(2026, 3, 2),
        determination="partial",
        determination_on=date(2026, 3, 20),
        determination_notice=notice(sent_on=date(2026, 3, 20)),
        records_made_available_on=date(2026, 3, 20),
        withholdings=(Withholding(exemption=exemption, exemption_conditions_found=True, harm_finding_recorded=True, amount_deleted_indicated=True),),
        full_disclosure_possible=False,
        partial_disclosure_considered=True,
        segregability_review_recorded=True,
    )
    result = runtime().evaluate(rec)
    valid = exemption in {f"(b)({n})" for n in range(1, 10)}
    if valid:
        assert isinstance(result, Proof), [r.model_dump() for r in result.reasons]
    else:
        assert isinstance(result, Reasons)
        assert "EXEMPTION_NOT_IN_LIST" in {r.code for r in result.reasons}


@settings(max_examples=50)
@given(harm=st.none() | st.booleans(), prohibited=st.booleans())
def test_a_withholding_with_no_recorded_basis_is_routed_or_refused_never_proved(harm: bool | None, prohibited: bool) -> None:
    rec = Record(
        as_of=date(2026, 4, 1),
        received_by_designated_component_on=date(2026, 3, 2),
        determination="partial",
        determination_on=date(2026, 3, 20),
        determination_notice=notice(sent_on=date(2026, 3, 20)),
        records_made_available_on=date(2026, 3, 20),
        withholdings=(Withholding(exemption="(b)(4)", exemption_conditions_found=True, harm_finding_recorded=harm, prohibited_by_law=prohibited, amount_deleted_indicated=True),),
        full_disclosure_possible=False,
        partial_disclosure_considered=True,
        segregability_review_recorded=True,
    )
    result = runtime().evaluate(rec)
    if prohibited or harm is True:
        assert isinstance(result, Proof), [r.model_dump() for r in result.reasons]
    else:
        assert isinstance(result, Reasons)
        if harm is None:
            assert ("whether disclosure would harm an interest protected by an exemption", "agency") in {(r.decision, r.role) for r in result.routes}
