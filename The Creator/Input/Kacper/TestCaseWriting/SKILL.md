---
name: timetracker-test-case-writing
description: >-
  Draft and review Timetracker manual UI test cases (TTQA-* / TS-*) in Action,
  Data, Expected Result format. Ask for Summary, TTQA key, Jira issue key/summary/id
  before drafting or handing off to automation; never invent or borrow KAN-* from other cases.
  Use Jira stories and epics the user sends (link, paste, export) for scope and AC context.
  Ground in code; XRay-ready CSV. Pair with AutomatingTestCases. Does not create Jira/XRay issues.
disable-model-invocation: false
---

# Timetracker test case writing (QA CoE)

Draft **manual UI** test cases for Jira (`TTQA-*`) and optional **E2E automation candidates**. Source material for Playwright under `qa-coe/E2E/Timetracker/`.

**Automation implementation** → [`AutomatingTestCases/SKILL.md`](../AutomatingTestCases/SKILL.md).

**XRay / Jira:** compatible copy/import format only. **Nothing is created automatically.**

## Examples from the live suite (patterns, not authority)

Before drafting or reviewing, **grep** ~**143** Playwright cases under `qa-coe/E2E/Timetracker/specs/TS-*/TTQA-*.case.ts` — use them as **examples** for step shape, Data conventions, helpers, and date labels. They are **not** the source of truth: some cases predate current skills, Jira wording, or product UI.

**Authority (in order):**

1. **Approved Jira steps** — Action / Data / Expected Result for the case you are writing or automating
2. **Current product code + live UI** — labels, layout, behavior (`translate.ts`, Jira-UI / client components)
3. **Repo examples** — closest `TTQA-*.case.ts` in the same `TS-*` or theme (copy patterns; fix gaps when Jira or code disagree)

**Context (not step authority):** Jira **stories** and **epics** the user sends (link, paste, export) — AC, scope, parent epic. Use for coverage and **Preliminary** drafts; do not override approved steps or skip code/UI checks for **Final**.

| Lookup (examples) | Where |
|--------|--------|
| Same feature / theme | `specs/TS-*/` folder + `grep -l "Smart Suggestions" specs/` |
| Step wording + Data shape | Closest matching `TTQA-<n>.case.ts` — adapt to **this** Jira case |
| Scenario registration order | `TS-<n><suffix>.scenario.spec.ts` (e.g. `TS-8a`, `TS-6b`) |
| `KAN-*` issue keys | `fixtures/jiraIssueIds.json` for **this** `TTQA-*` only — never borrow from another case |
| E2E user emails | `api/e2eRequiredJiraUserEmails.ts` |
| Date isolation labels | **Strict phrases in Data** (`10 weeks in the future`, `03/2 months in the future`) — same text in Playwright `testStep` literals; `parallelTestDateIsolation.ts` only for automation seed bands |

**Repo scenario ids use letter suffixes** — not bare `TS-5` / `TS-8`. Examples: `TS-1a`/`TS-1b`/`TS-1c`, `TS-5a`/`TS-5b`, `TS-6a`/`TS-6b`/`TS-6c`, `TS-8a`/`TS-8b`. Folder is still `specs/TS-5/`; the **registered** id in `testScenario("TS-5a", …)` includes the suffix.

When a draft topic has **no** automated case yet (e.g. Audit Log), follow the CSV patterns below but label output **Preliminary** until a repo case or live UI verification exists.

## Jira story and epic context (user-provided)

When you **paste, link, or export** Jira **stories**, **epics**, or related parent items from Jira, use them as **background context** — not as a substitute for approved XRay test steps.

**Use for:**

- Acceptance criteria and scope (what to cover, what to defer)
- Feature area and user-facing intent
- Parent epic / initiative context (how the slice fits the bigger picture)
- Traceability in Description (`Based on: TT-7532 under EPIC-123`)
- Gaps and open questions → **Open assumptions** when AC is incomplete

**Do not:**

- Treat story AC alone as **Final draft** without code/UI verification (label **Preliminary** until grounded)
- Copy Jira story task lists verbatim as XRay steps when they disagree with Action / Data / Expected Result format
- Assume story issue keys (`TT-*`, `EPIC-*`) are the same as **`KAN-*` / `SUG-*`** work items used in test Data — ask when steps need an issue under test

