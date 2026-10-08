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

**Does not:** import to Xray, invent requirements, run per-child Epic suites (**CR-EPIC-01**), or embed vendor names in skill text (**CR-AGNOSTIC-01**).

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

1. Load product config; resolve `golden_root` and read `golden/v1/style-rules.md` + 2–3 closest examples from golden (`rag/chunks.jsonl` or `golden/v1/examples/`).
2. Load **`review_ref`**; apply gates in [`reference.md`](reference.md). Build **Epic coverage matrix** from payload (ACs, goals, findings, risks) — not from `coverage-catalog.md` unless config points at a matching catalog.
3. Validate output against `TestCaseDraft.schema.json`.
4. **Epic scope:** child story keys only in `linked_requirement_keys` / traceability.

## Workflow

1. **Pre-flight** — Gate, readiness, fingerprint staleness vs live Jira.
2. **Golden sampling** — From `golden_root`, find 2–3 production tests similar in domain (folder names, labels, summary keywords). Mirror **depth and step style**, not ticket-specific data.
3. **Plan suite** (Test Architect) — Propose **3–5** journey titles mapping to the matrix; operator may adjust before full draft.
4. **Draft journeys** — Each test includes:
   - `test_pattern: journey` (required in `release_slice_e2e`)
   - Up to **15** steps; multi-surface flow (setup → action → verification across relevant UI/API)
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
| No placeholders | No “TBD”, “verify as appropriate” |
| No invented secrets/URLs | Use config redaction patterns |
| P3 | `deferrable: true` + `deferrable_rationale` |
| Count | **3–5** journeys in `release_slice_e2e` without operator approval to exceed |
| Atomic | **Forbidden** when `allow_atomic` is false |

## Trinity Studio

```text
Trinity Studio → Creator → Import batch
  Trinity/creator/samples/demo-story.suite.json
  Trinity/creator/artifacts/{run_id}/suite-payload.json
```

Operator reviews each test (approve / reject / edit). **Marked for Xray import** is separate from approval (Studio Phase 2).
