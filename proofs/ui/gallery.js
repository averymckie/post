(() => {
  "use strict";
  const model = JSON.parse(document.getElementById("gallery-model").textContent);
  const search = document.getElementById("gallery-search"), tabs = [...document.querySelectorAll("[data-category]")], cards = [...document.querySelectorAll("[data-entry]")];
  let category = "all";
  const rows = new Map(model.entries.map(e => [e.id, e]));
  function draw() {
    const query = search.value.trim().toLocaleLowerCase("en-US");
    let count = 0;
    for (const card of cards) {
      const entry = rows.get(card.dataset.entry);
      const haystack = [entry.title, entry.description, entry.proof, entry.format, entry.evidence].join(" ").toLocaleLowerCase("en-US");
      card.hidden = !((category === "all" || category === entry.category) && haystack.includes(query));
      if (!card.hidden) count++;
    }
    document.getElementById("gallery-count").textContent = `${count} ${count === 1 ? "deliverable" : "deliverables"}`;
    document.getElementById("gallery-empty").hidden = count !== 0;
  }
  function select(button, focus = false) {
    category = button.dataset.category;
    for (const tab of tabs) { const active = tab === button; tab.setAttribute("aria-selected", String(active)); tab.tabIndex = active ? 0 : -1; }
    draw(); if (focus) button.focus();
  }
  tabs.forEach((button, index) => {
    button.addEventListener("click", () => select(button));
    button.addEventListener("keydown", event => {
      const positions = { ArrowRight: (index + 1) % tabs.length, ArrowLeft: (index + tabs.length - 1) % tabs.length, Home: 0, End: tabs.length - 1 };
      if (event.key in positions) { event.preventDefault(); select(tabs[positions[event.key]], true); }
    });
  });
  search.addEventListener("input", draw);
  document.getElementById("gallery-reset").addEventListener("click", () => { search.value = ""; select(tabs[0]); search.focus(); });
  draw();
})();
