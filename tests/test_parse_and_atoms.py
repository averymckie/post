"""The parse is deterministic and every citation is byte-exact."""

from __future__ import annotations

from pathlib import Path

from compiled_ai.check import check_atoms
from compiled_ai.fol import compile_atoms
from compiled_ai.model import Sentence, Token
from compiled_ai.normalize import normalize
from compiled_ai.pack import model_path, read_sources
from compiled_ai.parse import parse_source

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "foia"
PREDICATES = {"event", "agent", "patient", "theme", "obligatory", "negated", "precedes"}


def test_parse_is_deterministic_and_token_ranges_are_byte_exact() -> None:
    sources, errors = read_sources(PACK)
    assert not errors
    mp = model_path(PACK)
    a = parse_source(sources[0], mp)
    b = parse_source(sources[0], mp)
    assert a == b
    raw = (PACK / "sources" / "usdoj-foia.gov-foia-statute.html").read_text(encoding="utf-8")
    units = {u.id: u for u in sources[0].units}
    for ps in a:
        s = ps.sentence
        assert units[s.unit_id].text[s.start : s.end] == s.text
        assert raw[s.origin_offset] == s.text[0]
        for t in ps.tokens:
            assert s.text[t.start : t.end] == t.form


def test_every_atom_is_cited_byte_exact_and_uses_the_seven_predicates() -> None:
    sources, _ = read_sources(PACK)
    parsed = parse_source(sources[0], model_path(PACK))
    atoms = compile_atoms(parsed)
    atoms, _ = normalize(atoms, parsed)
    check_atoms(atoms, parsed)
    assert {a.predicate for a in atoms} <= PREDICATES
    assert any(a.predicate == "obligatory" for a in atoms)
    assert any(a.predicate == "precedes" for a in atoms)
    by_sid = {ps.sentence.id: ps.sentence for ps in parsed}
    for a in atoms:
        assert a.quote.encode("utf-8") in by_sid[a.sentence_id].text.encode("utf-8")


def _sentence(text: str) -> Sentence:
    from compiled_ai.model import sha256_text

    return Sentence(id="t:u0:s00", source_id="t", unit_id="u0", path="(a)", start=0, end=len(text), text=text, origin_offset=0, digest=sha256_text(text))


def _tok(sid: str, i: int, form: str, lemma: str, upos: str, head: int, deprel: str, start: int) -> Token:
    return Token(sentence_id=sid, id=i, form=form, lemma=lemma, upos=upos, xpos="", feats="", head=head, deprel=deprel, start=start, end=start + len(form))


def test_compilation_rules_on_a_hand_built_parse() -> None:
    from compiled_ai.model import ParsedSentence

    text = "The agency shall not notify the person after the receipt of the request"
    s = _sentence(text)
    words = text.split(" ")
    starts = []
    pos = 0
    for w in words:
        starts.append(pos)
        pos += len(w) + 1
    sid = s.id
    tokens = (
        _tok(sid, 1, "The", "the", "DET", 2, "det", starts[0]),
        _tok(sid, 2, "agency", "agency", "NOUN", 5, "nsubj", starts[1]),
        _tok(sid, 3, "shall", "shall", "AUX", 5, "aux", starts[2]),
        _tok(sid, 4, "not", "not", "PART", 5, "advmod", starts[3]),
        _tok(sid, 5, "notify", "notify", "VERB", 0, "root", starts[4]),
        _tok(sid, 6, "the", "the", "DET", 7, "det", starts[5]),
        _tok(sid, 7, "person", "person", "NOUN", 5, "obj", starts[6]),
        _tok(sid, 8, "after", "after", "ADP", 10, "case", starts[7]),
        _tok(sid, 9, "the", "the", "DET", 10, "det", starts[8]),
        _tok(sid, 10, "receipt", "receipt", "NOUN", 5, "obl", starts[9]),
        _tok(sid, 11, "of", "of", "ADP", 13, "case", starts[10]),
        _tok(sid, 12, "the", "the", "DET", 13, "det", starts[11]),
        _tok(sid, 13, "request", "request", "NOUN", 10, "nmod", starts[12]),
    )
    ps = ParsedSentence(sentence=s, tokens=tokens, conllu="")
    atoms = compile_atoms([ps])
    ids = {a.id for a in atoms}
    assert f"event({sid}#e5,notify)" in ids
    assert f"agent({sid}#e5,{sid}#x2)" in ids
    assert f"patient({sid}#e5,{sid}#x7)" in ids
    assert f"obligatory({sid}#e5)" in ids
    assert f"negated({sid}#e5)" in ids
    assert f"event({sid}#e10,receipt)" in ids
    assert f"precedes({sid}#e10,{sid}#e5)" in ids
    by_id = {a.id: a for a in atoms}
    assert by_id[f"obligatory({sid}#e5)"].quote == "shall not notify"
    assert by_id[f"precedes({sid}#e10,{sid}#e5)"].quote == "notify the person after the receipt"
    check_atoms(atoms, [ps])
    # normalization keeps a transitive subject as agent
    normalized, candidates = normalize(atoms, [ps])
    assert f"agent({sid}#e5,{sid}#x2)" in {a.id for a in normalized}
    assert not candidates


def test_normalization_routes_an_intransitive_inanimate_subject_to_theme() -> None:
    from compiled_ai.model import ParsedSentence

    text = "The period shall commence"
    s = _sentence(text)
    sid = s.id
    tokens = (
        _tok(sid, 1, "The", "the", "DET", 2, "det", 0),
        _tok(sid, 2, "period", "period", "NOUN", 4, "nsubj", 4),
        _tok(sid, 3, "shall", "shall", "AUX", 4, "aux", 11),
        _tok(sid, 4, "commence", "commence", "VERB", 0, "root", 17),
    )
    ps = ParsedSentence(sentence=s, tokens=tokens, conllu="")
    atoms, candidates = normalize(compile_atoms([ps]), [ps])
    ids = {a.id for a in atoms}
    assert f"theme({sid}#e4,{sid}#x2)" in ids
    assert f"agent({sid}#e4,{sid}#x2)" not in ids
    assert [c.code for c in candidates] == ["ANIMACY_BY_VERB_SELECTION"]
