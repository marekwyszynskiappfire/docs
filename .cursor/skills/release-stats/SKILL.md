---
name: release-stats
description: >-
  End-to-end BigPicture Cloud release statistics: on trigger, ask for the
  release-stats canvas URL; if the canvas already exists, enrich train JSON
  and re-render in place (avoid re-gather unless needed). Gather cut-off, Xray,
  production dates, bugs, customer-reported SUPPORT, optional known-issues Git
  breakdown; refresh comparison table and per-train sections. Use for
  /release-stats or a train version (8.77).
disable-model-invocation: true
---

# Release stats

**Deliverable:** Cursor canvas file (`.canvas.tsx`), default:

`~/.cursor/projects/Users-marek-wyszynski-repo-DOCS/canvases/release-stats.canvas.tsx`

Regenerated with `render_canvas.py` (pass `--canvas` with the path or URL the operator gave).

**Data:** one file per train — `Release Process/stats/data/{version}.json` (`schema_version: 1`). Reference train: [`8.76.json`](Release%20Process/stats/data/8.76.json).

**Scope of this skill:** the **whole** release-stats product (comparison table, per-train stats, Xray bars, bug tables, cloud versions, customer-reported, known issues). Known-issues Git grouping is **one late optional block**, not the main workflow.

Details: [`reference.md`](reference.md) (canvas map, `metrics` contract, MCP import, scripts).

**On every trigger:** run **step 0** of the wizard first (canvas URL). Do not gather or overwrite JSON until the canvas path is confirmed.

**Always run the interactive configuration below before work**, unless the operator names a train **and** says to skip the interview (still ask for canvas URL unless they already pasted it in the same message).

---

## What the canvas shows

### Top: Release comparison table

- Renders **every** `Release Process/stats/data/*.json` (newest train left in per-release sections; comparison columns follow `RELEASES` sort in `render_canvas.py`).
- **Adding train 8.77** → save `8.77.json` → run `render_canvas.py` → a **new column** `8.77` appears automatically.
- Rows (today) read from each file’s `metrics` / view model:

| Row label | Source |
|-----------|--------|
| Days cut-off → production | `metrics.days_in_preprod`, `metrics.release_date` |
| Test run — tests / executed / passed / failed / skipped / to do | `metrics.tests_*` ← Xray |
| Test run duration (weekdays) | `metrics.test_run_duration_days` |
| Linked bugs | `metrics.bugs_found_by_test_run` (Defect link count) |
| Other bugs since cut-off | `metrics.bugs_other_since_cutoff` |
| Customer-reported (SUPPORT link) | `metrics.bugs_customer_reported` |
| QA engineers (test executors) | `metrics.qa_engineers_count` |

To **add a new comparison row**, extend `COMPARISON_METRICS` + `comparisonValue()` in `render_canvas.py` and populate the matching field in `metrics` during gather/enrich. Do not add rows only in prose — the table is code-driven.

### Per train: collapsible “Cloud {version}”

Each section is filled from the same JSON:

1. **Stat row** — cut-off, production release (changelog signal + trigger bug link), days in preprod, linked / other / customer-reported counts, test-run duration, QA engineer count (and names when present).
2. **Major Release Test Run** — TC execution link, summary, **UsageBar** + stats (Xray: passed/failed/skipped/todo rules below).
3. **Failed tests (Xray test runs)** — collapsible table when `test_run.failed_tests[]` is present; each row links to the Xray Testing Board (`testExecutionKey` = Major run, `testKey` = test case). Populated by `enrich_xray_stats.py` (same latest-status rule as failed counts).
4. **Bugs by priority** — pie from cut-off-scoped bugs (`metrics.bugs_by_priority`).
5. **Linked bugs** — all `test_run.defect_keys` as **BugTable**; Jira link uses `issue in linkedIssues("TC-…")`.
6. **Other bugs since cut-off** — BugTable + JQL (cut-off bugs not linked from the run).
7. **Customer-reported bugs** — **CustomerBugTable** (SUPPORT columns).
8. **Known issues after release (Git placement)** — only when `known_issues.breakdown[]` exists; groups + BugTables (optional).
9. **bigpicture-cloud versions** — Jira fix versions table + release signal notes.
10. **Notes** — gather warnings (ambiguous test run, missing Xray, etc.).

Re-render after **any** JSON change that should appear in the canvas.

---

## Domain rules (do not reinterpret)

