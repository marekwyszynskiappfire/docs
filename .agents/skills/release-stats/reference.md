# Release stats — reference

Golden train: `Release Process/stats/data/8.76.json`.

Canvas: operator-specific `.canvas.tsx` (ask URL on every skill run). Default:

`~/.cursor/projects/Users-marek-wyszynski-repo-DOCS/canvases/release-stats.canvas.tsx`

Re-render in place: `python3 "Release Process/stats/scripts/render_canvas.py" --canvas "<path-or-url>"`.

If that file already exists → **enrich** train JSON + re-render; do not re-gather unless inventory requires it.

## Canvas ↔ JSON map

| Canvas UI | JSON / script |
|-----------|----------------|
| Comparison table columns | One column per `data/{version}.json` |
| Comparison row values | `metrics.*` (+ view-model fields in `render_canvas.view_model`) |
| Cloud {version} stat row | `cutoff`, `metrics`, `production.release_signal`, `test_run.stats.timing`, customer count |
| UsageBar / test stats | `test_run.stats` (Xray) |
| Failed tests table | `test_run.failed_tests[]`, `test_run.failed_tests_source` |
| Pie chart | `metrics.bugs_by_priority` from cut-off bugs |
| Linked / Other BugTables | `test_run.defect_keys` + `bugs.issues`; JQL in `bugs.slices` |
| CustomerBugTable | `bugs.customer_reported.issues` |
| Known issues groups | `known_issues.breakdown[]` + `issues[]` |
| Cloud versions table | `production.versions`, `production.release_signal` |

Adding **`8.77.json`** and re-rendering updates **both** the comparison table and a new bottom section — no separate “register train” step.

## `metrics` contract (comparison + future analytics)

Populated by `gather_release_stats.py` and enrich scripts. Fields used in the top table today:

| Field | Meaning |
|-------|---------|
| `cutoff_date` | Preprod cut-off (ISO date) |
| `release_date` / `released` / `days_in_preprod` | Production signal |
| `tests_total` … `tests_todo` | Major Release Test Run (Xray) |
| `test_run_duration_days` | Weekdays first→last test status change |
| `test_run_first_status_change` / `test_run_last_status_change` | ISO timestamps |
| `bugs_total` | Cut-off-scoped bug count |
| `bugs_found_by_test_run` | `len(defect_keys)` |
| `bugs_other_since_cutoff` | Cut-off bugs not linked from TC run |
| `bugs_customer_reported` | SUPPORT-linked count |
| `bugs_by_priority` | Pie chart |
| `qa_engineers_count` | Distinct Xray executors |

Extend comparison rows only by changing `render_canvas.py` **and** ensuring gather/enrich sets the new metric.

## Paths and scripts

| Path | Role |
|------|------|
| `Release Process/stats/data/{version}.json` | Single train source of truth |
| `Release Process/stats/data/.preserve/{version}.json` | Pre–re-gather snapshot |
| `gather_release_stats.py` | Base gather (**overwrites** file) |
| `merge_release_enrichments.py` | `--inventory`, merge after gather |
| `enrich_xray_stats.py` | Test run counts, timing, QA ids |
| `enrich_release_dates.py` | `release_signal`, `metrics.release_date` |
| `enrich_customer_support.py` | `bugs.customer_reported` |
| `refresh_execution_defects.py` | Refresh `defect_keys` |
| `apply_qa_user_cache.py` | Display names for QA stat |
| `render_canvas.py` | Full canvas including comparison table |
| `materialize_trains.py` / `mcp_import/` | When Jira REST 404 |
| `Trinity/studio/.env.production` | Production Xray OAuth |

## Train JSON blocks (create vs enrich)

| Block | Created by | Enriched by |
|-------|------------|-------------|
| `cutoff`, `preprod_versions`, `bugs.issues`, bug JQL | gather or MCP + `materialize_trains` | Re-gather |
| `test_run`, `defect_keys` | gather / `--execution` | `refresh_execution_defects.py` |
| `test_run.stats`, `metrics.tests_*`, timing, QA | — | `enrich_xray_stats.py` |
| `test_run.failed_tests[]` (Testing Board URLs) | — | `enrich_xray_stats.py` |
| `production.release_signal`, release dates | — | changelogs + `enrich_release_dates.py` |
| `bugs.customer_reported` | — | MCP + `enrich_customer_support.py` |
| `known_issues` (jql, url) | gather | MCP count |
| `known_issues.breakdown[]` | Agent + GitHub + MCP | Optional; refresh `issues[]` |

Gather **replaces** the entire JSON. Use `.preserve/` + `merge_release_enrichments.py --write` after re-gather.

## MCP import path (REST 404)

1. `fetch_mcp_import.py` / agent saves pages under `mcp_import/_fetch/{version}/`
2. `compose_mcp_import.py`, `materialize_trains.py` → `data/{version}.json`
3. Continue enrich pipeline + `render_canvas.py`

Production ONE: **plugin-atlassian-atlassian** or **user-atlassian_appfire**.

## Known issues JQL

```
project = ONE AND affectedVersion = "{preprod}" AND status NOT IN (Done, Canceled)
AND issuetype = Bug AND "Bug Type[Dropdown]" = Internal
```

Saved filters: **Known issues after release {version}**.

## Git breakdown (optional; 8.76)

| Group `id` | Rule |
|------------|------|
| `on_develop` | Fix on `AppfireBigPicture/ppm` **develop** |
| `global_teams_work_branch` | `work/ONE-301061/global-teams-move-feature-branch` |
| `ado_poc_work_branch` | `work/ONE-336447/azuredevops-poc` |
| `in_flight` | Open PR; document target branch |
| `no_github_fix` | No ppm merge by issue key |

Each group: `keys`, `count`, `jql`/`url` (`key in (...)`), `issues[]` for BugTable.

## Inventory

```bash
python3 "Release Process/stats/scripts/merge_release_enrichments.py" 8.77 --inventory
```

Required vs optional gaps are labeled in script output.
