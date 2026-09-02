"""Mechanical checks over atoms and parses. Nothing here trusts the parser.

- every atom's cited tokens exist in its sentence and its quote is the byte-exact
  slice of the sentence spanning them;
- every atom argument names a token of the same sentence;
- a sentence with no event, or whose root is not a predicate, is flagged as a
  fragment for adjudication.
"""

from __future__ import annotations

from .model import Atom, Candidate, ParsedSentence


class CheckError(Exception):
    pass


def check_atoms(atoms: list[Atom], parsed: list[ParsedSentence]) -> None:
    by_sid = {ps.sentence.id: ps for ps in parsed}
    for a in atoms:
        ps = by_sid.get(a.sentence_id)
        if ps is None:
            raise CheckError(f"{a.id}: unknown sentence {a.sentence_id}")
        ids = {t.id: t for t in ps.tokens}
        for tid in a.tokens:
            if tid not in ids:
                raise CheckError(f"{a.id}: cites token {tid}, which sentence {a.sentence_id} does not have")
        lo = min(ids[t].start for t in a.tokens)
        hi = max(ids[t].end for t in a.tokens)
        if ps.sentence.text[lo:hi] != a.quote or a.quote.encode("utf-8") not in ps.sentence.text.encode("utf-8"):
            raise CheckError(f"{a.id}: quote is not the byte-exact slice of its sentence")
        for arg in a.args[: 2 if a.predicate != "event" else 1]:
            sid, _, ref = arg.rpartition("#")
            target = by_sid.get(sid)
            if target is None or not ref or ref[0] not in "ex" or int(ref[1:]) not in {t.id for t in target.tokens}:
                raise CheckError(f"{a.id}: argument {arg!r} does not name a token of a parsed sentence")


def fragment_candidates(atoms: list[Atom], parsed: list[ParsedSentence]) -> list[Candidate]:
    with_event = {a.sentence_id for a in atoms if a.predicate == "event"}
    out: list[Candidate] = []
    for ps in parsed:
        sid = ps.sentence.id
        if sid not in with_event:
            out.append(Candidate(sentence_id=sid, code="NO_EVENT", detail="no event was compiled from this sentence"))
            continue
        roots = [t for t in ps.tokens if t.head == 0]
        if roots and roots[0].upos not in ("VERB", "AUX") and not any(t.head == roots[0].id and t.deprel in ("cop", "aux") for t in ps.tokens):
            out.append(Candidate(sentence_id=sid, code="FRAGMENT", detail=f"root {roots[0].form!r} is {roots[0].upos}, not a predicate"))
    return out
