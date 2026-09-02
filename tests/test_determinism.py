"""Guarantee G2: the same sources, checklist, and toolchain seal to the same manifest,
in separate processes, under different hash seeds. The sealed manifest committed
in the pack must match too."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "foia"

SCRIPT = f"""
import sys
sys.path.insert(0, {str(ROOT / "src")!r})
from pathlib import Path
from compiled_ai.pack import compile_pack
from compiled_ai.seal import manifest_json
b = compile_pack(Path({str(PACK)!r}))
assert b.manifest is not None, [e.model_dump() for e in b.errors]
sys.stdout.write(manifest_json(b.manifest))
"""


def _build(seed: str) -> str:
    out = subprocess.run(
        [sys.executable, "-c", SCRIPT],
        capture_output=True,
        text=True,
        check=True,
        env={"PYTHONHASHSEED": seed, "PATH": "", "HOME": str(ROOT)},
        cwd=ROOT,
    )
    return out.stdout


def test_double_build_is_byte_identical_under_different_hash_seeds() -> None:
    a = _build("1")
    b = _build("424242")
    assert a == b
    assert json.loads(a)["digest"] == json.loads(b)["digest"]


def test_rebuild_matches_the_sealed_manifest_in_the_pack() -> None:
    sealed = (PACK / "build" / "manifest.json").read_text(encoding="utf-8")
    assert _build("7") == sealed
