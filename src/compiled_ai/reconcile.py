"""Step 8, reconcile: can all the rules be true at once? Symbolic.

Each confirmed statement contributes constraints:

- a clock: the deadline for its subject equals its amount, in its unit;
- a reserved decision: the decider for its decision equals its role.

The solver checks that the constraints of every scope taken together are
satisfiable. When they are not, it returns a minimal set of statements that
cannot all be true. The set is minimized here by deletion, so it does not
depend on the solver's own core minimization, which its documentation does
not guarantee. A minimal set is one that cannot be shrunk; it is not
necessarily the smallest.

A conflicting set whose statements come from more than one scope is a
variation point: the same subject is governed differently in different
places. A conflicting set inside one scope is a contradiction and fails the
build.

Solver settings are fixed: seeds zero, a resource limit instead of a
wall-clock timeout, because the documentation says wall-clock timeouts are
non-deterministic and the resource limit is not.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .model import Statement, Strict

UNIT_CODES = {"days": 1, "calendar_days": 1, "working_days": 2, "business_days": 3, "months": 4, "years": 5}


class Constraint(Strict):
    id: str
    scope: str
    sentence_id: str
    kind: str
    subject: str
    text: str


class Reconciliation(Strict):
    consistent: bool
    contradictions: tuple[tuple[str, ...], ...]
    variations: tuple[tuple[str, ...], ...]
    checked: int


def constraints_from(statements: Iterable[Statement], scope_of: dict[str, str]) -> list[Constraint]:
    out: list[Constraint] = []
    for st in statements:
        p = st.proposal
        scope = scope_of.get(st.sentence.source_id, st.sentence.source_id)
        if p.clock is not None:
            out.append(
                Constraint(
                    id=f"{st.sentence.id}:clock:{p.clock.subject}",
                    scope=scope,
                    sentence_id=st.sentence.id,
                    kind="clock",
                    subject=p.clock.subject,
                    text=f"{p.clock.amount} {p.clock.unit}",
                )
            )
        if p.kind == "reserved_decision" and p.role and p.subject:
            out.append(
                Constraint(
                    id=f"{st.sentence.id}:decider:{p.subject}",
                    scope=scope,
                    sentence_id=st.sentence.id,
                    kind="decider",
                    subject=p.subject,
                    text=p.role,
                )
            )
    return sorted(out, key=lambda c: c.id)


def _encode(z3: Any, constraints: list[Constraint]) -> tuple[Any, dict[str, Any]]:
    """Return a solver and a map from tracking name to constraint id."""
    z3.set_param("smt.random_seed", 0)
    z3.set_param("sat.random_seed", 0)
    z3.set_param("smt.core.minimize", True)
    z3.set_param("sat.core.minimize", True)
    s = z3.Solver()
    s.set("rlimit", 5_000_000)
    ints: dict[str, Any] = {}
    roles: dict[str, int] = {}
    track: dict[str, Any] = {}
    for c in constraints:
        if c.kind == "clock":
            amount_s, unit_s = c.text.split(" ", 1)
            amount = ints.setdefault(f"deadline::{c.subject}", z3.Int(f"deadline::{c.subject}"))
            unit = ints.setdefault(f"unit::{c.subject}", z3.Int(f"unit::{c.subject}"))
            expr = z3.And(amount == int(amount_s), unit == UNIT_CODES[unit_s])
        else:
            code = roles.setdefault(c.text, len(roles) + 1)
            decider = ints.setdefault(f"decider::{c.subject}", z3.Int(f"decider::{c.subject}"))
            expr = decider == code
        p = z3.Bool(f"track::{c.id}")
        s.assert_and_track(expr, p)
        track[str(p)] = c.id
    return s, track


def _is_sat(z3: Any, constraints: list[Constraint]) -> bool:
    s, _ = _encode(z3, constraints)
    r = s.check()
    if r == z3.unknown:
        raise RuntimeError("solver returned unknown; raise the resource limit")
    return bool(r == z3.sat)


def _minimal_unsat_subset(z3: Any, constraints: list[Constraint]) -> list[Constraint]:
    """Deletion-based minimization: deterministic given the sorted input."""
    core = list(constraints)
    i = 0
    while i < len(core):
        trial = core[:i] + core[i + 1 :]
        if not _is_sat(z3, trial):
            core = trial
        else:
            i += 1
    return core


def reconcile(constraints: list[Constraint]) -> Reconciliation:
    import z3  # compiler-only dependency

    contradictions: list[tuple[str, ...]] = []
    variations: list[tuple[str, ...]] = []
    remaining = sorted(constraints, key=lambda c: c.id)
    # Iterate: find one minimal conflicting set, classify it, drop one member,
    # and continue until the rest is satisfiable.
    guard = 0
    while remaining and not _is_sat(z3, remaining):
        guard += 1
        if guard > 1000:
            raise RuntimeError("too many conflicting sets")
        s, track = _encode(z3, remaining)
        s.check()
        core_ids = sorted(track[str(p)] for p in s.unsat_core())
        core = _minimal_unsat_subset(z3, [c for c in remaining if c.id in core_ids])
        ids = tuple(c.id for c in core)
        scopes = {c.scope for c in core}
        (variations if len(scopes) > 1 else contradictions).append(ids)
        remaining = [c for c in remaining if c.id != core[-1].id]
    return Reconciliation(
        consistent=not contradictions,
        contradictions=tuple(contradictions),
        variations=tuple(variations),
        checked=len(constraints),
    )
