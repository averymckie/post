"""Step 2, cut: sentences with their positions.

spaCy's rule-based sentencizer on a blank English pipeline. No statistical
model is loaded, so the same bytes always cut the same way. Rules added for
legal text: a heading unit is one sentence; abbreviations common in statutes
do not end a sentence; a parenthesized designator such as (b)(2) never splits.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from .model import Sentence, Source, sha256_text

PUNCT_CHARS = [".", "!", "?"]
ABBREVIATIONS = ["U.S.C.", "U.S.", "Sec.", "No.", "e.g.", "i.e.", "et seq.", "Stat.", "Pub.", "L."]


@lru_cache(maxsize=1)
def _nlp() -> Any:
    import spacy  # compiler-only dependency

    nlp = spacy.blank("en")
    for abbr in ABBREVIATIONS:
        nlp.tokenizer.add_special_case(abbr, [{"ORTH": abbr}])
    nlp.add_pipe("sentencizer", config={"punct_chars": PUNCT_CHARS})
    return nlp


_DESIGNATOR_SPLIT = re.compile(r"\)\s*\(")


def cut(source: Source) -> list[Sentence]:
    nlp = _nlp()
    out: list[Sentence] = []
    for unit in source.units:
        spans: list[tuple[int, int]]
        if unit.is_heading:
            spans = [(0, len(unit.text))]
        else:
            doc = nlp(unit.text)
            spans = [(s.start_char, s.end_char) for s in doc.sents]
            spans = _merge_designator_splits(unit.text, spans)
        for start, end in spans:
            text = unit.text[start:end]
            # trim spaces at both ends, keeping the offset map exact
            while text and text[0] == " ":
                start += 1
                text = text[1:]
            while text and text[-1] == " ":
                end -= 1
                text = text[:-1]
            if not text:
                continue
            out.append(
                Sentence(
                    id=f"{source.id}:{unit.id}:s{len([s for s in out if s.unit_id == unit.id]):02d}",
                    source_id=source.id,
                    unit_id=unit.id,
                    path=unit.path,
                    start=start,
                    end=end,
                    text=text,
                    origin_offset=unit.offsets[start],
                    page=unit.page,
                    digest=sha256_text(text),
                )
            )
    return out


def _merge_designator_splits(text: str, spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """A split that lands inside a run of designators like (b)(2) is undone."""
    merged: list[tuple[int, int]] = []
    for span in spans:
        if merged:
            ps, pe = merged[-1]
            between = text[pe:span[0]]
            if _DESIGNATOR_SPLIT.fullmatch(between or "") or text[ps:pe].rstrip().endswith(")") and text[span[0]:span[0] + 1] == "(":
                merged[-1] = (ps, span[1])
                continue
        merged.append(span)
    return merged
