---
name: trinity-creator
description: >-
  Generates 3–5 end-to-end journey test scenarios per Epic from Reviewer review_ref,
  styled against per-product golden corpora; automation_fit tagging; persona lenses.
  Does not import to Xray (Studio review + Trinity Importer). Epic-only scope.
disable-model-invocation: true
---

# Trinity Creator

Draft **e2e journey test cases** from an approved **Reviewer** handoff. Default output is **3–5 scenarios** that maximize Epic coverage — not granular button-level tests. Output is **JSON batch** + **Markdown** suite report.

**Does not:** import to Xray, invent requirements, run per-child Epic suites (**CR-EPIC-01**), embed vendor names in skill text (**CR-AGNOSTIC-01**), or draft tests from `review_ref` alone without reading production golden tests (**CR-GOLDEN-01**).

## Personas (load every run)

Read all three files under `{trinity_root}/personas/` and apply them to every test:

| File | Lens |
|------|------|
| `creator-expert-qa-engineer.md` | Customer outcomes, data, traceability → `persona_notes.qa_engineer` |
| `creator-test-architect.md` | Suite shape, coverage matrix, no overlap → `persona_notes.test_architect` |
| `creator-expert-test-automation-engineer.md` | `automation_fit`, blockers → `persona_notes.automation_engineer` |

Summarize each persona in one line to the operator before drafting.

## Paths (`{skill_root}` = this folder, `{trinity_root}` = `Trinity/`)

| Resource | Path |
|----------|------|
| Batch schema | `{skill_root}/schemas/TestCaseDraft.schema.json` |
| Priority scoring | `{trinity_root}/shared/priority_score.py` + `{skill_root}/scripts/score_priority.py` |
| Product config | `{skill_root}/config/<product>.json` → `default.json` |
| Golden root | `config.golden_root` (e.g. BigPicture → `golden/v2/filter-17844-bigpicture-manual`) |
| Style rules | `config.assets.golden_style` or `golden/v1/style-rules.md` |
| Optional product catalog | `config.assets.coverage_catalog` — **not** default for Epic runs |
| `review_ref` template | `{skill_root}/templates/marek-test-case-creation/` |
| Reference | [`reference.md`](reference.md) |
| Demo batch | `{skill_root}/samples/demo-story.suite.json` |
| Artifacts | `{skill_root}/{config.output.artifacts_dir}/{run_id}/` |

Announce `product_id`, `golden_root`, `run_id`, and `suite_mode` at run start.

## Golden as writing reference (**CR-GOLDEN-01** — mandatory)

`style-rules.md` sets policy; **production golden tests set voice, depth, and step shape**. Every run must treat golden as a **writing reference**, not optional context.

| Rule | Detail |
|------|--------|
| **Read before draft** | Select **5–10** full golden tests from `golden_root` (see [`reference.md`](reference.md) § Golden sampling) and read every selected `rag/by-key/TC-*.json` **before** proposing journey titles or writing steps. |
| **Similarity first** | Rank tests in `extraction.md` by **thematic closeness** to the Epic (keywords from `review_ref` summary, goals, findings, module names). Take **as many top matches as possible** (cap **10**, at least **5** when the corpus has enough on-theme tests). |
| **Random fallback** | Only when **&lt;5** similar tests exist: fill remaining slots with a **seeded random** draw from the rest of the extract (`method`: `similarity_with_random_fill`). If **no** keyword overlap at all, use seeded **random** 5–10 (`method`: `random`). |
| **Helper** | `{skill_root}/scripts/sample_golden_references.py` — pass `--keywords` from Epic theme and optional `--theme-file` (review excerpt). |
| **Sample size** | `sample_count` = `len(golden_references)` (**5–10**). Prefer **all** similar matches up to 10, not a fixed count. |
| **Sources (priority)** | `rag/by-key/TC-*.json` → `rag/chunks.jsonl` / `extraction.md` index → `assets.golden_examples` (v1) when v2 is missing. |
| **Match depth** | Step count per journey should be **in the same band** as the sampled tests for that domain (often **6–15** for BigPicture manual journeys — not a fixed 5). `release_slice_e2e` limits **journey count** (3–5), not steps per journey (`max_steps_per_journey`). |
| **Match style** | Mirror title patterns (e.g. `Feature area - …`), navigation phrasing, separate **test data** in steps where golden does, `boxName` / role setup when journeys use dedicated boxes. |
| **No copy-paste** | Reuse structure and tone; do **not** copy ticket-specific data, passwords, or unrelated module flows from samples. |
| **Self-contained steps (CR-STEP-01)** | Steps and `expected_result` must stand alone: **no** Jira keys (`ONE-*`, `TC-*`), **no** “as in step N”, **no** analogies to other tests (“like TC-…”, “per PRD/Q7”), **no** “works as described in …”. Golden TCs inform the author only — **never** appear in step text. Use concrete UI labels, messages, HTTP codes, and data values. |
| **Record provenance** | Populate `golden_sampling` (`method`, `similarity_count`, `random_fill_count`, `sample_count`, `keywords`, `random_seed` when random used) and `golden_references[]` — one entry per TC with paths, similarity rationale, and style cues applied. List in `suite-report.md`. |
| **Stop** | If `golden_root` is missing, empty, or no test is plausibly on-domain after search → **stop** and ask the operator to refresh the extract or name fallback keys — do not invent generic QA prose. |

