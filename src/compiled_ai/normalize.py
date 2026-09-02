"""Normalization operator.

Two rules, both deterministic and both computed from the corpus itself:

1. Pronoun resolution for the closed class. A pronoun argument is resolved to
   the nearest preceding entity in the same unit whose animacy matches the
   pronoun's. An unresolved pronoun is flagged for adjudication.

2. Animacy by closed-class morphology and by verb selection. Personal and
   relative pronouns carry their animacy lexically. A noun is animate if,
   anywhere in the corpus, it is the subject of a transitive event (an event
   with a patient). Every other subject is inanimate, and an inanimate subject
   is routed from the agent role to the theme role. The open-class boundary
   between a human collective and an object noun is not decided here; each
   routing is flagged so the analyst can reject it against the sentence.
"""

from __future__ import annotations

from .model import Atom, Candidate, ParsedSentence, Token

ANIMATE_PRONOUNS = frozenset({"he", "she", "they", "him", "her", "them", "his", "their", "who", "whom", "whose", "someone", "anyone"})
INANIMATE_PRONOUNS = frozenset({"it", "its", "which", "that", "this", "these", "those", "such"})
PRONOUNS = ANIMATE_PRONOUNS | INANIMATE_PRONOUNS


def _token_of(arg: str, tokens: dict[str, dict[int, Token]]) -> Token | None:
    sid, _, ref = arg.rpartition("#")
    return tokens.get(sid, {}).get(int(ref[1:]))


def role_assignment(atoms: list[Atom], tokens: dict[str, dict[int, Token]]) -> frozenset[str]:
    """Lemmas of nouns that are agents of a transitive event anywhere in the corpus."""
    transitive = {a.args[0] for a in atoms if a.predicate == "patient"}
    animate: set[str] = set()
    for a in atoms:
        if a.predicate != "agent" or a.args[0] not in transitive:
            continue
        t = _token_of(a.args[1], tokens)
        if t is not None and t.upos in ("NOUN", "PROPN"):
            animate.add(t.lemma.lower())
    return frozenset(animate)


def _is_animate(t: Token, roles: frozenset[str]) -> bool | None:
    lemma = t.lemma.lower()
    if t.upos == "PRON" or lemma in PRONOUNS:
        if lemma in ANIMATE_PRONOUNS:
            return True
        if lemma in INANIMATE_PRONOUNS:
            return False
        return None
    if t.upos in ("NOUN", "PROPN"):
        return lemma in roles
    return None


def normalize(atoms: list[Atom], parsed: list[ParsedSentence]) -> tuple[list[Atom], list[Candidate]]:
    tokens: dict[str, dict[int, Token]] = {ps.sentence.id: {t.id: t for t in ps.tokens} for ps in parsed}
    unit_of = {ps.sentence.id: ps.sentence.unit_id for ps in parsed}
    order_of = {ps.sentence.id: i for i, ps in enumerate(parsed)}
    roles = role_assignment(atoms, tokens)
    candidates: list[Candidate] = []

    # entities in document order, for pronoun resolution
    entities: list[tuple[int, int, str, bool | None]] = []  # (sentence order, token id, arg, animacy)
    for a in atoms:
        if a.predicate in ("agent", "patient", "theme"):
            t = _token_of(a.args[1], tokens)
            if t is None or t.upos not in ("NOUN", "PROPN"):
                continue
            entities.append((order_of[a.sentence_id], t.id, a.args[1], _is_animate(t, roles)))
    entities = sorted(set(entities))

    def resolve(arg: str, sid: str) -> str | None:
        t = _token_of(arg, tokens)
        if t is None:
            return None
        want = _is_animate(t, roles)
        pos = (order_of[sid], t.id)
        best: str | None = None
        for so, tid, ent, anim in entities:
            if (so, tid) >= pos:
                break
            if unit_of[[s for s, o in order_of.items() if o == so][0]] != unit_of[sid]:
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
        if a.predicate == "agent" and t is not None and t.upos in ("NOUN", "PROPN") and not _is_animate(t, roles):
            routed = Atom(id=f"theme({a.args[0]},{a.args[1]})", predicate="theme", args=a.args, sentence_id=a.sentence_id, tokens=a.tokens, quote=a.quote)
            candidates.append(Candidate(sentence_id=a.sentence_id, code="ANIMACY_BY_VERB_SELECTION", detail=f"subject {t.lemma!r} is not the agent of any transitive event in the corpus; routed to theme", atom_ids=(routed.id,)))
            out.append(routed)
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
