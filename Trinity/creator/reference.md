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

## Golden corpus (`golden_root`) — **CR-GOLDEN-01**

Golden is **mandatory writing reference** for every Creator run. `review_ref` does not replace it.

| Config key | Purpose |
|------------|---------|
| `golden_root` | Product-specific extract or `golden/v1` for generic style |
| `assets.golden_style` | `style-rules.md` path (policy) |
| `assets.golden_examples` | v1 example folder when v2 `rag/by-key` is absent |
| `assets.coverage_catalog` | Optional path to `coverage-catalog.md` variant |

Example: `config/bigpicture.json` → `golden/v2/filter-17844-bigpicture-manual`.

### Golden sampling procedure (blocking before draft)

1. **Resolve path** — `config.golden_root` or session override.
2. **Theme keywords** — From Epic summary, goals, findings, and child titles in `review_ref` (e.g. Security, Permission, Risk, OKR, API, UPS, hub, M2M). Pass to `--keywords` and optionally `--theme-file` (short excerpt from review payload).
3. **Rank by similarity** — Score every row in `extraction.md` (title token overlap with keywords/theme). Sort descending.
4. **Select as many similar as possible** — Take top matches until:
   - **10** references (hard cap), or
   - the similar pool is exhausted,
   - but never fewer than **5** when at least 5 tests scored &gt; 0.
   If 12 tests match, use the **top 10**. If 7 match, use **all 7** (7 ≥ 5).
5. **Random fallback only if needed** — If fewer than **5** tests score &gt; 0, or fewer than 5 similar exist but you need 5 references: add **seeded random** keys from the remaining extract until `sample_count` is **5** (or up to 10 if operator requests). Set `method` to `similarity_with_random_fill` and `random_fill_count`.
6. **Pure random** — If **no** title scores &gt; 0 for the keyword set, draw **5–10** with seed (`method`: `random`). Widen keywords once before giving up.
7. **Read full tests** — Open every selected `rag/by-key/TC-*.json` (full `steps[]`).
8. **Draft** — Coverage from `review_ref`; voice from the **selected similar set** (plus any random-fill TCs for step-depth band only). **CR-STEP-01:** each step and expected result is self-contained (no `ONE-*`/`TC-*`, no “repeat step N”, no analogies to other tests).
9. **Record** — `golden_sampling` + `golden_references[]` (equal length). Document in `suite-report.md` § Golden references.

Helper: `scripts/sample_golden_references.py` implements steps 3–6.

### Batch field `golden_sampling`

| Field | Required | Notes |
|-------|----------|-------|
| `method` | Yes | `similarity` \| `similarity_with_random_fill` \| `random` |
| `sample_count` | Yes | 5–10; equals `len(golden_references)` |
| `candidate_pool_size` | Yes | Tests in extract |
| `similarity_count` | Yes | Keys chosen by rank (score &gt; 0) |
| `random_fill_count` | Yes | 0 when no random fill |
| `similarity_pool_size` | No | Count with score &gt; 0 |
| `random_seed` | When random used | `{run_id}-golden` |
| `keywords` | No | Theme terms used for ranking |
| `pool_note` | No | Widen/fallback explanation |

### Batch field `golden_references[]`

| Field | Required | Notes |
|-------|----------|-------|
| `jira_key` | Yes | e.g. `TC-1798` |
| `path` | Yes | Repo-relative path to JSON read |
| `why_selected` | Yes | Thematic fit to Epic (rank / score), or random fill slot |
| `style_cues_applied` | Yes | ≥1 string mirrored from **this** file |

**5–10** entries per batch. Per-test optional: `golden_reference_keys[]`.

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
