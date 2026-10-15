# Trinity Studio — screenshot capture guide

Git does not ship bitmaps by default (size + UI churn). **Operators and doc maintainers** add PNGs here after each major Studio release so Confluence and [`OPERATOR-ONBOARDING.md`](../OPERATOR-ONBOARDING.md) stay visual.

**Naming:** `{area}-{short-description}.png` (lowercase, hyphens).

---

## Required set (pilot GA)

Capture at **1280×800** or wider, light theme, no personal tokens visible in `.env` or browser.

| Filename | What to show | Used in |
|----------|--------------|---------|
| `nav-dashboard.png` | Top nav: Dashboard, Statistics, Personas, Reviewer configs, Creator, Importer | OPERATOR-ONBOARDING §4 |
| `dashboard-run-list.png` | Dashboard with at least one run imported | FIRST-RUN |
| `run-epic-table.png` | Run page epic/unit table with readiness column | METRICS / Statistics intro |
| `unit-triage.png` | Unit detail: approve, fit, link to report | MANUAL |
| `reviewer-configs-prompt.png` | Reviewer configs with **Copy Cursor prompt** visible | PROMPTS-AND-INPUTS §1 |
| `creator-import.png` | Creator tab: import batch + test list | PROMPTS-AND-INPUTS §2 |
| `importer-plan.png` | Importer: instance, mapping, project key, preview | GUIDE |
| `statistics-compare.png` | Statistics: run selected + compare dropdowns | MANUAL §5.9 |

---

## Optional

| Filename | What to show |
|----------|--------------|
| `personas-editor.png` | Personas edit screen |
| `mcp-cursor-settings.png` | Cursor Settings → MCP with Atlassian servers (blur tokens) |

---

## Publishing to Confluence

1. Attach PNGs to the relevant QACoE page (see [`confluence/README.md`](../../confluence/README.md)).
2. Insert image macro below the matching heading in **First run** or **Operator manual**.
3. Keep git copies here so the next `sync_confluence_from_git.py` run can reference the same assets if wiki storage moves.

---

## Status (2026-10-15)

Committed captures from Studio **0.2.0** (demo run `DEMO-4500`). Re-capture after major nav changes.

| File | Status |
|------|--------|
| `nav-dashboard.png` | Done |
| `dashboard-run-list.png` | Done (same view as nav-dashboard; runs table visible) |
| `run-epic-table.png` | Done |
| `unit-triage.png` | Done |
| `reviewer-configs-prompt.png` | Done |
| `creator-import.png` | Done |
| `importer-plan.png` | Done |
| `statistics-compare.png` | Done |

**FIRST-RUN** embeds: see [Phase 1 screenshots](../../FIRST-RUN.md#11-load-demo-data).

Confluence: attach these files to **First run** / **Operator onboarding** wiki pages (git does not auto-upload binaries).