- **Cut-off:** date embedded in ONE Affected Version `preprod/YYYY-MM-DD/{version}`. If several preprod names match a train, use the **latest** date and record in `notes`.
- **Test run:** exactly one TC Test Execution whose summary contains the version and **`Major Release Test Run`**. If zero or many → list candidates; **never** pick silently.
- **Bugs (cut-off scope):** `issuetype = Bug`, that preprod AV, `created >= cutoff`.
  - **`found_by_test_run`** on a row = key ∈ `test_run.defect_keys` (Xray Defect links).
  - **`metrics.bugs_found_by_test_run`** = **`len(defect_keys)`**, not “linked keys that also match cut-off JQL”.
- **Linked bugs (canvas + Jira):** `issuetype = Bug AND issue in linkedIssues("{TC key}")`. Count = defect link count.
- **Other bugs:** cut-off JQL with `AND issue not in linkedIssues("{TC key}")` inserted **before** `ORDER BY`.
- **Production date (`metrics.release_date`):** **earliest** date a **test-run-linked** bug hits status **`Done`** (exact name) while Fix Version matches `bigpicture-cloud-{version}.*`. Replay changelogs (Fix Version + status). Jira “released” on a cloud version is informational only.
- **Xray:** credentials from `Trinity/studio/.env.production`. Counts from **`getTestExecution.testRuns`** (latest status per test). Skipped = ABORTED, SKIPPED, N/A. Executed excludes TO DO and EXECUTING. Do not invent counts.
- **Failed test links:** `test_run.failed_tests[]` entries `{ key, summary, url }` where `url` is the Xray Testing Board pattern  
  `…/projects/TC?selectedItem=…xray__testing-board&ac.testExecutionKey={TC execution}&ac.testKey={test case}#!page=test-run&testExecutionKey={TC execution}&testKey={test case}&testPlanId=`  
  Built by `gather_release_stats.xray_testing_board_url` during **`enrich_xray_stats.py`** (same FAILED/FAIL latest-status rule as `metrics.tests_failed`).
- **Test run duration:** **weekdays only** (Mon–Fri) from first → last test status change in that execution; same calendar day → 0.
- **QA engineers:** distinct `executedById` on all test runs in the Major Release Test Run; names via Jira user lookup when API allows (`apply_qa_user_cache.py` if needed).
- **Customer-reported:** bugs with train **preprod AV** and a link to **`SUPPORT-*`** (or Support Ticket types). MCP `issuelinks` + `versions` (`view: full`), caches in `data/support_links_cache.json` / `affected_versions_cache.json`, then `enrich_customer_support.py`.
- **Known issues (post-release, optional):** JQL in [`reference.md`](reference.md). **`breakdown[]`** + GitHub `AppfireBigPicture/ppm` is for operational follow-up after release — not required for a new train to appear in the comparison table.

### Trains since a date

```bash
python3 "Release Process/stats/scripts/gather_release_stats.py" --since 2025-10-01
```

If REST 404 on ONE, use `Release Process/stats/trains_since_2025-10-01.json`, MCP under `mcp_import/`, and `materialize_trains.py` (see reference).

---

## Interactive run configuration (mandatory)

### Step 0 — Canvas URL (always first)

Ask the operator:

> **Paste the release-stats canvas URL** (from the Canvas tab or “Copy link”), **or** the path to the `.canvas.tsx` file.  
> (Recommended default if unsure: `~/.cursor/projects/Users-marek-wyszynski-repo-DOCS/canvases/release-stats.canvas.tsx`)

Then:

1. Resolve to a filesystem path (`render_canvas.resolve_canvas_path` logic: path, `file://`, or URL containing `release-stats` → file under the project `canvases/` folder).
2. If the file **exists** and looks like release-stats (`Release comparison` or `const RELEASES` in the file):
   - **Default mode: enrich only** — update `data/{version}.json`, re-render **in place** to that path. **Do not** run base `gather_release_stats.py` unless `--inventory` shows **required** gaps or the operator explicitly asks for re-gather.
3. If the file **does not exist** — treat as **new canvas**; after data work, `render_canvas.py --canvas "<resolved-path>"` creates it.

Announce: resolved path, whether the canvas already existed, and **enrich-only vs new** default.

Use **AskQuestion** when available; if the operator already pasted a URL in the trigger message, confirm it instead of re-asking.

### Detect situation (after canvas)

| Situation | Recommended default |
|-----------|---------------------|
| Canvas **exists** | **Enrich only** — inventory → fill gaps → re-render same `--canvas` path |
| Canvas missing | New canvas + data pipeline for requested train(s) |
| No `data/{version}.json` for requested train | Base gather **for that train only**, then enrich |
| `data/{version}.json` exists | **`--inventory`** → enrich **missing** blocks only |
| Operator: “refresh everything” | Re-gather with **preserve + merge** (explicit opt-in) |

### Wizard (continued; use **AskQuestion** when available)

