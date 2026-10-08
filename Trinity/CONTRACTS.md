# Trinity contracts (handoff)

Canonical schemas live in skill folders; this page indexes them.

| Artifact | Schema / doc |
|----------|----------------|
| Reviewer output | [`reviewer/schemas/review-payload.schema.json`](reviewer/schemas/review-payload.schema.json) |
| Reviewer portfolio run config | [`reviewer/schemas/run-config.schema.json`](reviewer/schemas/run-config.schema.json) → `reviewer/config/runs/{portfolio_id}.json` |
| Trinity personas | [`personas/`](personas/) — editable role prompts (Reviewer loads via run config) |
| QA layer on payload | `studio_qa` (see [`studio/web/src/types/studio-qa.ts`](studio/web/src/types/studio-qa.ts)) |
| Epic feedback export | `{jira_key}-epic-feedback.json` (items with `send_to_epic`) |
| Creator input | `review_ref` → approved `review-payload.json` ([`reviewer/reference.md`](reviewer/reference.md)) |
| Test batch | Creator `TestCaseDraft` schema under `creator/schemas/` when promoted |
| HTML reports | [`shared/html-report-guidelines.md`](shared/html-report-guidelines.md) |
