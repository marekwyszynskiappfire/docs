# Trinity Creator — reference

## `review_ref` (Reviewer handoff)

| Field / check | Rule |
|---------------|------|
| File | Approved `review-payload.json` (Studio export under `Trinity/studio/data/exports/`) |
| Gate `BLOCKED` | Refuse unless `force=true` and QA confirms → `gate_override: true` |
| Readiness `needs_clarification` | Stay in `release_slice_e2e` and the selected `coverage_profile`; document gaps in `coverage_report.warnings` |
| Coverage | Build `coverage_report.matrix[]` from Reviewer ACs/goals/findings — primary driver |
| Staleness | Compare `requirement_fingerprint` in review vs live issue; warn on mismatch |
| Epic | **CR-EPIC-01** — one suite on Epic key; children for traceability only |

## Suite modes

| `suite_mode` | Tests | `test_pattern` |
|--------------|-------|----------------|
| `release_slice_e2e` (default) | `coverage_profile` range, otherwise 3–5 | `journey` only when `policy.allow_atomic` is false |
| `comprehensive_legacy` | Operator-defined | Journey-first; atomic only if catalog explicitly requires |

## Coverage depth

The workspace slider sets `coverage_profile` on the Creator prompt. `suite_mode` stays `release_slice_e2e`.

| Profile | Journeys | What to write |
|---------|----------|---------------|
| `smoke` | 1–2 | Release-blocking happy paths |
| `core` | 3–5 | Main journeys, the main role or permission difference, and one material failure |
| `balanced` | 5–8 | Core coverage plus key states, validation, recovery, and integration behaviour. Studio default |
| `thorough` | 8–12 | Balanced coverage plus boundaries, combinations, data variants, and integration failures |
| `edge` | 12–20 | Thorough coverage plus evidence-backed corner cases |

Write fewer when the requirement cannot support another distinct journey. Do not invent expected results to fill the range. Record the chosen id, the range, `actual_count`, and `omitted` on the suite.

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

## Coverage linkage — `coverage_catalog_id` vs `linked_ac_ids` (CQ-02)

Grill decision: **`coverage_catalog_id` is canonical** when the batch uses the optional product coverage catalog (`config.assets.coverage_catalog`). **`linked_ac_ids`** remains the traceability field to Reviewer ACs / goals (`AC-01`, `GOAL-01`, etc.).

| Field | Role | Required when |
|-------|------|----------------|
| `linked_ac_ids` | Traceability to requirements in `review_ref` | Epic-driven runs (Reviewer matrix) |
| `coverage_catalog_id` | Row id in `coverage-catalog.md` (e.g. `CAT-…`) | Only when catalog-driven generation is enabled for the product |

Rules for authors and tools:

1. Prefer **`linked_ac_ids`** from the Reviewer coverage matrix for Epic runs without a catalog.
2. When both appear, **`coverage_catalog_id`** names the catalog row; **`linked_ac_ids`** must still list the AC/goal keys that row satisfies — they must not contradict.
3. Importer / Studio validation may enrich missing `coverage_catalog_id` from catalog rules; do not treat `linked_ac_ids` as a substitute catalog key.
4. Schema tightening (require catalog id when `linked_ac_ids` present) is **post-pilot**; until then, document mismatches in `coverage_report.warnings`.

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

## Execution tiers, scoring, customer impact, test data (**CR-SCORE-01**)

Scoring is **required** on every drafted test. Golden similarity scores only pick writing references; they do **not** set release priority.

| Field | Rule |
|-------|------|
| `priority_score.customer_harm` | 1–5: who is harmed and how badly if this journey fails |
| `priority_score.likelihood` | 1–5: chance of regression (new/changed code, complexity, known risk) |
| `priority_score.coverage_criticality` | 1–5: how central this journey is to Epic ACs / the gate |
| `priority_score.automation_value` | 1–5: regression ROI — **does not** change `execution_tier` |
| `priority_score.total` | Sum of the three gate factors (3–15); must match the arithmetic |
| `priority_score.derived_tier` | From total: **13–15 P0**, **10–12 P1**, **7–9 P2**, **3–6 P3** |
| `priority_score.rationale` | Why these factor values were chosen |
| `execution_tier` | **Must equal** `derived_tier` |
| `priority` | Canonical only: P0→Highest, P1→High, P2→Medium, P3→Low |
| P3 | `deferrable: true` + `deferrable_rationale` |
| P0 / P1 | `deferrable` must not be true |

Helper: `scripts/score_priority.py --payload suite-payload.json` (add `--in-place` to fill defaults from tier). Shared implementation: `Trinity/shared/priority_score.py`. Populate batch `execution_plan` from the resulting tiers.

See also `golden/v1/style-rules.md` §3.

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
