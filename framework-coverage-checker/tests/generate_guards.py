"""Generate the test body with the pinned public Ghostwriter callable."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hypothesis.extra import ghostwriter
from fwcheck.diagnostics import z3_integer_interval, cvc5_integer_interval
from fwcheck.io import write_json, digest

ROOT = Path(__file__).resolve().parents[1]
generated = ghostwriter.equivalent(z3_integer_interval, cvc5_integer_interval, style="unittest")
if "st.nothing()" in generated or "TODO" in generated:
    raise RuntimeError("Generated guard contains a vacuous or unfinished strategy")
(ROOT / "tests/test_generated_differential.py").write_text(generated)
write_json(ROOT / "results/guard-generation.json", {
    "generator": "hypothesis.extra.ghostwriter.equivalent", "version": "6.131.9", "style": "unittest",
    "assertion": "unittest.TestCase.assertEqual", "generated_source_sha256": digest(generated),
    "generated_test_functions": 1, "targets": ["fwcheck.diagnostics.z3_integer_interval", "fwcheck.diagnostics.cvc5_integer_interval"],
    "scope": "Differential generated-input regression of project-owned bindings and independent encoders. Does not qualify every P302/P344 premise or actual domain implementation."})
