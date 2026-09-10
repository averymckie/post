"""Author illustrative model fixtures. These are NOT original-corpus completions.

Hand-authored demonstration cases are excluded from inherited guard qualification.
"""
from copy import deepcopy
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fwcheck.io import digest, file_hash, write_json
from fwcheck.schema import BOUNDARY_FIELDS
from fwcheck.construction import inventory_hash

ROOT = Path(__file__).resolve().parents[1]


def envelope(stage):
    base = {k: "explicitly_outside_this_formal_model" for k in BOUNDARY_FIELDS}
    base.update(schema=f"{stage}.v1", meaning=f"accepted_{stage}_contract", identity="job-1", time="one_finite_batch",
                basis="SCENARIO", coverage="declared_job_only", numeric="integer_hours", resources="staff-pool-1",
                evidence="ASSUMED_COMPONENT_CONTRACT", exceptions="failure_not_modeled")
    return base


def planning_example():
    source_text = "Illustrative bounded scheduling model: derive a released plan through three prerequisites; total staff use must not exceed eight hours. This is not UC-00078 or a completion of its missing details."
    clauses = [{"id": "C1", "text": "Produce a released plan whose declared work is complete"},
               {"id": "C2", "text": "The two concurrent branches share a capacity of eight staff-hours"}]
    p = {"format": "fwcheck.case.v1", "id": "DEMO-PLAN-THREE-STAGES",
         "source_sha256": digest(source_text), "framework_sha256": file_hash(ROOT / "data/framework-baseline.txt"),
         "variables": {"capacity": "Int", "a": "Int", "b": "Int", "tasks": "Bool", "scheduled": "Bool", "released": "Bool"},
         "context": {"=": ["capacity", 8]}, "source_clauses": clauses,
         "semantic_review": {"status": "DRAFT", "reviewer": "analyst-authored demonstration; no claim of user-approved world semantics", "inventory_sha256": "0" * 64},
         "sources": [{"id": "accepted_request", "envelope": envelope("request"), "guarantee": True}],
         "components": [], "requirements": [
             {"id": "R1", "source_clause": "C1", "predicate": "released", "envelope": envelope("plan")},
             {"id": "R2", "source_clause": "C2", "predicate": {"<=": [{"+": ["a", "b"]}, "capacity"]}, "envelope": None}],
         "grammar": ["Seq", "ForkJoin"], "acceptance_scope": "FORMAL_MODEL",
         "limits": {"max_components": 6, "max_candidates": 100, "timeout_ms": 3000, "search_seconds": 30}}
    for id_, fam, refs, before, after, pre, post in [
        ("formalize", "F01", ["P191"], "request", "tasks", True, "tasks"),
        ("schedule", "F11", ["P222"], "tasks", "schedule", "tasks", {"and": ["scheduled", {"=": ["a", 3]}, {"=": ["b", 4]}]}),
        ("release", "F29", ["P25", "P99"], "schedule", "plan", "scheduled", "released")]:
        p["components"].append({"id": id_, "family": fam, "proof_refs": refs,
                                 "inputs": [{"id": "in", "envelope": envelope(before), "requires": pre}],
                                 "outputs": [{"id": "out", "envelope": envelope(after), "guarantee": post}],
                                 "requires": True, "profile_origin": "ANALYST_PROPOSED", "external_effect": False})
    p["semantic_review"]["inventory_sha256"] = inventory_hash(p)
    return p


if __name__ == "__main__":
    p = planning_example()
    write_json(ROOT / "examples/planning.json", p)
    bad = deepcopy(p)
    bad["id"] = "DEMO-PLAN-OVERBOOKED"
    bad["components"][1]["outputs"][0]["guarantee"] = {"and": ["scheduled", {"=": ["a", 5]}, {"=": ["b", 5]}]}
    write_json(ROOT / "examples/overbooked.json", bad)
    swapped = deepcopy(p)
    swapped["id"] = "DEMO-WRONG-BASIS"
    swapped["components"][2]["inputs"][0]["envelope"]["basis"] = "OBSERVATION"
    write_json(ROOT / "examples/wrong-basis.json", swapped)
    states = {"format": "fwcheck.states.v1", "id": "DEMO-REVOCATION", "states": ["active", "revoked", "effect_after_revocation"],
              "initial": ["active"], "unsafe": ["effect_after_revocation"], "terminal": ["effect_after_revocation"],
              "transitions": [{"from": "active", "to": "revoked"}, {"from": "revoked", "to": "effect_after_revocation"}],
              "interpretation": "Illustrative abstract consent bug; these transitions are supplied assumptions, not observed implementation traces"}
    write_json(ROOT / "examples/revocation-states.json", states)
    rules = {"format": "fwcheck.obligations.v1", "id": "DEMO-INTERACTIONS", "features": ["fork", "shared_staff", "external_effect"],
             "selected": ["fork", "shared_staff"], "rules": [
                 {"id": "O1", "all_of": ["fork"], "obligation": "all_branches_complete"},
                 {"id": "O2", "all_of": ["fork", "shared_staff"], "obligation": "joint_resource_bound"},
                 {"id": "O3", "all_of": ["external_effect"], "obligation": "actual_receipt"}],
             "reviewed_rule_scope": "Demonstration table only; not the complete framework grammar-to-obligation relation"}
    write_json(ROOT / "examples/interaction-rules.json", rules)
