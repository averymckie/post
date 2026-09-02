"""The build is byte-identical across processes and hash seeds, matches the sealed
manifest in the pack, and depends on no language model or model client."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "foia"

BUILD = f"""
import sys
sys.path.insert(0, {str(ROOT / "src")!r})
from pathlib import Path
from compiled_ai.pack import compile_pack
from compiled_ai.seal import manifest_json
b = compile_pack(Path({str(PACK)!r}))
assert b.manifest is not None, [e.model_dump() for e in b.errors]
sys.stdout.write(manifest_json(b.manifest))
"""

BOUNDARY = f"""
import sys
sys.path.insert(0, {str(ROOT / "src")!r})
import compiled_ai.pack, compiled_ai.parse, compiled_ai.fol, compiled_ai.normalize, compiled_ai.reconcile, compiled_ai.order, compiled_ai.seal  # noqa
from pathlib import Path
compiled_ai.pack.compile_pack(Path({str(PACK)!r}))
bad = sorted(m for m in sys.modules if m.split('.')[0] in ('anthropic', 'openai', 'spacy', 'hypothesis', 'transformers', 'torch'))
print(','.join(bad))
"""


def _run(script: str, seed: str) -> str:
    out = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True, env={"PYTHONHASHSEED": seed, "PATH": "", "HOME": str(ROOT)}, cwd=ROOT)
    return out.stdout


def test_double_build_is_byte_identical_under_different_hash_seeds() -> None:
    assert _run(BUILD, "1") == _run(BUILD, "424242")


def test_rebuild_matches_the_sealed_manifest() -> None:
    assert _run(BUILD, "7") == (PACK / "build" / "manifest.json").read_text(encoding="utf-8")


def test_no_language_model_is_loaded_and_none_is_named_in_the_source() -> None:
    assert _run(BOUNDARY, "0").strip() == ""
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        assert "anthropic" not in text and "openai" not in text, path
