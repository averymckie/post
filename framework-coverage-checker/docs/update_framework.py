"""Apply the explicit amendment to the frozen baseline without changing proof bodies."""
from pathlib import Path
import difflib
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fwcheck.io import file_hash, write_json
from fwcheck.catalogue import index_framework

ROOT = Path(__file__).resolve().parents[1]
baseline = ROOT / "data/framework-baseline.txt"
original = baseline.read_text()
old = "The coverage method explores operations, composition forms and the dimensions that alter semantics. Repeated patterns belong in parameterized families. A materially different output type, state behavior, construction procedure or acceptance argument can require a new family or rule. A finite grammar can express unboundedly many finite compositions. Demonstrating that a particular grammar covers every possible real-world requirement needs a separate completeness argument; the 38-family partition remains a working classification."
new = "Coverage testing starts with practical and diverse cases generated independently from the world. The case generator receives no framework families, grammar, proofs or mapping feedback. Freeze those cases before reverse engineering each requirement into the frozen framework. A failure can identify a missing family, composition form, axis value, boundary rule, adapter or proof, but incomplete case detail and bounded search failure must retain their own states. Repeated world-side patterns may motivate parameterized families after the test. A finite grammar can express unboundedly many finite compositions; completeness over real-world requirements needs a separate argument. The 38-family partition remains a working classification. Section 11 records the implemented bounded checker and its evidence limits."
assert original.count(old) == 1
updated = original.replace(old, new)
anchor = "Existing anchors: P14, P15, P24, P25, P39, P73, P80, P83, P87, P88, P109, P121, P124, P140, P151, P165, P167."
replacement = anchor.replace("P88, P109", "P88, P99, P109")
assert updated.count(anchor) == 1
updated = updated.replace(anchor, replacement)
updated = updated.rstrip() + "\n\n" + (ROOT / "docs/framework-amendment.md").read_text().rstrip() + "\n"
target = ROOT / "data/framework-updated.txt"
target.write_text(updated)
diff = "".join(difflib.unified_diff(original.splitlines(keepends=True), updated.splitlines(keepends=True),
                                  fromfile="framework-baseline.txt", tofile="framework-updated.txt"))
(ROOT / "docs/framework-changes.patch").write_text(diff)
before, after = index_framework(baseline), index_framework(target)
assert set(before["families"]) == set(after["families"])
assert set(before["proofs"]) == set(after["proofs"])
assert all(before["proofs"][p]["text"].rstrip() == after["proofs"][p]["text"].rstrip() for p in before["proofs"])
assert all(before["families"][f]["text"].rstrip() == after["families"][f]["text"].rstrip() for f in before["families"] if f != "F29")
write_json(ROOT / "results/framework-update-verification.json", {
    "baseline_sha256": file_hash(baseline), "updated_sha256": file_hash(target),
    "family_count_preserved": len(after["families"]), "proof_count_preserved": len(after["proofs"]),
    "all_349_proof_bodies_preserved": True, "unrelated_37_family_cards_preserved": True,
    "changes": ["Independent world-case generation made explicit in section 1", "P99 added to F29 anchors", "Section 11 CK01 implemented scope, recorded results and open hardening items added"]})
print(file_hash(target))
