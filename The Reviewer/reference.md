# The Reviewer — reference

Supporting detail for [`SKILL.md`](SKILL.md). Every rule here traces to a decision in [`DECISIONS.md`](DECISIONS.md); rulings are cited inline as `(D#)`, `(A-#)`, `(R-G#)`, `(RV#)`, `(U-#)`.

---

## Severity model

One scale for findings, a separate scale for questions — not two competing severity scales (RV2).

| Finding severity | Meaning | `blocks_test_generation` | Gate impact |
|---|---|---|---|
| **CRITICAL** | Missing/untestable AC, unresolved blocking open question, scope contradiction, live secret/credential in text. **Story/Bug/Task only — never raised in Epic mode** (capped at HIGH, see "Epic-specific finding patterns") | computed `true` | `BLOCKED` unless `force=true` |
| **HIGH** | Ambiguous or non-atomic AC, a Group B behavioural GAP that blocks defining pass criteria, unredacted PII in output, missing testability signal | computed `false` | `PASS_WITH_WARNINGS` |
| **MEDIUM** | Template/source-completeness gap, minor clarity issue, edge-scope behavioural GAP | computed `false` | `PASS_WITH_WARNINGS` |
| **LOW** | Suggestion, nice-to-have, low-impact behavioural GAP | computed `false` | `PASS` |

| Question priority | Meaning |
|---|---|
| **High** | Unblocks a HIGH+ finding or a core-behaviour definition. **Mandatory** for any question that clears a HIGH+ finding (PRF-13). Max 5 per scan by default — merge related questions first, then go up to the 15 limit with `report.question_cap_reason`. |
| **Medium** | Unblocks a MEDIUM finding or a significant edge-scope gap. |
| **Optional** | Unblocks a LOW finding; polish or readiness nuance. |

