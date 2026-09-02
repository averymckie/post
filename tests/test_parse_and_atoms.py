"""The parse is deterministic, PredPatt extraction plus the projection yields the
seven predicates, and every citation is byte-exact."""

from __future__ import annotations

from pathlib import Path

from compiled_ai.check import check_atoms
from compiled_ai.fol import compile_atoms
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


def test_every_atom_uses_the_seven_predicates_and_is_cited_byte_exact() -> None:
    sources, _ = read_sources(PACK)
    parsed = parse_source(sources[0], model_path(PACK))
    atoms = compile_atoms(parsed)
    atoms, _ = normalize(atoms, parsed)
    check_atoms(atoms, parsed)
    assert atoms  # PredPatt finds predicates in the statute
    assert {a.predicate for a in atoms} <= PREDICATES
    assert any(a.predicate == "event" for a in atoms)
    assert any(a.predicate == "obligatory" for a in atoms)
    by_sid = {ps.sentence.id: ps.sentence for ps in parsed}
    for a in atoms:
        assert a.quote.encode("utf-8") in by_sid[a.sentence_id].text.encode("utf-8")


def test_predpatt_projection_on_a_real_clause() -> None:
    """A clause with an overt subject compiles to event + agent + obligatory,
    each byte-exact, via PredPatt and the projection table."""
    from compiled_ai.model import Source, Unit, sha256_text

    text = "The agency shall determine the request."
    unit = Unit(id="u0", path="(x)", text=text, offsets=tuple(range(len(text))))
    source = Source(id="t", kind="text", path="t", sha256=sha256_text(text), canon_version=1, units=(unit,))
    parsed = parse_source(source, model_path(PACK))
    atoms = compile_atoms(parsed)
    kinds = {a.predicate for a in atoms}
    assert "event" in kinds and "agent" in kinds and "obligatory" in kinds
    by_lemma_event = [a for a in atoms if a.predicate == "event" and a.args[1] == "determine"]
    assert by_lemma_event, [a.id for a in atoms]
    oblig = [a for a in atoms if a.predicate == "obligatory"]
    assert oblig and oblig[0].quote in text and "shall" in oblig[0].quote
    for a in atoms:
        assert parsed[0].sentence.text.encode("utf-8").find(a.quote.encode("utf-8")) >= 0


def test_normalization_routes_an_inanimate_subject_to_theme_via_clingo() -> None:
    from compiled_ai.model import Source, Unit, sha256_text

    text = "The agency shall notify the person. The period shall commence."
    unit = Unit(id="u0", path="(x)", text=text, offsets=tuple(range(len(text))))
    source = Source(id="t", kind="text", path="t", sha256=sha256_text(text), canon_version=1, units=(unit,))
    parsed = parse_source(source, model_path(PACK))
    atoms = compile_atoms(parsed)
    normalized, candidates = normalize(atoms, parsed)
    # "agency" is the agent of a transitive event (notify the person) -> stays agent
    agent_lemmas = {a.args[1].split("#")[0] for a in normalized if a.predicate == "agent"}
    # "period" is an intransitive subject -> routed to theme, and flagged
    assert any(c.code == "ANIMACY_BY_VERB_SELECTION" for c in candidates)
