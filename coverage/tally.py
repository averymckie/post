#!/usr/bin/env python3
"""Render cumulative conceptual-coverage tables from coverage/iterations/*.mapping.json.

The judgments in the mapping files are made by hand. This script only counts.
Usage: python3 coverage/tally.py            -> cumulative block for the latest iteration
       python3 coverage/tally.py --all      -> cumulative block after every iteration
"""
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FAMILY_NAMES = {
    "F01": "Source formalization and operating-model assembly",
    "F02": "Entity identity and relationship registries",
    "F03": "Data transformation, migration and synchronization",
    "F04": "Query, retrieval and knowledge navigation",
    "F05": "Rules, policies and scoped decisions",
    "F06": "Authority, access, delegation and information release",
    "F07": "Admission, readiness and lifecycle transitions",
    "F08": "Agreements, entitlements and recurring obligations",
    "F09": "Workflow and case coordination",
    "F10": "Collaborative review and decision records",
    "F11": "Planning, scheduling and qualified assignment",
    "F12": "Routing, packing and network allocation",
    "F13": "Transactions, external effects and reconciliation",
    "F14": "Quantitative ledgers, allocation and valuation",
    "F15": "Material supply and fulfillment",
    "F16": "Asset maintenance and service reliability",
    "F17": "Measurement, analytics and reporting",
    "F18": "Prediction, inference and uncertainty",
    "F19": "Diagnosis and next-evidence selection",
    "F20": "Trade-off, portfolio and allocation decisions",
    "F21": "Simulation and digital twins",
    "F22": "Experiment and measurement campaigns",
    "F23": "Learning, assessment and qualification paths",
    "F24": "Software application construction and maintenance",
    "F25": "API, connector and event-service construction",
    "F26": "Infrastructure, deployment and operations configuration",
    "F27": "Engineering design and manufacturing preparation",
    "F28": "Spatial and spatiotemporal information products",
    "F29": "Document, media and communication construction",
    "F30": "Interactive interfaces and visualization construction",
    "F31": "Verification, qualification and assurance",
    "F32": "Change impact, repair and modernization",
    "F33": "Recovery, replay and records lifecycle",
    "F34": "Streaming detection and governed response",
    "F35": "Physical control and embedded automation",
    "F36": "Analytical model construction and deployment",
    "F37": "Product-family configurator generation",
    "F38": "Assembly of systems from multiple families",
}
SETS = {
    "O": [f"O{i:02d}" for i in range(1, 19)],
    "C": [f"C{i:02d}" for i in range(1, 15)],
    "V": [f"V{i:02d}" for i in range(1, 19)],
    "R": [f"R{i:02d}" for i in range(1, 33)],
    "X": [f"X{i:02d}" for i in range(1, 13)],
}
AXES = [f"A{i:02d}" for i in range(1, 19)]
VERDICTS = ["COVERED", "PARTIAL", "UNCOVERED", "NO-WITNESS"]


def load():
    files = sorted(glob.glob(os.path.join(ROOT, "iterations", "*.mapping.json")))
    its = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            its.append(json.load(fh))
    its.sort(key=lambda d: d["iteration"])
    return its