`review_ref` drives **what** to cover; golden drives **how** it reads in Xray.

## Session inputs

| Input | Mandatory? | Notes |
|-------|------------|-------|
| **`review_ref`** | **Yes** when Studio handoff | Approved `review-payload.json` — primary source for coverage matrix |
| **Requirement source** | **Yes** | Epic key from handoff or explicit `scope` |
| **`product`** | No | Config id (`bigpicture`, `default`, …) |
| **`golden_root` override** | No | Overrides `config.golden_root` for one run |
| **`existing_xray_extract`** | No | Extra dedupe path under `golden_root` |
| **External context** | No | Per templates |

If `review_ref` is missing outside a deliberate dry-run, stop and ask — set `review_skipped` + reason only when operator confirms.

### Analytics linkage contract

Every `suite-payload.json` must retain:

- `product_id` from the resolved Creator config;
- the exact `review_ref` path when Reviewer handoff was used;
- `pipeline_run_id` when the Studio/Reviewer handoff supplies its `run_id`.

Do not replace `review_ref` with a copied temporary file or omit these fields
from the final payload. Studio uses them to join Creator and Importer activity to
the original Reviewer run before telemetry is synchronized to BigQuery. The
skill itself never writes BigQuery and never reads GCP credentials.

## Session parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `suite_mode` | `release_slice_e2e` | Journey tests. Count follows `coverage_profile` when the handoff sets one; otherwise **3–5** |
| `coverage_profile` | from the workspace slider | `smoke` 1–2, `core` 3–5, `balanced` 5–8, `thorough` 8–12, `edge` 12–20. Fewer tests are valid when evidence runs out. Do not exceed the maximum. |
| `comprehensive` | `false` | If `true` → `comprehensive_legacy`; still journey-first unless operator requests atomic |
| `scope` / Epic key | from `review_ref` | One Creator run per Epic |
| `run_id` | Epic key or timestamp | |
| `force` | `false` | Bypass Reviewer `BLOCKED` only with QA confirmation → `gate_override: true` |

Policy from config: `release_slice_test_count_min/max` applies only when the handoff has no `coverage_profile`. `allow_atomic` (default **false**), `max_steps_per_journey` (**15**). A coverage profile changes how many journeys to write. It does not lengthen steps and it does not change priority scoring.

## Preconditions

1. Load product config; resolve `golden_root`; read `assets.golden_style` (`style-rules.md`).
2. **Golden sampling (blocking)** — Derive Epic theme keywords from config + early `review_ref` skim; rank golden TCs by similarity; take **max on-theme matches (5–10)**; random-fill only if needed. Read each selected JSON fully **before** matrix drafting.
3. Load **`review_ref`**; apply gates in [`reference.md`](reference.md). Build **Epic coverage matrix** from payload (ACs, goals, findings, risks) — not from `coverage-catalog.md` unless config points at a matching catalog.
4. Validate output against `TestCaseDraft.schema.json` (including `golden_references[]`).
5. **Epic scope:** child story keys only in `linked_requirement_keys` / traceability.

## Workflow

