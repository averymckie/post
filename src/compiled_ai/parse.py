"""Parse: UDPipe dependency parses under Universal Dependencies.

Each unit of canonical text is tokenized, sentence-segmented, tagged, and parsed
by UDPipe with the pinned model. The tokenizer runs with `ranges`, so every
token carries its character range in the input, and every citation downstream
is byte-exact by construction. The parser is the only statistical component in
the chain; its output is checked, never trusted, and the analyst rejects
candidates against their cited bytes.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from .model import ParsedSentence, Sentence, Source, Token, sha256_text


@lru_cache(maxsize=2)
def _pipeline(model_path: str) -> tuple[Any, Any]:
    """The model and its pipeline, cached together: the pipeline holds a raw
    pointer to the model, so the model must stay alive as long as the pipeline."""
    from ufal.udpipe import Model, Pipeline

    model = Model.load(model_path)
    if model is None:
        raise RuntimeError(f"UDPipe could not load the model at {model_path}")
    return model, Pipeline(model, "tokenizer=ranges", Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")


def parse_text(text: str, model_path: Path) -> str:
    from ufal.udpipe import ProcessingError

    _, pipeline = _pipeline(str(model_path))
    err = ProcessingError()
    out: str = pipeline.process(text, err)
    if err.occurred():
        raise RuntimeError(err.message)
    return out


def _token_range(misc: str) -> tuple[int, int]:
    for part in misc.split("|"):
        if part.startswith("TokenRange="):
            a, b = part[len("TokenRange=") :].split(":")
            return int(a), int(b)
    raise ValueError(f"token has no TokenRange: {misc!r}")


def _split_conllu(conllu: str) -> list[list[str]]:
    """Return the token lines of each sentence, in order."""
    sentences: list[list[str]] = []
    current: list[str] = []
    for line in conllu.splitlines():
        if not line.strip():
            if current:
                sentences.append(current)
                current = []
            continue
        if line.startswith("#"):
            continue
        current.append(line)
    if current:
        sentences.append(current)
    return sentences


def parse_source(source: Source, model_path: Path) -> list[ParsedSentence]:
    out: list[ParsedSentence] = []
    for unit in source.units:
        conllu = parse_text(unit.text, model_path)
        for k, lines in enumerate(_split_conllu(conllu)):
            rows: list[tuple[int, str, str, str, str, str, int, str, int, int]] = []
            for line in lines:
                f = line.split("\t")
                if len(f) != 10 or "-" in f[0] or "." in f[0]:
                    continue  # multiword token ranges and empty nodes carry no parse
                a, b = _token_range(f[9])
                rows.append((int(f[0]), f[1], f[2], f[3], f[4], f[5], int(f[6]), f[7], a, b))
            if not rows:
                continue
            s_start = min(r[8] for r in rows)
            s_end = max(r[9] for r in rows)
            text = unit.text[s_start:s_end]
            sid = f"{source.id}:{unit.id}:s{k:02d}"
            sentence = Sentence(
                id=sid,
                source_id=source.id,
                unit_id=unit.id,
                path=unit.path,
                start=s_start,
                end=s_end,
                text=text,
                origin_offset=unit.offsets[s_start],
                digest=sha256_text(text),
            )
            tokens = []
            for tid, form, lemma, upos, xpos, feats, head, deprel, a, b in rows:
                if unit.text[a:b] != form:
                    raise ValueError(f"token range does not match form in {sid}: {unit.text[a:b]!r} != {form!r}")
                tokens.append(
                    Token(
                        sentence_id=sid,
                        id=tid,
                        form=form,
                        lemma=lemma,
                        upos=upos,
                        xpos=xpos,
                        feats=feats,
                        head=head,
                        deprel=deprel,
                        start=a - s_start,
                        end=b - s_start,
                    )
                )
            out.append(ParsedSentence(sentence=sentence, tokens=tuple(tokens), conllu="\n".join(lines) + "\n"))
    return out
