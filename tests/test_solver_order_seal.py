"""Difference logic over precedes atoms, the forced-precedence graph, and the seal."""

from __future__ import annotations

from compiled_ai.model import Atom, Manifest
from compiled_ai.order import order
from compiled_ai.reconcile import reconcile
from compiled_ai.seal import canonical_json, verify_digest


def prec(a: str, b: str, sid: str = "t:u0:s00") -> Atom:
    return Atom(id=f"precedes({a},{b})", predicate="precedes", args=(a, b), sentence_id=sid, tokens=(1,), quote="x")


def test_consistent_chain_is_satisfiable() -> None:
    r = reconcile([prec("a", "b"), prec("b", "c"), prec("a", "c")])
    assert r.consistent and r.checked == 3 and r.cores == ()


def test_injected_cycle_is_reported_as_the_minimal_core() -> None:
    r = reconcile([prec("a", "b"), prec("b", "c"), prec("c", "a"), prec("x", "y")])
    assert not r.consistent
    assert r.cores == (("precedes(a,b)", "precedes(b,c)", "precedes(c,a)"),)


def test_forced_precedence_is_the_transitive_reduction_and_order_is_unique() -> None:
    o = order([prec("a", "b"), prec("b", "c"), prec("a", "c")])
    assert o.forced == (("a", "b"), ("b", "c"))
    assert o.order == ("a", "b", "c")
    assert o.cycle == ()
    cyc = order([prec("a", "b"), prec("b", "a")])
    assert cyc.cycle == (("a", "b"), ("b", "a")) and cyc.order == ()


def test_manifest_digest_verifies_and_detects_tampering() -> None:
    from compiled_ai.model import AtomSeal

    m = Manifest(
        pack="t",
        canon_version=1,
        toolchain={"canon": "1"},
        sources=(("s", "d" * 64),),
        atoms=(AtomSeal(id="event(x,y)", sentence_id="s", sentence_digest="a" * 64, quote_digest="b" * 64),),
        forced=(("a", "b"),),
        order=("a", "b"),
        consistent=True,
        digest="",
    )
    import hashlib

    body = m.model_dump()
    body.pop("digest")
    body["sources"] = [list(s) for s in body["sources"]]
    body["forced"] = [list(e) for e in body["forced"]]
    sealed = m.model_copy(update={"digest": hashlib.sha256(canonical_json(body).encode()).hexdigest()})
    assert verify_digest(sealed)
    assert not verify_digest(sealed.model_copy(update={"order": ("b", "a")}))
