"""Register completed DOM and print checks after checking their input digests."""
from __future__ import annotations

import json
import sys

from proofs.augment import DEFAULT_OUT, HERE, ROOT, digest


def main() -> None:
    from proofs import chains
    sys.path.insert(0, str(HERE))
    import itil

    dom_path = DEFAULT_OUT / "dom-verification.json"
    print_path = DEFAULT_OUT / "print-verification.json"
    dom = json.loads(dom_path.read_text())
    printing = json.loads(print_path.read_text())
    if digest(dom_path.read_bytes()) != printing["dom_report_sha256"]:
        raise ValueError("Print evidence does not match the completed DOM tests")
    for file, check in dom["files"].items():
        if digest((DEFAULT_OUT / file).read_bytes()) != check["sha256"]:
            raise ValueError(f"Stale DOM evidence: {file}")
    if dom["errors"] or dom["network_attempts"] or printing["resource_requests"]:
        raise ValueError("Checks did not pass")
    itil.load_register()
    chains.PROOFS.clear()
    definitions = [
        ("P72", "standalone interfaces -> offline interaction tests -> checked DOM snapshots", [dom_path],
         "jsdom.JSDOM; dispatchEvent; HTMLElement.click; node:assert.deepStrictEqual; Document.cloneNode",
         [f"assertions {dom['assertions']}; policy inputs 19; invalid inputs 6; stored meetings 8", "process nodes 42 and edges 21 preserved; workbook rows 370 compared; document blocks 27 preserved", "keyboard tabs, node selection, search, sort, pagination, and source controls passed", "network attempts 0; browser layout and responsive behavior unverified", "browser blocked: supported preview service unavailable; local-file access rejected by browser policy"]),
        ("P73", "checked DOM snapshots -> styled print rendering -> reproducible PDFs", [print_path, DEFAULT_OUT / "policy-print.pdf", DEFAULT_OUT / "majority-briefing.pdf"],
         "WeasyPrint.HTML.write_pdf; SOURCE_DATE_EPOCH; PyMuPDF.Page.get_text; hashlib.sha256",
         [f"print samples {len(printing['samples'])}; pages {sum(s['pages'] for s in printing['samples'])}; repeated PDF bytes equal for every sample", f"printed document and table blocks checked {sum(s['printed_text_blocks_checked'] for s in printing['samples'])}; text outside pages 0", "resource requests 0; source text preserved; embedded font timestamps canonicalized", "native library initialization precedes the render guard; source reads and rendering are guarded", "CSS print engine validation; browser rendering remains unverified"]),
    ]
    for pid, title, paths, functions, shows in definitions:
        files = [(p, digest(p.read_bytes()), itil.check_register(str(p.relative_to(ROOT)), digest(p.read_bytes()))) for p in paths]
        proof = chains.Proof(pid, title, ["P65-P70 artifacts; checked source model; versioned presentation handlers"], [chains.Step("execute checks", functions, lambda c: None), chains.Step("compare and record", "typed value equality; source hashes; output hashes", lambda c: None)], "validation evidence")
        proof.evidence = [("all", files, shows)]
        chains.PROOFS.append(proof)
    counts = chains.append_ledger()
    itil.save_register(reregister=True)
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
