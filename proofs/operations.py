"""P74-P76: registered workbooks -> typed cases -> offline operational views."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import importlib.metadata
import io
import json
import math
import os
from pathlib import Path
import textwrap

from proofs.augment import DEFAULT_OUT, HERE, ROOT, Inputs, canonical, digest, install_boundary


def workbook(data: bytes) -> dict:
    from openpyxl import load_workbook
    from python_calamine import CalamineWorkbook

    book = load_workbook(io.BytesIO(data), read_only=True, data_only=False)
    independent = CalamineWorkbook.from_filelike(io.BytesIO(data))
    result = {}
    for sheet in book:
        values = [list(row) for row in sheet.values]
        other = [[None if value == "" else value for value in row] for row in independent.get_sheet_by_name(sheet.title).to_python()]
        if not values or not all(isinstance(x, str) and x for x in values[0]) or len(values[0]) != len(set(values[0])):
            raise ValueError("Workbook needs unique string column names")
        if any(isinstance(v, str) and v.startswith("=") for row in values[1:] for v in row):
            raise ValueError("An explicit formula-value adapter is required")
        if values != other:
            raise ValueError(f"Independent readers disagree: {sheet.title}")
        result[sheet.title] = {"columns": values[0], "rows": values[1:]}
    book.close()
    return result


def dictionaries(table: dict, columns: list[str]) -> list[dict]:
    if table["columns"] != columns:
        raise ValueError(f"Unexpected columns: {table['columns']}")
    return [dict(zip(columns, row, strict=True)) for row in table["rows"]]


def unique(rows: list[dict]) -> dict:
    result = {}
    for row in rows:
        key = row["case"]
        if not isinstance(key, str) or key in result:
            raise ValueError("Case keys must be unique strings")
        result[key] = row
    return result


def utc(value: str) -> tuple[str, float]:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("An explicit timestamp offset is required")
    normalized = parsed.astimezone(timezone.utc)
    return normalized.isoformat(), normalized.timestamp() * 1000


def join_cases(cases: list[dict], risks: list[dict], calendars: list[dict]) -> list[dict]:
    base, risk, calendar = unique(cases), unique(risks), unique(calendars)
    if base.keys() != calendar.keys():
        raise ValueError("Calendar and deadline case sets must match exactly")
    if set(risk) != {key for key, row in base.items() if row["outcome"] == "open"}:
        raise ValueError("Risk assessments must match the open-case set exactly")
    result = []
    for row in cases:
        key = row["case"]
        if row["department"] != calendar[key]["department"] or key in risk and row["department"] != risk[key]["department"]:
            raise ValueError("Department mismatch across joined records")
        if row["deadline"].split(" ")[0] != calendar[key]["deadline"]:
            raise ValueError("Deadline dates disagree across joined records")
        if row["outcome"] not in {"open", "by deadline", "after deadline"}:
            raise ValueError("Unknown recorded outcome")
        iso, milliseconds = utc(row["deadline"])
        result.append({**row, "risk": risk.get(key), "calendar": calendar[key], "deadline_utc": iso, "deadline_epoch_ms": milliseconds})
    return result


def source_model() -> dict:
    import zen

    config = json.loads((HERE / "operations.json").read_text())
    if config["locale"] != "en-US" or config["runtime"] != {"llm_reasoning": "forbidden", "network": "forbidden"}:
        raise ValueError("The execution contract cannot be relaxed")
    inputs = Inputs(ROOT)
    tables = {key: workbook(inputs.read(config[key])) for key in ["cases", "risk", "calendar", "groups", "flows", "variants", "heatmap", "bottlenecks", "handover"]}
    cases = dictionaries(tables["cases"]["cases"], ["case", "department", "channel", "deadline", "enddate", "last_event", "outcome"])
    risks = dictionaries(tables["risk"]["open_cases"], ["case", "department", "elapsed_days_at_log_end", "at_risk", "rule"])
    calendar = dictionaries(tables["calendar"]["cases"], ["case", "department", "start", "deadline", "calendar_days", "working_days_nl"])
    joined = join_cases(cases, risks, calendar)
    policy_bytes = inputs.read(config["risk_policy"])
    policy = json.loads(policy_bytes)
    decision = zen.ZenEngine().create_decision(policy_bytes.decode())
    for row in risks:
        if type(row["at_risk"]) is not bool or not math.isfinite(row["elapsed_days_at_log_end"]):
            raise ValueError("Invalid risk input types")
        if decision.evaluate({"department": row["department"], "elapsed_days": row["elapsed_days_at_log_end"]})["result"] != {"at_risk": row["at_risk"], "rule": row["rule"]}:
            raise ValueError("Stored risk decision disagrees with Zen")
    rule_table = next(node["content"] for node in policy["nodes"] if node["type"] == "decisionTableNode")
    rules = {rule["_id"]: rule["_description"] for rule in rule_table["rules"]}
    if any(row["rule"] not in rules for row in risks):
        raise ValueError("Unknown risk rule")
    for group in ["department", "channel"]:
        actual = Counter(row[group] for row in cases)
        expected = {row[0]: row[1] for row in tables["groups"][group]["rows"]}
        if dict(actual) != expected:
            raise ValueError(f"Group counts disagree: {group}")
    variants = dictionaries(tables["variants"]["variants"], ["cases", "length", "variant"])
    for index, variant in enumerate(variants):
        steps = variant["variant"].split(" -> ")
        if len(steps) != variant["length"]:
            raise ValueError("Variant length disagrees with stored sequence")
        variant.update({"id": index, "steps": steps})
    if sum(row["cases"] for row in variants) != len(cases):
        raise ValueError("Variant case total disagrees with the case table")
    snapshot = max(utc(row["last_event"])[0] for row in cases)
    selected = list(config["brief_cases"])
    selected.append(next(row["case"] for row in risks if not row["at_risk"]))
    return {"version": config["version"], "locale": config["locale"], "note": config["note"], "sources": inputs.used,
            "tables": tables, "cases": joined, "variants": variants, "risk_rules": rules, "snapshot": snapshot,
            "summary": {"cases": len(cases), "outcomes": dict(Counter(row["outcome"] for row in cases)), "flagged": sum(row["at_risk"] for row in risks), "assessed": len(risks), "variants": len(variants)},
            "brief_cases": selected, "checks": {"independent_workbook_readers": len(tables), "unique_case_join": len(joined), "zen_risk_agreement": len(risks), "group_count_agreement": ["department", "channel"], "variant_total": len(cases)}}


def figures(model: dict) -> dict:
    import plotly.graph_objects as go

    summary = model["summary"]
    order = ["by deadline", "after deadline", "open"]
    outcomes = go.Figure(go.Bar(x=[summary["outcomes"][x] for x in order], y=order, orientation="h", marker_color=["#086e61", "#b96035", "#517f99"], text=[summary["outcomes"][x] for x in order], textposition="outside", hovertemplate="%{y}: %{x} cases<extra></extra>"))
    bottlenecks = model["tables"]["bottlenecks"]["bottlenecks"]["rows"]
    top = sorted(enumerate(bottlenecks), key=lambda item: (-item[1][3], item[0]))[:10]
    gaps = go.Figure(go.Bar(x=[row[3] for _, row in top], y=[f"{row[0]} → {row[1]}" for _, row in top], orientation="h", marker_color="#086e61", customdata=[[i, row[2]] for i, row in top], hovertemplate="%{y}<br>%{x:.2f} hours<br>%{customdata[1]} recorded cases<extra></extra>"))
    heatmap = model["tables"]["heatmap"]["mean_hours"]
    heat = go.Figure(go.Heatmap(x=[row[0] for row in heatmap["rows"]], y=heatmap["columns"][1:], z=[[row[i] for row in heatmap["rows"]] for i in range(1, len(heatmap["columns"]))], colorscale=[[0, "#e7f1ed"], [1, "#086e61"]], colorbar={"title": "Hours"}, hoverongaps=False, hovertemplate="%{x}<br>%{y}<br>%{z:.2f} hours<extra></extra>"))
    catalog = {
        "outcomes": {"title": "Recorded case outcomes", "note": "Counts across the complete receipt-phase dataset.", "figure": outcomes, "height": 360},
        "gaps": {"title": "Largest recorded gaps between activities", "note": "Top ten stored mean waiting intervals. These values do not measure task duration.", "figure": gaps, "height": 800},
        "heatmap": {"title": "Elapsed time by department and activity", "note": "Mean hours since the previous event. Blank cells mean no recorded value, not zero.", "figure": heat, "height": 1100},
    }
    for key, item in catalog.items():
        item["figure"].update_layout(template="none", paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", font={"family": "Arial, sans-serif", "color": "#172e35", "size": 12}, height=item["height"], margin={"l": 370 if key == "gaps" else 290 if key == "heatmap" else 125, "r": 65, "t": 35, "b": 70}, yaxis={"autorange": "reversed", "automargin": True}, xaxis={"title": "Cases" if key == "outcomes" else "Hours" if key == "gaps" else "Department", "gridcolor": "#e6eeea", "zeroline": False})
        item["spec"] = json.loads(item["figure"].to_json())
    return catalog


def static_chart(key: str, item: dict, output: Path) -> dict:
    import matplotlib
    from matplotlib.figure import Figure
    import numpy as np

    trace = item["spec"]["data"][0]
    with matplotlib.rc_context({"font.family": "DejaVu Sans", "font.size": 10, "svg.hashsalt": "function-chain-operations-v1", "svg.fonttype": "none", "axes.edgecolor": "#cbd8d4", "text.color": "#172e35", "axes.labelcolor": "#52666d", "xtick.color": "#52666d", "ytick.color": "#52666d"}):
        fig = Figure(figsize=(11, 5 if key == "outcomes" else 9 if key == "gaps" else 14), facecolor="white")
        ax = fig.subplots()
        if key == "heatmap":
            z = np.array([[float("nan") if v is None else v for v in row] for row in trace["z"]])
            from matplotlib.colors import LinearSegmentedColormap
            colors = LinearSegmentedColormap.from_list("chain", ["#e7f1ed", "#086e61"])
            colors.set_bad("#e5e9e7")
            artist = ax.imshow(np.ma.masked_invalid(z), cmap=colors, aspect="auto", interpolation="nearest")
            ax.set_xticks(range(len(trace["x"])), trace["x"])
            ax.set_yticks(range(len(trace["y"])), [textwrap.fill(label, 40) for label in trace["y"]], fontsize=9)
            for y, row in enumerate(trace["z"]):
                for x, value in enumerate(row):
                    ax.text(x, y, "n/a" if value is None else f"{value:.2f}", ha="center", va="center", fontsize=8, color="white" if value is not None and value > np.nanmax(z) * .55 else "#172e35")
            fig.colorbar(artist, ax=ax, fraction=.035, pad=.04, label="Hours")
            fig.subplots_adjust(left=.39, right=.94, top=.9, bottom=.06)
            plotted = [[None if not math.isfinite(v) else float(v) for v in row] for row in z]
            if plotted != trace["z"]:
                raise ValueError("Heatmap values changed during plotting")
            count = sum(v is not None for row in trace["z"] for v in row)
        else:
            labels = [textwrap.fill(label, 55 if key == "gaps" else 30) for label in trace["y"]]
            bars = ax.barh(range(len(labels)), trace["x"], color=trace["marker"]["color"], height=.58)
            ax.set_yticks(range(len(labels)), labels, fontsize=9 if key == "gaps" else 12)
            ax.invert_yaxis()
            ax.set_xlabel("Recorded cases" if key == "outcomes" else "Mean hours between the paired activities")
            ax.set_xlim(0, max(trace["x"]) * 1.2)
            ax.xaxis.grid(True, color="#e6eeea"); ax.set_axisbelow(True)
            for i, bar in enumerate(bars):
                ax.text(bar.get_width() + max(trace["x"]) * .02, bar.get_y() + bar.get_height() / 2, f"{trace['x'][i]:,}" if key == "outcomes" else f"{trace['x'][i]:.2f} h", va="center", fontsize=10)
            if [bar.get_width() for bar in bars] != trace["x"]:
                raise ValueError("Bar values changed during plotting")
            fig.subplots_adjust(left=.52 if key == "gaps" else .19, right=.97, top=.87, bottom=.11)
            count = len(bars)
        for side in ["top", "right", "left"]:
            ax.spines[side].set_visible(False)
        ax.tick_params(axis="y", length=0, pad=10)
        fig.text(.045, .965, item["title"], fontsize=17, weight="bold", va="top")
        fig.text(.045, .915 if key == "outcomes" else .935, textwrap.fill(item["note"], 110), fontsize=10, color="#52666d", va="top")
        svg = io.BytesIO(); fig.savefig(svg, format="svg", metadata={"Date": None, "Creator": "Function Chain"})
        png = io.BytesIO(); fig.savefig(png, format="png", dpi=120, metadata={"Software": "Function Chain"})
        (output / f"ops-{key}.svg").write_bytes(svg.getvalue())
        (output / f"ops-{key}.png").write_bytes(png.getvalue())
        return {"marks_checked": count, "svg_sha256": digest(svg.getvalue()), "png_sha256": digest(png.getvalue())}


def render(model: dict, charts: dict, output: Path) -> None:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
    from lxml import etree

    env = Environment(loader=FileSystemLoader(HERE / "ui"), autoescape=True, undefined=StrictUndefined)
    colors = json.loads((HERE / "presentation.json").read_text())["theme"]
    svg = {}
    for key in charts:
        node = etree.fromstring((output / f"ops-{key}.svg").read_bytes(), parser=etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True))
        ids = {element.get("id"): f"ops-{key}-{element.get('id')}" for element in node.iter() if element.get("id")}
        for element in node.iter():
            if element.get("id"):
                element.set("id", ids[element.get("id")])
            for attribute, value in list(element.attrib.items()):
                if attribute.endswith("href") and value.startswith("#"):
                    value = "#" + ids[value[1:]]
                for old, new in ids.items():
                    value = value.replace(f"url(#{old})", f"url(#{new})")
                element.set(attribute, value)
        svg[key] = etree.tostring(node, encoding="unicode")
    (output / "operations.html").write_text(env.get_template("operations.html").render(model=model, css=(HERE / "ui/operations.css").read_text(), js=(HERE / "ui/operations.js").read_text(), theme=colors, charts=charts, svg=svg))
    sections = []
    for i, (key, item) in enumerate(charts.items()):
        plot = item["figure"].to_html(full_html=False, include_plotlyjs=i == 0, include_mathjax=False, div_id="atlas-" + key, config={"responsive": True, "displaylogo": False, "displayModeBar": False, "scrollZoom": False})
        sections.append({**item, "plot": plot})
    specs = {key: item["spec"] for key, item in charts.items()}
    (output / "performance-atlas.html").write_text(env.get_template("performance-atlas.html").render(charts=sections, specs=specs, css=(HERE / "ui/operations.css").read_text(), theme=colors))
    (output / "operations-figures.json").write_bytes(canonical(specs))


def build(output: Path, boundary: dict) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    model = source_model()
    charts = figures(model)
    chart_checks = {key: static_chart(key, chart, output) for key, chart in charts.items()}
    render(model, charts, output)
    (output / "operations-model.json").write_bytes(canonical(model))
    from lxml import html
    for name, expected in [("operations.html", model), ("performance-atlas.html", {key: item["spec"] for key, item in charts.items()})]:
        doc = html.fromstring((output / name).read_bytes())
        if json.loads(doc.get_element_by_id("operations-model" if name == "operations.html" else "atlas-model").text) != expected:
            raise ValueError("Embedded data roundtrip failed")
        if doc.get("lang") != "en-US" or doc.xpath("//script[@src] | //link[@href] | //iframe"):
            raise ValueError("Interface has invalid locale or external dependencies")
        ids = doc.xpath("//@id")
        if len(ids) != len(set(ids)):
            raise ValueError("Inline components must use distinct element IDs")
    if any(boundary.values()):
        raise ValueError("Execution crossed the declared boundary")
    files = ["operations-model.json", "operations.html", "performance-atlas.html", "operations-figures.json"] + [f"ops-{key}.{ext}" for key in charts for ext in ["svg", "png"]]
    report = {"model_sha256": digest(canonical(model)), "sources": model["sources"], "checks": model["checks"], "chart_checks": chart_checks, "runtime": boundary,
              "guard_scope": "Model joins, policy evaluation, rendering, and output checks are guarded; native plotting initialization precedes the guard",
              "versions": {name: importlib.metadata.version(name) for name in ["openpyxl", "python-calamine", "zen-engine", "matplotlib", "plotly", "numpy", "Jinja2"]},
              "implementation": {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in [Path(__file__), HERE / "augment.py", HERE / "operations.json", HERE / "presentation.json", *sorted((HERE / "ui").glob("operations.*")), HERE / "ui/performance-atlas.html"]},
              "files": {name: digest((output / name).read_bytes()) for name in files},
              "browser": "unverified; supported browser preview unavailable; no alternate browser attempted"}
    (output / "operations-verification.json").write_bytes(canonical(report))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    os.environ["SOURCE_DATE_EPOCH"] = "0"
    os.environ.setdefault("MPLCONFIGDIR", str(HERE / "cache/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager
    font_manager.findfont("DejaVu Sans")
    boundary = install_boundary()
    report = build(args.output, boundary)
    print(json.dumps({"cases": report["checks"]["unique_case_join"], "risk_checks": report["checks"]["zen_risk_agreement"], "files": len(report["files"]), "sources": len(report["sources"])}))


if __name__ == "__main__":
    main()
