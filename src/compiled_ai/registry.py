"""The rule registry a pack's rules module uses, and the outcomes a rule returns.

A rule is a small function over the pack's typed record. It returns one of
four outcomes. It never raises for a well-typed record; if it does, the
runtime reports the failure as a reason and never as a proof.

This module imports nothing but pydantic and the standard library, so the
runtime image can carry it without any compiler dependency.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from types import ModuleType
from typing import Any, Literal, TypeVar

from .model import Kind, Strict


class Ok(Strict):
    kind: Literal["ok"] = "ok"


class Fail(Strict):
    kind: Literal["fail"] = "fail"
    code: str
    message: str
    remedy: str


class RouteTo(Strict):
    kind: Literal["route"] = "route"
    decision: str
    role: str


class Skip(Strict):
    kind: Literal["skip"] = "skip"


Outcome = Ok | Fail | RouteTo | Skip

RuleFn = Callable[[Any], Outcome]
F = TypeVar("F", bound=Callable[..., Outcome])


class RuleDef(Strict):
    id: str
    statement: str
    kind: Kind
    function: str
    source: str

    model_config = {"extra": "forbid", "frozen": True, "arbitrary_types_allowed": True}


_ATTR = "__compiled_rule__"


def rule(*, id: str, statement: str, kind: Kind) -> Callable[[F], F]:
    """Register a rule function.

    id:        stable rule id, e.g. "foia.determination_clock"
    statement: the checklist entry id the rule implements
    kind:      the statement kind, which must match the checklist entry
    """

    def deco(fn: F) -> F:
        setattr(fn, _ATTR, {"id": id, "statement": statement, "kind": kind})
        return fn

    return deco


def collect_rules(module: ModuleType) -> list[tuple[RuleDef, RuleFn]]:
    """Every registered rule in a module, sorted by id."""
    found: list[tuple[RuleDef, RuleFn]] = []
    for name in sorted(vars(module)):
        obj = getattr(module, name)
        meta = getattr(obj, _ATTR, None)
        if meta is None or not callable(obj):
            continue
        src = inspect.getsource(obj)
        found.append(
            (
                RuleDef(id=meta["id"], statement=meta["statement"], kind=meta["kind"], function=name, source=src),
                obj,
            )
        )
    ids = [r.id for r, _ in found]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise ValueError(f"duplicate rule ids: {dupes}")
    return sorted(found, key=lambda t: t[0].id)
