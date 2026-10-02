---
name: timetracker-playwright-e2e
description: >-
  Implement approved Timetracker TTQA-* cases as Playwright E2E. Jira steps are
  the contract. Ask for test Summary, Jira issue key/summary/id before coding;
  never reuse another TTQA-* issue. Follow TestCaseWriting; testStep titles are plain
  strings only (no ${}); Jira Data is source of truth for date phrases; UTC/timezone
  rules for Weekly worklog seeds; avoid repeat CR mistakes.
disable-model-invocation: false
---

# Timetracker Playwright E2E (AutomatingTestCases)

Implement **approved** Jira `TTQA-*` cases as Playwright specs.

**Read first:** [`TestCaseWriting/SKILL.md`](../TestCaseWriting/SKILL.md) · [`qa-coe/E2E/README.md`](../../README.md) · [`qa-coe/E2E/Timetracker/README.md`](../../Timetracker/README.md)

## What to trust vs what to copy

| Source | Role |
|--------|------|
| **Approved Jira steps** | Contract — `testStep` titles and expected results must match |
| **Product code + live UI** | Truth for selectors, labels, and behavior when implementing |
| **`views/` / `api/` / `selectors/`** | Reuse first — shared automation building blocks |
| **Sibling `TTQA-*.case.ts` (~143 specs)** | **Examples** — import patterns, resolver usage, helper choice; may be outdated (interpolated dates, wrong tooltip asserts, etc.) |
| **`jiraIssueIds.json`** | Authoritative **only** for the **same** `TTQA-*` the user confirmed — never copy from another case |

When an example spec disagrees with Jira or this skill, **follow Jira + skill + code** — do not perpetuate the example’s mistake.

**Do not start implementation** until all of the following are confirmed with the user. If any is missing, **ask explicitly** — do not guess, placeholder, or borrow from another `TTQA-*`.

**TTQA-* exists only after the test is created in Jira** — never invent a number when drafting manual cases; when automating, the user must supply the real key.

| # | Required input | Maps to |
|---|----------------|---------|
| 1 | **Test case key** | `TTQA-87` → file `TTQA-87.case.ts`, export `TTQA_87()` |
| 2 | **XRay / Jira Test Summary** | 2nd argument of `testCase(...)` — exact string from the XRay test issue (e.g. `Weekly View - Hover over worklog`) |
| 3 | **Scenario** | Target folder `specs/TS-<id>/` (e.g. `TS-6b`, `TS-9a`) **and** registration in `TS-<id><suffix>.scenario.spec.ts` (e.g. `TS-5a.scenario.spec.ts`, not bare `TS-5`) |
| 4 | **Approved Jira steps** | Action / Data / Expected Result — finalized text for `testStep` titles and comments |
| 5 | **Jira work item key** (`KAN-*`, `SUG-*`, …) | When steps seed, select, or assert on an issue — **required**; constants + `testStep` Data |
| 6 | **Jira work item summary** | Exact issue **title** as shown in Jira UI (tooltip, ATD, issue panel) — **required** with #5 |
| 7 | **Jira work item id** (numeric) | `fixtures/jiraIssueIds.json` `{ "id", "key", "summary" }` entry for this case — **required** with #5 unless entry already exists for this exact `TTQA-*` + key |

**When steps reference an issue in Data** (`IssueKey1`, `KAN-*`, or `alias: [summary]`): items **5–7 are mandatory**. Grep `jiraIssueIds.json` and `specs/TS-*/TTQA-<same-n>.case.ts` **only** for the **same** `TTQA-*` the user gave — not a sibling case.

**Not asked:** `Stage` is always `Stage.DEVELOP | Stage.REVIEW` for every new case — fixed convention, never prompt the user.

**Prompt template when blocked:**

```text
Before I automate this case, please confirm:
1. Test case key (TTQA-___)
2. XRay / Jira Test Summary (exact testCase title)
3. Scenario folder (TS-___) — e.g. TS-1c
4. Approved steps (CSV or Jira export) — or confirm I should use the attached CSV
5. Jira work item key (KAN-* / SUG-*) — if the flow uses an issue
6. Jira work item summary (exact issue title in Jira)
7. Jira work item id (numeric) — for jiraIssueIds.json
```

