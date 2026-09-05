/** Offline DOM checks. jsdom does not perform browser layout or paint. */
import assert from "node:assert/strict";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import jsdom from "jsdom";
const { JSDOM, VirtualConsole } = jsdom;

const root = new URL("../", import.meta.url);
const output = new URL("proofs/out/augmentation/", root);
const snapshots = new URL("proofs/cache/visual/", root);
mkdirSync(snapshots, { recursive: true });
const sha = x => createHash("sha256").update(x).digest("hex");
let checks = 0;
const eq = (a, b) => { assert.deepEqual(a, b); checks++; };
const ok = a => { assert.ok(a); checks++; };
const sourceText = v => v === null ? "—" : typeof v === "boolean" ? (v ? "True" : "False") : String(v);
const files = ["policy", "process", "records", "briefing", "slides", "workbench"];
const report = { engine: "jsdom", version: "30.0.1", scope: "offline DOM and event behavior; no browser layout or paint", files: {}, snapshots: {}, scenarios: {}, assertions: 0, network_attempts: 0, errors: [], browser: { status: "blocked", reason: "Supported preview service unavailable; browser policy rejects local files. No browser visual or responsive test is claimed." } };
function load(name) {
  const html = readFileSync(new URL(name + ".html", output), "utf8");
  const errors = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on("jsdomError", e => errors.push(e.message));
  const dom = new JSDOM(html, { runScripts: "dangerously", virtualConsole, beforeParse(w) {
    const block = () => { report.network_attempts++; throw new Error("External execution forbidden"); };
    w.fetch = block; w.XMLHttpRequest = block; w.WebSocket = block; w.EventSource = block;
    // Layout-dependent methods are unavailable in jsdom. Do not report them as tested.
    w.HTMLElement.prototype.scrollIntoView = () => {};
    w.HTMLElement.prototype.scrollTo = () => {};
    w.print = () => {};
  } });
  eq(errors, []);
  eq(dom.window.document.querySelectorAll('script[src],link[href],iframe,img[src]').length, 0);
  report.files[name + ".html"] = { sha256: sha(html), initial_script_errors: errors.length };
  return { dom, w: dom.window, d: dom.window.document, model: JSON.parse(dom.window.document.getElementById("model").textContent), errors };
}
function snapshot(d, name) {
  const copy = d.cloneNode(true);
  copy.querySelectorAll("script,noscript").forEach(n => n.remove());
  copy.querySelectorAll("input").forEach(n => { const original = d.getElementById(n.id); n.setAttribute("value", original.value); });
  copy.querySelectorAll("select").forEach(n => {
    const original = d.getElementById(n.id);
    n.querySelectorAll("option").forEach(o => { o.removeAttribute("selected"); if (o.value === original.value) o.setAttribute("selected", ""); });
  });
  const html = "<!doctype html>\n" + copy.documentElement.outerHTML;
  writeFileSync(new URL(name + ".html", snapshots), html);
  report.snapshots[name + ".html"] = sha(html);
}
for (const name of files) {
  const { dom, d, errors } = load(name);
  const active = Array.from(d.querySelectorAll('[role="tabpanel"]')).filter(n => !n.hidden);
  eq(active.length, 1);
  ok(d.querySelector('[role="tab"][aria-selected="true"]'));
  eq(d.documentElement.lang, "en-US");
  eq(errors, []);
  dom.window.close();
}

const { dom, w, d, model, errors } = load("workbench");
const el = id => d.getElementById(id);
const set = (id, value, event = "change") => { el(id).value = String(value); el(id).dispatchEvent(new w.Event(event, { bubbles: true })); };
const tab = name => el("tab-" + name).click();
const key = (node, key) => node.dispatchEvent(new w.KeyboardEvent("keydown", { key, bubbles: true }));
for (const [count, reachable, rule] of model.policy.truth) {
  set("present", count, "input");
  eq(el("result-title").textContent, reachable ? "Reachable" : "Not reachable");
  eq(el("result-rule").textContent, rule);
  eq(el("present").getAttribute("aria-invalid"), "false");
  eq(d.querySelector('[data-count][aria-pressed="true"]').dataset.count, String(count));
  d.querySelector(`[data-count="${count}"]`).click();
  eq(el("result-present").textContent, String(count));
}
report.scenarios.policy_counts = model.policy.truth.length;
for (const value of ["", "-1", "19", "1.5", "1e1", "abc"]) {
  set("present", value, "input");
  eq(el("present").getAttribute("aria-invalid"), "true");
  eq(el("result-title").textContent, "Check the input");
  eq(el("result-rule").textContent, "—");
  eq(d.querySelectorAll('[data-count][aria-pressed="true"]').length, 0);
}
report.scenarios.invalid_inputs = 6;
model.policy.meetings.forEach((row, index) => { set("meeting", index); eq(el("result-present").textContent, String(row[1])); eq(el("result-title").textContent, row[2] ? "Reachable" : "Not reachable"); });
report.scenarios.meetings = model.policy.meetings.length;
set("present", model.policy.threshold, "input"); snapshot(d, "policy");
key(el("tab-policy"), "End"); eq(d.activeElement.id, "tab-slides");
key(el("tab-slides"), "Home"); eq(d.activeElement.id, "tab-policy");
key(el("tab-policy"), "ArrowRight"); eq(d.activeElement.id, "tab-process");
key(el("tab-process"), "ArrowLeft"); eq(d.activeElement.id, "tab-policy");
report.scenarios.keyboard_tab_actions = 4;