If the user sends both **TTQA steps** and **story/epic context**, approved steps win for step wording; story/epic enriches coverage planning and assumptions.

## Ask before drafting

**Do not write steps** until enough context is confirmed. If anything below is missing, **ask explicitly** — do not guess `KAN-*` keys, `TTQA-*` numbers, or scenario folders.

**Jira stories and epics you send** (link, paste, or export from Jira) count as valid context input — read them for AC and scope even when the TTQA case is not fully written yet.

| # | Ask when missing | Why |
|---|------------------|-----|
| 1 | **Summary** (full XRay title) | Primary identifier; required always |
| 2 | **TTQA-* key** | If the test already exists or is reserved in Jira — use as lookup anchor. **Do not invent** if unknown |
| 3 | **XRay folder / theme** | e.g. `Audit Log`, `Smart Suggestions` |
| 4 | **TS-* scenario** (if known) | e.g. `TS-8a Smart Suggestions` — grep `qa-coe/E2E/Timetracker/specs/` and read `TS-*<suffix>.scenario.spec.ts` |
| 5 | **Story / epic / bug from Jira** (optional) | Link, paste, or export — AC, scope, parent epic; traceability in Description (e.g. `TT-7532` under `EPIC-123`) |
| 6 | **Jira work item key** (`KAN-*`, `SUG-*`) | When steps use an issue — **ask the user**; do not copy from another `TTQA-*` |
| 7 | **Jira work item summary** | Exact issue title in Jira (for Description, Data, and later Playwright constants) |
| 8 | **Jira work item id** (numeric) | For `jiraIssueIds.json` when automation is planned — **ask**; never guess |
| 9 | **Final vs Preliminary** | Code-grounded vs story-only |

**When Data mentions `IssueKey1` or `KAN-*` for an issue:** items **6–8 are required** before **Final draft** or before handing off to **AutomatingTestCases** (which will block without them).

**Prompt template when blocked:**

```text
Before I draft this test case, please confirm:
1. Summary (full XRay title)
2. TTQA-* key (if already assigned in Jira — e.g. TTQA-59)
3. XRay folder / feature area
4. TS-* scenario (if known)
5. Jira story / epic / bug (link, paste, or export — optional but useful for AC and scope)
6. Jira work item key (KAN-* / SUG-*) — if steps use an issue
7. Jira work item summary (exact issue title in Jira)
8. Jira work item id (numeric) — if you plan to automate
9. Final draft (code verified) or Preliminary (assumptions)?
```

When the user supplies **TTQA-59** (or any real key), grep the repo for **that same key** only (`specs/TS-*/TTQA-59.case.ts`, `jiraIssueIds.json`). For **patterns** (not fixtures), also skim sibling examples in the same `TS-*`. **Never substitute a different TTQA number or borrow `KAN-*` from another case.**

## When to use

| Situation | Action |
|-----------|--------|
| New user-facing feature (e.g. Audit Log) | Draft manual TCs + E2E candidates |
| Bug fix with UI impact | Focused regression TC(s) |
| Exploratory notes → structured cases | Convert to Action / Data / Expected Result |
| API/backend-only change | **No** UI TC table — bullets for backend/integration scope only |

## Draft status (label every output)

| Status | When |
|--------|------|
| **Final draft** | Labels/behavior verified in **current code** (`translate.ts`, components) or live develop/review |
| **Preliminary draft — assumptions must be confirmed** | Story/AC only, spec draft, or open product questions |

List assumptions under **Open assumptions** — never present them as confirmed behavior.

## Workflow

```
Ask for Summary + TTQA-* (if any) + folder + issue keys (if any)
→ Read user-provided Jira story/epic (link/paste/export) for AC and scope
→ Grep example TTQA-* in specs/ (same TS-* or same Summary theme) for patterns
→ Ground in code + live UI (approved Jira steps win over stale examples; story AC alone → Preliminary)
→ Plan layers (access → platform → happy path → edges)
→ Draft manual TCs + E2E candidates
→ CSV per test (Action, Data, Expected Result) for XRay import
→ Human review → create/update test in Jira/XRay
→ (optional) AutomatingTestCases skill (requires confirmed TTQA-*)
```

## Test case anatomy

