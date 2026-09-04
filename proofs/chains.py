"""The proofs, as code.

Every proof is a chain of steps.  A step is a plain-English change bound to the
functions that perform it.  Running this file executes every chain on the real
inputs under packs/ and proofs/in/, writes each deliverable under proofs/out/,
and writes PROOFS.md at the repository root: the chains in arrow form, each
followed by its deliverables and their SHA-256 digests.

    .venv/bin/python proofs/chains.py
"""
from __future__ import annotations

import collections
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "proofs" / "out"
MD = ROOT / "PROOFS.md"
os.environ.setdefault("PM4PY_SHOW_PROGRESS_BAR", "false")

# ----------------------------------------------------------------------------
# framework
# ----------------------------------------------------------------------------


@dataclass
class Step:
    change: str
    fns: str
    run: Callable[[dict[str, Any]], None]


@dataclass
class Proof:
    pid: str
    title: str
    inputs: list[str]  # lines naming what enters; two names on one line is a join
    steps: list[Step]
    result: str
    evidence: list[tuple[str, list[tuple[Path, str]], list[str]]] = field(default_factory=list)


PROOFS: list[Proof] = []
RESULTS: dict[str, Any] = {}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sha256_json(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


def out_dir(pid: str, label: str) -> Path:
    d = OUT / pid / label
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_json(p: Path, obj: Any) -> Path:
    p.write_text(json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return p


def write_jsonl(p: Path, rows: list[Any]) -> Path:
    with p.open("w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True, ensure_ascii=False, default=str) + "\n")
    return p


def workbook(p: Path, sheets: dict[str, list[list[Any]]]) -> Path:
    import openpyxl

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for name, rows in sheets.items():
        ws = wb.create_sheet(name[:31])
        for r in rows:
            ws.append([("" if v is None else v) if isinstance(v, (int, float, str)) or v is None else str(v) for v in r])
    wb.save(p)
    return p


def run(proof: Proof, label: str, ctx: dict[str, Any]) -> dict[str, Any]:
    for s in proof.steps:
        s.run(ctx)
    files = [(p, sha256_file(p)) for p in ctx.get("files", [])]
    existing = next((p for p in PROOFS if p.pid == proof.pid), None)
    if existing is None:
        PROOFS.append(proof)
        existing = proof
    existing.evidence.append((label, files, ctx.get("shows", [])))
    return ctx


STOP = set(
    "the a an of to in on at by for and or is are be was were been being with as that this these those it its "
    "from into than then there their they them he she his her we our you your i me my will would shall should "
    "may might must can could not no nor if but so such any all each other which who whom what when where how "
    "also more most very only same do does did done has have had having about over under between within after "
    "before upon per via etc one two three four five six seven eight nine ten".split()
)


def lit(s: Any) -> str:
    """A clingo string literal."""
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z\-']+", text.lower()) if w not in STOP and len(w) > 2}


# ----------------------------------------------------------------------------
# door one: procedures -> facts ; facts -> ordered steps -> digest
# ----------------------------------------------------------------------------

from compiled_ai.pack import model_path, read_sources  # noqa: E402
from compiled_ai.parse import parse_source  # noqa: E402
from compiled_ai.fol import compile_atoms  # noqa: E402
from compiled_ai.normalize import normalize  # noqa: E402
from compiled_ai.check import check_atoms  # noqa: E402
from compiled_ai.adjudicate import apply_rejections, load_rejections  # noqa: E402
from compiled_ai.reconcile import reconcile  # noqa: E402
from compiled_ai.order import order as order_atoms  # noqa: E402
from compiled_ai.seal import manifest_json, seal  # noqa: E402

PACKS = {
    "usc5-552-doj": ROOT / "packs" / "foia",
    "nodejs-tsc-charter": ROOT / "packs" / "nodejs-tsc-charter",
    "nodejs-governance": ROOT / "packs" / "nodejs-governance",
    "nodejs-tsc-minutes": ROOT / "packs" / "nodejs-tsc-minutes",
}


def s_read(ctx: dict[str, Any]) -> None:
    sources, errs = read_sources(ctx["pack"])
    assert not errs, errs
    ctx["sources"] = sources


def s_parse(ctx: dict[str, Any]) -> None:
    mp = model_path(ctx["pack"])
    ctx["parsed"] = [ps for s in ctx["sources"] for ps in parse_source(s, mp)]


def s_extract(ctx: dict[str, Any]) -> None:
    ctx["atoms"] = compile_atoms(ctx["parsed"])


def s_route(ctx: dict[str, Any]) -> None:
    ctx["atoms"], ctx["candidates"] = normalize(ctx["atoms"], ctx["parsed"])


def s_check(ctx: dict[str, Any]) -> None:
    check_atoms(ctx["atoms"], ctx["parsed"])


def s_adjudicate(ctx: dict[str, Any]) -> None:
    ctx["atoms"] = apply_rejections(ctx["atoms"], load_rejections(ctx["pack"] / "rejections.yaml"))
    d = ctx["dir"]
    p = write_jsonl(d / "facts.jsonl", [a.model_dump() for a in ctx["atoms"]])
    ctx["files"] = [p]
    ctx["shows"] = [f"facts {len(ctx['atoms'])}; sentences {len(ctx['parsed'])}"] + [
        f'{a.predicate}({", ".join(x.split("#")[-1] for x in a.args)})  "{a.quote}"' for a in ctx["atoms"][:4]
    ]


def door_one(label: str) -> dict[str, Any]:
    proof = Proof(
        "P1",
        "procedures -> facts",
        ["procedures"],
        [
            Step("read", "compiled_ai.read.read_html | compiled_ai.read.read_text; html.parser.HTMLParser", s_read),
            Step("canonical text", "compiled_ai.canon.canonicalize; unicodedata.normalize NFC", lambda c: None),
            Step("dependency parse", "compiled_ai.parse.parse_source; ufal.udpipe.Pipeline.process", s_parse),
            Step("predicate extraction", "compiled_ai.fol.compile_atoms; predpatt.PredPatt", s_extract),
            Step("project", "compiled_ai.fol.compile_atoms; projection table as data", lambda c: None),
            Step("route roles", "compiled_ai.normalize.normalize; clorm.clingo.Control, two rules as data", s_route),
            Step("byte check", "compiled_ai.check.check_atoms; sentence.text[lo:hi] == quote", s_check),
            Step("adjudicate", "compiled_ai.adjudicate.apply_rejections; yaml.safe_load", s_adjudicate),
        ],
        "facts",
    )
    ctx = {"pack": PACKS[label], "dir": out_dir("P1", label), "label": label}
    run(proof, label, ctx)
    RESULTS[("facts", label)] = ctx
    return ctx


def s_reconcile(ctx: dict[str, Any]) -> None:
    ctx["rec"] = reconcile(ctx["atoms"])


def s_order(ctx: dict[str, Any]) -> None:
    ctx["ordering"] = order_atoms(ctx["atoms"])
    d = ctx["dir"]
    o = ctx["ordering"]
    ctx["files"] = [write_json(d / "ordered_steps.json", o.model_dump())]
    lemma = {a.args[0]: a.args[1] for a in ctx["atoms"] if a.predicate == "event"}
    ctx["shows"] = [f"consistent: {ctx['rec'].consistent}; cycle: {list(o.cycle)}"] + [
        f"{lemma.get(a, '?')} -> {lemma.get(b, '?')}   forced" for a, b in o.forced[:4]
    ]


def s_seal(ctx: dict[str, Any]) -> None:
    m = seal(ctx["pack"].name, ctx["sources"], ctx["parsed"], ctx["atoms"], ctx["rec"], ctx["ordering"], model_path(ctx["pack"]))
    ctx["manifest"] = m
    p = ctx["dir"] / "manifest.json"
    p.write_text(manifest_json(m), encoding="utf-8")
    ctx["files"].append(p)
    ctx["shows"].append(f"digest {m.digest}")


def door_one_order(label: str) -> dict[str, Any]:
    src = RESULTS[("facts", label)]
    proof = Proof(
        "P2",
        "facts -> ordered steps -> digest",
        ["facts"],
        [
            Step("consistency proof", "compiled_ai.reconcile.reconcile; z3.Solver.check, z3.Solver.unsat_core", s_reconcile),
            Step("forced order", "compiled_ai.order.order; networkx.transitive_reduction, networkx.lexicographical_topological_sort", s_order),
            Step("seal", "compiled_ai.seal.seal; json.dumps, hashlib.sha256", s_seal),
        ],
        "ordered steps, digest",
    )
    ctx = dict(src)
    ctx["dir"] = out_dir("P2", label)
    ctx["files"] = []
    run(proof, label, ctx)
    RESULTS[("ordered steps", label)] = ctx
    return ctx


# ----------------------------------------------------------------------------
# P3 facts -> anchor dates
# ----------------------------------------------------------------------------


def s_timexy(ctx: dict[str, Any]) -> None:
    import spacy
    import timexy  # noqa: F401

    nlp = spacy.blank("en")
    nlp.add_pipe("timexy", config={"kb_id_type": "timex3", "label": "timexy", "overwrite": False})
    sents = {ps.sentence.id: ps.sentence.text for ps in ctx["parsed"]}
    rows: list[dict[str, Any]] = []
    for sid, text in sorted(sents.items()):
        for e in nlp(text).ents:
            rows.append({"sentence_id": sid, "span": e.text, "timex3": e.kb_id_, "sentence": text})
    ctx["anchors"] = rows
    p = write_jsonl(ctx["dir"] / "anchor_dates.jsonl", rows)
    ctx["files"] = [p]
    ctx["shows"] = [f'"{r["span"]}" -> {r["timex3"]}' for r in rows[:4]]


def anchor_dates(label: str) -> dict[str, Any]:
    src = RESULTS[("facts", label)]
    proof = Proof(
        "P3",
        "facts -> anchor dates",
        ["facts"],
        [Step("anchor dates", "timexy (spacy.blank('en').add_pipe('timexy')); TIMEX3 durations and dates", s_timexy)],
        "anchor dates",
    )
    ctx = dict(src)
    ctx["dir"] = out_dir("P3", label)
    run(proof, label, ctx)
    RESULTS[("anchor dates", label)] = ctx
    return ctx


# ----------------------------------------------------------------------------
# P4 facts -> required actions -> decision table -> policy
# ----------------------------------------------------------------------------

JDM_TEMPLATE = """{
 "contentType": "application/vnd.gorules.decision",
 "nodes": [
  {"id": "in", "type": "inputNode", "name": "request", "position": {"x": 0, "y": 0}},
  {"id": "dt", "type": "decisionTableNode", "name": "required actions", "position": {"x": 0, "y": 0},
   "content": {"hitPolicy": "first",
    "inputs": [{"id": "i1", "name": "action", "field": "action"}],
    "outputs": [{"id": "o1", "name": "required", "field": "required"}, {"id": "o2", "name": "rule", "field": "rule"}],
    "rules": [
{% for r in rows %}     {"_id": "r{{ loop.index }}", "_description": {{ r.quote|tojson }}, "i1": {{ (r.action|tojson)|tojson }}, "o1": "true", "o2": "'r{{ loop.index }}'"}{{ "," if not loop.last }}
{% endfor %}    ]}},
  {"id": "out", "type": "outputNode", "name": "decision", "position": {"x": 0, "y": 0}}
 ],
 "edges": [{"id": "e1", "sourceId": "in", "targetId": "dt", "type": "edge"}, {"id": "e2", "sourceId": "dt", "targetId": "out", "type": "edge"}]
}
"""


def s_required(ctx: dict[str, Any]) -> None:
    atoms = ctx["atoms"]
    lemma = {a.args[0]: a.args[1] for a in atoms if a.predicate == "event"}
    quote = {a.sentence_id: a.quote for a in atoms}
    rows = []
    for a in atoms:
        if a.predicate == "obligatory":
            e = a.args[0]
            rows.append({"event": e, "action": lemma.get(e, "?"), "sentence_id": a.sentence_id, "quote": a.quote})
    ctx["required"] = rows
    ctx["shows"] = [f'{r["action"]}  "{r["quote"]}"' for r in rows[:3]]


def s_decision_table(ctx: dict[str, Any]) -> None:
    import jinja2

    rows = ctx["required"]
    seen: set[str] = set()
    uniq = [r for r in rows if not (r["action"] in seen or seen.add(r["action"]))]
    jdm = jinja2.Environment().from_string(JDM_TEMPLATE).render(rows=uniq)
    json.loads(jdm)
    p = ctx["dir"] / "policy.jdm.json"
    p.write_text(jdm, encoding="utf-8")
    ctx["jdm"] = jdm
    ctx["files"] = [p]


def s_policy(ctx: dict[str, Any]) -> None:
    import zen

    d = zen.ZenEngine().create_decision(ctx["jdm"])
    sample = ctx["required"][0]["action"]
    r = d.evaluate({"action": sample})["result"]
    ctx["decision"] = d
    ctx["shows"].append(f"zen loads the table; evaluate({{action: {sample!r}}}) -> {r}")


def policy(label: str) -> dict[str, Any]:
    src = RESULTS[("facts", label)]
    proof = Proof(
        "P4",
        "facts -> required actions -> decision table -> policy",
        ["facts"],
        [
            Step("required actions", "the obligatory facts with their event lemma and quote", s_required),
            Step("decision table", "jinja2.Environment.from_string(...).render -> GoRules JDM", s_decision_table),
            Step("policy", "zen.ZenEngine.create_decision; zen.ZenDecision.evaluate", s_policy),
        ],
        "policy",
    )
    ctx = dict(src)
    ctx["dir"] = out_dir("P4", label)
    run(proof, label, ctx)
    RESULTS[("policy", label)] = ctx
    return ctx


# ----------------------------------------------------------------------------
# P5 ordered steps -> process model -> process
# ----------------------------------------------------------------------------


def s_bpmn_from_order(ctx: dict[str, Any]) -> None:
    from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter
    from pm4py.objects.bpmn.obj import BPMN

    o = ctx["ordering"]
    lemma = {a.args[0]: a.args[1] for a in ctx["atoms"] if a.predicate == "event"}
    b = BPMN()
    nodes: dict[str, Any] = {}
    start, end = BPMN.StartEvent(name="start"), BPMN.EndEvent(name="end")
    b.add_node(start)
    b.add_node(end)
    inv = {e for e in o.order}
    preds = collections.defaultdict(set)
    succs = collections.defaultdict(set)
    for a, c in o.forced:
        preds[c].add(a)
        succs[a].add(c)
    for e in o.order:
        t = BPMN.Task(name=f"{lemma.get(e, '?')} [{e.split(':')[-1]}]")
        nodes[e] = t
        b.add_node(t)
    for a, c in o.forced:
        b.add_flow(BPMN.Flow(nodes[a], nodes[c]))
    for e in o.order:
        if not preds[e]:
            b.add_flow(BPMN.Flow(start, nodes[e]))
        if not succs[e]:
            b.add_flow(BPMN.Flow(nodes[e], end))
    p = ctx["dir"] / "process.bpmn"
    bpmn_exporter.apply(b, str(p))
    ctx["bpmn"] = b
    ctx["files"] = [p]
    ctx["shows"] = [f"tasks {len(inv)}, flows {len(b.get_flows())}; first flow {lemma.get(o.forced[0][0])} -> {lemma.get(o.forced[0][1])}" if o.forced else "no forced edges"]


def process_from_order(label: str) -> dict[str, Any]:
    src = RESULTS[("ordered steps", label)]
    proof = Proof(
        "P5",
        "ordered steps -> process model -> process",
        ["ordered steps"],
        [Step("process model", "pm4py.objects.bpmn.obj.BPMN (StartEvent, Task, EndEvent, Flow); pm4py.objects.bpmn.exporter.exporter.apply", s_bpmn_from_order)],
        "process",
    )
    ctx = dict(src)
    ctx["dir"] = out_dir("P5", label)
    run(proof, label, ctx)
    RESULTS[("process", label)] = ctx
    return ctx


# ----------------------------------------------------------------------------
# door two: records -> facts
# ----------------------------------------------------------------------------


def s_read_rows_csv(ctx: dict[str, Any]) -> None:
    with open(ctx["path"], encoding="utf-8", newline="") as fh:
        ctx["rows"] = list(csv.DictReader(fh))
    ctx["shows"] = [f"columns {list(ctx['rows'][0].keys())[:6]}...", f"first row {dict(list(ctx['rows'][0].items())[:3])}"]


def s_read_rows_roster(ctx: dict[str, Any]) -> None:
    import lxml.html
    import markdown

    html = markdown.markdown(Path(ctx["path"]).read_text(encoding="utf-8"))
    doc = lxml.html.fromstring(html)
    rows = []
    for h in doc.iter("h4"):
        if h.text_content().strip() == "TSC voting members":
            ul = next(s for s in h.itersiblings() if s.tag == "ul")
            for li in ul.iter("li"):
                t = " ".join(li.text_content().split())
                m = re.match(r"(\S+) - (.+?)(?: <| \(|$)", t)
                if m:
                    rows.append({"handle": m.group(1), "name": m.group(2).strip()})
    ctx["rows"] = rows
    ctx["shows"] = [f"first rows {rows[:2]}"]


def s_type_rows(ctx: dict[str, Any]) -> None:
    import pydantic

    cols = list(ctx["rows"][0].keys())
    M = pydantic.create_model(ctx["model"], **{c: (str, ...) for c in cols})
    ctx["typed"] = [M(**r) for r in ctx["rows"]]
    ctx["shows"].append(f"pydantic model {ctx['model']} with fields {cols[:4]}...")


def s_assert_rows(ctx: dict[str, Any]) -> None:
    import clingo

    facts = []
    for r in ctx["typed"]:
        d = r.model_dump()
        vals = ",".join(lit(d[c]) for c in ctx["cols"])
        facts.append(f'{ctx["pred"]}({vals}).')
    prog = "\n".join(facts) + "\n"
    ctl = clingo.Control(["0"])
    ctl.add("base", [], prog)
    ctl.ground([("base", [])])
    n = 0
    for sym in ctl.symbolic_atoms:
        n += 1
    p = ctx["dir"] / "facts.lp"
    p.write_text(prog, encoding="utf-8")
    ctx["facts_lp"] = prog
    ctx["files"] = [p]
    ctx["shows"].append(f"clingo grounds {n} facts; first {facts[0][:120]}")


def door_two(label: str, path: Path, reader: Callable, model: str, pred: str, cols: list[str]) -> dict[str, Any]:
    proof = Proof(
        "P6",
        "records -> facts",
        ["records"],
        [
            Step("read rows", "csv.DictReader | markdown.markdown + lxml.html.fromstring", reader),
            Step("type", "pydantic.create_model", s_type_rows),
            Step("assert", "clingo.Control.add; rows as ground facts", s_assert_rows),
        ],
        "facts",
    )
    ctx = {"path": path, "dir": out_dir("P6", label), "model": model, "pred": pred, "cols": cols, "label": label}
    run(proof, label, ctx)
    RESULTS[("records", label)] = ctx
    return ctx


# ----------------------------------------------------------------------------
# door four: event log -> log -> process model -> process diagram ; replay
# ----------------------------------------------------------------------------


def s_read_xes(ctx: dict[str, Any]) -> None:
    import pm4py

    log = pm4py.read_xes(str(ctx["path"]))
    ctx["log"] = log
    ctx["shows"] = [
        f"events {len(log)}, cases {log['case:concept:name'].nunique()}, activities {log['concept:name'].nunique()}",
        f"span {log['time:timestamp'].min().date()} to {log['time:timestamp'].max().date()}",
    ]


def s_discover(ctx: dict[str, Any]) -> None:
    import pm4py

    log = ctx["log"]
    cases = sorted(log["case:concept:name"].unique())
    train = log[log["case:concept:name"].isin(cases[: len(cases) // 2])]
    net, im, fm = pm4py.discover_petri_net_inductive(train)
    ctx["net"] = (net, im, fm)
    ctx["train_cases"] = len(cases) // 2
    starts = pm4py.get_start_activities(train)
    ctx["shows"].append(f"discovered from the first half of cases by id; start activities {starts}")


def s_chart(ctx: dict[str, Any]) -> None:
    import pm4py
    from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter
    from pm4py.objects.conversion.wf_net.variants import to_bpmn

    net, im, fm = ctx["net"]
    p1 = ctx["dir"] / "process.pnml"
    pm4py.write_pnml(net, im, fm, str(p1))
    b = to_bpmn.apply(net, im, fm)
    p2 = ctx["dir"] / "process.bpmn"
    bpmn_exporter.apply(b, str(p2))
    ctx["files"] = [p1, p2]
    ctx["shows"].append(f"petri net places {len(net.places)}, transitions {len(net.transitions)}; bpmn nodes {len(b.get_nodes())}")


def door_four(label: str, path: Path) -> dict[str, Any]:
    proof = Proof(
        "P8",
        "event log -> log -> process model -> process diagram",
        ["event log"],
        [
            Step("read", "pm4py.read_xes", s_read_xes),
            Step("discover", "pm4py.discover_petri_net_inductive", s_discover),
            Step("chart", "pm4py.write_pnml; pm4py.objects.conversion.wf_net.variants.to_bpmn.apply; pm4py.objects.bpmn.exporter.exporter.apply", s_chart),
        ],
        "process diagram",
    )
    ctx = {"path": path, "dir": out_dir("P8", label), "label": label}
    run(proof, label, ctx)
    RESULTS[("log", label)] = ctx
    return ctx


def s_replay(ctx: dict[str, Any]) -> None:
    import pm4py

    net, im, fm = ctx["net"]
    log = ctx["log"]
    el = pm4py.convert_to_event_log(log)
    res = pm4py.conformance_diagnostics_token_based_replay(el, net, im, fm)
    rows = [["case", "trace_fitness", "is_fit", "missing_tokens", "remaining_tokens"]]
    fit = 0
    for tr, r in zip(el, res):
        rows.append([tr.attributes["concept:name"], round(r["trace_fitness"], 4), r["trace_is_fit"], r["missing_tokens"], r["remaining_tokens"]])
        fit += bool(r["trace_is_fit"])
    p = workbook(ctx["dir"] / "conformance.xlsx", {"conformance": rows})
    ctx["conformance_rows"] = rows
    ctx["files"] = [p]
    ctx["shows"] = [f"cases fit {fit} of {len(res)}; model from the first {ctx['train_cases']} cases", f"first rows {rows[1:3]}"]


def replay(label: str) -> dict[str, Any]:
    src = RESULTS[("log", label)]
    proof = Proof(
        "P9",
        "process, event log -> conformance -> workbook",
        ["process, event log"],
        [
            Step("replay", "pm4py.convert_to_event_log; pm4py.conformance_diagnostics_token_based_replay", s_replay),
            Step("tabulate", "openpyxl.Workbook.save", lambda c: None),
        ],
        "conformance",
    )
    ctx = dict(src)
    ctx["dir"] = out_dir("P9", label)
    run(proof, label, ctx)
    RESULTS[("conformance", label)] = ctx
    return ctx


# ----------------------------------------------------------------------------
# door three: minutes -> parsed minutes (the same functions as door one)
# ----------------------------------------------------------------------------


def door_three(label: str) -> dict[str, Any]:
    proof = Proof(
        "P7",
        "minutes -> parsed minutes",
        ["minutes"],
        [
            Step("read", "compiled_ai.read.read_text", s_read),
            Step("dependency parse", "compiled_ai.parse.parse_source; ufal.udpipe.Pipeline.process", s_parse),
            Step("predicate extraction", "compiled_ai.fol.compile_atoms; predpatt.PredPatt", s_extract),
            Step("route roles", "compiled_ai.normalize.normalize; clorm.clingo.Control", s_route),
            Step("byte check", "compiled_ai.check.check_atoms", s_check),
            Step("adjudicate", "compiled_ai.adjudicate.apply_rejections", s_adjudicate),
        ],
        "parsed minutes",
    )
    ctx = {"pack": PACKS[label], "dir": out_dir("P7", label), "label": label}
    run(proof, label, ctx)
    RESULTS[("parsed minutes", label)] = ctx
    return ctx


# ----------------------------------------------------------------------------
# joins
# ----------------------------------------------------------------------------


def step_words(ctx: dict[str, Any], events: list[str]) -> dict[str, set[str]]:
    atoms = ctx["atoms"]
    ws: dict[str, set[str]] = {e: set() for e in events}
    for a in atoms:
        if a.predicate == "event" and a.args[0] in ws:
            ws[a.args[0]].add(a.args[1].lower())
        if a.predicate in ("agent", "patient", "theme") and a.args[0] in ws:
            ws[a.args[0]] |= words(a.quote)
    return ws


def s_tag(ctx: dict[str, Any]) -> None:
    import clingo

    steps = ctx["steps"]  # dict event -> words
    minutes = ctx["minutes_ctx"]
    sents = {ps.sentence.id: ps.sentence.text for ps in minutes["parsed"]}
    line_words: dict[str, set[str]] = collections.defaultdict(set)
    for a in minutes["atoms"]:
        if a.predicate == "event":
            line_words[a.sentence_id].add(a.args[1].lower())
        elif a.predicate in ("agent", "patient", "theme"):
            line_words[a.sentence_id] |= words(a.quote)
    prog = []
    for e, ws in steps.items():
        for w in ws:
            prog.append(f'step_word({lit(e)},{lit(w)}).')
    for sid, ws in line_words.items():
        for w in ws:
            prog.append(f'line_word({lit(sid)},{lit(w)}).')
    prog.append("shared(L,E,W) :- line_word(L,W), step_word(E,W).")
    prog.append("score(L,E,N) :- line_word(L,_), step_word(E,_), N = #count{ W : shared(L,E,W) }, N > 0.")
    prog.append("best(L,E) :- score(L,E,N), N = #max{ M : score(L,_,M) }.")
    prog.append("tie(L) :- best(L,E1), best(L,E2), E1 < E2.")
    prog.append("untagged(L) :- line_word(L,_), not score(L,_,_).")
    prog.append("#show best/2. #show shared/3. #show tie/1. #show untagged/1.")
    ctl = clingo.Control(["0"])
    ctl.add("base", [], "\n".join(prog))
    ctl.ground([("base", [])])
    syms: list[Any] = []
    ctl.solve(on_model=lambda m: syms.extend(m.symbols(shown=True)))
    best = collections.defaultdict(list)
    shared = collections.defaultdict(set)
    ties, untagged = set(), set()
    for s in syms:
        if s.name == "best":
            best[s.arguments[0].string].append(s.arguments[1].string)
        elif s.name == "shared":
            shared[(s.arguments[0].string, s.arguments[1].string)].add(s.arguments[2].string)
        elif s.name == "tie":
            ties.add(s.arguments[0].string)
        elif s.name == "untagged":
            untagged.add(s.arguments[0].string)
    lemma = ctx["lemma"]
    rows = [["sentence_id", "sentence", "step", "step_lemma", "shared_words", "tie"]]
    tags = []
    for sid in sorted(best):
        for e in sorted(best[sid]):
            rows.append([sid, sents[sid], e, lemma.get(e, "?"), " ".join(sorted(shared[(sid, e)])), sid in ties])
            tags.append({"sentence_id": sid, "step": e, "shared": sorted(shared[(sid, e)]), "tie": sid in ties})
    unt = [["sentence_id", "sentence"]] + [[sid, sents[sid]] for sid in sorted(untagged)]
    p = workbook(ctx["dir"] / "tagged_steps.xlsx", {"tagged": rows, "untagged": unt})
    write_jsonl(ctx["dir"] / "tags.jsonl", tags)
    ctx["tags"] = tags
    ctx["files"] = [p, ctx["dir"] / "tags.jsonl"]
    strongest = sorted(rows[1:], key=lambda r: (-len(r[4].split()), r[0]))[:4]
    ctx["shows"] = [
        f"tagged sentences {len(best)}, ties {len(ties)}, untagged {len(untagged)}",
        *[f'{r[3]} <- "{r[1][:70]}"  shared: {r[4]}' for r in strongest],
    ]


def tag(label_steps: str, label_minutes: str) -> dict[str, Any]:
    steps_ctx = RESULTS[("ordered steps", label_steps)]
    minutes = RESULTS[("parsed minutes", label_minutes)]
    events = list(steps_ctx["ordering"].order)
    proof = Proof(
        "P10",
        "ordered steps, parsed minutes -> tagged steps -> workbook",
        ["ordered steps, parsed minutes"],
        [
            Step("tag", "clingo: shared words, #max score, ties flagged, untagged listed; stopword list as data", s_tag),
            Step("tabulate", "openpyxl.Workbook.save", lambda c: None),
        ],
        "tagged steps",
    )
    ctx = {
        "dir": out_dir("P10", f"{label_steps}+{label_minutes}"),
        "steps": step_words(steps_ctx, events),
        "minutes_ctx": minutes,
        "lemma": {a.args[0]: a.args[1] for a in steps_ctx["atoms"] if a.predicate == "event"},
        "order": events,
        "forced": list(steps_ctx["ordering"].forced),
    }
    run(proof, f"{label_steps}+{label_minutes}", ctx)
    RESULTS[("tagged steps", label_steps)] = ctx
    return ctx


def s_measure_tags(ctx: dict[str, Any]) -> None:
    import clingo

    prog = [f'tag({lit(t["sentence_id"])},{lit(t["step"])}).' for t in ctx["tags"]]
    prog += [f'step({lit(e)}).' for e in ctx["order"]]
    prog.append("count(E,N) :- step(E), N = #count{ L : tag(L,E) }.")
    prog.append("#show count/2.")
    ctl = clingo.Control(["0"])
    ctl.add("base", [], "\n".join(prog))
    ctl.ground([("base", [])])
    counts: dict[str, int] = {}
    ctl.solve(on_model=lambda m: counts.update({s.arguments[0].string: s.arguments[1].number for s in m.symbols(shown=True)}))
    rows = [["step", "step_lemma", "minutes_sentences"]] + [[e, ctx["lemma"].get(e, "?"), counts.get(e, 0)] for e in ctx["order"]]
    p = workbook(ctx["dir"] / "measured_steps.xlsx", {"measured": rows})
    ctx["counts"] = counts
    ctx["files"] = [p]
    ctx["shows"] = [f"{r[1]}: {r[2]}" for r in sorted(rows[1:], key=lambda r: -r[2])[:4]]


def measure_tags(label_steps: str) -> dict[str, Any]:
    src = RESULTS[("tagged steps", label_steps)]
    proof = Proof(
        "P11",
        "tagged steps -> measured steps -> workbook",
        ["tagged steps"],
        [Step("measure", "clingo #count per step", s_measure_tags), Step("tabulate", "openpyxl.Workbook.save", lambda c: None)],
        "measured steps",
    )
    ctx = dict(src)
    ctx["dir"] = out_dir("P11", label_steps)
    run(proof, label_steps, ctx)
    RESULTS[("measured steps", label_steps)] = ctx
    return ctx


def s_key_measure_log(ctx: dict[str, Any]) -> None:
    import duckdb

    net, _, _ = ctx["net"]
    labels = sorted(t.label for t in net.transitions if t.label)
    rows = ctx["rows"]
    con = duckdb.connect()
    con.execute("create table ev(case_id varchar, activity varchar, ts timestamptz)")
    con.executemany("insert into ev values (?, ?, ?)", [(r["case:concept:name"], r["concept:name"], r["time:timestamp"]) for r in rows])
    con.execute("create table model(activity varchar)")
    con.executemany("insert into model values (?)", [(l,) for l in labels])
    res = con.execute(
        """
        with seq as (
          select case_id, activity, ts,
                 lag(ts) over (partition by case_id order by ts) as prev
          from ev)
        select m.activity, count(e.activity) as events,
               round(avg(epoch(e.ts - e.prev))/3600, 2) as mean_hours_since_previous
        from model m left join seq e on e.activity = m.activity
        group by m.activity order by m.activity
        """
    ).fetchall()
    table = [["activity", "events", "mean_hours_since_previous"]] + [list(r) for r in res]
    p = workbook(ctx["dir"] / "measured_activities.xlsx", {"measured": table})
    ctx["files"] = [p]
    ctx["shows"] = [f"{r[0]}: events {r[1]}, mean hours since previous {r[2]}" for r in res[:4]]


def key_measure_log(label_log: str, label_records: str) -> dict[str, Any]:
    proof = Proof(
        "P12",
        "process, records -> measured steps -> workbook",
        ["process, records"],
        [
            Step("key", "duckdb: join on activity name between the model's transition labels and the rows", s_key_measure_log),
            Step("measure", "duckdb: count, avg(epoch(ts - lag(ts)))", lambda c: None),
            Step("tabulate", "openpyxl.Workbook.save", lambda c: None),
        ],
        "measured steps",
    )
    ctx = {"dir": out_dir("P12", f"{label_log}+{label_records}"), "net": RESULTS[("log", label_log)]["net"], "rows": RESULTS[("records", label_records)]["rows"]}
    run(proof, f"{label_log}+{label_records}", ctx)
    return ctx


MAJORITY_JDM = """{
 "contentType": "application/vnd.gorules.decision",
 "nodes": [
  {"id": "in", "type": "inputNode", "name": "meeting", "position": {"x": 0, "y": 0}},
  {"id": "dt", "type": "decisionTableNode", "name": "simple majority of all TSC voting members", "position": {"x": 0, "y": 0},
   "content": {"hitPolicy": "first",
    "inputs": [{"id": "i1", "name": "present voting members", "field": "present"}],
    "outputs": [{"id": "o1", "name": "majority reachable", "field": "majority_reachable"}, {"id": "o2", "name": "rule", "field": "rule"}],
    "rules": [
     {"_id": "r1", "_description": {{ quote|tojson }}, "i1": ">= {{ majority }}", "o1": "true", "o2": "'r1'"},
     {"_id": "r2", "_description": {{ quote|tojson }}, "i1": "", "o1": "false", "o2": "'r2'"}
    ]}},
  {"id": "out", "type": "outputNode", "name": "decision", "position": {"x": 0, "y": 0}}
 ],
 "edges": [{"id": "e1", "sourceId": "in", "targetId": "dt", "type": "edge"}, {"id": "e2", "sourceId": "dt", "targetId": "out", "type": "edge"}]
}
"""


def s_attendance(ctx: dict[str, Any]) -> None:
    import lxml.html
    import markdown

    rows = []
    for src in ctx["minutes_ctx"]["sources"]:
        html = markdown.markdown(Path(src.path).read_text(encoding="utf-8"))
        doc = lxml.html.fromstring(html)
        for h in doc.iter("h2"):
            if h.text_content().strip() == "Present":
                ul = next(s for s in h.itersiblings() if s.tag == "ul")
                present = [" ".join(li.text_content().split()) for li in ul.iter("li")]
                voting = [p for p in present if "(voting member)" in p]
                rows.append({"meeting": src.id, "present_voting": len(voting), "present": len(present)})
    ctx["attendance"] = rows
    ctx["shows"] = [f'{r["meeting"]}: voting members present {r["present_voting"]}' for r in rows[:3]]


def s_majority_policy(ctx: dict[str, Any]) -> None:
    import jinja2
    import zen

    total = len(ctx["roster"])
    majority = total // 2 + 1
    rule = next(a for a in ctx["charter_atoms"] if a.predicate == "obligatory" and "majority" in a.quote.lower()) if any(
        a.predicate == "obligatory" and "majority" in a.quote.lower() for a in ctx["charter_atoms"]
    ) else None
    sent = {ps.sentence.id: ps.sentence.text for ps in ctx["charter_parsed"]}
    quote = next(t for t in sent.values() if "simple majority of all TSC voting members" in t)
    jdm = jinja2.Environment().from_string(MAJORITY_JDM).render(majority=majority, quote=quote)
    p = ctx["dir"] / "policy.jdm.json"
    p.write_text(jdm, encoding="utf-8")
    ctx["decision"] = zen.ZenEngine().create_decision(jdm)
    ctx["files"] = [p]
    ctx["shows"].append(f'roster: {total} voting members (nodejs/node README, retrieved 2026-09-04); majority = {majority}; rule quoted from the charter: "{quote[:90]}..."')


def s_evaluate(ctx: dict[str, Any]) -> None:
    rows = [["meeting", "present_voting", "majority_reachable"]]
    for r in ctx["attendance"]:
        res = ctx["decision"].evaluate({"present": r["present_voting"]})["result"]
        rows.append([r["meeting"], r["present_voting"], res["majority_reachable"]])
    p = workbook(ctx["dir"] / "decisions.xlsx", {"decisions": rows})
    ctx["files"].append(p)
    ctx["shows"] += [f"{r[0]}: present {r[1]} -> majority reachable {r[2]}" for r in rows[1:]]


def evaluate_majority() -> dict[str, Any]:
    proof = Proof(
        "P13",
        "policy, records -> decisions -> workbook",
        ["policy (charter: simple majority of all TSC voting members), records (roster; attendance from the minutes)"],
        [
            Step("attendance rows", "markdown.markdown; lxml.html.fromstring; the Present list of each minutes file", s_attendance),
            Step("policy", "jinja2 render of the rule with the roster count -> GoRules JDM; zen.ZenEngine.create_decision", s_majority_policy),
            Step("evaluate", "zen.ZenDecision.evaluate per meeting", s_evaluate),
            Step("tabulate", "openpyxl.Workbook.save", lambda c: None),
        ],
        "decisions",
    )
    ctx = {
        "dir": out_dir("P13", "charter+roster+minutes"),
        "minutes_ctx": RESULTS[("parsed minutes", "nodejs-tsc-minutes")],
        "roster": RESULTS[("records", "tsc-voting-members")]["rows"],
        "charter_atoms": RESULTS[("facts", "nodejs-tsc-charter")]["atoms"],
        "charter_parsed": RESULTS[("facts", "nodejs-tsc-charter")]["parsed"],
    }
    run(proof, "charter+roster+minutes", ctx)
    return ctx


# ----------------------------------------------------------------------------
# renders
# ----------------------------------------------------------------------------


def draw_deck(path: Path, order: list[str], forced: list[tuple[str, str]], label_of: Callable[[str], str], title: str) -> dict[str, Any]:
    import networkx as nx
    from pptx import Presentation
    from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
    from pptx.util import Inches, Pt

    G = nx.DiGraph()
    G.add_nodes_from(order)
    G.add_edges_from(forced)
    layers = list(nx.topological_generations(G))
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(16), Inches(9)
    s = prs.slides.add_slide(prs.slide_layouts[6])
    tb = s.shapes.add_textbox(Inches(0.3), Inches(0.1), Inches(15), Inches(0.5))
    tb.text_frame.text = title
    pos: dict[str, Any] = {}
    for li, layer in enumerate(layers):
        for ni, n in enumerate(sorted(layer)):
            sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3 + li * 2.4), Inches(0.8 + ni * 0.62), Inches(2.1), Inches(0.5))
            sh.text_frame.text = label_of(n)
            for para in sh.text_frame.paragraphs:
                for r in para.runs:
                    r.font.size = Pt(8)
            pos[n] = sh
    for a, b in forced:
        c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, 0, 0, 0, 0)
        c.begin_connect(pos[a], 3)
        c.end_connect(pos[b], 1)
    prs.save(path)
    return {"layers": len(layers), "boxes": len(pos), "connectors": len(forced)}


def s_deck(ctx: dict[str, Any]) -> None:
    o = ctx["ordering"]
    lemma = {a.args[0]: a.args[1] for a in ctx["atoms"] if a.predicate == "event"}
    p = ctx["dir"] / "dependencies.pptx"
    info = draw_deck(p, list(o.order), list(o.forced), lambda e: f"{lemma.get(e, '?')}\n{e.split(':')[-1]}", f"{ctx['label']}: forced order")
    ctx["files"] = [p]
    ctx["shows"] = [f"layers {info['layers']}, boxes {info['boxes']}, connectors {info['connectors']}"]


def deck(label: str) -> dict[str, Any]:
    src = RESULTS[("ordered steps", label)]
    proof = Proof(
        "P14",
        "ordered steps -> deck",
        ["ordered steps"],
        [
            Step("layers", "networkx.topological_generations", lambda c: None),
            Step("draw", "pptx.Presentation; Shapes.add_shape, Shapes.add_connector, Connector.begin_connect, Connector.end_connect; Presentation.save", s_deck),
        ],
        "deck",
    )
    ctx = dict(src)
    ctx["dir"] = out_dir("P14", label)
    run(proof, label, ctx)
    RESULTS[("deck", label)] = ctx
    return ctx


def s_document(ctx: dict[str, Any]) -> None:
    import docx

    o = ctx["ordering"]
    atoms = ctx["atoms"]
    lemma = {a.args[0]: a.args[1] for a in atoms if a.predicate == "event"}
    quote = {a.args[0]: a.quote for a in atoms if a.predicate == "event"}
    sent = {ps.sentence.id: ps.sentence.text for ps in ctx["parsed"]}
    d = docx.Document()
    d.add_heading(f"{ctx['label']}: ordered steps", 1)
    for i, e in enumerate(o.order, 1):
        d.add_paragraph(f"{i}. {lemma.get(e, '?')}  [{e}]")
        d.add_paragraph(sent.get(e.split('#')[0], ""), style="Intense Quote")
    d.add_heading("forced precedence", 2)
    t = d.add_table(rows=1, cols=2)
    t.rows[0].cells[0].text, t.rows[0].cells[1].text = "before", "after"
    for a, b in o.forced:
        r = t.add_row().cells
        r[0].text, r[1].text = lemma.get(a, "?"), lemma.get(b, "?")
    p = ctx["dir"] / "ordered_steps.docx"
    d.save(p)
    ctx["files"] = [p]
    ctx["shows"] = [f"paragraphs {len(d.paragraphs)}, table rows {len(t.rows)}"]


def document(label: str) -> dict[str, Any]:
    src = RESULTS[("ordered steps", label)]
    proof = Proof("P15", "ordered steps -> document", ["ordered steps"], [Step("write", "docx.Document; Document.add_heading, add_paragraph, add_table; docx.document.Document.save", s_document)], "document")
    ctx = dict(src)
    ctx["dir"] = out_dir("P15", label)
    run(proof, label, ctx)
    return ctx


def s_tabulate_facts(ctx: dict[str, Any]) -> None:
    rows = [["id", "predicate", "args", "sentence_id", "quote"]] + [[a.id, a.predicate, " ".join(a.args), a.sentence_id, a.quote] for a in ctx["atoms"]]
    p = workbook(ctx["dir"] / "facts.xlsx", {"facts": rows})
    ctx["files"] = [p]
    ctx["shows"] = [f"rows {len(rows) - 1}; first {rows[1][1]} {rows[1][2]} \"{rows[1][4]}\""]


def tabulate(label: str) -> dict[str, Any]:
    src = RESULTS[("facts", label)]
    proof = Proof("P16", "facts -> workbook", ["facts"], [Step("tabulate", "openpyxl.Workbook; Worksheet.append; Workbook.save", s_tabulate_facts)], "workbook")
    ctx = dict(src)
    ctx["dir"] = out_dir("P16", label)
    run(proof, label, ctx)
    return ctx


def s_seal_all(ctx: dict[str, Any]) -> None:
    entries = []
    for pr in PROOFS:
        for label, files, _ in pr.evidence:
            for p, h in files:
                entries.append({"proof": pr.pid, "input": label, "file": str(p.relative_to(ROOT)), "sha256": h})
    entries.sort(key=lambda e: e["file"])
    digest = sha256_json(entries)
    p = write_json(ctx["dir"] / "digests.json", {"entries": entries, "digest": digest})
    ctx["files"] = [p]
    ctx["shows"] = [f"deliverables {len(entries)}; digest {digest}"]


def seal_all() -> dict[str, Any]:
    proof = Proof("P17", "anything -> digest", ["every deliverable above"], [Step("seal", "json.dumps sort_keys; hashlib.sha256", s_seal_all)], "digest")
    ctx = {"dir": out_dir("P17", "all")}
    run(proof, "all", ctx)
    return ctx


# ----------------------------------------------------------------------------
# composition, reverse, minutes as a log
# ----------------------------------------------------------------------------


def s_select_meeting(ctx: dict[str, Any]) -> None:
    import clingo

    meeting = ctx["meeting"]
    prog = [f'tag({lit(t["sentence_id"])},{lit(t["step"])}).' for t in ctx["tags"]]
    prog += [f'step({lit(e)}).' for e in ctx["order"]]
    prog += [f'forced({lit(a)},{lit(b)}).' for a, b in ctx["forced"]]
    prog.append(f'meeting_line(L) :- tag(L,_), @startswith(L, "{meeting}") = 1.')
    prog.append("selected(E) :- tag(L,E), meeting_line(L).")
    prog.append("count(E,N) :- selected(E), N = #count{ L : tag(L,E), meeting_line(L) }.")
    prog.append("edge(A,B) :- forced(A,B), selected(A), selected(B).")
    prog.append("#show selected/1. #show count/2. #show edge/2.")

    class Ctx:
        def startswith(self, s: Any, p: Any) -> Any:
            return clingo.Number(1 if s.string.startswith(p.string) else 0)

    ctl = clingo.Control(["0"])
    ctl.add("base", [], "\n".join(prog))
    ctl.ground([("base", [])], context=Ctx())
    sel, cnt, edges = [], {}, []
    for_model: list[Any] = []
    ctl.solve(on_model=lambda m: for_model.extend(m.symbols(shown=True)))
    for s in for_model:
        if s.name == "selected":
            sel.append(s.arguments[0].string)
        elif s.name == "count":
            cnt[s.arguments[0].string] = s.arguments[1].number
        elif s.name == "edge":
            edges.append((s.arguments[0].string, s.arguments[1].string))
    ctx["selected"] = sorted(sel, key=ctx["order"].index)
    ctx["counts"] = cnt
    ctx["edges"] = sorted(edges)
    ctx["shows"] = [f"meeting {meeting}: steps discussed {len(sel)}, forced edges among them {len(edges)}"]


def s_compose_deck(ctx: dict[str, Any]) -> None:
    lemma = ctx["lemma"]
    p = ctx["dir"] / "deck.pptx"
    rows = [[e, lemma.get(e, "?"), ctx["counts"].get(e, 0)] for e in ctx["selected"]]
    info = draw_deck(p, ctx["selected"], ctx["edges"], lambda e: f"{lemma.get(e, '?')}  ({ctx['counts'].get(e, 0)} lines)\n{e.split(':')[-1]}", f"steps discussed at {ctx['meeting']}, with minutes lines per step")
    ctx["rows"] = rows
    ctx["files"] = [p]
    ctx["shows"].append(f"deck layers {info['layers']}, boxes {info['boxes']}, connectors {info['connectors']}")


def s_compose_seal(ctx: dict[str, Any]) -> None:
    d = sha256_json(ctx["rows"])
    p = write_json(ctx["dir"] / "digest.json", {"rows": ctx["rows"], "digest": d})
    ctx["digest"] = d
    ctx["files"].append(p)
    ctx["shows"].append(f"digest over the rows {d}")


def compose(label_steps: str, meeting: str) -> dict[str, Any]:
    src = RESULTS[("tagged steps", label_steps)]
    proof = Proof(
        "P18",
        "ordered steps, parsed minutes -> tagged steps -> measured steps -> selected steps -> deck -> digest",
        ["tagged steps (P10), forced order (P2)"],
        [
            Step("select", "clingo: steps tagged by lines of one meeting; forced edges among them; #count lines per step", s_select_meeting),
            Step("layers", "networkx.topological_generations", lambda c: None),
            Step("draw", "pptx.Presentation; add_shape, add_connector; Presentation.save", s_compose_deck),
            Step("seal", "json.dumps sort_keys; hashlib.sha256", s_compose_seal),
        ],
        "deck, digest",
    )
    ctx = dict(src)
    ctx["dir"] = out_dir("P18", f"{label_steps}+{meeting}")
    ctx["meeting"] = meeting
    run(proof, f"{label_steps}+{meeting}", ctx)
    RESULTS[("composed deck", label_steps)] = ctx
    return ctx


def s_read_shapes(ctx: dict[str, Any]) -> None:
    from pptx import Presentation

    prs = Presentation(ctx["deck_path"])
    rows = []
    for sh in prs.slides[0].shapes:
        if sh.__class__.__name__ == "Shape" and sh.has_text_frame and "(" in sh.text_frame.text:
            first, ident = sh.text_frame.text.split("\n")
            lemma, n = re.match(r"(.+?)  \((\d+) lines\)", first).groups()
            rows.append([ident, lemma, int(n)])
    ctx["rows_back"] = sorted(rows, key=lambda r: r[0])
    ctx["shows"] = [f"boxes read back {len(rows)}"]


def s_reverse_seal(ctx: dict[str, Any]) -> None:
    fwd = sorted([[e.split(":")[-1], l, n] for e, l, n in ctx["rows"]], key=lambda r: r[0])
    d = sha256_json(ctx["rows_back"])
    ctx["digest_back"] = d
    ctx["fwd_rows"] = fwd
    ctx["shows"].append(f"digest' {d}")


def s_compare(ctx: dict[str, Any]) -> None:
    from csv_diff import compare

    fwd = {r[0]: {"lemma": r[1], "lines": str(r[2])} for r in ctx["fwd_rows"]}
    back = {r[0]: {"lemma": r[1], "lines": str(r[2])} for r in ctx["rows_back"]}
    diff = compare(fwd, back)
    same = not (diff["added"] or diff["removed"] or diff["changed"])
    p = write_json(ctx["dir"] / "compare.json", {"digest_forward": sha256_json(fwd and ctx["fwd_rows"]), "digest_back": ctx["digest_back"], "diff": diff, "match": same})
    ctx["files"] = [p]
    ctx["shows"].append(f"rows match: {same}; changed {len(diff['changed'])}, added {len(diff['added'])}, removed {len(diff['removed'])}")


def reverse(label_steps: str) -> dict[str, Any]:
    src = RESULTS[("composed deck", label_steps)]
    proof = Proof(
        "P19",
        "deck -> rows -> digest' ; digest', digest -> match",
        ["deck (P18)"],
        [
            Step("read shapes", "pptx.Presentation; slide.shapes, Shape.text_frame", s_read_shapes),
            Step("seal", "json.dumps sort_keys; hashlib.sha256", s_reverse_seal),
            Step("compare", "csv_diff.compare", s_compare),
        ],
        "match, or the differing cell",
    )
    ctx = dict(src)
    ctx["dir"] = out_dir("P19", label_steps)
    ctx["deck_path"] = src["files"][0]
    ctx["files"] = []
    run(proof, label_steps, ctx)
    return ctx


def s_minutes_log(ctx: dict[str, Any]) -> None:
    import clingo

    prog = [f'tag({lit(t["sentence_id"])},{lit(t["step"])}).' for t in ctx["tags"] if not t["tie"]]
    prog += [f'forced({lit(a)},{lit(b)}).' for a, b in ctx["forced"]]
    prog.append("meeting(L,M) :- tag(L,_), M = @meeting(L).")
    prog.append("occurs(M,E,L) :- tag(L,E), meeting(L,M).")
    prog.append("first(M,E,L) :- occurs(M,E,L), L = #min{ L2 : occurs(M,E,L2) }.")
    prog.append("violated(M,A,B,LA,LB) :- forced(A,B), first(M,A,LA), first(M,B,LB), LB < LA.")
    prog.append("respected(M,A,B) :- forced(A,B), first(M,A,LA), first(M,B,LB), LA < LB.")
    prog.append("#show violated/5. #show respected/3.")

    class Ctx:
        def meeting(self, l: Any) -> Any:
            return clingo.String(l.string.split(":")[0])

    ctl = clingo.Control(["0"])
    ctl.add("base", [], "\n".join(prog))
    ctl.ground([("base", [])], context=Ctx())
    syms: list[Any] = []
    ctl.solve(on_model=lambda m: syms.extend(m.symbols(shown=True)))
    lemma = ctx["lemma"]
    v = [["meeting", "before", "after", "line_of_before", "line_of_after"]]
    r = [["meeting", "before", "after"]]
    for s in syms:
        a = [x.string for x in s.arguments]
        if s.name == "violated":
            v.append([a[0], lemma.get(a[1], "?"), lemma.get(a[2], "?"), a[3], a[4]])
        else:
            r.append([a[0], lemma.get(a[1], "?"), lemma.get(a[2], "?")])
    p = workbook(ctx["dir"] / "conformance.xlsx", {"violated": v, "respected": r})
    ctx["files"] = [p]
    ctx["shows"] = [f"forced edges respected in the minutes {len(r) - 1}, violated {len(v) - 1}", *[f"{x[0]}: {x[1]} before {x[2]}" for x in r[1:3]], *[f"VIOLATED {x[0]}: {x[2]} discussed before {x[1]}" for x in v[1:3]]]


def minutes_as_log(label_steps: str) -> dict[str, Any]:
    src = RESULTS[("tagged steps", label_steps)]
    proof = Proof(
        "P20",
        "tagged steps -> event log ; process, event log -> conformance -> workbook",
        ["tagged steps (P10), forced order (P2)"],
        [
            Step("event log", "clingo: case = meeting, activity = tagged step (ties dropped), time = first sentence that mentions it", s_minutes_log),
            Step("replay", "clingo: violated(M,A,B) :- forced(A,B), first mention of B before first mention of A", lambda c: None),
            Step("tabulate", "openpyxl.Workbook.save", lambda c: None),
        ],
        "conformance",
    )
    ctx = dict(src)
    ctx["dir"] = out_dir("P20", label_steps)
    run(proof, label_steps, ctx)
    return ctx


# ----------------------------------------------------------------------------
# PROOFS.md
# ----------------------------------------------------------------------------

DOORS = [
    ("procedures", "packs/foia/sources/usdoj-foia.gov-foia-statute.html (5 U.S.C. 552, DOJ); packs/nodejs-tsc-charter/sources/tsc-TSC-Charter.md; packs/nodejs-governance/sources/GOVERNANCE.md"),
    ("records", "proofs/in/receipt.csv (WABO receipt phase, 8577 rows); proofs/in/node-README.md (TSC voting members)"),
    ("minutes", "packs/nodejs-tsc-minutes/sources/tsc-*.md (eight Node.js TSC meetings)"),
    ("event log", "proofs/in/receipt.xes (WABO receipt phase, 1434 cases)"),
]

PINS = "ufal.udpipe 1.4.0.1 · predpatt 1.0.1 · clingo 5.8.2 · clorm 1.6.3 · z3-solver 5.1.0.0 · networkx 3.6.1 · timexy 0.1.3 · spacy 3.8.16 · zen-engine 2.0.2 · Jinja2 3.1.6 · pm4py 2.7.23.8 · pydantic 2.13.5 · duckdb 1.5.5 · markdown 3.6 · lxml 6.1.3 · python-pptx 1.0.2 · python-docx 1.2.0 · openpyxl 3.1.2 · csv-diff 1.2 · PyYAML 6.0.3"


def write_md() -> None:
    lines = ["# Proofs", "", "```", "thing", "-> change (functions)", "-> thing", "a line naming two things is a join", "every function ran on the named input; every deliverable carries its sha256", "```", "", "## Doors", "", "```"]
    for name, where in DOORS:
        lines.append(f"{name:12s} {where}")
    lines += ["```", ""]
    for pr in sorted(PROOFS, key=lambda p: int(re.sub(r"\D", "", p.pid) or 0)):
        lines += [f"## {pr.pid}  {pr.title}", "", "```"]
        for inp in pr.inputs:
            lines.append(inp)
        for s in pr.steps:
            lines.append(f"-> {s.change} ({s.fns})")
        lines.append(f"-> {pr.result}")
        lines += ["```", ""]
        for label, files, shows in pr.evidence:
            lines.append(f"**{label}**")
            lines.append("")
            lines.append("```")
            for p, h in files:
                lines.append(f"{str(p.relative_to(ROOT)):58s} sha256 {h}")
            for sh in shows:
                lines.append(f"shows: {sh}")
            lines += ["```", ""]
    lines += ["## Pins", "", "```", PINS, "```", ""]
    MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    for label in ["usc5-552-doj", "nodejs-tsc-charter", "nodejs-governance"]:
        door_one(label)
    for label in ["usc5-552-doj", "nodejs-tsc-charter", "nodejs-governance"]:
        door_one_order(label)
    anchor_dates("usc5-552-doj")
    anchor_dates("nodejs-tsc-charter")
    policy("usc5-552-doj")
    policy("nodejs-tsc-charter")
    process_from_order("usc5-552-doj")
    process_from_order("nodejs-governance")
    door_two("receipt-csv", ROOT / "proofs" / "in" / "receipt.csv", s_read_rows_csv, "receipt_event", "event_row", ["case:concept:name", "concept:name", "time:timestamp", "org:resource", "case:department", "case:channel"])
    door_two("tsc-voting-members", ROOT / "proofs" / "in" / "node-README.md", s_read_rows_roster, "voting_member", "voting_member", ["handle", "name"])
    door_three("nodejs-tsc-minutes")
    door_four("receipt-xes", ROOT / "proofs" / "in" / "receipt.xes")
    replay("receipt-xes")
    tag("nodejs-governance", "nodejs-tsc-minutes")
    measure_tags("nodejs-governance")
    key_measure_log("receipt-xes", "receipt-csv")
    evaluate_majority()
    deck("usc5-552-doj")
    deck("nodejs-governance")
    document("usc5-552-doj")
    tabulate("usc5-552-doj")
    compose("nodejs-governance", "tsc-2024-01-17")
    reverse("nodejs-governance")
    minutes_as_log("nodejs-governance")
    seal_all()
    write_md()
    print(f"proofs {len(PROOFS)}; wrote {MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
