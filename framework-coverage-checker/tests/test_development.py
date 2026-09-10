"""Authored development tests. These do not claim inherited GP01 qualification."""
import json
from copy import deepcopy
from pathlib import Path
import pytest
from hypothesis import given, strategies as st, settings
from jsonschema import ValidationError
from fwcheck.logic import implication, solve_pair
from fwcheck.io import InputError, read_json, digest
from fwcheck.construction import check_project, validate_witness, inventory_hash
from fwcheck.catalogue import index_framework
from fwcheck.certificate import make_certificate, replay
from fwcheck.finite import check_state_model, derive_obligations
from examples.make_examples import planning_example

ROOT = Path(__file__).resolve().parents[1]


def test_three_stage_recursive_construction_and_proof_gap():
    p = planning_example()
    r = check_project(p)
    assert r["construction_status"] == "MODEL_RECONSTRUCTED"
    assert set(r["witness"]["witness"]["selected"]) == {"formalize", "schedule", "release"}
    assert r["coverage_status"] == "PROOF_GAP"
    assert len(r["proof_gaps"]) == 3


def test_joint_shared_resource_failure_retains_counterexample():
    p = read_json(ROOT / "examples/overbooked.json")
    r = check_project(p)
    assert r["construction_status"] == "NO_CONSTRUCTION_IN_DECLARED_CATALOGUE_AND_BOUNDS"
    assert r["search_exhausted"]
    check = next(x for x in r["candidates"][0]["validation"]["checks"] if x["obligation"] == "R2")
    assert check["result"]["status"] == "COUNTEREXAMPLE"
    assert check["result"]["counterexample_query"]["z3"]["model"]["a"] == "5"


@pytest.mark.parametrize("field", ["schema", "meaning", "identity", "time", "basis", "coverage", "authority", "state", "effects", "numeric", "resources", "evidence", "change", "exceptions"])
def test_boundary_field_swap_cannot_be_implicitly_adapted(field):
    p = planning_example()
    p["components"][2]["inputs"][0]["envelope"][field] = "incompatible"
    r = check_project(p)
    assert r["construction_status"] == "NO_CONSTRUCTION_IN_DECLARED_CATALOGUE_AND_BOUNDS"
    assert r["candidate_count"] == 0


def test_dropped_requirement_rejected():
    p = planning_example()
    p["requirements"].pop()
    with pytest.raises(InputError, match="inventory mismatch"):
        check_project(p)


def test_changed_predicate_invalidates_acceptance():
    p = planning_example()
    p["requirements"][0]["predicate"] = True
    with pytest.raises(InputError, match="inventory"):
        check_project(p)


def test_changed_baseline_rejected():
    with pytest.raises(InputError, match="Framework hash"):
        check_project(planning_example(), "a" * 64)


def test_vacuity_is_not_implication_success():
    assert implication({"x": "Int"}, {"and": [{">": ["x", 3]}, {"<": ["x", 2]}]}, True)["status"] == "VACUOUS"


def test_incompatible_consumer_contract():
    p = planning_example()
    p["components"][2]["inputs"][0]["requires"] = {">": ["a", 4]}
    r = check_project(p)
    assert r["candidates"][0]["validation"]["status"] == "CONSTRUCTION_FAILED"


def test_cycle_and_missing_prerequisite_rejected():
    p = planning_example()
    p["components"][0]["inputs"][0]["envelope"] = deepcopy(p["components"][2]["outputs"][0]["envelope"])
    assert check_project(p)["candidate_count"] == 0


def test_graph_replay_rejects_open_input_and_extraneous_component():
    p = planning_example()
    w = check_project(p)["witness"]["witness"]
    w["bindings"].pop("formalize:in")
    assert validate_witness(p, w)["status"] == "INVALID_WITNESS"


def test_search_bound_does_not_claim_universal_absence():
    p = planning_example()
    p["limits"]["max_components"] = 2
    r = check_project(p)
    assert r["construction_status"] == "NO_CONSTRUCTION_IN_DECLARED_CATALOGUE_AND_BOUNDS"
    assert r["coverage_status"] == "UNESTABLISHED"


def test_unsupported_grammar_not_silently_flattened():
    p = planning_example()
    p["grammar"].append("Feedback")
    assert check_project(p)["construction_status"] == "UNSUPPORTED_ENCODING"


