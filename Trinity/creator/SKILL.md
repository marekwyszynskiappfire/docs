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

## Session parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `suite_mode` | `release_slice_e2e` | **3–5** tests, `test_pattern: journey` only |
| `comprehensive` | `false` | If `true` → `comprehensive_legacy`; still journey-first unless operator requests atomic |
| `scope` / Epic key | from `review_ref` | One Creator run per Epic |
| `run_id` | Epic key or timestamp | |
| `force` | `false` | Bypass Reviewer `BLOCKED` only with QA confirmation → `gate_override: true` |

Policy from config: `release_slice_test_count_min/max`, `allow_atomic` (default **false**), `max_steps_per_journey` (**15**).

## Preconditions

1. Load product config; resolve `golden_root`; read `assets.golden_style` (`style-rules.md`).
2. **Golden sampling (blocking)** — Derive Epic theme keywords from config + early `review_ref` skim; rank golden TCs by similarity; take **max on-theme matches (5–10)**; random-fill only if needed. Read each selected JSON fully **before** matrix drafting.
3. Load **`review_ref`**; apply gates in [`reference.md`](reference.md). Build **Epic coverage matrix** from payload (ACs, goals, findings, risks) — not from `coverage-catalog.md` unless config points at a matching catalog.
4. Validate output against `TestCaseDraft.schema.json` (including `golden_references[]`).
5. **Epic scope:** child story keys only in `linked_requirement_keys` / traceability.

## Workflow

1. **Pre-flight** — Gate, readiness, fingerprint staleness vs live Jira.
2. **Golden sampling (blocking)** — Run `scripts/sample_golden_references.py --golden-root … --keywords … --theme-file … --seed {run_id}-golden`. Read **all** selected tests. Announce `method`, `similarity_count`, `random_fill_count`, and TC keys. Fill `golden_sampling` + `golden_references[]`.
3. **Plan suite** (Test Architect) — Propose **3–5** journey titles mapping to the matrix **and** golden title patterns; operator may adjust before full draft.
4. **Draft journeys** — Write steps **in golden voice** (CR-GOLDEN-01) and **CR-STEP-01** (fully executable prose). Each test includes:
   - `test_pattern: journey` (required in `release_slice_e2e`)
   - Up to **15** steps; target the **depth band** of sampled golden tests; multi-surface flow (setup → action → verification across relevant UI/API)
   - `automation_fit`, `automation_candidate`, `automation_blockers[]`
   - `persona_notes` for all three personas
   - `linked_requirement_keys`, `linked_ac_ids` / goals, `source_quotes` where possible
5. **Coverage report** — Prefer `coverage_report.matrix[]` from Reviewer ACs/goals; `catalog_coverage` only if product catalog loaded.
6. **Write artifacts**

| File | Purpose |
|------|---------|
| `suite-payload.json` | Studio import |
| `suite-report.md` | Human suite (**D21**) |

7. **Handoff** — Studio → Creator → import batch → operator **approve/reject** and mark **fit for Xray import** (Phase 2 UI). **Importer** submits to Xray.

## Quality bar (all personas)

| Rule | Detail |
|------|--------|
| No granular tests | Reject single-control or single-screen scenarios unless Epic scope is trivial |
| No placeholders | No “TBD”, “verify as appropriate”, `{from Q7}`, or “when documented” without a concrete example value in `test_data` |
| CR-STEP-01 | Every step/action + expected result is **self-contained**; repeatable by manual tester or automation without reading other tests, epics, or golden keys |
| No invented secrets/URLs | Use config redaction patterns |
| P3 | `deferrable: true` + `deferrable_rationale` |
| Count | **3–5** journeys in `release_slice_e2e` without operator approval to exceed |
| Steps per journey | Up to **15**; prefer golden-like depth (often **>5** when samples are longer) — do not default every journey to five steps |
| Golden | **CR-GOLDEN-01** — similarity-first **5–10** TCs; random only as fallback; `golden_sampling` + `golden_references[]` |
| Atomic | **Forbidden** when `allow_atomic` is false |

## Trinity Studio

```text
Trinity Studio → Creator → Import batch
  Trinity/creator/samples/demo-story.suite.json
  Trinity/creator/artifacts/{run_id}/suite-payload.json
```

Operator reviews each test (approve / reject / edit). **Marked for Xray import** is separate from approval (Studio Phase 2).