tab("process");
model.processes.forEach((graph, index) => {
  set("process-choice", index);
  eq(Array.from(el("process-canvas").querySelectorAll("[data-node-id]")).map(n => n.dataset.nodeId), graph.nodes.map(n => n.id));
  eq(Array.from(el("process-canvas").querySelectorAll("[data-source]")).map(n => [n.dataset.source, n.dataset.target]), graph.edges);
  graph.nodes.forEach((node, i) => {
    set("step-choice", node.id);
    eq(el("node-quote").textContent, node.quote);
    eq(el("node-label").textContent, node.label);
    eq(el("node-sentence").textContent, node.sentence);
    const target = el("process-canvas").querySelectorAll("[data-node-id]")[i];
    key(target, "Enter"); eq(target.getAttribute("aria-pressed"), "true");
    key(target, " "); eq(el("node-id").textContent, node.id);
  });
  set("step-choice", graph.nodes[0].id); snapshot(d, "process-" + index);
});
report.scenarios.graph_nodes = model.processes.reduce((n, g) => n + g.nodes.length, 0);
report.scenarios.graph_edges = model.processes.reduce((n, g) => n + g.edges.length, 0);

tab("records");
const shown = () => Array.from(el("records-table").querySelectorAll("tbody tr[data-source-row]"));
model.records.forEach((data, index) => {
  set("record-choice", index); set("record-page-size", 10);
  const originalOrder = [];
  do {
    shown().forEach(tr => { const i = Number(tr.dataset.sourceRow); originalOrder.push(i); eq(Array.from(tr.cells).map(c => c.textContent), data.rows[i].map(sourceText)); });
    if (el("record-next").disabled) break;
    el("record-next").click();
  } while (true);
  eq(originalOrder, data.rows.map((_, i) => i));
  el("records-table").querySelector("thead button").click();
  const expected = data.rows.map((row, index) => ({ row, index })).sort((a, b) => String(a.row[0]).localeCompare(String(b.row[0]), "en-US", { numeric: true }) || a.index - b.index);
  eq(shown().map(n => Number(n.dataset.sourceRow)), expected.slice(0, 10).map(r => r.index));
  el("records-table").querySelector("thead button").click();
  eq(el("records-table").querySelector("th").getAttribute("aria-sort"), "descending");
  set("record-search", "zz_no_such_record_zz", "input"); eq(shown().length, 0); ok(el("record-next").disabled); ok(el("record-prev").disabled);
  const query = sourceText(data.rows[0][0]); set("record-search", query, "input");
  const matches = data.rows.filter(r => r.some(v => sourceText(v).toLocaleLowerCase("en-US").includes(query.toLocaleLowerCase("en-US"))));
  ok(el("record-count").textContent.includes(`of ${matches.length} matching`));
  set("record-choice", index); set("record-page-size", 10); snapshot(d, "records-" + index);
});
report.scenarios.record_rows = model.records.reduce((n, r) => n + r.rows.length, 0);
report.scenarios.record_datasets = model.records.length;

tab("briefing");
model.documents.forEach((doc, index) => {
  set("document-choice", index);
  eq(el("document-body").children.length, doc.blocks.length);
  doc.blocks.forEach((block, i) => {
    const node = el("document-body").children[i];
    if (block.kind === "table") eq(Array.from(node.querySelectorAll("tr")).map(tr => Array.from(tr.cells).map(c => c.textContent)), block.rows);
    else eq(node.textContent, block.text);
  });
  snapshot(d, "briefing-" + index);
});
report.scenarios.document_blocks = model.documents.reduce((n, doc) => n + doc.blocks.length, 0);
tab("slides");
model.deck.slides.forEach((slide, index) => {
  set("slide-choice", index);
  eq(Array.from(el("slide-canvas").querySelectorAll("[data-source]")).map(n => [n.dataset.source, n.dataset.target]), slide.edges);
  eq(Array.from(el("slide-transcript").children).map(n => n.textContent), [...slide.headings, ...slide.nodes.map(n => n.text)]);
  snapshot(d, "slides-" + index);
});
report.scenarios.slides = model.deck.slides.length;
el("show-evidence").click(); eq(el("evidence").hidden, false); eq(d.activeElement.id, "hide-evidence");
el("hide-evidence").click(); eq(el("evidence").hidden, true); eq(d.activeElement.id, "show-evidence");
for (const name of ["policy", "process", "records", "briefing", "slides"]) { tab(name); eq(Array.from(d.querySelectorAll('[role="tabpanel"]')).filter(n => !n.hidden).map(n => n.id), ["view-" + name]); }
eq(errors, []); eq(report.network_attempts, 0);
report.assertions = checks;
report.implementation_sha256 = sha(readFileSync(new URL("tests/test_augmentation_ui.mjs", root)));
writeFileSync(new URL("dom-verification.json", output), JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify({ assertions: checks, scenarios: report.scenarios, network_attempts: report.network_attempts, browser: report.browser.status }));
dom.window.close();
