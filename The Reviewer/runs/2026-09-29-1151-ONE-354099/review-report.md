# Requirement Review — 2026-09-29-1151-ONE-354099

**Scanned:** Initial scan — 2026-09-29  
**Scope:** Epic — [ONE-354099](https://appfire.atlassian.net/browse/ONE-354099) — "Undo button works with any change" · Status: Open  
**Product:** BigPicture · schema 1.1  
**Data sources analyzed:** Target issue (ONE-354099) · Acceptance criteria field · Comments on ONE-354099 · Child inventory + content · Issue links and subtasks · Confluence: PRD - [2026/H2] Spreadsheet-like navigation in BigPicture (page 99074146305) · Confluence: Embers 2026 Q4 planning (page 99820732524)  
**Data sources unavailable or failed:** none

**Readiness for test planning:** Needs clarification before scope can be tested  
_Seven High findings stand between this epic and a testable scope — chiefly the undecided multi-undo model and limit (RR-ONE-354099-01, RR-ONE-354099-02, Q1) and the redo and exclusion boundary (RR-ONE-354099-05, Q2) — and the epic has no child items yet (Q5)._  
No child issues are linked yet; address the findings below before individual child scans.

**Testability:** Low · **Test scope confidence:** Low · **Risk:** High (data integrity, regression surface) · **Automation candidate:** TBD

## Findings

| ID | Severity | Checklist ref | Finding | Testing impact | Owner |
|----|----------|---------------|---------|----------------|-------|
| RR-ONE-354099-01 | HIGH | A6 | The interaction model for undoing more than one operation is left open between Options A, B and C in the epic's own Questions section, while the Definition of done already assumes multi-change undo. | Cannot define the multi-undo flow, its selection rules or its UI to test until one option is chosen. | PO |
| RR-ONE-354099-02 | HIGH | A3 | Definition of done item "User can revert last X changes" leaves X undefined; the Questions section says only "we can investigate technical feasibility 5 or 10". | No pass/fail assertion on the undo-count limit is possible until X is set. | PO |
| RR-ONE-354099-03 | HIGH | A6 | Whether older changes stay revertible when the most recent one cannot be undone is raised as open, with only a "mild suggestion" and no decision. | Negative-path tests for the undo history after a failed undo cannot be scoped. | EM |
| RR-ONE-354099-04 | HIGH | A2 | No out-of-scope note exists although the change touches shared systems (field editing, bulk actions, scheduling, structure), and the "some exceptions" datatypes are never listed. | Cannot build the field/datatype coverage matrix or know which fields should refuse undo. | PO |
| RR-ONE-354099-05 | HIGH | A4 | The linked PRD names this epic "Undo/redo support for more fields", but the epic's scope and Definition of done mention undo only; redo is neither in nor out of scope. | Whether a whole redo test surface exists is unknown, so the epic's test scope cannot be bounded. | PO |
| RR-ONE-354099-06 | HIGH | B12 | The epic describes four delivery phases but has no child work items, so no child description owns any phase; the Q4 planning page nonetheless marks it "Ready for Q4? Yes" with a start date of 2026-10-26. | No child can be scanned or test-planned yet; epic-level coverage cannot be mapped to any story. | PO |
| RR-ONE-354099-07 | HIGH | A5 | No design reference exists (UX Design status "To decide", PRD Design Artifacts empty, no Figma link) although the Definition of done implies UI validation: an error message is displayed, and Options B and C describe a selectable list of actions. | UI assertions for error messages and any multi-undo list cannot be written without a design reference. | UX |
| RR-ONE-354099-08 | MEDIUM | B4 | Bulk actions are in scope, but undoing a bulk action where only some items were changed by someone else in the meantime is not described (whole undo refused, partial undo, or per-item errors). | Bulk-undo conflict tests cannot state an expected result; the single-item error path stays testable. | EM |
| RR-ONE-354099-09 | MEDIUM | B8 | The lifecycle of an undoable action is only partly stated (survives refresh, expires after 8 hours, refused after a conflicting change); what happens to the history after an undo, or when a new change supersedes an undoable one, is not described. | State-transition coverage of the undo history is limited to the three stated rules. | EM |
| RR-ONE-354099-10 | MEDIUM | B9 | The performance impact of raising the undo limit is named by the epic's author as an open investigation, with no target stated. | No performance acceptance threshold exists for undo with a longer history. | EM |
| RR-ONE-354099-11 | MEDIUM | C1 | Neither the epic nor the linked pages name how the change is released: no feature flag, staged rollout, or statement that it ships to everyone at once, although phase 1 replaces the existing dates undo. | Cannot plan flag-on/flag-off regression of the existing dates undo during rollout. | PO |
| RR-ONE-354099-12 | LOW | B11 | Event sourcing is named as the mechanism, but no logging, audit or metrics for undo actions themselves are mentioned. | Support/debug signals for undo cannot be verified. | EM |
| RR-ONE-354099-13 | LOW | B10 | No test environment, fixture or data note for exercising undo across many datatypes, concurrent editors, or the 8-hour expiry. | Test setup for concurrency and expiry must be designed from scratch. | EM |
| RR-ONE-354099-14 | LOW | C3 | Tracking fields tell different stories: the Q4 planning page marks the epic ready, while it has no children, no fix version, and UX Design status "To decide". | Low impact now; worth aligning before sprint planning picks it up. | PO |

## Clarification questions

### Definition of done

#### Q1. Which multi-undo model ships — Option A (most recent only), Option B (a list, reverting from the most recent down with no skips) or Option C (chainable/non-chainable)? And, for that option, what is X in "User can revert last X changes", and is the 8-hour time limit confirmed?
- Context: The Definition of done assumes multi-change undo and an 8-hour expiry, while the Questions section leaves both the option and the limit open ("5 or 10", "I suggest" 8 hours). Option A would make X a fixed one. Resolving X also frames the performance question in RR-ONE-354099-10. · Source: Description — Definition of done; Questions section · Priority: High · Unblocks: RR-ONE-354099-01, RR-ONE-354099-02, RR-ONE-354099-10 · Owner: PO

### PRD authority

#### Q2. The PRD lists this epic as "Undo/redo support for more fields", but the epic mentions only undo. Is redo in scope? And which fields or datatypes are the "some exceptions" that stay out of scope?
- Context: The PRD and the epic disagree on redo, and the epic has no out-of-scope list for a change that touches field editing, bulk actions, scheduling and structure. · Source: Confluence PRD (appfireteam.atlassian.net, page 99074146305) — Features and Functionality; Description — Definition of done · Priority: High · Unblocks: RR-ONE-354099-04, RR-ONE-354099-05 · Owner: PO

### Design authority

#### Q3. Will a design reference be produced for the undo error messages and any multi-undo list, and before which phase?
- Context: UX Design status is "To decide" and the PRD's Design Artifacts row is empty; phase 1 is backend-only, but later phases add UI. · Source: Custom field UX Design status; Confluence PRD — Project Summary · Priority: High · Unblocks: RR-ONE-354099-07 · Owner: UX

### Rollout

#### Q4. How will the new backend undo be released — behind a feature flag (name, default, who flips it), staged, or to everyone at once?
- Context: Phase 1 replaces the existing frontend dates undo, so the release path decides the regression plan. · Source: Description — Definition of done · Priority: Medium · Unblocks: RR-ONE-354099-11 · Owner: PO

### Scope

#### Q5. Which child items will carry phases 1–4, and will they exist before the planned start on 2026-10-26?
- Context: The epic has no children, yet the Q4 planning page marks it "Ready for Q4? Yes". · Source: Child inventory (0 children); Confluence: Embers 2026 Q4 planning; custom field Start date (migrated) · Priority: High · Unblocks: RR-ONE-354099-06, RR-ONE-354099-14 · Owner: PO

### Edge cases

#### Q6. If the most recent change can't be undone, can older changes still be undone? And when undoing a bulk action where only some items were changed by someone else, is the whole undo refused, applied partially, or reported per item?
- Context: The epic calls the first part "a mild suggestion" left to technical optimization; the bulk case is not mentioned. · Source: Description — Questions section; Business goal · Priority: High · Unblocks: RR-ONE-354099-03, RR-ONE-354099-08 · Owner: EM

## Not stated in epic

- Which multi-undo option ships, and the value of X.
- Whether redo is in scope (the PRD says undo/redo; the epic says undo).
- Which fields or datatypes are the "some exceptions" — no out-of-scope list.
- Whether older changes stay revertible when the most recent can't be undone.
- How undo of a bulk action behaves when only some items conflict.
- The text of either error message.
- What happens to the undo history after an undo, or when a newer change supersedes an undoable one.
- A design reference for any UI part of the change.
- A performance target for a longer undo history.
- How the change is released (feature flag, staged, or all at once).
- Logging, audit or metrics for undo actions.
- Test environment or data for concurrency and expiry.
- Any child work item for phases 1–4.

## Known or suspected risks

- Undo writes data back across tasks; with scheduling and structure cascades (and the "revert all the chainable operations that happened after to be safe" rule sketched in Option C), an undo could revert more than the user intended. *(Source: Description — Scope of the epic; Questions, Option C)*
- Phase 1 moves the working dates and scheduling undo from frontend to backend, so the existing behaviour is a regression surface from day one. *(Source: Description — Definition of done)*
- Concurrent edits from Jira or other users drive the main error path; conflict detection must be correct for every newly supported field. *(Source: Description — Support for errors)*
- Planning signals readiness for Q4 while the epic has no children, no design reference and open core questions; test planning may start late relative to the 2026-10-26 start. *(Source: Confluence: Embers 2026 Q4 planning; ONE-354099 fields)*

## Suggested testing focus

- Regression of the existing dates and scheduling undo once it runs on backend event sourcing (phase 1).
- Concurrent-change refusal per newly supported field, starting with the Assignee A → B → C example. *(waits on: RR-ONE-354099-04, Q2)*
- Expiry after 8 hours, including a stale browser tab with an apparently active undo button. *(waits on: Q1)*
- Own-changes-only rule and undo surviving a page refresh.
- Multi-undo selection and limit behaviour, once the option and X are chosen. *(waits on: RR-ONE-354099-01, RR-ONE-354099-02, Q1)*
- Bulk-action undo, including partial conflicts. *(waits on: RR-ONE-354099-08, Q6)*

## Information identified

- Business goal: "Currently undo button reverses last dates change. The plan is to make it work with any editable data type. User should be able to reverse status change, assignee change etc with this button. This includes bulk actions." *(Source: Description — Business goal)*
- Must have: undo works with most (or all) fields; Should have: revert more than one change; "Should to have": undo of structure changes, which reverts the structure change, the task's dates, and any other tasks' dates affected through dependencies or parent-child relations. *(Source: Description — Scope of the epic)*
- Four phases: re-create the current single dates undo on the backend; add all (or most) data types and editable fields; add undo of more than one action; add undo of structure changes. *(Source: Description — Scope of the epic)*
- The new mechanism is backend event sourcing; the current dates and scheduling undo "works fine - just needs to be moved to backend". *(Source: Description — Definition of done)*
- "User can only undo changes they did." and "Page refresh does not remove possibility to undo last change." *(Source: Description — Definition of done)*
- An undo is refused with an error when the data changed in the meantime (worked example: Assignee A → B by me, then C by a colleague; undo to A is not possible) or when the operation is more than 8 hours old. *(Source: Description — Definition of done, Support for errors)*
- The undo-count limit is open ("Currently it’s 1, we can investigate technical feasibility 5 or 10"); the 8-hour time limit is offered as "I suggest". *(Source: Description — Questions)*
- The PRD lists this epic as "Undo/redo support for more fields (currently it’s only task dates)" with priority CRITICAL, under an objective to deliver the navigation "by the end of 2026". Its Success Criteria and Design Artifacts sections are empty. *(Source: Confluence PRD, appfireteam.atlassian.net page 99074146305 (v4))*
- The Q4 planning page marks this epic "Ready for Q4? Yes". Its estimate cell, in Polish and cut short with an ellipsis in the page itself, translates as: 1. estimate of a new backend mechanism that keeps date undo, which is what the current undo does; 2. extension of that mechanism with… (text ends there). *(Source: Confluence: Embers 2026 Q4 planning, appfireteam.atlassian.net page 99820732524 (v23))*
- Estimate: backend 4w, frontend 5d. *(Source: Comment @Grzegorz Radynski-Figlarz, 2026-09-09)*
- Status Open; UX Design status "To decide"; Start date (migrated) 2026-10-26, End date (migrated) 2026-11-25; no fix version; team Embers; parent Initiative AEPORT-1240 "BP - Adaptive Hierarchies & Grids". *(Source: ONE-354099 fields)*

## QA readiness checklist (preliminary)

| # | Check | Source | Owner | Done |
|---|-------|--------|-------|------|
| 1 | Confirm the multi-undo option, the value of X, and the 8-hour limit | Pending Q1 | PO | ☐ |
| 2 | Confirm whether redo is in scope and list excluded fields/datatypes | Pending Q2 | PO | ☐ |
| 3 | Confirm a design reference for error messages and any undo list | Pending Q3 | UX | ☐ |
| 4 | Confirm the release path (flag, staged, or all at once) | Pending Q4 | PO | ☐ |
| 5 | Confirm child items exist for phases 1–4 | Pending Q5 | PO | ☐ |
| 6 | Confirm undo-history and bulk-undo behaviour after a conflict | Pending Q6 | EM | ☐ |
| 7 | Regression-check the existing dates and scheduling undo after the move to backend event sourcing | Description — Definition of done | QA | ☐ |
| 8 | Check the concurrent-change error using the Assignee A → B → C example | Description — Support for errors | QA | ☐ |
| 9 | Check the expiry error for an operation older than 8 hours | Description — Support for errors | QA | ☐ |
| 10 | Check that a user cannot undo another user's change, and that undo survives a page refresh | Description — Definition of done | QA | ☐ |

## Child inventory & status mix

**Full inventory — 0 children, paginated to `isLast`, never a sample.**  
**Status mix:** no children yet


## Epic batch handoff

This epic has no child work items yet — both "Epic Link" and parent JQL returned none — so there is nothing to scan individually. Re-run this review once children exist.

No children are recommended for an individual scan.

## Recommended next action

Take Q1, Q2 and Q5 to the PO, Q3 to UX and Q6 to EM; Q4 can follow. Once child items exist for the four phases, rescan this epic and then scan each child.

---
_This review supports shift-left preparation. It does not approve or reject the requirement._
