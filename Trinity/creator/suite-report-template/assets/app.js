/**
 * Creator test suite — Profile B faceted table + step details.
 */
(function () {
  "use strict";

  const data = window.REPORT_DATA;
  if (!data || !Array.isArray(data.rows)) {
    document.body.innerHTML =
      '<p role="alert">Report data missing. Regenerate <code>data/report-data.js</code>.</p>';
    return;
  }

  const { meta, filters, stats, columns, rows } = data;

  let activeFilters = new Set(loadFiltersFromHash());
  let textQuery = "";
  let sortCol = 0;
  let sortDir = 1;

  const els = {
    title: document.getElementById("page-title"),
    meta: document.getElementById("meta-line"),
    note: document.getElementById("note-body"),
    filterCards: document.getElementById("filterCards"),
    statCards: document.getElementById("statCards"),
    clearFilters: document.getElementById("clearFilters"),
    activeFilters: document.getElementById("activeFilters"),
    activeFilterList: document.getElementById("activeFilterList"),
    textFilter: document.getElementById("textFilter"),
    resultSummary: document.getElementById("resultSummary"),
    tableHead: document.getElementById("tableHead"),
    tableBody: document.getElementById("tableBody"),
    stepPanelsBody: document.getElementById("stepPanelsBody"),
  };

  const predicates = {
    "tier-p0": (r) => r.execution_tier === "P0",
    "tier-p1": (r) => r.execution_tier === "P1",
    "tier-p2": (r) => r.execution_tier === "P2",
    "tier-p3": (r) => r.execution_tier === "P3",
    "pattern-journey": (r) => r.test_pattern === "journey",
    "pattern-atomic": (r) => r.test_pattern === "atomic",
    "review-approved": (r) => r.human_review_status === "approved",
    "review-pending": (r) =>
      r.human_review_status === "pending" || r.human_review_status === "edited",
    "review-rejected": (r) => r.human_review_status === "rejected",
    "automation-candidate": (r) => r.automation_candidate,
    "automation-full": (r) => r.automation_fit === "full",
    "automation-partial": (r) => r.automation_fit === "partial",
    "automation-manual": (r) => r.automation_fit === "manual_only",
    "deferrable": (r) => r.deferrable,
    "import-ready": (r) => r.import_ready,
  };

  const filterById = Object.fromEntries(filters.map((f) => [f.id, f]));

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function rowMatchesFacets(row, active, excludeId) {
    for (const id of active) {
      if (id === excludeId) continue;
      const fn = predicates[id];
      if (fn && !fn(row)) return false;
    }
    return true;
  }

  function rowMatchesAllFacets(row, active) {
    return rowMatchesFacets(row, active, null);
  }

  function facetCount(facetId, active) {
    const fn = predicates[facetId];
    if (!fn) return 0;
    let n = 0;
    for (const row of rows) {
      if (!rowMatchesFacets(row, active, facetId)) continue;
      if (fn(row)) n += 1;
    }
    return n;
  }

  function rowMatchesText(row, q) {
    if (!q) return true;
    const hay = [
      row.draft_id,
      row.title,
      row.execution_tier,
      row.priority,
      row.priority_score_total,
      row.test_pattern,
      row.human_review_status,
      row.automation_fit,
      ...(row.linked_requirement_keys || []),
      ...(row.linked_ac_ids || []),
      row.steps_plain,
    ]
      .join(" ")
      .toLowerCase();
    return hay.includes(q);
  }

  function visibleRows() {
    const q = textQuery.trim().toLowerCase();
    return rows.filter(
      (r) => rowMatchesAllFacets(r, activeFilters) && rowMatchesText(r, q)
    );
  }

  function aggregateStats(subset) {
    let journeys = 0;
    let approved = 0;
    let importReady = 0;
    let steps = 0;
    for (const r of subset) {
      if (r.test_pattern === "journey") journeys += 1;
      if (r.human_review_status === "approved") approved += 1;
      if (r.import_ready) importReady += 1;
      steps += r.step_count || 0;
    }
    return {
      tests: subset.length,
      journeys,
      approved,
      importReady,
      steps,
    };
  }

  function loadFiltersFromHash() {
    const hash = location.hash.replace(/^#/, "");
    if (!hash.startsWith("f=")) return [];
    const out = [];
    for (const segment of hash.slice(2).split(",")) {
      const raw = segment.trim();
      if (!raw) continue;
      try {
        const id = decodeURIComponent(raw);
        if (predicates[id]) out.push(id);
      } catch {
        /* ignore */
      }
    }
    return out;
  }

  function syncHash() {
    try {
      if (activeFilters.size === 0) {
        history.replaceState(null, "", location.pathname + location.search);
        return;
      }
      const part = Array.from(activeFilters)
        .sort()
        .map(encodeURIComponent)
        .join(",");
      history.replaceState(null, "", `#f=${part}`);
    } catch {
      /* file:// */
    }
  }

  function compareRows(a, b, colKey) {
    const av = a.sortValues[colKey] ?? "";
    const bv = b.sortValues[colKey] ?? "";
    return String(av).localeCompare(String(bv), undefined, {
      sensitivity: "base",
      numeric: true,
    });
  }

  function renderMeta() {
    if (meta.title) els.title.textContent = meta.title;
    els.meta.textContent = meta.subtitle || "";
    els.note.innerHTML = meta.noteHtml || "";
  }

  function renderFilterCards() {
    els.filterCards.innerHTML = "";
    for (const f of filters) {
      const count = facetCount(f.id, activeFilters);
      const pressed = activeFilters.has(f.id);
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "card card-facet" + (f.accent ? ` accent-${f.accent}` : "");
      btn.dataset.filterId = f.id;
      btn.setAttribute("aria-pressed", pressed ? "true" : "false");
      btn.disabled = count === 0 && !pressed;
      btn.innerHTML = `<div class="n">${count}</div><div class="l">${escapeHtml(f.label)}</div>`;
      btn.addEventListener("click", () => toggleFilter(f.id));
      els.filterCards.appendChild(btn);
    }
  }

  function renderStatCards(subset) {
    const agg = aggregateStats(subset);
    els.statCards.innerHTML = stats
      .map(
        (s) =>
          `<div class="card card-stat"><div class="n">${agg[s.key] ?? 0}</div><div class="l">${escapeHtml(s.label)}</div></div>`
      )
      .join("");
  }

  function renderActiveChips() {
    els.activeFilterList.innerHTML = "";
    if (activeFilters.size === 0) {
      els.activeFilters.hidden = true;
      els.clearFilters.disabled = true;
      return;
    }
    els.activeFilters.hidden = false;
    els.clearFilters.disabled = false;
    for (const id of Array.from(activeFilters).sort()) {
      const def = filterById[id];
      const li = document.createElement("li");
      li.textContent = def ? def.shortLabel || def.label : id;
      els.activeFilterList.appendChild(li);
    }
  }

  function renderTableHead() {
    els.tableHead.innerHTML = `<tr>${columns
      .map(
        (c, i) =>
          `<th scope="col" data-col="${i}" tabindex="0">${escapeHtml(c.label)}<span class="arrow" aria-hidden="true"></span></th>`
      )
      .join("")}</tr>`;
    els.tableHead.querySelectorAll("th").forEach((h) => {
      h.addEventListener("click", () => onSort(Number(h.dataset.col)));
      h.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          onSort(Number(h.dataset.col));
        }
      });
    });
  }

  function updateSortHeaders() {
    const headers = els.tableHead.querySelectorAll("th");
    headers.forEach((h) => {
      h.classList.remove("sorted-asc", "sorted-desc");
      h.setAttribute("aria-sort", "none");
    });
    const active = headers[sortCol];
    if (!active) return;
    active.classList.add(sortDir === 1 ? "sorted-asc" : "sorted-desc");
    active.setAttribute("aria-sort", sortDir === 1 ? "ascending" : "descending");
  }

  function renderTableBody(sorted) {
    els.tableBody.innerHTML = sorted
      .map((row) => {
        const reqs = (row.linked_requirement_keys || []).join(", ") || "—";
        const acs = (row.linked_ac_ids || []).join(", ") || "—";
        const review = row.human_review_status || "—";
        const auto = row.automation_fit || "—";
        const xray = row.xray_test_key
          ? escapeHtml(row.xray_test_key)
          : row.marked_for_xray_import
            ? "marked"
            : "—";
        return `<tr>
  <td><code>${escapeHtml(row.draft_id)}</code></td>
  <td>${escapeHtml(row.title)}</td>
  <td>${escapeHtml(row.execution_tier || "—")}</td>
  <td>${escapeHtml(row.priority || "—")}</td>
  <td>${escapeHtml(String(row.priority_score_total ?? "—"))}</td>
  <td>${escapeHtml(row.test_pattern || "—")}</td>
  <td>${escapeHtml(review)}</td>
  <td>${escapeHtml(auto)}</td>
  <td>${escapeHtml(reqs)}</td>
  <td>${escapeHtml(acs)}</td>
  <td>${row.step_count ?? 0}</td>
  <td>${xray}</td>
</tr>`;
      })
      .join("");
  }

  function renderStepPanels(sorted) {
    if (!els.stepPanelsBody) return;
    els.stepPanelsBody.innerHTML = sorted
      .map(
        (row) =>
          `<details class="test-detail" id="test-${escapeHtml(row.draft_id)}">
  <summary><code>${escapeHtml(row.draft_id)}</code> — ${escapeHtml(row.title)}</summary>
  ${row.steps_html || "<p class=\"muted\">No steps in batch.</p>"}
</details>`
      )
      .join("");
  }

  function onSort(col) {
    if (sortCol === col) sortDir *= -1;
    else {
      sortCol = col;
      sortDir = 1;
    }
    refresh();
  }

  function toggleFilter(id) {
    if (activeFilters.has(id)) activeFilters.delete(id);
    else activeFilters.add(id);
    syncHash();
    refresh();
  }

  function clearAllFilters() {
    activeFilters.clear();
    syncHash();
    refresh();
  }

  function refresh() {
    renderFilterCards();
    renderActiveChips();
    const visible = visibleRows();
    const colKey = columns[sortCol]?.key ?? "draft_id";
    const sorted = [...visible].sort(
      (a, b) => sortDir * (compareRows(a, b, colKey) || 0)
    );
    renderStatCards(visible);
    renderTableBody(sorted);
    renderStepPanels(sorted);
    updateSortHeaders();
    els.resultSummary.textContent = `Showing ${visible.length} of ${rows.length} tests${
      activeFilters.size
        ? ` (${activeFilters.size} filter${activeFilters.size > 1 ? "s" : ""} active)`
        : ""
    }${textQuery.trim() ? " matching search" : ""}.`;
  }

  els.textFilter.addEventListener("input", () => {
    textQuery = els.textFilter.value;
    refresh();
  });
  els.clearFilters.addEventListener("click", clearAllFilters);
  window.addEventListener("hashchange", () => {
    activeFilters = new Set(loadFiltersFromHash());
    refresh();
  });

  renderMeta();
  renderTableHead();
  refresh();
})();