def block(its):
    n = its[-1]["iteration"]
    cases = [(it["iteration"], c) for it in its for c in it["cases"]]
    out = []
    out.append(f"#### Cumulative after iteration {n}")
    out.append("")
    verd = collections.Counter(c["verdict"] for _, c in cases)
    origins = {c["origin"] for _, c in cases}
    stress_total = sum(1 for _, c in cases if c.get("stress"))
    stress_expr = sum(1 for _, c in cases if c.get("stress") and c["stress"].get("expressed") is True)
    out.append("| Measure | Value |")
    out.append("| --- | --- |")
    out.append(f"| Iterations | {n} |")
    out.append(f"| Cases mapped | {len(cases)} |")
    out.append(f"| Unique origin clusters | {len(origins)} |")
    for v in VERDICTS:
        out.append(f"| {v} | {verd.get(v, 0)} |")
    out.append(f"| Stress variations expressed by catalogue | {stress_expr} of {stress_total} |")
    ext = sum(len(it.get("extension_proposals", [])) for it in its)
    out.append(f"| Extension proposals (not counted as coverage) | {ext} |")
    out.append("")
    # families
    fam_cases = collections.Counter()
    fam_primary = collections.Counter()
    fam_iters = collections.defaultdict(set)
    for i, c in cases:
        fams = c.get("families", [])
        for f in set(fams):
            fam_cases[f] += 1
            fam_iters[f].add(i)
        if fams:
            fam_primary[fams[0]] += 1
    out.append("| Family | Name | Cases (any role) | Cases (primary) | Iterations hit |")
    out.append("| --- | --- | --- | --- | --- |")
    for f, name in FAMILY_NAMES.items():
        its_hit = ",".join(str(x) for x in sorted(fam_iters[f])) or "-"
        out.append(f"| {f} | {name} | {fam_cases.get(f, 0)} | {fam_primary.get(f, 0)} | {its_hit} |")
    never = [f for f in FAMILY_NAMES if fam_cases.get(f, 0) == 0]
    out.append("")
    out.append(f"Families never hit: {', '.join(never) if never else 'none'}")
    out.append("")
    # O C V R X
    for key, ids in SETS.items():
        cnt = collections.Counter()
        for _, c in cases:
            vals = c.get(key)
            if vals is None:
                continue
            if isinstance(vals, str):
                vals = [vals]
            for v in set(vals):
                cnt[v] += 1
        hit = [f"{i}({cnt[i]})" for i in ids if cnt.get(i)]
        miss = [i for i in ids if not cnt.get(i)]
        out.append(f"{key} exercised: {', '.join(hit) if hit else 'none'}")
        out.append(f"{key} never exercised: {', '.join(miss) if miss else 'none'}")
        out.append("")
    # axes values
    ax = collections.defaultdict(collections.Counter)
    for _, c in cases:
        for v in c.get("A", []):
            if ":" in v:
                a, val = v.split(":", 1)
                ax[a][val.strip()] += 1
    out.append("| Axis | Values seen (count) |")
    out.append("| --- | --- |")
    for a in AXES:
        vals = ", ".join(f"{k}({n_}))".replace("))", ")") for k, n_ in sorted(ax[a].items())) or "-"
        out.append(f"| {a} | {vals} |")
    out.append("")
    # categories
    cats = collections.defaultdict(set)
    for _, c in cases:
        cat = c.get("category", "")
        if cat:
            scheme = cat.split()[0]
            cats[scheme].add(cat)
    for scheme in sorted(cats):
        out.append(f"{scheme} categories with at least one mapped case: {', '.join(sorted(cats[scheme]))}")
    out.append("")
    # gap ledger
    gaps = [(i, c) for i, c in cases if c["verdict"] != "COVERED"]
    out.append("Gap ledger (catalogue side):")
    if not gaps:
        out.append("- none")
    for i, c in gaps:
        blocking = "; ".join(c.get("blocking", [])) or c.get("gap") or "-"
        out.append(f"- it{i} {c['id']} [{c['verdict']}]: {blocking}")
    out.append("")
    # family-fit-no-anchor
    noanchor = [(i, c) for i, c in cases if c.get("no_anchor")]
    out.append("Family fits but no anchoring proof record:")
    if not noanchor:
        out.append("- none")
    for i, c in noanchor:
        out.append(f"- it{i} {c['id']}: {'; '.join(c['no_anchor'])}")
    out.append("")
    # duplicates across iterations
    seen = collections.defaultdict(list)
    for i, c in cases:
        seen[c["origin"]].append((i, c["id"]))
    dups = {k: v for k, v in seen.items() if len({i for i, _ in v}) > 1}
    out.append("Origin clusters rediscovered in more than one iteration:")
    if not dups:
        out.append("- none")
    for k, v in sorted(dups.items()):
        out.append(f"- {k}: " + ", ".join(f"it{i} {cid}" for i, cid in v))
    out.append("")
    return "\n".join(out)


def main():
    its = load()
    if not its:
        print("no mapping files", file=sys.stderr)
        sys.exit(1)
    if "--all" in sys.argv:
        for k in range(1, len(its) + 1):
            print(block(its[:k]))
            print()
    else:
        print(block(its))


if __name__ == "__main__":
    main()
