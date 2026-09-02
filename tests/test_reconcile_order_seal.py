"""Steps 8, 9, 10: an injected contradiction is reported as exactly the pair that conflicts;
a cross-scope conflict is a variation point; a cycle is reported; the seal verifies."""

from __future__ import annotations

from compiled_ai.model import Manifest, RuleSpec
from compiled_ai.order import order
from compiled_ai.reconcile import Constraint, reconcile
from compiled_ai.seal import canonical_json, verify_digest


def c(id: str, scope: str, kind: str, subject: str, text: str) -> Constraint:
    return Constraint(id=id, scope=scope, sentence_id=id, kind=kind, subject=subject, text=text)


def test_consistent_set_is_consistent() -> None:
    r = reconcile([c("a", "s", "clock", "determination", "20 working_days"), c("b", "s", "clock", "appeal", "20 working_days")])
    assert r.consistent and not r.contradictions and not r.variations and r.checked == 2


def test_injected_contradiction_is_reported_as_the_minimal_pair() -> None:
    cs = [
        c("a", "s", "clock", "determination", "20 working_days"),
        c("b", "s", "clock", "appeal", "20 working_days"),
        c("x", "s", "clock", "determination", "10 working_days"),
        c("d", "s", "decider", "appeal", "head of the agency"),
    ]
    r = reconcile(cs)
    assert not r.consistent
    assert r.contradictions == (("a", "x"),)
    assert r.variations == ()


def test_cross_scope_conflict_is_a_variation_point() -> None:
    cs = [
        c("statute", "statute", "clock", "determination", "20 working_days"),
        c("agency-reg", "agency-reg", "clock", "determination", "10 working_days"),
    ]
    r = reconcile(cs)
    assert r.consistent
    assert r.variations == (("agency-reg", "statute"),)


def test_conflicting_deciders_are_a_contradiction() -> None:
    cs = [c("p", "s", "decider", "appeal", "head of the agency"), c("q", "s", "decider", "appeal", "the vendor")]
    r = reconcile(cs)
    assert r.contradictions == (("p", "q"),)


def test_order_is_unique_and_cycle_is_reported() -> None:
    o = order([("receipt", "determination", "s1"), ("determination", "notice", "s2"), ("receipt", "search", "s3")])
    assert o.order == ("receipt", "determination", "notice", "search")
    assert o.cycle == ()
    cyc = order([("a", "b", "s1"), ("b", "a", "s2")])
    assert cyc.order == ()
    assert cyc.cycle == (("a", "b"), ("b", "a"))


def test_manifest_digest_verifies_and_detects_tampering() -> None:
    spec = RuleSpec(id="r", sentence_id="s", sentence_digest="d" * 64, path="(a)", kind="step", function="f", function_digest="e" * 64, quote="q", provisional=True)
    from compiled_ai.seal import seal

    m = seal("t", [], [spec], ["a", "b"])
    assert verify_digest(m)
    tampered = Manifest.model_validate({**m.model_dump(), "order": ["b", "a"]})
    assert not verify_digest(tampered)
    assert canonical_json({"b": 1, "a": [1, 2]}) == '{"a":[1,2],"b":1}'
