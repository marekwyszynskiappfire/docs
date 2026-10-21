# Trinity contracts (handoff)

Canonical schemas live in skill folders; this page indexes them.

| Artifact | Schema / doc |
|----------|----------------|
| Reviewer decision | [`reviewer/requirements-testability-spec.md`](reviewer/requirements-testability-spec.md) — default verdict `testable_now` / `testable_with_clarifications` / `not_testable_yet`. `checklist.md` is deep audit only. |
| Reviewer output | [`reviewer/schemas/review-payload.schema.json`](reviewer/schemas/review-payload.schema.json) — `report.testability_verdict` and `report.testability_reasons` when the Reviewer wrote the decision. |
| Pipeline manifest | [`studio/schemas/pipeline-manifest.schema.json`](studio/schemas/pipeline-manifest.schema.json) — portfolio entry; references per-Epic `review-payload.json` by path and `content_sha256`. Import: `POST /api/import/pipeline-manifest`. Unchanged payload hashes reuse the pipeline run and do not add a review revision. Response `workspace_path` is `/workspace/{pipeline_run_id}`. |
| Cursor handoff | Studio table `cursor_handoff`, prompt version `1`. Statuses: `awaiting_cursor`, `output_detected`, `invalid_output`, `imported`, `stale_output`. A missing expected file while `awaiting_cursor` is waiting, not a failure. |
| Reviewer portfolio run config | [`reviewer/schemas/run-config.schema.json`](reviewer/schemas/run-config.schema.json) → `reviewer/config/runs/{portfolio_id}.json` |
| Trinity personas | [`personas/`](personas/) — editable role prompts (Reviewer loads via run config) |
| QA layer on payload | `studio_qa` (see [`studio/web/src/types/studio-qa.ts`](studio/web/src/types/studio-qa.ts)) |
| Epic feedback export | `{jira_key}-epic-feedback.json` (items with `send_to_epic`) |
| Creator input | `review_ref` → approved `review-payload.json` ([`reviewer/reference.md`](reviewer/reference.md)) |
| Test batch | Creator `TestCaseDraft` schema under `creator/schemas/` when promoted |
| Importer handoff | Studio `importer-payload.json` (`export_kind`: `creator_importer_handoff`) |
| Importer operator config | [`importer/schemas/import-operator-config.schema.json`](importer/schemas/import-operator-config.schema.json) |
| HTML reports | [`shared/html-report-guidelines.md`](shared/html-report-guidelines.md) |
