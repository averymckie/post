"""P77-P78: registered case records and checked DOM states -> shareable PDFs."""
from __future__ import annotations

import importlib.metadata
import base64
import json
import logging
import os
from pathlib import Path
import re

from proofs.augment import DEFAULT_OUT, HERE, ROOT, Inputs, canonical, digest, install_boundary


def display(value):
    if value is None:
        return "Not recorded"
    if type(value) is bool:
        return "true" if value else "false"
    return str(value)


def brief_model(model: dict) -> list[dict]:
    cases = {row["case"]: row for row in model["cases"]}
    labels = {
        "case": "Case ID", "department": "Department", "channel": "Channel", "deadline": "Deadline",
        "enddate": "Recorded end", "last_event": "Last event", "outcome": "Recorded outcome",
        "deadline_utc": "Deadline, UTC", "deadline_epoch_ms": "Deadline, epoch ms", "start": "Start date",
        "calendar_days": "Calendar days", "working_days_nl": "Working days, NL", "at_risk": "Rule flag",
        "rule": "Rule ID", "elapsed_days_at_log_end": "Elapsed days at log end",
    }
    briefs = []
    for key in model["brief_cases"]:
        row = cases[key]
        risk = row["risk"]
        briefs.append({"record": row, "flag": "Not assessed" if risk is None else "Flagged" if risk["at_risk"] else "Unflagged",
                       "rule": "The recorded rule was applied to open cases only." if risk is None else f"{risk['rule']}: {model['risk_rules'][risk['rule']]}",
                       "case_fields": [(labels[k], display(row[k])) for k in ["case", "department", "channel", "outcome", "deadline", "deadline_utc", "deadline_epoch_ms", "enddate", "last_event"]],
                       "calendar_fields": [(labels[k], display(row["calendar"][k])) for k in ["case", "department", "start", "deadline", "calendar_days", "working_days_nl"]],
                       "risk_fields": [] if risk is None else [(labels[k], display(risk[k])) for k in ["case", "department", "at_risk", "rule", "elapsed_days_at_log_end"]]})
    return briefs


def compact(text):
    return re.sub(r"\s", "", text)


def inspect_pdf(data: bytes, expected: list[str], name: str) -> dict:
    import fitz
    pdf = fitz.open(stream=data, filetype="pdf")
    text = compact("".join(page.get_text() for page in pdf))
    missing = [value for value in expected if compact(value) not in text]
    if missing:
        raise ValueError(f"PDF content missing in {name}: {missing[:3]}")
    outside = []
    for index, page in enumerate(pdf):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    x0, y0, x1, y1 = span["bbox"]
                    if x0 < -1 or y0 < -1 or x1 > page.rect.width + 1 or y1 > page.rect.height + 1:
                        outside.append({"page": index + 1, "text": span["text"]})
    if outside:
        raise ValueError(f"Text outside pages in {name}: {outside[:3]}")
    result = {"pdf_sha256": digest(data), "pages": len(pdf), "text_values_checked": len(expected), "outside_page_text": outside}
    pdf.close()
    return result


