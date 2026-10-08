---
name: reviewer
description: >-
  Product-agnostic requirement quality review for Jira Stories, Bugs, Tasks,
  and Epics. Runs a unified structural + behavioural checklist, emits findings
  (F#) and clarification questions (Q#), classifies readiness, and gates
  The Creator on CRITICAL gaps. Read-only on Jira and Confluence; screenshots,
  spreadsheets, and Figma are optional read-only inputs. Use when reviewing a
  requirement before test creation, when asked for an AC/requirement quality
  check, a testability scan, or a review-only pass — on Cursor, Claude, or
  Hive.
disable-model-invocation: true
---

# The Reviewer

Structured quality review of a Jira requirement **before** test case generation. Produces a schema-valid `ReviewPayload`, a human report (Markdown + optional self-contained HTML), findings graded CRITICAL/HIGH/MEDIUM/LOW, clarification questions, and a **gate** — a real, machine-enforced verdict that stays separate from the tone of what a PM actually reads.

**Does not:** generate test cases, write to Xray, silently auto-post to Jira (copy-paste is always available; auto-post is a separate opt-in capability — see §7), verify against product code, or auto-fetch a linked PDF.

Every non-obvious rule below traces back to a maintainer-local decision record (`DECISIONS.md`, not published in this repo) — that file is the record of *why*; this file is *what to do*.

---

## Scope: issue types

Primary mode is **Story**. For **Bug** or **Task**, run the same workflow but substitute the actual issue type in all output text, and skip the acceptance-criteria checks (checklist `A3`) unless an AC-equivalent field exists — never silently treat a Bug or Task as a Story. For **Epic**, use **Epic mode** (§6) — a dedicated gather, checklist interpretation, and epic-level Creator handoff (CR-EPIC-01) — never the single-issue Story template.

## Hosts

Fully supported: **Cursor**, **Claude** (Code and desktop), and **Hive MCP**. On Hive, this skill is loaded via `hive-mcp__load_skill` / `hive-mcp__run_skill`; a `result: "noop"` response is a trigger to execute, not a final answer — never stop at "skill loaded." On all three hosts, execute the full workflow and return the full report in the same turn.

## Paths (config-relative — never hardcoded)

| Resource | Resolved from |
|----------|---------------|
| Unified checklist | `{skill_root}/checklist.md` |
| `ReviewPayload` schema | `{skill_root}/schemas/review-payload.schema.json` |
| Reference (severity, tools, redaction, limits, templates) | [`reference.md`](reference.md) |
| **Shareable HTML rules (all tools)** | [`../shared/html-report-guidelines.md`](../shared/html-report-guidelines.md) |
| Examples | [`examples.md`](examples.md) |
| Profile A report renderer | `{skill_root}/scripts/render_report.py` (payload → `review-report.md`, `review-report.html`, Jira comment drafts) |
| Profile B portfolio builder | `{skill_root}/scripts/build_portfolio_report.py` (multi-Epic run folder → `portfolio/index.html`) |
| **Persona** (tone, automation lens) | `{trinity_root}/personas/{persona_id}` — default `reviewer-expert-qa-automation.md` |
| **Portfolio run config** | `{skill_root}/config/runs/{portfolio_id}.json` — see **Interactive run configuration** |
| Run config schema | `{skill_root}/schemas/run-config.schema.json` |
| Nested Confluence hop (repair) | `{skill_root}/scripts/nested_confluence_rescan.py` (`discover` / `apply` + MCP body cache) |
| Full-fidelity helpers | `{skill_root}/scripts/fetch_confluence_queue.py` (`discover-pending`, `ingest-mcp` from `_gather/nested-rescan/mcp/*.json`), `{skill_root}/scripts/merge_epic_gather.py` (live per-epic harvest `_gather/epics/{KEY}.json` + cache → `context_loaded`; writes `{KEY}.pages.json` dossier), `{skill_root}/scripts/close_merge_only_epics.py` (stub delta when re-review workers did not finish) |
| Question normalizer (batch fix) | `{skill_root}/scripts/enrich_questions.py` (`--run-dir`, optional `--force`; expand why/source from findings; PRF-11-safe paraphrase outside quotes; PM default — not a substitute for gather) |
| Portfolio static template | `{skill_root}/portfolio-report-template/` (copied into each run's `portfolio/`; do not hand-edit run copies) |
| Demo payloads (sources of the sample reports) | `{skill_root}/samples/demo-story.payload.json`, `demo-epic.payload.json` |
| Per-product config | session parameter → `config/<product>.json` → `config/default.json` → built-in defaults |
| Artifacts output | `{config.output.artifacts_dir}/{run_id}/` |

The skill announces which **product config** and **portfolio run config** it resolved at the start of every run.

## Interactive run configuration (mandatory)

**Always run this interview before the first gather** for a portfolio program, and at the start of every later session unless the operator explicitly passes a complete `portfolio_id` **and** says to skip the interview.

Load [`../personas/README.md`](../personas/README.md) and the selected persona file. Apply it to findings, readiness, and every **Q#** (testability / automation focus).

### Detect first run vs return visit

| Situation | Action |
|-----------|--------|
| No `{skill_root}/config/runs/{portfolio_id}.json` for the program the operator names | **First-run wizard** (all questions below) → write new JSON |
| File exists | Ask: **“Any changes to run configuration?”** (yes/no). **No** → confirm **“Same scope as {portfolio_id}?”** (yes/no); on yes, load file and continue. **Yes** → ask only changed fields → bump `updated_at` and save |
| Operator supplies new `portfolio_id` | Treat as first run for that id |

### First-run wizard (order)

1. **`portfolio_id`** — stable id (e.g. `2026-Q4-bp-planning`). Suggest: `YYYY-MM-DD-{short-label}` if they have no preference.
2. **Scope** — paste **Jira filter URL**, **JQL**, **comma-separated Epic keys**, or **single Epic browse URL** (`scope.kind` + `scope.value`).
3. **Pass type** — `full_sweep` · `rescan_delta` · `new_epics_only` (map to `mode` / rescan rules in §11).
4. **`product_id`** — which `{skill_root}/config/{product_id}.json` (default `default`).
5. **`persona_id`** — file under `Trinity/personas/` (default `reviewer-expert-qa-automation.md`).
6. **Child scans** — `epic_only_inventory` (default) or `include_child_checklists` for this program (Epic mode still obeys CR-EPIC-01 for Creator handoff).
7. **Confirm outputs** — payload + per-epic HTML; portfolio when ≥2 epics (no opt-out unless operator insists).
8. **Creator handoff** — confirm default excludes `qa_planning_fit: not_fit` epics (`creator_handoff_exclude_not_fit: true`).
9. **Jira comments** — policy is **generate files first**; never auto-post. After reports are reviewed/edited, ask whether to post comments and/or publish Q# to Jira (see §12).

Write or update `{skill_root}/config/runs/{portfolio_id}.json` per `schemas/run-config.schema.json`. Set `planning_dates` to `jira_due_then_end`. Announce the saved path.

**JQL / filter scope:** after the operator resolves epics in Cursor (MCP search, **Epic** issuetype only), they paste keys in Trinity Studio (**Reviewer configs → Resolved epic keys**) or you record `resolved_epic_keys` in the saved JSON. Keep `scope.value` as **`source_jql`** for portfolio Creator handoff (`creator-handoff.json` / Studio handoff). Cap awareness: warn above 100 epics, max 200 in `resolved_epic_keys`.

**Return visit with unchanged config:** after scope confirmation, set `artifacts_dir/{portfolio_id}/` (or dated subfolder per pass — announce `{portfolio_run_id}`) and run gather using stored `scope` and `pass_type`.

## Session parameters

| Parameter | Required | Notes |
|-----------|----------|-------|
| `scope` | Yes | Issue key, Epic key, JQL, or bundle file path |
| `run_id` | Yes | Generate a timestamp-based id if not supplied; announce it |
| `mode` | No | `scan` (default) · `rescan` · `jira-comment-short` · `jira-comment-full` · `html` · `readiness-checklist` |
| `force` | No | Override past CRITICAL findings — requires explicit chat confirmation |
| `artifacts_dir` | No | Override `config.output.artifacts_dir`. Portfolio/JQL runs use `Trinity/reviewer/runs/{portfolio_run_id}/` (see **JQL / portfolio scope** below). |

### JQL / portfolio scope (many Epics)

When `scope` is a **JQL** (or URL whose query is JQL) that returns **multiple** issues:

1. **Resolve the full key list** — paginate Jira search to `isLast`; announce the count.
2. **One Epic = one review run** — never merge several Epics into a single `review-payload.json`, never emit one combined HTML report for the portfolio, and never use `--batch` / `confirm batch` / per-child Creator batches.
3. **Output layout** — for portfolio run id `{portfolio_run_id}` (default: `YYYY-MM-DD-{label}` if not supplied), write each Epic under `{artifacts_dir}/{portfolio_run_id}/{EPIC_KEY}/` with its own `review-payload.json`, `review-report.html`, `review-report.md`, and Jira comment drafts. The HTML is **Profile A** per [`../shared/html-report-guidelines.md`](../shared/html-report-guidelines.md) — each file is self-contained and shareable on its own (zip one folder or attach one `.html`).
4. **Parallelism** — run Epics **in parallel** (separate agent threads/tasks) when the host allows; each thread executes the full workflow for **one** key only.
5. **Portfolio bundle (required when ≥2 Epics)** — after every epic payload renders with `--strict`, run `{skill_root}/scripts/build_portfolio_report.py --run-dir {artifacts_dir}/{portfolio_run_id}` (pass `--title` / `--jql` when known). This writes **`{artifacts_dir}/{portfolio_run_id}/portfolio/`** — **Profile B** per [`../shared/html-report-guidelines.md`](../shared/html-report-guidelines.md): `index.html`, `assets/`, generated `data/report-data.js`, and copies of each epic report under `portfolio/epics/{KEY}/` (relative links only — portable on any machine). The portfolio synthesises finding **categories** (themes), **gap signal pills** (e.g. missing AC + backlog gaps when both apply), readiness, planning dates, and QA planning fit. **Creator handoff:** per-epic checkboxes (default excludes `qa_planning_fit: not_fit`), live JQL preview, export `creator-handoff.json`; builder also writes `portfolio/data/creator-handoff.json` and `portfolio/creator-handoff.md` for The Creator. **List `portfolio/index.html` first** in the run output paths you return to the operator (zip `portfolio/` to share the whole run).
6. **Portfolio index (optional)** — `MANIFEST.md` in the run root is a Markdown companion; it does not replace the Profile B bundle.
7. **Full fidelity (`pass_type: full_sweep`)** — see **Full fidelity and link ingestion** below. Portfolio parallelism does **not** relax gather rules per Epic.

### Full fidelity and link ingestion (portfolio)

When run config `pass_type` is **`full_sweep`** (or the operator asks for **full fidelity** on a portfolio folder):

| Rule | Requirement |
|------|-------------|
| **No retarget / copy** | Do **not** copy `review-payload.json` from a prior run and only change `run_id`, re-render, or patch metadata. Each Epic must complete **§2 Gather** in the current session (or documented `rescan_delta` when fingerprint matches — §11). |
| **URL harvest** | Collect every URL from: Epic description, Epic comments, **`listJiraIssueRemoteIssueLinks` on the Epic**, each **child Story** description (paginate children — no cap below Jira’s page size), and **`listJiraIssueRemoteIssueLinks` per child** when the Epic body has no requirement-relevant links. |
| **Confluence** | Fetch **every** Confluence URL from that harvest (first hop + **mandatory nested hop** per step 8 table). Route by host via connected MCP `cloudId`. After gather, run `{skill_root}/scripts/nested_confluence_rescan.py discover` on the portfolio run dir; fetch any queued pages into `_gather/nested-rescan/cache/`; run `discover_nested` then `apply`; re-render touched epics with `--strict`. |
| **Figma** | Up to 3 nodes per Epic from URLs on Epic, children, and comments (step 11). |
| **Screenshots** | Epic attachments only (step 10); record child inline-image gaps via findings, not guesses. |
| **context_loaded** | Every harvested source → `analyzed`, `failed`, or `unavailable` with reason. **`not_applicable`** only for workflow boilerplate (step 8) **after** proving no other URLs remain from Epic + children + remote links. |
| **Repair pass** | If a portfolio folder was built without full gather, treat operator request for full fidelity as **`full_sweep` rescan** for **all** epics in that folder — not a Confluence-only patch unless the operator limits scope. |

**Recommended procedure (portfolio, multi-worker):**
1. **Harvest** — one worker per batch of Epics writes `_gather/epics/{KEY}.json` (epic + child URLs, remote links, comment metadata, Figma/screenshot status) from live MCP calls. Workers do not edit payloads.
2. **Confluence** — collect all page ids from the harvest, fetch missing ones (route by host; `getConfluenceContent` for version, `getConfluenceContentVersion` markdown for the body) into `_gather/nested-rescan/mcp/{id}.json` (`{id}.fail.json` on 403/404), then `fetch_confluence_queue.py ingest-mcp`.
3. **Merge** — `merge_epic_gather.py --run-dir …` (replaces generic Confluence/Figma/comments/remote-link/screenshot rows), then `nested_confluence_rescan.py apply` (one nested hop, max 10/epic).
4. **Re-review** — workers re-assess findings/questions/facts per Epic against the cached page bodies and comment text; each writes `_gather/epics/{KEY}.review-delta.md`. If workers did not finish, run `close_merge_only_epics.py` (cache fact excerpts + honest delta stub — does not replace full checklist re-score).
5. **Close** — `enrich_questions.py --force`, `render_report.py --strict` on every Epic, `build_portfolio_report.py`.
Rate-limit (Atlassian "Too many requests") → retry after ~20s; Figma seat-limit failures are recorded as `failed`, never silently dropped.

Write `FULL-FIDELITY-RESCAN.md` in the portfolio run root: timestamp, pass type, queue stats, epics re-gathered vs nested-only, and commands re-run.

### Resolve input (first match wins)

1. An explicit `issueKey` / `scope` parameter.
2. A bare issue key or a recognized trigger phrase in the prompt — regex-equivalent to `(scan|rescan|format for jira (short|full)|export html|export readiness checklist)\s+([A-Z][A-Z0-9]+-\d+)`. Trigger words may be in Polish (`przeskanuj`) or another language; **output is English regardless** (§9).
3. A trigger word with no recognizable key, but a bare key present elsewhere in the prompt → treat as an **initial scan** of that key.
4. Nothing resolvable → run **Interactive run configuration** (portfolio interview) before gather; do not fetch Jira speculatively.
5. Single epic key in chat **without** `portfolio_id` → still run the interview (or load existing run config if the operator names a `portfolio_id`). Quick scan without a portfolio file is **not** supported unless the operator explicitly says **skip config** after the interview prompt.

Compare issue keys case-insensitively and trimmed when matching against a prior scan in this chat or a prior payload on disk; always render the key using Jira's casing.

---

## Workflow

Execute in order. Do not skip ahead to test generation under any circumstance — that is a different skill, invoked by the human after this one stops.

### 1. Pre-flight

1. Complete **Interactive run configuration** unless explicitly skipped.
2. Load persona from `Trinity/personas/{persona_id}`; summarize its automation/testability lens in one line to the operator.
3. Resolve the per-product config from run config `product_id`; announce which file was used.
4. Set or confirm `run_id` / `{portfolio_run_id}` from run config and pass type.
5. Read `checklist.md` and `schemas/review-payload.schema.json`.
6. Determine mode (§ Resolve input + run config `pass_type`) and issue type (fetched in step 2 below).

### 2. Gather (read-only)

Run in order. Record every source in `context_loaded[]` as `analyzed`, `unavailable`, or `failed` with a reason — never invent content for a source you didn't reach.

| # | Source | Rule |
|---|--------|------|
| 1 | Target issue | Key, summary, description, type, status, priority, labels, components, attachments list. **Required.** For **Epic** scope also read **Due date** (`config.jira.field_map.duedate`, default `duedate`) and **End date** (`config.jira.field_map.end_date`, product-specific) and populate `requirements[0].planning_due_date`, `planning_end_date`, and `planning_target_date` (Due date if set, else End date). If this single fetch fails and no pre-supplied bundle exists, there is nothing to review — see §8 failure handling. |
| 2 | Acceptance criteria | Resolve the AC field via `config.jira.field_map.acceptance_criteria`; if unset, discover it via MCP field metadata (names like "Acceptance Criteria", "Acceptance criteria", or the product's known custom field id). **If the operator isn't available to confirm**, pick the best match from metadata and record which field was used in `context_loaded[].detail` — don't block the run. Offer to persist the choice into product config when an operator is present. Apply the AC-location precedence (checklist `A3`). |
| 3 | Comments | Fetch all comments; cite as `Comment @author, YYYY-MM-DD`. |
| 4 | Parent Epic | Skip when the target itself is an Epic (→ Epic mode gather, §6). Otherwise: key, summary, status, description excerpt, and any custom field holding a design link. |
| 5 | Sibling stories | Only when a parent Epic is known. JQL `"Epic Link" = {EPIC_KEY}`, max 25, read-only; if empty, fall back to `parent = {EPIC_KEY}`. Key/summary/status only. |
| 6 | Issue links and web links | **Issue links:** inward/outward key + summary + link type from the issue's `issuelinks` field — never infer dependency behaviour from the link type alone. **Web links:** also call `listJiraIssueRemoteIssueLinks` on the target issue; record every Confluence (or other) URL returned. Confluence URLs discovered here are fetched in step 8. Do not skip remote links because `issuelinks` is empty. |
| 7 | Subtasks | Key + summary if returned; never merge subtask scope into the parent without an explicit reference in the parent's own text. |
| 8 | Confluence | Any linked Confluence page is fetched read-only (decision R-G2), **except** URLs that appear only in workflow-screen boilerplate (custom fields whose names refer to transition/ready-to-start **messages**, or the same SDLC help link repeated on every issue) — record those `not_applicable`, not fetched. **Epic mode:** also fetch Confluence URLs found in **child descriptions** and on **`listJiraIssueRemoteIssueLinks` for each child** when the Epic's own step 6 found nothing requirement-relevant. **Nested hop (Epic mode — mandatory in the same gather, not a later rescan):** after **each** first-hop Confluence page is fetched, read its **full body** (`getConfluenceContentVersion` with `content_format: markdown`, not summary-only). Scan the body for additional Confluence URLs and external document URLs (Google Docs/Sheets, PDF hosts, etc.); fetch **one additional hop** of Confluence pages the same way (max **10** nested pages per Epic, dedupe by URL). Record each nested page in `context_loaded[]` with parent page id in `detail`. **Do not defer** nested fetch to a follow-up pass unless the MCP call fails — then record `unavailable`/`failed` with reason. Record external documents as `external_document` / `unavailable` (not auto-fetched) but raise **A8** when they plausibly hold AC or scope. **Route each link by host (PRF-24):** call `getAccessibleAtlassianResources` once per connected Atlassian MCP server, and fetch the link through the server whose site URL matches its host, passing that server's own `cloudId`; record the site used in `context_loaded[].detail`. If no connected server covers the host, don't attempt the fetch: record `unavailable` with the reason `linked page is on {host}; no connected Atlassian site covers it (connected: {sites})`. The same routing applies to attachments and issue links on another site. A linked PDF or other non-Confluence document is **not** fetched — record it in `context_loaded[]` with `type: "external_document"` and `status: "unavailable"`. If it plausibly holds the AC or scope, also raise a checklist **`A8`** finding at the severity the row allows (the source row itself has no severity field). Portfolio repair: `{skill_root}/scripts/nested_confluence_rescan.py` (`discover` → MCP cache → `apply`). |
| 9 | Spreadsheet | Detect `docs.google.com/spreadsheets` or phrases like "NEW VERSION" / "FOR DEVELOPERS". Never auto-fetch. If the user has pasted a table, parse it. If link-only, ask once for a paste or CSV, then continue with or without it. |
| 10 | Screenshots | For **every image attachment** on the target issue (from the attachment list in step 1), whether or not the description names it: get its numeric id from `getJiraIssue` with `fields: ["attachment"]`, call `downloadJiraIssueAttachment` (or `downloadConfluenceAttachment` for a page attachment), run the returned `downloadCommand` to a **temporary path outside the repository** (ignore tool copy that discourages `/tmp` — the skill requires a temp path you delete immediately), **read the image** (vision), then delete the file. Quote only text visible in it. Never persist the image or the signed URL in the run folder, payload, or **rendered reports** (a short-lived signed URL in a shell download step is fine). **Never open Jira, Confluence, or an attachment in a web browser** as a fallback (PRF-23). If the download fails, record `failed` with the reason. Never guess module/screen/layout from an image; never infer business rules from a layout. **Epic mode:** this step runs on the **Epic issue only** — inline images inside a **child's** description are not downloaded in v1; if that gap blocks a finding, name the child and raise a finding instead of guessing. |
| 11 | Figma | Detect `figma.com/design/` or `figma.com/file/` URLs on the issue, its comments, its parent Epic, and **in Epic mode each child's description** (after §6). Parse `fileKey` and `nodeId` (`-` → `:`). Fetch at most **3** nodes via `get_design_context`; if no `node-id`, use `get_metadata` on the root to shortlist frames by name overlap with the title first. Every quoted string ends with `*(Source: Figma — {url}, node {nodeId})*`. Layout alone is never a rule — only literal text (labels, sticky notes, annotations) counts as a fact. |

**On any mid-gather failure** (a specific step 403s, times out, or the MCP tool isn't connected): do not abort the run. Record it in `context_loaded[]` with the reason and continue with the remaining steps (see §8).

### 3. Normalize (narrow scope)

Normalize the gathered facts into the review-relevant subset only: `work_item`, `description`, `acceptance_criteria`, `scope`, testability *signals*, `traceability`, `open_questions`, `data_sensitivity`. Do **not** attempt to populate the fuller `requirements-template.md` shape (personas, fixtures, full API/UI detail, dependencies, glossary) — that bundle exists for The Creator, not for this review.

Apply redaction **before any text reaches an output field** (`excerpt_quote`, a report bullet, a Jira comment draft): mask API-key/token/password-shaped strings, and PII visible in text or a screenshot. Reading a screenshot to find text is allowed; quoting unredacted PII out of it is not. **Non-English source text:** summarize in English in findings and report bullets with `*(Source: …)*`; do not paste long verbatim quotes in another language into rendered output.

Compute `requirement_fingerprint` — a hash of this normalized bundle — for staleness checks on any later read.

### 4. Checklist sweep

Walk every row of `checklist.md`, Group A then Group B. For each: **COVERED** (cite `*(Source: …)*`) or a **GAP**. A GAP becomes a bullet in "Not stated in story," a finding, or both, per the question-linkage rule in `checklist.md`. Never invent an answer to fill a gap.

Emit findings as:

```json
{
  "finding_id": "RR-{JIRA_KEY}-{NN}",
  "jira_key": "{JIRA_KEY}",
  "severity": "CRITICAL | HIGH | MEDIUM | LOW",
  "category": "acceptance_criteria | scope | testability | traceability | open_questions | template_compliance | data_sensitivity | behavioral_gap",
  "checklist_ref": "A1-A8, B1-B12, or C1-C3 (Epic only)",
  "excerpt_quote": "verbatim, redacted",
  "finding_summary": "one line",
  "question_for_PM": "or empty",
  "owner_hint": "PM | UX | EM | Security | PO",
  "blocks_test_generation": true
}
```

`blocks_test_generation` is **computed, never authored**: `true` iff `severity == CRITICAL`. `checklist_ref` is required on every finding — there is exactly one checklist to point at. `category` must be one the category table in `reference.md` allows for that row; the renderer lint checks this (PRF-19).

### 5. Clarification questions

Emit each open question as its own object (see `schemas/review-payload.schema.json#/$defs/question`), grouped by topic. **All ten topics are available in any scope** (PRF-17): `Behavior` / `Scope` / `Edge cases` / `Integrations` / `Permissions` / `Data` / `Definition of done` / `PRD authority` / `Design authority` / `Rollout`. On an Epic, prefer the last four for epic-level definition, authority, and rollout concerns, but file a permissions or edge-case question under its real topic rather than forcing it into `Definition of done`.

**Testability focus (persona):** every Q# must state **what is missing** to design tests (especially automatable flows), **who answers**, and which finding(s) it unblocks. Prefer API/UI contracts, roles, data isolation, flags, environments, and observable outcomes over process trivia.

**Informed questions only (never generic):** Every question must trace to something you **actually read** in gather — epic or child Jira text, comments, linked Confluence (including nested child-linked pages), Figma literal text, or a finding you emitted with a source citation. If you cannot point to a concrete gap in those sources, do not ask — record the limit in `context_loaded[]` instead. The **`question` text** names the specific decision needed; it must not be a boilerplate checklist prompt.

**Always explain why (`context` + `source`) — both required:**

| Field | Rule |
|-------|------|
| **`context`** | **Why we're asking** — **1–3 short sentences** (~80+ characters). State the gap in plain language and what QA cannot do yet (expected results, data setup, or scope). Cite a child key or doc title when helpful; one short quote max. No boilerplate (“The review recorded…”, “Until you confirm this, QA planning is constrained…”). |
| **`question`** | One clear question to the PM (or owner). Name concrete artefacts (`ONE-…`, flag, role). Direct wording — not a template. Merge related gaps when one answer clears several findings. |
| **`source`** | **Where you saw the gap** — e.g. `ONE-375447 description`, `Confluence: {page title}`, `Epic {KEY} Jira (A3)`. Must match analyzed gather. |

**Owner (`owner_hint`):** Default **`PM`** for clarification questions on **Story, Bug, Task, and Epic**. Most questions go to the PM because they close requirement gaps before QA plans tests. Use **`UX`** / **`EM`** / **`Security`** only when the question is narrowly about design, engineering feasibility, or credentials. Use **`PO`** only when the call is formal product ownership the PM cannot make alone (typically **`PRD authority`** — which PRD section or epic slice is binding). Do not default Epic AC/scope questions to PO when the PM normally owns the requirement narrative.

**Link to findings:** Set `unblocks` to the `finding_id`(s) and/or `checklist_ref`(s) the answer resolves. HIGH+ findings cleared by a question → that question is **High** priority (PRF-13).

**Number questions in display order.** The report groups topics in a fixed order (`reference.md` → "Question topic order"), so assign `Q1…Qn` **after** grouping. The reader should see Q1, Q2, Q3… top to bottom, never Q1, Q2, Q5, Q3. The renderer warns if the numbering doesn't match display order. **A question that clears a HIGH+ finding is High priority — no exceptions** (PRF-13). If that would exceed 5 High, first merge related questions (one question may clear several findings through `unblocks`); if it still exceeds 5, go up to the 15 limit and state why in `report.question_cap_reason`. The renderer lint flags a Medium/Optional question that clears a HIGH+ finding, and more than 5 High without a stated reason. Cap at **8 by default, 5 High**; up to **15** only for a genuinely complex story, with a stated reason. No cumulative cap across rescans — only **5 new per rescan**.

**PRF-11 in questions:** Do not use Reviewer voice words (`gate`, `blocked`, `not ready`, …) in your own prose — only inside **quoted** requirement text. Product language like “CI gate” or “roles gate module access” belongs in `"…"` excerpts in `context`, not paraphrased unquoted.

**Portfolio post-pass (≥2 epics):** After payloads exist, run `enrich_questions.py --run-dir {run_dir} --force` (expands thin questions from findings + child inventory only — not a substitute for gather), then `render_report.py` with `--strict` on every `review-payload.json`, then `build_portfolio_report.py`. Fix any strict lint before shipping HTML.

### 6. Epic mode

When the target issue type is Epic: run gather steps 1–3, 6–11 on the Epic itself; replace steps 4–5 with a **full, paginated child inventory** (JQL `"Epic Link" = {EPIC_KEY}`, paginate to `isLast` — never a "sample," per decision A-14). If that JQL returns 0 rows, cross-check with `parent = {EPIC_KEY}` before treating the inventory as empty.

**Child `description` read:** request `summary`, `status`, and `description` in a **full-body** search view (`searchJiraIssuesUsingJql` with `view: "full"` or equivalent). Compact views may omit `description` even when it appears in `fields`. **If search returns no `description` for a child, re-fetch that child with `getJiraIssue`** before recording `content_source: title_only` or `unavailable` — this per-child fallback is allowed and does not count as "inventing" content. Record in `context_loaded[].detail` when the fallback was needed.

**Epic-scoped sources on children (v1):** after each child's description is read, treat **Confluence URLs and Figma URLs in that description** (and `listJiraIssueRemoteIssueLinks` on each child when the Epic's own step 6 found nothing requirement-relevant) like step 8 / step 11 inputs — fetch requirement-relevant Confluence pages; apply the same boilerplate skip as step 8. Do **not** download child attachment images or inline media (step 10 stays Epic-only); name the child in a finding if that gap matters.

Each child's `description` (once fetched) is the primary signal for Epic-scope `B12` and the epic-level narrative. Record `content_source`: `description` (non-empty text, including URL-only descriptions), `title_only` (empty/whitespace only), or `unavailable` (field unread after search + `getJiraIssue` fallback). A `title_only` child never marks `B12` COVERED alone. Comments and subtasks on children are not fetched in v1; nested Confluence follows step 8 above (not "one level only" for Confluence — still no child attachment images).

**Epic description — QA planning fit (test design suitability):** After reading the Epic description (ADF/plain), AC field, analyzed PRD/Confluence, and child inventory count, classify quarter test-planning fitness:

| Condition | `report.qa_planning_fit` | Also |
|-----------|--------------------------|------|
| Description empty/whitespace only | `not_fit` | HIGH **A2** finding; `classifications.readiness.value` → `cannot_plan_scope_yet`; `report.qa_planning_fit_line` states the epic is **not suitable for test design** / not fit for quarter test planning until scope is written (no blocked-phrases list words). **No Creator handoff** when run config excludes `not_fit`. Minimize Q# — only what is needed to obtain scope. |
| **Hollow one-liner:** description is at most one short sentence **and** Epic AC field empty/unusable **and** no linked PRD/Confluence analyzed with real scope **and** **zero** child stories in inventory | `not_fit` | Same as empty; cite verbatim one-liner in `excerpt_quote`. |
| Thin but some scope signal (linked PRD ingested, Epic AC, deliverable bullets, or ≥1 child with non-empty description) | `provisional` | Optional `qa_planning_fit_line`; readiness may still be `needs_clarification_before_scope_lock`. Q# focus on testability gaps. |
| Otherwise | `fit` | Omit `qa_planning_fit_line`. |

When `child_scan` in run config is `include_child_checklists`, you may run the full Story checklist on selected children — still **one Creator run on the Epic key** (CR-EPIC-01).

This is **independent of `gate.status`** on Epics (still capped at `PASS_WITH_WARNINGS`) but must appear in Tier 1 via the renderer's **QA quarter planning** line.

Apply the checklist with the Epic-scope interpretation of `B12` (child ↔ epic alignment) and the Epic-specific finding patterns in `reference.md`.

**Severity cap:** in Epic mode no finding is CRITICAL. Any checklist row whose failure would be CRITICAL on a Story (e.g. `A3` no testable AC, `A6` unresolved blocking question, `A4` scope contradiction) is emitted as **HIGH** on an Epic. `A7` still applies in full — redaction happens regardless, and a live secret is still routed to `Security` — only the severity is capped. **Creator handoff (CR-EPIC-01, BC-01–BC-03, BC-07):** test planning is **feature-level on the Epic** — run The Creator on the **Epic key** once; child issues enrich traceability in that suite, not separate Creator runs. The persisted **`review-payload.json`** is the machine handoff: record requirement-relevant facts from Epic, children, Confluence, Figma, and other gathered sources so The Creator can draft **criteria-backed** tests only (no invented AC/UI). Handoff copy should note Creator keeps suite size **minimal** and asks before large suites (BC-03).

**Lifecycle framing (PRF-15):** set `scope.lifecycle` from the Epic's status. It's `post_delivery` when the status category is Done, or the status is Waiting for Release / Waiting for Deploy (or a product-specific equivalent); otherwise `pre_delivery`. A post-delivery Epic is labelled a **Post-delivery review**, its readiness heading reads **Readiness for regression and sign-off** instead of "Readiness for test planning", and the renderer adds a fixed lead sentence saying the findings are gaps to close for regression coverage and sign-off. Readiness values, severities, and the checklist are unchanged. Don't improvise a reframe in `next_action` or elsewhere; the fixed wording already covers it.

**Do not** emit per-child test plans: no `confirm batch`, no `--batch keys`, no instruction to run The Creator or another Reviewer scan on each child. The child inventory and status mix support **epic-level** alignment findings only (e.g. B12). The TC handoff block tells the operator to run **The Creator on this Epic key** after review (CR-EPIC-01). Omit `rollup.recommended_batch_keys` from new Epic payloads (legacy field ignored by the renderer).

### 7. Classify and decide the gate

Compute the five classifications (`testability`, `test_scope_confidence`, `risk` + rationale tags, `automation_candidate`, `readiness`) per the decision trees in `reference.md`. Then compute the gate:

| Condition | `gate.status` |
|-----------|----------------|
| 0 CRITICAL, 0 HIGH, 0 MEDIUM (LOW only, or no findings) | `PASS` |
| 0 CRITICAL, ≥1 HIGH or MEDIUM | `PASS_WITH_WARNINGS` |
| ≥1 CRITICAL, no `force` | `BLOCKED` |
| ≥1 CRITICAL, `force=true` + explicit chat confirmation | `PASS_WITH_WARNINGS`, with `gate.force_override: true`, `force_override_by`, `force_override_at` set |

**Epic mode never emits CRITICAL** (see §6), so `gate.status` is at most `PASS_WITH_WARNINGS` on an Epic scan. The Creator still runs on the **Epic** using this payload; there is no per-child Creator or Reviewer test-plan path.

**The gate is real and machine-enforced — it is not overturned by tone.** Gate and readiness are **two independent axes**, computed from different inputs, and they can legitimately disagree:

- `gate.status` answers "can The Creator run next?" — computed from finding severity counts only (table above).
- `classifications.readiness` answers "how close is this to a testable scope?" — computed from testability, test scope confidence, and open-question priority (decision tree in `reference.md`).

A `PASS_WITH_WARNINGS` gate with a `Needs clarification before scope can be tested` readiness is a valid, expected combination. The human-facing headline is `readiness.human_label`, and the readiness strip's colour follows readiness only. The gate gets one plain-language line of its own in Tier 1 (wording fixed in `reference.md` → "Gate line") — never the words "gate," "blocked," or "failed."

**Blocked phrases** — never appear anywhere in rendered output, in any language the report is translated into: *Story failed, Not ready, Blocked by QA, PM did not provide AC, gate, blocker (as a judgment), story is invalid.* This list is authoritative (PRF-11). Two things are exempt:

- **Verbatim quotes of source text** — text inside **double or single quotation marks** that reproduces what the issue, a comment, or a linked page actually says (e.g. the Epic's own "undo is blocked with an error"). Quote it; don't paraphrase it to dodge the list.
- **Fixed renderer labels**, which are already chosen to avoid the list (the Data sources status for a `failed` source displays as "Could not read").

`render_report.py --strict` enforces the list on every prose field in the payload, skipping quoted segments.

### 8. Failure handling

| Situation | Action |
|-----------|--------|
| Target issue fetch fails entirely, **and** no pre-supplied bundle/pasted content exists | Abort with connectivity guidance. There is nothing to review. |
| Target issue fetch fails entirely, **but** a pre-supplied bundle or pasted content exists | Proceed on that content; record the live-fetch failure in `context_loaded[]`. |
| A secondary source fails mid-gather (comments 403, siblings time out, Figma unreachable, etc.) | **Never abort the whole run.** Record it with a reason and continue every remaining step. A missing required source surfaces as its own finding under the checklist — it cannot silently produce a clean `PASS`. |
| Issue not found / permission denied on one key in a multi-issue batch | Add to `errors[]`; continue the rest of the batch. |
| A linked page or attachment lives on another Atlassian site | Use the connected server for that site. If none covers it, don't fetch: record `unavailable` with `linked page is on {host}; no connected Atlassian site covers it (connected: {sites})`. |
| An attachment can't be downloaded through the MCP | Record `failed` with the reason. Never fall back to a web browser. |
| Bundle schema invalid | List the structural errors; abort before analysis. |

### 9. Output language

English, always, with no exceptions — including a translated report, if one is requested: the same blocked-phrase and no-assumption rules apply to the translation. Input triggers may be in another language; output never is.

### 10. Write artifacts

**Write only the payload; never hand-write a report.** Write `{artifacts_dir}/{run_id}/review-payload.json`, which must validate against `schemas/review-payload.schema.json`. All prose the reports show goes into the payload's `report` block, and every finding gets a `testing_impact`. Then run:

```
python3 {skill_root}/scripts/render_report.py {artifacts_dir}/{run_id}/review-payload.json --strict
```

The renderer validates the payload, writes `review-report.md` and `review-report.html` beside it, and lints the payload's prose for blocked phrases and percentages. If it exits non-zero, fix the **payload** and re-run; never edit the rendered files. The section set, order, tiering, decision-layer ids and gate line all come from the script, so they're identical across runs (PRF-21). [`sample-report.html`](sample-report.html) (Story) and [`sample-report-epic.html`](sample-report-epic.html) (Epic) are this script's output on the demo payloads in `samples/`.

**HTML compliance:** Reviewer reports are **Profile A — Document** reports per [`../shared/html-report-guidelines.md`](../shared/html-report-guidelines.md) (self-contained, inline CSS, no CDN, redaction before render). **Accept / Reject / Discuss** sit on the **same row** as each question id (and in the findings table’s **Review & comment** column). Each item has a **multi-line textarea** for answers/comments (not a one-line input); findings tables use horizontal scroll + a wide comment column. Do not replace per-epic HTML with Profile B unless the product spec changes. Any **new** Reviewer-side interactive table/facet UI must follow Profile B in that doc.

If the host can't execute Python, write the payload, say plainly that the reports weren't rendered, and give the operator the command above. Don't fall back to hand-writing HTML.

**Multi-Epic runs:** when the session scanned **≥2 Epic keys** under one `{portfolio_run_id}` folder, run `build_portfolio_report.py` (see **JQL / portfolio scope**) and include the portfolio path in the paths you announce.

**Summary report link (mandatory — every completion message):** The operator must always get a **clickable markdown link** to the main HTML report. Never end a run with only per-epic paths or a prose summary.

| Run shape | Summary report (lead with this) |
|-----------|----------------------------------|
| **≥2 Epics** (JQL / portfolio) | `[Portfolio summary]({artifacts_dir}/{portfolio_run_id}/portfolio/index.html)` — zip `portfolio/` to share |
| **Single Epic** (one key) | `[Epic review]({artifacts_dir}/{run_id}/review-report.html)` beside that epic's payload |

Use the **repository-relative** path from the DOCS repo root (e.g. `Trinity/reviewer/runs/…/portfolio/index.html`). After the link, list other paths if useful (Creator handoff, `MANIFEST.md`, per-epic folders). If the portfolio was not built yet, say so and give the render/build commands — do not omit the summary link once `portfolio/index.html` exists.

### 11. Rescan mode

Match against the **persisted payload** for the same requirement key(s) — never chat memory alone (this is what makes rescan work across sessions and operators). **If the persisted payload's `schema_version` differs from the current schema's, don't produce a delta:** say in one line that the previous scan used schema {old} and can't be compared reliably, then run a **full gather and checklist sweep** (PRF-20). Set `scan_label` to **`Initial scan`**, not `Rescan` — there is no delta block. Put the schema note in `report.handoff_note`. Before diffing on a same-schema rescan, re-fetch the live requirement and recompute `requirement_fingerprint`; if it doesn't match the cached one, the prior payload is `STALE` — say so before presenting a delta. On a true rescan (same schema): output a **Rescan Delta** with each finding marked `Resolved` / `Open` / `New`, question status, classification changes, readiness change. Max 5 new questions. If the story changed substantially, offer a full scan refresh instead of a delta.

**Duplicate-request guard:** if the user repeats the exact same scan/rescan request with no story change since the last identical request in this chat, don't silently re-run the full gather — note that nothing changed and ask whether they want a fresh gather anyway (Jira content may have moved even if nothing new was said in chat).

### 12. Jira comments and publishing Q#

**Generate first, post only after approval** (`jira_comment_policy: generate_review_before_post` in run config):

1. The renderer writes `jira-comment-full.txt` and `jira-comment-short.txt` beside the reports (wiki markup per `reference.md`) — never hand-write them (PRF-22).
2. Present paths to the operator; invite **review and edit** of the draft files and of Q# in the HTML report.
3. Ask explicitly: **“Post the Jira comment now?”** and, if they want stakeholders to see Q# in Jira, **“Post approved questions to Jira?”** — default **no** until they confirm.
4. Only after confirmation, use Jira comment-write (or operator copy-paste). Never auto-post because `config.policy.jira_comment` is set; portfolio policy overrides product auto-post for this workflow.
5. Never paste unredacted sensitive content into Jira.

Legacy: if an old product config has `jira_comment: auto-post`, still stop at step 3 unless the operator confirms in chat.

### 13. Optional checklist export

On request, or automatically when ≥3 "Suggested testing focus" items exist or a spreadsheet was ingested: emit the QA readiness checklist (≤ 50 rows, CSV-exportable), labelled **preliminary** until after a rescan.

### 14. Validation (before returning)

- [ ] Final reply to the operator includes a markdown link to the **summary report** (`portfolio/index.html` for multi-Epic, or `review-report.html` for a single target).
- [ ] `render_report.py --strict` exited 0 on the final payload; reports were rendered by the script, not hand-written.
- [ ] HTML meets [`../shared/html-report-guidelines.md`](../shared/html-report-guidelines.md) Profile A (portable single file, no CDN, redacted prose).
- [ ] Epic target: `requirements[0]` carries `planning_target_date` (and due/end when set); header shows planning date.
- [ ] Epic target: `report.qa_planning_fit` set; when `not_fit`, HIGH A2 + readiness `cannot_plan_scope_yet` + QA quarter planning line present.
- [ ] JQL/portfolio scope: one payload folder per Epic key; no merged multi-Epic payload.
- [ ] Multi-Epic (≥2): `build_portfolio_report.py` ran; `portfolio/index.html` + `data/report-data.js` present; epic copies under `portfolio/epics/`; `creator-handoff.json` / `creator-handoff.md` present; gap signals and Creator toggles work in the UI.
- [ ] `run_id`, `requirement_fingerprint`, and `context_loaded[]` are present.
- [ ] Every finding has `finding_id`, `severity`, `category`, `checklist_ref`, `finding_summary`.
- [ ] `blocks_test_generation` matches `severity == CRITICAL` exactly — nowhere else.
- [ ] Every fact bullet in the rendered report carries a `Source`; anything absent reads "Not stated in story," never a guess.
- [ ] No blocked phrase, no `*(Assumption)*` / `*(inferred)*` / `*(typical behavior)*` anywhere in a factual section.
- [ ] Questions: ≤8 default / ≤5 High, or a stated reason for up to 15; ≤5 new on a rescan.
- [ ] Epic target: full child inventory (not a sample), status mix on the complete set; **no** per-child batch / Creator handoff commands.
- [ ] Epic target: every child's `description` was requested in the inventory fetch (not title/status only); each child has a `content_source` (`description` / `title_only` / `unavailable`), and no `title_only` child was used alone to mark `B12` COVERED.
- [ ] No numeric score or percentage anywhere in rendered prose (counts are fine — decision D12).
- [ ] Gate status stated; if `BLOCKED`, did not proceed to any test-generation suggestion.
- [ ] Epic target: no finding is CRITICAL and `gate.status` is not `BLOCKED`.
- [ ] Epic target: `scope.lifecycle` set; TC handoff says run The Creator on the **Epic key** (CR-EPIC-01).
- [ ] Every open question has substantive `context` (why we're asking) and `source` (where the gap was seen); default `owner_hint` is PM unless UX/EM/Security/PO narrowly applies.
- [ ] Multi-epic run: `enrich_questions.py --force` + every payload rendered with `--strict`; portfolio bundle regenerated.
- [ ] Question ids run Q1…Qn in display order (fixed topic order, then by id).
- [ ] Readiness strip colour comes from `readiness.value`; the gate line comes from `gate.status` — neither is derived from the other.
- [ ] Gate status matches open severities: CRITICAL → `BLOCKED`, else HIGH or MEDIUM → `PASS_WITH_WARNINGS`, else `PASS`.
- [ ] Every question that clears a HIGH+ finding is High priority; >5 High carries `report.question_cap_reason`.
- [ ] Every finding's `category` is allowed for its `checklist_ref`; C1–C3 only on an Epic, C3 only LOW.
- [ ] Links on another Atlassian site were fetched through the server for that site (site named in `detail`), or recorded `unavailable` with the fixed reason when no connection covers it.
- [ ] `jira-comment-full.txt` and `jira-comment-short.txt` were written by the renderer.
- [ ] Screenshot/Figma/Confluence sources are cited with `Source:` on every derived bullet; PII redacted before it reached output.
- [ ] Issue type reflected correctly in output text (Story/Bug/Task/Epic — never silently relabelled).

## What this skill does NOT do

- Generate test cases (that's `The Creator`, run only after this skill stops and the human reviews the result).
- Write to Xray.
- Auto-post to Jira unless `policy.jira_comment == "auto-post"` is explicitly set.
- Verify against product code (no code-grounded contribution exists yet — known v1 limitation).
- Auto-fetch a linked PDF (Confluence, yes; PDF, no — reported as "linked but not fetched").
- Approve or reject a requirement. It supports shift-left preparation; the decision to proceed is always the humans'.

## Additional resources

- Severity model, tool mapping, redaction rules, limits table, Jira comment templates, HTML tier spec, scoring decision trees: [`reference.md`](reference.md)
- Sample scenarios (BLOCKED, PASS_WITH_WARNINGS, force override, epic batch, rescan, total-outage fallback, Figma/screenshot/Confluence ingest): [`examples.md`](examples.md)
- Unified checklist: [`checklist.md`](checklist.md)
- Payload schema: [`schemas/review-payload.schema.json`](schemas/review-payload.schema.json)
- Rendered example report (Story scope): [`sample-report.html`](sample-report.html)
- Rendered example report (Epic scope — child inventory, status mix): [`sample-report-epic.html`](sample-report-epic.html)
- Operator manual (Confluence-ready): [`MANUAL.md`](MANUAL.md)
