# requirements-review — examples

## Example 1 — Single Story, BLOCKED

**User request:**
```
Review requirements for PROJ-456. run_id: 2026-06-09-001
```

**Input bundle excerpt (simplified):**
```yaml
work_item:
  jira_key: PROJ-456
  summary: Checkout authorize for saved card
acceptance_criteria:
  items: []
open_questions:
  - id: OQ-01
    text: What is the retry limit after soft-decline?
    blocking: true
    owner: PM
```

**Sample finding:**
```json
{
  "finding_id": "RR-PROJ-456-01",
  "jira_key": "PROJ-456",
  "severity": "CRITICAL",
  "category": "acceptance_criteria",
  "checklist_ref": "3.1",
  "excerpt_quote": "acceptance_criteria:\n  items: []",
  "finding_summary": "No acceptance criteria defined",
  "question_for_PM": "Please add testable AC items for happy path and decline scenarios.",
  "suggested_AC_patch": "Given a logged-in customer with a saved card\nWhen they submit checkout\nThen payment is authorized and order status is Paid",
  "blocks_test_generation": true
}
```

**Gate:** `BLOCKED` — agent stops; does not offer test-case-creation.

---

## Example 2 — Story with warnings, PASS_WITH_WARNINGS

**Finding (HIGH):**
```json
{
  "finding_id": "RR-PROJ-457-01",
  "jira_key": "PROJ-457",
  "severity": "HIGH",
  "category": "testability",
  "checklist_ref": "5.3",
  "excerpt_quote": "When the user submits the form",
  "finding_summary": "AC references API behaviour but no endpoint or method documented",
  "question_for_PM": "Which API endpoint and HTTP method does this AC refer to?",
  "suggested_AC_patch": "",
  "blocks_test_generation": false
}
```

**Gate:** `PASS_WITH_WARNINGS` — QA may proceed; warnings listed in chat.

---

## Example 3 — Force override

**User request:**
```
force=true — proceed despite CRITICAL findings; PM will fix ACs in parallel.
```

**Agent must:**
1. Confirm QA intent explicitly in chat before acknowledging override.
2. Set `gate.force_override: true` in JSON.
3. Set `gate.status: PASS_WITH_WARNINGS` (not PASS).
4. Still list all CRITICAL items for PM.

---

## Example 4 — Live Jira fetch (Atlassian MCP)

**User request:**
```
Run requirements-review on Epic PROJ-100 and child stories.
```

**Agent steps:**
1. `getJiraIssue` for PROJ-100.
2. `searchJiraIssuesUsingJql` with `"Epic Link" = PROJ-100` or project-specific epic JQL.
3. For each child: `getJiraIssue` with fields from mapping.
4. Normalize to bundle shape; run checklist.
5. Write artifacts to `Skills/artifacts/2026-06-09-001/`.

---

## Example 5 — Pre-supplied bundle file

**User request:**
```
Review the bundle at bundles/pilot-v1/PROJ-456.requirement.yaml
```

**Agent steps:**
1. Read file; validate required sections.
2. Skip Jira MCP unless user asks to refresh.
3. Run checklist; write artifacts.