def main() -> None:
    os.environ["SOURCE_DATE_EPOCH"] = "0"
    from weasyprint import HTML
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
    from lxml import html
    import fitz

    # Native text-library initialization precedes the guard. Source reads and
    # every render, comparison, and file handoff follow its installation.
    boundary = install_boundary()
    inputs = Inputs(ROOT)
    model_data = inputs.read("proofs/out/augmentation/operations-model.json")
    model = json.loads(model_data)
    dom_data = inputs.read("proofs/out/augmentation/operations-dom-verification.json")
    dom_report = json.loads(dom_data)
    if dom_report["errors"] or dom_report["network_attempts"] or digest(inputs.read("proofs/out/augmentation/operations.html")) != dom_report["file_sha256"]:
        raise ValueError("Operations DOM evidence is stale or failed")
    messages, requests, embedded_reads = [], [], []
    embedded = {}
    class Log(logging.Handler):
        def emit(self, record):
            messages.append(record.getMessage())
    logging.getLogger("weasyprint").addHandler(Log())
    def reject(url, *args, **kwargs):
        if url in embedded:
            embedded_reads.append(digest(embedded[url]))
            return {"string": embedded[url], "mime_type": "image/png"}
        requests.append(url.split(",", 1)[0])
        raise ValueError("Print resource fetching is forbidden")
    def render(source):
        first = HTML(string=source, url_fetcher=reject).write_pdf()
        if first != HTML(string=source, url_fetcher=reject).write_pdf():
            raise ValueError("Repeated PDF bytes disagree")
        return first

    briefs = brief_model(model)
    payload = {"snapshot": model["snapshot"], "sources": model["sources"], "model_sha256": digest(model_data), "cases": [b["record"] for b in briefs]}
    env = Environment(loader=FileSystemLoader(HERE / "ui"), autoescape=True, undefined=StrictUndefined)
    source = env.get_template("case-briefs.html").render(briefs=briefs, snapshot=model["snapshot"], model_sha256=digest(model_data), payload=payload)
    doc = html.fromstring(source)
    if json.loads(doc.get_element_by_id("brief-records").text) != payload or doc.xpath("//script[@src] | //link[@href] | //iframe | //img"):
        raise ValueError("Case brief readback or local asset check failed")
    expected = [node.text_content() for node in doc.xpath("//*[@data-value] | //p[@class='flag'] | //section[contains(@class,'assessment')]/p[last()]")]
    result = render(source)
    brief_check = inspect_pdf(result, expected, "case-briefs.pdf")
    if brief_check["pages"] != len(briefs):
        raise ValueError("Each case brief must occupy exactly one page")
    # Bind each printed page to its particular case and all of that case's values.
    pdf = fitz.open(stream=result, filetype="pdf")
    for index, brief in enumerate(briefs):
        page_text = compact(pdf[index].get_text())
        fields = brief["case_fields"] + brief["calendar_fields"] + brief["risk_fields"]
        if any(compact(v) not in page_text for _, v in fields) or compact(brief["flag"]) not in page_text:
            raise ValueError(f"Case brief page omitted fields: {brief['record']['case']}")
    pdf.close()
    (DEFAULT_OUT / "case-briefs.html").write_text(source)
    (DEFAULT_OUT / "case-briefs.json").write_bytes(canonical(payload))
    (DEFAULT_OUT / "case-briefs.pdf").write_bytes(result)

    samples = []
    packet = fitz.open()
    css = (HERE / "ui/operations-print.css").read_text()
    cache = HERE / "cache/operations-visual"
    for index, (name, expected_hash) in enumerate(dom_report["snapshots"].items()):
        data = (cache / name).read_bytes()
        if digest(data) != expected_hash:
            raise ValueError(f"Snapshot changed after DOM checks: {name}")
        tree = html.fromstring(data)
        if tree.xpath("//script | //iframe | //img | //link[@href]"):
            raise ValueError("Snapshots must contain no scripts or external assets")
        # Matplotlib's SVG contains local PNG rasters for the heatmap and its
        # color scale. Decode only assets already covered by the snapshot hash.
        embedded.clear()
        for node in tree.xpath("//*[local-name()='image']"):
            for key, value in node.attrib.items():
                if key.endswith("href"):
                    if not value.startswith("data:image/png;base64,"):
                        raise ValueError("Only checked embedded PNG assets are allowed")
                    image_data = base64.b64decode(re.sub(r"\s", "", value.split(",", 1)[1]), validate=True)
                    if not image_data.startswith(b"\x89PNG\r\n\x1a\n"):
                        raise ValueError("Embedded PNG signature mismatch")
                    embedded[value] = image_data
        style = html.Element("style")
        style.text = css + '\n@page{@bottom-right{content:"' + str(index + 1) + ' / ' + str(len(dom_report["snapshots"])) + '"}}'
        tree.find("head").append(style)
        if name.startswith("overview-"):
            key = name.removeprefix("overview-").removesuffix(".html")
            tree.find("body").set("class", "print-" + key)
            nodes = tree.xpath(f"//*[@data-chart='{key}']//*[local-name()='text']")
        elif name.startswith("case"):
            nodes = tree.xpath("//*[@id='detail-fields']/* | //*[@id='detail-id' or @id='detail-risk' or @id='detail-rule']")
        elif name.startswith("paths"):
            nodes = tree.xpath("//*[@id='path-steps']/li | //*[@id='path-title' or @id='path-summary']")
        else:
            selections = []
            for control, label in [("flow-from", "From"), ("flow-to", "To")]:
                option = tree.get_element_by_id(control).xpath("./option[@selected]")
                selections.append(label + ": " + (option[0].text_content() if option else "All"))
            selections.append("Minimum recorded value: " + tree.get_element_by_id("flow-min").get("value", "0"))
            note = html.Element("p", {"class": "print-context"})
            note.text = tree.get_element_by_id("flow-note").text_content() + " Filters: " + "; ".join(selections) + "."
            tree.get_element_by_id("ops-flows").insert(0, note)
            nodes = tree.xpath("//*[@id='flow-table']//td | //*[@id='flow-table']//th | //*[@id='flow-table']/caption")
            nodes.append(note)
        expected = [node.text_content() for node in nodes]
        printed = render(html.tostring(tree, encoding="unicode"))
        check = inspect_pdf(printed, expected, name)
        (cache / name.replace(".html", ".pdf")).write_bytes(printed)
        part = fitz.open(stream=printed, filetype="pdf")
        packet.insert_pdf(part)
        part.close()
        samples.append({"snapshot": name, "snapshot_sha256": expected_hash, "repeat_bytes_equal": True, **check})
    packet_data = packet.tobytes(garbage=4, deflate=True, no_new_id=True)
    packet.close()
    packet_check = inspect_pdf(packet_data, [], "operations-print-samples.pdf")
    (DEFAULT_OUT / "operations-print-samples.pdf").write_bytes(packet_data)
    if requests or any(boundary.values()):
        raise ValueError(f"Print chain crossed the runtime boundary: rejected resource types {requests}; {boundary=}")
    report = {"sources": inputs.used, "runtime": boundary, "resource_requests": requests, "embedded_image_reads": embedded_reads,
              "guard_scope": "Native imports precede the guard; source reads, rendering, and output checks are guarded",
              "versions": {n: importlib.metadata.version(n) for n in ["WeasyPrint", "PyMuPDF", "Jinja2", "fonttools"]},
              "case_briefs": {"case_ids": model["brief_cases"], "risk_states": [b["flag"] for b in briefs], "repeat_bytes_equal": True, "all_fields_checked_on_own_page": True, **brief_check},
              "print_samples": samples, "packet": packet_check, "renderer_messages": sorted(set(messages)),
              "implementation": {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in [Path(__file__), HERE / "augment.py", HERE / "ui/case-briefs.html", HERE / "ui/operations-print.css"]},
              "files": {name: digest((DEFAULT_OUT / name).read_bytes()) for name in ["case-briefs.html", "case-briefs.json", "case-briefs.pdf", "operations-print-samples.pdf"]},
              "scope": "CSS print engine checks; browser layout and browser print dialogs remain unverified"}
    (DEFAULT_OUT / "operations-print-verification.json").write_bytes(canonical(report))
    print(json.dumps({"case_briefs": brief_check, "snapshots": len(samples), "snapshot_pages": sum(s["pages"] for s in samples), "snapshot_text_values": sum(s["text_values_checked"] for s in samples), "resource_requests": len(requests), "renderer_messages": len(report["renderer_messages"])}))


if __name__ == "__main__":
    main()
