# Trinity — metrics and telemetry

English operator reference for **local metrics** (always on in Studio) and **optional BigQuery** upload. Use with pilot scorecards and acceptance-rate evidence.

Related: [BIGQUERY.md](BIGQUERY.md) · [FAQ.md](FAQ.md) · [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md)

---

## Stable run IDs (BigQuery / Looker Studio)

| Entity | `id` format | `label` |
|--------|-------------|---------|
| Reviewer import | `pr-<uuid>` (new imports) or legacy folder name | Renamable display name in Studio |
| Creator batch | `cr-<uuid>` (new imports) or explicit `run_id` in batch JSON | Renamable display name |

Join telemetry on `pipeline_run_id`, `entity_id`, and `entity_type` (`pipeline_run`, `creator_run`). Re-importing the same folder or batch path updates the **same** row; IDs do not change. Events: `pipeline_run_renamed`, `pipeline_run_deleted`, `creator_run_renamed`, `creator_run_deleted`.

---

## Principles

1. **Local first** — SQLite `metric_event` + `telemetry_outbox` under `Trinity/studio/data/`.
2. **Non-blocking** — Studio works with no GCP credentials; failed uploads never stop review or import.
3. **BigQuery ingest** — Studio POSTs the outbox after **every recorded step** when `TRINITY_TELEMETRY_URL` is set. `./Trinity/studio/scripts/start.sh` starts a local ingest on `:8787` when the configured credential file exists.
4. **Looker Studio** — Connect to `qa-coe.trinity` after events exist. Join on `pipeline_run_id`. Filter on `operator_id` / `operator_name` / `product_id` — those are the **human operator and product**, not the GCP service account.

---

## Standard measures

| Measure | Source |
|---------|--------|
| AI-generated test count | `creator_batch_imported` payload `ai_generated_test_count`; `test_cases_total` in summary |
| Accepted after human review | `test_cases_approved`; `test_case_review` events with `human_review_status: approved` |
| Rejected | `test_cases_rejected`; events with `rejected` + `rejection_reason` |
| Acceptance rate | `approved / total` in `/api/telemetry/summary` |
| Rejection reasons | Enum on reject in Studio; aggregated in summary |
| Pipeline funnel | Event types: `review_run_imported`, `review_unit_approved`, `creator_batch_imported`, `test_case_review`, `creator_importer_export`, `importer_plan`, `xray_import_persisted` |
| Automation signal | `test_case_row.automation_fit` / `automation_candidate` — **not** sent to Xray in POC (all Manual in TC); use for acceptance analytics |
| Xray keys in Studio | Importer → **Persist Xray keys** or `POST /api/importer/record-results` |

**Phase timings (per pipeline run):** computed in Studio → top nav **Statistics** (single or compare), or a **Dashboard** run → **Statistics** tab, or `GET /api/runs/{pipeline_run_id}/statistics`. Snapshots persist in SQLite table `pipeline_run_report` for later BigQuery ingest alongside `telemetry_outbox`.

**Studio UI:** All list tables use sortable column headers (`SortableDataTable`). **Compare runs** uses five dropdowns (Run 1 = baseline, runs 2–5 optional); URL param `compare=id1,id2,...`.

**Not yet automated:** baseline comparison without AI (capture manually in scorecard).

---

## Per-run E2E statistics

For each **pipeline run** (Reviewer folder import through Xray), Studio computes a structured report:

| Measure | Source |
|---------|--------|
| Epics reviewed, findings spotted, epics not ready (`not_fit` / `needs_clarification_before_scope_lock`) | Latest `review-payload` per epic |
| Questions marked / posted to epic (suggested vs QA-added) | `studio_qa.decisions` + `jira_comment_post` |
| Epics selected for Creator, TCs drafted / amended / sent to import / Xray keys | `review_unit`, `creator_run`, `test_case_row` |
| **TC creation readiness** (ready / reservations / not ready / unknown) | Latest payload `report.qa_planning_fit` (fallback: `requirements[].qa_planning_fit`, then `review_unit.qa_planning_fit` on import) → `summary` buckets |
| **Compare runs** (2–5) | `GET /api/statistics/compare?runs=id1,id2` — first id = baseline for deltas |
| Phase durations | `metric_event` timestamps + reviewer folder / handoff `generated_at` |
| Product & Jira context | `pipeline_run`, portfolio `creator-handoff.json` |

