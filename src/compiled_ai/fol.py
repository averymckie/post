"""Compilation operator: token tables to first-order-logic atoms.

Seven predicates, compiled by fixed rules over Universal Dependencies relations:

    event(E, lemma)        E is a verb token, or a root predicate with an aux or copula
    agent(E, X)            X is the nominal subject of E (obl:agent for passives)
    patient(E, X)          X is the object of E, or the passive subject
    theme(E, X)            X is an oblique or indirect object of E
    obligatory(E)          E carries the auxiliary "shall" or "must"
    negated(E)             E carries "not" or "never", or its subject carries "no"
    precedes(E1, E2)       a temporal case or mark orders E1 before E2

A coordinated verb with no subject of its own inherits the subject of the verb
it is conjoined with. A control complement (xcomp) inherits the subject of its
matrix verb. A temporal anchor that is a noun ("after the receipt") becomes a
nominal event so that precedes always relates two events.

Every atom records the sentence id, the token ids it was compiled from, and
the byte-exact slice of the sentence spanning those tokens. Nothing here is
learned or authored per sentence.
"""

from __future__ import annotations

from collections.abc import Iterable

from .model import Atom, ParsedSentence, Token

AFTER = frozenset({"after", "following", "upon", "once", "since"})
BEFORE = frozenset({"before", "prior", "until", "pending"})
OBLIGATION_AUX = frozenset({"shall", "must"})
NEGATORS = frozenset({"not", "never", "n't"})

_EVENT_ROOT_UPOS = frozenset({"ADJ", "NOUN", "PROPN", "PRON", "NUM"})


def _e(sid: str, tid: int) -> str:
    return f"{sid}#e{tid}"


def _x(sid: str, tid: int) -> str:
    return f"{sid}#x{tid}"


def _atom(pred: str, args: tuple[str, ...], ps: ParsedSentence, tokens: tuple[int, ...]) -> Atom:
    by_id = {t.id: t for t in ps.tokens}
    a = min(by_id[t].start for t in tokens)
    b = max(by_id[t].end for t in tokens)
    return Atom(
        id=f"{pred}({','.join(args)})",
        predicate=pred,  # type: ignore[arg-type]
        args=args,
        sentence_id=ps.sentence.id,
        tokens=tuple(sorted(tokens)),
        quote=ps.sentence.text[a:b],
    )


def _children(tokens: Iterable[Token], head: int) -> list[Token]:
    return sorted((t for t in tokens if t.head == head), key=lambda t: t.id)


def _base_rel(deprel: str) -> str:
    return deprel.split(":")[0]


def _is_event(t: Token, tokens: tuple[Token, ...]) -> bool:
    if t.upos == "VERB":
        return True
    if t.upos in _EVENT_ROOT_UPOS and any(_base_rel(c.deprel) in ("aux", "cop") for c in _children(tokens, t.id)):
        return True
    return False


def compile_atoms(parsed: list[ParsedSentence]) -> list[Atom]:
    atoms: list[Atom] = []
    for ps in parsed:
        sid = ps.sentence.id
        tokens = ps.tokens
        by_id = {t.id: t for t in tokens}
        events = [t for t in tokens if _is_event(t, tokens)]
        event_ids = {t.id for t in events}
        subject_of: dict[int, tuple[int, str]] = {}  # event token -> (subject token, role)

        for t in events:
            atoms.append(_atom("event", (_e(sid, t.id), t.lemma), ps, (t.id,)))

        # subjects, objects, obliques, modality, negation
        for t in events:
            E = _e(sid, t.id)
            for c in _children(tokens, t.id):
                rel = c.deprel
                base = _base_rel(rel)
                if rel == "nsubj:pass":
                    atoms.append(_atom("patient", (E, _x(sid, c.id)), ps, (t.id, c.id)))
                    subject_of[t.id] = (c.id, "patient")
                    for cj in _children(tokens, c.id):
                        if cj.deprel == "conj":
                            atoms.append(_atom("patient", (E, _x(sid, cj.id)), ps, (t.id, cj.id)))
                elif base == "nsubj" or base == "csubj":
                    atoms.append(_atom("agent", (E, _x(sid, c.id)), ps, (t.id, c.id)))
                    subject_of[t.id] = (c.id, "agent")
                    for cj in _children(tokens, c.id):
                        if cj.deprel == "conj":
                            atoms.append(_atom("agent", (E, _x(sid, cj.id)), ps, (t.id, cj.id)))
                    if any(d.deprel == "det" and d.lemma == "no" for d in _children(tokens, c.id)):
                        atoms.append(_atom("negated", (E,), ps, (t.id, c.id)))
                elif rel == "obl:agent":
                    atoms.append(_atom("agent", (E, _x(sid, c.id)), ps, (t.id, c.id)))
                elif base == "obj":
                    atoms.append(_atom("patient", (E, _x(sid, c.id)), ps, (t.id, c.id)))
                    for cj in _children(tokens, c.id):
                        if cj.deprel == "conj":
                            atoms.append(_atom("patient", (E, _x(sid, cj.id)), ps, (t.id, cj.id)))
                elif base == "iobj":
                    atoms.append(_atom("theme", (E, _x(sid, c.id)), ps, (t.id, c.id)))
                elif base == "obl":
                    case = [d for d in _children(tokens, c.id) if d.deprel == "case"]
                    case_lemmas = {d.lemma.lower() for d in case}
                    if case_lemmas & AFTER or case_lemmas & BEFORE:
                        anchor = _e(sid, c.id)
                        if c.id not in event_ids:
                            atoms.append(_atom("event", (anchor, c.lemma), ps, (c.id,)))
                        if case_lemmas & AFTER:
                            atoms.append(_atom("precedes", (anchor, E), ps, (t.id, c.id, *[d.id for d in case])))
                        else:
                            atoms.append(_atom("precedes", (E, anchor), ps, (t.id, c.id, *[d.id for d in case])))
                    else:
                        atoms.append(_atom("theme", (E, _x(sid, c.id)), ps, (t.id, c.id)))
                elif base == "aux" and c.lemma.lower() in OBLIGATION_AUX:
                    atoms.append(_atom("obligatory", (E,), ps, (t.id, c.id)))
                elif base == "advmod" and c.lemma.lower() in NEGATORS:
                    atoms.append(_atom("negated", (E,), ps, (t.id, c.id)))
                elif base == "advcl" and c.id in event_ids:
                    marks = {d.lemma.lower() for d in _children(tokens, c.id) if d.deprel == "mark"}
                    if marks & AFTER:
                        atoms.append(_atom("precedes", (_e(sid, c.id), E), ps, (t.id, c.id)))
                    elif marks & BEFORE:
                        atoms.append(_atom("precedes", (E, _e(sid, c.id)), ps, (t.id, c.id)))
                elif base == "ccomp" and c.id in event_ids:
                    atoms.append(_atom("theme", (E, _e(sid, c.id)), ps, (t.id, c.id)))

        # subject inheritance: coordination and control
        for t in events:
            if t.id in subject_of:
                continue
            head = by_id.get(t.head)
            if head is None or head.id not in event_ids:
                continue
            if _base_rel(t.deprel) in ("conj", "xcomp") and head.id in subject_of:
                subj, role = subject_of[head.id]
                atoms.append(_atom(role, (_e(sid, t.id), _x(sid, subj)), ps, (t.id, subj)))
                subject_of[t.id] = (subj, role)

    return sorted(atoms, key=lambda a: (a.sentence_id, a.tokens, a.id))
