"""Conversion operator: token tables and the citation index.

The token table is one row per token with its sentence id, dependency head,
relation, and character range. The citation index maps each sentence id to
its source, unit, statutory path, origin offset in the source file, text, and
digest. Both are written in a fixed order so a rebuild reproduces them byte
for byte.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .model import ParsedSentence

TOKEN_COLUMNS = ("sentence_id", "id", "form", "lemma", "upos", "xpos", "feats", "head", "deprel", "start", "end")


def token_rows(parsed: Iterable[ParsedSentence]) -> list[tuple[str, ...]]:
    rows: list[tuple[str, ...]] = []
    for ps in parsed:
        for t in ps.tokens:
            rows.append((t.sentence_id, str(t.id), t.form, t.lemma, t.upos, t.xpos, t.feats, str(t.head), t.deprel, str(t.start), str(t.end)))
    return rows


def citation_index(parsed: Iterable[ParsedSentence]) -> dict[str, dict[str, object]]:
    idx: dict[str, dict[str, object]] = {}
    for ps in parsed:
        s = ps.sentence
        idx[s.id] = {
            "source_id": s.source_id,
            "unit_id": s.unit_id,
            "path": s.path,
            "start": s.start,
            "end": s.end,
            "origin_offset": s.origin_offset,
            "digest": s.digest,
            "text": s.text,
        }
    return dict(sorted(idx.items()))


def write_tables(parsed: list[ParsedSentence], out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tokens = out_dir / "tokens.tsv"
    with tokens.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(TOKEN_COLUMNS) + "\n")
        for row in token_rows(parsed):
            fh.write("\t".join(row) + "\n")
    cites = out_dir / "citations.json"
    cites.write_text(json.dumps(citation_index(parsed), indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    conllu = out_dir / "parses.conllu"
    with conllu.open("w", encoding="utf-8", newline="\n") as fh:
        for ps in parsed:
            fh.write(f"# sent_id = {ps.sentence.id}\n# text = {ps.sentence.text}\n{ps.conllu}\n")
    return {"tokens": tokens, "citations": cites, "conllu": conllu}