**Never do without user confirmation:**

- Reuse `KAN-*` / issue summary from another `TTQA-*` (“existing E2E issue”, “similar case”, “until fixture is reserved”)
- Assume issue details from Description when **Data** lacks inline key + summary — **ask** for concrete key, summary, and id; manual CSV must not use `see Description`
- Implement with a stand-in issue and “update later”
- Add `jiraIssueIds.json` with guessed `id` or summary

After implementation (when #5–7 apply):

- Add or update **`fixtures/jiraIssueIds.json`** with user-provided `id`, `key`, `summary`
- Use the same `ISSUE_KEY` / `ISSUE_SUMMARY` in the spec constants and `testStep` Data strings

After implementation:

- Create `specs/TS-<n>/TTQA-<n>.case.ts`
- Add `TTQA_<n>()` to the matching `TS-<n>.scenario.spec.ts` in the correct order (respect serial dependencies and cleanup hooks in that scenario)

## Jira ↔ code mapping

| Jira | Playwright |
|------|------------|
| **Action** (+ **Data**) | `testStep("…", async () => { … })` — **verbatim from approved Jira**; plain `"..."` only — never `` `…${…}` `` |
| **Expected Result** | `//` comment + `expect*` assertions |
| Preconditions / seed | First `testStep` or API in step 1 |

**Do not deviate while automating** — update Jira first if flow must change.

## `testCase` signature

```typescript
import { Platform, Stage } from "@qa-coe-e2e/core/library/common/config";
import { testCase } from "../../fixtures/timetracker.fixture";

testCase(
  "TTQA-87",                              // ← user-provided key
  "Timesheet - Undo Deletion of a Single Worklog Item in Timesheet", // ← user-provided human-readable / Jira Summary title
  "TIMETRACKER",
  Platform.JIRACLOUD,
  Stage.DEVELOP | Stage.REVIEW,
  async ({ cloudPage, request }) => { /* … */ }
);
```

Product: `'TIMETRACKER'`. Six parameters — no `teamName`. **Stage:** always `Stage.DEVELOP | Stage.REVIEW` — do not ask, do not change.

Register in the matching scenario file, e.g. `specs/TS-5/TS-5a.scenario.spec.ts`:

```typescript
testScenario("TS-5a", "Timesheet", "default", () => {
    TTQA_96();
});
```

Export name: `TTQA_96()` from `TTQA-96.case.ts` (underscore, not hyphen). Special cases follow the file name (e.g. `TTQA_4_e2e_users()`).

### Optional `testCase` options (6th parameter)

When worklogs or gadgets need scoped cleanup, pass options **before** the callback — reuse existing fixture keys; do not add new ones:

```typescript
testCase(
  "TTQA-287",
  "Visual reporting - Bar chart showing hours",
  "TIMETRACKER",
  Platform.JIRACLOUD,
  Stage.DEVELOP | Stage.REVIEW,
  {
    worklogsDeleteDateRange: {
      dateRangeStart: TTQA_287_WORKLOGS_DATE_RANGE_START,
      dateRangeEnd: TTQA_287_WORKLOGS_DATE_RANGE_END,
    },
  },
  async ({ cloudPage, request, cleanUpWorklogs }) => {
    void cleanUpWorklogs;
    // …
  }
);
```

Reference `cleanUpWorklogs` in the callback (`void cleanUpWorklogs`) when the opt-in fixture should run.

## Paths

| Role | Path |
|------|------|
| Specs | `specs/TS-*/TTQA-NNN.case.ts` |
| Scenario registry | `specs/TS-*/TS-<id><suffix>.scenario.spec.ts` (e.g. `TS-5a`, `TS-6b`, `TS-8a`) |
| Views | `views/` — one export per file, filename = function name |
| Selectors | `selectors/` |
| API | `api/` |
| Per-scenario seed | `specs/TS-*/seedTtqa*.ts` — reuse before adding another seed module |
| Issue keys | `fixtures/jiraIssueIds.json` — `KAN-*` mapped to TTQA summaries |

## Reuse before create (mandatory)

**Do not add new helpers, fixtures, or seed modules until you have searched and confirmed nothing suitable exists.** Duplicated `views/` exports and extra fixture keys are a common review failure.

### Before every new `views/` file or export

1. **Grep `views/`** for the UI action or assertion (verb + area): e.g. `clickWeekly`, `expectTimesExplorer`, `Custom Rules`, `AddTimeDialog`.
2. **Grep sibling specs** in the same `TS-*` folder as **examples**: `specs/TS-<n>/TTQA-*.case.ts` and any `seedTtqa*.ts` — copy import/resolver patterns from the closest case, then align with **Jira steps** and this skill (examples can be wrong).
3. **Check `@qa-coe-e2e/core`** and **`@qa-coe-e2e/jiracloud`** for shared navigation, login, and Jira shell helpers.
4. **Check `selectors/`** — add a selector there only when no existing selector covers the element; do not inline duplicate selectors in a new helper if one already exists.
5. **Only then** add a new file under `views/<area>/` (or `views/<area>/expected/` for assertions).

**Reuse rules:**

| Need | Do | Do not |
|------|-----|--------|
| UI click / fill / navigate | Import existing `views/` export | Copy-paste locator logic into the spec |
| Assertion | Import existing `views/.../expected/expect*` | New `expect*` that differs only by a string literal — extend the existing helper’s params |
| API seed / cleanup | Reuse `api/*`, `setup/ts6CaseCleanup.ts`, scenario `seedTtqa*.ts` | New seed file when an existing seed covers the same worklog shape and date range |
| Date isolation | Entry in `config/parallelTestDateIsolation.ts` + resolver call | Ad-hoc `moment()` offsets that collide with another `TTQA-*` in the same scenario **or another parallel worker** |
| Opt-in cleanup | Existing fixture keys (`cleanUpWorklogs`, `worklogsDeleteDateRange`, `cleanUpVisualReportingGadgets`) | New keys in `fixtures/timetracker.fixture.ts` without explicit user approval |
| Issue key | User-confirmed entry in `fixtures/jiraIssueIds.json` for **this** `TTQA-*` | Invent `KAN-*`, copy from unrelated `TTQA-*`, or reuse “any existing E2E issue” |

**Fixtures (`fixtures/timetracker.fixture.ts`):** infrastructure only — `cleanUpWorklogs`, `worklogsDeleteDateRange`, `cleanUpVisualReportingGadgets`, auto hooks. **Never** add product navigation, iframe resolution, or per-case setup as fixture keys. **Never** create a second fixture file for Timetracker unless the user explicitly requests a `mergeTests` split (see `educationalExamples/README.md`).

**Filename = exported function** — before creating `clickFooBar.ts`, confirm `clickFooBar` / `expectFooBar` is not already exported from another path.

### Helper search order

1. Same-`TS-*` / same-theme `TTQA-*.case.ts` — **example** specs for structure (not override Jira/skill)
2. `qa-coe/E2E/Timetracker/views/` (400+ helpers) — prefer over inventing from product code
3. `qa-coe/E2E/Timetracker/api/` and scenario `seedTtqa*.ts`
4. Product UI code (`jira/services/Jira-UI`, `@7pace/components`) — when adding a **new** helper and no `views/` match exists
5. `@qa-coe-e2e/core` (`testCase`, `testStep`, `testScenario`)
6. `@qa-coe-e2e/jiracloud`

## Parallel workers — calendar clashes (read before new date bands)

Fast CI runs **many scenarios on 8 workers** with **one shared E2E user**. Isolation is per `TTQA-*` via `config/parallelTestDateIsolation.ts`, not only “serial within one scenario file.”

**Exemplar (TTQA-70 flaky, Expected 3 / Received 4):**

| Case | Band | What happened |
|------|------|----------------|
| **TS-4** (`TTQA-42` seed / **TTQA-70**) | Full calendar month at **+2 months** (`TTQA_42_SCENARIO_MONTH`); narrow UI range **day 3–16** expects **3** seeded rows |
| **TS-1c** (**TTQA-44**) | Worklog on **ISO week + N weeks forward** (worklog day = week start **+ 5 days**) |

A **fixed** `+6 weeks` forward put TTQA-44’s worklog on **06/Nov** while TS-4 used **November** — inside TTQA-70’s **03–16** window. TTQA-44 ran on another worker **after** TTQA-70’s full-month assert → Times Explorer showed **KAN-28 / `TTQA-44 worklog1`** as a fourth row. Fix: `resolveTtqa44WeeksForward()` in `parallelTestDateIsolation.ts` picks the **smallest** N ≥ 6 so that worklog day is **outside** the TS-4 (+2 month) scenario month.

When adding **forward** weeks/months near **+2 months**, grep `TTQA_42_SCENARIO_MONTH` / `seedTtqa42TimesExplorerWorklogs.ts` and confirm no overlap on the worklog day you seed. If `resolveTtqa44WeeksForward()` (or similar) changes N, **update approved Jira Data first** (e.g. `10 weeks in the future`), then the same phrase in `testStep` literals — optional module-load assert in the spec (see `TTQA-44.case.ts`).

## `testStep` titles — static string literals only (Jira is source of truth)

Every `testStep` first argument must be a **plain `"..."` string literal** copied from **approved Jira** Action + Data. **Never** use template literals or **`${…}` interpolation** — not for dates, issue keys, durations, or resolver output.

| Do | Do not |
|----|--------|
| `testStep("Open Weekly Module and go to week. week: 10 weeks in the future. Totaltime: 30m", …)` — exact Jira Data | `` testStep(`week: ${weeksForwardLabel}`, …) `` or any `` `${…}` `` in the title |
| `testStep("Open Timesheet … Week1: 5 months ago …", …)` matching Jira | Build step titles from `formatWeeksForward`, `moment()`, or constants “to stay DRY” |
| Change **Jira** when isolation band moves, then paste the new phrase into code | Leave Jira at `6 weeks in the future` while code/resolver uses `10` |

**Isolation vs Jira:** `parallelTestDateIsolation.ts` decides **which calendar** to seed (may compute N to avoid parallel clashes). **Jira Data** states the **strict relative label** testers and reports see (`10 weeks in the future`, `03/2 months in the future`, etc.). Playwright **only mirrors Jira** in step titles; seed code uses resolvers. When N changes, workflow is: adjust resolver → **update Jira steps** → copy strings into `testStep` → optional assert `formatWeeksForward(weeksForward) === JIRA_…_LABEL` at file top (`TTQA-44`).

Constants (`ISSUE_KEY`, durations) belong in the spec body and assertions — not interpolated into step names. Example specs that use `` `${…}` `` in `testStep` are **outdated**; do not copy that pattern.

## Dates in `testStep` titles and seed data

Parallel workers share one E2E user — cases use **isolated calendar offsets**, not literal “today” in step text when automation uses a shifted date.

### Rules

- **No placeholder dates** — never `today`, `yesterday`, `some date`, `TBD`, or a bare calendar date in `testStep` without a defined offset **that appears in Jira Data**.
- **Use the exact relative labels from Jira** in `testStep` strings:
  - `5 months ago`, `38 months back`, `3 months in the future`, `10 weeks in the future`
- **No `${…}` in `testStep` titles** — see **static string literals only** above
- **In code:** derive `startedAt` / navigation via `config/parallelTestDateIsolation.ts` — must match the **same** band as Jira’s phrase (after Jira is updated when the band moves).
- **New case with isolated dates:** add the `TTQA-*` entry to `parallelTestDateIsolation.ts` (see file header). If N is computed to avoid another worker’s month, **still** put the resulting phrase in Jira; do not drive step titles from the resolver at runtime.

### Good vs bad

```typescript
// ✅ GOOD — verbatim Jira; resolver matches in code (not in the title)
await testStep(
  "Open Timesheet and go to Week1. Week1: 5 months ago, issueKey: KAN-58, Date1: Sunday 5 months ago, Time1: 02:00",
  async () => { /* resolveTs5Week("TTQA-96") */ }
);

await testStep("Open Weekly Module and go to week. week: 10 weeks in the future. Totaltime: 30m", async () => { … });

// ❌ BAD
await testStep(`Open Weekly Module and go to week. week: ${weeksForwardLabel}.`, async () => { … });
await testStep("Open Timesheet for today", async () => { … });
await testStep(`Delete and seed one worklog via API. IssueKey1: ${ISSUE_KEY}`, async () => { … });
```

When Jira **Data** says a relative period, copy that **exact** wording into `testStep` — character for character.

## Worklog times, browser timezone, and day headers

API `startedAt`, weekly `th[data-date="…"]`, and on-screen clock times must describe the **same calendar day**. Mismatch is a common failure mode (`expectWeeklyTotalTimeForDayHeaderVisible` timeout, or card time regex never matching).

### Rules

1. **Pin browser timezone** when the case asserts clock times on Weekly view (card range, hover, day header tied to a seeded worklog):
   ```typescript
   export function TTQA_59(): void {
       test.use({ timezoneId: "UTC" });
       testCase(/* … */);
   }
   ```
   Reference: `TTQA-28`, `TTQA-59`.

2. **Seed `startedAt` on the same calendar day as `targetDate.format("YYYY-MM-DD")`** when using `test.use({ timezoneId: "UTC" })`:
   ```typescript
   // ✅ BEST — runner-TZ-independent; hour 9 in UTC on the same data-date as the day header assert
   const WORKLOG_STARTED_AT = moment.utc(`${targetDate.format("YYYY-MM-DD")}T09:00:00.000Z`).toDate();

   await expectWeeklyTotalTimeForDayHeaderVisible(
       frame,
       targetDate.format("YYYY-MM-DD"),
       "1h 00m"
   );
   await expectWeeklyWorklogCardTimeRange(frame, card, /9:00 am - 10:00 am/i);
   ```

   ```typescript
   // ✅ OK on UTC CI runners only — local .set({ hour }) follows Node TZ, not browser TZ
   targetDate.clone().set({ hour: 9, minute: 0, second: 0, millisecond: 0 }).toDate();
   ```

   ```typescript
   // ❌ BAD — .utc() before .set() on a local moment shifts the calendar day
   targetDate.clone().utc().set({ hour: 9, minute: 0, second: 0, millisecond: 0 }).toDate();
   ```

   Resolvers use `moment()` in the **runner** timezone; `test.use({ timezoneId: "UTC" })` affects the **browser** only. Do not “fix” drift by asserting a different `data-date` than `targetDate` — fix the seed chain instead.

3. **Match UI time format** in regex/assertions (`/9:00 am - 10:00 am/i`), not 24h `09:00.*10:00` unless the UI shows 24h.

4. **Weekly hover — where times live:**
   - **Card inline** `.from-to-container` — default for hover cases (`TTQA-59`): `expectWeeklyWorklogCardTimeRange(frame, card, pattern)` **without** `tooltipFilterText`.
   - **Tooltip** — project / issue type / summary / billable via `expectWeeklyWorklogCardTooltipContents`; **do not** expect start/end in tooltip unless verified in UI (TTQA-59 tooltip has no times).
   - **`tooltipFilterText`** — only when the card has `data-timeframe-hidden` **and** the tooltip actually contains the time range (some resize/edit flows — `TTQA-28`).

5. **`TTQA-44` pattern** (`.utc().set({ hour })` without `test.use({ timezoneId: "UTC" })`) exists for legacy cases — **prefer the TTQA-28 pattern** for new Weekly seeds + time assertions.

## Forge / iframe model

- `getTimetrackerFrame(cloudPage)` → `FrameLocator`; pass **`frame` first** in helpers
- After `page.reload()` or long serial runs → `resetTimetrackerFrameResolutionCache(page)`
- Nested iframes → `pickForgeFrameWithMarker(page, selector)`
- ATD → `resolveAddTimeDialogFrame` + cache reset + `expect().toPass()` after filter popups

## Date pickers — ATD vs Approval settings (do not reuse selectors)

| Surface | Component | Locators / asserts |
|---------|-----------|-------------------|
| **Add Time / ATD** | Jira `MultiDayDatePicker` | `[data-testid="multi-day-date-picker"]`, `expectAddTimeDatePickerDayNonWorkingState` + `resolveAddTimeDatePickerLookupScope` |
| **Approval periods → schedule Start date** | `@7pace/design` `DatePickerSlot` (react-datepicker) | `[data-testid="date-picker-select--container"]`, `role="grid"`, day `getByRole("button", { name: "D, dddd MMMM YYYY" })` — see `fillDatePickerInApprovals`, `expectApprovalStartDateCalendarVisible`, `expectApprovalStartDatePickerDayNonWorkingState` |

**Wrong:** `addTimeSelectors.datePickerPopover` on Approval settings — that test id exists only on ATD multi-day picker; the approval calendar is already open in the snapshot as `grid "September 2026"` with `aria-label` day buttons.

## Code review lessons — do not repeat

### 1. Stale Forge context after settings changes

**Wrong:** save Custom Rules / timer limit → immediately `visitJiraIssueByKey` from Settings host.

**Right:** `clickGoBackButtonIfVisible` → `reloadTimetrackerPage` / `openTimetrackerModuleFresh` → then issue panel (TTQA-309 class).

### 2. Iframe cache invalidation

Portal popups invalidate cached `FrameLocator`. Reset cache, retry `pickForgeFrameWithMarker`, wrap in `expect().toPass()`.

### 3. Error handling — do not swallow with `.catch(() => undefined)`

**Wrong:** attach `.catch(() => undefined)` (or `.catch(() => {})`) to navigation, reload, API calls, or `page.evaluate` so failures disappear.

**Right:**

- Let the step fail when a required action fails (`await reloadTimetrackerPage(page)`).
- For **optional** probes (e.g. “is this overlay visible?”), use an explicit sentinel such as `.catch(() => false)` on `.isVisible()` only — not on full flows.
- For best-effort cleanup after a visibility check, use `try` / `catch` with a narrow scope and a short comment — still avoid masking errors on the main path.

Grep new/changed files for `.catch(() => undefined)` before finishing.

### 4. Playwright strict mode

One element per action/expect. Avoid `.or()` when both branches visible. Prefer `data-testid`, scoped parent.

### 5. Selectors and helpers

- Prefer **`data-testid`**
- **Search before create** — see **Reuse before create**; no duplicate `views/` exports or fixture keys
- **No speculative helpers** / dead code
- **Filename = exported function**

### 6. Assertions discipline

- Expect before/after transitions
- Weekly card **clock times** → card `.from-to-container` via `expectWeeklyWorklogCardTimeRange` (see **Worklog times, browser timezone, and day headers**); tooltip only when it actually shows start/end and the card hides inline times
- Weekly hover **metadata** (project, summary, billable) → `expectWeeklyWorklogCardTooltipContents`
- Issue panel delete → `waitForDeleteWorklogIssuePanelDialogScope`
- Insights → `ensureTimetrackerInsightsExpanded` first

### 7. Feature flags and environment

- `endTimeAnchoredEnabled`: two ATD models — PW E2E tenant keeps it **off**; check flag before “fixing” selectors
- PR runs: **`pnpm run e2e:target --pr=N --env=M`** — not `--pr` on `qa-coe-e2e-ui` directly

### 8. Data and cleanup

- `getTimetrackerJwt` + `createWorklogViaApi` / `deleteAllWorklogsByDateRange`
- TS-6: `setup/ts6CaseCleanup.ts` — standard `try { … } finally { await cleanup*(cloudPage) }` (`cleanupApprovalSchedule`, `cleanupTimeLimitations`, `cleanupSearchFilters`, `cleanupTrackingDetails`); failure-only `teardownCompleted` + `cleanup*AfterFailure` for TTQA-83, TTQA-265; TTQA-368/TTQA-374 use inline failure cleanup (happy path resets in last step); staged CI runs one orchestrator `resetTenantSettingsForE2e` before TS-6a→b→c — don’t invent per-case teardown

### 9. Coverage scope

- Platform shell once (access, filters, pagination); domain smoke separately
- Backend integration owns mapping fidelity

### 10. Step fidelity

- Don’t rename steps vs Jira during “cleanup”
- Cypress → Playwright: same step names as Jira

## ATD / issue panel quick refs

| Area | Pattern |
|------|---------|
| Forge inline ATD | Skip assignee helpers |
| Duration | `expectAddTimeDialogDurationValue` |
| Time on items | `child-issue-${issueKey}` (TTQA-91) |
| Timer after settings | Reload + fresh panel |

## Add Time dialog (`endTimeAnchoredEnabled` off on PW E2E)

FROM fixed; quick-picks advance TO. Example: FROM `09:00`, +0.5h → TO `09:30`, duration `00:30`. Do not mix with anchored-TO model.

## Verification

```bash
pnpm run e2e:target --pr=<N> --env=<M> --case=TTQA-XXX
pnpm run e2e:ui
```

Reports: `qa-coe/E2E/Timetracker/dist/report/`

### Mandatory self-review after any E2E change

Whenever you add or edit files under `qa-coe/E2E/Timetracker/` (specs, `views/`, `api/`, `selectors/`, `config/parallelTestDateIsolation.ts`), **re-read this skill** and confirm before finishing:

| Check | Action |
|-------|--------|
| `testStep` titles | Plain `"..."` only — **grep the diff for `` ` `` and `${`**; no runtime labels (`monthsAgoLabel`, `formatWeeksForward`, issue keys) in step names |
| Jira alignment | Step text matches approved Action/Data; TS-5 week band uses literal **`5 months ago`** when resolver is `resolveTs5Week` (anchor 5) |
| Parallel isolation | New/changed date band → `TTQA-*` entry in `parallelTestDateIsolation.ts` |
| Reuse | Grep `views/` / `api/` before new helpers; no duplicate `expect*` / seed logic |
| Playwright | Locator `expect` with auto-retry; avoid one-shot `expect(value).toBe` on async UI state |
| Error swallowing | **Grep for `.catch(() => undefined)`** — do not use on navigation, reload, API, or required `evaluate`; let failures surface |
| Fixtures | No new fixture keys without user approval; `jiraIssueIds.json` only with confirmed id/key/summary |

If a sibling spec uses `` `${…}` `` in `testStep`, treat it as **outdated** — fix the file you touched; do not copy the pattern.

## Anti-patterns

- Starting without **key, Test Summary, scenario, and (when applicable) Jira work item key + summary + id** confirmed by the user
- **Blind copy from an old `TTQA-*.case.ts`** when Jira steps or this skill differ — treat examples as patterns only
- **Stand-in issue keys** (e.g. `KAN-23` from another case) with a note to update later
- **New `views/` helper, fixture key, or `seedTtqa*.ts` without grep-first reuse check**
- Duplicating an existing `expect*` / `click*` with a one-line parameter change instead of extending the original
- Renaming `testStep` away from Jira
- **Template literals or `${…}` in `testStep` titles** — use plain `"..."` only (copy Jira)
- **Jira / code mismatch** — Jira still says `6 weeks in the future` while resolver moved to 10; update Jira, then literals
- Vague dates in `testStep` titles (`today`, `yesterday`, bare calendar dates, `TBD`)
- **`.utc().set({ hour })` on resolver `targetDate`** while asserting `targetDate.format("YYYY-MM-DD")` with `test.use({ timezoneId: "UTC" })` — shifts worklog to previous/next day vs day header
- **Worklog time regex in hover tooltip** when tooltip has no start/end (assert on card `.from-to-container`)
- Giant specs without `views/` extraction (but also: extracting helpers that already exist elsewhere)
- **`.catch(() => undefined)`** on required awaits (reload, navigation, API, `evaluate`) — hides real failures
- `sleep` instead of GraphQL `operationName` wait
- Flake fix by removing assertions
- Automating every manual TC — pick **E2E candidates** from TestCaseWriting table
- Adding `TTQA_*()` to a scenario file without checking serial order / per-case `finally` cleanup in that `TS-*`
- Registering in `TS-5.scenario.spec.ts` when the repo uses **`TS-5a` / `TS-5b`** suffix scenario ids

## Blocked actions

- Implementing with **assumed or borrowed** `KAN-*` / issue summary from another `TTQA-*`
- Adding `jiraIssueIds.json` rows without user-provided **numeric id** and **exact issue summary**
- Changing Jira step text only in code without Jira update
- Skipping cleanup hooks in serial `TS-*` scenarios that mutate tenant settings
