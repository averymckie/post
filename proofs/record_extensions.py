"""Register completed case, print, and gallery extensions after integrity checks."""
from __future__ import annotations

import argparse
import json
import sys

from proofs.augment import DEFAULT_OUT, HERE, ROOT, digest
from proofs.record_operations import checked_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", choices=["print", "gallery"])
    args = parser.parse_args()
    if args.part == "print":
        r = checked_report("operations-print-verification.json")
        if r["resource_requests"]:
            raise ValueError("Print checks attempted external resources")
        definitions = [
            ("P77", "registered case selections -> defined brief fields -> one-page case briefs",
             ["case-briefs.html", "case-briefs.json", "case-briefs.pdf"],
             "dictionary field mapping; Jinja2.Template.render; WeasyPrint.HTML.write_pdf; PyMuPDF.Page.get_text",
             ["three historical cases: flagged, unflagged, and not assessed; every selected source field retained", f"three one-page briefs; {r['case_briefs']['text_values_checked']} printed values checked; all fields checked on their own case page", "HTML typed-record roundtrip equal; missing values remain explicit; original timestamps and rule IDs retained", "repeated PDF bytes equal; text outside pages 0; source reads and rendering guarded"]),
            ("P78", "checked interface states -> print stylesheet -> operations print collection",
             ["operations-print-samples.pdf", "operations-print-verification.json"],
             "lxml.html.fromstring; base64.b64decode for checked embedded PNGs; WeasyPrint.HTML.write_pdf; PyMuPDF.Document.insert_pdf; Page.get_text",
             [f"ten checked DOM states; {sum(s['pages'] for s in r['print_samples'])} printed pages; {sum(s['text_values_checked'] for s in r['print_samples'])} source text values preserved", "chart, case, path, and connection print states rendered and visually reviewed", "embedded heatmap and color-scale PNGs decoded only from hash-checked snapshots; external resource requests 0", "repeated sample PDF bytes equal; text outside pages 0; browser rendering and browser print dialogs unverified"]),
        ]
    else:
        r = checked_report("gallery-verification.json")
        dom = json.loads((DEFAULT_OUT / "gallery-dom-verification.json").read_text())
        if dom["file_sha256"] != r["files"]["index.html"] or dom["implementation_sha256"] != digest((ROOT / "tests/test_gallery_ui.mjs").read_bytes()) or dom["errors"] or dom["network_attempts"]:
            raise ValueError("Gallery DOM evidence is stale or failed")
        printing = checked_report("gallery-print-verification.json")
        if printing["file_sha256"] != dom["file_sha256"] or printing["dom_report_sha256"] != digest((DEFAULT_OUT / "gallery-dom-verification.json").read_bytes()) or printing["resource_requests"]:
            raise ValueError("Gallery print evidence is stale or failed")
        workflow = json.loads((DEFAULT_OUT / "workflow-verification.json").read_text())
        if not workflow["completed"] or workflow["coordinator_boundary_attempts"] or workflow["implementation_sha256"] != digest((HERE / "run_augmentation.py").read_bytes()):
            raise ValueError("Fixed workflow evidence is stale or failed")
        for name, expected in workflow["evidence"].items():
            if digest((DEFAULT_OUT / name).read_bytes()) != expected:
                raise ValueError(f"Workflow evidence is stale: {name}")
        definitions = [
            ("P79", "registered deliverables -> typed catalog -> searchable collection",
             ["index.html", "catalog.json", "gallery-verification.json", "gallery-dom-verification.json", "gallery-print-verification.json", "workflow-verification.json"],
             "hashlib.sha256; Jinja2.Template.render; Array.filter; DOM.hidden; jsdom.JSDOM; WeasyPrint.HTML.write_pdf",
             [f"{r['catalog_entries']} deliverables; {r['artifact_links_checked']} distinct registered artifact links checked", f"{dom['assertions']} offline DOM assertions; {dom['filter_combinations']} search and format combinations; keyboard navigation checked", "all referenced deliverable bytes match the source register; thumbnails embedded from registered PNGs", f"complete P65-P79 workflow uses fixed commands and fails on the first failed handoff; {workflow['tests']['tests']} presentation and operations tests passed", "print rendering reviewed; browser layout remains unverified; model and network attempts 0"]),
        ]
    from proofs import chains
    sys.path.insert(0, str(HERE))
    import itil
    itil.load_register()
    chains.PROOFS.clear()
    for pid, title, names, functions, shows in definitions:
        paths = [DEFAULT_OUT / name for name in names]
        files = [(p, digest(p.read_bytes()), itil.check_register(str(p.relative_to(ROOT)), digest(p.read_bytes()))) for p in paths]
        proof = chains.Proof(pid, title, ["previously registered source artifacts and their checked execution evidence"],
                             [chains.Step("check inputs", "registered source hashes; explicit output contracts", lambda c: None),
                              chains.Step("transform and verify", functions, lambda c: None),
                              chains.Step("append evidence", "source equality; output hashes; append-only ledger", lambda c: None)], "checked presentation extension")
        proof.evidence = [("all", files, shows)]
        chains.PROOFS.append(proof)
    counts = chains.append_ledger()
    itil.save_register(reregister=True)
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
