"""P79: registered deliverables -> typed catalog -> searchable offline entry page."""
from __future__ import annotations

import base64
import json
from pathlib import Path

from proofs.augment import DEFAULT_OUT, HERE, ROOT, Inputs, canonical, digest, install_boundary


ENTRIES = [
    ("workbench", "workbench.html", "Core workbench", "interfaces", "P70", "Five connected views for policies, processes, records, briefings, and discussion maps.", "DOM tested"),
    ("operations", "operations.html", "Operations desk", "interfaces", "P75", "Explore 1,434 historical cases, follow activity paths, and inspect every connection.", "DOM tested"),
    ("atlas", "performance-atlas.html", "Performance atlas", "interfaces", "P76", "Three interactive Plotly charts with exact values and the complete bundle included locally.", "Figure data checked"),
    ("briefs", "case-briefs.html", "Case brief collection", "interfaces", "P77", "Read the flagged, unflagged, and unassessed cases alongside their original source fields.", "Print checked"),
    ("policy", "policy.html", "Policy explorer", "interfaces", "P65", "Explore the recorded majority rule and its complete 19-row truth table.", "DOM tested"),
    ("process", "process.html", "Process explorer", "interfaces", "P66", "Follow recorded dependencies across two processes, with source IDs and citations.", "DOM tested"),
    ("records", "records.html", "Workbook records", "interfaces", "P67", "Search, sort, and page through 370 original rows across three workbook views.", "DOM tested"),
    ("briefing", "briefing.html", "Policy briefings", "interfaces", "P68", "Read the original policy explanations and charter actions in their recorded order.", "DOM tested"),
    ("slides", "slides.html", "Discussion map", "interfaces", "P69", "Inspect the deck's text and explicitly connected discussion elements.", "DOM tested"),
    ("policy-print", "policy-print.pdf", "Majority rule printout", "documents", "P73", "A checked print view of the recorded majority policy.", "Print reviewed"),
    ("majority-briefing", "majority-briefing.pdf", "Policy explanation brief", "documents", "P73", "The original explanation blocks in a printable reading layout.", "Print reviewed"),
    ("case-pdf", "case-briefs.pdf", "Three case briefs", "documents", "P77", "One page per selected case, with risk state, calendar values, and source provenance.", "Print reviewed"),
    ("print-samples", "operations-print-samples.pdf", "Operations print collection", "documents", "P78", "Ten checked views of the overview, cases, activity paths, and connections.", "Print reviewed"),
    ("outcomes", "ops-outcomes.png", "Recorded case outcomes", "figures", "P76", "All 1,434 cases grouped by their stored outcome. Available in PNG and SVG.", "Values checked"),
    ("gaps", "ops-gaps.png", "Largest activity gaps", "figures", "P76", "The ten largest recorded mean intervals between paired activities. PNG and SVG.", "Values checked"),
    ("heatmap", "ops-heatmap.png", "Department activity measures", "figures", "P76", "Recorded mean intervals by activity and department, with missing values preserved. PNG and SVG.", "Values checked"),
]


def main() -> None:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
    from lxml import html
    boundary = install_boundary()
    inputs = Inputs(ROOT)
    model = json.loads(inputs.read("proofs/out/augmentation/operations-model.json"))
    entries = []
    for key, name, title, category, proof, description, evidence in ENTRIES:
        data = inputs.read("proofs/out/augmentation/" + name)
        entry = {"id": key, "file": name, "title": title, "category": category, "proof": proof, "description": description,
                 "evidence": evidence, "sha256": digest(data), "bytes": len(data), "format": Path(name).suffix[1:].upper(), "alternates": [], "thumbnail": ""}
        if category == "figures":
            alternative = name.removesuffix(".png") + ".svg"
            svg = inputs.read("proofs/out/augmentation/" + alternative)
            entry["alternates"].append({"file": alternative, "format": "SVG", "sha256": digest(svg), "bytes": len(svg)})
            entry["thumbnail"] = "data:image/png;base64," + base64.b64encode(data).decode()
        entries.append(entry)
    public = [{k: v for k, v in entry.items() if k != "thumbnail"} for entry in entries]
    catalog = {"locale": "en-US", "checkpoint": "P79", "snapshot": model["snapshot"], "cases": model["summary"]["cases"], "entries": public}
    env = Environment(loader=FileSystemLoader(HERE / "ui"), autoescape=True, undefined=StrictUndefined)
    source = env.get_template("gallery.html").render(catalog=catalog, entries=entries, css=(HERE / "ui/gallery.css").read_text(), js=(HERE / "ui/gallery.js").read_text())
    doc = html.fromstring(source)
    if json.loads(doc.get_element_by_id("gallery-model").text) != catalog or doc.get("lang") != "en-US":
        raise ValueError("Catalog readback or locale check failed")
    links = doc.xpath("//*[@data-artifact]/@href")
    expected = {e["file"] for e in entries} | {a["file"] for e in entries for a in e["alternates"]}
    if set(links) != expected:
        raise ValueError("Gallery artifact links disagree with the registered catalog")
    if doc.xpath("//script[@src] | //link[@href] | //iframe") or any(not src.startswith("data:image/png;base64,") for src in doc.xpath("//img/@src")):
        raise ValueError("Gallery has external dependencies")
    (DEFAULT_OUT / "index.html").write_text(source)
    (DEFAULT_OUT / "catalog.json").write_bytes(canonical(catalog))
    report = {"sources": inputs.used, "runtime": boundary, "catalog_entries": len(entries), "artifact_links_checked": len(expected), "link_instances_checked": len(links),
              "implementation": {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in [Path(__file__), HERE / "augment.py", *sorted((HERE / "ui").glob("gallery.*"))]},
              "files": {name: digest((DEFAULT_OUT / name).read_bytes()) for name in ["index.html", "catalog.json"]},
              "scope": "Registered file and HTML payload checks; browser layout remains unverified"}
    if any(boundary.values()):
        raise ValueError("Catalog execution crossed the runtime boundary")
    (DEFAULT_OUT / "gallery-verification.json").write_bytes(canonical(report))
    print(json.dumps({"entries": len(entries), "verified_links": len(expected), "runtime": boundary}))


if __name__ == "__main__":
    main()
