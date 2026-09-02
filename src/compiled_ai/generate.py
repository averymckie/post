"""Step 6, generate: a rule function per confirmed statement. Neural.

The generated function is committed to the pack's rules module once the
reviewer has read it, so the committed source is the fixture. The replay
generator therefore does two things: it returns the committed source for a
statement, and it refuses a rule that has no confirmed statement behind it
or a confirmed rule statement that has no function. That second job is the
zero-fabrication control at the rule level: no rule exists without a checked,
confirmed sentence.

The live generator drafts a function from the statement and the record
schema. It is not exercised in this repository's tests.
"""

from __future__ import annotations

from collections.abc import Iterable

from .model import Confirmation, Statement, Strict
from .registry import RuleDef

RULE_KINDS = ("step", "condition", "reserved_decision")


class GenerateError(Strict):
    code: str
    detail: str


class GenerateReport(Strict):
    matched: tuple[tuple[str, str], ...]  # (statement id, rule id)
    errors: tuple[GenerateError, ...]


def match_rules(
    confirmed: Iterable[tuple[Statement, Confirmation]], rules: Iterable[RuleDef]
) -> GenerateReport:
    by_statement: dict[str, list[RuleDef]] = {}
    for r in rules:
        by_statement.setdefault(r.statement, []).append(r)
    errors: list[GenerateError] = []
    matched: list[tuple[str, str]] = []
    seen_statements: set[str] = set()
    for st, conf in confirmed:
        seen_statements.add(conf.id)
        if st.proposal.kind not in RULE_KINDS:
            continue
        rs = by_statement.get(conf.id, [])
        if not rs:
            errors.append(GenerateError(code="MISSING_RULE", detail=f"confirmed statement {conf.id!r} has no rule function"))
            continue
        if len(rs) > 1:
            errors.append(GenerateError(code="DUPLICATE_RULE", detail=f"statement {conf.id!r} has {len(rs)} rule functions"))
            continue
        r = rs[0]
        if r.kind != st.proposal.kind:
            errors.append(
                GenerateError(
                    code="KIND_MISMATCH",
                    detail=f"rule {r.id!r} is registered as {r.kind!r} but statement {conf.id!r} is {st.proposal.kind!r}",
                )
            )
            continue
        matched.append((conf.id, r.id))
    for r in sorted(rules, key=lambda r: r.id):
        if r.statement not in seen_statements:
            errors.append(
                GenerateError(
                    code="RULE_WITHOUT_STATEMENT",
                    detail=f"rule {r.id!r} names statement {r.statement!r}, which is not a confirmed statement",
                )
            )
    return GenerateReport(matched=tuple(sorted(matched)), errors=tuple(sorted(errors, key=lambda e: (e.code, e.detail))))


LIVE_PROMPT = """You draft one small Python function that implements one confirmed statement of a regulation over a typed record.

Return only the function. It takes the record and returns Ok(), Fail(code=..., message=..., remedy=...), RouteTo(decision=..., role=...), or Skip(). It must be total: no exceptions for a well-typed record. It must not decide anything the statement reserves to a role; it routes instead. Every message must quote the statement's exact words.
"""