| Field | Rule |
|-------|------|
| **Summary** | `[Area] - [Outcome]`. Match **exact** Jira/XRay wording once assigned — repo titles vary in casing (`Monthly view`, `Issue View`, `Timesheet`). Examples: `Timesheet - Undo Deletion of a Single Worklog Item in Timesheet`, `Smart Suggestions - Jira Activity Displays as Suggested Cards on the Grid`. |
| **Scenario** | `TS-*` theme (e.g. `TS-8 Smart Suggestions`). Registered Playwright id may add a suffix (`TS-8a`). One theme, many `TTQA-*`. |
| **Product** | `TIMETRACKER` |
| **Platform** | `Jira Cloud` (Playwright: `Platform.JIRACLOUD`) |
| **Stage** | `Develop` / `Review` (Playwright: `Stage.DEVELOP \| Stage.REVIEW`) |
| **Preconditions** | Tenant, role, seed, flags — or step 1 **Data** |
| **Steps** | **Action**, **Data**, **Expected Result** per step |

### Step format (mandatory)

| Action | Data | Expected Result |
|--------|------|-----------------|
| What tester **does** | User, issue alias, dates, filters, API seed | **Observable** UI outcome |

**Data conventions:**
- **Issues — do not invent or borrow `KAN-*` / `SUG-*`:**
  - **Preliminary (no issue reserved yet):** use **descriptive aliases** + state — e.g. `closedIssue: Jira issue assigned to UserA, transitioned to Done after recent activity today`.
  - **When user gives `TTQA-*` and automation is planned:** **ask** for `KAN-*`, exact issue **summary**, and numeric **id** — put them inline in **Data** on every step that uses the issue.
  - **When user gives all three (key + summary + id):** use them verbatim in **Data** (e.g. `plannedTaskBothDates: ABC-2 [BP Planned] Both dates — 8h estimate`) and note the `jiraIssueIds.json` row for AutomatingTestCases.
  - **When the same `TTQA-*` already exists in repo:** reuse **only** from `fixtures/jiraIssueIds.json` or `specs/TS-*/TTQA-<same-n>.case.ts` for **that** key.
  - **Never** copy `KAN-*` from unrelated `TTQA-*` cases — **ask the user** instead.
  - **Never use `see Description` in Data** — each step must be runnable from its **Data** cell alone; put **inline seed in Data** (`alias: [summary]`, plus dates or key when known).
- **Users:** role alias + known E2E email in **manual Data** — e.g. `user1: timetracker-jira-e2e-first@appfire.com`, `UserA: timetracker-jira-dev@appfire.com`. Canonical list: `qa-coe/E2E/Timetracker/api/e2eRequiredJiraUserEmails.ts` (`timetracker-jira-dev@appfire.com`, `kacper.woloszyn@appfire.com`, `timetracker-jira-e2e-first@appfire.com`). **Never invent users**, never passwords/tokens. In Playwright code, cases often use **Jira display names** (`Dev Testing`, `Timetracker Jira e2e First`) — manual Data still uses alias + email for testers.
- **Routes:** shorthand in Data is OK — e.g. `Route audit-log` for direct navigation to the Audit Log page.
- **Named periods (empty-state / custom month):** use a label + description — e.g. `month1: A month where no actions took place` in **Data**, with Action `Change Timeframe to month1`. Tester picks a month that satisfies the description; do not use bare `today` / `yesterday` / `TBD`.
- **Worklog / navigation seed dates:** put the **exact** relative label in **Data** on every step that needs it (`week: 10 weeks in the future`, `Date1: 15/2 months in the future`) — testers and Playwright reports use this text; automation seed bands live in `parallelTestDateIsolation.ts` (see **Parallel workers** in AutomatingTestCases when bands move, e.g. TTQA-44 vs TS-4 / TTQA-70 — update Jira steps when N changes).
- **Clock times in Data (Weekly / hover / issue panel):** use 12h labels as testers see them (`09:00 am`, `10:00 am`). Pair `Date1` with a **relative offset** from `parallelTestDateIsolation.ts`, not bare `today`, when automation will seed via API on an isolated week/month.
- **Weekly hover Expected Result:** verify in UI before promising start/end in the **tooltip** — hover often shows project, issue type, summary, billable only; times may stay on the **card** (AutomatingTestCases maps this to `expectWeeklyWorklogCardTimeRange` on the card, not tooltip).
- **Tenant preconditions on a step:** put seed requirements in **Data** on the relevant step — e.g. `Tenant has audit activity in current calendar month` on a verify step (TTQA-385 pattern).
- **Empty Data:** leave blank when the step has no inputs (common for verify/click steps). When admin login is a **Description** precondition, step 1 Data can stay empty — avoid redundant `E2E admin` on every step.
- **Jira wiki links in Data:** exports may show `[email|mailto:email]` — plain `alias: email@domain.com` is preferred in drafts; both are acceptable.