1. **Train version(s)** — e.g. `8.77`. (Recommended: one train per run unless batching enrich.)
2. **Goal** — if canvas existed: default **`enrich_missing`** (only offer `full_refresh_base` if they insist). If new canvas/train JSON: `new_train_column`.
3. **Major Release Test Run** — `TC-XXXX` if ambiguous (required for Xray + linked bugs).
4. **Enrichment checklist** (yes/no each; recommend **yes** to all except known-issues Git until post-release):
   - Base gather (cutoff, `bugs.issues`, bug JQL URLs, `known_issues` shell) — **skip when enrich-only and inventory has no required gaps**
   - Xray stats + duration + QA executors + **`test_run.failed_tests[]`** (Testing Board URLs)
   - Production / `release_signal` / `metrics.release_date`
   - Customer-reported SUPPORT block
   - Known issues count verify
   - Known issues Git **breakdown + table rows** (heavy; post-release)
5. **Re-gather** on existing file? → only if operator opted in; then copy to `data/.preserve/{version}.json`, then `merge_release_enrichments.py --write`.
6. **Access** — (Recommended) Atlassian MCP production ONE + production Xray env.
7. **Re-render** — always `render_canvas.py --canvas "<resolved-path>"` and return the **same URL/path** the operator gave.

Confirm plan in one paragraph, then execute.

---

## Execution pipeline

Working directory: repo root (`DOCS`).

### 0. Inventory

```bash
python3 "Release Process/stats/scripts/merge_release_enrichments.py" 8.77 --inventory
```

Fix **required** gaps first (cutoff, test run, bugs, Xray, release date when shipped). **Optional** gaps (customer-reported, known issues) per wizard.

### 1. Preserve (before re-gather)

```bash
mkdir -p "Release Process/stats/data/.preserve"
cp "Release Process/stats/data/8.77.json" "Release Process/stats/data/.preserve/8.77.json"
```

### 2. Base gather

```bash
python3 "Release Process/stats/scripts/gather_release_stats.py" 8.77
python3 "Release Process/stats/scripts/gather_release_stats.py" 8.77 --execution 8.77=TC-6690
```

### 3. Merge after gather

```bash
python3 "Release Process/stats/scripts/merge_release_enrichments.py" 8.77 --write
```

### 4. Xray (feeds comparison table + UsageBar + failed-test links)

```bash
python3 "Release Process/stats/scripts/enrich_xray_stats.py" 8.77 --execution 8.77=TC-6690
```

Writes `test_run.stats`, syncs `metrics.tests_*`, and **`test_run.failed_tests[]`** with Xray Testing Board URLs.

Optional: `refresh_execution_defects.py` if Defect links changed.

### 5. Production date (feeds comparison “days” + stat row)

```bash
python3 "Release Process/stats/scripts/_build_changelogs_oauth.py"
python3 "Release Process/stats/scripts/enrich_release_dates.py" 8.77
```

Or MCP changelog dumps + `fetch_changelog_cache.py` / `_fetch_changelogs_mcp.py`.

### 6. Customer-reported

```bash
python3 "Release Process/stats/scripts/enrich_customer_support.py"
```

If MCP stdio lacks cloud grant: `populate_support_links_batches.py` → MCP batches → `merge_support_link_batch.py` → `enrich_customer_support.py --apply-only`.

### 7. Known issues (optional block)

- MCP count → `known_issues.issue_count_verified`.
- Git breakdown + `issues[]` per [`reference.md`](reference.md) (8.76 group ids).
- Helpers in `gather_release_stats.py`: `known_issues_jql`, `key_in_jql`, `key_in_jql_url`.

### 8. Re-render canvas in place (comparison + all sections)

```bash
python3 "Release Process/stats/scripts/render_canvas.py" --canvas "/path/or/url/from/step-0"
```

Use the **resolved filesystem path** from step 0. Default if omitted: `DEFAULT_CANVAS` in `render_canvas.py`.

### 9. Close out

- Re-run `--inventory`.
- Report: what changed in JSON and that the canvas was refreshed **at the operator’s URL/path**.
- Do not change comparison row definitions unless the operator asks to **extend the top table**.

---

## Enrich-only (default when canvas exists)

1. Step 0 — confirm canvas URL/path; **enrich-only** default.
2. `--inventory` for requested train(s).
3. Wizard subset for listed **required** gaps first, then optional.
4. Steps 4–7 as needed (**skip** base gather unless required).
5. `render_canvas.py --canvas "<path>"`.

Never re-gather without preserve/merge unless the file is new or the operator accepts losing enriched blocks.

---

## Operator preferences (Marek)

- **develop** = only branch for “fix on develop” in known-issues groups.
- Known-issues canvas groups need **BugTable** rows (`breakdown[].issues`), not links alone.
- Prefer verified Jira counts over automation comments for totals.
