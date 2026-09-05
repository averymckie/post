"""Checked DOM snapshots -> CSS print renderer -> PDF samples and evidence.

Run after proofs.augment and tests/test_augmentation_ui.mjs. This is a print
engine check, not browser layout testing. All resource fetching is rejected.
"""
from __future__ import annotations

import importlib.metadata
import json
import logging
import os
import re
from pathlib import Path

from proofs.augment import DEFAULT_OUT, HERE, ROOT, canonical, digest, install_boundary


def main() -> None:
    # Canonical packaging time for embedded font tables, not source content.
    os.environ["SOURCE_DATE_EPOCH"] = "0"
    from weasyprint import HTML
    from lxml import html
    import fitz

    # Native imports use the system's library resolver before the render guard.
    # No input is read and no rendering occurs before the guard is installed.
    boundary = install_boundary()

    dom_report = json.loads((DEFAULT_OUT / "dom-verification.json").read_text())
    for filename, record in dom_report["files"].items():
        if digest((DEFAULT_OUT / filename).read_bytes()) != record["sha256"]:
            raise ValueError(f"DOM test evidence is stale: {filename}")
    attempts = []
    def reject(url: str, *args, **kwargs):
        attempts.append(url)
        raise ValueError("PDF resource fetching is forbidden")
    messages: list[str] = []
    class Log(logging.Handler):
        def emit(self, record):
            messages.append(record.getMessage())
    logging.getLogger("weasyprint").addHandler(Log())
    snapshots = HERE / "cache/visual"
    rendered = []
    for name, expected in dom_report["snapshots"].items():
        source = snapshots / name
        data = source.read_bytes()
        if digest(data) != expected:
            raise ValueError(f"Snapshot changed after interaction test: {name}")
        doc = html.fromstring(data)
        if doc.xpath("//script | //iframe | //img | //link[@href]"):
            raise ValueError("Print snapshots must have no scripts or external assets")
        result = HTML(string=data.decode(), url_fetcher=reject).write_pdf()
        repeat = HTML(string=data.decode(), url_fetcher=reject).write_pdf()
        if result != repeat:
            raise ValueError(f"PDF generation is not repeatable: {name}")
        pdf_path = source.with_suffix(".pdf")
        pdf_path.write_bytes(result)
        pdf = fitz.open(stream=result, filetype="pdf")
        outside = []
        for p, page in enumerate(pdf):
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        x0, y0, x1, y1 = span["bbox"]
                        if x0 < -1 or y0 < -1 or x1 > page.rect.width + 1 or y1 > page.rect.height + 1:
                            outside.append({"page": p + 1, "text": span["text"]})
        if outside:
            raise ValueError(f"Text extends outside PDF pages in {name}: {outside[:3]}")
        checked_blocks = 0
        if name.startswith(("briefing-", "records-")):
            section = "document-body" if name.startswith("briefing-") else "records-table"
            expected_nodes = doc.get_element_by_id(section).xpath(".//td | .//th | .//p | .//blockquote | .//h2 | .//h3")
            printed = re.sub(r"\s", "", "".join(page.get_text() for page in pdf))
            for node in expected_nodes:
                if re.sub(r"\s", "", node.text_content()) not in printed:
                    raise ValueError(f"Printed content missing in {name}: {node.text_content()[:80]}")
            checked_blocks = len(expected_nodes)
        rendered.append({"snapshot": name, "snapshot_sha256": expected, "pdf_sha256": digest(result), "pages": len(pdf), "repeat_bytes_equal": True, "outside_page_text": outside, "printed_text_blocks_checked": checked_blocks})
        if name in {"policy.html", "briefing-0.html"}:
            target = DEFAULT_OUT / ("policy-print.pdf" if name == "policy.html" else "majority-briefing.pdf")
            target.write_bytes(result)
        pdf.close()
    if attempts or boundary["model_import_attempts"] or boundary["external_execution_attempts"]:
        raise ValueError("Print rendering crossed the execution boundary")
    versions = {n: importlib.metadata.version(n) for n in ["WeasyPrint", "PyMuPDF", "fonttools", "pydyf", "tinycss2", "tinyhtml5", "cssselect2", "cffi", "pyphen", "Pillow"]}
    report = {"engine": "WeasyPrint", "version": versions["WeasyPrint"], "versions": versions, "scope": "CSS print layout; browser layout and responsive behavior remain unverified", "guard_scope": "Rendering and source reads are guarded; native library imports precede the guard", "dom_report_sha256": digest((DEFAULT_OUT / "dom-verification.json").read_bytes()), "samples": rendered, "resource_requests": attempts, "runtime": boundary, "renderer_messages": sorted(set(messages)), "implementation_sha256": digest(Path(__file__).read_bytes())}
    (DEFAULT_OUT / "print-verification.json").write_bytes(canonical(report))
    print(json.dumps({"print_samples": len(rendered), "pages": sum(r["pages"] for r in rendered), "outside_page_text": 0, "resource_requests": len(attempts), "renderer_messages": len(report["renderer_messages"])}))


if __name__ == "__main__":
    main()
