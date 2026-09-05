/* Fixed presentation handlers. Decisions are looked up in the checked table. */
"use strict";
(() => {
  const model = JSON.parse(document.getElementById("model").textContent);
  const el = id => document.getElementById(id);
  const make = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const display = value => value === null ? "—" : typeof value === "boolean" ? (value ? "True" : "False") : String(value);
  const tabs = Array.from(document.querySelectorAll("[data-view]"));
  function showView(view, focus = false) {
    const chosen = tabs.find(t => t.dataset.view === view);
    if (!chosen) return;
    tabs.forEach(t => { const active = t === chosen; t.setAttribute("aria-selected", String(active)); t.tabIndex = active ? 0 : -1; el("view-" + t.dataset.view).hidden = !active; });
    document.title = "Function Chain | " + chosen.textContent.trim().replace(/^\d+/, "").replace("↗", "").trim();
    if (focus) chosen.focus();
  }
  tabs.forEach((tab, i) => {
    tab.addEventListener("click", () => showView(tab.dataset.view));
    tab.addEventListener("keydown", e => {
      let next;
      if (e.key === "ArrowRight") next = (i + 1) % tabs.length;
      if (e.key === "ArrowLeft") next = (i + tabs.length - 1) % tabs.length;
      if (e.key === "Home") next = 0;
      if (e.key === "End") next = tabs.length - 1;
      if (next !== undefined) { e.preventDefault(); showView(tabs[next].dataset.view, true); }
    });
  });
  showView(document.body.dataset.initial);
  el("show-evidence").addEventListener("click", () => { el("evidence").hidden = false; el("evidence").scrollIntoView({ block: "start" }); el("hide-evidence").focus({ preventScroll: true }); });
  el("hide-evidence").addEventListener("click", () => { el("evidence").hidden = true; el("show-evidence").focus(); });
  document.querySelectorAll(".print-button").forEach(b => b.addEventListener("click", () => window.print()));

  if (model.policy) {
    const policy = model.policy;
    function applyAttendance() {
      const raw = el("present").value;
      const n = Number(raw);
      const valid = /^(0|[1-9]\d*)$/.test(raw) && Number.isSafeInteger(n) && n >= 0 && n <= policy.total;
      const row = valid ? policy.truth[n] : null;
      if (row && row[0] !== n) throw new Error("Truth table index mismatch");
      el("present").setAttribute("aria-invalid", String(!valid));
      el("present-error").hidden = valid;
      el("present-error").textContent = valid ? "" : `Enter a whole number from 0 to ${policy.total}.`;
      el("policy-result").className = "panel result-panel" + (!valid ? " is-invalid" : row[1] ? "" : " is-no");
      el("result-title").textContent = !valid ? "Check the input" : row[1] ? "Reachable" : "Not reachable";
      el("result-symbol").textContent = !valid ? "?" : row[1] ? "✓" : "−";
      el("result-present").textContent = valid ? String(n) : "—";
      el("result-rule").textContent = valid ? row[2] : "—";
      el("result-detail").textContent = !valid ? "A valid attendance count is required before showing a decision." : row[1] ? `${n} members are present. The recorded threshold of ${policy.threshold} can be reached.` : `${n} members are present. ${policy.threshold - n} more would be needed to reach the recorded threshold.`;
      const description = valid ? policy.rules[row[2]].description : policy.rules[policy.truth[0][2]].description;
      el("rule-quote").textContent = description;
      document.querySelectorAll("[data-count]").forEach(b => b.setAttribute("aria-pressed", String(valid && Number(b.dataset.count) === n)));
    }
    el("present").addEventListener("input", () => { el("meeting").value = ""; applyAttendance(); });
    el("meeting").addEventListener("change", () => {
      if (el("meeting").value !== "") { el("present").value = String(policy.meetings[Number(el("meeting").value)][1]); applyAttendance(); }
    });
    document.querySelectorAll("[data-count]").forEach(b => b.addEventListener("click", () => { el("present").value = b.dataset.count; el("meeting").value = ""; applyAttendance(); }));
    applyAttendance();
  }

  const NS = "http://www.w3.org/2000/svg";
  function svgNode(tag, attrs, text) {
    const node = document.createElementNS(NS, tag);
    Object.entries(attrs || {}).forEach(([k, v]) => node.setAttribute(k, String(v)));
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function graphView(graph, container, prefix, onSelect) {
    container.replaceChildren();
    const svg = svgNode("svg", { viewBox: `0 0 ${graph.width} ${graph.height}`, "aria-label": prefix === "process" ? "Recorded process dependencies" : "Recorded slide connections" });
    const defs = svgNode("defs");
    const marker = svgNode("marker", { id: prefix + "-arrow", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" });
    marker.append(svgNode("path", { d: "M 0 0 L 10 5 L 0 10 z", fill: "#71948a" })); defs.append(marker); svg.append(defs);
    const byId = new Map(graph.nodes.map(n => [n.id, n]));
    graph.edges.forEach(([a, b]) => {
      const from = byId.get(a), to = byId.get(b);
      const x1 = from.x + 215, y1 = from.y + 35, x2 = to.x - 6, y2 = to.y + 35;
      const mid = (x1 + x2) / 2;
      svg.append(svgNode("path", { class: "graph-edge", fill: "none", stroke: "#71948a", "stroke-width": 2, d: `M${x1} ${y1} C${mid} ${y1},${mid} ${y2},${x2} ${y2}`, "marker-end": `url(#${prefix}-arrow)`, "data-source": a, "data-target": b }));
    });
    graph.nodes.forEach((node, i) => {
      const g = svgNode("g", { class: "graph-node", "data-node-id": node.id, transform: `translate(${node.x},${node.y})` });
      const full = node.text || node.label;
      g.append(svgNode("title", {}, full));
      g.append(svgNode("rect", { width: 215, height: 72, fill: "#ffffff", stroke: "#afc6be", "stroke-width": 1.5, rx: 8 }));
      g.append(svgNode("text", { x: 14, y: 29, class: "node-main", fill: "#19342e", "font-size": 17, "font-weight": 600 }, node.label.length > 23 ? node.label.slice(0, 22) + "…" : node.label));
      const detail = node.text ? (node.text.split("\n").slice(1).join(" · ") || `Shape ${node.id}`) : `Step ${String(i + 1).padStart(2, "0")} · ${node.sentence.split(":").slice(-1)[0]}`;
      g.append(svgNode("text", { x: 14, y: 52, class: "node-sub", fill: "#536d64", "font-size": 11 }, detail));
      if (onSelect) {
        g.setAttribute("role", "button"); g.setAttribute("tabindex", "0"); g.setAttribute("aria-label", `Select step ${i + 1}: ${node.label}`); g.setAttribute("aria-pressed", "false");
        g.addEventListener("click", () => onSelect(node.id));
        g.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(node.id); } });
      }
      svg.append(g);
    });
    container.append(svg);
  }

  if (model.processes) {
    let current;
    function selectStep(id) {
      const node = current.nodes.find(n => n.id === id);
      if (!node) throw new Error("Unknown graph node");
      el("step-choice").value = id;
      el("node-label").textContent = node.label;
      el("node-quote").textContent = node.quote;
      el("node-sentence").textContent = node.sentence;
      el("node-id").textContent = node.id;
      el("node-connections").replaceChildren();
      current.edges.forEach(([a, b]) => { if (a === id || b === id) { const other = current.nodes.find(n => n.id === (a === id ? b : a)); el("node-connections").append(make("li", `${a === id ? "Before" : "After"}: ${other.label} (${other.id})`)); } });
      if (!el("node-connections").children.length) el("node-connections").append(make("li", "No recorded dependency edges."));
      el("process-canvas").querySelectorAll("[data-node-id]").forEach(g => g.setAttribute("aria-pressed", String(g.dataset.nodeId === id)));
    }
    function showProcess() {
      current = model.processes[Number(el("process-choice").value)];
      el("process-counts").textContent = `${current.nodes.length} steps · ${current.edges.length} dependencies`;
      el("step-choice").replaceChildren();
      current.nodes.forEach((n, i) => { const o = make("option", `${String(i + 1).padStart(2, "0")} · ${n.label}`); o.value = n.id; el("step-choice").append(o); });
      graphView(current, el("process-canvas"), "process", selectStep);
      selectStep(current.nodes[0].id);
    }
    el("process-choice").addEventListener("change", showProcess);
    el("step-choice").addEventListener("change", () => selectStep(el("step-choice").value));
    el("process-fit").addEventListener("click", () => { el("process-canvas").scrollTo({ top: 0, left: 0 }); el("process-canvas").focus({ preventScroll: true }); });
    showProcess();
  }

  if (model.records) {
    let page = 0, sort = null, direction = 1;
    function chart(data) {
      const box = el("activity-chart"); box.replaceChildren(); box.hidden = data.id !== "activities";
      if (box.hidden) return;
      box.append(make("h2", "Largest recorded gaps between events"));
      box.append(make("p", "Five activities with the highest mean hours since the previous event.", "hint"));
      const rows = data.rows.filter(r => typeof r[2] === "number").slice().sort((a, b) => b[2] - a[2] || a[0].localeCompare(b[0], "en-US")).slice(0, 5);
      const maximum = Math.max(...rows.map(r => r[2]));
      rows.forEach(row => { const r = make("div", undefined, "bar-row"), track = make("div", undefined, "bar-track"), fill = make("div", undefined, "bar-fill"); fill.style.width = `${100 * row[2] / maximum}%`; fill.setAttribute("aria-hidden", "true"); track.append(fill); r.append(make("span", row[0]), track, make("span", `${row[2].toFixed(2)} h`, "bar-value")); box.append(r); });
    }
    function drawRecords(reset = false) {
      if (reset) page = 0;
      const data = model.records[Number(el("record-choice").value)];
      const query = el("record-search").value.trim().toLocaleLowerCase("en-US");
      let rows = data.rows.map((row, index) => ({ row, index })).filter(r => r.row.some(v => display(v).toLocaleLowerCase("en-US").includes(query)));
      if (sort !== null) rows.sort((a, b) => {
        const x = a.row[sort], y = b.row[sort];
        let result = x === y ? 0 : x === null ? 1 : y === null ? -1 : typeof x === "number" && typeof y === "number" ? x - y : typeof x === "boolean" && typeof y === "boolean" ? Number(x) - Number(y) : String(x).localeCompare(String(y), "en-US", { numeric: true });
        return direction * result || a.index - b.index;
      });
      const size = Number(el("record-page-size").value), pages = Math.max(1, Math.ceil(rows.length / size));
      page = Math.min(page, pages - 1);
      const head = el("records-table").querySelector("thead"), body = el("records-table").querySelector("tbody"), tr = make("tr");
      head.replaceChildren(); body.replaceChildren();
      data.labels.forEach((label, i) => { const th = make("th"), button = make("button", label + (sort === i ? direction === 1 ? " ↑" : " ↓" : " ↕")); th.scope = "col"; th.setAttribute("aria-sort", sort === i ? direction === 1 ? "ascending" : "descending" : "none"); button.type = "button"; button.setAttribute("aria-label", `Sort by ${label}`); button.addEventListener("click", () => { direction = sort === i ? -direction : 1; sort = i; drawRecords(true); }); th.append(button); tr.append(th); });
      head.append(tr);
      rows.slice(page * size, (page + 1) * size).forEach(({row, index}) => { const tr = make("tr"); tr.dataset.sourceRow = String(index); row.forEach((v, i) => { const cell = make("td", display(v), typeof v === "number" ? "numeric" : ""); cell.dataset.column = data.columns[i]; tr.append(cell); }); body.append(tr); });
      if (!rows.length) { const tr = make("tr"), td = make("td", "No matching records. Try another search."); td.colSpan = data.columns.length; tr.append(td); body.append(tr); }
      el("records-caption").textContent = data.title;
      el("record-description").textContent = data.description;
      el("record-count").textContent = rows.length ? `${page * size + 1}–${Math.min((page + 1) * size, rows.length)} of ${rows.length} matching records · ${data.rows.length} total` : `0 matching records · ${data.rows.length} total`;
      el("record-prev").disabled = page === 0;
      el("record-next").disabled = page === pages - 1;
      chart(data);
    }
    el("record-choice").addEventListener("change", () => { sort = null; direction = 1; el("record-search").value = ""; drawRecords(true); });
    el("record-search").addEventListener("input", () => drawRecords(true));
    el("record-page-size").addEventListener("change", () => drawRecords(true));
    el("record-prev").addEventListener("click", () => { page--; drawRecords(); });
    el("record-next").addEventListener("click", () => { page++; drawRecords(); });
    drawRecords();
  }

  function tableBlock(rows) {
    const wrap = make("div", undefined, "table-scroll"), table = make("table"), head = make("thead"), body = make("tbody");
    wrap.tabIndex = 0; wrap.setAttribute("aria-label", "Document table, scroll for all columns");
    rows.forEach((row, i) => { const tr = make("tr"); row.forEach(v => { const cell = make(i ? "td" : "th", v); if (!i) cell.scope = "col"; tr.append(cell); }); (i ? body : head).append(tr); });
    table.append(head, body); wrap.append(table); return wrap;
  }
  if (model.documents) {
    function showDocument() {
      const doc = model.documents[Number(el("document-choice").value)];
      const body = el("document-body"), sections = el("document-section"); body.replaceChildren(); sections.replaceChildren();
      doc.blocks.forEach((block, i) => {
        if (block.kind === "table") { body.append(tableBlock(block.rows)); return; }
        const heading = /^Heading [1-6]$/.test(block.style), quote = /Quote/.test(block.style);
        const tag = heading ? block.style === "Heading 1" ? "h2" : "h3" : quote ? "blockquote" : "p";
        const node = make(tag, block.text); node.id = `doc-block-${i}`; node.dataset.block = String(i); body.append(node);
        if (heading) { const option = make("option", block.text); option.value = node.id; sections.append(option); }
      });
      sections.disabled = !sections.children.length;
    }
    el("document-choice").addEventListener("change", showDocument);
    el("document-section").addEventListener("change", () => { const node = el(el("document-section").value); node.tabIndex = -1; node.scrollIntoView({ block: "start" }); node.focus({ preventScroll: true }); });
    showDocument();
  }
  if (model.deck) {
    function showSlide() {
      const slide = model.deck.slides[Number(el("slide-choice").value)];
      el("slide-heading").textContent = slide.headings.join("\n");
      el("slide-counts").textContent = `${slide.nodes.length} text nodes · ${slide.edges.length} connected arrows`;
      graphView(slide, el("slide-canvas"), "slide", null);
      el("slide-transcript").replaceChildren();
      [...slide.headings, ...slide.nodes.map(n => n.text)].forEach(t => el("slide-transcript").append(make("p", t, "slide-transcript-item")));
    }
    el("slide-choice").addEventListener("change", showSlide); showSlide();
  }
})();
