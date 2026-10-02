---
name: requirements-review
description: >-
  Analyzes Jira requirements against team standards and produces structured
  findings with severities for PM. Gates test generation on CRITICAL gaps.
  Use when reviewing Epics or Stories before test creation, when the user asks
  for requirement quality review, AC gaps, review-only pass, or before invoking
  test-case-creation.
disable-model-invocation: true
---

# Requirements review

Structured quality analysis of Jira requirements **before** test case generation. Produces actionable findings for PM and a **gate** that blocks `test-case-creation` on CRITICAL gaps.

**Does not:** generate tests, write to Xray, or edit Jira (read + optional comment only).

## Paths (this repo layout)

| Resource | Path (from workspace root) |
|----------|----------------------------|
| Review checklist | `AI in QA/Skills/templates/requirement_standard.md` |
| Output JSON schema | `AI in QA/Skills/templates/review_findings.schema.json` |
| Bundle shape | `AI in QA/requirements-template.md` |
| Field mapping (optional) | `config/jira_xray_mapping.yaml` |
| Artifacts output | `AI in QA/Skills/artifacts/{run_id}/` |
| Reference | [reference.md](reference.md) |
| Examples | [examples.md](examples.md) |

## Session parameters

| Parameter | Required | Notes |
|-----------|----------|-------|
| `scope` | Yes | Epic key, Story key(s), JQL, or bundle file path |
| `run_id` | Yes | Generate UUID/timestamp if user did not provide |
| `force` | No | QA override past CRITICAL findings — requires explicit chat confirmation |

## Workflow

Execute steps **in order**. Do not skip to test generation.

### 1. Pre-flight

1. Set or confirm `run_id`; announce it.
2. Read `AI in QA/Skills/templates/requirement_standard.md`.
3. Read `AI in QA/Skills/templates/review_findings.schema.json`.
4. If fetching from Jira: verify MCP with `getJiraIssue` on one known key. On failure, abort with connectivity guidance.
5. If `config/jira_xray_mapping.yaml` exists, load Jira field IDs from it.

### 2. Acquire requirements

**Path A — Live Jira fetch**

1. Resolve scope:
   - Epic → `getJiraIssue` + `searchJiraIssuesUsingJql` for child Stories.
   - Story → single `getJiraIssue`.
   - JQL → `searchJiraIssuesUsingJql` with pagination limit (state limit in chat).
2. Per issue: fetch fields per mapping; `getJiraIssueRemoteIssueLinks` for design links.
3. Normalize each issue to bundle shape per `AI in QA/requirements-template.md`.
4. Apply redaction (see [reference.md](reference.md)); set `document.redaction_applied: true` when done.
5. Show summary table: `jira_key | summary | AC count | blocking OQ count`.

**Path B — Pre-supplied bundle**

1. Read YAML/markdown bundle from user-provided path.
2. Validate required sections; report structural errors before analysis.
3. Refresh from Jira only if user explicitly requests.

If scope is empty or bundle invalid, abort with structured errors.

### 3. Analyze each requirement

For each `jira_key`, walk every criterion in `requirement_standard.md`.

For each gap, emit one finding:

```json
{
  "finding_id": "RR-PROJ-456-01",
  "jira_key": "PROJ-456",
  "severity": "CRITICAL | HIGH | MEDIUM | LOW",
  "category": "acceptance_criteria | scope | testability | traceability | open_questions | template_compliance | data_sensitivity",
  "checklist_ref": "3.1",
  "excerpt_quote": "verbatim text from requirement",
  "finding_summary": "one-line description",
  "question_for_PM": "actionable question or empty",
  "suggested_AC_patch": "proposed AC text or empty",
  "blocks_test_generation": true
}
```

**Rules:**

- `excerpt_quote` must be **verbatim** from the bundle — never paraphrase as a quote.
- Do not invent product behaviour; ask PM via `question_for_PM`.
- `open_questions` with `blocking: true` unanswered → CRITICAL (`blocks_test_generation: true`).
- Empty AC section and empty description → CRITICAL.
- `blocks_test_generation: true` **only** for CRITICAL findings.

Severity defaults: see [reference.md](reference.md).

### 4. Rollup (multi-story / Epic scope)

When scope has multiple requirements, add `rollup` to JSON:

- Common gap patterns (e.g. "3/5 stories missing test data").
- Cross-story dependencies.
- `recommended_pm_order` — which keys to fix first.

### 5. Write artifacts

Create directory `AI in QA/Skills/artifacts/{run_id}/` and write:

**`requirements-review.json`** — must validate against `review_findings.schema.json`:

```json
{
  "run_id": "...",
  "reviewed_at": "ISO-8601",
  "scope": { "type": "epic|story|stories|jql|bundle", "value": "..." },
  "requirement_keys": ["PROJ-456"],
  "findings": [],
  "rollup": {},
  "gate": {
    "status": "PASS | PASS_WITH_WARNINGS | BLOCKED",
    "critical_unresolved_count": 0,
    "blocks_test_generation": false
  },
  "schema_version": "1.0"
}
```

**`requirements-review.md`** — human report per template in [reference.md](reference.md).

Tell the user both file paths when done.

### 6. Gate decision

| Condition | `gate.status` | Action |
|-----------|---------------|--------|
| 0 CRITICAL | PASS or PASS_WITH_WARNINGS | Tell QA they may run `test-case-creation` |
| ≥1 CRITICAL, no `force` | BLOCKED | **Stop.** List CRITICAL findings. Do not run test-case-creation. |
| ≥1 CRITICAL, `force=true` | PASS_WITH_WARNINGS | Require explicit QA confirmation in chat; set `gate.force_override: true` in JSON |

### 7. Optional Jira comment

Only if user opts in and policy allows:

- `addCommentToJiraIssue` on Epic or each Story.
- Include: finding counts by severity, gate status, `run_id`, path to artifact.
- Do not paste sensitive content into Jira.

## Failure handling

| Failure | Action |
|---------|--------|
| Jira MCP unreachable | Abort; no partial gate PASS |
| Issue not found / permission denied | Add to `errors[]`; continue other keys in batch |
| Wrong mapping → empty AC field | HIGH finding + suggest mapping fix |
| Bundle schema invalid | List errors; abort review |

## Output checklist

Before finishing, confirm:

- [ ] `run_id` in JSON and markdown
- [ ] Every finding has `finding_id`, `severity`, `category`, `finding_summary`
- [ ] CRITICAL findings have `blocks_test_generation: true`
- [ ] Gate status stated clearly in chat
- [ ] BLOCKED → did not proceed to test generation

## Additional resources

- Severity, categories, MCP mapping: [reference.md](reference.md)
- Sample inputs and gate outcomes: [examples.md](examples.md)