**Expected Result:**
- **System messages and errors:** exact copy from **current** UI (`translate.ts`, `en.json`, live app) — e.g. `No history entries match your filters.`
- **Navigation and layout:** concise observable outcomes are OK — e.g. `Timetracker loads correctly`, `Audit logs open`, `Clear filters button is not visible`
- **Lists (filters, columns):** space-separated names in one phrase — e.g. `Timeframe Performed by Affected users Action Source are visible`

Playwright mirrors this: `testStep` title = **Action** (+ **Data** when present in Jira) as a **plain `"..."` string** — **no `` `${…}` ``**; copy date phrases **verbatim** from Jira Data (strict relative labels, not resolver variables). `//` comment inside the step = **Expected Result** (see `TTQA-96`, `TTQA-8`). Automation may add **extra setup steps** not exported to XRay (e.g. API worklog delete before UI checks in `TTQA-5`) — keep those out of manual CSV unless product wants them in Jira.

## Coverage strategy

Do **not** write one case per button. Layer by **risk and reuse**:

1. **Access / navigation**
2. **Platform / shell** — filters, pagination, empty/loading/error (**once per surface**)
3. **Domain happy path** — one golden flow per capability
4. **Domain edges** — unauthorized, actor ≠ affected, bulk = N rows, import vs 7pace, empty state
5. **Regression** — known bugs only

Typical count: **5–15** manual cases per feature slice; **2–5** E2E automation candidates (skip section if none qualify).

Mark heavy-setup cases as **manual-only** in **Data** or **Notes** (e.g. `>100` audit rows).

## Source of truth

**Older Playwright specs can be wrong or inconsistent** — treat them as examples only (see above).

Before **Final draft**, verify against:

1. UI: `npm-packages/client/<feature>/`, `jira/services/Jira-UI/src/features/`
2. Labels: `resources/translations/translate.ts`
3. Permissions: `REQUIRED_PERMISSIONS.ts`
4. **Approved Jira test steps** for the case under review; **user-provided Jira story/epic** (link/paste/export) for AC and scope — story alone is not enough for Final without code/UI check
5. Example specs: `qa-coe/E2E/Timetracker/specs/TS-*/TTQA-*.case.ts` — grep by Summary theme for **patterns** (step tone, Data shape), not blind copy
6. `.agents/projects/<feature>/specification/` = **intent only** — note gaps in **Open assumptions**

Example: spec says 25 rows + “Load more”; code may use 100 rows + infinite scroll → write case for **code**, note in assumptions.

## E2E automation candidates

Separate table — not duplicate manual steps. Recommend only when:

- Behavior is stable and observable on develop/review E2E tenant
- High regression value (access, filters, pagination shell)
- Approved for automation in `TS-*` Playwright suite

Implementation → **AutomatingTestCases** skill. Pass **Test Summary**, steps, and **Jira work item key + summary + id** — AutomatingTestCases will not start without them when issues are involved. For Weekly cases with clock times in Data, note that automation pins `timezoneId: "UTC"` and aligns API seed day with `Date1` (see that skill’s **Worklog times, browser timezone, and day headers**). Do not export E2E rows as Manual XRay steps by default.

## Output template

Use every time. **Chat/review** tables may include Summary and Step for readability; **XRay CSV export** uses only Action, Data, Expected Result.

