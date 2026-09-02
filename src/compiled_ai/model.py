"""Typed records shared by every step. Every model forbids extra fields and is frozen."""

from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, ConfigDict


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- read


class Unit(Strict):
    """A block of source text. `text` is canonical; `offsets[i]` is the position in
    the original file of the character that produced `text[i]`."""

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


# -------------------------------------------------------------------------- parse


class Sentence(Strict):
    """A sentence as segmented by the parser. `text` is a byte-exact slice of its
    unit's canonical text; `origin_offset` locates it in the source file."""

    id: str
    source_id: str
    unit_id: str
    path: str
    start: int
    end: int
    text: str
    origin_offset: int
    digest: str


class Token(Strict):
    """One CoNLL-U token. `start`/`end` are character offsets within the sentence."""

    sentence_id: str
    id: int
    form: str
    lemma: str
    upos: str
    xpos: str
    feats: str
    head: int
    deprel: str
    start: int
    end: int


class ParsedSentence(Strict):
    sentence: Sentence
    tokens: tuple[Token, ...]
    conllu: str


# ---------------------------------------------------------------------------- fol

Predicate = Literal["event", "agent", "patient", "theme", "obligatory", "negated", "precedes"]


class Atom(Strict):
    """One first-order-logic atom with its citation.

    `args` are event or entity identifiers of the form `<sentence id>#e<token>` or
    `<sentence id>#x<token>`. `tokens` are the token ids the atom was compiled
    from, and `quote` is the byte-exact slice of the sentence that spans them.
    """

    id: str
    predicate: Predicate
    args: tuple[str, ...]
    sentence_id: str
    tokens: tuple[int, ...]
    quote: str


class Candidate(Strict):
    """A flag raised for adjudication. The analyst rejects; nothing is authored."""

    sentence_id: str
    code: Literal["NO_EVENT", "FRAGMENT", "UNRESOLVED_PRONOUN", "ANIMACY_BY_VERB_SELECTION"]
    detail: str
    atom_ids: tuple[str, ...] = ()


class Rejection(Strict):
    atom_id: str
    analyst: str
    reason: str


# ----------------------------------------------------------------- reconcile/order


class Reconciliation(Strict):
    consistent: bool
    checked: int
    cores: tuple[tuple[str, ...], ...]


class Ordering(Strict):
    order: tuple[str, ...]
    forced: tuple[tuple[str, str], ...]
    cycle: tuple[tuple[str, str], ...]


# ----------------------------------------------------------------------- seal


class AtomSeal(Strict):
    id: str
    sentence_id: str
    sentence_digest: str
    quote_digest: str


class Manifest(Strict):
    pack: str
    canon_version: int
    toolchain: dict[str, str]
    sources: tuple[tuple[str, str], ...]
    atoms: tuple[AtomSeal, ...]
    forced: tuple[tuple[str, str], ...]
    order: tuple[str, ...]
    consistent: bool
    digest: str
