"use strict";
(() => {
  const model = JSON.parse(document.getElementById("operations-model").textContent);
  const el = id => document.getElementById(id);
  const make = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
  const show = value => value === null ? "No recorded value" : typeof value === "boolean" ? value ? "True" : "False" : String(value);
  const tabs = Array.from(document.querySelectorAll("[data-tab]"));
  function tab(name, focus = false) {
    tabs.forEach(t => { const active = t.dataset.tab === name; t.setAttribute("aria-selected", String(active)); t.tabIndex = active ? 0 : -1; el("ops-" + t.dataset.tab).hidden = !active; if (active && focus) t.focus(); });
  }
  tabs.forEach((t, i) => {
    t.addEventListener("click", () => tab(t.dataset.tab));
    t.addEventListener("keydown", e => {
      const next = e.key === "ArrowRight" ? (i + 1) % tabs.length : e.key === "ArrowLeft" ? (i + tabs.length - 1) % tabs.length : e.key === "Home" ? 0 : e.key === "End" ? tabs.length - 1 : null;
      if (next !== null) { e.preventDefault(); tab(tabs[next].dataset.tab, true); }
    });
  });
  el("open-sources").addEventListener("click", () => { el("ops-sources").hidden = false; el("ops-sources").scrollIntoView({ block: "start" }); el("close-sources").focus(); });
  el("close-sources").addEventListener("click", () => { el("ops-sources").hidden = true; el("open-sources").focus(); });
  el("chart-choice").addEventListener("change", () => document.querySelectorAll("[data-chart]").forEach(n => n.hidden = n.dataset.chart !== el("chart-choice").value));

  const byCase = new Map(model.cases.map(row => [row.case, row]));
  let casePage = 0, selected = model.cases[0].case, filtered = model.cases.slice();
  const compareId = (a, b) => a.case.localeCompare(b.case, "en-US", { numeric: true });
  function options(id, values, initial) {
    el(id).replaceChildren(); const first = make("option", initial); first.value = ""; el(id).append(first);
    Array.from(new Set(values)).sort((a, b) => a.localeCompare(b, "en-US", { numeric: true })).forEach(value => { const option = make("option", value); option.value = value; el(id).append(option); });
  }
  options("case-department", model.cases.map(r => r.department), "All departments");
  options("case-channel", model.cases.map(r => r.channel), "All channels");
  function riskLabel(row) { return !row.risk ? "Not assessed" : row.risk.at_risk ? "Flagged" : "Unflagged"; }
  function selectCase(id) {
    const row = byCase.get(id);
    if (!row) throw new Error("Unknown case key");
    selected = id;
    el("detail-id").textContent = row.case;
    el("detail-group").textContent = `${row.department} / ${row.channel}`;
    el("detail-status").textContent = row.outcome;
    el("detail-risk").textContent = riskLabel(row);
    el("detail-rule").textContent = row.risk ? `${row.risk.rule}: ${model.risk_rules[row.risk.rule]}` : "The recorded rule was applied to open cases only.";
    const fields = [
      ["Recorded deadline", row.deadline], ["Recorded end date", row.enddate], ["Last recorded event", row.last_event],
      ["Calendar start date", row.calendar.start], ["Calendar days to deadline", row.calendar.calendar_days], ["Working days to deadline, Netherlands calendar", row.calendar.working_days_nl],
      ["Elapsed days at snapshot", row.risk ? row.risk.elapsed_days_at_log_end : null], ["Recorded rule", row.risk ? row.risk.rule : null],
    ];
    el("detail-fields").replaceChildren();
    fields.forEach(([label, value]) => { el("detail-fields").append(make("dt", label), make("dd", show(value))); });
    el("detail-json").textContent = JSON.stringify(row, null, 2);
    el("case-table").querySelectorAll("tbody tr[data-case]").forEach(tr => tr.setAttribute("aria-selected", String(tr.dataset.case === id)));
  }
  function filterCases() {
    const query = el("case-search").value.trim().toLocaleLowerCase("en-US");
    const department = el("case-department").value, channel = el("case-channel").value, outcome = el("case-outcome").value, risk = el("case-risk").value, date = el("case-date").value;
    const rows = model.cases.filter(row =>
      (!query || [row.case, row.department, row.channel, row.outcome].some(v => v.toLocaleLowerCase("en-US").includes(query))) &&
      (!department || row.department === department) && (!channel || row.channel === channel) && (!outcome || row.outcome === outcome) &&
      (!risk || (risk === "unassessed" ? row.risk === null : risk === "flagged" ? row.risk?.at_risk === true : row.risk?.at_risk === false)) &&
      (!date || row.calendar.deadline <= date));
    const order = el("case-sort").value;
    rows.sort((a, b) => order === "deadline" ? a.deadline_epoch_ms - b.deadline_epoch_ms || compareId(a, b) : order === "elapsed" ? (b.risk?.elapsed_days_at_log_end ?? -1) - (a.risk?.elapsed_days_at_log_end ?? -1) || compareId(a, b) : compareId(a, b));
    return rows;
  }
  function drawCases(reset = false) {
    if (reset) casePage = 0;
    filtered = filterCases();
    const size = Number(el("case-size").value), pages = Math.max(1, Math.ceil(filtered.length / size));
    casePage = Math.min(casePage, pages - 1);
    const body = el("case-table").querySelector("tbody"); body.replaceChildren();
    filtered.slice(casePage * size, (casePage + 1) * size).forEach(row => {
      const tr = make("tr"); tr.dataset.case = row.case; tr.setAttribute("aria-selected", String(row.case === selected));
      const first = make("td"), button = make("button", row.case, "case-link"); button.type = "button"; button.setAttribute("aria-label", "Inspect " + row.case); button.addEventListener("click", () => selectCase(row.case)); first.append(button);
      const group = make("td", row.department); group.append(make("small", row.channel));
      const flag = make("td"); flag.append(make("span", riskLabel(row), "badge " + (!row.risk ? "" : row.risk.at_risk ? "flagged" : "clear")));
      tr.append(first, group, make("td", row.outcome), make("td", row.calendar.deadline), flag); body.append(tr);
    });
    if (!filtered.length) { const tr = make("tr"), td = make("td", "No cases match these filters. Reset filters or try another search."); td.colSpan = 5; tr.append(td); body.append(tr); }
    el("case-count").textContent = `${filtered.length.toLocaleString("en-US")} of ${model.cases.length.toLocaleString("en-US")} cases`;
    el("case-page").textContent = `Page ${casePage + 1} of ${pages}`;
    el("case-prev").disabled = casePage === 0; el("case-next").disabled = casePage === pages - 1;
    el("export-cases").disabled = filtered.length === 0;
    el("case-detail").hidden = filtered.length === 0;
    if (filtered.length) selectCase(filtered.some(r => r.case === selected) ? selected : filtered[0].case);
  }
  function resetCases() {
    ["case-search", "case-department", "case-channel", "case-outcome", "case-risk", "case-date"].forEach(id => el(id).value = "");
    el("case-sort").value = "case"; drawCases(true);
  }
  ["case-department", "case-channel", "case-outcome", "case-risk", "case-date", "case-sort", "case-size"].forEach(id => el(id).addEventListener("change", () => drawCases(true)));
  el("case-search").addEventListener("input", () => drawCases(true));
  el("reset-cases").addEventListener("click", resetCases);
  el("case-prev").addEventListener("click", () => { casePage--; drawCases(); });
  el("case-next").addEventListener("click", () => { casePage++; drawCases(); });
  el("show-flagged").addEventListener("click", () => { resetCases(); el("case-risk").value = "flagged"; drawCases(true); tab("cases"); });
  el("show-all-cases").addEventListener("click", () => { resetCases(); tab("cases"); });
  el("print-case").addEventListener("click", () => window.print());
  function exportText() { return JSON.stringify({ version: 1, snapshot: model.snapshot, sources: model.sources, cases: filtered }, null, 2) + "\n"; }
  el("export-cases").addEventListener("click", () => {
    const url = URL.createObjectURL(new Blob([exportText()], { type: "application/json" }));
    const link = make("a"); link.href = url; link.download = "recorded-cases.json"; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 0);
  });
  // The downloadable bytes are exposed for deterministic verification without a file dialog.
  window.FunctionChainOperations = Object.freeze({ exportText });
  drawCases();

  let pathPage = 0, selectedPath = 0;
  const countLabel = (n, word) => `${n.toLocaleString("en-US")} ${word}${n === 1 ? "" : "s"}`;
  function selectPath(id) {
    const path = model.variants.find(row => row.id === id);
    if (!path) throw new Error("Unknown variant key");
    selectedPath = id; el("path-title").textContent = `Path ${id + 1}`;
    el("path-summary").textContent = `${countLabel(path.cases, "case")} / ${path.length} recorded ${path.length === 1 ? "step" : "steps"}`;
    el("path-steps").replaceChildren(); path.steps.forEach(step => el("path-steps").append(make("li", step)));
    el("path-original").textContent = path.variant;
    document.querySelectorAll("[data-path]").forEach(button => button.setAttribute("aria-pressed", String(Number(button.dataset.path) === id)));
  }
  function drawPaths(reset = false) {
    if (reset) pathPage = 0;
    const query = el("path-search").value.trim().toLocaleLowerCase("en-US");
    const rows = model.variants.filter(row => row.variant.toLocaleLowerCase("en-US").includes(query)).slice().sort((a, b) => b.cases - a.cases || a.id - b.id);
    const pages = Math.max(1, Math.ceil(rows.length / 8)); pathPage = Math.min(pathPage, pages - 1);
    el("path-list").replaceChildren();
    rows.slice(pathPage * 8, (pathPage + 1) * 8).forEach(row => { const button = make("button", undefined, "path-card"); button.type = "button"; button.dataset.path = String(row.id); button.setAttribute("aria-pressed", String(selectedPath === row.id)); button.append(make("strong", `Path ${row.id + 1}`), make("span", countLabel(row.cases, "case")), make("small", `${countLabel(row.length, "step")} / ${row.steps[0]}`)); button.addEventListener("click", () => selectPath(row.id)); el("path-list").append(button); });
    el("path-count").textContent = `${countLabel(rows.length, "path")} / ${countLabel(rows.reduce((total, row) => total + row.cases, 0), "case")}`;
    el("path-page").textContent = `Page ${pathPage + 1} of ${pages}`; el("path-prev").disabled = pathPage === 0; el("path-next").disabled = pathPage === pages - 1;
    document.querySelector(".sequence-panel").hidden = rows.length === 0;
    if (!rows.length) el("path-list").append(make("p", "No recorded paths match this activity."));
    else selectPath(rows.some(r => r.id === selectedPath) ? selectedPath : rows[0].id);
  }
  el("path-search").addEventListener("input", () => drawPaths(true));
  el("path-prev").addEventListener("click", () => { pathPage--; drawPaths(); });
  el("path-next").addEventListener("click", () => { pathPage++; drawPaths(); });
  drawPaths();

  function flowRows() { return el("flow-type").value === "activity" ? model.tables.flows.edges.rows : model.tables.handover.handover.rows; }
  function drawFlows() {
    const raw = el("flow-min").value, minimum = Number(raw), valid = raw.trim() !== "" && Number.isFinite(minimum) && minimum >= 0;
    el("flow-min").setAttribute("aria-invalid", String(!valid)); el("flow-error").hidden = valid;
    const from = el("flow-from").value, to = el("flow-to").value;
    const rows = valid ? flowRows().map((row, index) => ({ row, index })).filter(({row}) => (!from || row[0] === from) && (!to || row[1] === to) && row[2] >= minimum).sort((a, b) => b.row[2] - a.row[2] || a.index - b.index) : [];
    const body = el("flow-table").querySelector("tbody"); body.replaceChildren();
    rows.forEach(({row, index}) => { const tr = make("tr"); tr.dataset.sourceRow = String(index); row.forEach(value => tr.append(make("td", show(value)))); body.append(tr); });
    if (!rows.length) { const tr = make("tr"), td = make("td", valid ? "No matching connections." : "A valid minimum is required."); td.colSpan = 3; tr.append(td); body.append(tr); }
    el("flow-count").textContent = `${rows.length} of ${flowRows().length} connections`;
  }
  function setFlow() {
    const activity = el("flow-type").value === "activity", rows = flowRows();
    options("flow-from", rows.map(row => row[0]), "All starting points"); options("flow-to", rows.map(row => row[1]), "All destinations"); el("flow-min").value = "0";
    el("flow-caption").textContent = activity ? "Recorded directly following activities" : "Recorded resource handovers";
    el("flow-unit").textContent = activity ? "Recorded count" : "Recorded weight";
    el("flow-note").textContent = activity ? "Inspect the stored directly-follows counts. Repeated activity pairs are retained as recorded." : "Inspect the stored handover weights. These values are weights, not raw event counts.";
    drawFlows();
  }
  el("flow-type").addEventListener("change", setFlow);
  ["flow-from", "flow-to"].forEach(id => el(id).addEventListener("change", drawFlows)); el("flow-min").addEventListener("input", drawFlows);
  setFlow();
})();
