---
name: story-ui-test-cases
description: >-
  Draft manual and Playwright-oriented UI E2E test cases in XRay-compatible
  format for user-facing stories. Run after @story-testability scan
  (ideally after rescan). Links TCs to scan Q# and F#. Does not create tests
  in XRay. Use for UI test cases, E2E candidates, or XRay draft after
  testability scan. Self-contained single-file skill for platform agents.
disable-model-invocation: true
---

# Story UI Test Cases

Draft **manual UI** and **UI E2E automation candidates** only. Not API/integration/unit test design.

## Execution contract (Hive MCP + Cursor) — mandatory

When loaded via `hive-mcp__load_skill` or `hive-mcp__run_skill`, **do not stop** after metadata or `noop`. In the **same turn**, produce the full TC draft per **Output template** below.

**Resolve issue key:** `arguments.issueKey`, parse `arguments.prompt` for `([A-Z][A-Z0-9]+-\d+)`, or user message (e.g. `@story-ui-test-cases PROJ-123`).

If no prior `@story-testability` scan for that KEY in this chat → ask for scan or run `scan {KEY}` first (unless user pasted story content — then Preliminary only).

**Forbidden end states:** skill loaded only; empty tables; claiming XRay/Jira publish.

## Quick invoke

| You type | Result |
|----------|--------|
| `@story-ui-test-cases PROJ-123` | TC draft from scan in chat |
| `generate test cases for PROJ-123` | Same — confirm scan context |

**Epic:** do not call this on the epic key for full child coverage. After `scan EPIC` → `confirm batch` or `scan EPIC --batch`, this skill runs **per recommended child** (Preliminary). Or manually: `scan ONE-xxx` then `@story-ui-test-cases ONE-xxx`.

**Prerequisite:** `@story-testability` scan in the **same chat** (ideally **after rescan**).

**Output language:** English only, no exceptions — same rule as `@story-testability` (see its **Blocked phrases** section).

**TC status label — single source of truth** (supersedes any other mention of Preliminary/Final in this file):

