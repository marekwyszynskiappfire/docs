# Trinity changelog

Distribution semver ([`VERSION`](VERSION)). JSON schema versions are unchanged unless noted.

## 0.2.0 — 2026-10-13 (`trinity-v0.2.0`)

- Mateusz POC closure: [`SCORECARD.md`](SCORECARD.md), [`MATEUSZ-CRITERIA.md`](MATEUSZ-CRITERIA.md), pilot 1 reveal.js deck.
- Single release version via [`VERSION`](VERSION) + Studio `/api/health`.
- Repo trimmed to runtime essentials; planning docs gitignored ([`.gitignore`](.gitignore)).
- Studio: telemetry export, rejection reasons, Importer execute guards, React UI on 8765 when built.
- Operator docs: FIRST-RUN, MANUAL, ARCHITECTURE; Confluence three-page tree.

## Unreleased

- Studio telemetry: auto-flush after each pipeline step; full backfill via `/api/telemetry/sync`; Creator batches link to Reviewer runs through `review_ref`; envelopes include human `operator_id` / `operator_name` and `product_id` / `product_name`; run snapshots upsert to BigQuery. Local ingest and Looker-ready views: [`BIGQUERY.md`](BIGQUERY.md).
- Removed legacy trees: `The Reviewer/`, `The Creator/`, `TestCaseCreator/`, root `Creator/` (skills live under `Trinity/` only).

## Pre-0.2.0

Internal iterations (Reviewer 1.1 payloads, Creator golden v2, Studio MVP). No prior public tags.