```markdown
# UI Test Cases — {FEATURE}

**Status:** Final draft | Preliminary draft — assumptions must be confirmed
**TTQA-* (if assigned):** TTQA-319
**XRay Summary:** Smart Suggestions - Suggestions Honor Custom rules - Tracking details - Closed items
**XRay folder:** Smart Suggestions
**Repo scenario (after automation):** TS-8a Smart Suggestions
**Based on:** code review + TTQA-319 | story/AC only | exploratory notes

## Manual test cases

Use **Summary** as the primary identifier. Use **TTQA-*** only when the user supplied it or it already exists in Jira — never invent a number. Never use internal labels like `TC-01`.

### Audit Log - Initial load

| Step | Action | Data | Expected Result |
|------|--------|------|-----------------|
| 1 | Open Audit Log as admin | E2E admin | Timeframe = Current month; table loads |

**XRay Description** (paste into the test issue in Jira **before** importing steps — omit this block when no preconditions / aliases are needed):

```text
{preconditions, users, issue aliases, tenant seed — plain text for Jira Description field}
```

When no Description is required, state explicitly: **No XRay Description required.**

**XRay CSV** (import steps after Summary and Description are set):
```csv
Action,Data,Expected Result
Open Audit Log,,Audit logs open
Verify Timeframe filter,,Predefined selection shows Current month
```

## E2E automation candidates

| Summary | Why automate | Risk if skipped |
|---------|--------------|-----------------|
| Audit Log - access | Gate for all audit tests | Unauthorized leak |

## Open assumptions
- {item} *(confirm with PO / code)*

## XRay import note
Import steps via Action / Data / Expected Result CSV. Create the XRay Test with **Summary** first; TTQA-* appears after save. Nothing created automatically.
```

## XRay CSV format (team standard)

XRay import uses **three columns only** — `Action`, `Data`, `Expected Result`. No `Scenario` or `Test Case Key` in the file.

Rules:
- **One row per step** per XRay Test issue.
- **Summary** and folder (e.g. Audit Log) are set in Jira **outside** the CSV.
- **Global preconditions** (integration setup, users, seed CSV import workflow, seed ↔ UI matrix, timeframes) go in XRay **Description** — output a **Paste into XRay Description** block when needed; say **No XRay Description required** when none apply.
- **Step-level inputs** (issues, dates, users, filters) go inline in **Data** on each row — never `see Description`. Use **inline seed in Data** (`alias: [summary]`, plus dates or key when known).
- **Description formatting:** use section headers and bullet lists — **do not** use pipe (`|`) tables; Jira Description breaks column alignment.
- Leave **Data** empty when the step has no inputs.
- Escape commas in fields with double quotes.

**Import order:** Summary → folder → **Description** (if any) → CSV steps.

### Exemplar: Audit Log platform suite (manual draft pattern — not yet in `specs/`)

These CSV blocks follow the planned XRay **Audit Log** folder style. **No `TTQA-383`–`TTQA-387` Playwright cases exist in the repo yet** — treat as **Preliminary** until code/UI verification or automation lands. For **automated** step tone, compare `TTQA-287` (Times Explorer platform shell) or `TTQA-3` (filters + empty state).

Reference exports: **TTQA-383** (access) through **TTQA-387** (empty state) in XRay folder **Audit Log**.

**Access — TTQA-383 style** (login in step 1; no user in Data when default admin):

```csv
Action,Data,Expected Result
Log in to Jira and open 7pace Timetracker,,Timetracker loads correctly
Click Audit Log in the left navigation,,Audit Log title and description are shown
Verify filter toolbar,,Timeframe Performed by Affected users Action Source are visible
Verify activity table,,Columns Date Performed by Email Action Details are visible
```

**Unauthorized — TTQA-384 style** (concrete `user1` + email):

```csv
Action,Data,Expected Result
Log in to Jira as user1 and open 7pace Timetracker,user1: timetracker-jira-e2e-first@appfire.com,Timetracker loads
Inspect left navigation,,Audit Log is not visible in the left navigation
Open Audit Log via direct URL,Route audit-log,Access denied; no audit log table or filter toolbar
```

**Filters — TTQA-386 style** (alias + email for people filter):

```csv
Action,Data,Expected Result
Open Audit Log,,Unfiltered audit entries are visible
Set Performed by,UserA: timetracker-jira-dev@appfire.com,Only entries with UserA as performer
Set Action,Created worklog,Results match UserA and Created worklog
Set Source,7pace,Only 7pace source rows remain
Click Clear filters,,All filter selections cleared; Current month restored; Clear filters button hidden
```

