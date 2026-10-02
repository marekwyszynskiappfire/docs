---
name: story-testability
description: >-
  Jira story and epic testability analysis: deterministic gather, gap heuristics,
  epic scan mode for child inventory and release planning,
  findings table, readiness classification, rescan, clarification questions,
  epic context, optional Figma design ingest, QA checklist, optional HTML report,
  Jira comment formatting. Read-only on Jira. Use for shift-left QA review.
  Self-contained single-file
  skill for platform agents. Use when user runs hive-mcp__run_skill,
  hive-mcp__load_skill, or says scan/rescan {ISSUE_KEY}. After load, execute
  full Jira gather + gap scan + report in the same turn.
disable-model-invocation: true
---

# Story Testability

Single skill for **analysis**, **rescan**, and **Jira comment formatting**. Read-only on Jira — nothing is published automatically.

**Highlights:** deterministic gather, testability gap heuristics, findings table (F#), readiness for test planning, qualitative scoring only, optional HTML with TC handoff.

**Scope:** primary mode is issue type **Story**. For **Epic**, use **Epic scan mode** (dedicated gather, report sections, and gap interpretation — do not run the Story template unchanged). For **Bug** or **Task**, run the Story workflow but replace "story" with the actual issue type in all output text and skip **Acceptance criteria gaps** unless an AC-equivalent field exists. Do not silently treat non-Story types as Stories.

---

## Quick start — what to type (QA cheat sheet)

Copy-paste commands in chat (Cursor + Atlassian MCP, or Hive **Scan Story** + issue key). English reports; Polish triggers like `przeskanuj ONE-123` also work.

### A. Single User Story (or Bug/Task)

| Step | You type | You get |
|------|----------|---------|
| 1 | `scan ONE-338330` or `/scan-story ONE-338330` | Full **story** scan: F#, Q#, readiness |
| 2 | (optional) `export html ONE-338330` | HTML report file |
| 3 | After Jira updates | `rescan ONE-338330` |
| 4 | Test cases (separate skill) | `@story-ui-test-cases ONE-338330` — run **after** scan in same chat |
| 5 | (optional) | `format for Jira short` or `format for Jira full` — comment text to paste |

**Do not expect UI test case tables from this skill alone** — use step 4.

### B. Epic (plan release + batch children)

| Step | You type | You get |
|------|----------|---------|
| 1 | `scan ONE-324502` | **Epic** scan + children summary (Done / WfR / Open…) + **Epic batch handoff** with **recommended** story keys (≤ 8) |
| 2a | `confirm batch` or `yes` or `run batch` or `tak` | For each **recommended** child: story `scan` + **Preliminary** UI TC → **Batch** tab in one HTML |
| 2b | *or* one shot | `scan ONE-324502 --batch` (= step 1 + 2a in one turn) |
| 3 | Only if you explicitly want every WfR child | `scan ONE-324502 --batch all-wfr` (not default) |
| 4 | Custom child list (max 8) | `scan ONE-324502 --batch keys ONE-341257,ONE-338330` |

**HTML (epic):** `{EPIC_KEY}-epic-and-batch-report.html` — **Tab Epic** (children first) | **Tab Batch** (fills after step 2).

**After batch:** refine individual stories with `rescan {KEY}` then `@story-ui-test-cases {KEY}` for **Final** TC when High F#/Q# are closed.

### C. What this skill does **not** do

- Does not publish to Jira or XRay  
- Does not run batch automatically after epic scan **unless** you confirm (step 2a) or use `--batch`  
- Does not replace **Story UI Test Cases** skill for TC tables  

### D. Agent rule (when this file is loaded)

Follow **Execution contract** below: never stop at "skill loaded"; always deliver the full scan report (and run batch when user confirmed or `--batch` flags present). End every **Epic** scan with the **Epic batch handoff** block from **Epic unified workflow**.

---

## Table of contents

0. Quick start — what to type (QA cheat sheet)
1. Execution contract — resolve input, default mode, mandatory steps
2. Hive `arguments` shape · Modes
3. Recommended QA process · Blocked phrases
4. Report integrity — no assumptions
5. Classifications (canonical definitions — see **Scoring** for decision trees)
6. Initial scan workflow · Scan output template
7. Rescan mode · Jira comment mode · Checklist export
8. Validation (before output)
9. Platform note (Hive/Cursor execution behavior, MCP fallback)
10. Gather (read-only) — steps 1–10, unavailable-source handling
11. Testability gap scan heuristics (12 dimensions)
12. Severity model (F# / Q# definitions — canonical)
13. Scoring (qualitative) — decision trees only, refers back to §12
14. Epic unified workflow · Epic scan mode · Epic context (story scans) · Screenshot · Figma · Spreadsheet ingest
15. QA readiness checklist export
16. Jira comment templates (full / short) · Wiki markup rules · Labels
17. HTML export
18. Examples (tone calibration)

## Limits reference (canonical — all other sections refer here, do not restate numbers)

| Limit | Value |
|-------|-------|
| Clarification questions (default) | ≤ 8 total, ≤ 5 High |
| Clarification questions (complex story, justified) | ≤ 15 (state why) |
| New questions per rescan | ≤ 5 |
| Sibling stories fetched (JQL, story scan) | ≤ 25 |
| Epic children sampled (JQL, epic scan) | Paginate until `isLast`; full inventory required for status mix + recommended batch |
| Recommended batch size (default) | ≤ 8 keys |
| Batch all Waiting for Release | Only when user passes `--batch all-wfr` |
| Figma frames analyzed per scan (`get_design_context` / targeted nodes) | ≤ 3 |
| Readiness checklist CSV rows | ≤ 50 |
| QA readiness checklist auto-include threshold | ≥ 3 Suggested testing focus items |
| Numeric scores / percentages / weighted totals in any output | **0 — never** |

## Execution contract (Hive MCP + Cursor) — mandatory

When this skill is loaded via `hive-mcp__load_skill` or `hive-mcp__run_skill`, **do not stop** after metadata or `result: "noop"`. In the **same turn**, run the full workflow and return the full markdown scan report as the primary deliverable.

### Resolve input (first match wins)

1. `arguments.issueKey` — e.g. `"ONE-372713"`
2. Parse `arguments.prompt` — regex: `(?i)(scan|rescan|format for jira short|format for jira full|export html(?: report)?|export readiness checklist)\s+([A-Z][A-Z0-9]+-\d+)`; bare issue key in prompt also accepted
3. User chat text — e.g. `scan ONE-372713`
4. **Trigger word not recognized, but a bare issue key is present** (e.g. `"check ONE-372713"`, `"przeskanuj ONE-372713"`) → treat as **initial scan** of that key; do not require an exact keyword match
5. If no issue key found anywhere → ask once; do not run gather

**Issue key normalization:** compare keys case-insensitively and trimmed of whitespace when matching against a prior scan in this chat (e.g. `one-372713` = `ONE-372713`). Always render the key in output using the casing returned by Jira.

### Default mode

- Only `issueKey` or bare key in prompt → **initial scan**
- `rescan` in prompt → **rescan delta**
- `format` / `export` without prior scan in chat → run initial scan first (unless user pasted prior scan output)

### Mandatory steps (same turn)

1. Resolve issue key + mode
2. **Jira gather (read-only)** — Atlassian MCP; if issue type is **Epic**, follow **Epic scan mode** gather (not story parent/sibling steps)
3. **Testability gap scan** — heuristics + **Epic scan mode** gap rules when target is Epic
4. **Output** — Story scan template or **Epic scan template** + clarification questions

### Forbidden end states

- Returning only `noop`, skill metadata, or "skill loaded"
- Stopping before the markdown report
- Auto-publishing to Jira/XRay

## Hive `arguments` shape

```json
{
  "prompt": "scan ONE-372713",
  "issueKey": "ONE-372713",
  "mode": "scan"
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `prompt` | recommended | Natural-language trigger, e.g. `"scan ONE-372713"` |
| `issueKey` | optional | Shortcut; default mode = initial scan |
| `mode` | optional | `scan` · `rescan` · `jira-comment-short` · `jira-comment-full` · `html` · `readiness-checklist` |

All fields are optional at MCP level; the agent must resolve issue key before gather.

## Modes

| Trigger | Mode |
|---------|------|
| `scan PROJ-123`, `@story-testability` on new story | **Initial scan** |
| `scan EPIC-KEY` (issue type Epic) | **Epic initial scan** + batch handoff (see **Epic unified workflow**) |
| `scan EPIC-KEY --batch` / `--batch recommended` | **Epic scan + recommended batch** (same turn) |
| `scan EPIC-KEY --batch all-wfr` | **Epic scan + all Waiting for Release children** (explicit; warn if > 8) |
| `confirm batch` / `yes` / `run batch` after epic scan in chat | **Recommended batch only** (orchestrator skill) |
| `rescan PROJ-123`, story updated in same chat | **Rescan delta** |
| `format for Jira short` / `full` | **Jira comment** (from approved scan in chat) |
| `export HTML report` / `export html` | **HTML report** (see **HTML export** section below) |
| `hive-mcp__run_skill` + `arguments: { "prompt": "scan ONE-372713" }` | **Initial scan** |
| `hive-mcp__run_skill` + `arguments: { "issueKey": "ONE-372713" }` | **Initial scan** (default mode) |
| `hive-mcp__run_skill` + `arguments: { "prompt": "rescan ONE-372713" }` | **Rescan delta** |

If rescan requested but **no prior scan in this chat** → ask for previous output or run initial scan. Do not pretend to know prior state.

## Recommended QA process

```
1. Initial scan → 2. QA review → 3. format for Jira → 4. story updated
→ 5. rescan → 6. @story-ui-test-cases → 7. export readiness checklist
```

Default handoff after scan: Jira comment → rescan → UI TCs (not TCs immediately after scan).

## Blocked phrases

Story failed · Not ready · Blocked by QA · PM did not provide AC · gate · bloker/blocker (as judgment) · story is invalid

**Output language rule:** all output — markdown scan report, HTML export (including the TC handoff block), Jira comment templates, and clarification questions — is **English by default, with no exceptions**. If a user explicitly requests a translated report, apply the same "no assumption / no blocked phrase" rules to the translated text, and block the equivalent phrases in that language too.

## Report integrity — no assumptions

**In the scan report, do not assume, infer, or fill gaps with defaults.**

| Rule | Apply to |
|------|----------|
| Only **facts** from analyzed sources | Information identified, Impacted areas, Flows |
| Every fact bullet → `*(Source: …)*` | Information identified |
| If not in story → **Not stated in story** (not an assumption bullet) | Flows, scope, behavior |
| No `*(Assumption)*`, `*(inferred)*`, `*(typical behavior)*` in report body | All sections |
| Gaps → **Testability findings**, **Missing or unclear information**, or **Clarification questions** | — |
| Epic/sibling context → titles and keys only; no invented epic intent | Epic context |
| Testing focus → **what to verify after clarification**, not presumed behavior | Suggested testing focus |
| Automation → assess only from **stated** observable outcomes; else **TBD** | Automation assessment |

Questions carry hypotheses; the **report** stays factual.

## Classifications

| Field | Values |
|-------|--------|
| **Testability** | High / Medium / Low |
| **Test scope confidence** | High / Medium / Low |
| **Risk level** | High / Medium / Low + rationale tags |
| **Automation candidate** | Yes / No / TBD |
| **Readiness for test planning** | Ready with clarifications · Needs clarification before scope lock · Cannot plan scope yet |

This table lists the possible **values** only. Decision trees for how to pick a value live in **Scoring** (qualitative); severity/priority definitions for F#/Q# live in **Severity model**. Do not duplicate the trees here. See **Limits reference** above for the numeric-scores rule.

## Story type (handoff only — classify from stated user-facing vs not)

User-facing UI · API/backend · Mixed · Config · Discovery — do not infer from stack (e.g. Forge).

## Initial scan workflow

```
Gather (read-only) → Facts-only extraction → Testability gap scan → Score
→ Full markdown scan report + findings (F#) + questions (≤8 default)
→ QA readiness checklist (if ≥3 focus items)
→ HTML report (optional — see below)
→ Stop for review — no Jira comment unless asked
```

Follow inline sections below: **Gather**, **Epic scan mode** (when target is Epic), **Gap scan heuristics**, **Spreadsheet ingest**, **Screenshot rules**, **Figma design ingest**, **Epic context** (when target is Story), **HTML export**.

### Gather (read-only) — required

Follow **Gather (read-only)** section below in order. Record **Data sources analyzed** vs **unavailable** in the report header. Never invent missing fields.

### Testability gap scan

After facts extraction, run **Testability gap scan heuristics** below. For each dimension: **COVERED** (with Source) or **GAP** (bullet in *Not stated in story* / finding). Do not invent answers. High-impact GAPs → findings F# and/or clarification questions.

### Clarification questions

Default **max 8**; **max 5 High**; up to **15** only if genuinely complex (state why).

Each question: **Context · Source · Priority · Unblocks**. Link to finding ID when applicable (`Unblocks: F2`). Group by topic (Behavior, Scope, Edge cases, Integrations, Permissions, Data).

Focus bullets may use `*(blocks: Q#)*` or `*(blocks: F#)*` — report facts sections must not.

### Scan output template (mandatory sections)

Use this structure every time. Calibrate tone via **Examples** section below.

```markdown
# Story Testability Scan — {KEY}

| | |
|---|---|
| **Testability** | High / Medium / Low |
| **Test scope confidence** | High / Medium / Low |
| **Risk level** | {level} |
| **Automation candidate** | Yes / No / TBD |

**Readiness for test planning:** Ready with clarifications | Needs clarification before scope lock | Cannot plan scope yet
_{one line citing top blocking F# or Q# — not a gate judgment}_

**Story type:** {from stated content only}
**Scanned:** {date}
**Data sources analyzed:** {list}
**Data sources unavailable:** {list}

**Parent context:** {key — summary — status} or *No parent epic*

## Epic context
{Per Epic context rules below — facts only; or: Epic context not available — not guessed}

## Information identified
- {fact only} *(Source: Description § / Comment @user / Attachment / Field name)*

## Design observations (Figma)
_Include this section only when at least one Figma URL was fetched successfully (see **Figma design ingest**). Omit the section entirely if no link was found or fetch failed — do not leave an empty heading._

- {visible UI string, control label, frame name, or sticky note text — exact quote} *(Source: Figma — {canonical URL}, node `{nodeId}`)*

## Testability findings
| ID | Severity | Finding | Testing impact | Source / Gap |
|----|----------|---------|----------------|--------------|
| F1 | High / Medium / Low | {what is missing or ambiguous} | {why QA cannot plan/assert yet} | {Source or Gap analysis} |

## Identified flows
### User flows
- {flow only if described in story — quote steps, no arrow chains from inference} *(Source: …)*
- *Not described in story* — if no user steps in analyzed content

### System flows
- {flow only if described in story} *(Source: …)*
- *Not described in story* — if no system behavior in analyzed content

## Impacted areas
- **Modules / components:** {only if named in story}
- **Integrations:** {only if named in story}
- **UI areas:** {named in story and/or Figma frame/component names from **Design observations (Figma)** — cite Figma source on each bullet}
- *Not stated in story:* {list fields not provided — not guessed values}

## Not stated in story
- {bullet per missing scope/behavior/trigger/rule — no invented answers}

## Known or suspected risks
- {risk tied to stated fact or documented gap} — *{level}* *(Source: …)*

## Missing or unclear information
- **{topic}:** {what is missing — no suggested answer}

## Acceptance criteria gaps
- {only if AC field or AC in description exists but is incomplete/vague — suggest what AC should clarify; label as gap, not as new requirement}

## Suggested testing focus
- Verify {area} once {Q# or F# or story update clarifies …} *(blocks: Q#)* — not presumed pass criteria

## Automation assessment
**Candidate:** Yes / No / TBD
**Rationale:** {from stated observable outcomes only; TBD if behavior undefined}
**Suggested approach:** {only if candidate ≠ TBD; else "Pending clarification on Q#"}

## Recommended next action
{Collaborative suggestion — suggested owners only}

## Scoring rationale
{Why classifications using qualitative rules from scoring-reference.md; cite findings F#; no invented detail}

## QA readiness checklist (preliminary)
| # | Check | Source | Owner | Done |
|---|-------|--------|-------|------|
| 1 | {observable or Pending Q# / F#} | {ref} | QA | ☐ |

_Optional CSV block for Excel — on `export readiness checklist`_

---

# Clarification Questions — {KEY}

## {Topic}
### Q{n}. {question}
- **Context:** …
- **Source:** … / Gap analysis / F#
- **Priority:** High / Medium / Optional
- **Unblocks:** …
```

**Do not** include UI test case drafts — use `@story-ui-test-cases` after clarification.

### QA readiness checklist (in scan output)

Include section **## QA readiness checklist (preliminary)** when:
- ≥3 **Suggested testing focus** items, OR
- spreadsheet ingested, OR
- user requests full scan / checklist

Label **preliminary** until after rescan. Checks must be **observable** or explicitly **Pending Q# / F#** — no assumed pass criteria. See **QA readiness checklist export** section below.

### HTML report (optional by default)

Generate HTML when user requests `export HTML report` / `export html` or explicitly asks during scan.

Otherwise: complete markdown scan only; offer HTML on request.

**Platform note:** paste HTML in chat unless file write is available.

When generating:
Follow **HTML export** section below. Output full HTML in chat (or write file if workspace allows). Same facts as markdown — no extra assumptions. Include TC handoff block. Do not auto-publish.

On platforms without file write: **always paste HTML in chat** when user requests export.

## Rescan mode

Prior scan for **same issue key in this chat** (matched per the normalization rule in **Resolve input**). Output **Rescan Delta**: content changes, finding status (F# resolved/open), question status, classification changes, readiness line, focus changes, TC update hints. Max **5 new** questions (see **Limits reference**). Major changes → offer full scan refresh. After rescan, offer to **regenerate HTML report**.

**Scan labels:** label each scan/rescan output with type and date, e.g. `Initial scan — {date}` / `Rescan — {date}`, so later references in chat (comment formatting, HTML export, TC handoff) can point to "the latest scan" unambiguously.

**Duplicate request:** if the user repeats the exact same `scan {KEY}` or `rescan {KEY}` request with no story change since the last identical request in this chat, do not silently re-run the full gather — note that the story is unchanged since the last scan/rescan and ask whether they want a fresh gather anyway (Jira content may have changed even if nothing new was said in chat).

## Jira comment mode

From approved scan — do not re-analyze. `format for Jira short` | `full` — see **Jira comment templates** section below. Copy-paste only.

## Checklist export

`export readiness checklist` / `readiness CSV` — prefer after rescan. **QA readiness checklist export** section below

## Integrations

Jira read-only · comment ≠ publish · XRay format via `@story-ui-test-cases` only · Sheets paste only

## Validation (before output)

- [ ] Gather steps completed or marked unavailable
- [ ] Testability gap scan run per heuristics section
- [ ] No assumption/inference language in factual sections
- [ ] Every Information identified bullet has Source
- [ ] Testability findings table present with F# IDs and testing impact
- [ ] Readiness for test planning line present with blocking F#/Q# cite
- [ ] Flows say "Not described" when absent
- [ ] Not stated in story lists gaps, not guesses
- [ ] ≤8 questions default, ≤5 High
- [ ] Epic not guessed; sibling rules from Epic context section
- [ ] Screenshot rules followed (text only)
- [ ] If a Figma URL was present: fetch attempted or failure recorded; **Design observations (Figma)** only contains quoted Figma facts with `Source: Figma` on every bullet; no Figma-based behavior invented
- [ ] Blocked phrases absent
- [ ] No unit/API TC design for QA
- [ ] No numeric scores or percentages in output
- [ ] HTML only when criteria met; content matches markdown if generated
- [ ] Issue type reflected correctly in output text (Story vs Bug/Task/Epic)
- [ ] **Epic target:** Epic scan template used; **full** child inventory + status mix; **Epic batch handoff** block; `recommendedBatchKeys` ≤ 8; no faux "parent epic" block; two-tab HTML when exported; batch only after confirm or `--batch`
- [ ] Any failed gather step (not just missing data) recorded in Data sources unavailable with reason
- [ ] Scan/rescan output carries a scan label (Initial scan / Rescan + date)

## Inline reference sections

All rules are in this file — no external skill files required.

---

## Platform note (single-file skill)

This file is **self-contained**. Do not expect companion `.md` or `.html` files.

| Capability | Behavior on platform |
|------------|---------------------|
| Hive `run_skill` / `load_skill` | Execute steps 1–4 from **Execution contract** in the same turn; report is required output |
| `result: "noop"` from Hive | **Not** the final response — trigger to execute this skill |
| Scan / rescan | Full markdown scan output |
| Jira gather | **Required** when issue key is known — Atlassian MCP (read-only); record unavailable sources |
| Atlassian MCP tools | `getAccessibleAtlassianResources` → `getJiraIssue` (issue, comments, parent) → `searchJiraIssuesUsingJql` → optional links/subtasks. **Story scan children of epic:** `"Epic Link" = {EPIC_KEY}` first; if 0 results, retry `parent = {EPIC_KEY}`. **Epic scan:** `"Epic Link" = {EPIC_KEY}` (same key as target). If these exact tool names are unavailable, look for a semantically equivalent connected MCP tool (issue get / JQL search) before falling back to unavailable |
| Figma MCP (optional) | When a Figma URL is discovered during gather, use connected Figma MCP (`get_design_context` on parsed `fileKey` + `nodeId`; `get_metadata` only to pick ≤3 relevant child frames). Load project **figma-design-to-code** skill before `get_design_context` when the host requires it. If Figma MCP is missing or fetch fails, record in **Data sources unavailable** — continue the scan |
| Missing Jira MCP (tool not connected) | Record in **Data sources unavailable**; continue with user-pasted content if provided |
| Jira MCP call fails mid-gather (timeout, rate limit, permission denied) | Do **not** abort the whole scan. Record the specific failed step in **Data sources unavailable** with the reason (e.g. `Comments (403 permission denied)`), continue gather for remaining steps, and proceed to report |
| HTML export | Paste in chat unless file write works |
| TC generation | **Not in this skill** — use separate TC agent if available |
| Publish to Jira/XRay | Never automatic — copy-paste only |

---

## Gather (read-only)

Execute in order during **Initial scan**. Record results in report header: **Data sources analyzed** vs **Data sources unavailable**.

Do **not** invent content for unavailable sources.

## 1. Target issue (required)

Fetch and read:

| Field | Record as |
|-------|-----------|
| Key, summary | Header |
| Description (full, ADF/plain) | Primary source |
| Issue type, status, priority | Overview / badges |
| Reporter, assignee | Overview |
| Labels, components | Impacted areas (if named) |
| Created / updated | Optional metadata |
| Attachments | Metadata + screenshot pass if readable |

## 2. Acceptance criteria (required attempt)

| Step | Action |
|------|--------|
| 1 | Request project AC field(s) via MCP (custom field names vary) |
| 2 | If AC field empty but AC bullets exist **in description** → analyze description AC as source |
| 3 | If AC field contains only template/boilerplate → record `AC template empty — no story-specific criteria` |
| 4 | If AC unavailable via MCP → record in **Data sources unavailable** |

Do not treat empty template as "story has no requirements" if description/comments contain criteria.

## 3. Comments (required)

- Fetch **all** comments (expand threads if MCP supports)
- Cite as `Comment @author, YYYY-MM-DD`

## 4. Parent epic (story / bug / task target only)

- **Skip as "parent epic" when target issue type is Epic** — use **Epic scan mode** instead
- Parent key, summary, status, description excerpt (facts only)
- On epic (and story if returned), read Jira custom fields that commonly hold design links (e.g. **Figma (URL)**, **Acceptance Criteria** when value is a `figma.com` URL) — pass URLs to **Figma design ingest** (step 10); record field name in **Data sources analyzed**
- If no parent → `No parent epic`

## 5. Sibling stories (story target — parent epic known)

- JQL: `"Epic Link" = {EPIC_KEY}` — max **25** results; if empty, `parent = {EPIC_KEY}`
- Store: key, summary, status only (read-only)
- Per **Epic context (story scans)** section below

## 5b. Epic children (epic target only)

- Per **Epic scan mode → Gather** — required when issue type is Epic

## 6. Issue links (if MCP supports)

- Inward/outward linked issues: **key + summary + link type** only
- Do not infer dependency behavior from link type alone — record as fact; gap if behavior unstated

## 7. Subtasks / child issues (optional)

- List key + summary if returned by MCP
- Do not merge subtask scope into story without explicit reference in story text

## 8. Spreadsheet / external links

- Detect per Spreadsheet ingest section above
- Do not auto-fetch Google Sheets
- Collect `figma.com` URLs from description, comments (if readable), and design-related custom fields — dedupe; see step 10

## 9. Screenshots

- Per Screenshot section above
- If unreadable (403, auth) → **Data sources unavailable: Attachment {name}**

## 10. Figma design links

- Run **Figma design ingest** below when any URL matches detection rules
- If no URL → skip step (no **Design observations (Figma)** section)

## Unavailable sources — report honestly

```markdown
**Data sources unavailable:** Acceptance Criteria field (MCP), Attachment screenshot.png (403), Figma `https://…` (MCP not connected / auth / timeout)
```

Never substitute guessed content for unavailable sources.

---

## Testability gap scan heuristics

Run **after** facts extraction and **before** scoring. This is a **gap checklist**, not test case generation.

**Rule:** For each dimension, output either **COVERED** (with `*(Source: …)*`) or **GAP** (bullet in *Not stated in story* and/or finding F#). **Never invent answers.**

## Dimensions

| # | Dimension | COVERED when | GAP examples (list only, do not answer) |
|---|-----------|--------------|----------------------------------------|
| 1 | Happy path | Expected success behavior stated | Main outcome undefined |
| 2 | Negative paths | Failure/rejection cases mentioned | Invalid input, denied access not described |
| 3 | Boundaries | Limits, min/max, empty, max items stated | Sort order, pagination, empty state absent |
| 4 | Error / failure | Error messages, fallback, timeout mentioned | Service down, validation errors absent |
| 5 | Roles / permissions | Who can/cannot use feature stated | Role matrix, guest vs admin absent |
| 6 | Data | Inputs, outputs, persistence, formats stated | Field mapping, ID format, audit absent |
| 7 | Integrations | External systems/APIs named with expected interaction | Contract, sync direction absent |
| 8 | States / transitions | Lifecycle (draft→published) described | Toggle persistence, undo absent |
| 9 | NFR | Perf, a11y, i18n, security requirements stated | Load time, locale, WCAG absent |
| 10 | Test data / environment | Env, fixtures, seed data mentioned | Staging flag, test account absent |
| 11 | Observability | Logging, metrics, audit mentioned | Support/debug signals absent |
| 12 | Epic consistency | Epic facts align with story facts (factual diff only) | Same term used differently — cite both sources; story term vs **Design observations (Figma)** on epic-linked file |

## Severity for GAPs → findings F#

Use Severity model section above:

- **High** — blocks defining pass criteria or primary test scope
- **Medium** — affects edge/regression scope but core path testable
- **Low** — nice-to-have clarity; low impact on initial scope

## Ambiguity detection

Flag vague terms in story text as findings (not rewrites):

- "natural order", "appropriate", "fast", "soon", "etc.", "as usual", "similar to before"

**Finding text:** `Term "{term}" is ambiguous — pass criteria cannot be defined without clarification.`

## Question linkage

- High-severity GAP → finding F# + clarification question Q# (if PM/dev can answer)
- Medium GAP → finding F#; question optional if scope still outlineable
- Low GAP → *Not stated in story* only; question only if user-facing impact

## Do not

- Generate test steps or expected results in the scan
- Fill GAPs with "typical" or industry-default behavior
- Use sibling epic titles to mark dimensions COVERED
- Count dimensions as percentages or scores

---

## Severity model

Three severity levels — **no numeric scores**.

## Finding severity (F#)

Used in **Testability findings** table.

| Severity | Meaning | Typical testing impact |
|----------|---------|------------------------|
| **High** | Cannot define pass criteria or primary scope for this topic | Blocks checklist items; needs Q# before scope lock |
| **Medium** | Affects edge, regression, or integration scope | Outline testable; detailed cases need clarification |
| **Low** | Clarification improves confidence; core path still outlineable | Optional question; note in Not stated |

## Question priority (Q#)

| Priority | When |
|----------|------|
| **High** | Unblocks High finding or core behavior definition |
| **Medium** | Unblocks Medium finding or significant edge scope |
| **Optional** | Low finding; polish or readiness nuance |

Max **5 High** questions default (see workflow above).

## Story risk level

Separate from finding severity — see Scoring section above. A story can have **Medium risk** with several **High findings**.

## Readiness mapping

| Readiness for test planning | Typical finding/question profile |
|-----------------------------|----------------------------------|
| Ready with clarifications | No High findings on dimensions 1–6; Optional questions only |
| Needs clarification before scope lock | ≥1 High finding on behavior, boundaries, errors, or roles |
| Cannot plan scope yet | Low testability; core happy path GAP; multiple High findings on scope |

## Traceability

- Checklist row → cite Source, F#, or `Pending Q#`
- Question → **Unblocks:** F# and/or testing focus area
- Rescan → mark F# **Resolved** / **Open** when story updates

---

## Scoring (qualitative)

**No numeric scores, percentages, or weighted totals in scan output.**

Use gap analysis from Gap scan heuristics section above and findings (F#) to apply these rules consistently.

## Classification definitions

### Testability (High / Medium / Low)

> Can tests be planned and executed clearly from current story content?

| Level | Meaning |
|-------|---------|
| **High** | Expected behavior and scope are clear; remaining gaps are Low-severity findings or Optional questions only |
| **Medium** | Core intent clear; one or more Medium/High findings may change test scope or pass criteria |
| **Low** | Core expected behavior OR scope boundary cannot be stated from sources; or multiple High findings block scope |

**Decision tree (no percentages):**

- **Low** if: no observable expected behavior can be cited with Source, OR scope boundary undefined for the main change
- **Medium** if: core intent is clear but ≥1 **High** finding affects scope, pass criteria, or primary flow definition
- **High** if: observable behavior and scope are clear; blocking gaps are none or Low/Optional only

Empty AC field alone does **not** lower testability if description/comments provide equivalent detail.

### Test scope confidence (High / Medium / Low)

> Confidence that QA can define a **complete intended test scope** from current content — not assessment of existing automated test coverage.

| Level | Meaning |
|-------|---------|
| **High** | Checklist can be drafted now; remaining gaps are low-impact |
| **Medium** | Outline scope possible; several gaps may change coverage |
| **Low** | Scope cannot be estimated reliably |

**Decision tree:**

- **Low** if: ≥2 High findings on scope-defining dimensions (happy path, boundaries, errors, roles)
- **Medium** if: outline possible but ≥1 High finding remains on behavior or edge cases
- **High** if: scope dimensions mostly COVERED per heuristics; remaining gaps are Optional

### Risk (High / Medium / Low + rationale)

Story-level risk — not the same as finding severity. Always add 1–2 rationale tags where relevant:

`customer impact` · `regression surface` · `permissions/security` · `data integrity` · `integration dependency` · `reversibility`

**Decision tree:**

- **High** if: stated or gap-affected area touches security, payments, data loss, or broad regression with undefined behavior
- **Medium** if: meaningful regression or integration dependency with partial definition
- **Low** if: narrow, well-bounded change with clear stated outcomes

### Automation candidate (Yes / No / TBD)

| Value | When |
|-------|------|
| **Yes** | Repeatable observable UI outcomes stated; stable selectors/flows implied by story; no blocking High findings on behavior |
| **No** | Discovery-only, no user-observable outcome, or manual-only verification explicitly required |
| **TBD** | Behavior or assertions undefined; pending clarification on High findings |

**Suggested approach** must match evidence: UI verbs → Playwright UI E2E only; do not recommend API/unit test design for QA testers in this skill.

### Readiness for test planning

| Value | When |
|-------|------|
| **Ready with clarifications** | Testability High or Medium; no High findings on core behavior; Optional/Medium questions only |
| **Needs clarification before scope lock** | Medium testability; ≥1 High finding or question on scope/pass criteria |
| **Cannot plan scope yet** | Low testability or Low scope confidence; core behavior or scope undefined |

Cite top blocking F# or Q# in one line — collaborative, not a gate.

## Spreadsheet ingest adjustment

| Situation | Test scope confidence adjustment |
|-----------|----------------------------------|
| Full NEW VERSION column ingested | May raise Low → Medium or Medium → High if story depended on sheet |
| Partial paste | Keep current; note "partial checklist" |
| Link only, no paste | Keep Low if story depends on sheet |

## Report rule

Classifications use qualitative gap analysis only. **Scan report body** must not state assumptions — use *Not stated in story* (or *Not stated in epic* for Epic scans), findings F#, and questions instead.

---

## Epic unified workflow (SCAN + optional batch)

Single entry: **`scan {EPIC_KEY}`** (or `SCAN {EPIC_KEY}`). Detect Epic via Jira issue type after gather step 1.

### Phase 1 — Epic scan (always)

1. Run **Epic scan mode** (full child inventory, status mix on **all** children, Figma/PRD as available).
2. Compute **`recommendedBatchKeys`** (≤ 8) per **`story-epic-batch-orchestrator`** skill — includes **Done** stories when they score into top 8 (regression); default batch is **recommended only**, not all WfR.
3. Output epic markdown + **Epic batch handoff** block (mandatory at end of epic scan):

```markdown
## Epic batch handoff

**Recommended for batch scan + Preliminary TC ({n}):** ONE-…, ONE-…
**Excluded from recommended (examples):** ONE-381100 — unit tests · …

**Status mix (all children):** Done {n} · Waiting for Release {n} · Open {n} · …

### Continue workflow
| You say / run | What happens |
|---------------|----------------|
| `confirm batch` / `yes` / `run batch` / `tak` | Recommended batch: child `scan` + **Preliminary** `@story-ui-test-cases` per key → **Batch** tab |
| `scan {EPIC_KEY} --batch` | Same as confirm, in one turn (epic + batch) |
| `scan {EPIC_KEY} --batch all-wfr` | All **Waiting for Release** children only (explicit; not default) |
| `scan {EPIC_KEY} --batch keys ONE-a,ONE-b` | Custom list (max 8) |

**HTML:** one file `{EPIC_KEY}-epic-and-batch-report.html` — **Tab Epic** | **Tab Batch** (Batch empty until batch runs).
```

4. **Do not** run batch in phase 1 unless `--batch` flag is on the same command.

### Phase 2 — Batch (after confirmation or `--batch`)

Load and execute **`story-epic-batch-orchestrator`** with the batch set from the table above. Merge results into the **Batch** tab of the same HTML file.

**TC status:** always **Preliminary draft** for batch runs.

### Epic HTML — children first (Tab Epic)

Before standard Tier 1 KPI cards on Epic exports:

1. **Children summary bar:** `{total} children · Done {n} · Waiting for Release {n} · Open {n} · Canceled {n} · …` (+ optional type breakdown).
2. **`<details open>` — All epic children ({total})** — group by status; each row: linked key, type, summary, **Batch?** column: `✓ recommended` | `—` + reason.
3. **Recommended batch** — copyable comma-separated keys.

### Epic HTML — two tabs (single file)

```html
<!-- Tab controls: Epic | Batch (n) -->
<div id="panel-epic">{epic scan body}</div>
<div id="panel-batch" hidden>{batch sections or placeholder}</div>
```

Filename: `{EPIC_KEY}-epic-and-batch-report.html`. Updating Batch tab after phase 2 replaces placeholder; Epic tab unchanged.

### Parse `scan` prompt

Regex examples: `scan ONE-324502`, `SCAN ONE-324502 --batch`, `--batch recommended`, `--batch all-wfr`, `--batch keys A,B,C`.

---

## Epic scan mode

Use when the **target issue** from Jira is issue type **Epic**. Goal: support **release / initiative test planning** and **child-story triage** — not story-level pass criteria for a single flow.

## What an epic scan is (and is not)

| In scope | Out of scope |
|----------|----------------|
| Epic goal, constraints, PRD/design links as **facts** | Inventing acceptance criteria for the whole epic |
| Inventory of child issues (sampled) + status mix | Full test case tables (use `@story-ui-test-cases` per Story after child scans) |
| Gaps: untestable epic wording, missing completion signals, child hygiene | Asserting which child "owns" a behavior without epic or child text |
| Epic-level E2E **themes** and **suggested testing focus** | API/unit test design |
| Figma/PRD ingest at **epic** fields | Reading every child description (unless user lists keys) |

## Gather (epic target)

Run standard gather steps **1–3, 6–10** on the epic itself. **Replace** steps 4–5 with:

1. **Child work inventory (required)** — JQL `"Epic Link" = {EPIC_KEY}` ORDER BY status, key; **paginate until `isLast`**. Fields: key, summary, status, issuetype. Compute **status mix on full set**. If pagination fails mid-way, record partial sample in **Data sources unavailable** and note mix is incomplete.
2. **Optional depth (only if ≤ 5 children or user names keys):** `getJiraIssue` evidence view on individual children to flag empty description / missing AC — cite counts as facts, not full child analysis
3. **Initiative parent (optional):** if epic has `parent` (e.g. Initiative), one-line summary only — not expanded scope
4. **Epic custom fields:** Figma URL, UX status, counts (e.g. children done/open) when returned by MCP — facts only
5. **Figma design ingest** on epic URLs (step 10) — often high value for epics whose AC is a Figma link

## Gap scan (epic target)

Apply the **12 dimensions** to **epic description, epic comments, epic AC/design links, and child inventory metadata** — not as if the epic were a single UI story.

| Dimension | Epic interpretation |
|-----------|---------------------|
| Happy path | Epic states user outcome or journey end state — **GAP** if only vision language ("instantly understand value") with no observable completion signal |
| States / transitions | Release phases, feature flags, or rollout stated at epic level — else **GAP** for epic E2E timing |
| Epic consistency (12) | Rename to **Child ↔ epic alignment (facts):** terms in epic goal vs child summaries (keyword overlap table); empty-description children vs epic In Progress |
| Roles / permissions | Only if epic or ≥2 child summaries name roles |

**Epic-specific findings (still use F# IDs):**

- **High:** Epic has no testable completion criterion in analyzed sources (only PRD/Figma link with body not fetched); OR majority of sampled children have **empty description** while epic is active; OR epic describes end-to-end journey with **no** child summary containing matching capability keywords (list epic phrase + "no child summary contains …" — do not assign work)
- **Medium:** PRD/Confluence linked but not fetched; UX Design status blocks design-backed assertions; child status mix prevents epic-level E2E (e.g. all UI children Done but integration children Waiting for Release) — cite counts from sample
- **Low:** Duplicate/near-duplicate child summaries in sample; naming inconsistency (Tour panel vs Tour Panel)

Do **not** produce High findings of the form "story does not define steps" — epics are not expected to define UI steps.

## Scoring (epic target)

| Field | Epic meaning |
|-------|----------------|
| **Story type** | Render as **Epic-level planning** + optional tag from child sample only: `User-facing UI (inferred from child summaries)` / `Mixed` / `Discovery` — cite JQL sample, do not guess from one child |
| **Testability** | Can QA outline **epic release verification** (smoke themes + which children need story scans)? |
| **Test scope confidence** | How well epic text + child inventory bound what to test before opening each story |
| **Risk** | Customer impact of shipping epic with open High F# on completion criteria or child hygiene |
| **Automation candidate** | **TBD** unless epic text describes repeatable cross-module UI journey; otherwise "Epic E2E after child stories clarified" |
| **Readiness** | Same three values — cite epic-blocking F# (e.g. unfetched PRD, empty children) |

## Epic scan output template

Use instead of the Story template when target is Epic. Title: `# Epic Testability Scan — {KEY}`

```markdown
# Epic Testability Scan — {KEY}

| | |
|---|---|
| **Testability** | High / Medium / Low |
| **Test scope confidence** | High / Medium / Low |
| **Risk level** | {level} |
| **Automation candidate** | Yes / No / TBD |

**Readiness for test planning:** …
**Planning scope type:** Epic-level planning (+ inferred child themes if stated)
**Scanned:** {date}
**Data sources analyzed:** …
**Data sources unavailable:** …

## Epic scope (facts)
- Goal / intent excerpt *(Source: Epic description)*
- Requirements / PRD / design links *(Source: field or description)*
- Initiative parent (if any): {key — summary}

## Design observations (Figma)
{same rules as Story scan — omit if not fetched}

## Child work inventory
_Sample: {n} issues via JQL `"Epic Link" = {KEY}`; truncated: yes/no_

| Key | Type | Status | Summary |
|-----|------|--------|---------|
| … | … | … | … |

**Status mix (sample):** {counts by status category if inferable}

## Child ↔ epic alignment (facts only)
- {epic phrase} — child keys whose summary contains related terms, or "none in sample"

## Testability findings
{F# table — epic-oriented findings}

## Epic-level user / release flows
- {only flows literally stated in epic text} *(Source: …)*
- *Not described in epic* — if absent

## Not stated in epic
- {gaps at epic level}

## Acceptance criteria / definition of done gaps
- {e.g. AC field is Figma-only; epic AC not testable without design/PRD fetch}

## Suggested testing focus (epic)
- Epic smoke / journey theme: … once {Q# / PRD / Figma} available *(blocks: …)*
- Run **story testability scan** on: {list High-risk child keys from inventory — empty description, matches epic keyword, Done but no AC in sample}

## Automation assessment
…

## Recommended next action
PO/UX: … · QA: scan children {KEYs} · Fetch PRD/Figma: …

## QA readiness checklist (preliminary)
| # | Check | Source | Owner | Done |
…

## Epic batch handoff
{Mandatory block per **Epic unified workflow**}
```

**Do not include** Story-only section **Epic context** (parent of self) or **Not in this story (from epic text)**.

## Clarification questions (epic)

Group for **PO / UX / EM**: definition of done for the epic, which PRD section is authoritative, which Figma node is canonical, priority order of child stories for E2E, rollout/feature flag. Default limits still apply (≤ 8, ≤ 5 High).

## Handoff to story scans and TCs

Epic scan ends with **Epic batch handoff** (see **Epic unified workflow**). **`recommendedBatchKeys`** replace the informal “Suggested child scans” list. Batch execution uses **`story-epic-batch-orchestrator`**; each child still gets its own scan + **Preliminary** TC table in the **Batch** tab — not one combined epic TC table.

---

## Epic context (story scans only)

When the **target** is a Story (or Bug/Task), not an Epic.

## What Epic context includes

- Epic goal and intent (**facts from epic description only**)
- Key constraints stated in epic description or comments on epic
- Related behaviors **literally mentioned** at epic level
- Sibling stories (key, summary, status)
- Factual inconsistencies between epic text and current story text *(quote both)*

## Rules

- If **no parent epic** or epic **cannot be read** → *Epic context not available — do not guess.*
- **Do not** invent epic scope from sibling titles alone
- **Do not** write *may be covered by {KEY}* or *likely implemented in sibling*
- When sibling summary shares a keyword with current story:

```markdown
- Sibling {KEY} summary includes "{term}"; not referenced in {STORY_KEY}. *(Source: JQL sibling list)*
```

- Optional question Q# only if keyword overlap is **explicit in both** story and sibling summary — ask for relationship, do not assert scope split

- JQL: `"Epic Link" = {EPIC_KEY}` limit 25, read-only; fallback `parent = {EPIC_KEY}` if empty

## Epic-level gaps (factual only)

Add bullets to *Not stated in story* or findings F# when:

- Epic states a completion criterion not reflected in story *(cite epic Source)*
- Same term defined differently in epic vs story *(cite both)*
- End-to-end journey: epic mentions step sequence; story does not state which step it owns — **GAP**, do not assign steps to siblings

## Output sections

**Epic context** — parent summary, status, intent excerpt (quoted), sibling table

**Sibling keyword overlap (facts only)** — optional table: keyword, sibling keys mentioning it, referenced in current story Y/N

**Not in this story (from epic text)** — epic facts not mentioned in story sources — not "out of scope" judgments

---

## Screenshot analysis (facts only)

Use when Jira issue has image attachments (PNG, JPG) referenced in description or listed on issue.

## When to analyze

- Description says "see screenshots below" or embeds images
- Jira MCP returns attachment with readable URL or local path
- User uploaded images in chat

## How to analyze

1. For each image attachment, **read the image** (Read tool on URL if accessible, or downloaded file)
2. If readable, add subsection under **Information identified** or dedicated **Screenshot observations**:

```markdown
### Screenshot: {filename}
- **Readable text:** {bullet list — exact strings only}
- **Source:** Attachment `{filename}`
```

3. If image **cannot be read** (auth, 403, blob URL):

- Record in `**Data sources unavailable:** Attachment {filename} (not readable)`
- Add finding F# if story relies on screenshot for scope: `Screenshot referenced in description but content not analyzed`

## Rules

- **Quote only text you can see** — no paraphrase of unreadable UI
- **Do not** add: module guess, screen name guess, layout description, old vs new intent, UX interpretation
- **Do not** use `*(Assumption from screenshot)*` in scan report body
- Map screenshot #1/#2/#3 in description to attachment filenames by order when filenames are listed
- Observed text may inform **Suggested testing focus** as "Verify visible label '{exact string}' once build available" — only if string was read

## Questions (not report facts)

Questions may ask: *Does the screenshot show column X as described?* — only when description references screenshot content not readable during scan.

## Do not

- Replace spreadsheet checklist with screenshots when both exist — use both
- Treat screenshot text as approved requirements without build verification
- Infer business rules from UI layout

---

## Figma design ingest

Use when gather finds at least one **Figma design URL** on the story, parent epic, or linked fields.

## Detection

Collect URLs containing `figma.com/design/` or `figma.com/file/` from:

1. Story description and comments (if MCP returns comment bodies)
2. Story custom fields (e.g. **Figma (URL)**)
3. Parent epic description and custom fields (e.g. **Figma (URL)**, epic **Acceptance Criteria** when the field value is a Figma link)
4. User-pasted Figma URL in the same chat as the scan request

**Priority:** story URL first; if the story has none, use parent epic URL(s). If multiple URLs differ only by `node-id`, treat as one file with multiple candidate nodes — analyze up to **3** nodes total (see Limits reference).

## URL parsing

From `https://www.figma.com/design/{fileKey}/…?node-id={id}`:

- `fileKey` — path segment after `/design/` or `/file/`
- `nodeId` — query `node-id`; convert `-` to `:` for MCP (e.g. `766-122827` → `766:122827`)
- If URL has no `node-id`, use `get_metadata` on the file root only to list top-level frames whose **names** overlap keywords from the story title/summary (e.g. "Tour", "Panel", "Guide") — then fetch ≤3 matching frames

## Fetch (when Figma MCP is connected)

1. Load **figma-design-to-code** skill when the host requires it before `get_design_context`
2. For each selected node (max **3**), call `get_design_context` with `fileKey` + `nodeId`
3. If the linked node is a large canvas/page, call `get_metadata` on that node, pick ≤3 child frames relevant to the story (by frame name: Tour, Panel, Guide, Home, Wizard, Spotlight, etc.), then `get_design_context` on those children only — do not dump the whole file

## Report output — mandatory labeling

Add section **## Design observations (Figma)** (see scan output template). Every bullet must:

- Quote **only** text visible in Figma output (labels, headings, button copy, sticky notes, visible list item titles)
- End with `*(Source: Figma — {url}, node `{nodeId}`)*` — use the same URL the user would open; include `node-id` when analyzed
- Prefix the section with one line: `_Design reference only — not verified on build._`

Also add to **Data sources analyzed:** `Figma: {url} (node {nodeId})` for each successfully fetched node.

Record failures in **Data sources unavailable:** `Figma {url} (reason: MCP missing / auth / timeout / node not found)`.

## What Figma may improve in the scan (facts only)

| Use in report | Example |
|---------------|---------|
| **Information identified** / **Design observations** | Exact button label `Exit tour` |
| **Impacted areas → UI areas** | Frame `Home`, component `Guide` |
| **Suggested testing focus** | Verify visible label `"{string}"` matches Figma once build available *(Source: Figma)* |
| **Finding F# (factual diff)** | Story text mentions `CURRENT` but analyzed Figma frames show status icons + step titles only — cite both sources |
| **Epic consistency (dim 12)** | Epic AC field points to Figma node A; story description uses terms not present in analyzed frames |

## What Figma does **not** do

- Does **not** mark behavior dimensions **COVERED** unless the behavior or rule is **literally** in Figma text (sticky, annotation) or unambiguous visible state labels — layout alone is not a rule
- Does **not** replace missing story AC for pass/fail of resume logic, permissions, or persistence unless written on the frame
- Does **not** prove implementation matches design — scan states design intent only
- Do **not** use `*(Assumption from Figma)*` in factual sections — use `Source: Figma` for observed design facts; keep behavioral gaps as F# / Q#

## Questions

May ask Q# when story and Figma disagree on labels or states (quote both). May ask which Figma node is canonical when epic and story link different nodes.

## Do not

- Invent strings not present in `get_design_context` / readable sticky text from metadata
- Auto-fetch Figma when no URL was found in gather
- Exceed **3** `get_design_context` calls per scan without user asking for a deeper pass

---

## Spreadsheet ingest

Use when a Jira story links a Google Spreadsheet (or user pastes tabular copy changes).

## Detection

Trigger ingest when description/comments contain:
- `docs.google.com/spreadsheets`
- "FOR DEVELOPERS", "NEW VERSION", "spreadsheet", "Google Sheet"

## Input modes (priority)

1. **User pasted table/CSV** in chat with scan request — parse immediately
2. **Local file** `.csv`, `.tsv`, `.xlsx` path — read if user provides
3. **Link only** — ask once:

> This story references a Google Spreadsheet. For a complete QA checklist, paste the relevant rows (Module/Screen, OLD, NEW VERSION) or attach a CSV export. I will continue the scan with available Jira content if you skip.

Do **not** fetch Google Sheets URLs automatically (no OAuth in Phase 1).

## Checklist output format

Add section to scan after ingest:

```markdown
## Spreadsheet change checklist
_Source: {filename or "Pasted table"} | Rows: {n}_

| # | Module / Screen | Old (if provided) | New (expected) | QA check |
|---|-----------------|-------------------|----------------|----------|
| 1 | ... | ... | ... | ☐ |
```

## Scoring impact

| Situation | Test scope confidence adjustment |
|-----------|-------------------------------|
| Full NEW VERSION column ingested | May raise Low → Medium or Medium → High |
| Partial paste | Keep current; note "partial checklist" |
| Link only, no paste | Keep Low if story depends on sheet |

## Link to testing focus

Each checklist row should map to a **Suggested testing focus** bullet with matching `*(blocks: Q#)*` only when NEW text is ambiguous.

---

## QA readiness checklist export

Formerly "sign-off checklist". Supports QA preparation — **does not automatically approve or reject the story**.

## When to include

- Auto: spreadsheet ingested OR ≥3 testing focus items
- On request: `export readiness checklist` / `readiness CSV` / `sign-off CSV` (aliases)

## Format

| # | Check | Source | Owner | Done |
|---|-------|--------|-------|------|
| 1 | {observable check or Pending F# / Q#} | {Source / F# / Q#} | QA | ☐ |

CSV block for Excel copy-paste. Max 50 rows. Manual/E2E oriented checks only.

## Recommended timing

Generate **final** checklist **after rescan** when story is clarified — not only after initial scan.

## Traceability

- Link each row to **Source**, finding **F#**, or `Pending Q#`
- After rescan, update rows when F# resolved

---

## Jira comment templates

Replace placeholders from the **approved** scan only. **Copy-paste only — not published automatically.**

## Full template

```
h3. Story Testability Scan — {issue_key}

_Based on the current story content, here is a collaborative testability review to support early alignment._

----

*Testability:* {High | Medium | Low}
*Test scope confidence:* {High | Medium | Low}
*Risk level:* {level} — {short rationale}
*Readiness for test planning:* {Ready with clarifications | Needs clarification before scope lock | Cannot plan scope yet}
*Automation candidate:* {Yes | No | TBD}

*Data reviewed:* {data_sources_analyzed}

h4. Top findings (testing impact)
* F1 ({severity}): {finding} — {testing impact}

h4. Information identified
* {bullet}

h4. Suggested testing focus
* {bullet}

h4. Known or suspected risks
* {bullet}

h4. Open points (may affect testing scope)
* {bullet}

----

h3. Clarification questions

{opening_line}

*{topic}*
# {question}

----

_This scan supports shift-left preparation — it does not approve or reject the story._

_Scanned via Story Testability Scanner on {date}._
```

## Short template

Use when user requests **format for Jira short**.

```
h3. Story Testability Scan (summary) — {issue_key}

_Collaborative testability summary — full detail available from QA on request._

----

*Testability:* {level}
*Test scope confidence:* {level}
*Risk level:* {level}
*Readiness for test planning:* {level}
*Automation candidate:* {Yes | No | TBD}

h4. Priority testing focus
* {bullet — max 3}

----

h3. Clarification needed

{opening_line — Medium/Low testability variant recommended}

*{topic}*
# {High priority question only — max 5}

----

_This scan supports shift-left preparation — it does not approve or reject the story._

_Scanned via Story Testability Scanner on {date}._
```

**Short mode omits:** full findings table, long information list, risks section, Medium/Optional questions, checklist table.

## Opening lines

**Ready with clarifications / High testability** (few questions):

> Based on the current story content, there is enough information to start testing preparation, but the following points should be clarified.

**Needs clarification / Cannot plan scope yet**:

> The scan identified open points that may affect testing scope or QA readiness.

## Wiki markup rules

| Element | Markup |
|---------|--------|
| Heading 3 | `h3. Title` |
| Heading 4 | `h4. Title` |
| Label | `*Label:* value` |
| Italic | `_text_` |
| Bullet | `* item` |
| Question | `# question` |
| Rule | `----` |

## Suggested labels (manual)

| Label | When |
|-------|------|
| `testability-high` / `testability-medium` / `testability-low` | Matching level |
| `qa-clarification-needed` | ≥1 High question in comment |
| `automation-candidate` / `automation-tbd` | Matching automation candidate |

One testability label only (mutually exclusive).

---

## HTML export

Generate when user requests `export HTML report` / `export html`, or automatically when completing **Epic unified workflow** (epic with or without batch). **Same facts as markdown** — no extra assumptions.

**Epic:** use **two-tab** `{EPIC_KEY}-epic-and-batch-report.html` per **Epic unified workflow**; **children summary + `<details open>` inventory first** on Tab Epic. Mirror epic template sections in Tier 2/3 — not Story **Epic context**.

### Output
- **Primary (platform):** paste complete HTML in chat
- **If file write available:** Story: `{ISSUE_KEY}-testability-report.html`; Epic: `{ISSUE_KEY}-epic-and-batch-report.html` (optional `reports/` folder)

### Structure (standalone document)
Use Tailwind CDN or simple semantic HTML. Organize into **three information tiers** so a reader gets the decision-relevant facts first and can drill into evidence/detail on demand — do not render everything flat at the same visual weight.

**Tier 1 — always visible, no interaction required.** This is the "can I proceed" summary:
1. Header with issue key, **issue type** (Story/Bug/Task/Epic — see **Scope** note at top of this file), scan label (`Initial scan` / `Rescan` + date), and Jira link
2. One-line summary counts (e.g. "3 findings — 2 High, 1 Medium · 2 open questions") directly under the header
3. **Readiness for test planning** — render this immediately after the summary counts, above the other KPI cards, since it is the single most-acted-on field. Give it a visually distinct treatment (full-width strip or top accent bar) and state the blocking F#/Q# count inline (e.g. "Blocked by 2 High findings")
4. KPI cards: Testability, Scope confidence, Risk, Automation

**Tier 2 — expanded by default, one `<details open>` block per section.** This is the "why" behind Tier 1 — most readers who care about Tier 1 will also want this without an extra click, but it's visually separated so Tier 1 stays scannable:
5. Testability findings table (F#) — **sorted High → Medium → Low**; within the same severity, keep gather order
6. Clarification questions
7. Known/suspected risks + Suggested testing focus

**Tier 3 — collapsed by default, one `<details>` block (no `open`) per section.** This is reference/audit detail — needed by someone going deep, not by someone deciding next steps:
8. Information identified (raw facts)
9. **Design observations (Figma)** — if present; badge or subtitle “Source: Figma” on each bullet
10. **Not stated in story** + **Missing or unclear information**
11. Epic context + siblings (include epic Figma URL(s) as facts when read from Jira)
12. Flows + Impacted areas
13. **QA readiness checklist** (if included per the markdown criteria) — render as a table with a checkbox-style column: `#` · `Check` · `Source` · `Owner` · `Done` (empty `☐` glyph or a disabled checkbox input); include only when the markdown scan includes it

**Always visible, outside the tier system, at the end of the document:**
14. **TC handoff** (`#tc-handoff`) — see snippet below; no TC tables in scan HTML. Mention that `@story-ui-test-cases` should reuse **Design observations (Figma)** for Expected strings when present. This is a call to action, not information to absorb, so it never collapses.

### Collapsible section markup (Tier 2 / Tier 3)

Use native `<details>`/`<summary>` — no JavaScript required, works when printed to PDF, and is keyboard/screen-reader accessible. Tier 2 sections carry the `open` attribute; Tier 3 sections omit it.

```html
<!-- Tier 2 example: expanded by default -->
<details open class="rounded-lg border border-slate-200 bg-white">
  <summary class="cursor-pointer px-4 py-3 font-medium text-slate-700 list-none flex justify-between items-center">
    <span>Testability findings <span class="text-slate-400 font-normal">(3)</span></span>
    <span class="text-xs text-slate-400 group-open:hidden">▸</span>
  </summary>
  <div class="px-4 pb-4">
    <!-- findings table -->
  </div>
</details>

<!-- Tier 3 example: collapsed by default -->
<details class="rounded-lg border border-slate-200 bg-white">
  <summary class="cursor-pointer px-4 py-3 font-medium text-slate-700 list-none flex justify-between items-center">
    <span>Epic context</span>
    <span class="text-xs text-slate-400">▸ click to expand</span>
  </summary>
  <div class="px-4 pb-4">
    <!-- epic context content -->
  </div>
</details>
```

Include an item count in every `<summary>` where the section is a list or table (e.g. "Not stated in story (4)") so the collapsed state still conveys scale.

### KPI dot colors

**Testability & Scope confidence** (higher is better): High=`bg-emerald-500`, Medium=`bg-amber-500`, Low=`bg-rose-500`

**Risk** (higher is worse): High=`bg-rose-500`, Medium=`bg-amber-500`, Low=`bg-emerald-500`

**Automation:** Yes=`bg-emerald-500`, TBD=`bg-amber-500`, No=`bg-slate-400`

**Findings table severity text:** High=`text-rose-600`, Medium=`text-amber-600`, Low=`text-slate-500` — use the same color mapping as the Risk KPI (higher severity = warmer color) for visual consistency across the report.

### TC handoff block (embed in HTML)

Replace `{ISSUE_KEY}`, `{READINESS}`, `{BLOCKING_ITEMS}`:

```html
<!-- Inner HTML for {{TC_HANDOFF_HTML}} in html-report-template.html -->
<div class="border-b border-teal-100 pb-4">
  <h3 class="text-lg font-bold text-slate-900">Next step — draft test cases</h3>
  <p class="text-xs text-slate-500">Handoff to <code class="font-mono text-teal-800">@story-ui-test-cases</code> (this report does not contain TCs)</p>
</div>
<p class="text-sm text-slate-700 leading-relaxed">
  This scan supports story clarification. It <strong>does not include</strong> test cases —
  those are generated by a separate skill, <code class="text-xs font-mono bg-slate-100 px-1.5 py-0.5 rounded text-teal-800">@story-ui-test-cases</code>.
</p>
<div class="p-4 rounded-xl bg-white border border-teal-200/80 space-y-3">
  <p class="text-sm font-semibold text-slate-900">Run <span class="font-mono text-teal-700">@story-ui-test-cases</span> for {ISSUE_KEY} and generate a proposed TC draft?</p>
  <p class="text-xs text-slate-600"><strong>Readiness:</strong> {READINESS}. <strong>Blocked by:</strong> {BLOCKING_ITEMS}.</p>
  <ul class="text-xs text-slate-600 space-y-1.5 list-disc pl-4">
    <li><strong>Recommended flow:</strong> review → Jira comment → story updated → <strong>rescan</strong> → TC</li>
    <li><strong>Now (without rescan):</strong> <em>Preliminary draft — contains assumptions that must be confirmed</em></li>
    <li><strong>After rescan:</strong> fewer assumptions; better F# → TC mapping</li>
    <li>XRay format to copy-paste — no auto-publish</li>
  </ul>
</div>
<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
  <div class="p-3 rounded-lg border border-amber-200 bg-amber-50/60">
    <div class="font-bold text-amber-900 mb-1">Option A — now</div>
    <p class="text-amber-900/90 font-mono">@story-ui-test-cases {ISSUE_KEY}</p>
  </div>
  <div class="p-3 rounded-lg border border-emerald-200 bg-emerald-50/60">
    <div class="font-bold text-emerald-900 mb-1">Option B — after rescan</div>
    <p class="text-emerald-900/90 font-mono">rescan {ISSUE_KEY} → @story-ui-test-cases</p>
  </div>
</div>
<p class="text-[11px] text-slate-500 italic">Workflow suggestion — does not block delivery.</p>
```

### Rules
- HTML content = subset of markdown scan facts only
- Flows: *Not described in story* if absent
- Do not embed test case tables — handoff prompts separate TC workflow
- Footer: read-only · not published
- All text in the HTML report, including the TC handoff block, is **English** (see **Output language rule** in Blocked phrases)
- **Tier assignment is fixed by section, not by content length or severity** — a section stays in its tier (e.g. Findings always Tier 2) even on a scan with zero findings; render the section with an empty-state line ("No findings") rather than moving it to a different tier or omitting it
- The markdown scan report has no tiers — it is one linear document as defined elsewhere in this file. Tiering is an HTML-only presentation layer; do not change what content exists, only how it is progressively disclosed

---

## Examples (tone calibration)

**Report rule:** factual sections = stated content + Source refs only. Gaps → F#, *Not stated*, questions — never assumptions in report body.

### PROJ-1842 (Medium) — excerpt

**Readiness:** Needs clarification before scope lock — _blocked by F1, F5_

| ID | Severity | Finding | Testing impact |
|----|----------|---------|----------------|
| F1 | High | Discount calculation order not stated | Cannot define expected totals |
| F5 | High | Promotion Service unavailable behavior not stated | Cannot plan fallback tests |

- User enters discount code before payment. *(Source: Description)*
- *Not described in story* — step sequence for user flows
- **Automation:** TBD — pending Q1, Q5

### ONE-323108 (Medium) — sparse story excerpt

**Readiness:** Needs clarification before scope lock — _blocked by F1, F2_

| ID | Severity | Finding |
|----|----------|---------|
| F1 | High | Sort trigger, columns, direction not stated |
| F3 | Medium | Sibling ONE-309217 mentions sorting; not referenced in story |

- Sorting on Overview requested. *(Source: Description)*
- User flows: *Not described in story*
- Epic sibling fact only: ONE-309217 summary includes "sorting on Overview". *(Source: JQL)*

### ONE-324502 (Epic, Medium) — excerpt

**Readiness:** Needs clarification before scope lock — _blocked by F1 (PRD not fetched), F2 (child descriptions empty in sample)_

| ID | Severity | Finding | Testing impact |
|----|----------|---------|----------------|
| F1 | High | Epic completion criteria only in linked PRD/Confluence — body not analyzed | Cannot lock epic DoD tests |
| F2 | High | {n} of {sample} children have empty description in Jira | Story-level scope unknown until child scans |

**Child work inventory:** 25-row sample · Guided onboarding Q3 · mix Done / Waiting for Release *(Source: JQL Epic Link)*

**Suggested child scans:** ONE-338330, ONE-341257, … *(empty description or epic keyword "tour")*

**Suggested testing focus:** Epic E2E smoke after PRD + Figma ingested; per-story scan before TC import.