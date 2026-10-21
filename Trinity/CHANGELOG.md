# Trinity changelog

Distribution semver ([`VERSION`](VERSION)). JSON schema versions are unchanged unless noted.

## 0.3.0 — 2026-10-21

- Studio launches persisted local Cursor SDK agents for Reviewer, Creator, and
  Importer, with queued/running/final state, cancel/retry, restart recovery, and
  **Copy prompt** fallback.
- Workspace recovery now lists all Creator runs, imports off-workspace Epic
  suites, and previews safe Xray plans directly from `importer-payload.json`.
- Importer agent launch recomputes the server-owned plan and preserves
  production confirmation, Reviewer, redaction, idempotency, and one-Epic
  write gates.
- BigQuery is a pre-UAT release gate: retry and report-upsert coverage, live
  sync verification, and explicit non-blocking behavior when credentials or
  ingest are unavailable.
- Operator, setup, first-run, prompt, test, and UAT guidance now use **Run in
  Cursor** as the primary workflow.
- Studio navigation keeps **Personas** and **Statistics** in the top bar.

## 0.2.0 — 2026-10-13 (`trinity-v0.2.0`)

- Mateusz POC closure: [`SCORECARD.md`](SCORECARD.md), [`MATEUSZ-CRITERIA.md`](MATEUSZ-CRITERIA.md), pilot 1 reveal.js deck.
- Single release version via [`VERSION`](VERSION) + Studio `/api/health`.
- Repo trimmed to runtime essentials; planning docs gitignored ([`.gitignore`](.gitignore)).
- Studio: telemetry export, rejection reasons, Importer execute guards, React UI on 8765 when built.
- Operator docs: FIRST-RUN, MANUAL, ARCHITECTURE; Confluence three-page tree.

## Unreleased

- Removed legacy trees: `The Reviewer/`, `The Creator/`, `TestCaseCreator/`, root `Creator/` (skills live under `Trinity/` only).

## Pre-0.2.0

Internal iterations (Reviewer 1.1 payloads, Creator golden v2, Studio MVP). No prior public tags.
