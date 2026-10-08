/**
 * Reviewer portfolio — Profile B faceted epic table + Creator handoff toggles.
 */
(function () {
  "use strict";

  const data = window.REPORT_DATA;
  if (!data || !Array.isArray(data.rows)) {
    document.body.innerHTML =
      '<p role="alert">Report data missing. Regenerate <code>data/report-data.js</code>.</p>';
    return;
  }

  const { meta, filters, themes, rows } = data;
  const jiraBase = meta.jiraBase || "https://appfire.atlassian.net/browse/";
  const jiraIssuesBase = meta.jiraIssuesJqlBase || "https://appfire.atlassian.net/issues/?jql=";
  const storageKey = `reviewer-creator-include:${meta.runId || "portfolio"}`;

  /** @type {Set<string>} */
  let activeFilters = new Set(loadFiltersFromHash());
  let textQuery = "";
  let sortCol = "keyNum";
  let sortDir = 1;

  /** @type {Record<string, boolean>} */
  let creatorInclude = loadCreatorInclude();

  const predicates = {};
  for (const f of filters) {
    if (f.predicate === "field") {
      const field = f.field;
      const value = f.value;
      predicates[f.id] = (r) => r[field] === value;
    } else if (f.predicate === "flag") {
      const field = f.field;
      predicates[f.id] = (r) => !!r[field];
    } else if (f.predicate === "category") {
      const cat = f.category;
      predicates[f.id] = (r) => (r.categories || []).includes(cat);
    } else if (f.predicate === "minHigh") {
      const n = f.min || 1;
      predicates[f.id] = (r) => (r.highCount || 0) >= n;
    }
  }

  const filterById = Object.fromEntries(filters.map((f) => [f.id, f]));

  const els = {
    title: document.getElementById("page-title"),
    meta: document.getElementById("meta-line"),
    note: document.getElementById("note-body"),
    execStats: document.getElementById("execStats"),
    synth: document.getElementById("synth-text"),
    themesHint: document.getElementById("themes-hint"),
    themeBars: document.getElementById("themeBars"),
    themeGroups: document.getElementById("themeGroups"),
    filterCards: document.getElementById("filterCards"),
    statCards: document.getElementById("statCards"),
    clearFilters: document.getElementById("clearFilters"),
    activeFilters: document.getElementById("activeFilters"),
    activeFilterList: document.getElementById("activeFilterList"),
    textFilter: document.getElementById("textFilter"),
    resultSummary: document.getElementById("resultSummary"),
    tableHead: document.getElementById("tableHead"),
    tableBody: document.getElementById("tableBody"),
    creatorJqlPreview: document.getElementById("creatorJqlPreview"),
    creatorSelectDefaults: document.getElementById("creatorSelectDefaults"),
    creatorCopyJql: document.getElementById("creatorCopyJql"),
    creatorExport: document.getElementById("creatorExport"),
  };

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function loadCreatorInclude() {
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === "object") return parsed;
      }
    } catch (_e) {
      /* ignore */
    }
    const out = {};
    for (const r of rows) {
      out[r.key] = r.creatorIncludeDefault !== false;
    }
    return out;
  }

  function saveCreatorInclude() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(creatorInclude));
    } catch (_e) {
      /* file:// quota */
    }
  }

  function creatorJql() {
    const keys = rows
      .filter((r) => creatorInclude[r.key])
      .map((r) => r.key)
      .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
    if (!keys.length) return "key = IMPOSSIBLE-0";
    return `key in (${keys.join(", ")}) ORDER BY key ASC`;
  }

  function creatorHandoffPayload() {
    const included = rows.filter((r) => creatorInclude[r.key]).map((r) => r.key);
    const excluded = rows.filter((r) => !creatorInclude[r.key]).map((r) => r.key);
    const jql = creatorJql();
    let url = jiraIssuesBase + encodeURIComponent(jql);
    return {
      schema_version: "1.0",
      run_id: meta.runId || "",
      exported_at: new Date().toISOString(),
      source_jql: meta.jql || "",
      creator_jql: jql,
      creator_jql_url: url,
      included_epics: included,
      excluded_epics: excluded,
      note: "Exported from portfolio UI; feed creator_jql or creator_jql_url to The Creator.",
    };
  }

  function updateCreatorPreview() {
    if (!els.creatorJqlPreview) return;
    const n = rows.filter((r) => creatorInclude[r.key]).length;
    els.creatorJqlPreview.textContent = `${n} epic(s): ${creatorJql()}`;
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
    const gapLabels = (row.gapFlags || []).map((g) => g.label).join(" ");
    const hay = [
      row.key,
      row.summary,
      row.readinessLabel,
      row.gate,
      row.planningTargetDate || "",
      row.qaPlanningFit,
      gapLabels,
      ...(row.categories || []),
      ...(row.checklistRefs || []),
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
    let findings = 0;
    let high = 0;
    let notFit = 0;
    let multiGap = 0;
    for (const r of subset) {
      findings += r.findingCount || 0;
      high += r.highCount || 0;
      if (r.qaPlanningFit === "not_fit") notFit += 1;
      if (r.multiGap) multiGap += 1;
    }
    return { epics: subset.length, findings, high, notFit, multiGap };
  }

  function loadFiltersFromHash() {
    try {
      const hash = location.hash.replace(/^#/, "");
      if (!hash.startsWith("f=")) return [];
      const out = [];
      for (const segment of hash.slice(2).split(",")) {
        const raw = segment.trim();
        if (!raw) continue;
        const id = decodeURIComponent(raw);
        if (predicates[id]) out.push(id);
      }
      return out;
    } catch (_e) {
      return [];
    }
  }

  function saveFiltersToHash() {
    try {
      if (activeFilters.size === 0) {
        history.replaceState(null, "", location.pathname + location.search);
        return;
      }
      const part = Array.from(activeFilters)
        .map((id) => encodeURIComponent(id))
        .join(",");
      history.replaceState(null, "", `#f=${part}`);
    } catch (_e) {
      /* file:// */
    }
  }

  function readinessPill(label) {
    if (label === "Ready to build tests") return "ok";
    if (label === "Needs clarification before scope can be tested") return "scope";
    return "warn";
  }

  function fitPill(fit) {
    if (fit === "not_fit") return "scope";
    if (fit === "provisional") return "warn";
    return "ok";
  }

  function gapPills(row) {
    const flags = row.gapFlags || [];
    if (!flags.length) return '<span class="gap-pill">—</span>';
    const multi = row.multiGap;
    return (
      '<span class="gap-pills">' +
      flags
        .map((g) => {
          const cls = multi ? "gap-pill multi" : "gap-pill";
          return `<span class="${cls}" title="${escapeHtml(g.id)}">${escapeHtml(g.label)}</span>`;
        })
        .join("") +
      (multi ? '<span class="gap-pill multi" title="multiple criteria">Multiple gaps</span>' : "") +
      "</span>"
    );
  }

  function renderExec() {
    if (els.title) els.title.textContent = meta.title || "Reviewer portfolio";
    if (els.meta) {
      els.meta.textContent =
        meta.subtitle ||
        `${rows.length} epics · run ${meta.runId || ""} · generated ${meta.generatedAt || ""}`;
    }
    if (els.note) {
      els.note.textContent =
        meta.note ||
        "Each row links to a self-contained epic review (Profile A). Gap pills summarise checklist themes; use Creator column to exclude epics from test generation.";
    }
    const all = aggregateStats(rows);
    const execItems = [
      ["Epics reviewed", all.epics],
      ["Total findings", all.findings],
      ["HIGH findings (sum)", all.high],
      ["Not fit for QA planning", all.notFit],
      ["Multiple gap types", all.multiGap],
    ];
    if (els.execStats) {
      els.execStats.innerHTML = execItems
        .map(
          ([label, val]) =>
            `<div class="stat"><div class="stat-label">${escapeHtml(label)}</div>` +
            `<div class="stat-value">${escapeHtml(val)}</div></div>`
        )
        .join("");
    }
    if (els.synth) els.synth.textContent = meta.synthesis || "";
  }

  function renderThemes() {
    if (!themes || !themes.length) return;
    if (els.themesHint) {
      els.themesHint.textContent =
        "Themes use finding category across all epic payloads. Expand a theme to see affected epics and open their reports.";
    }
    const total = themes.reduce((s, t) => s + t.findingCount, 0) || 1;
    if (els.themeBars) {
      els.themeBars.innerHTML = themes
        .map((t) => {
          const pct = Math.round((1000 * t.findingCount) / total) / 10;
          return (
            `<div class="theme-bar-row">` +
            `<span class="theme-bar-label">${escapeHtml(t.label)}</span>` +
            `<span class="theme-bar-track"><span class="theme-bar-fill" style="width:${pct}%;background:${escapeHtml(t.color)}"></span></span>` +
            `<span class="theme-bar-pct">${pct}%</span></div>`
          );
        })
        .join("");
    }
    if (els.themeGroups) {
      els.themeGroups.innerHTML = themes
        .map((t) => {
          const links = (t.epicKeys || [])
            .map((k) => {
              const row = rows.find((r) => r.key === k);
              const rep = row ? row.reportPath : `epics/${k}/review-report.html`;
              return (
                `<a href="${escapeHtml(rep)}">${escapeHtml(k)}</a>` +
                `<a class="report" href="${escapeHtml(rep)}">report</a>`
              );
            })
            .join(" · ");
          return (
            `<details class="theme-group"><summary>${escapeHtml(t.label)} ` +
            `<span style="color:var(--muted);font-weight:400">(${t.epicKeys.length} epics · ${t.findingCount} findings)</span></summary>` +
            `<div class="body"><p>${escapeHtml(t.explanation || "")}</p>` +
            `<p class="epic-links">${links || "—"}</p></div></details>`
          );
        })
        .join("");
    }
  }

  function renderFilterCards() {
    if (!els.filterCards) return;
    els.filterCards.innerHTML = filters
      .map((f) => {
        const count = facetCount(f.id, activeFilters);
        const pressed = activeFilters.has(f.id);
        return (
          `<button type="button" class="facet" data-id="${escapeHtml(f.id)}" aria-pressed="${pressed}">` +
          `<span class="facet-label">${escapeHtml(f.label)}</span>` +
          `<span class="facet-count">${count} epic${count === 1 ? "" : "s"}</span></button>`
        );
      })
      .join("");
    els.filterCards.querySelectorAll(".facet").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-id");
        if (activeFilters.has(id)) activeFilters.delete(id);
        else activeFilters.add(id);
        saveFiltersToHash();
        refresh();
      });
    });
  }

  function renderActiveFilters() {
    const has = activeFilters.size > 0;
    if (els.clearFilters) els.clearFilters.disabled = !has;
    if (!els.activeFilters || !els.activeFilterList) return;
    if (!has) {
      els.activeFilters.hidden = true;
      return;
    }
    els.activeFilters.hidden = false;
    els.activeFilterList.innerHTML = Array.from(activeFilters)
      .map((id) => {
        const f = filterById[id];
        return `<li>${escapeHtml(f ? f.label : id)}</li>`;
      })
      .join("");
  }

  function renderStatCards(subset) {
    const s = aggregateStats(subset);
    const items = [
      ["Visible epics", s.epics],
      ["Findings (visible)", s.findings],
      ["HIGH (visible)", s.high],
      ["Multi-gap (visible)", s.multiGap],
    ];
    if (els.statCards) {
      els.statCards.innerHTML = items
        .map(
          ([label, val]) =>
            `<div class="stat"><div class="stat-label">${escapeHtml(label)}</div>` +
            `<div class="stat-value">${escapeHtml(val)}</div></div>`
        )
        .join("");
    }
  }

  const columns = [
    {
      id: "creator",
      label: "Creator",
      sort: null,
      className: "num",
      cell: (r) => {
        const checked = creatorInclude[r.key] ? " checked" : "";
        return `<input type="checkbox" class="creator-check" data-key="${escapeHtml(r.key)}" aria-label="Include ${escapeHtml(r.key)} in Creator JQL"${checked}>`;
      },
    },
    {
      id: "keyNum",
      label: "Key",
      sort: (a, b) => a.keyNum - b.keyNum,
      cell: (r) => `<a href="${escapeHtml(r.url)}">${escapeHtml(r.key)}</a>`,
    },
    {
      id: "summary",
      label: "Summary",
      sort: (a, b) => a.summary.localeCompare(b.summary),
      cell: (r) => escapeHtml(r.summary),
    },
    {
      id: "gaps",
      label: "Gap signals",
      sort: (a, b) => (a.gapFlagCount || 0) - (b.gapFlagCount || 0),
      cell: (r) => gapPills(r),
    },
    {
      id: "planning",
      label: "Planning target",
      sort: (a, b) =>
        String(a.planningTargetDate || "").localeCompare(String(b.planningTargetDate || "")),
      cell: (r) => escapeHtml(r.planningTargetDate || "—"),
    },
    {
      id: "fit",
      label: "QA planning fit",
      sort: (a, b) => a.qaPlanningFit.localeCompare(b.qaPlanningFit),
      cell: (r) =>
        `<span class="pill ${fitPill(r.qaPlanningFit)}">${escapeHtml(r.qaPlanningFit.replace("_", " "))}</span>`,
    },
    {
      id: "readiness",
      label: "Readiness",
      sort: (a, b) => a.readinessSort - b.readinessSort,
      cell: (r) =>
        `<span class="pill ${readinessPill(r.readinessLabel)}">${escapeHtml(r.readinessLabel)}</span>`,
    },
    {
      id: "high",
      label: "HIGH",
      sort: (a, b) => a.highCount - b.highCount,
      cell: (r) => String(r.highCount),
      className: "num",
    },
    {
      id: "report",
      label: "Report",
      sort: null,
      cell: (r) => `<a href="${escapeHtml(r.reportPath)}">Open HTML</a>`,
    },
  ];

  function renderTable(subset) {
    if (!els.tableHead || !els.tableBody) return;
    els.tableHead.innerHTML =
      "<tr>" +
      columns
        .map((c) => {
          if (!c.sort) return `<th>${escapeHtml(c.label)}</th>`;
          const aria =
            sortCol === c.id
              ? sortDir === 1
                ? ' aria-sort="ascending"'
                : ' aria-sort="descending"'
              : "";
          return `<th class="sortable" data-col="${escapeHtml(c.id)}"${aria}>${escapeHtml(c.label)}<span class="sort-icon"></span></th>`;
        })
        .join("") +
      "</tr>";
    const sorted = subset.slice().sort((a, b) => {
      const col = columns.find((c) => c.id === sortCol);
      if (!col || !col.sort) return 0;
      return sortDir * col.sort(a, b);
    });
    els.tableBody.innerHTML = sorted
      .map((r) => {
        return (
          "<tr>" +
          columns
            .map((c) => {
              const cls = c.className ? ` class="${c.className}"` : "";
              return `<td${cls}>${c.cell(r)}</td>`;
            })
            .join("") +
          "</tr>"
        );
      })
      .join("");
    els.tableBody.querySelectorAll(".creator-check").forEach((cb) => {
      cb.addEventListener("change", () => {
        const key = cb.getAttribute("data-key");
        creatorInclude[key] = cb.checked;
        saveCreatorInclude();
        updateCreatorPreview();
      });
    });
    els.tableHead.querySelectorAll("th.sortable").forEach((th) => {
      th.addEventListener("click", () => {
        const col = th.getAttribute("data-col");
        if (sortCol === col) sortDir = -sortDir;
        else {
          sortCol = col;
          sortDir = 1;
        }
        refresh();
      });
      th.classList.remove("sort-asc", "sort-desc");
      if (th.getAttribute("data-col") === sortCol) {
        th.classList.add(sortDir === 1 ? "sort-asc" : "sort-desc");
      }
    });
  }

  function refresh() {
    renderFilterCards();
    renderActiveFilters();
    const subset = visibleRows();
    renderStatCards(subset);
    renderTable(subset);
    updateCreatorPreview();
    if (els.resultSummary) {
      els.resultSummary.textContent = `Showing ${subset.length} of ${rows.length} epics`;
    }
  }

  if (els.clearFilters) {
    els.clearFilters.addEventListener("click", () => {
      activeFilters.clear();
      saveFiltersToHash();
      refresh();
    });
  }
  if (els.textFilter) {
    els.textFilter.addEventListener("input", () => {
      textQuery = els.textFilter.value;
      refresh();
    });
  }
  if (els.creatorSelectDefaults) {
    els.creatorSelectDefaults.addEventListener("click", () => {
      for (const r of rows) {
        creatorInclude[r.key] = r.creatorIncludeDefault !== false;
      }
      saveCreatorInclude();
      refresh();
    });
  }
  if (els.creatorCopyJql) {
    els.creatorCopyJql.addEventListener("click", async () => {
      const jql = creatorJql();
      try {
        await navigator.clipboard.writeText(jql);
        els.creatorCopyJql.textContent = "Copied!";
        setTimeout(() => {
          els.creatorCopyJql.textContent = "Copy JQL";
        }, 1500);
      } catch (_e) {
        window.prompt("Copy JQL:", jql);
      }
    });
  }
  if (els.creatorExport) {
    els.creatorExport.addEventListener("click", () => {
      const payload = creatorHandoffPayload();
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "creator-handoff.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  renderExec();
  renderThemes();
  refresh();
})();
