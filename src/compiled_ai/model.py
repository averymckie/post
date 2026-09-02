"""Typed records shared by every step.

Every model forbids extra fields and is frozen, so a record is either exactly
what the schema says or it is rejected. Nothing here is neural.
"""

from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- read


class Unit(Strict):
    """A block of source text: a paragraph, a list item, a heading.

    `text` is canonical (see canon.py). `offsets[i]` is the position in the
    original file of the character that produced `text[i]`, so any span of the
    canonical text can be located in the source.
    """

    id: str
    path: str
    text: str
    offsets: tuple[int, ...]
    page: int = 1
    is_heading: bool = False


class Source(Strict):
    id: str
    kind: Literal["html", "pdf", "text"]
    path: str
    sha256: str
    canon_version: int
    units: tuple[Unit, ...]
    notes: tuple[str, ...] = ()

    @property
    def text(self) -> str:
        return "\n".join(u.text for u in self.units)


# ---------------------------------------------------------------------------- cut


class Sentence(Strict):
    id: str
    source_id: str
    unit_id: str
    path: str
    start: int
    end: int
    text: str
    origin_offset: int
    page: int
    digest: str


# ------------------------------------------------------------------------ propose

Kind = Literal["definition", "condition", "step", "precedence", "reserved_decision", "none"]

ClockUnit = Literal["days", "working_days", "business_days", "calendar_days", "months", "years"]


class Clock(Strict):
    amount: int = Field(ge=0)
    unit: ClockUnit
    trigger: str
    subject: str


class Proposal(Strict):
    """What the model proposes for one sentence. Nothing downstream trusts it."""

    kind: Kind
    quote: str
    actor: str | None = None
    condition: str | None = None
    action: str | None = None
    subject: str | None = None
    term: str | None = None
    meaning: str | None = None
    clock: Clock | None = None
    role: str | None = None
    before: str | None = None
    after: str | None = None
    allowed_example: str | None = None
    forbidden_example: str | None = None


class Provenance(Strict):
    producer: Literal["model", "human"]
    channel: Literal["propose-adapter", "interactive-session", "manual"]
    model: str | None = None
    note: str | None = None


class ProposalRecord(Strict):
    sentence_digest: str
    sentence_text: str
    proposal: Proposal
    provenance: Provenance


# -------------------------------------------------------------------------- check

CheckCode = Literal[
    "QUOTE_NOT_BYTE_EXACT",
    "QUOTE_EMPTY",
    "ACTOR_UNDEFINED",
    "CONNECTIVE_MISMATCH",
    "ROLE_NOT_RESERVED",
    "RESERVED_WITHOUT_ROLE",
    "CLOCK_NOT_IN_QUOTE",
    "EXAMPLES_MISSING",
]


class CheckFailure(Strict):
    code: CheckCode
    detail: str


class CheckResult(Strict):
    ok: bool
    failures: tuple[CheckFailure, ...] = ()


class Statement(Strict):
    sentence: Sentence
    proposal: Proposal
    check: CheckResult


# ------------------------------------------------------------------------ confirm


class Confirmation(Strict):
    sentence_digest: str
    reviewer: str
    answer: bool | None
    provisional: bool
    allowed_example: str
    forbidden_example: str
    note: str | None = None


# --------------------------------------------------------------------- generate


class RuleSpec(Strict):
    """A rule as sealed: which sentence, which function, which bytes."""

    id: str
    sentence_id: str
    sentence_digest: str
    path: str
    kind: Kind
    function: str
    function_digest: str
    quote: str
    provisional: bool


# ----------------------------------------------------------------------- seal


class Manifest(Strict):
    pack: str
    canon_version: int
    toolchain: dict[str, str]
    sources: tuple[tuple[str, str], ...]
    rules: tuple[RuleSpec, ...]
    order: tuple[str, ...]
    provisional: bool
    digest: str


# -------------------------------------------------------------------- runtime


class Applied(Strict):
    rule_id: str
    sentence_id: str
    path: str
    quote: str


class Reason(Strict):
    code: str
    message: str
    remedy: str
    rule_id: str | None = None
    sentence_id: str | None = None
    path: str | None = None
    quote: str | None = None


class Route(Strict):
    decision: str
    role: str
    rule_id: str
    sentence_id: str
    path: str
    quote: str


class Proof(Strict):
    kind: Literal["proof"] = "proof"
    applied: tuple[Applied, ...]
    routes: tuple[Route, ...]
    provisional: bool
    manifest_digest: str


class Reasons(Strict):
    kind: Literal["reasons"] = "reasons"
    reasons: tuple[Reason, ...]
    applied: tuple[Applied, ...]
    routes: tuple[Route, ...]
    provisional: bool
    manifest_digest: str


Result = Proof | Reasons
