# Trinity changelog

Distribution semver ([`VERSION`](VERSION)). JSON schema versions are unchanged unless noted.

## Unreleased

- Each Epic has a Generate tests button, so drafting one Epic does not wait for the other reviews to be approved. A suite already on disk is not imported until that file changes. Test titles use the width of the row.
- Importer plans a known Creator run from current approvals, and a saved `importer-payload.json` cannot replace them. A batch that names more than one Epic cannot be written. Cancelling a queued Cursor agent does not start it. The Importer CLI requires the same Reviewer acknowledgement and existing-Xray-key acknowledgement as Studio. The full Importer page opens on the sandbox instance.
- Production Xray credentials no longer stay in the Studio process after a production plan or project list.
- A second Cursor agent for the same target is rejected while one is queued or running.
- BigQuery flush runs on a background thread, so a slow ingest does not hold the Studio database during Reviewer, Creator, or Importer requests.
- A missing Reviewer payload must be acknowledged before Importer execute. A mapping whose Jira site does not match the selected instance cannot execute.
- The Importer CLI requires `--confirm-production PRODUCTION` before a production write or issue-link delete.
- Operator docs and Studio empty-state copy use **Run in Cursor** as the primary path. This pilot is macOS.
- Studio reattaches to a queued or running Cursor agent after a reload. Re-importing a Creator suite clears approval when the case text changes, and drops drafts that left the suite.
- A REST sweep writes under `rest-sweep/` and does not replace a canonical `review-payload.json`. The Q4 backlog generator no longer sets `gate_override` on a BLOCKED review unless `--force-blocked` is passed.
- Removed legacy trees: `The Reviewer/`, `The Creator/`, `TestCaseCreator/`, root `Creator/` (skills live under `Trinity/` only).

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

## Pre-0.2.0

Internal iterations (Reviewer 1.1 payloads, Creator golden v2, Studio MVP). No prior public tags.
