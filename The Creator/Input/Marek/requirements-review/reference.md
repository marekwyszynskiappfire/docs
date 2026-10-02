# requirements-review — reference

## Severity model

| Severity | Meaning | `blocks_test_generation` | Gate impact |
|----------|---------|--------------------------|-------------|
| CRITICAL | Missing/untestable AC; blocking open question; scope contradiction; secrets in text | `true` | BLOCKED unless `force=true` |
| HIGH | Ambiguous AC; missing testability; incomplete traceability | `false` | PASS_WITH_WARNINGS |
| MEDIUM | Template deviation; minor clarity | `false` | PASS_WITH_WARNINGS |
| LOW | Suggestion; nice-to-have | `false` | PASS |

Only **CRITICAL** findings block test generation by default.

---

## Finding categories

| Category | Examples |
|----------|----------|
| `acceptance_criteria` | Missing AC, non-testable AC, duplicate AC, AC contradicts description |
| `scope` | In/out scope unclear or conflicting |
| `testability` | No environment, no test data, API path missing, UI screen unnamed |
| `traceability` | No design link when UI feature; parent Epic missing |
| `open_questions` | Blocking question unresolved |
| `template_compliance` | Required section empty without `N/A` |
| `data_sensitivity` | Possible PII/secrets — flag for redaction |

---

## Finding ID format

```
RR-{JIRA_KEY}-{NN}
```

Example: `RR-PROJ-456-01`, `RR-PROJ-456-02`

---

## Jira MCP tool mapping

Use Atlassian MCP when available; fall back to logical names for custom servers.

| Logical tool | Atlassian MCP tool |
|--------------|-------------------|
| `jira_get_issue` | `getJiraIssue` |
| `jira_search` | `searchJiraIssuesUsingJql` |
| `jira_get_issue_links` | `getJiraIssueRemoteIssueLinks` (+ parent/epic from issue fields) |
| `jira_add_comment` | `addCommentToJiraIssue` |
| `jira_get_attachment_metadata` | From `getJiraIssue` attachment fields |

---

## Normalizing Jira issue → requirement bundle

Map fetched Jira fields into the shape defined in [requirements-template.md](../../requirements-template.md). Minimum mapping:

| Bundle path | Typical Jira source |
|-------------|---------------------|
| `work_item.jira_key` | Issue key |
| `work_item.summary` | Summary |
| `work_item.issue_type` | Issue type name |
| `work_item.project_key` | Project key |
| `description` | Description (rendered) |
| `acceptance_criteria.items[]` | Custom AC field (ID from mapping) |
| `parent.epic_key` | Epic Link / parent |
| `traceability.design_references` | URLs in description or remote links |
| `document.redaction_applied` | Set `false` until redaction pass completes |

If `config/jira_xray_mapping.yaml` exists, use its field IDs. Otherwise ask the user which field holds acceptance criteria.

---

## Redaction rules

Before LLM analysis:

1. Mask patterns that look like API keys, tokens, passwords.
2. Replace live customer emails/names with placeholders if governance requires.
3. Set `document.redaction_applied: true` after redaction.
4. If unredacted sensitive data is found, emit `data_sensitivity` CRITICAL finding.

---

## Gate decision table

| Condition | `gate.status` | Agent action |
|-----------|---------------|--------------|
| 0 CRITICAL findings, 0 HIGH | PASS | May proceed to test-case-creation |
| 0 CRITICAL, ≥1 HIGH/MEDIUM/LOW | PASS_WITH_WARNINGS | Proceed; list warnings |
| ≥1 CRITICAL, `force` not set | BLOCKED | Stop; do not run test-case-creation |
| ≥1 CRITICAL, `force=true` + QA confirms in chat | PASS_WITH_WARNINGS | Log `force_override` in JSON |

---

## Markdown report template

```markdown
# Requirements review — {run_id}

**Reviewed:** {ISO-8601}
**Scope:** {type} — {value}
**Gate:** {status}

## Executive summary

- Requirements reviewed: {count}
- Findings: CRITICAL {n} | HIGH {n} | MEDIUM {n} | LOW {n}
- Blocks test generation: {yes/no}

## Per-requirement summary

| Jira key | Summary | CRITICAL | HIGH | Blocks? |
|----------|---------|----------|------|---------|

## Findings

### {jira_key}

| ID | Severity | Category | Summary | PM question |
|----|----------|----------|---------|-------------|

## Rollup (multi-story)

{common patterns, recommended PM fix order}

## Next actions

**PM:** ...
**QA:** ...
```

---

## What this skill does NOT do

- Generate test cases
- Write to Xray
- Edit Jira issues (read + optional comment only)
- Auto-fix requirements
