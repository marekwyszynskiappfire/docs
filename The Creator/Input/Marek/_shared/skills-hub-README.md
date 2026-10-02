# AI in QA — Agent Skills (staging)

Skills are authored here before moving to `.cursor/skills/` in the QA tooling repo (or this repo when adopted).

## Implemented

| Skill | Directory | Status |
|-------|-----------|--------|
| requirements-review | [requirements-review/](requirements-review/) | Ready |
| test-case-creation | [test-case-creation/](test-case-creation/) — **[README with prompts](test-case-creation/README.md)** · **Portable copy:** [../TestCaseCreator/README.md](../TestCaseCreator/README.md) | Ready (comprehensive mode v2) |

## Shared assets

| Path | Purpose |
|------|---------|
| [templates/requirement_standard.md](templates/requirement_standard.md) | Review checklist (Skill 1) |
| [templates/review_findings.schema.json](templates/review_findings.schema.json) | Review output schema |
| [schemas/TestCaseDraft.schema.json](schemas/TestCaseDraft.schema.json) | Test draft batch schema (Skill 2 → Skill 3) |
| [golden/v1/style-rules.md](golden/v1/style-rules.md) | Test writing style baseline |
| [golden/v1/examples/](golden/v1/examples/) | Golden example tests (atomic + journey) |
| [test-case-creation/coverage-catalog.md](test-case-creation/coverage-catalog.md) | Optional domain coverage checklist when the feature matches that catalog |

## Session artifacts

Primary outputs are documented per skill. **test-case-creation** writes a **single** file: `artifacts/{JIRA-KEY} - testcase-draft.md` (full suite, traceability, and TestCaseDraftBatch JSON in an appendix). Other skills may still use `artifacts/{run_id}/`.

| Skill | Outputs |
|-------|---------|
| requirements-review | `requirements-review.json`, `requirements-review.md` (paths per that skill) |
| test-case-creation | `artifacts/{JIRA-KEY} - testcase-draft.md` only (JSON batch lives in the appendix unless user requests a separate `.json` export) |

## Workflow order

```
requirements-review → (PM fixes / force) → test-case-creation → (QA triage) → xray-import
```

## Using in Cursor

Until skills are installed under `.cursor/skills/`:

1. Reference explicitly: e.g. "Follow the test-case-creation skill" and point to `AI in QA/Skills/test-case-creation/SKILL.md`.
2. For **copy-paste prompts**, optional `external_context`, and a full runbook, use [test-case-creation/README.md](test-case-creation/README.md).
3. Or copy skill folders to `.cursor/skills/` in your working repo.

Specification: [Agent Skills Specification.md](Agent%20Skills%20Specification.md)
