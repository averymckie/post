"""Reconcile: the precedes atoms as a difference-logic constraint set.

Each event E gets an integer time t(E). Each precedes(E1, E2) atom asserts
t(E1) - t(E2) <= -1. Z3 decides whether the set is satisfiable; satisfiability
certifies that the ordering claims of the corpus are jointly consistent. When
the set is unsatisfiable, a minimal conflicting set of atoms is returned. Z3
does not guarantee a minimal core, so the core is minimized here by deletion
in a fixed order. Seeds are fixed and a resource limit replaces a wall-clock
timeout.
"""

from __future__ import annotations

from typing import Any

from .model import Atom, Reconciliation


def _encode(z3: Any, precedes: list[Atom]) -> tuple[Any, dict[str, str]]:
    z3.set_param("smt.random_seed", 0)
    z3.set_param("sat.random_seed", 0)
    z3.set_param("smt.core.minimize", True)
    z3.set_param("sat.core.minimize", True)
    s = z3.Solver()
    s.set("rlimit", 20_000_000)
    times: dict[str, Any] = {}
    track: dict[str, str] = {}
    for i, a in enumerate(precedes):
        e1, e2 = a.args
        t1 = times.setdefault(e1, z3.Int(e1))
        t2 = times.setdefault(e2, z3.Int(e2))
        p = z3.Bool(f"p{i}")
        s.assert_and_track(t1 - t2 <= -1, p)
        track[str(p)] = a.id
    return s, track


def _sat(z3: Any, precedes: list[Atom]) -> bool:
    s, _ = _encode(z3, precedes)
    r = s.check()
    if r == z3.unknown:
        raise RuntimeError("solver returned unknown; raise the resource limit")
    return bool(r == z3.sat)


def _minimal(z3: Any, atoms: list[Atom]) -> list[Atom]:
    core = list(atoms)
    i = 0
    while i < len(core):
        trial = core[:i] + core[i + 1 :]
        if not _sat(z3, trial):
            core = trial
        else:
            i += 1
    return core


def reconcile(atoms: list[Atom]) -> Reconciliation:
    import z3

    precedes = sorted((a for a in atoms if a.predicate == "precedes"), key=lambda a: a.id)
    remaining = list(precedes)
    cores: list[tuple[str, ...]] = []
    guard = 0
    while remaining and not _sat(z3, remaining):
        guard += 1
        if guard > 10_000:
            raise RuntimeError("too many conflicting sets")
        s, track = _encode(z3, remaining)
        s.check()
        core_ids = sorted(track[str(p)] for p in s.unsat_core())
        core = _minimal(z3, [a for a in remaining if a.id in core_ids])
        cores.append(tuple(a.id for a in core))
        remaining = [a for a in remaining if a.id != core[-1].id]
    return Reconciliation(consistent=not cores, checked=len(precedes), cores=tuple(cores))
