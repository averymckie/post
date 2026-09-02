"""Normalization operator.

The role-routing rule is run by clingo, the answer-set solver, over the fact
base, through clorm. It is the two rules the method specifies, as clingo
program text, not Python:

    animate(X) :- agent(E, X), patient(E, _).
    theme(E, X) :- agent(E, X), not animate(X).

A subject is animate when it is the agent of some transitive event (an event
that has a patient) anywhere in the corpus, keyed by lemma. An inanimate
subject's agent atom is routed to a theme atom. clingo returns the unique
stable model, and every routed atom is flagged for the analyst, because the
open-class boundary between a human collective and an object noun is not
decided by this rule.

Pronoun resolution is a separate, deterministic rule: a pronoun argument is
resolved to the nearest preceding entity of matching animacy in the same unit.
An unresolved pronoun is flagged. (A neural coreference resolver such as
stanza would replace this step where its model is available; it is not, so the
deterministic rule stands and its misses become adjudication candidates.)
"""

from __future__ import annotations

from typing import Any

from .model import Atom, Candidate, ParsedSentence, Token

ANIMATE_PRONOUNS = frozenset({"he", "she", "they", "him", "her", "them", "his", "their", "who", "whom", "whose", "someone", "anyone"})
INANIMATE_PRONOUNS = frozenset({"it", "its", "which", "that", "this", "these", "those", "such"})
PRONOUNS = ANIMATE_PRONOUNS | INANIMATE_PRONOUNS

ANIMACY_RULES = "animate(X) :- agent(E,X), patient(E,_).\ntheme(E,X) :- agent(E,X), not animate(X)."


def _token_of(arg: str, tokens: dict[str, dict[int, Token]]) -> Token | None:
    sid, _, ref = arg.rpartition("#")
    return tokens.get(sid, {}).get(int(ref[1:]))


def _lemma(arg: str, tokens: dict[str, dict[int, Token]]) -> str | None:
    t = _token_of(arg, tokens)
    return t.lemma.lower() if t is not None else None


def _routed_agents(atoms: list[Atom], tokens: dict[str, dict[int, Token]]) -> set[str]:
    """Run the two ASP rules in clingo and return the lemmas routed to theme."""
    from clorm import FactBase, IntegerField, Predicate, StringField
    from clorm.clingo import Control

    class agent(Predicate):  # noqa: N801
        e = IntegerField
        x = StringField

    class patient(Predicate):  # noqa: N801
        e = IntegerField
        x = StringField

    class animate(Predicate):  # noqa: N801
        x = StringField

    agent_cls: Any = agent
    patient_cls: Any = patient
    control_cls: Any = Control
    event_ids = sorted({a.args[0] for a in atoms if a.predicate in ("agent", "patient")})
    eid = {e: i for i, e in enumerate(event_ids)}
    facts: list[Any] = []
    for a in atoms:
        if a.predicate == "agent":
            lem = _lemma(a.args[1], tokens)
            if lem is not None:
                facts.append(agent_cls(e=eid[a.args[0]], x=lem))
        elif a.predicate == "patient":
            lem = _lemma(a.args[1], tokens)
            if lem is not None:
                facts.append(patient_cls(e=eid[a.args[0]], x=lem))
    ctrl: Any = control_cls(unifier=[agent, patient, animate], logger=lambda code, msg: None, arguments=["--warn=none"])
    ctrl.add_facts(FactBase(facts))
    ctrl.add("base", [], ANIMACY_RULES)
    ctrl.ground([("base", [])])
    animate_lemmas: set[str] = set()
    with ctrl.solve(yield_=True) as handle:
        for m in handle:
            animate_lemmas = {a.x for a in m.facts(unifier=[animate], atoms=True).query(animate).all()}
            break
    # a lemma that is ever an agent but never animate is routed
    agent_lemmas = {_lemma(a.args[1], tokens) for a in atoms if a.predicate == "agent"}
    agent_lemmas.discard(None)
    return {lem for lem in agent_lemmas if lem is not None and lem not in animate_lemmas}


