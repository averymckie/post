"""Print-engine review of the checked catalog state, with no external fetching."""
from __future__ import annotations

import base64
import json
import logging
import os
from pathlib import Path

from proofs.augment import DEFAULT_OUT, HERE, ROOT, canonical, digest, install_boundary
from proofs.operations_print import inspect_pdf
from proofs.record_operations import checked_report


def main() -> None:
    os.environ["SOURCE_DATE_EPOCH"] = "0"
    from weasyprint import HTML
    from lxml import html
    import fitz
    boundary = install_boundary()
    r = checked_report("gallery-verification.json")
    dom = json.loads((DEFAULT_OUT / "gallery-dom-verification.json").read_text())
    if dom["file_sha256"] != r["files"]["index.html"] or dom["errors"] or dom["network_attempts"]:
        raise ValueError("Gallery behavior evidence is stale or failed")
    snapshot = (HERE / "cache/gallery-snapshot.html").read_bytes()
    if digest(snapshot) != dom["snapshot_sha256"]:
        raise ValueError("Gallery snapshot changed after its behavior test")
    doc = html.fromstring(snapshot)
    if doc.xpath("//script | //iframe | //link[@href]"):
        raise ValueError("Gallery print source has active or external content")
    assets = {}
    for value in doc.xpath("//img/@src"):
        if not value.startswith("data:image/png;base64,"):
            raise ValueError("Only catalog-embedded PNGs are allowed")
        assets[value] = base64.b64decode(value.split(",", 1)[1], validate=True)
    requests, reads, messages = [], [], []
    def fetch(url, *args, **kwargs):
        if url not in assets:
            requests.append(url.split(",", 1)[0])
            raise ValueError("External resource fetching is forbidden")
        reads.append(digest(assets[url]))
        return {"string": assets[url], "mime_type": "image/png"}
    class Log(logging.Handler):
        def emit(self, record):
            messages.append(record.getMessage())
    logging.getLogger("weasyprint").addHandler(Log())
    result = HTML(string=snapshot.decode(), url_fetcher=fetch).write_pdf()
    if result != HTML(string=snapshot.decode(), url_fetcher=fetch).write_pdf():
        raise ValueError("Gallery print bytes are not repeatable")
    expected = [node.text_content() for node in doc.xpath("//*[@data-entry]//h3 | //*[@data-entry]/*[@class='description']")]
    check = inspect_pdf(result, expected, "gallery-review.pdf")
    if requests or any(boundary.values()):
        raise ValueError("Gallery print crossed the execution boundary")
    (HERE / "cache/gallery-review.pdf").write_bytes(result)
    report = {"file_sha256": r["files"]["index.html"], "snapshot_sha256": dom["snapshot_sha256"], "dom_report_sha256": digest((DEFAULT_OUT / "gallery-dom-verification.json").read_bytes()),
              "repeat_bytes_equal": True, "runtime": boundary, "resource_requests": requests, "embedded_image_reads": reads,
              "renderer_messages": sorted(set(messages)), "implementation": {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in [Path(__file__), HERE / "operations_print.py", HERE / "augment.py"]},
              "scope": "CSS print engine only; browser layout remains unverified", **check}
    (DEFAULT_OUT / "gallery-print-verification.json").write_bytes(canonical(report))
    print(json.dumps(check))


if __name__ == "__main__":
    main()
