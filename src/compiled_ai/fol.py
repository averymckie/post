"""Compilation operator: token tables to first-order-logic atoms.

The predicate-argument structure of each sentence is extracted by PredPatt
(White et al.), a rule-based system over Universal Dependencies with no neural
model. PredPatt identifies the predicates and their arguments, and handles the
hard grammar (coordination, control, relative clauses, embedded predicates).
This module does not re-implement that; it calls PredPatt over the UDPipe
parse, with PredPatt's Universal Dependencies v2 relation table selected
(option ud="2.0"; the default is the v1 table, whose names "dobj",
"nsubjpass", and "nmod" never occur in a v2 parse), and projects PredPatt's
output onto the seven predicates through a fixed table over the closed
inventory of Universal Dependencies relations:

    event(E, lemma)     a PredPatt predicate; E is its root token, lemma its lemma
    agent(E, X)         an argument whose root relation is a subject (nsubj, csubj)
                        or an agent oblique (obl:agent)
    patient(E, X)       an argument whose root relation is an object (obj) or a
                        passive subject (nsubj:pass)
    theme(E, X)         an argument whose root relation is an indirect object
                        (iobj) or an oblique (obl) whose case is not temporal
    obligatory(E)       the predicate root has the auxiliary "shall" or "must"
    negated(E)          the predicate root has "not"/"never", or its subject "no"
    precedes(E1, E2)    a temporal case ("after") or mark orders two events; the
                        temporal anchor noun ("the receipt") becomes an event

Modality, negation, and temporal precedence are read from the Universal
Dependencies children of the PredPatt predicate root, because PredPatt does not
emit them. Every atom records the sentence id, the token ids it was compiled
from, and the byte-exact slice of the sentence spanning those tokens.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from .model import Atom, ParsedSentence, Token

AFTER = frozenset({"after", "following", "upon", "once", "since"})
BEFORE = frozenset({"before", "prior", "until", "pending"})
OBLIGATION_AUX = frozenset({"shall", "must"})
NEGATORS = frozenset({"not", "never", "n't"})

_SUBJECT_RELS = frozenset({"nsubj", "csubj"})


def _e(sid: str, tid: int) -> str:
    return f"{sid}#e{tid}"


def _x(sid: str, tid: int) -> str:
    return f"{sid}#x{tid}"


@lru_cache(maxsize=4096)
def _predpatt(conllu: str) -> Any:
    from predpatt import PredPatt, PredPattOpts, load_conllu
    from predpatt.util.ud import dep_v2

    parsed = list(load_conllu(conllu))
    if not parsed:
        return None
    _, ud = parsed[0]
    return PredPatt(ud, opts=PredPattOpts(ud=dep_v2.VERSION))


def _minimal_conllu(ps: ParsedSentence) -> str:
    lines = [
        f"{t.id}\t{t.form}\t{t.lemma}\t{t.upos}\t{t.xpos}\t{t.feats or '_'}\t{t.head}\t{t.deprel}\t_\t_"
        for t in ps.tokens
    ]
    return "# sent_id = 1\n# text = _\n" + "\n".join(lines) + "\n"


def _base_rel(deprel: str) -> str:
    return deprel.split(":")[0]


def _atom(pred: str, args: tuple[str, ...], ps: ParsedSentence, tokens: tuple[int, ...]) -> Atom:
    by_id = {t.id: t for t in ps.tokens}
    lo = min(by_id[t].start for t in tokens)
    hi = max(by_id[t].end for t in tokens)
    return Atom(
        id=f"{pred}({','.join(args)})",
        predicate=pred,  # type: ignore[arg-type]
        args=args,
        sentence_id=ps.sentence.id,
        tokens=tuple(sorted(tokens)),
        quote=ps.sentence.text[lo:hi],
    )


def _children(ps: ParsedSentence, head_id: int) -> list[Token]:
    return sorted((t for t in ps.tokens if t.head == head_id), key=lambda t: t.id)


def _case_tokens(ps: ParsedSentence, head_id: int) -> list[Token]:
    return [d for d in _children(ps, head_id) if d.deprel == "case"]


def _is_temporal_anchor(ps: ParsedSentence, tid: int) -> bool:
    return bool({d.lemma.lower() for d in _case_tokens(ps, tid)} & (AFTER | BEFORE))


def _arg_predicate(gov_rel: str) -> str | None:
    rel = gov_rel
    base = _base_rel(rel)
    if rel == "nsubj:pass":
        return "patient"
    if rel == "obl:agent":
        return "agent"
    if base in _SUBJECT_RELS:
        return "agent"
    if base == "obj":
        return "patient"
    if base == "iobj":
        return "theme"
    if base == "obl":
        return "theme"
    return None


def compile_atoms(parsed: list[ParsedSentence]) -> list[Atom]:
    atoms: list[Atom] = []
    for ps in parsed:
        sid = ps.sentence.id
        by_id = {t.id: t for t in ps.tokens}
        pp = _predpatt(_minimal_conllu(ps))
        if pp is None:
            continue
        pred_token_ids: set[int] = set()
        for pred in pp.instances:
            root_id = pred.root.position + 1  # PredPatt position is 0-based; token id is 1-based
            if root_id not in by_id:
                continue
            pred_token_ids.add(root_id)
            atoms.append(_atom("event", (_e(sid, root_id), by_id[root_id].lemma), ps, (root_id,)))
            for arg in pred.arguments:
                arg_id = arg.root.position + 1
                if arg_id not in by_id:
                    continue
                kind = _arg_predicate(arg.root.gov_rel)
                if kind is None:
                    continue
                if kind == "theme" and _base_rel(arg.root.gov_rel) == "obl" and _is_temporal_anchor(ps, arg_id):
                    continue  # a temporal anchor is compiled below as an event with a precedes atom
                atoms.append(_atom(kind, (_e(sid, root_id), _x(sid, arg_id)), ps, (root_id, arg_id)))

        # modality, negation, and temporal precedence over the UD children of each predicate root
        for root_id in sorted(pred_token_ids):
            E = _e(sid, root_id)
            for c in _children(ps, root_id):
                base = _base_rel(c.deprel)
                low = c.lemma.lower()
                if base == "aux" and low in OBLIGATION_AUX:
                    atoms.append(_atom("obligatory", (E,), ps, (root_id, c.id)))
                elif base == "advmod" and low in NEGATORS:
                    atoms.append(_atom("negated", (E,), ps, (root_id, c.id)))
                elif base == "obl":
                    cases = _case_tokens(ps, c.id)
                    case_lemmas = {d.lemma.lower() for d in cases}
                    if case_lemmas & AFTER or case_lemmas & BEFORE:
                        anchor = _e(sid, c.id)
                        if c.id not in pred_token_ids:
                            atoms.append(_atom("event", (anchor, c.lemma), ps, (c.id,)))
                        span = (root_id, c.id, *[d.id for d in cases])
                        if case_lemmas & AFTER:
                            atoms.append(_atom("precedes", (anchor, E), ps, span))
                        else:
                            atoms.append(_atom("precedes", (E, anchor), ps, span))
                elif base == "advcl" and c.id in pred_token_ids:
                    marks = {d.lemma.lower() for d in _children(ps, c.id) if d.deprel == "mark"}
                    if marks & AFTER:
                        atoms.append(_atom("precedes", (_e(sid, c.id), E), ps, (root_id, c.id)))
                    elif marks & BEFORE:
                        atoms.append(_atom("precedes", (E, _e(sid, c.id)), ps, (root_id, c.id)))
                # subject carrying "no" negates the event
                if base in _SUBJECT_RELS and any(d.deprel == "det" and d.lemma.lower() == "no" for d in _children(ps, c.id)):
                    atoms.append(_atom("negated", (E,), ps, (root_id, c.id)))

    # de-duplicate and order
    seen: set[str] = set()
    out: list[Atom] = []
    for a in sorted(atoms, key=lambda a: (a.sentence_id, a.tokens, a.id)):
        if a.id in seen:
            continue
        seen.add(a.id)
        out.append(a)
    return out