| Endpoint | Purpose |
|----------|---------|
| `GET /api/runs/{id}/statistics` | Recompute + return report; upsert `pipeline_run_report` |
| `GET /api/runs/{id}/statistics/export` | JSON bundle (`export_kind: pipeline_run_statistics`) for local archive; configured telemetry also syncs the snapshot |
| `GET /api/statistics/compare?runs=id1,id2` | Compare 2–5 runs (comma-separated; first id = baseline for Δ) |

```bash
curl -s "http://127.0.0.1:8765/api/runs/<pipeline_run_id>/statistics" | jq '.summary'
```

---

## Rejection reason enum

| ID | Label |
|----|--------|
| `granularity_too_high` | Granularity too high |
| `granularity_too_low` | Granularity too low |
| `duplicate` | Duplicate |
| `missing_scenarios` | Missing scenarios |
| `wrong_assumptions` | Incorrect assumptions |
| `weak_steps_or_expected` | Weak steps or expected results |
| `requirements_mismatch` | Does not match requirements |
| `maintainability` | Maintainability concerns |
| `other` | Other |

Required when **rejecting** tests in Studio (bulk or single patch).

---

## Studio API

| Endpoint | Purpose |
|----------|---------|
| `GET /api/telemetry/summary` | Rollup for this Studio install |
| `GET /api/telemetry/events?limit=500` | Recent `metric_event` rows |
| `GET /api/telemetry/export` | Full local bundle for scorecard / archive |
| `GET /api/telemetry/rejection-reasons` | Enum for UI |
| `POST /api/telemetry/flush` | Send pending `telemetry_outbox` to BigQuery ingest |
| `POST /api/telemetry/sync` | Recompute every run report, queue snapshots, and flush all pending telemetry |
| `GET /api/runs/{id}/statistics` | Per-run E2E report (see above) |
| `GET /api/runs/{id}/statistics/export` | BigQuery-shaped run report JSON |
| `GET /api/statistics/compare?runs=id1,id2` | Multi-run comparison payload for Statistics → Compare |

Example (Studio API on port 8765):

```bash
curl -s http://127.0.0.1:8765/api/telemetry/summary | jq .
./Trinity/scripts/export-telemetry.sh trinity-telemetry-export.json
```

The export bundle includes `summary` (test-case acceptance), `metric_events`, and **`cursor_usage`** (per `pipeline_run_id` stage breakdown when Cursor hooks recorded sessions).

---

## BigQuery

The GCP service account is only allowed to **write tables**. Identity of the person running Trinity is sent on every event:

| Field | Source |
|-------|--------|
| `operator_id` | `TRINITY_OPERATOR_ID` or `JIRA_EMAIL` |
| `operator_name` | `TRINITY_OPERATOR_NAME`, else the macOS account full name |
| `product_id` / `product_name` | Reviewer handoff / pipeline_run / Creator batch, resolved via `Trinity/creator/config/*.json` |

Add to `Trinity/studio/.env` (never commit). Full setup, permissions,
backfill, verification, and Looker Studio instructions:
[`BIGQUERY.md`](BIGQUERY.md).

```bash
TRINITY_OPERATOR_ID=you@appfire.com
TRINITY_OPERATOR_NAME="Your Name"
BQ_PROJECT=qa-coe
BQ_DATASET=trinity
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/key.json
```

Ingest accepts `POST` JSON: `{"events": [<envelope>, ...]}` with optional `Authorization: Bearer <key>`. Each envelope includes `event_id`, `event_time`, `event_type`, `operator_id`, `operator_name`, `product_id`, `product_name`, `studio_install_id`, `payload`. Run snapshots use `event_type=pipeline_run_report_snapshot` and upsert `pipeline_run_reports` by `pipeline_run_id`.

Manual flush (usually unnecessary — Studio flushes after each step):

```bash
curl -s -X POST http://127.0.0.1:8765/api/telemetry/flush | jq .
```

Complete backfill after adding credentials or repairing run links:

```bash
curl -s -X POST http://127.0.0.1:8765/api/telemetry/sync | jq .
```

---

## Install identity

`Trinity/studio/data/.telemetry_install_id` — stable UUID per machine (gitignored with `data/`). Use with `operator_id` to dedupe operators in BigQuery without storing secrets.