| Condition | TC status |
|-----------|-----------|
| Rescan in this chat, and readiness is **Ready with clarifications** or better (no open High F#) | **Final draft** |
| Rescan in this chat, but ≥1 open **High** F# or High Q# remains | **Preliminary draft — contains assumptions that must be confirmed** |
| Initial scan only (no rescan), readiness **Ready with clarifications** and only Optional questions open | **Final draft** — note which Optional items remain |
| Initial scan only, any open High F# or High Q# | **Preliminary draft — contains assumptions that must be confirmed** |
| No scan — user pasted story content directly | **Preliminary draft — contains assumptions that must be confirmed** |

The status depends on **open High-severity items**, not on rescan-vs-initial alone — a clean initial scan can be Final; a rescan that still has open High findings stays Preliminary.

The **scan report** contains no assumptions — only facts, findings (F#), and gaps. **Assumptions are allowed only in this TC output**, listed under **Open assumptions** and linked to Q# / F#.

**XRay:** compatible format for copy/import. **No changes are made in XRay or Jira.**

## When to run

| Testing scope type (from scan's **Story type** field) | Action |
|------------------------|--------|
| User-facing UI | Generate UI TCs |
| Mixed UI + backend | UI TCs + **Backend testing focus** (bullets, no API TC tables) |
| API/backend only | **Do not** generate TC table — testing focus + recommended areas only |
| Config / infrastructure | Config verification checks only if user-facing |
| Discovery / planning | Decline TC generation; offer review checklist from scan instead |

**Forge** is not a skip rule — classify by whether users interact with UI.

**Naming note:** "Testing scope type" here is the scan's functional classification (User-facing UI / Mixed / API-backend / Config / Discovery) — do not confuse with the Jira **issue type** (Story/Bug/Task/Epic) shown in the scan's HTML header.

## Workflow

```
Confirm story KEY + scan context in chat (or ask for scan first)
→ Determine Final vs Preliminary status
→ Map open Q# / F# from scan to assumptions and Linked Q column
→ Generate manual TCs + E2E candidates (see **Output template** below)
→ Optional CSV block (see **XRay format** below)
→ Note rescan trigger if story still has open High Q# / F#
```

Follow inline sections below: **Handoff**, **Output template**, **XRay format**, **Examples**.

## Output structure

Use **Output template** section below every time.

## Manual TC rules

- Observable steps and expected results — no hidden state
- Happy path only from **stated** story content; edge/error cases only if story mentions them OR explicitly labeled as assumption pending Q#
- Do **not** invent business rules — mark as assumption with Q# / F#
- **Linked Q** column: Q1, F2, or `—` when fully stated
- Typical count: **5–15** manual; **2–5** E2E candidates (skip E2E section if none qualify). If the scan's open items would genuinely require more than 15 manual TCs, group by the scan's F# dimension (e.g. "Permissions", "Boundaries") and generate the top group(s) tied to **High** findings first; note in the output that additional groups are available on request rather than silently truncating
- **Priority column** is derived, not free-choice: inherit the severity of the F# a TC is `Linked Q`/traced to (High F# → High priority TC). A TC with no linked F#/Q# (fully stated behavior) defaults to **Medium** unless the scan's **Risk level** for the story is High, in which case use High
- **TC ID stability across regeneration:** when regenerating after a rescan, keep the same `TC-0N` / `E2E-0N` ID for a test case whose intent is unchanged, even if wording is refined — only assign a new ID to a genuinely new test case. Note in the output which IDs were updated in place vs newly added, so a user who already copied IDs into XRay isn't silently desynced
- **Design facts from the scan:** if the testability scan includes **Design observations (Figma)**, **Screenshot observations**, or a **Spreadsheet change checklist**, prefer those as concrete `Expected` values (quote the exact string) over a generic assumption — tag Figma-backed expectations as `*(per Figma — {url}, node {nodeId})*` in the Expected column or as a footnote on the row. This reduces Open assumptions; Figma does not by itself clear open High F# on behavior not shown in design

## E2E candidates

"E2E" = **UI E2E** (e.g. Playwright). Out of scope: API contract suites, unit tests.

Recommend E2E only when scan **Automation candidate** is Yes or behavior is stable and observable after Q# resolved.

## Traceability to scan

| TC element | Link to scan |
|------------|--------------|
| Open assumptions | F# + Q# |
| Linked Q column | Q# that assumption depends on |
| Preconditions | Facts from scan Information identified or **Design observations (Figma)** only, or "Pending Q#" |
| Expected (when available) | Exact strings from scan's **Design observations (Figma)** (preferred for UI labels/states), **Screenshot observations**, or Spreadsheet change checklist — quoted verbatim; Figma rows must cite `per Figma` + URL/node from scan |

## Blocked phrases (same spirit as scan skill)

Story failed · Not ready · Blocked by QA · gate · claiming tests were saved to XRay/Jira

## Blocked actions

- Generating API contract test suites for QA
- Auto-import or auto-create in XRay/Jira
- TC generation for API-only stories (use testing focus bullets)
- Labeling output **Final draft** while any High F# or High Q# is still open in the scan (see **TC status label** table above)

## Handoff back to scan skill

After story changes → `@story-testability` **rescan** → regenerate TCs or patch rows noted in rescan delta.

**Duplicate request:** if `@story-ui-test-cases {KEY}` is invoked again with no new scan/rescan since the last TC generation in this chat, do not silently regenerate from scratch — note that the underlying scan is unchanged and ask whether to reuse the existing draft or regenerate anyway.

## Validation (before output)

- [ ] Status line: Final or Preliminary (with reason, per **TC status label** table)
- [ ] Based on: scan/rescan / pasted content
- [ ] Open assumptions listed with Q# or F#
- [ ] No invented rules without assumption label
- [ ] When scan includes **Design observations (Figma)**: UI copy in Expected uses quoted Figma strings with `per Figma` source; behavioral gaps still use Open assumptions + Q#/F#
- [ ] API-only stories: no TC table
- [ ] XRay import note present
- [ ] No claim of XRay/Jira publish

---

## Platform note (single-file skill)

This file is **self-contained**. Do not expect companion `.md` files.

| Capability | Behavior on platform |
|------------|---------------------|
| TC generation | Manual UI + E2E candidate tables |
| Prerequisite | Prior `@story-testability` scan in same chat/session, or pasted story (Preliminary only) |
| Pairing | Works with `@story-testability` scan output (F# + Q# + readiness line + **Design observations (Figma)** when scan fetched Figma) |
| Figma | Do not call Figma MCP again if scan already included **Design observations (Figma)** — reuse scan quotes; only re-fetch if user pastes a new node URL or scan lacked Figma due to MCP failure |
| XRay | Copy/paste format only — **never** auto-create in XRay/Jira |
| Rescan | After story update, run scan rescan first, then regenerate TCs |

## Inline reference sections

All rules are in this file — no external skill files required.

---

## Handoff from scan skill

## Epic batch (orchestrator)

When **`story-epic-batch-orchestrator`** runs after an epic scan:

- Invoke this skill **once per child key** in the batch set (recommended ≤ 8).
- **Always** label output **Preliminary draft — epic batch run** (even if a lone story scan could be Final).
- Reuse epic **Design observations (Figma)** in Expected only when the child scan does not contradict them — cite `per Figma` from epic or child scan.
- Do not generate a single merged TC table for the whole epic.

## Recommended order

```
@story-testability scan KEY
→ QA review + format for Jira
→ story updated in Jira
→ rescan KEY
→ @story-ui-test-cases KEY
→ export readiness checklist (optional)
```

**Epic:**

```
scan EPIC-KEY → confirm batch (or scan EPIC-KEY --batch)
→ orchestrator runs scan + Preliminary TC per recommended child
→ one HTML: Tab Epic | Tab Batch
```

## When user asks for TC immediately after initial scan

1. Determine status per the **TC status label** table at the top of this file (may still be Final if readiness is high and only Optional items are open — do not assume Preliminary by default)
2. Pull open **Q#** and **F#** from scan in chat — every assumption must link to one
3. Do **not** duplicate scan findings as if they were test steps with pass criteria already decided

## HTML report handoff

If scan HTML includes **tc-handoff** section, user may arrive from report — same rules apply. Do not regenerate scan; use chat context.

## Decline TC generation

Return short message + point to scan checklist when:

- Story type Discovery / planning
- API/backend only
- User has not provided scan or story content

---

## Output template

Copy this structure every time.

```markdown
# UI Test Cases — {KEY}

**Status:** Final draft | Preliminary draft — contains assumptions that must be confirmed
**Testing scope type:** {from scan's Story type field}
**Based on:** {scan label, e.g. "Initial scan — {date}" or "Rescan — {date}"} from this chat | pasted content
**Regenerated from prior TC draft:** {yes — IDs preserved where unchanged | no — first draft}

## Traceability summary
| Open items from scan | Count | Blocks TC IDs |
|----------------------|-------|---------------|
| High Q# | {n} | TC-… |
| High F# | {n} | TC-… |

**Figma from scan:** {none | list URLs + nodes used in TC Expected} — _design reference; build verification still required_

## Manual test cases

| ID | Title | Preconditions | Steps | Expected | Priority | Linked Q |
|----|-------|---------------|-------|----------|----------|----------|
| TC-01 | … | … | 1. … | … | High | Q1 |

## E2E automation candidates

| ID | Title | Why automate | Suggested level | Risk if skipped | Linked Q |
|----|-------|--------------|-----------------|-----------------|----------|
| E2E-01 | … | … | Playwright UI | … | — |

## Backend testing focus
_(Mixed or API-only only — bullets, not TC tables; each bullet ends with `(blocks: Q#)` or `(blocks: F#)` when it depends on an open item, or nothing when fully stated)_
- {area to verify} *(blocks: Q#)*

## Open assumptions
- {assumption} *(depends on Q1 / F2)*

## Out of scope for this draft
- API contract tests, unit tests (QA manual/UI scope only)

## XRay import note
Copy the table or CSV block below into XRay manually. **Nothing is created automatically.**

## CSV (optional)
```csv
Test Type,Test Summary,Test Step,Expected Result,Priority
Manual,...
```
```

---

## XRay format

Manual copy/import — **no automatic XRay API calls**.

## Table columns (in-skill)

| Column | XRay mapping hint |
|--------|-------------------|
| ID | Internal reference (TC-01); optional in XRay |
| Title | Test Summary |
| Preconditions | Precondition or first step context |
| Steps | Test Step (numbered; one row per step in CSV) |
| Expected | Expected Result |
| Priority | High / Medium / Low |
| Linked Q | Traceability only — omit in XRay or put in Description |

## CSV export (multi-step)

One **row per step** — repeat Test Summary for each step:

```csv
Test Type,Test Summary,Test Step,Expected Result,Priority
Manual,Overview natural sort — valid sequence,"1. Open Overview with tasks Task 1, Task 2, Task 10","Tasks appear in order per agreed rule (Pending Q3)",High
Manual,Overview natural sort — valid sequence,2. Verify order matches clarified rule,Order matches PM/dev clarification (Pending Q3),High
```

## E2E candidates

Do not export as XRay Manual steps by default — list in chat table; optional separate Test Type `Automated` if team uses it.

## Labels (manual in Jira/XRay)

Suggest after Final draft: `ui-test-cases-draft`, `automation-candidate` — user applies manually.

---

## Examples

## Example: ONE-323108 — Preliminary (after initial scan)

**Context:** Initial scan only; High F1–F3, Q1–Q3 open. No rescan.

```markdown
# UI Test Cases — ONE-323108

**Status:** Preliminary draft — contains assumptions that must be confirmed
**Testing scope type:** User-facing UI
**Based on:** Initial scan — 2026-09-14 from this chat
**Regenerated from prior TC draft:** no — first draft

## Traceability summary
| Open items from scan | Count | Blocks TC IDs |
|----------------------|-------|---------------|
| High Q# | 3 | TC-01, TC-02, TC-03 |
| High F# | 3 | TC-01, TC-02, TC-03 |

## Manual test cases

| ID | Title | Preconditions | Steps | Expected | Priority | Linked Q |
|----|-------|---------------|-------|----------|----------|----------|
| TC-01 | Overview — task order matches natural sequence | User on Overview; tasks with titles Task 1, Task 2, Task 10 visible *(assumption: title column — Q1)* | 1. Open Overview module<br>2. Observe order of Task rows | Task 2 appears before Task 10; order matches rule confirmed in Q3 *(Pending Q3)* | High | Q1, Q3 |
| TC-02 | Overview — sort applies on load | Same as TC-01 | 1. Reload Overview without user sort action | Order matches natural sequence without manual sort *(Pending Q2)* | High | Q2 |
| TC-03 | Overview — scope Tasks only | Mixed issue types on Overview if available | 1. Compare sort behavior for Task vs non-Task rows | Only Tasks sorted per story scope *(Pending Q4)* | Medium | Q4 |

## E2E automation candidates

| ID | Title | Why automate | Suggested level | Risk if skipped | Linked Q |
|----|-------|--------------|-----------------|-----------------|----------|
| E2E-01 | Overview natural sort regression | Repeatable UI order check once Q1–Q3 resolved | Playwright UI | Sort regression on Overview | Q1, Q2, Q3 |

## Open assumptions
- Sort uses task **title/summary** column *(depends on Q1 / F2)*
- Natural order = numeric-aware on embedded numbers *(depends on Q3 / F1)*
- Sort applies on Overview **load** by default *(depends on Q2 / F3)*
- Scope limited to **Task** issue type *(depends on Q4 / F4)*

## Out of scope for this draft
- API tests, permalink behavior (ONE-309217 — pending Q5)

## XRay import note
Preliminary — confirm Q1–Q4 before execution sign-off. Copy CSV below manually.
```

**Report rule:** assumptions live here only — not in scan report body.

---

## Quick invoke

| User says | Action |
|-----------|--------|
| `@story-ui-test-cases ONE-323108` | Generate TCs for KEY using scan in chat |
| `generate test cases for PROJ-123` | Same — confirm scan context or ask for scan |
| After initial scan with open High Q# or High F# | Label **Preliminary draft**; list assumptions |
| After rescan with no open High Q# / High F# | Label **Final draft** (per **TC status label** table) |
| User asks for copy-friendly report | Offer markdown tables + optional HTML file in workspace `reports/{KEY}-ui-test-cases-report.html` |
