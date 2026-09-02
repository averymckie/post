"""Guarantee G4: the runtime depends on no model and on no compiler-only library."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN = ["anthropic", "spacy", "z3", "networkx", "pdfplumber", "compiled_ai.propose", "compiled_ai.pack", "compiled_ai.cut"]

SCRIPT = f"""
import sys
sys.path.insert(0, {str(ROOT / "src")!r})
sys.path.insert(0, {str(ROOT)!r})
from compiled_ai import model, registry, runtime  # noqa
from packs.foia import calendar, record, rules  # noqa
bad = sorted(m for m in sys.modules if any(m == f or m.startswith(f + ".") for f in {FORBIDDEN!r}))
print(",".join(bad))
"""


def test_runtime_and_pack_rules_import_no_model_or_compiler_dependency() -> None:
    out = subprocess.run([sys.executable, "-c", SCRIPT], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "", f"forbidden modules loaded: {out.stdout.strip()}"
