"""Steps 1 and 2: canonical text keeps an exact offset map; the statute cuts the same way every time."""

from __future__ import annotations

from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from compiled_ai.canon import canonicalize
from compiled_ai.cut import cut
from compiled_ai.read import read_html, read_text

FOIA = Path(__file__).resolve().parents[1] / "packs" / "foia" / "sources" / "usdoj-foia.gov-foia-statute.html"


@given(st.text(min_size=0, max_size=200))
def test_canonical_text_has_no_double_spaces_and_maps_every_char(text: str) -> None:
    chars = list(text)
    canon, offsets = canonicalize(chars, list(range(len(chars))))
    assert "  " not in canon
    assert not canon.startswith(" ") and not canon.endswith(" ")
    assert len(canon) == len(offsets)
    assert all(0 <= o < len(chars) for o in offsets)
    # every non-space canonical character came from the original character at its offset
    for ch, off in zip(canon, offsets):
        if ch != " ":
            import unicodedata

            assert ch in unicodedata.normalize("NFC", chars[off])


def test_read_html_drops_struck_text_and_keeps_bold(tmp_path: Path) -> None:
    page = tmp_path / "p.html"
    page.write_text("<p>(a) Keep <s>old words</s> <strong>new words</strong> here.</p>", encoding="utf-8")
    src = read_html(page, "t")
    assert [u.text for u in src.units] == ["(a) Keep new words here."]
    assert "9 characters dropped" in src.notes[0]
    # offsets point at the original characters
    raw = page.read_text(encoding="utf-8")
    u = src.units[0]
    assert raw[u.offsets[0]] == "("
    assert raw[u.offsets[u.text.index("new")]] == "n"


def test_read_text_units_are_paragraphs(tmp_path: Path) -> None:
    f = tmp_path / "t.txt"
    f.write_text("First   paragraph.\n\nSecond\nparagraph.", encoding="utf-8")
    src = read_text(f, "t")
    assert [u.text for u in src.units] == ["First paragraph.", "Second paragraph."]


def test_statute_reads_and_cuts_the_same_way_twice() -> None:
    a = read_html(FOIA, "usc5-552-doj", start_marker="§ 552.")
    b = read_html(FOIA, "usc5-552-doj", start_marker="§ 552.")
    assert a == b
    sa, sb = cut(a), cut(b)
    assert sa == sb
    assert len(sa) == 284
    paths = {s.path for s in sa}
    for expected in ["(a)(6)(A)(i)", "(a)(6)(A)(i)(III)(aa)", "(a)(6)(B)(i)", "(b)(3)(A)(ii)", "(f)(1)", "(i)", "(m)(1)"]:
        assert expected in paths


def test_sentence_text_is_located_in_the_source_file() -> None:
    src = read_html(FOIA, "usc5-552-doj", start_marker="§ 552.")
    raw = FOIA.read_text(encoding="utf-8")
    for s in cut(src):
        assert raw[s.origin_offset] == s.text[0]
