/** Offline DOM behavior. Browser layout, download dialogs, and Plotly paint are unverified. */
import jsdom from "jsdom";
import assert from "node:assert/strict";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
const { JSDOM, VirtualConsole } = jsdom;
const root = new URL("../", import.meta.url), out = new URL("proofs/out/augmentation/", root), snapshots = new URL("proofs/cache/operations-visual/", root);
mkdirSync(snapshots, { recursive: true });
const hash = x => createHash("sha256").update(x).digest("hex");
const html = readFileSync(new URL("operations.html", out), "utf8");
const report = { assertions: 0, errors: [], network_attempts: 0, snapshots: {}, scenarios: {}, file_sha256: hash(html), browser: "unverified", scope: "offline DOM and event behavior; file dialogs, browser layout, and Plotly rendering unverified" };
const eq = (x, y) => { assert.deepEqual(x, y); report.assertions++; };
const ok = x => { assert.ok(x); report.assertions++; };
const virtualConsole = new VirtualConsole(); virtualConsole.on("jsdomError", e => report.errors.push(e.message));
const dom = new JSDOM(html, { runScripts: "dangerously", virtualConsole, beforeParse(w) {
  const block = () => { report.network_attempts++; throw new Error("Network use forbidden"); };
  w.fetch = block; w.XMLHttpRequest = block; w.WebSocket = block; w.EventSource = block;
  w.HTMLElement.prototype.scrollIntoView = () => {}; w.print = () => {};
} });
const w = dom.window, d = w.document, el = id => d.getElementById(id), model = JSON.parse(el("operations-model").textContent);
const set = (id, value, event = "change") => { el(id).value = String(value); el(id).dispatchEvent(new w.Event(event, { bubbles: true })); };
const tab = name => el("ops-tab-" + name).click();
const exported = () => JSON.parse(w.FunctionChainOperations.exportText());
function snapshot(name) {
  const copy = d.cloneNode(true); copy.querySelectorAll("script,noscript").forEach(n => n.remove());
  copy.querySelectorAll("input").forEach(n => n.setAttribute("value", el(n.id).value));
  copy.querySelectorAll("select").forEach(n => n.querySelectorAll("option").forEach(o => { o.removeAttribute("selected"); if (o.value === el(n.id).value) o.setAttribute("selected", ""); }));
  const text = "<!doctype html>\n" + copy.documentElement.outerHTML;
  writeFileSync(new URL(name + ".html", snapshots), text); report.snapshots[name + ".html"] = hash(text);
}
eq(report.errors, []); eq(d.documentElement.lang, "en-US"); eq(d.querySelectorAll("script[src],link[href],iframe").length, 0);
for (const key of ["outcomes", "gaps", "heatmap"]) { set("chart-choice", key); eq(Array.from(d.querySelectorAll("[data-chart]")).filter(n => !n.hidden).map(n => n.dataset.chart), [key]); snapshot("overview-" + key); }
const keys = ["End", "Home", "ArrowRight", "ArrowLeft"], expectedTabs = ["flows", "overview", "cases", "overview"];
let active = el("ops-tab-overview");
keys.forEach((key, i) => { active.dispatchEvent(new w.KeyboardEvent("keydown", { key, bubbles: true })); eq(d.activeElement.id, "ops-tab-" + expectedTabs[i]); active = d.activeElement; });
report.scenarios.keyboard_tab_actions = 4;
tab("cases"); set("case-size", 50);
const seen = [];
do {
  const rows = Array.from(el("case-table").querySelectorAll("tbody tr[data-case]"));
  for (const tr of rows) {
    const id = tr.dataset.case, source = model.cases.find(r => r.case === id); seen.push(id); tr.querySelector("button").click();
    eq(JSON.parse(el("detail-json").textContent), source);
    eq(el("detail-id").textContent, id);
    eq(el("detail-risk").textContent, source.risk === null ? "Not assessed" : source.risk.at_risk ? "Flagged" : "Unflagged");
  }
  if (el("case-next").disabled) break; el("case-next").click();
} while (true);
eq(new Set(seen).size, model.cases.length); eq(seen.length, model.cases.length); report.scenarios.cases_inspected = seen.length;
el("reset-cases").click();
const departments = ["", ...new Set(model.cases.map(r => r.department))], channels = ["", ...new Set(model.cases.map(r => r.channel))], outcomes = ["", "by deadline", "after deadline", "open"];
let combinations = 0;
for (const department of departments) for (const channel of channels) for (const outcome of outcomes) {
  set("case-department", department); set("case-channel", channel); set("case-outcome", outcome);
  const expected = model.cases.filter(r => (!department || r.department === department) && (!channel || r.channel === channel) && (!outcome || r.outcome === outcome));
  eq(exported().cases.map(r => r.case).sort(), expected.map(r => r.case).sort());
  eq(el("case-detail").hidden, expected.length === 0); combinations++;
}
report.scenarios.facet_combinations = combinations;
el("reset-cases").click();
for (const [risk, count] of [["flagged", 94], ["clear", 11], ["unassessed", 1329]]) { set("case-risk", risk); eq(exported().cases.length, count); }
el("show-flagged").click(); eq(exported().cases.length, 94); snapshot("cases-flagged");
el("reset-cases").click(); set("case-date", "2011-12-06"); ok(exported().cases.every(r => r.calendar.deadline <= "2011-12-06"));
eq(exported().cases.length, model.cases.filter(r => r.calendar.deadline <= "2011-12-06").length);
el("reset-cases").click(); set("case-sort", "deadline"); const dates = exported().cases.map(r => r.deadline_epoch_ms); ok(dates.every((n, i) => i === 0 || n >= dates[i - 1]));
set("case-sort", "elapsed"); const elapsed = exported().cases.map(r => r.risk?.elapsed_days_at_log_end ?? -1); ok(elapsed.every((n, i) => i === 0 || n <= elapsed[i - 1]));
el("reset-cases").click(); set("case-search", "does-not-exist", "input"); eq(exported().cases.length, 0); ok(el("case-detail").hidden); ok(el("export-cases").disabled);
el("reset-cases").click(); eq(exported().sources, model.sources); eq(exported().snapshot, model.snapshot);
for (const id of model.brief_cases) { set("case-search", id, "input"); const button = el("case-table").querySelector(`tr[data-case="${id}"] button`); ok(button); button.click(); snapshot(id); }
report.scenarios.risk_states = 3; report.scenarios.brief_cases = model.brief_cases;
tab("paths"); const paths = [];
do {
  for (const button of Array.from(el("path-list").querySelectorAll("[data-path]"))) {
    const id = Number(button.dataset.path), source = model.variants.find(r => r.id === id); paths.push(id); button.click();
    eq(Array.from(el("path-steps").children).map(n => n.textContent), source.steps); eq(el("path-original").textContent, source.variant);
    eq(el("path-summary").textContent, `${source.cases.toLocaleString("en-US")} ${source.cases === 1 ? "case" : "cases"} / ${source.length} recorded ${source.length === 1 ? "step" : "steps"}`);
  }
  if (el("path-next").disabled) break; el("path-next").click();
} while (true);
eq(new Set(paths).size, model.variants.length); report.scenarios.variants_inspected = paths.length;
set("path-search", "confirmation", "input"); ok(el("path-list").querySelector("[data-path]")); snapshot("paths");
set("path-search", "nonexistent_activity", "input"); ok(d.querySelector(".sequence-panel").hidden);
tab("flows"); let flowCount = 0;
for (const type of ["activity", "handover"]) {
  set("flow-type", type); const original = type === "activity" ? model.tables.flows.edges.rows : model.tables.handover.handover.rows;
  const rows = Array.from(el("flow-table").querySelectorAll("tbody tr[data-source-row]")); eq(rows.length, original.length);
  rows.forEach(row => { eq(Array.from(row.cells).map(c => c.textContent), original[Number(row.dataset.sourceRow)].map(String)); }); flowCount += rows.length;
  set("flow-from", original[0][0]); eq(el("flow-table").querySelectorAll("tbody tr[data-source-row]").length, original.filter(r => r[0] === original[0][0]).length);
  set("flow-to", original[0][1]); eq(el("flow-table").querySelectorAll("tbody tr[data-source-row]").length, original.filter(r => r[0] === original[0][0] && r[1] === original[0][1]).length);
  set("flow-min", -1, "input"); eq(el("flow-table").querySelectorAll("tbody tr[data-source-row]").length, 0); eq(el("flow-min").getAttribute("aria-invalid"), "true");
  set("flow-min", 0, "input"); snapshot("flows-" + type);
}
report.scenarios.connections_inspected = flowCount;
el("open-sources").click(); ok(!el("ops-sources").hidden); eq(d.activeElement.id, "close-sources"); el("close-sources").click(); ok(el("ops-sources").hidden);
eq(report.errors, []); eq(report.network_attempts, 0);
report.implementation_sha256 = hash(readFileSync(new URL("tests/test_operations_ui.mjs", root)));
writeFileSync(new URL("operations-dom-verification.json", out), JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify({ assertions: report.assertions, scenarios: report.scenarios, network_attempts: report.network_attempts })); dom.window.close();