Gate decision table (stated once here — do not restate the numbers elsewhere, per `checklist.md`'s own append-only convention):

| Condition | `gate.status` | Agent action |
|---|---|---|
| 0 CRITICAL, 0 HIGH, 0 MEDIUM (LOW only, or no findings) | `PASS` | May proceed to `The Creator` |
| 0 CRITICAL, ≥1 HIGH or MEDIUM | `PASS_WITH_WARNINGS` | Proceed; list warnings |
| ≥1 CRITICAL, no `force` | `BLOCKED` | Stop. List CRITICAL findings. Do not suggest test generation. |
| ≥1 CRITICAL, `force=true`, QA confirms in chat | `PASS_WITH_WARNINGS` | Set `gate.force_override`, `force_override_by`, `force_override_at` |

(A-3, amended by PRF-14 — MEDIUM gives warnings, LOW alone does not, matching the severity table above. The renderer lint recomputes the gate from severity counts and flags a mismatch.)

**Epic targets:** `BLOCKED` is unreachable, because Epic mode never emits a CRITICAL finding. An Epic scan's gate is `PASS` or `PASS_WITH_WARNINGS`, and the batch handoff is always offered.

### Gate line (Tier 1, rendered under the readiness strip)

The gate is shown to humans as one fixed sentence, never as the enum and never using a blocked phrase:

| `gate.status` | Gate line |
|---|---|
| `PASS` | Test case drafting can start. |
| `PASS_WITH_WARNINGS` | Test case drafting can start; the findings below should travel with it. |
| `PASS_WITH_WARNINGS` + `force_override` | Test case drafting was started by explicit override ({force_override_by}, {date}); {n} critical finding(s) remain open. |
| `BLOCKED` | Test case drafting waits on {n} critical finding(s). |

For an Epic target, replace "Test case drafting" with "Child scans".

When the Epic has **no linked child issues** (child inventory empty, or every child is Canceled), the renderer uses fixed lines instead — never "Child scans can start":

| `gate.status` | Gate line (zero children) |
|---|---|
| `PASS` | No child issues are linked yet; epic-level review is clear enough to break work down when children exist. |
| `PASS_WITH_WARNINGS` | No child issues are linked yet; address the findings below before individual child scans. |

### Post-delivery framing (Epic, PRF-15)

When `scope.lifecycle == "post_delivery"`:

- The scan label renders as **Post-delivery review** (in place of "Initial scan"; a rescan reads "Post-delivery rescan").
- The readiness heading reads **Readiness for regression and sign-off** instead of "Readiness for test planning", in every output including the Jira comment.
- A fixed lead sentence opens the readiness line: *"This epic is already {status}: the findings below are gaps to close for regression coverage and sign-off, not reasons to hold back the build."* `{status}` comes from `requirements[0].status` when present; otherwise the renderer uses **"delivered"**.
- Nothing else changes: readiness values and labels, severities, gate, and checklist rows are identical to a pre-delivery scan.

---

## Finding categories

| Category | Allowed checklist rows |
|---|---|
| `acceptance_criteria` | A3 |
| `scope` | A2 (missing out-of-scope note), A4 |
| `testability` | A8, B9, B10 |
| `traceability` | A5 |
| `open_questions` | A6, A8 |
| `template_compliance` | A1, A2, A8 |
| `data_sensitivity` | A7 |
| `behavioral_gap` | B1–B12 |
| `epic_lifecycle` | C1–C3 (Epic scope only) |

The renderer lint rejects any other pairing and any C-row in Story/Bug/Task scope (PRF-19).

## Finding and question ID formats

- Finding: `RR-{JIRA_KEY}-{NN}` — e.g. `RR-PROJ-456-01`.
- Question: `Q{n}` — e.g. `Q1`, `Q2`. Sequential within a run **in display order** (assigned after grouping by topic, PRF-17), not globally unique across runs.

### Question topic order

All ten topics are valid in any scope. The report groups them in this fixed order:

| Scope | Order |
|---|---|
| Story / Bug / Task | Behavior · Scope · Edge cases · Integrations · Permissions · Data · Definition of done · PRD authority · Design authority · Rollout |
| Epic | Definition of done · PRD authority · Design authority · Rollout · Behavior · Scope · Edge cases · Integrations · Permissions · Data |

---

## Owner routing

`owner_hint` generalises the original PM-only model (R-G8). Use the narrowest owner who can actually act:

| `owner_hint` | When |
|---|---|
| `PM` | Default for story-scope AC/scope/behaviour questions |
| `UX` | Figma/design disagreement, copy/labelling questions |
| `EM` | Technical feasibility, integration/dependency questions |
| `Security` | `data_sensitivity` findings |
| `PO` | Epic-scope definition-of-done, PRD authority, rollout questions; the default for epic-scope acceptance-criteria and scope questions (PRF-17) |

---

## Tool mapping

Logical capability names, mapped per host. A missing capability degrades with a stated warning — it never silently aborts the whole run for a single missing tool (A8, architectural decision).

| Logical capability | Atlassian MCP (Cursor/Claude) | Notes |
|---|---|---|
| `jira_search` | `searchJiraIssuesUsingJql` | Epic child inventory: paginate to `isLast`, request **`view: "full"`**. If `description` is missing on a row, fall back to **`getJiraIssue`** for that key before `title_only` |
| `jira_get_issue` | `getJiraIssue` | Target issue, AC field, and **per-child description fallback** when search omits the field |
| `jira_get_issue_links` | `issuelinks` on `getJiraIssue` **and** `listJiraIssueRemoteIssueLinks` (via `executeRead` when not a primary tool) | Issue links from the issue body; **web links** (Confluence URLs, etc.) from remote links — both are required in gather step 6 |
| `jira_add_comment` | `addOrEditJiraIssueComment` | **opt-in only** — `policy.jira_comment == "auto-post"` (Q6) |
| `confluence_get_page` | `getConfluenceContent` with `detail: "full"` (or an equivalent full-body preset) | Summary-only responses are not sufficient for AC or scope checks (R-G2) |
| `confluence_search` | `searchConfluence` | used only if a linked page's exact id/URL can't be resolved directly |
| `figma_get_design_context` | `get_design_context` (Figma MCP) | ≤3 calls per scan |
| `figma_get_metadata` | `get_metadata` (Figma MCP) | frame shortlisting only |
| `site_routing` | `getAccessibleAtlassianResources` on each connected Atlassian server | Map host → server + `cloudId` once per run; every read of a link, page, or attachment goes to the server whose site matches its host (PRF-24). No match → `unavailable` with the fixed reason. |
| `jira_list_attachments` | `getJiraIssue` with `fields: ["attachment"]` | returns numeric attachment ids, filename, mimeType |
| `screenshot_read` | `downloadJiraIssueAttachment` / `downloadConfluenceAttachment` (via `executeRead`) → run the returned `downloadCommand` to a temp path outside the repo → vision read → delete the file | Verified working 2026-09-29 (PRF-23). Bytes never pass through the model as data; only the derived text is redaction-checked (second-pass resolution). Never persist the signed URL or the image. **No browser fallback.** |

On Hive, the same logical capabilities resolve through whatever MCP tools Hive has connected; if the exact tool name is unavailable, look for a semantically equivalent connected tool before declaring the source unavailable.

---

## Redaction rules

Display-time, not pre-analysis (A-6 — the original "redact before LLM analysis" wording was unimplementable for an agent-driven fetch, since the agent *is* the model doing the reading).

1. The model may read raw Jira/Confluence text and screenshot images directly — this is unavoidable and, for screenshots, a deliberately adopted capability (second-pass resolution: "allow vision").
2. Before any string reaches `excerpt_quote`, a report bullet, a Jira comment draft, or an HTML report: mask patterns that look like API keys, tokens, or passwords; replace live customer names/emails with placeholders.
3. If unredacted sensitive data would otherwise reach output, emit a `data_sensitivity` CRITICAL finding (checklist `A7`) instead of the raw text.
4. This applies identically to text derived from Jira fields, Confluence pages, spreadsheet pastes, and screenshot reads — one rule, four sources (R-G6).

---

## Limits reference (canonical — do not restate numbers elsewhere)

| Limit | Value |
|---|---|
| Clarification questions (default) | ≤ 8 total, ≤ 5 High |
| Clarification questions (complex story, justified) | ≤ 15 (state why) |
| New questions per rescan | ≤ 5 |
| Cumulative open questions across rescans | **No cap** (confirmed — an earlier ≤15 proposal was dropped) |
| Sibling stories fetched | ≤ 25 |
| Epic children | Paginate to `isLast` — full inventory always, never a sample. Each child's `description` is fetched in the same call (decision C4) — the "never a sample" rule binds content as well as the key/summary/status list, not just the latter. |
| Recommended batch | Every non-Canceled child, no cap, ranked; scanned in groups of 8 (PRF-16) |
| Batch ranking — "named by findings/questions" | At most **one** rank point per open finding (severity CRITICAL/HIGH/MEDIUM) and per open question when the child key appears in that finding's summary/testing-impact blob or that question's text/context/unblocks — not per field, and not from `excerpt_quote` |
| Figma nodes analyzed per scan | ≤ 3 |
| Readiness checklist CSV rows | ≤ 50 |
| QA readiness checklist auto-include threshold | ≥ 3 suggested-testing-focus items |
| Numeric scores / percentages / weighted totals in rendered prose | **0 — never.** Raw counts ("3 findings, 2 High") are always fine; derived numbers are payload-only (D12/A-13). |

---

## Classification decision trees

### Testability (High/Medium/Low)

- **Low** if no observable expected behaviour can be cited with a Source, or the scope boundary is undefined for the main change.
- **Medium** if core intent is clear but ≥1 HIGH finding affects scope, pass criteria, or primary-flow definition.
- **High** if observable behaviour and scope are clear; remaining gaps are none, or LOW/Optional only.

An empty AC field alone does not lower testability if the description/comments provide equivalent detail.

### Test scope confidence (High/Medium/Low)

Confidence that QA can define a **complete intended test scope** from current content — not an assessment of existing automated coverage.

- **Low** if ≥2 HIGH findings on scope-defining rows (A3, A4, B1, B3, B4, B5).
- **Medium** if an outline is possible but ≥1 HIGH finding remains on behaviour or edge cases.
- **High** if scope-defining rows are mostly COVERED and remaining gaps are Optional.

### Risk (High/Medium/Low + rationale tags)

Story-level risk, distinct from finding severity — a story can be Medium risk with several HIGH findings. Add 1–2 tags: `customer impact` · `regression surface` · `permissions/security` · `data integrity` · `integration dependency` · `reversibility`.

- **High** if the stated or gap-affected area touches security, payments, data loss, or broad regression with undefined behaviour.
- **Medium** if there's meaningful regression/integration dependency with partial definition.
- **Low** if the change is narrow, well-bounded, with clear stated outcomes.

### Automation candidate (Yes/No/TBD)

- **Yes** — repeatable, observable UI outcomes stated; stable flow implied; no blocking HIGH findings on behaviour.
- **No** — discovery-only, no user-observable outcome, or manual-only verification explicitly required.
- **TBD** — behaviour/assertions undefined, pending a HIGH finding's resolution.

`suggested_level` is always a **logical** level (`UI E2E` / `API` / `Unit` / `TBD`) — never a specific framework name (A-18). The framework comes from `config.assets` / product config, not from this skill.

### Readiness for test planning

| `readiness.value` | `readiness.human_label` (the only thing a PM sees) | When |
|---|---|---|
| `ready_with_clarifications` | Ready to build tests | Testability High or Medium; no HIGH finding on core behaviour; **only Optional questions open** (RV1 + A-15, the stricter of two originally-conflicting definitions) |
| `needs_clarification_before_scope_lock` | Needs clarification before test design | Medium testability, or ≥1 HIGH finding/question on scope or pass criteria, or any open Medium question |
| `cannot_plan_scope_yet` | Needs clarification before scope can be tested | Low testability or low scope confidence; core behaviour or scope undefined |

`readiness.value` and `gate.status` are **independent axes** (PRF-10): the gate comes from severity counts only; readiness comes from the tree above. Any combination is valid — e.g. `PASS_WITH_WARNINGS` with `cannot_plan_scope_yet` means "The Creator may run, but expect a thin or provisional suite." Never adjust one to make it agree with the other.

---

## Epic-specific finding patterns

**Severity cap (PRF-12):** Epic mode never emits CRITICAL. Where a Group A row would be CRITICAL on a Story (`A3`, `A4`, `A6`, `A7`, `A2`), emit it as HIGH on an Epic. `A7` redaction and `Security` routing still apply unchanged.

| Severity | Pattern |
|---|---|
| HIGH | No testable completion criterion in analyzed sources (only an unfetched PRD/Figma link), or the Epic's own text marks its completion criterion as unresolved |
| HIGH | A **strict majority** (> half) of the **complete** child set has `content_source: title_only` or `unavailable` while `scope.lifecycle` is **`pre_delivery`** and the Epic is still active — a 50/50 tie does not qualify. Skip this pattern on **`post_delivery`** Epics (historical empty descriptions are expected). |
| HIGH | The epic describes an end-to-end journey with no child **description** containing matching capability keywords (falling back to a child's summary only where its description is empty, per B12/C4) — name the gap, never assign the work to a child |
| MEDIUM | A linked PRD/Confluence page was not fetched (fetch it now — R-G2 — before falling back to this) |
| MEDIUM | Child status mix prevents an epic-level E2E pass (e.g. all UI children Done, integration children still Waiting for Release) |
| MEDIUM | A specific child that is materially in scope for a finding/question has `content_source: title_only` — name that child, don't silently reason from its title as if it were description text |
| LOW | Duplicate/near-duplicate child summaries; naming inconsistency across children |

Never produce a HIGH finding of the form "the epic does not define UI steps" — epics aren't expected to.

---

## Markdown report template

Produced by `scripts/render_report.py`; this is the shape it writes (see `samples/demo-*.report.md`). Change the script and this template together.

```markdown
# Requirement Review — {run_id}

**Scanned:** {scan_label} — {date}
**Scope:** {issue_type} — [{key}]({url}) — "{summary}" · Status: {status}
**Product:** {product} · schema {schema_version}
**Data sources analyzed:** {list}
**Data sources unavailable or failed:** {list, with reasons | none}

**Readiness for test planning:** {human_label}      ← "Readiness for regression and sign-off" when scope.lifecycle == post_delivery
_{post-delivery lead sentence, if applicable} {report.readiness_line}_
{gate line — see "Gate line"}

**Testability:** {level} · **Test scope confidence:** {level} · **Risk:** {level} ({tags}) · **Automation candidate:** {value}

## Findings
| ID | Severity | Checklist ref | Finding | Testing impact | Owner |

## Clarification questions
### {Topic}                      ← fixed topic order; questions sorted by number within a topic
#### Q{n}. {question}
- Context: … · Source: … · Priority: … · Unblocks: … · Owner: …

## Not stated in {issue type}    ← "story", "epic", "bug", "task"
## Known or suspected risks
## Suggested testing focus       ← each item may end "(waits on: {ids})"
## Information identified
## Design observations (Figma)   ← only if report.design_observations is non-empty
## Epic context                  ← Story/Bug/Task only
## QA readiness checklist (preliminary)   ← | # | Check | Source | Owner | Done |
## Child inventory & status mix  ← Epic only
## Epic batch handoff            ← Epic only
## Recommended next action

---
_This review supports shift-left preparation. It does not approve or reject the requirement._
```

---

## Jira comment templates (copy-paste only, unless `policy.jira_comment == "auto-post"`)

### Full

```
h3. Requirement Review — {issue_key}

_Based on the current content, here is a collaborative review to support early alignment._

----
*Testability:* {level}    *Test scope confidence:* {level}
*Risk level:* {level} — {rationale}    *{readiness heading}:* {human_label}
*Automation candidate:* {value}

*Data reviewed:* {data_sources_analyzed}

h4. Top findings (testing impact)
* {severity} — {finding}: {testing impact}

h4. Clarification questions
*{Topic}*
# {question} _— for {owner}_
----
_This review supports shift-left preparation — it does not approve or reject the requirement._
```

### Short (High-priority only, max 5 questions)

```
h3. Requirement Review (summary) — {issue_key}

*{readiness heading}:* {human_label}

h4. Priority clarification needed
*{Topic}*
# {High priority question only} _— for {owner}_
----
```

`{readiness heading}` is "Readiness for test planning", or "Readiness for regression and sign-off" for a post-delivery Epic (PRF-15).

Both comments are generated by `scripts/render_report.py` as `jira-comment-full.txt` and `jira-comment-short.txt` (PRF-22); the templates above describe their shape.

### Wiki markup rules

| Element | Markup |
|---|---|
| Heading 3/4 | `h3. Title` / `h4. Title` |
| Label | `*Label:* value` |
| Italic | `_text_` |
| Bullet | `* item` |
| Numbered question | `# question` |
| Rule | `----` |

---

## HTML report — tier specification

**Implemented by `scripts/render_report.py` (PRF-21)** — this spec describes what the script produces; change the script and this section together. [`sample-report.html`](sample-report.html) (Story) and [`sample-report-epic.html`](sample-report-epic.html) (Epic) are the script's output on `samples/demo-story.payload.json` and `samples/demo-epic.payload.json`; regenerate them after any renderer change rather than editing them. Tier assignment is **fixed per section**, never by content length or severity — a section with zero findings still renders with an empty-state line ("No findings"), it never moves tier or disappears.

**Tier 1 — always visible, no interaction:**
1. Header: issue key, issue type, scan label + date, Jira link.
2. One-line summary counts ("3 findings — 2 High, 1 Medium · 2 open questions").
3. Readiness strip — full-width, visually distinct, colour from `readiness.value` only, states the blocking finding/question count inline; directly beneath it, the **gate line** (see "Gate line" above).
4. KPI cards: Testability, Test scope confidence, Risk, Automation candidate.

**Tier 2 — `<details open>`, one block per section:**
5. Findings table, sorted High → Medium → Low.
6. Clarification questions, grouped by topic.
7. Known/suspected risks + suggested testing focus.
7a. **Epic mode only:** child inventory + status mix (moved from Tier 3 — for an Epic it's the primary content for release managers, PRF-21), followed by the Epic batch handoff block.

**Tier 3 — `<details>` (collapsed), one block per section:**
8. **Data sources** — every `context_loaded[]` entry with its status and reason if not `analyzed`. Display labels: `analyzed` → Analyzed, `unavailable` → Unavailable, `failed` → **Could not read** (PRF-11 — the payload value stays `failed`), `not_applicable` → Not applicable. **Always rendered**, even when every source succeeded — the empty state is an explicit "No sources were unavailable or failed in this run" line, not a hidden or dropped section. This is the section addressed to persona P10 (Platform/MCP administrator); see `PERSONA-REVIEW.md` PRF-04.
9. Information identified (raw facts).
10. Design observations (Figma) — only if `report.design_observations` is non-empty.
11. Not stated in {issue type} — "Not stated in story", "…in epic", "…in bug", etc.
12. Epic context / siblings — Story/Bug/Task only (Epic mode shows the child inventory in Tier 2 instead).
13. QA readiness checklist, if included.

After Tier 3: Recommended next action (always visible).

**Always visible, outside the tier system, at the end:** the TC handoff block — a call to action pointing at The Creator, never test case tables themselves.

No JavaScript is required for tiering — native `<details>`/`<summary>` survives printing to PDF and is keyboard/screen-reader accessible. Inline CSS only, no CDN (D1/C3.3). A light decision layer (accept/reject/needs-discussion per finding, with an export-decisions button) is additive on top of this — see `sample-report.html`'s script block — and the document stays fully readable with JavaScript disabled.

**Decision-layer ids (PRF-21):** every decision control, and the exported decisions file, uses the payload's own id — the full `finding_id` (`RR-ONE-333681-01`, never `F1` or `RR-01`) or `question_id` — so an exported file joins back to the payload on rescan. The export carries `run_id`, `jira_key`, and `schema_version`. The "N of M items decided" total is computed from the inclusion rule below, never hand-set.

**Decision-layer inclusion rule (PRF-05):** a decision control (Accept/Reject/Needs discussion) renders only for a **HIGH+ severity finding** or a **High-priority question** — the same threshold the gate itself treats as worth a human's attention. MEDIUM/LOW findings and Medium/Optional questions render without a decision control; they still appear in their tables/cards, just without the row of buttons. This is a deliberate signal-to-noise choice, not an omission — don't add controls to every row when extending the sample.

**Owner display (PRF-03):** `owner_hint` renders in both the HTML and Markdown reports — as an **Owner** column in the findings table, and as an owner badge on each clarification-question card (alongside its topic and priority). Colour is cosmetic only (see `sample-report.html` `.owner.*` classes); the value itself always comes from the owner-routing table above, never from which HTML colour looked right.

**KPI colour mapping** (unchanged, restated for proximity to the states below): Testability/Scope confidence (higher is better) — High `emerald`, Medium `amber`, Low `rose`. Risk (higher is worse) — inverse. Automation — Yes `emerald`, TBD `amber`, No `slate`.

**Readiness-strip and severity states (PRF-02):** three readiness-strip states exist — `ok` (emerald, `Ready to build tests`), `warn` (amber, `Needs clarification before test design`), `blocked` (rose, `Needs clarification before scope can be tested`) — mapping 1:1 to `readiness.value`, and **never** to `gate.status` (a rose strip does not mean the gate is `BLOCKED`; the gate line says what the gate is). Finding severity has four CSS states, `CRITICAL`/`HIGH`/`MEDIUM`/`LOW`. `sample-report.html` only demonstrates `warn`/HIGH/MEDIUM/LOW (a `PASS_WITH_WARNINGS` scan); all four severity classes and all three strip states are defined in its CSS regardless, so a `BLOCKED` or clean-`PASS` render needs no new CSS — only different data.

KPI colour mapping: Testability/Scope confidence (higher is better) — High `emerald`, Medium `amber`, Low `rose`. Risk (higher is worse) — inverse. Automation — Yes `emerald`, TBD `amber`, No `slate`.

---

## Config additions (extends `working-plan.md` §6)

```json
{
  "policy": {
    "jira_comment": "off",
    "confluence_fetch": true
  }
}
```

`policy.jira_comment` — `"off"` (default, copy-paste block still generated) | `"copy-paste-only"` (explicit, same effective behaviour as off) | `"auto-post"` (calls the Jira comment-write capability directly).

---

## What this skill does NOT do (restated for the reference reader)

- Generate test cases, write to Xray, verify against product code, auto-fetch a PDF, or approve/reject a requirement. See `SKILL.md` for the full list and the decisions behind each.
