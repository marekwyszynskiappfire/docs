# Trinity Creator — reference

## `review_ref` (Reviewer handoff)

| Field / check | Rule |
|---------------|------|
| File | Approved `review-payload.json` (Studio export under `Trinity/studio/data/exports/`) |
| Gate `BLOCKED` | Refuse unless `force=true` and QA confirms → `gate_override: true` |
| Readiness `needs_clarification` | Stay in `release_slice_e2e`; 3–5 journeys; document gaps in `coverage_report.warnings` |
| Coverage | Build `coverage_report.matrix[]` from Reviewer ACs/goals/findings — primary driver |
| Staleness | Compare `requirement_fingerprint` in review vs live issue; warn on mismatch |
| Epic | **CR-EPIC-01** — one suite on Epic key; children for traceability only |

## Suite modes

| `suite_mode` | Tests | `test_pattern` |
|--------------|-------|----------------|
| `release_slice_e2e` (default) | 3–5 | `journey` only when `policy.allow_atomic` is false |
| `comprehensive_legacy` | Operator-defined | Journey-first; atomic only if catalog explicitly requires |

## Golden corpus (`golden_root`)

| Config key | Purpose |
|------------|---------|
| `golden_root` | Product-specific extract or `golden/v1` for generic style |
| `assets.golden_style` | `style-rules.md` path |
| `assets.golden_examples` | Optional v1 example folder |
| `assets.coverage_catalog` | Optional path to `coverage-catalog.md` variant |

Example: `config/bigpicture.json` → `golden/v2/filter-17844-bigpicture-manual`.

Use `rag/chunks.jsonl` or `extraction.json` for depth; use v1 examples for structure when v2 is absent.

## Automation fields (per test)

| Field | Values |
|-------|--------|
| `automation_fit` | `full` \| `partial` \| `manual_only` |
| `automation_candidate` | `true` for `full` or automatable `partial` happy path |
| `automation_blockers` | e.g. `dynamic_dom_ids`, `no_api_for_setup`, `third_party_widget` — `[]` when `full` |

## Personas

Fixed trio for v1 (no Creator run-config CRUD yet):

- `creator-expert-qa-engineer.md`
- `creator-test-architect.md`
- `creator-expert-test-automation-engineer.md`

Record paths in batch `persona_files[]`.

## Execution tiers, customer impact, test data

Same semantics as legacy test-case-creation reference (P0–P3, `test_data_required`, deferrable rules). See tiers in `golden/v1/style-rules.md`.

## Output filenames

| Artifact | Consumer |
|----------|----------|
| `suite-payload.json` | Trinity Studio Creator import |
| `suite-report.md` | Human review |

## Studio operator workflow (contract)

| State | Meaning |
|-------|---------|
| `human_review_status` | `pending` → `edited` → `approved` \| `rejected` |
| `marked_for_xray_import` | Operator flag — only when `approved` |

**Export:** Studio → Creator run → **Export for Importer** writes  
`Trinity/studio/data/exports/creator/{run_id}/importer-payload.json`  
(tests where approved + marked). **Importer** consumes that file (roadmap).

Creator sets draft content only; Studio owns approval and import marking.

## Importer boundary

No Xray GraphQL from Creator (**CR-IMPORTER-01**).
