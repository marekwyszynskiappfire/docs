---
name: qa-work-tracking
description: >-
  Runs a conversational QA work check-in via Atlassian MCP: lists the engineer's
  open Jira items, asks for status updates, captures new work, and creates or
  updates issues with correct issue type, Metric, team, and Epic links per Appfire
  QA transparency standards. Use when logging QA work, syncing Jira with actual
  effort, running a QA standup, or improving Jellyfish visibility.
---

# QA Work Tracking (Jira + Jellyfish)

Conduct a **friendly, structured check-in** with a QA engineer so Jira matches reality and **Jellyfish** can report capacity accurately.

**Standards (read when classifying work):**

- [qa_work_tracking_in_jira.md](../../../QA_TRANSPARENCY/qa_work_tracking_in_jira.md) — issue types, activity mapping, Horizon vs Eng team
- [improving_visibility_of_qa_work_in_jellyfish.md](../../../QA_TRANSPARENCY/improving_visibility_of_qa_work_in_jellyfish.md) — five work types, Epic rules, status semantics, 2h rule
- [activity-mapping.md](activity-mapping.md) — quick lookup table
- [work-model.md](work-model.md) — Metric / team / project by work type

---

## Prerequisites

1. **Atlassian MCP** must be connected and authenticated (`plugin-atlassian-atlassian`).
2. Before any Jira call, resolve **cloudId**:
   - Call `getAccessibleAtlassianResources` (no args), or
   - Use site URL: `https://appfire.atlassian.net` (typical for product QA Jira/Confluence).
3. Read each MCP tool schema under `mcps/plugin-atlassian-atlassian/tools/` before calling it.
4. If auth fails, run `mcp_auth` for the Atlassian server once, then retry.

**Never** scrape Confluence/Jira in a browser when MCP is available.

---

## Core rules (non-negotiable)

| Rule | Detail |
| --- | --- |
| Visible work | Meaningful QA effort → Jira artifact. Untracked = unmanaged. |
| 2-hour rule | Expected effort **> 2 hours** → create a Jira task. |
| Jellyfish signals | **Status** (Open → In Progress → Done), **Metric**, **Team**, **Project** must be correct. |
| No silent writes | Show a confirmation summary; apply MCP changes only after the engineer agrees. |
| Effort, not only bugs | Investigations with no bug still get a task (especially maintenance). |
| PO environment setup | QA tracks env prep: In Progress while setting up → hand back to PO when ready. |

---

## MCP tools used in this skill

| Step | Tool | Purpose |
| --- | --- | --- |
| Setup | `getAccessibleAtlassianResources` | Resolve `cloudId` |
| Identity | `lookupJiraAccountId` | Map name/email → `assignee_account_id` |
| List work | `searchJiraIssuesUsingJql` | Open / assigned QA issues |
| Detail | `getJiraIssue` | Metric, Team, parent Epic, description |
| Create | `createJiraIssue` | New Task / Test Execution / Test Case |
| Update fields | `editJiraIssue` | Metric, Team, assignee, parent, labels |
| Status | `getTransitionsForJiraIssue` → `transitionJiraIssue` | Workflow changes |
| Notes | `addCommentToJiraIssue` | Progress summary from check-in |
| Metadata | `getJiraIssueTypeMetaWithFields` | Required fields before create (if create fails) |

Use `additional_fields` on `createJiraIssue` for **Metric**, **Team**, and other custom fields (not top-level params).

---

## Check-in workflow

Track progress:

```
- [ ] 1. Identify engineer + App QA project key(s)
- [ ] 2. Load assigned / open issues (JQL)
- [ ] 3. Present list; flag hygiene gaps
- [ ] 4. Ask status updates per item (or batch)
- [ ] 5. Ask for new / untracked work
- [ ] 6. Propose creates/updates/transitions
- [ ] 7. Confirm with engineer → execute MCP writes
- [ ] 8. Summarize with links
```

### Step 1 — Who and where

Ask (one message, 2–3 questions max):

1. **Your name or email** (for assignee lookup).
2. **App QA project key** (e.g. `TC` for BigPicture QA) — do not guess.
3. **Optional:** product Epic keys or release version you are working on.

Call `lookupJiraAccountId` with `cloudId` and search string.

### Step 2 — Load existing work

Run JQL via `searchJiraIssuesUsingJql`. Start with:

```jql
project = {QA_PROJECT_KEY}
AND assignee = currentUser()
AND status NOT IN (Done, Closed, Cancelled)
ORDER BY updated DESC
```

If `currentUser()` fails for the MCP context, use assignee by account ID:

```jql
project = {QA_PROJECT_KEY} AND assignee = "{accountId}" AND status NOT IN (Done, Closed, Cancelled) ORDER BY updated DESC
```

Request fields: `summary`, `status`, `issuetype`, `assignee`, `priority`, `parent`, and **Metric** / **Team** if available in JQL.

Set `maxResults` to **25–50** for check-ins.

Also run a hygiene query for the same assignee:

```jql
project = {QA_PROJECT_KEY} AND assignee = currentUser() AND status NOT IN (Done, Closed) AND (Metric is EMPTY OR Team is EMPTY)
```

