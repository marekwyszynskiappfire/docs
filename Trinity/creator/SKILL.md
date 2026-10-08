---
name: trinity-creator
description: >-
  Generates a structured test suite (Markdown + JSON batch) from Jira requirements,
  anchored to an optional Reviewer review_ref. Release-slice sizing (5–15 tests) when
  review readiness needs clarification; journey + atomic patterns; P0–P3 tiers;
  coverage reporting. Does not import to Xray (use Trinity Importer after Studio
  approval). Use after The Reviewer or with an approved review-payload.json.
disable-model-invocation: true
---

# Trinity Creator

Draft **QA-ready test cases** from requirement context. Output is **machine JSON** plus human **Markdown** — the model does not hand-write HTML report shells (see [`../shared/html-report-guidelines.md`](../shared/html-report-guidelines.md); suite reports = Profile A when a renderer exists).

**Does not:** import to Xray, invent requirements, run per-child Epic test plans (epic-only scope — **CR-EPIC-01**), or embed product-specific vendor names in skill text (**CR-AGNOSTIC-01**).

Decision memory: maintainer-local [`../reviewer/DECISIONS.md`](../reviewer/DECISIONS.md) § Creator resolutions — Part 2.

## Paths (`{skill_root}` = this folder)

| Resource | Path |
|----------|------|
| Test batch schema (Studio import) | `{skill_root}/schemas/TestCaseDraft.schema.json` |
| Golden style + examples | `{skill_root}/golden/v1/` |
| Domain coverage catalog (optional) | `{skill_root}/coverage-catalog.md` |
| Templates (review gate, external context) | `{skill_root}/templates/marek-test-case-creation/` |
| Reference (gates, tiers, review_ref) | [`reference.md`](reference.md) |
| Demo batch (Studio) | `{skill_root}/samples/demo-story.suite.json` |
| Per-product config | `config/<product>.json` → `config/default.json` |
| Run artifacts | `{config.output.artifacts_dir}/{run_id}/` (default `{skill_root}/artifacts/{run_id}/`) |
| Profile B triage example | `{skill_root}/runs/TC-6504/report/` |

Announce resolved `product` and `run_id` at the start of every run.

## Session inputs

| Input | Mandatory? | Notes |
|-------|------------|-------|
| **Requirement source** | **Yes** | Jira key (Story or **Epic**), JQL, or normalized bundle |
| **`review_ref`** | **Strongly encouraged** | Path to `review-payload.json` from Reviewer or Trinity Studio export (**CV4**) |
| **External context** | No | User-supplied paths/URLs — see templates |
| **Xray extract** | No | Dedupe / depth hints only |

If `review_ref` is omitted, set `review_skipped: true` and a one-line reason in batch metadata; do not pretend a gate was evaluated.

## Session parameters

| Parameter | Required | Notes |
|-----------|----------|-------|
| `scope` | Yes | Issue key(s), JQL, bundle path, or `review_ref` path |
| `run_id` | No | Default `{PRIMARY-KEY}` or timestamp |
| `jira_primary_key` | No | Filename anchor when scope is multi-key |
| `comprehensive` | No | Default **`false`** → **5–15** tests, `suite_mode=release_slice`. **`true`** only when review readiness is not `needs_clarification` and no open High Q#/RR-*, or user explicitly requests full suite |
| `force` | No | Bypass Reviewer `BLOCKED` gate only with explicit QA confirmation in chat; set `gate_override: true` |
| `figma_policy` | No | `link-only` (default), `export`, `out` — from config |
| `external_context` | No | `paths[]`, `urls[]` per template |
| `existing_xray_extract` | No | Path to extract JSON/MD |

## Preconditions (enforce before drafting)

1. Resolve primary `{JIRA-KEY}` (Epic preferred when scope is an Epic batch).
2. Load `review_ref` when provided; apply gate rules in [`reference.md`](reference.md).
3. Load `golden/v1/style-rules.md`, both `golden/v1/examples/`, and validate against `TestCaseDraft.schema.json`.
4. Build or load coverage checklist (`coverage-catalog.md` or run-scoped `CAT-*` rows).
5. Acquire requirements (Jira MCP, bundle, linked Confluence/Figma per policy). User `external_context` merges **before** embedded link crawl — see reference.
6. **Epic scope:** one suite on the Epic key; child stories supply traceability only — no separate child suites.

## Workflow

1. **Pre-flight** — `comprehensive`, gate, fingerprint staleness: if `review_ref` fingerprint ≠ live requirement fingerprint, warn and ask whether to proceed.
2. **Ingest** — Requirements + review findings; record loaded sources in batch metadata.
3. **Size** — Release slice vs comprehensive per parameters and review readiness.
4. **Draft tests** — Each test: `draft_id`, tiers, `customer_impact`, `test_data_*`, steps (`step` / `expected_result` / optional `test_data`), traceability keys and `source_quotes` where possible.
5. **Coverage report** — `coverage_report` with `uncovered_ac_ids`, warnings, optional `catalog_coverage`.
6. **Write artifacts** (same `run_id` folder):

| File | Purpose |
|------|---------|
| `suite-payload.json` | Canonical **TestCaseDraftBatch** (schema 1.0) — Studio import target |
| `suite-report.md` | Human-readable suite (required per D21) |
| `suite-report.html` | Optional Profile A HTML when `render_report` supports `suite` kind |

7. **Handoff** — Tell QA to import `suite-payload.json` in **Trinity Studio** (Creator tab) or continue edit/approve flow; Xray submit is **Importer** only (**CR-IMPORTER-01**).

## Quality bar

- No placeholder steps (“TBD”, “verify as appropriate”).
- No invented credentials or URLs; use config redaction patterns from Reviewer reference where applicable.
- P3 requires `deferrable: true` and `deferrable_rationale`.
- Do not exceed 15 tests in release slice without user approval for `comprehensive: true`.

## Trinity Studio

After generation, import the JSON batch:

```text
Trinity Studio → Creator → Import batch
Path: Trinity/creator/samples/demo-story.suite.json   (demo)
      Trinity/creator/artifacts/{run_id}/suite-payload.json   (your run)
```

Approve tests in Studio; export approved payload for Importer (roadmap).
