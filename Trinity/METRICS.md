# Trinity — metrics and telemetry

English operator reference for **local metrics** (always on in Studio) and **optional BigQuery** upload. Supports Mateusz POC scorecard and acceptance-rate evidence.

Related: [POC-TC-GENERATOR.md](POC-TC-GENERATOR.md) · [SCORECARD-TC-GENERATOR.md](SCORECARD-TC-GENERATOR.md) · [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md)

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
3. **BigQuery later** — Set `TRINITY_TELEMETRY_URL` when ingest exists; call flush manually or rely on automatic small batches after each event.
4. **Looker Studio** — Connect to BigQuery after the dataset exists (out of scope until credentials are ready).

---

## Mateusz-aligned measures

| Measure | Source |
|---------|--------|
| AI-generated test count | `creator_batch_imported` payload `ai_generated_test_count`; `test_cases_total` in summary |
| Accepted after human review | `test_cases_approved`; `test_case_review` events with `human_review_status: approved` |
| Rejected | `test_cases_rejected`; events with `rejected` + `rejection_reason` |
| Acceptance rate | `approved / total` in `/api/telemetry/summary` |
| Rejection reasons | Enum on reject in Studio; aggregated in summary |
| Pipeline funnel | Event types: `review_run_imported`, `review_unit_approved`, `creator_batch_imported`, `test_case_review`, `creator_importer_export`, `importer_plan`, `xray_import_persisted` |
| Xray keys in Studio | Importer → **Persist Xray keys** or `POST /api/importer/record-results` |

**Not yet automated:** wall-clock time per phase, baseline comparison without AI (capture manually in scorecard).

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
| `GET /api/telemetry/summary` | Mateusz rollup for this install |
| `GET /api/telemetry/events?limit=500` | Recent `metric_event` rows |
| `GET /api/telemetry/export` | Full local bundle for scorecard / archive |
| `GET /api/telemetry/rejection-reasons` | Enum for UI |
| `POST /api/telemetry/flush` | Send pending `telemetry_outbox` to BigQuery ingest |

Example (Studio API on port 8765):

```bash
curl -s http://127.0.0.1:8765/api/telemetry/summary | jq .
curl -s http://127.0.0.1:8765/api/telemetry/export -o trinity-telemetry-export.json
```

---

## Optional BigQuery (when credentials exist)

Add to `Trinity/studio/.env` (never commit):

```bash
TRINITY_TELEMETRY_URL=https://your-ingest.example/v1/events
TRINITY_TELEMETRY_API_KEY=
TRINITY_OPERATOR_ID=you@appfire.com   # optional; defaults to JIRA_EMAIL
```

Ingest should accept `POST` JSON: `{"events": [<envelope>, ...]}` with optional `Authorization: Bearer <key>`. Each envelope includes `event_id`, `event_time`, `event_type`, `operator_id`, `studio_install_id`, `payload`.

Flush after a pilot:

```bash
curl -s -X POST http://127.0.0.1:8765/api/telemetry/flush | jq .
```

---

## Install identity

`Trinity/studio/data/.telemetry_install_id` — stable UUID per machine (gitignored with `data/`). Use with `operator_id` to dedupe operators in BigQuery without storing secrets.
