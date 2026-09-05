/** Verify the catalog, every local artifact link, filtering, and keyboard controls. */
import jsdom from "jsdom";
import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
const { JSDOM, VirtualConsole } = jsdom;
const root = new URL("../", import.meta.url), out = new URL("proofs/out/augmentation/", root);
const hash = bytes => createHash("sha256").update(bytes).digest("hex");
const source = readFileSync(new URL("index.html", out), "utf8");
const report = { assertions: 0, errors: [], network_attempts: 0, file_sha256: hash(source), scope: "Offline DOM behavior and artifact hashes; browser layout unverified" };
const eq = (a, b) => { assert.deepEqual(a, b); report.assertions++; };
const console = new VirtualConsole(); console.on("jsdomError", error => report.errors.push(error.message));
const dom = new JSDOM(source, { runScripts: "dangerously", virtualConsole: console, beforeParse(w) {
  const blocked = () => { report.network_attempts++; throw new Error("External connection forbidden"); };
  w.fetch = blocked; w.XMLHttpRequest = blocked; w.WebSocket = blocked; w.EventSource = blocked;
} });
const w = dom.window, d = w.document, model = JSON.parse(d.getElementById("gallery-model").textContent);
eq(model, JSON.parse(readFileSync(new URL("catalog.json", out)))); eq(d.documentElement.lang, "en-US");
eq(d.querySelectorAll("script[src],link[href],iframe").length, 0);
const targets = new Map();
for (const e of model.entries) { targets.set(e.file, e.sha256); for (const a of e.alternates) targets.set(a.file, a.sha256); }
for (const link of d.querySelectorAll("[data-artifact]")) {
  const file = link.getAttribute("href"); eq(file.includes("/"), false); eq(hash(readFileSync(new URL(file, out))), targets.get(file));
}
const search = d.getElementById("gallery-search"), tabs = [...d.querySelectorAll("[data-category]")], cards = [...d.querySelectorAll("[data-entry]")];
let combinations = 0;
for (const tab of tabs) for (const query of ["", "case", "policy", "P76", "SVG", "no matching record", "<script>"]) {
  tab.click(); search.value = query; search.dispatchEvent(new w.Event("input", { bubbles: true }));
  const expected = model.entries.filter(e => (tab.dataset.category === "all" || e.category === tab.dataset.category) && [e.title, e.description, e.proof, e.format, e.evidence].join(" ").toLocaleLowerCase("en-US").includes(query.toLocaleLowerCase("en-US"))).map(e => e.id);
  eq(cards.filter(card => !card.hidden).map(card => card.dataset.entry), expected);
  eq(d.getElementById("gallery-count").textContent, `${expected.length} ${expected.length === 1 ? "deliverable" : "deliverables"}`);
  eq(d.getElementById("gallery-empty").hidden, expected.length !== 0); combinations++;
}
d.getElementById("gallery-reset").click(); eq(search.value, ""); eq(cards.filter(c => !c.hidden).length, model.entries.length); eq(d.activeElement.id, "gallery-search");
let current = tabs[0];
for (const [key, category] of [["End", "figures"], ["Home", "all"], ["ArrowRight", "interfaces"], ["ArrowLeft", "all"]]) {
  current.dispatchEvent(new w.KeyboardEvent("keydown", { key, bubbles: true })); eq(d.activeElement.dataset.category, category); current = d.activeElement;
  eq(tabs.filter(t => t.tabIndex === 0).length, 1);
}
const snapshot = d.cloneNode(true); snapshot.querySelectorAll("script").forEach(n => n.remove());
const snapshotText = "<!doctype html>\n" + snapshot.documentElement.outerHTML;
writeFileSync(new URL("proofs/cache/gallery-snapshot.html", root), snapshotText);
report.snapshot_sha256 = hash(snapshotText); report.implementation_sha256 = hash(readFileSync(new URL("tests/test_gallery_ui.mjs", root)));
report.entries = model.entries.length; report.unique_artifact_links = targets.size; report.filter_combinations = combinations;
eq(report.errors, []); eq(report.network_attempts, 0);
writeFileSync(new URL("gallery-dom-verification.json", out), JSON.stringify(report, null, 2) + "\n");
process.stdout.write(JSON.stringify({ assertions: report.assertions, entries: report.entries, links: report.unique_artifact_links, filter_combinations: combinations, network_attempts: 0 }) + "\n");
dom.window.close();
