"""Adjudication: the analyst rejects candidates against their cited sentences.

`rejections.yaml` in a pack lists atom ids an analyst has rejected, with the
analyst's name and reason. A rejected atom is removed before reconciliation.
The file is optional and nothing in it is generated.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .model import Atom, Rejection


def load_rejections(path: Path) -> list[Rejection]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return sorted((Rejection.model_validate(r) for r in data.get("rejections", [])), key=lambda r: r.atom_id)


def apply_rejections(atoms: list[Atom], rejections: list[Rejection]) -> list[Atom]:
    rejected = {r.atom_id for r in rejections}
    return [a for a in atoms if a.id not in rejected]
