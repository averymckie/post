"""Step 5, confirm: one recorded human answer per sentence. Human.

The checker has already answered every mechanical item. One question is left
per statement: do the allowed example and the forbidden example say what the
sentence says? The answer is recorded, with the reviewer's name, and it
becomes a permanent test.

A checklist entry whose reviewer is not a named person is provisional. The
build still compiles the statement, but the manifest and every runtime result
carry provisional=True until a named reviewer answers.

Two reviewers answering the same checklist either agree or produce a recorded
disagreement; `kappa` measures the agreement.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import yaml

from .model import Confirmation, Statement


def load_checklist(path: Path) -> list[Confirmation]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get("entries", [])
    out: list[Confirmation] = []
    for e in entries:
        out.append(Confirmation.model_validate(e))
    return sorted(out, key=lambda c: c.sentence_digest)


def confirmed_statements(
    statements: Iterable[Statement], checklist: Iterable[Confirmation]
) -> list[tuple[Statement, Confirmation]]:
    """Statements the checker accepted and a reviewer answered yes to."""
    by_digest: dict[str, list[Confirmation]] = {}
    for c in checklist:
        by_digest.setdefault(c.sentence_digest, []).append(c)
    out: list[tuple[Statement, Confirmation]] = []
    for st in statements:
        if not st.check.ok:
            continue
        for c in by_digest.get(st.sentence.digest, []):
            if c.answer is True and c.allowed_example == (st.proposal.allowed_example or "") and c.forbidden_example == (
                st.proposal.forbidden_example or ""
            ):
                out.append((st, c))
                break
    return out


def kappa(a: list[bool], b: list[bool]) -> float:
    """Cohen's kappa for two raters over the same items, binary answers."""
    if len(a) != len(b) or not a:
        raise ValueError("kappa needs two equal-length, non-empty answer lists")
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa_yes = sum(a) / n
    pb_yes = sum(b) / n
    pe = pa_yes * pb_yes + (1 - pa_yes) * (1 - pb_yes)
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def disagreements(first: Iterable[Confirmation], second: Iterable[Confirmation]) -> list[tuple[str, bool | None, bool | None]]:
    a = {c.sentence_digest: c.answer for c in first}
    b = {c.sentence_digest: c.answer for c in second}
    return [(d, a[d], b[d]) for d in sorted(set(a) & set(b)) if a[d] != b[d]]
