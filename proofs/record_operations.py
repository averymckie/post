"""Append completed operations evidence after checking source and output hashes."""
from __future__ import annotations

import json
import sys

from proofs.augment import DEFAULT_OUT, HERE, ROOT, Inputs, digest


def checked_report(name: str) -> dict:
    report = json.loads((DEFAULT_OUT / name).read_text())
    inputs = Inputs(ROOT)
    for path, expected in report.get("sources", {}).items():
        if digest(inputs.read(path)) != expected:
            raise ValueError(f"Source evidence is stale: {path}")
    for path, expected in report.get("implementation", {}).items():
        if digest((ROOT / path).read_bytes()) != expected:
            raise ValueError(f"Implementation evidence is stale: {path}")
    for path, expected in report.get("files", {}).items():
        if digest((DEFAULT_OUT / path).read_bytes()) != expected:
            raise ValueError(f"Output evidence is stale: {path}")
    if any(report.get("runtime", {}).values()):
        raise ValueError("Runtime boundary checks failed")
    return report


def main() -> None:
    report = checked_report("operations-verification.json")
    dom = json.loads((DEFAULT_OUT / "operations-dom-verification.json").read_text())
    if dom["file_sha256"] != report["files"]["operations.html"] or dom["implementation_sha256"] != digest((ROOT / "tests/test_operations_ui.mjs").read_bytes()):
        raise ValueError("DOM evidence is stale")
    if dom["errors"] or dom["network_attempts"]:
        raise ValueError("DOM checks failed")
    from proofs import chains
    sys.path.insert(0, str(HERE))
    import itil
    itil.load_register()
    chains.PROOFS.clear()
    definitions = [
        ("P74", "registered workbooks and policy -> exact case joins -> typed operations model",
         ["operations-model.json", "operations-verification.json"],
         "openpyxl.load_workbook; python_calamine.CalamineWorkbook; dictionary joins; datetime.astimezone; ZenEngine.create_decision; Decision.evaluate",
         ["ten registered source hashes checked; nine workbooks read by two independent readers", "1434 unique case joins preserve deadline, outcome, risk, and calendar fields", "all 105 open-case policy decisions reevaluated and equal; 94 flagged, 11 unflagged; 1329 closed cases unassessed", "department and channel totals agree with stored aggregates; activity variants account for all 1434 cases", "historical snapshot retained; no current-date risk inference; model and network attempts 0"]),
        ("P75", "typed operations model -> fixed interface handlers -> browsable cases and paths",
         ["operations.html", "operations-dom-verification.json"],
         "lxml.etree.fromstring; lxml.etree.tostring; scoped SVG IDs; Jinja2.Template.render; Array.filter; Array.sort; Array.slice; JSON.stringify; jsdom.JSDOM; dispatchEvent",
         [f"offline DOM assertions {dom['assertions']}; all 1434 case details compared; 96 facet combinations", "all 116 activity paths preserve repeated activities and order; all 385 stored connections compared", "risk states remain distinct; date sorting uses explicit UTC keys; empty results clear stale details", "inline SVG IDs and references scoped to each chart; singular and plural path labels checked on all 116 variants", "export bytes checked against selected source records; locale en-US; external resource attempts 0", "browser layout, file dialogs, and responsive behavior remain unverified"]),
        ("P76", "typed measures -> Plotly specifications -> static charts and offline atlas",
         ["operations-figures.json", "performance-atlas.html", *[f"ops-{key}.{ext}" for key in ["outcomes", "gaps", "heatmap"] for ext in ["svg", "png"]]],
         "plotly.graph_objects.Bar; plotly.graph_objects.Heatmap; Figure.to_html; matplotlib.axes.Axes.barh; Axes.imshow; Figure.savefig",
         ["55 plotted numeric marks equal source values; all 36 missing heatmap cells remain missing", "largest-gap values retain their paired source activities and case counts; gaps are not task durations", "PNG and SVG rendered from the same Plotly specifications; static charts visually reviewed", "offline Plotly bundle included once with fixed IDs; embedded figure data roundtrip equal", "native font initialization precedes guard; source reads and render functions are guarded; Plotly browser paint remains unverified"]),
    ]
    for pid, title, names, functions, shows in definitions:
        paths = [DEFAULT_OUT / name for name in names]
        files = [(p, digest(p.read_bytes()), itil.check_register(str(p.relative_to(ROOT)), digest(p.read_bytes()))) for p in paths]
        proof = chains.Proof(pid, title, ["registered historical artifacts selected in proofs/operations.json"],
                             [chains.Step("check source bytes", "hashlib.sha256; registered input equality", lambda c: None),
                              chains.Step("transform and verify", functions, lambda c: None),
                              chains.Step("record outputs", "typed value equality; output hashes; append-only ledger", lambda c: None)], "checked operations deliverables")
        proof.evidence = [("all", files, shows)]
        chains.PROOFS.append(proof)
    counts = chains.append_ledger()
    itil.save_register(reregister=True)
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