def test_duplicate_json_keys_and_nonfinite(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text('{"x":1,"x":2}')
    with pytest.raises(InputError, match="Duplicate"):
        read_json(p)
    p.write_text('{"x":NaN}')
    with pytest.raises(InputError, match="Nonfinite"):
        read_json(p)


@pytest.mark.parametrize("expression", [{"*": ["x", "x"]}, {"/": [1, 0]}, {"=": [True, 1]}, {"not": [1]}, {"=": ["absent", 1]}])
def test_unsupported_or_ill_typed_logic(expression):
    with pytest.raises(InputError):
        solve_pair({"x": "Int"}, expression)


@given(st.integers(-1000, 1000), st.integers(-1000, 1000))
def test_implication_threshold_matches_order(lower, required):
    r = implication({"x": "Int"}, {">=": ["x", lower]}, {">=": ["x", required]})
    assert r["status"] == ("PROVED" if lower >= required else "COUNTEREXAMPLE")


@given(st.integers(-1000, 1000), st.integers(1, 1000))
def test_exact_rational_cross_engine(numerator, denominator):
    q = {"rat": f"{numerator}/{denominator}"}
    assert solve_pair({"x": "Real"}, {"=": ["x", q]})["status"] == "sat"
    assert solve_pair({"x": "Real"}, {"and": [{"=": ["x", q]}, {"!=": ["x", q]}]})["status"] == "unsat"


def test_full_catalogue_includes_f29_proof_outside_short_anchors():
    ix = index_framework(ROOT / "data/framework-baseline.txt")
    assert len(ix["families"]) == 38
    assert len(ix["proofs"]) == 349
    assert "P99" in ix["proofs"]


def test_certificate_replay_and_tamper_detection():
    p = planning_example()
    r = check_project(p)
    cert = make_certificate(p, r)
    ix = index_framework(ROOT / "data/framework-baseline.txt")
    assert replay(p, cert, ix)["status"] == "REPLAY_MATCH"
    cert["result"]["coverage_status"] = "COVERED"
    with pytest.raises(InputError, match="integrity"):
        replay(p, cert, ix)
    cert["sha256"] = digest({k: v for k, v in cert.items() if k != "sha256"})
    with pytest.raises(InputError, match="differs"):
        replay(p, cert, ix)


def test_state_checker_finds_effect_after_revocation():
    r = check_state_model(read_json(ROOT / "examples/revocation-states.json"))
    assert r["status"] == "COUNTEREXAMPLE"
    assert r["unsafe_reachable"] == ["effect_after_revocation"]


def test_state_checker_safe_and_nonterminal_deadlock():
    m = read_json(ROOT / "examples/revocation-states.json")
    m["transitions"].pop()
    r = check_state_model(m)
    assert r["nonterminal_deadlocks"] == ["revoked"]
    m["terminal"].append("revoked")
    assert check_state_model(m)["status"] == "FINITE_SAFETY_PASS"


def test_obligations_include_interactions_and_exclude_absent_features():
    r = derive_obligations(read_json(ROOT / "examples/interaction-rules.json"))
    assert r["status"] == "FINITE_RULE_PARITY_PASS"
    assert r["derived"] == ["all_branches_complete", "joint_resource_bound"]


def test_unknown_propagates_without_relabeling(monkeypatch):
    from fwcheck import logic
    monkeypatch.setattr(logic, "z3_query", lambda *a, **kw: {"status": "unknown", "reason": "injected timeout"})
    monkeypatch.setattr(logic, "cvc5_query", lambda *a, **kw: {"status": "unknown", "reason": "injected timeout"})
    assert logic.implication({}, True, True)["status"] == "UNKNOWN"


def test_engine_disagreement_is_blocking(monkeypatch):
    from fwcheck import logic
    monkeypatch.setattr(logic, "z3_query", lambda *a, **kw: {"status": "sat"})
    monkeypatch.setattr(logic, "cvc5_query", lambda *a, **kw: {"status": "unsat"})
    assert logic.solve_pair({}, True)["status"] == "ENGINE_DISAGREEMENT"


def test_search_can_recover_with_an_alternative_supplier():
    p = read_json(ROOT / "examples/overbooked.json")
    alternative = deepcopy(p["components"][1])
    alternative["id"] = "schedule_alternative"
    alternative["outputs"][0]["guarantee"] = {"and": ["scheduled", {"=": ["a", 2]}, {"=": ["b", 3]}]}
    p["components"].append(alternative)
    r = check_project(p)
    assert r["construction_status"] == "MODEL_RECONSTRUCTED"
    assert "schedule_alternative" in r["witness"]["witness"]["selected"]


def test_failed_first_candidate_is_not_exhaustive_absence():
    p = read_json(ROOT / "examples/overbooked.json")
    alternative = deepcopy(p["components"][1])
    alternative["id"] = "another_overbooked_schedule"
    p["components"].append(alternative)
    p["limits"]["max_candidates"] = 1
    r = check_project(p)
    assert r["construction_status"] == "SEARCH_INCOMPLETE"
    assert r["search_stop_reason"] == "CANDIDATE_LIMIT"
    assert not r["search_exhausted"]
    p["limits"]["max_candidates"] = 100
    exhaustive = check_project(p)
    assert exhaustive["candidate_count"] == 2
    assert exhaustive["search_exhausted"]


def test_replay_validator_independently_rejects_cycle():
    p = planning_example()
    witness = check_project(p)["witness"]["witness"]
    p["components"][0]["inputs"][0]["envelope"] = deepcopy(p["components"][2]["outputs"][0]["envelope"])
    witness["bindings"]["formalize:in"] = "release:out"
    r = validate_witness(p, witness)
    assert r["status"] == "INVALID_WITNESS"
    assert r["checks"][0]["result"]["status"] == "unsat"


def test_solver_unknown_blocks_complete_search(monkeypatch):
    from fwcheck import logic
    monkeypatch.setattr(logic, "z3_query", lambda *a, **kw: {"status": "unknown"})
    monkeypatch.setattr(logic, "cvc5_query", lambda *a, **kw: {"status": "unknown"})
    r = check_project(planning_example())
    assert r["construction_status"] == "SEARCH_INCOMPLETE"
    assert r["coverage_status"] == "UNESTABLISHED"
