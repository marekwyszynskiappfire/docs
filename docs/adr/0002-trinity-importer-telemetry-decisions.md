# ADR 0002: Importer behaviour and telemetry (working session 2026-10-12)

## Status

Accepted (2026-10-12)

## Context

Interactive product review and pilot sign-off require clear Importer rules, optional BigQuery telemetry later, and local evidence in the meantime.

## Decisions

### Importer and handoff

| ID | Decision |
|----|----------|
| **IQ-01** | When the operator overrides Jira **project key**, Studio resolves **`project.id`** via Jira REST on plan; **execute_ready** is false if mapping `project.id` conflicts with resolved id. *(Implemented in `build_import_plan`.)* |
| **IQ-02** | **Production** Xray import requires **typed confirmation** (type `PRODUCTION`) plus a visible badge before plan preview and copy prompt. *(Implemented in Studio Importer UI.)* |
| **IQ-03** | **Official policy:** Xray import **production-only**; sandbox for Jira read/plan; document in GUIDE. |
| **IQ-04** | **`Trinity/shared/validate_for_xray.py`** — legacy Xray rules + `TestCaseDraft` JSON Schema. |
| **IQ-16 / PQ-04** | **Soft warn** when `review_ref` Reviewer readiness is not green; operator must **acknowledge** in Studio and re-preview plan before execute_ready (no hard block). *(Implemented in Importer plan + UI.)* |
| **RQ-01** | **`creator/config` → `importer.*`**; Studio `GET /api/importer/defaults`. |
| **IQ-08** | **Warn** on deferrable tests in export preflight. |
| **IQ-17** | **Lint** (warn) emails/sensitive URLs before export. |
| **PQ-02** | **PM-safe summary** on import plan + Cursor prompt. |
| **IQ-09** | **QA lead per product line** owns mapping JSON ([mappings/README.md](../../Trinity/importer/config/mappings/README.md)). |

### Telemetry

| ID | Decision |
|----|----------|
| **Local first** | Every Studio run records **`metric_event`** rows in SQLite; optional **`telemetry_outbox`** for BigQuery-shaped payloads. |
| **Non-blocking** | Missing `TRINITY_TELEMETRY_URL` or failed upload **never** blocks Reviewer, Creator, Importer, or Studio. |
| **BigQuery later** | When credentials exist, `POST /api/telemetry/flush` (or automatic flush after events) sends outbox rows to the configured ingest URL. Looker Studio is out of scope until BQ exists. |
| **Review metrics** | Acceptance, rejection counts, and **rejection reason** enum are captured on human review; see [`Trinity/METRICS.md`](../../Trinity/METRICS.md). |

## Consequences

- Operator docs: [`Trinity/FIRST-RUN.md`](../../Trinity/FIRST-RUN.md), [`Trinity/MANUAL.md`](../../Trinity/MANUAL.md), [`Trinity/FAQ.md`](../../Trinity/FAQ.md), [`Trinity/METRICS.md`](../../Trinity/METRICS.md), [`Trinity/CURSOR-COST.md`](../../Trinity/CURSOR-COST.md).
- Studio: telemetry export (`GET /api/telemetry/export`) includes QA summary + **`cursor_usage`** rollup; rejection reasons on bulk reject; **IQ-02** production guard; **IQ-05** `POST /api/importer/record-results`.
- Pilot review (2026-10-12): sign-off via evidence + presentation; **no BigQuery required** for pilot; Importer redaction and idempotency hardened in Studio post-pilot; Reviewer gate **soft** (IQ-16); optional **Cursor cost** via hooks + Admin API backfill.
- Studio parity (post-grill): portfolio rollup, child inventory + status banner, classifications banner, Reviewer **Profile A HTML** via API, Dashboard **`context_loaded`** alerts.
- P2 IQ-10–IQ-15 implemented 2026-10-12. Further work tracked in GitHub Issues (`docs/agents/issue-tracker.md`).
