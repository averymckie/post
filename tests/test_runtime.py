"""Guarantees G3 and G7 on the sealed FOIA pack: the runtime is total, and every route
names a decision and a role the source reserves."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from compiled_ai.model import Proof, Reasons
from compiled_ai.pack import load_manifest, load_record_type, load_rules
from compiled_ai.runtime import Runtime

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "foia"


def runtime() -> Runtime:
    return Runtime(load_manifest(PACK / "build" / "manifest.json"), load_rules(PACK), load_record_type(PACK))


json_scalars = st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False) | st.text(max_size=20)
json_values = st.recursive(json_scalars, lambda s: st.lists(s, max_size=4) | st.dictionaries(st.text(max_size=8), s, max_size=4), max_leaves=12)


@given(st.dictionaries(st.text(max_size=12), json_values, max_size=6))
@settings(max_examples=200)
def test_runtime_never_raises_on_arbitrary_input(raw: dict[str, object]) -> None:
    rt = runtime()
    result = rt.evaluate(raw)
    assert isinstance(result, (Proof, Reasons))
    if isinstance(result, Reasons):
        assert result.reasons


dates = st.dates(min_value=date(2025, 1, 5), max_value=date(2027, 12, 20))
notice = st.builds(
    dict,
    sent_on=dates.map(date.isoformat),
    states_determination=st.booleans(),
    states_reasons=st.booleans(),
    states_liaison_assistance=st.booleans(),
    states_appeal_right=st.booleans(),
    appeal_period_days=st.none() | st.integers(min_value=0, max_value=200),
    states_dispute_resolution=st.booleans(),
    states_judicial_review=st.booleans(),
    names_and_titles_of_responsible_persons=st.lists(st.sampled_from(["A. Officer, Chief"]), max_size=2),
)
withholding = st.builds(
    dict,
    exemption=st.sampled_from(["(b)(1)", "(b)(4)", "(b)(6)", "(b)(7)", "(b)(9)", "(c)(1)", "b6"]),
    exemption_conditions_found=st.none() | st.booleans(),
    harm_finding_recorded=st.none() | st.booleans(),
    prohibited_by_law=st.booleans(),
    amount_deleted_indicated=st.booleans(),
    indication_would_harm=st.none() | st.booleans(),
)
records = st.builds(
    dict,
    as_of=dates.map(date.isoformat),
    received_by_designated_component_on=dates.map(date.isoformat),
    received_by_appropriate_component_on=st.none() | dates.map(date.isoformat),
    expedited_processing_requested=st.booleans(),
    expedited_determination_on=st.none() | dates.map(date.isoformat),
    expedited_notice_on=st.none() | dates.map(date.isoformat),
    determination=st.sampled_from(["comply", "deny", "partial", "pending"]),
    determination_on=st.none() | dates.map(date.isoformat),
    determination_notice=st.none() | notice,
    records_made_available_on=st.none() | dates.map(date.isoformat),
    withholdings=st.lists(withholding, max_size=3),
    full_disclosure_possible=st.none() | st.booleans(),
    partial_disclosure_considered=st.none() | st.booleans(),
    segregability_review_recorded=st.none() | st.booleans(),
    tolling=st.lists(st.builds(dict, information_requested_on=dates.map(date.isoformat), response_received_on=st.none() | dates.map(date.isoformat), agency_finds_request_reasonable=st.none() | st.booleans()), max_size=3),
)


def reserved_decisions() -> set[tuple[str, str]]:
    data = yaml.safe_load((PACK / "reserved.yaml").read_text(encoding="utf-8"))
    return {(d["decision"], d["role"]) for d in data["decisions"]}


@given(records)
@settings(max_examples=300)
def test_every_route_names_a_reserved_decision_and_results_are_provisional(raw: dict[str, object]) -> None:
    rt = runtime()
    result = rt.evaluate(raw)
    assert isinstance(result, (Proof, Reasons))
    allowed = reserved_decisions()
    for route in result.routes:
        assert (route.decision, route.role) in allowed
    assert result.provisional is True
    assert result.manifest_digest == rt.manifest.digest


@given(records)
@settings(max_examples=300)
def test_pending_determination_is_always_routed_to_the_agency(raw: dict[str, object]) -> None:
    result = runtime().evaluate({**raw, "determination": "pending"})
    assert isinstance(result, (Proof, Reasons))
    assert ("whether to comply with the request", "agency") in {(r.decision, r.role) for r in result.routes}


def test_a_clean_case_is_a_proof_with_sentences_attached() -> None:
    case = json.loads((PACK / "cases" / "clean-partial-grant.json").read_text(encoding="utf-8"))
    result = runtime().evaluate(case)
    assert isinstance(result, Proof), getattr(result, "reasons", None)
    assert all(a.quote and a.path for a in result.applied)
    assert {a.rule_id for a in result.applied} >= {"foia.determination_clock", "foia.notice_reasons", "foia.denial_names"}


def test_a_late_denial_without_names_lists_the_clauses_tripped() -> None:
    case = json.loads((PACK / "cases" / "late-denial-without-names.json").read_text(encoding="utf-8"))
    result = runtime().evaluate(case)
    assert isinstance(result, Reasons)
    codes = {r.code for r in result.reasons}
    assert {"DETERMINATION_LATE", "DENIAL_WITHOUT_NAMES", "NOTICE_WITHOUT_REASONS"} <= codes
    for r in result.reasons:
        assert r.quote and r.path and r.remedy