**Initial load — TTQA-385 style** (tenant seed in Data on verify step):

```csv
Action,Data,Expected Result
Open Audit Log,,Audit logs open
Verify Timeframe filter,,Predefined selection shows Current month
Verify people action and source filters,,Performed by Affected users Action Source visible with no active selections
Verify first page of results,Tenant has audit activity in current calendar month,Up to 100 rows; newest entries first
Verify Clear filters,Default load state,Clear filters button is not visible
```

**Empty state — TTQA-387 style** (named period, not “last month” literal):

```csv
Action,Data,Expected Result
Open Audit Log,,Page loads; Current month selected
Change Timeframe to month1,month1: A month where no actions took place,Loading completes
Verify empty message,,No history entries match your filters.
Click Clear filters,,Current month restored; entries shown when current month has data
```

**Custom rules + suggestions — TTQA-324 style (automated in repo)**

Repo case: `specs/TS-8/TTQA-324.case.ts` — `Smart Suggestions - Jira Activity Displays as Suggested Cards on the Grid`. Manual CSV shape (issue aliases until keys are in Description):

```csv
Action,Data,Expected Result
Open Weekly view for current week,,Weekly grid loads
Enable Show suggestions,,Show suggestions toggle is on
Prepare jiraIssue for suggestions,jiraIssue: Jira issue with changelog activity today,Issue has recent Jira activity
Verify suggestion card on grid,jiraIssue: KAN-* Jira issue with changelog activity today,Suggestion card for jiraIssue visible
```

For **Custom Rules + closed items + comment required** (manual-only draft until automated), use aliases like the TTQA-319 template below — grep `specs/TS-6/TTQA-*.case.ts` for Time tracking limits / Tracking details wording.

**Custom rules + suggestions — manual alias template (Preliminary if not in Jira yet)**

```csv
Action,Data,Expected Result
Open Settings > Custom Rules,,Search filters Time tracking limits Tracking details visible
Enable Time tracking limits and closed-items rule,closed limit: 0 hours,Limit logging and modifying time on closed items enabled; limit saved as 0 hours
Enable Tracking details and require comment,,Tracking details enabled; Require a comment checked
Reload Timetracker,,Weekly view loads
Prepare closedIssue for suggestions,closedIssue: Jira issue assigned to UserA transitioned to Done after recent activity today,Issue is closed in Jira
Prepare activeIssue for suggestions,activeIssue: Jira issue assigned to UserA with recent changelog activity today,Issue is in progress with activity today
Open Weekly view for current week,,Weekly grid loads
Enable Show suggestions,,Show suggestions toggle is on
Verify closedIssue on grid,closedIssue: KAN-* Jira issue assigned to UserA transitioned to Done after recent activity today,No suggestion card for closedIssue
Verify activeIssue on grid,activeIssue: KAN-* Jira issue assigned to UserA with recent changelog activity today,Suggestion card for activeIssue visible
Accept activeIssue suggestion,activeIssue: KAN-* Jira issue assigned to UserA with recent changelog activity today,Add missing information modal opens
Save without comment,,Comment is required by your organization
Enter comment and save,comment: Honor custom rules test,Modal closes; worklog saved on weekly grid
```

Put concrete `KAN-*` / `SUG-*` keys inline in **Data** after the user or an existing `TTQA-*.case.ts` / `jiraIssueIds.json` entry confirms them. Description holds global setup only — not issue lookups for steps.

## AI-assisted drafting

When using Cursor AI:

1. Run **Ask before drafting** — get Summary, TTQA-* (if any), folder, issue keys
2. Use **Jira stories and epics the user sends** (link, paste, export from Jira) plus repo feature paths for scope and AC
3. Require **code grounding** (`translate.ts`, implementation files)
4. Ask for **Final vs Preliminary** explicitly
5. Request markdown table **and** XRay CSV (`Action,Data,Expected Result` only — one block per test case)
6. Human runs review checklist before import

**Risks:** wrong labels, stale spec, too many per-action TCs, generic `UserA` without E2E email, **invented `KAN-*` or `TTQA-*`**, secrets in Data.

## Review checklist (human, before Jira)

