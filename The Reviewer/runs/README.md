# Reviewer runs

One folder per run: `{YYYY-MM-DD-HHMM}-{ISSUE_KEY}/`, containing `review-payload.json` plus the reports rendered from it by `scripts/render_report.py` at the skill root.

## Runs that predate schema 1.1

These were produced under schema 1.0 with hand-written reports, before the 2026-09-29 run review (`../PERSONA-REVIEW-RUNS.md`). They're kept for history and **don't validate against the current schema**. The renderer won't render them, and a rescan of any of these Epics runs a full scan instead of a delta.

| Run | Why it fails 1.1 |
|---|---|
| `2026-09-28-1500-ONE-354099` | CRITICAL findings and a `BLOCKED` gate on an Epic (PRF-12); no `report` block |
| `2026-09-28-1513-ONE-324524` | No `content_source` on children, since it predates C4; no `report` block |
| `2026-09-28-1542-ONE-181964` | No `content_source` on children, since it predates C4; no `report` block |
| `2026-09-29-0925-ONE-333681` | Valid 1.0; no `report` block |

## Runs on schema 1.1

| Run | Status |
|---|---|
| `2026-09-29-1052-ONE-333681` | Validates and passes `--strict`. Batch re-ranked to all 37 non-Canceled children and re-rendered on 2026-09-29 (PRF-16). |
| `2026-09-29-1151-ONE-354099` | Validates and passes `--strict`. Full schema-1.1 re-run (0 children; two appfireteam Confluence pages via remote links). Supersedes `2026-09-28-1500-ONE-354099` for current spec. |
| `2026-09-29-1151-ONE-181964` | Validates and passes `--strict`. Post-delivery Epic; 19-child batch; both Epic screenshots read via MCP. Supersedes `2026-09-28-1542-ONE-181964`. |
| `2026-09-29-1153-ONE-324524` | Validates and passes `--strict`. Screenshot read via MCP. Supersedes `2026-09-28-1513-ONE-324524`. |

**Planned:** none — all four pilot Epics have a passing 1.1 run.
