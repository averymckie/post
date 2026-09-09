#!/usr/bin/env python3
"""Render one iteration's report section from its mapping JSON plus a hand-written findings file.

Usage: python3 coverage/render_iteration.py NN findings.md >> coverage/REPORT.md
The tables are derived from the mapping; the findings prose is the hand-written part.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tally  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def main():
    nn = sys.argv[1]
    findings_path = sys.argv[2]
    m = json.load(open(os.path.join(ROOT, "iterations", f"{nn}.mapping.json"), encoding="utf-8"))
    a = m["agent"]
    r = m["agent_reported"]
    cases = m["cases"]
    out = []
    out.append(f"## Iteration {m['iteration']}")
    out.append("")
    out.append("### Agent run")
    out.append("")
    out.append("| Field | Value |")
    out.append("| --- | --- |")
    for k in ["model_selector", "subagent_type", "started_utc", "duration_ms", "tool_uses", "subagent_tokens", "raw", "raw_note", "prompt_file_sha256", "prompt_received_sha256", "prompt_identity"]:
        if k in a:
            out.append(f"| {k} | {esc(a[k])} |")
    out.append("")
    out.append("### Agent-reported discovery and sampling")
    out.append("")
    out.append("| Field | Value |")
    out.append("| --- | --- |")
    for k in ["isic_version", "ford_version", "seed", "randomness_tool", "runtime", "sampling_algorithm", "inventory_size", "inventory_sha256", "categories", "selected", "read_status_selected", "source_acquisition", "scope_decision"]:
        if k in r:
            out.append(f"| {k} | {esc(r[k])} |")
    out.append("")
    out.append("Discovery shortages (agent side, kept separate from coverage gaps):")
    for s in r.get("shortages", []):
        out.append(f"- {s}")
    out.append("")
    out.append("### Per-case mapping")
    out.append("")
    out.append("| Case | Origin | Cat. | Src | Families (primary first) | O | C | V | R | X | Anchors | Verdict |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for c in cases:
        out.append("| " + " | ".join([
            c["id"], esc(c["origin"]), c.get("category", ""), c.get("source_status", ""),
            " ".join(c.get("families", [])), " ".join(c.get("O", [])), " ".join(c.get("C", [])),
            " ".join(c.get("V", [])) or "-", " ".join(c.get("R", [])), c.get("X") or "-",
            " ".join(c.get("anchors", [])), c["verdict"] + (" (" + "; ".join(c["blocking"]) + ")" if c.get("blocking") else ""),
        ]) + " |")
    out.append("")
    out.append("Axis values per case:")
    for c in cases:
        out.append(f"- {c['id']}: {', '.join(c.get('A', []))}")
    out.append("")
    out.append("Mapping notes:")
    for c in cases:
        if c.get("note"):
            out.append(f"- **{c['id']}**: {c['note']}")
    out.append("")
    out.append("### Stress variations")
    out.append("")
    out.append("| Case | # | Changed condition | Maps to | Expressed |")
    out.append("| --- | --- | --- | --- | --- |")
    for c in cases:
        s = c.get("stress") or {}
        if not s:
            continue
        out.append(f"| {c['id']} | {s.get('n','')} | {esc(s.get('condition',''))} | {esc(', '.join(s.get('maps_to', [])))} | {'yes' if s.get('expressed') else 'no'}: {esc(s.get('note',''))} |")
    out.append("")
    if m.get("composed_systems"):
        out.append("### Composed wholes proposed by the agent, compared with X01 to X12")
        out.append("")
        out.append("| Composed system | Members | Families | Closest chain | R | Note |")
        out.append("| --- | --- | --- | --- | --- | --- |")
        for cs in m["composed_systems"]:
            out.append(f"| {cs['id']} {esc(cs['title'])} | {' '.join(cs['members'])} | {' '.join(cs['families'])} | {cs.get('X') or '-'} | {' '.join(cs.get('R', []))} | {esc(cs['note'])} |")
        out.append("")
    if m.get("generators"):
        out.append("### Generators proposed by the agent, compared with F37")
        out.append("")
        out.append("| Generator | Families | Anchors | Note |")
        out.append("| --- | --- | --- | --- |")
        for g in m["generators"]:
            out.append(f"| {g['id']} {esc(g['title'])} | {' '.join(g['families'])} | {' '.join(g['anchors'])} | {esc(g['note'])} |")
        out.append("")
    out.append("### Family fits without an anchoring proof record (candidate additions, not counted)")
    out.append("")
    any_na = False
    for c in cases:
        for na in c.get("no_anchor", []):
            any_na = True
            out.append(f"- {c['id']}: {na}")
    if not any_na:
        out.append("- none")
    out.append("")
    out.append("### Extension proposals (never counted as coverage)")
    out.append("")
    if m.get("extension_proposals"):
        for e in m["extension_proposals"]:
            out.append(f"- {e}")
    else:
        out.append("- none")
    if m.get("extension_note"):
        out.append("")
        out.append(m["extension_note"])
    out.append("")
    out.append("### Findings")
    out.append("")
    out.append(open(findings_path, encoding="utf-8").read().rstrip())
    out.append("")
    its = tally.load()
    its = [it for it in its if it["iteration"] <= m["iteration"]]
    out.append(tally.block(its))
    out.append("")
    print("\n".join(out))


if __name__ == "__main__":
    main()