### Step 3 — Present assigned / open items

Show a table:

| Key | Summary | Type | Status | Metric | Team | Parent/Epic |
| --- | --- | --- | --- | --- | --- | --- |
| … | … | … | … | … | … | … |

**Flag:**

- Missing **Metric** or **Team**
- Stale **In Progress** with no recent update
- Work >2h likely spent but still no ticket
- Feature work not linked to an Epic

Ask: *“Does this list match what you’re working on? Anything missing or already finished?”*

### Step 4 — Status updates (conversation)

For each item the engineer mentions (or in batches: “anything else on TC-1234?”):

1. **Current state** — still active, blocked, or done?
2. **Short progress note** — optional comment text.
3. **Classification still correct?** — Metric, Team, Epic parent.

**Jellyfish reminder:** moving to **In Progress** = start of work; **Done** = completed.

When confirmed:

1. `getTransitionsForJiraIssue` → pick valid transition id.
2. `transitionJiraIssue` with `transition: { "id": "..." }`.
3. `addCommentToJiraIssue` if they gave a summary.
4. `editJiraIssue` if Metric, Team, assignee, or parent must change.

Do **not** transition issues owned by someone else without explicit approval.

### Step 5 — New work

Ask: *“Any QA work since your last check-in that isn’t in Jira yet?”*

For each activity:

1. Classify using [work-model.md](work-model.md) (product / maintenance / release / automation / operational excellence).
2. Map issue type + team using [activity-mapping.md](activity-mapping.md).
3. Apply **2-hour rule** — suggest ticket if ≥2h.
4. Propose **summary** (include product, version, activity: e.g. `BigPicture 8.72 — sanity Jira Cloud`).
5. Confirm **Metric**, **Team**, **parent Epic**, **assignee**.

**Special cases:**

| Case | Action |
| --- | --- |
| Test run (multi-QA) | **Test Execution** + linked **Task** per QA involved |
| Release | Min. one **test run** + one **sanity** ticket per QA |
| Feature acceptance | Task(s) in App QA project, parent = feature Epic, Metric = Feature, Team = delivering Eng team |
| Maintenance investigation | Task even if no bug filed, Metric = Maintenance or L3 Support |
| Training | **Task** in **QA CoE** project, Team = Horizon, Metric often unset |

### Step 6 — Confirm before write

Show:

```markdown
## Planned Jira changes

### Transitions
- TC-1234: In Progress → Done

### Field updates
- TC-5678: Metric → Maintenance, Team → {team}

### New issues
- [CREATE] TC | Test Execution | "8.72 sanity Jira Cloud" | Metric: Feature | Team: …

### Comments
- TC-1234: "Completed sanity on build X; no blockers."

Proceed? (yes / adjust / cancel)
```

Execute MCP only after **yes**.

### Step 7 — Execute and summarize

After writes:

- List each key with `https://appfire.atlassian.net/browse/{KEY}`
- Note any items still missing Metric/Team
- Remind: disciplined status + classification keeps **Jellyfish** trustworthy

---

## Classifying new work (shortcut)

| Engineer says… | Work type | See |
| --- | --- | --- |
| Acceptance / new feature / milestone testing | Product | work-model §1 |
| Repro support ticket / verify fix / L3 | Maintenance | work-model §2 |
| Test run / sanity / release | Release | work-model §3 |
| Playwright / automate TC / fix auto tests | Test automation | work-model §4 |
| TC cleanup / process improvement | QA Operational Excellence | work-model §5 |

When **Feature vs Maintenance** is ambiguous (sanity, test run), ask: *feature release or hotfix/maintenance release?*

---

## Issue creation (MCP pattern)

```
createJiraIssue(
  cloudId = "{cloudId}",
  projectKey = "{QA_PROJECT_KEY}",
  issueTypeName = "Task" | "Test Execution" | "Test Case",
  summary = "{summary}",
  description = "{optional markdown}",
  assignee_account_id = "{accountId}",
  additional_fields = {
    "Metric": { "value": "Feature" },   // use project-specific shape from getJiraIssueTypeMetaWithFields
    "Team": { "name": "..." },
    "parent": { "key": "EPIC-123" }
  }
)
```

If create fails on custom fields, call `getJiraProjectIssueTypesMetadata` + `getJiraIssueTypeMetaWithFields` for the project, then retry with correct field IDs/names.

---

## Failure modes

| Situation | Action |
| --- | --- |
| MCP not authenticated | `mcp_auth`; stop writes until fixed |
| Unknown QA project key | Ask engineer; list `getVisibleJiraProjects` only if needed |
| Invalid transition | Show available transitions; let engineer pick |
| Unsure Metric | Explain four metrics + release/feature vs hotfix |
| Work on two products | Run JQL per project key |
| Cannot set parent Epic | Create issue, then `editJiraIssue` or link manually; tell engineer |

---

## Tone

- Collaborative standup, not an audit.
- **One or two questions at a time.**
- Prefer tables for issue lists.
- Always **preview** Jira mutations before MCP writes.
