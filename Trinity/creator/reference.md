# Trinity Creator — reference

## `review_ref` (Reviewer handoff)

| Field / check | Rule |
|---------------|------|
| File | `review-payload.json` beside Reviewer HTML, or Studio-exported approved payload |
| Gate `BLOCKED` | Refuse unless `force=true` and QA confirms in chat → `gate_override: true` |
| Readiness `needs_clarification` | Default `comprehensive=false`, 5–15 tests |
| Staleness | Compare `requirement_fingerprint` in review vs live issue; warn on mismatch |
| Epic | Creator runs on **Epic key once**; child keys enrich `linked_requirement_keys` only (**CR-EPIC-01**) |
| Skipped review | Allowed; record `review_skipped` + reason — do not fabricate gate status |

Gate table (legacy requirements-review JSON) still applies when `review_ref` uses older shape — map `gate.blocks_test_generation` and `readiness` per [`templates/marek-test-case-creation/requirements-review.sample.json`](templates/marek-test-case-creation/requirements-review.sample.json) when present.

## Execution tiers, customer impact, test data

See the source reference in [`The Creator/Input/Marek/test-case-creation/reference.md`](../../The%20Creator/Input/Marek/test-case-creation/reference.md) (tiers P0–P3, `test_data_required`, deferrable rules). Trinity Creator adopts the same field semantics (**D25–D27**, **CV3**).

## Output filenames

| Artifact | Schema / profile |
|----------|------------------|
| `suite-payload.json` | `TestCaseDraft.schema.json` v1.0 (Studio import today) |
| `suite-report.md` | Human suite (**D21**) |
| `suite-report.html` | Profile A when renderer supports `suite` |

Future: dedicated `suite-payload.schema.json` may supersede the batch shape; until then, Studio and Importer consume **TestCaseDraftBatch** with `tests[]`.

## HTML

- **Suite:** Profile A — collapsible tests, self-contained or portable folder per [`../shared/html-report-guidelines.md`](../shared/html-report-guidelines.md).
- **Triage / analytics tables:** Profile B — see `runs/TC-6504/report/`.

## Config hooks

`config/default.json` mirrors Reviewer: `policy.figma_policy`, `output.artifacts_dir`, `product.id`. Add `policy.code_grounding`: `off` | `required` per product (**CV7**).

## Importer boundary

Creator stops at approved exports. Dry-run and Xray GraphQL submit live in **Trinity Importer** (**CR-IMPORTER-01**).