1. **Pre-flight** — Gate, readiness, fingerprint staleness vs live Jira. Read `policy.test_data_isolation` from product config (`shared_sandbox`, `dedicated_tenant`, `production_readonly`). If unset, still document isolation in each test’s prerequisites (PQ-03).
2. **Golden sampling (blocking)** — Run `scripts/sample_golden_references.py --golden-root … --keywords … --theme-file … --seed {run_id}-golden`. Read **all** selected tests. Announce `method`, `similarity_count`, `random_fill_count`, and TC keys. Fill `golden_sampling` + `golden_references[]`.
3. **Plan suite** (Test Architect) — Propose journey titles for the handoff `coverage_profile` (Studio default **balanced**, 5–8). Without a profile, propose **3–5**. Map titles to the matrix and golden title patterns. Stay under the profile maximum. Stop early when the requirement cannot support another distinct journey, and list that area in `coverage_profile.omitted`.
4. **Draft journeys** — Write steps **in golden voice** (CR-GOLDEN-01) and **CR-STEP-01** (fully executable prose). Score every test (**CR-SCORE-01**) before writing the batch. Each test includes:
   - `test_pattern: journey` (required in `release_slice_e2e`)
   - Up to **15** steps; target the **depth band** of sampled golden tests; multi-surface flow (setup → action → verification across relevant UI/API)
   - `priority_score` (harm, likelihood, coverage_criticality, automation_value) → `execution_tier` + canonical `priority` (**CR-SCORE-01**)
   - `automation_fit`, `automation_candidate`, `automation_blockers[]`
   - `persona_notes` for all three personas
   - `linked_requirement_keys`, `linked_ac_ids` / goals, `source_quotes` where possible
5. **Coverage report** — Prefer `coverage_report.matrix[]` from Reviewer ACs/goals; `catalog_coverage` only if product catalog loaded.
6. **Write artifacts** — preserve the analytics linkage contract above in
   `suite-payload.json`.

| File | Purpose |
|------|---------|
| `suite-payload.json` | Studio import |
| `suite-report.md` | Human suite (**D21**) |
| `suite-report/` | Profile B HTML (faceted table + steps) — Studio export or `scripts/build_suite_report.py` |

7. **Handoff** — Write `suite-payload.json`. The workspace imports that file and the operator approves or rejects each test there, then marks **Send to Xray**. **More → Creator** is the fallback import. The workspace **Plan Xray import** writes to Xray after a dry-run.

### Operator close-out (required in every reply)

Always give the operator a **single artifacts root** and the **import rule**:

| Scope | Artifacts root | Import |
|-------|----------------|--------|
| One Epic | `{skill_root}/{config.output.artifacts_dir}/{run_id}/suite-payload.json` (or `{run_id}/{EPIC_KEY}/` when nested) | The workspace imports this file |
| Multi-epic / portfolio | `{skill_root}/{config.output.artifacts_dir}/{portfolio_id}/` with `{EPIC_KEY}/suite-payload.json` per epic | **One file per Epic** — no combined batch. The workspace imports each file it is watching |

State explicitly: **“Leave the suite files in place. Studio imports each `suite-payload.json` on the workspace. There is no single merged payload.”** Point to [`artifacts/README.md`](artifacts/README.md). If `index.json` exists under the portfolio folder, say it is a catalog only. **More → Creator** is only for a file the workspace did not pick up.

## Quality bar (all personas)

| Rule | Detail |
|------|--------|
| No granular tests | Reject single-control or single-screen scenarios unless Epic scope is trivial |
| No placeholders | No “TBD”, “verify as appropriate”, `{from Q7}`, or “when documented” without a concrete example value in `test_data` |
| CR-STEP-01 | Every step/action + expected result is **self-contained**; repeatable by manual tester or automation without reading other tests, epics, or golden keys |
| No invented secrets/URLs | Use config redaction patterns |
| Test data isolation | Match `policy.test_data_isolation`; prerequisites must name tenant/user pool and forbid cross-worker clashes |
| P3 | `deferrable: true` + `deferrable_rationale` |
| CR-SCORE-01 | Required `priority_score`; tier from total (P0=13–15 … P3=3–6); `priority` mapping P0=Highest, P1=High, P2=Medium, P3=Low |
| Count | Follow `coverage_profile` min–max when the handoff sets one (default **balanced**, 5–8). Otherwise **3–5**. Do not exceed the maximum. Fewer journeys are required when the requirement runs out of distinct, evidence-backed cases. Record `coverage_profile` on the suite, including `actual_count` and `omitted`. |
| Steps per journey | Up to **15**; prefer golden-like depth (often **>5** when samples are longer) — do not default every journey to five steps |
| Golden | **CR-GOLDEN-01** — similarity-first **5–10** TCs; random only as fallback; `golden_sampling` + `golden_references[]` |
| Atomic | **Forbidden** when `allow_atomic` is false |

## Trinity Studio

```text
Workspace imports, one file per Epic:
  Trinity/creator/artifacts/{portfolio_id}/{EPIC_KEY}/suite-payload.json
  Trinity/creator/artifacts/{run_id}/suite-payload.json   # single-epic run
More → Creator is the fallback, including:
  Trinity/creator/samples/demo-story.suite.json
```

Operator reviews each test on the workspace (approve / reject / edit). **Send to Xray** is separate from approval. Each file creates or updates one **Creator run** — plan **one suite per Epic key**, not one file for the whole portfolio.
