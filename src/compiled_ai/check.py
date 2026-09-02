"""Step 4, check: the mechanical items. Symbolic. Nothing here trusts the proposal.

For every proposal about a sentence:

- the quote is byte-exact in the sentence's canonical text (UTF-8 bytes, no
  case folding, no whitespace tolerance);
- a context quote, if given, is byte-exact in the sentence it names;
- the actor is a term the source defines or a role the source names;
- the quote (with its context) contains a connective the fixed table maps to
  the proposed statement type;
- a clock's amount and unit appear in the quote, so a deadline can never be
  invented;
- a sentence that reserves a decision to a role carries a reserved-decision
  statement, not only a rule;
- a rule statement carries one allowed and one forbidden example for the
  reviewer.

A failure is a typed code with a detail string. The checker never repairs a
proposal.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping

from .model import CheckFailure, CheckResult, Kind, Proposal, Sentence, Statement

# The fixed table: which words in a quote license which statement type.
CONNECTIVES: Mapping[Kind, tuple[str, ...]] = {
    "definition": ("means", "includes", "the term", "as used in", "as defined in", "does not include"),
    "condition": (
        "if",
        "unless",
        "except",
        "provided",
        "in the case of",
        "to the extent",
        "only if",
        "only to the extent",
        "whether",
        "in cases in which",
        "when",
        "where",
        "does not apply",
        "shall not",
        "circumstances",
    ),
    "step": ("shall", "must", "shall not", "may not", "is required"),
    "precedence": ("before", "after", "prior to", "within", "not later than", "upon", "commence", "following", "until"),
    "reserved_decision": (
        "determine",
        "determination",
        "may",
        "discretion",
        "decide",
        "authoriz",
        "approv",
        "certif",
        "reasonabl",
        "judgment",
        "deem",
    ),
    "none": (),
}

# Words that mean a person is deciding something. A rule statement whose quote
# carries one of these must sit beside a reserved-decision statement.
DECISION_WORDS = (
    "determine",
    "determines",
    "make a determination",
    "determination of whether",
    "decide",
    "discretion",
    "reasonably",
    "reasonable",
    "deem",
)

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40, "sixty": 60,
    "ninety": 90, "one hundred": 100,
}

UNIT_WORDS = {
    "days": ("days", "day"),
    "calendar_days": ("calendar days", "days"),
    "working_days": ("working days", "excepting saturdays, sundays, and legal public holidays"),
    "business_days": ("business days", "business day"),
    "months": ("months", "month"),
    "years": ("years", "year"),
}

_WORD = re.compile(r"[a-z]+")


def _norm(term: str) -> str:
    return " ".join(_WORD.findall(term.lower()))


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    low = text.lower()
    return any(n in low for n in needles)


def _amount_in(text: str, amount: int) -> bool:
    low = text.lower()
    if re.search(rf"(?<!\d){amount}(?!\d)", low):
        return True
    return any(v == amount and w in low for w, v in NUMBER_WORDS.items())


def check_proposal(
    sentence: Sentence,
    proposal: Proposal,
    siblings: tuple[Proposal, ...],
    sentences_by_digest: Mapping[str, Sentence],
    defined_terms: Iterable[str],
    roles: Iterable[str],
) -> CheckResult:
    failures: list[CheckFailure] = []
    terms = {_norm(t) for t in defined_terms}
    role_set = {_norm(r) for r in roles}

    # 1. quote
    if not proposal.quote:
        failures.append(CheckFailure(code="QUOTE_EMPTY", detail="the proposal carries no quote"))
    elif proposal.quote.encode("utf-8") not in sentence.text.encode("utf-8"):
        failures.append(
            CheckFailure(code="QUOTE_NOT_BYTE_EXACT", detail=f"quote is not a byte-exact substring of sentence {sentence.id}")
        )

    # 2. context quote
    scope_text = proposal.quote
    if proposal.context is not None:
        ctx_sentence = sentences_by_digest.get(proposal.context.sentence_digest)
        if ctx_sentence is None:
            failures.append(
                CheckFailure(code="CONTEXT_SENTENCE_UNKNOWN", detail=f"no sentence has digest {proposal.context.sentence_digest}")
            )
        elif proposal.context.quote.encode("utf-8") not in ctx_sentence.text.encode("utf-8"):
            failures.append(
                CheckFailure(code="CONTEXT_NOT_BYTE_EXACT", detail=f"context quote is not byte-exact in sentence {ctx_sentence.id}")
            )
        else:
            scope_text = proposal.context.quote + " " + proposal.quote

    kind = proposal.kind

    # 3. actor
    if kind in ("step", "reserved_decision"):
        if proposal.actor is None:
            failures.append(CheckFailure(code="ACTOR_MISSING", detail=f"a {kind} statement needs an actor"))
        elif _norm(proposal.actor) not in terms and _norm(proposal.actor) not in role_set:
            failures.append(
                CheckFailure(code="ACTOR_UNDEFINED", detail=f"actor {proposal.actor!r} is not a defined term or a named role")
            )

    # 4. connective
    if kind != "none" and not _contains_any(scope_text, CONNECTIVES[kind]):
        failures.append(
            CheckFailure(code="CONNECTIVE_MISMATCH", detail=f"no connective for kind {kind!r} in the quote or its context")
        )

    # 5. clock
    if proposal.clock is not None:
        c = proposal.clock
        if not _amount_in(proposal.quote, c.amount) or not _contains_any(proposal.quote, UNIT_WORDS[c.unit]):
            failures.append(
                CheckFailure(code="CLOCK_NOT_IN_QUOTE", detail=f"clock {c.amount} {c.unit} is not stated in the quote")
            )

    # 6. reserved decisions
    if kind == "reserved_decision":
        if proposal.role is None:
            failures.append(CheckFailure(code="RESERVED_WITHOUT_ROLE", detail="a reserved decision names no role"))
        elif _norm(proposal.role) not in role_set:
            failures.append(CheckFailure(code="ROLE_UNDEFINED", detail=f"role {proposal.role!r} is not a role the source names"))
    elif kind in ("step", "condition", "precedence") and _contains_any(proposal.quote, DECISION_WORDS):
        if not any(s.kind == "reserved_decision" for s in siblings):
            failures.append(
                CheckFailure(
                    code="ROLE_NOT_RESERVED",
                    detail="the quote has a person deciding something, but no reserved-decision statement accompanies it",
                )
            )

    # 7. examples
    if kind in ("step", "condition", "reserved_decision") and (
        not proposal.allowed_example or not proposal.forbidden_example
    ):
        failures.append(CheckFailure(code="EXAMPLES_MISSING", detail="one allowed and one forbidden example are required"))

    return CheckResult(ok=not failures, failures=tuple(failures))


def check_all(
    sentences: list[Sentence],
    proposals_by_digest: Mapping[str, tuple[Proposal, ...]],
    defined_terms: Iterable[str],
    roles: Iterable[str],
) -> list[Statement]:
    by_digest = {s.digest: s for s in sentences}
    out: list[Statement] = []
    for s in sentences:
        props = proposals_by_digest.get(s.digest, ())
        for p in props:
            result = check_proposal(s, p, props, by_digest, defined_terms, roles)
            out.append(Statement(sentence=s, proposal=p, check=result))
    return out


def defined_terms_from(statements: Iterable[Statement]) -> set[str]:
    """Terms defined by accepted definition statements."""
    return {st.proposal.term for st in statements if st.check.ok and st.proposal.kind == "definition" and st.proposal.term}