def normalize(atoms: list[Atom], parsed: list[ParsedSentence]) -> tuple[list[Atom], list[Candidate]]:
    tokens: dict[str, dict[int, Token]] = {ps.sentence.id: {t.id: t for t in ps.tokens} for ps in parsed}
    unit_of = {ps.sentence.id: ps.sentence.unit_id for ps in parsed}
    order_of = {ps.sentence.id: i for i, ps in enumerate(parsed)}
    sid_by_order = {i: ps.sentence.id for i, ps in enumerate(parsed)}
    candidates: list[Candidate] = []

    # entities in document order, for pronoun resolution
    def animacy(t: Token, routed: set[str]) -> bool | None:
        lemma = t.lemma.lower()
        if t.upos == "PRON" or lemma in PRONOUNS:
            if lemma in ANIMATE_PRONOUNS:
                return True
            if lemma in INANIMATE_PRONOUNS:
                return False
            return None
        if t.upos in ("NOUN", "PROPN"):
            return lemma not in routed
        return None

    routed = _routed_agents(atoms, tokens)

    entities: list[tuple[int, int, str, bool | None]] = []
    for a in atoms:
        if a.predicate in ("agent", "patient", "theme"):
            t = _token_of(a.args[1], tokens)
            if t is None or t.upos not in ("NOUN", "PROPN"):
                continue
            entities.append((order_of[a.sentence_id], t.id, a.args[1], animacy(t, routed)))
    entities = sorted(set(entities))

    def resolve(arg: str, sid: str) -> str | None:
        t = _token_of(arg, tokens)
        if t is None:
            return None
        want = animacy(t, routed)
        pos = (order_of[sid], t.id)
        best: str | None = None
        for so, tid, ent, anim in entities:
            if (so, tid) >= pos:
                break
            if unit_of[sid_by_order[so]] != unit_of[sid]:
                continue
            if anim == want:
                best = ent
        return best

    out: list[Atom] = []
    for a in atoms:
        if a.predicate not in ("agent", "patient", "theme"):
            out.append(a)
            continue
        arg = a.args[1]
        t = _token_of(arg, tokens)
        if t is not None and (t.upos == "PRON" or t.lemma.lower() in PRONOUNS):
            resolved = resolve(arg, a.sentence_id)
            if resolved is None:
                candidates.append(Candidate(sentence_id=a.sentence_id, code="UNRESOLVED_PRONOUN", detail=f"{t.form!r} at token {t.id} has no matching antecedent in its unit", atom_ids=(a.id,)))
                out.append(a)
                continue
            a = a.model_copy(update={"args": (a.args[0], resolved), "id": f"{a.predicate}({a.args[0]},{resolved})"})
            t = _token_of(resolved, tokens)
        if a.predicate == "agent" and t is not None and t.upos in ("NOUN", "PROPN") and t.lemma.lower() in routed:
            routed_atom = Atom(id=f"theme({a.args[0]},{a.args[1]})", predicate="theme", args=a.args, sentence_id=a.sentence_id, tokens=a.tokens, quote=a.quote)
            candidates.append(Candidate(sentence_id=a.sentence_id, code="ANIMACY_BY_VERB_SELECTION", detail=f"subject {t.lemma!r} is never the agent of a transitive event in the corpus; clingo routed it to theme", atom_ids=(routed_atom.id,)))
            out.append(routed_atom)
            continue
        out.append(a)

    seen: set[str] = set()
    deduped: list[Atom] = []
    for a in sorted(out, key=lambda a: (a.sentence_id, a.tokens, a.id)):
        if a.id in seen:
            continue
        seen.add(a.id)
        deduped.append(a)
    return deduped, sorted(candidates, key=lambda c: (c.sentence_id, c.code, c.detail))
