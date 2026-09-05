"""Case joins, source fidelity, plotted data, and complete-run determinism."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from proofs.augment import ROOT, Inputs
from proofs.operations import dictionaries, join_cases, utc, workbook


@pytest.fixture(scope="module")
def outputs(tmp_path_factory):
    base = tmp_path_factory.mktemp("operations")
    paths = []
    for seed in ("17", "99991"):
        path = base / seed
        process = subprocess.run([sys.executable, "-m", "proofs.operations", "--output", str(path)], cwd=ROOT, env={**os.environ, "PYTHONHASHSEED": seed}, capture_output=True, text=True, timeout=100)
        assert process.returncode == 0, process.stderr
        paths.append(path)
    return paths


def test_full_run_bytes_match_across_hash_seeds(outputs):
    a, b = outputs
    assert sorted(p.name for p in a.iterdir()) == sorted(p.name for p in b.iterdir())
    for path in a.iterdir():
        assert path.read_bytes() == (b / path.name).read_bytes(), path.name
    report = json.loads((a / "operations-verification.json").read_text())
    assert report["runtime"] == {"model_import_attempts": [], "external_execution_attempts": []}


def test_every_joined_case_preserves_all_three_source_rows(outputs):
    model = json.loads((outputs[0] / "operations-model.json").read_text())
    config = json.loads((ROOT / "proofs/operations.json").read_text())
    inputs = Inputs(ROOT)
    for name, sheet, nested in [("cases", "cases", None), ("risk", "open_cases", "risk"), ("calendar", "cases", "calendar")]:
        table = workbook(inputs.read(config[name]))[sheet]
        original = {row[0]: dict(zip(table["columns"], row)) for row in table["rows"]}
        for case in model["cases"]:
            actual = case[nested] if nested else {key: case[key] for key in table["columns"]}
            assert actual == original.get(case["case"])
    assert len(model["cases"]) == 1434
    assert model["summary"] == {"cases": 1434, "outcomes": {"open": 105, "by deadline": 952, "after deadline": 377}, "flagged": 94, "assessed": 105, "variants": 116}
    assert model["checks"]["zen_risk_agreement"] == 105


def test_variant_paths_preserve_order_and_repeated_activities(outputs):
    model = json.loads((outputs[0] / "operations-model.json").read_text())
    assert sum(row["cases"] for row in model["variants"]) == 1434
    assert any(len(set(row["steps"])) < len(row["steps"]) for row in model["variants"])
    for row in model["variants"]:
        assert " -> ".join(row["steps"]) == row["variant"]
        assert len(row["steps"]) == row["length"]


def test_figures_preserve_nulls_zeros_and_original_numeric_values(outputs):
    model = json.loads((outputs[0] / "operations-model.json").read_text())
    specs = json.loads((outputs[0] / "operations-figures.json").read_text())
    heat = model["tables"]["heatmap"]["mean_hours"]
    assert specs["heatmap"]["data"][0]["z"] == [[row[i] for row in heat["rows"]] for i in range(1, len(heat["columns"]))]
    flattened = [v for row in specs["heatmap"]["data"][0]["z"] for v in row]
    assert None in flattened and 0 in flattened
    raw = model["tables"]["bottlenecks"]["bottlenecks"]["rows"]
    for value, reference in zip(specs["gaps"]["data"][0]["x"], specs["gaps"]["data"][0]["customdata"]):
        assert value == raw[reference[0]][3]
        assert reference[1] == raw[reference[0]][2]


def test_embedded_svg_ids_and_references_are_scoped(outputs):
    import re
    from lxml import html
    page = html.fromstring((outputs[0] / "operations.html").read_bytes())
    ids = page.xpath("//@id")
    assert len(ids) == len(set(ids))
    for panel in page.xpath("//*[@data-chart]"):
        prefix = "ops-" + panel.get("data-chart") + "-"
        local = set(panel.xpath(".//*[@id]/@id"))
        assert local and all(value.startswith(prefix) for value in local)
        for node in panel.iter():
            for key, value in node.attrib.items():
                if key.endswith("href") and value.startswith("#"):
                    assert value[1:] in local
                for reference in re.findall(r"url\(#([^)]+)\)", value):
                    assert reference in local


@pytest.mark.parametrize("change", ["duplicate", "missing", "department", "deadline", "risk_scope"])
def test_ambiguous_or_incomplete_joins_fail_closed(change):
    cases = [{"case": "a", "department": "D", "channel": "C", "outcome": "open", "deadline": "2020-01-02 00:00:00+00:00", "enddate": None, "last_event": "2020-01-01 00:00:00+00:00"}]
    risk = [{"case": "a", "department": "D", "at_risk": False, "rule": "r0", "elapsed_days_at_log_end": 0}]
    calendar = [{"case": "a", "department": "D", "start": "2020-01-01", "deadline": "2020-01-02", "calendar_days": 1, "working_days_nl": 1}]
    if change == "duplicate": cases.append(copy.deepcopy(cases[0]))
    if change == "missing": calendar.clear()
    if change == "department": risk[0]["department"] = "Other"
    if change == "deadline": calendar[0]["deadline"] = "2020-01-03"
    if change == "risk_scope": cases[0]["outcome"] = "by deadline"
    with pytest.raises(ValueError): join_cases(cases, risk, calendar)


def test_utc_sort_key_keeps_offsets_and_rejects_naive_dates():
    assert utc("2020-01-01 12:00:00+01:00") == utc("2020-01-01 11:00:00+00:00")
    with pytest.raises(ValueError, match="offset"):
        utc("2020-01-01 12:00:00")