- [ ] Status line: Final or Preliminary (with reason)
- [ ] Every step: Action, Data, Expected Result (Data may be empty)
- [ ] Expected results **observable** — exact copy for system messages; concise OK for layout/navigation
- [ ] Users in Data use **alias + email** from `e2eRequiredJiraUserEmails.ts` (not generic “UserA” alone)
- [ ] **Jira work item:** if steps use an issue — key, exact summary, and id captured (or explicitly **Preliminary** with aliases only)
- [ ] **No borrowed `KAN-*`** from another `TTQA-*` case
- [ ] **TTQA-*** matches what the user gave — not invented, not borrowed from another case
- [ ] **Repo scenario suffix** (`TS-8a`, not bare `TS-8`) noted when automation is planned
- [ ] Skimmed **example** sibling `TTQA-*.case.ts` for patterns — did not override Jira or code when they differ
- [ ] Empty-state / custom months use **named period + description** (e.g. `month1: …`), not vague dates — or **fixed seed dates** when a CSV attachment defines them
- [ ] **No `see Description` in Data** — inline seed on each step (alias, summary, dates or key when known)
- [ ] **Close Add Time dialog** when a step opens ATD and the flow continues in the host view
- [ ] **Empty aliases** match actual seed overlap (partial-date assignments may still show tasks)
- [ ] **Description** uses bullet lists for preconditions/seed — no pipe tables
- [ ] Preconditions achievable on develop/review E2E tenant (seed noted in Description when needed)
- [ ] No duplicate cases that differ only by one filter value
- [ ] Open assumptions listed (Preliminary)
- [ ] No secrets in Data
- [ ] No claim that tests were saved to XRay/Jira

## Comparison note (platform `story-ui-test-cases`)

| Their skill | This skill (Timetracker) |
|-------------|--------------------------|
| Requires `@story-testability` scan first | Grounds in **repo code** + Jira story; scan optional |
| Linked Q / F# columns | **Open assumptions** + Jira/AL-* traceability in Summary |
| Happy path from story only; edges if story says | **Edges encouraged** from platform patterns (access, empty, pagination) |
| Steps without separate Data column | **Action + Data + Expected Result** (E2E convention) |
| Internal TC-01 IDs | **Do not use** — **Summary** primary; **TTQA-*** when user/Jira supplies it; `TS-*` for repo folders |
| Generic XRay CSV | **Action, Data, Expected Result** only (no Scenario / TTQA key in CSV) |

Use both: story-testability for **story gaps**; this skill for **Timetracker execution format** and **code truth**.

## Anti-patterns

- **Invented `TTQA-*` or `TC-01` IDs** — use Summary until Jira assigns a key; if user gives `TTQA-324`, use exactly that
- **Copying an old spec verbatim** when Jira steps or current UI differ — examples are patterns, not law
- **Automating with `` testStep(`…${var}…`) ``** — step titles must be static `"..."` literals copied from Jira (AutomatingTestCases skill)
- **Jira Data out of date** — e.g. still `6 weeks in the future` after isolation moved to `10 weeks in the future`; update Jira, then Playwright literals
- **Wrong scenario id** — writing `TS-5` when registration uses `TS-5a` / `TS-5b`
- **Invented or copied `KAN-*` / `SUG-*`** from unrelated automation cases — ask the user for key, summary, and id
- **`see Description` in Data** — put `alias: [summary] (start …; due …)` inline on each step instead
- **Pipe tables in XRay Description** — use bullet lists; Jira breaks column alignment
- **Empty-state assertions on days/weeks that still overlap partial-date seed** — verify overlap rules in code or live UI first
- **Manual steps that simulate upstream API failure/retry** when product distinguishes empty, forbidden, and failure states
- **Confusing “no data for user” with forbidden** — successful empty copy ≠ access-denied copy (`translate.ts` / `en.json`)
- **Generic users** (`UserA`, `admin`) without alias + known E2E email in Data
- **Bare calendar dates** or `today`/`yesterday` for seed/empty-state setup — use named periods or relative offsets
- Vague expected results on **system messages** (empty state, errors must be exact)
- Invented business rules without assumption label
- 30-step mega cases
- One TC per audit action instead of platform + domain layers
- Spec/Miro labels without checking code
- Auto-import to XRay/Jira

## Blocked actions

- Auto-create or auto-import in XRay/Jira
- Generating API contract test suites as UI TC tables
- Claiming “tests saved to XRay”
