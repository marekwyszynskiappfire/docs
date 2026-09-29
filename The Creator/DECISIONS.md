# The Reviewer & The Creator — decision memory

Durable record of decisions made while planning the two super skills. Append to this file; do not rewrite history. When a decision changes, add a new entry and mark the old one superseded rather than deleting it.

**Project:** consolidate requirement-review and Xray test-scenario-creation skills into two product-agnostic super skills — **The Reviewer** and **The Creator** — each producing an interactive report used to review and correct output before submission to Xray.

**Plan document:** [working-plan.md](working-plan.md)

---

## Locked decisions

Confirmed by the user on 2026-09-25 and treated as fixed. Anything contradicting these needs an explicit new entry below.

| # | Decision | Choice | Rationale |
|---|---|---|---|
| D1 | Report format | Self-contained single-file HTML is **required**; Cursor Canvas optional only | A Canvas is a `.canvas.tsx` compiled solely by the Cursor IDE, confined to a Cursor-managed directory, importing from a Cursor-private module. It cannot render on Claude or in a browser. HTML opens anywhere, including for stakeholders with no AI tooling. |
| D2 | Host support | Must run on **Cursor and Claude** (Code and desktop). **Amended 2026-09-28:** Hive MCP confirmed in production use and added as a third fully-supported host — see D13 confirmation below. | Nothing host-specific in the critical path. |
| D3 | Edit loop | Report exports a **corrected JSON payload**; operator hands that file back to the agent | Accepted tradeoff: a `file://` page cannot write to disk, so the round-trip needs a download step. Avoids requiring a local server. |
| D4 | Xray writes | **The Creator submits**, only after explicit human approval, via **Xray MCP** with `xray_graphql_import.py` as fallback | Keeps the approval gate inside the skill rather than a separate hand-off. |
| D5 | Personas in scope | QA engineer, QA lead/manager, product manager/BA, automation engineer | Developer and engineering-leadership personas explicitly excluded from v1. |
| D6 | Portability | Product-agnostic skills plus a **per-product config file** | Teams must not fork or edit skill bodies. |
| D7 | Repo home | **`The Reviewer/`** (sibling folder next to the DOCS repo) and **`The Creator/`** (under DOCS) supersede the old skills; old ones archived | **Amended 2026-09-29:** The Reviewer shipped as `../The Reviewer` with its own git remote; not nested under `The Creator/Output/`. |
| D8 | Review gate | CRITICAL findings **keep hard-blocking** The Creator, with explicit `force` override | Preserves existing gate semantics. |
| D9 | Source material | **Only** the skills in `The Creator/Input/` are inputs to the consolidation | See correction C1. |

---

## Architectural decisions

| # | Decision | Rationale |
|---|---|---|
| A1 | Skills produce a **schema-valid JSON payload**; a separate script renders the report | Deterministic output across hosts, zero token cost, unit-testable, and the agent cannot drop a test while "summarising" into a document. |
| A2 | Renderer is `shared/render_report.py`, **Python 3 stdlib only** | Runs on any host with no install step. |
| A3 | Three payload contracts: `ReviewPayload`, `SuitePayload`, `ImportPayload`, each with `payload_version` | Renderer refuses unknown major versions with a clear message. |
| A4 | Per-test `decision` object lives **inside** the test in `SuitePayload` | One file round-trips; nothing has to be re-joined by id. |
| A5 | Coverage, traceability, and tier math are **always recomputed by the agent** on ingest, never trusted from the browser | Report editing is bounded so the report does not become a second authoring surface. |
| A6 | Export blocked while any test decision is `pending` | An unreviewed suite cannot reach Xray by accident. |
| A7 | The Creator has three explicit modes: `generate`, `dry-run`, `submit` — never implicitly chained | `submit` additionally requires a completed dry-run in the same session plus a chat confirmation. |
| A8 | Skills name **logical capabilities**, mapped to concrete MCP tools in a capability table | A missing capability degrades with a stated warning instead of aborting. |
| A9 | Config resolution order: session parameter → `config/<product>.json` → `config/default.json` → documented built-in defaults | Skill announces the resolved config at run start. |
| A10 | One report shell with a persona selector presetting filters and section visibility | Four entry points, one file, no persona-specific builds. |

---

## Corrections and superseded assumptions

### C1 — Source skills come from `The Creator/Input/`, not `AI in QA/Skills/`

**Date:** 2026-09-28 · **Supersedes:** an unstated assumption in the first draft of `working-plan.md`.

The initial plan was written after reading `AI in QA/Skills/requirements-review/` and `AI in QA/Skills/test-case-creation/`, and assumed those were the skills being consolidated. **They are not.** The authoritative inputs are whatever skills are placed in `The Creator/Input/`.

Consequences:

- Phase 1 must begin by inventorying `The Creator/Input/` and building the rule-by-rule port checklist from **those** files.
- Any specific claim in `working-plan.md` about existing behaviour — the `CAT-*` coverage model, P0–P3 tiers, the 15-step cap, `test_data_required` / `test_data_prerequisites`, the `{JIRA-KEY} - testcase-draft.md` output shape, the `artifacts/{run_id}/` convention — is **unverified** against the real inputs and must be re-checked, not assumed.
- References to `AI in QA/Skills/*` paths in the plan are illustrative background only. They are not the migration source and the folders there should not be archived or moved on the basis of this plan.
- The `ONE-232514` artifact named as a Phase 1/2 conversion fixture may not be relevant; pick fixtures from the real inputs instead.

**Status update 2026-09-28:** Marek's contribution is now in place at `The Creator/Input/Marek/` — the `requirements-review` and `test-case-creation` skill folders plus a `_shared/` copy of every asset they depend on (review checklist, findings schema, `TestCaseDraft.schema.json`, `golden/v1`, `requirements-template.md`, Jira/Xray mapping config, the GraphQL import script, and the prior Agent Skills Specification). Copied, not moved — the originals under `AI in QA/Skills/` are untouched.

This means the two skills I originally read *are* among the inputs after all, but only as **one contributor's** submission under `Input/Marek/`. Other contributors may add folders alongside it, so the plan's correction still stands: the inventory covers all of `Input/`, no single contribution is privileged, and conflicts between contributions are a first-class output of the Phase 1 checklist.

**Still pending:** whether other contributors are adding skills. Until that is known, the inventory should not be treated as complete.

### C2 — Contributions conflict on test representation and on who writes to Xray

**Date:** 2026-09-28 · **Affects:** D4, and the `SuitePayload` contract (A3)

Kacper's `TestCaseWriting` differs from Marek's skills in ways that cannot be resolved by merging text, so Phase 1 must decide them explicitly rather than let the first-read skill win:

1. **Test representation.** Kacper's output is Xray CSV with exactly three columns (`Action`, `Data`, `Expected Result`) plus a separate plain-text Jira Description block for preconditions. Marek's is a `TestCaseDraft` JSON batch with objectives, tiers, roles, and structured traceability. The merged `SuitePayload` must be a superset that can render to either, and the CSV constraint — every step runnable from its own `Data` cell, no `see Description` — is a real rule, not a formatting preference.
2. **Who writes to Xray.** Kacper's skill explicitly blocks auto-create and auto-import and forbids claiming tests were saved. Decision D4 has The Creator submitting after approval. Both can coexist only if submission is opt-in per product config, defaulting to off.
3. **Quality model.** Kacper uses a binary `Final draft` / `Preliminary draft` status keyed on code verification; Marek uses P0–P3 execution tiers and `CAT-*` catalog coverage. These measure different things and probably both belong in the payload.
4. **Grounding source.** Kacper's authority order puts **current product code and live UI** above repo examples, and requires code grounding before a `Final draft`. Marek's skills have no code-reading step. A product-agnostic skill needs code grounding to be an optional, config-declared capability.
5. **Identifier discipline.** Kacper's anti-invention rules for `TTQA-*`, `KAN-*`, `SUG-*`, and users are stricter and more specific than anything in Marek's skills. These should be generalised and adopted globally rather than treated as Timetracker-specific.

Also noted: Kacper's skill contains a comparison table against a platform skill named `story-ui-test-cases`, implying at least one more relevant skill exists in the organisation that we have not seen. Worth chasing before the inventory is declared complete.

### C3 — Karolina & Agata's `story-testability` contests four locked decisions

**Date:** 2026-09-28 · **Affects:** D1, D2, D3, D8 · **Source:** `Input/Karolina&Agata/TestabilityScanner.MD` (1,442 lines) · **Detail:** `Input/Karolina&Agata/NOTES.md`

This contribution is effectively a mature implementation of **The Reviewer**, with an HTML report design more developed than the working plan's. Most of it should be adopted. But it contradicts four decisions, and two of those contradictions are substantive rather than cosmetic.

1. **No hard gate — contradicts D8.** The skill's blocked-phrases list forbids "gate", "Blocked by QA", "Not ready", and "Story failed" outright. Readiness is a three-value advisory classification (`Ready with clarifications` / `Needs clarification before scope lock` / `Cannot plan scope yet`), deliberately framed as information rather than permission. Marek's skill hard-blocks on CRITICAL. **These cannot both be true.** The underlying disagreement is political, not technical: whether QA tooling is allowed to tell a team it may not proceed. Needs an explicit ruling, and D8 should not simply win by having been decided first.
2. **No numeric scores, ever — contradicts the plan's summary band.** The canonical limits table sets "Numeric scores / percentages / weighted totals in any output" to "**0 — never**". The working plan's Creator report leads with a coverage percentage and execution-hour estimates, and `catalog_coverage_pct` is in the payload. Their rationale is sound — a fabricated number invites false precision and gets quoted out of context — but coverage percentage is genuinely useful to the QA lead persona. Likely resolution: qualitative bands in the report, raw counts available, percentages confined to the payload rather than the rendered output.
3. **Tailwind CDN breaks self-containment — contradicts D1.** The skill permits "Tailwind CDN or simple semantic HTML". A CDN link is a network dependency, so the report stops working offline, in a locked-down browser, or as an email attachment. Resolution is straightforward: inline the CSS, keep their visual language and colour mapping. Non-negotiable given D1's whole purpose.
4. **Third host — extends D2.** The skill has a full execution contract for **Hive MCP** (`hive-mcp__run_skill` / `load_skill`), including the rule that a `result: "noop"` is a trigger to execute rather than a final answer. D2 covers Cursor and Claude only. Hive appears to be in real use, so it should be added to the host matrix.
5. **No-JS report vs the edit-and-export loop — tension with D3.** Their report uses `<details>`/`<summary>` with no JavaScript, which is why it prints to PDF and works with screen readers. D3 needs JavaScript for per-test decisions, inline editing, and the payload export. Resolution is progressive enhancement: the document is complete and readable with JavaScript disabled, and the editing layer is additive. The Reviewer's report may need no JavaScript at all.
6. **Scope — epic batch.** Their epic mode produces a two-tab report covering up to eight child stories in one file. The working plan assumes single-issue scope throughout, including in the payload contracts. This has to be designed in, not retrofitted.

**Adopt wholesale:** the three-tier information architecture (fixed tier per section, empty-state rather than omission), `<details>` progressive disclosure with item counts in summaries, the source-attribution and "Not stated in story" integrity rules, the blocked-phrases tone layer, data-sources-analyzed-vs-unavailable headers with per-step failure reasons, the canonical limits table pattern, and rescan delta mode marking each finding Resolved or Open.

**Still missing from `Input/`:** the `@story-ui-test-cases` skill. Both Kacper's and Karolina & Agata's skills reference it — one hands off to it, the other compares itself against it — so two independent contributions point at a skill we do not have.

**Supporting evidence for D1.** Kacper's repo already ships `skills-overview.html` — a fully self-contained HTML guide with inline style and script and no external references. That is independent confirmation that the self-contained-HTML choice in D1 fits how this team already works, and it gives `shared/render_report.py` an existing house style to stay consistent with rather than inventing one.

### C4 — Epic mode read child titles/status only, never child content — user-reported gap

**Date:** 2026-09-28 · **Reported by:** user, live usage of the shipped v1 skill · **Affects:** `SKILL.md` §6, `checklist.md` B12, `reference.md` Epic-specific finding patterns and limits table, `schemas/review-payload.schema.json` `rollup.epic_child_inventory`, `sample-report-epic.html`, `MANUAL.md` §7, `examples.md` Example 4.

As shipped, the Epic-mode child inventory (§6, gather steps 4–5 replaced by "a full, paginated child inventory") only ever requested `key`/`summary`/`status` — literally the same three fields as the Story-scope "sibling stories" gather step (item 5), which is deliberately title/status-only for a *different* issue's siblings. Nothing in the workflow text ever told the agent to fetch a child's `description`. This meant `checklist.md`'s existing B12 wording ("empty-description children vs an active epic") was unenforceable exactly as written — there was no step that ever populated a child's description to check whether it was empty. The user noticed in practice: the Reviewer was not recursively reading Epic children, only listing them.

**Fix, confirmed by the user:**
1. The same paginated JQL call that already builds the full child inventory (A-14 — never a sample) now also requests each child's `description` field. This is not an added round trip — Jira's search API returns arbitrary requested fields for every matched issue in one paginated call, so "recursive" here means "actually read," not "N additional fetches."
2. **Fallback (per explicit user instruction):** when a child's description is empty or template-boilerplate-only, the review falls back to that child's `summary` (its name) as a lower-confidence enrichment signal for the epic-level narrative — risk framing, "Not stated in epic," batch-handoff rationale, and the B12 keyword-overlap check itself.
3. This fallback is never allowed to silently look like real content. Each child records a `content_source` (`description` / `title_only` / `unavailable`) in the payload's `rollup.epic_child_inventory`, and a `title_only` child can never mark B12 COVERED on its own — this is exactly A-17's existing rule ("sibling/epic titles alone cannot mark dimension 12 COVERED"), which had only ever been written with Story-scope siblings in mind; C4 makes it apply identically to an Epic's own children.
4. Depth is one level (Epic → its direct children) — this does not additionally recurse into each child's own comments, subtasks, or links. That deeper read stays reserved for when that child is scanned individually (batch handoff, or a direct `scan {CHILD_KEY}`).

**Not reopened:** A-14 (full inventory, never a sample) is unchanged and now explicitly covers content as well as the key/summary/status list — the fix closes a gap in *what* was fetched per child, not the *completeness* rule around *how many* children are inventoried.

### C5 — Run-review rulings from the first four Epic runs (2026-09-29)

**Source:** `Output/Reviewer/PERSONA-REVIEW-RUNS.md` (PRF-10…PRF-25), triaged interactively with the user. Each ruling below records only what the user decided.

| Finding | Ruling | Amends |
|---|---|---|
| PRF-10 | **Readiness and gate are independent axes.** The gate comes from severity counts only; readiness comes from testability, scope confidence, and question priority. Any combination is valid. The readiness strip's colour follows readiness only. The gate gets one fixed plain-language line in Tier 1 (`reference.md` → "Gate line"), with no blocked phrases. | RV1 ("maps 1:1 to the same enum" is withdrawn; the split vocabulary and tone rules stand) |
| PRF-12 | **Epic mode never blocks.** No finding is CRITICAL in Epic mode. Group A rows that would be CRITICAL on a Story are emitted as HIGH, so an Epic's gate is at most `PASS_WITH_WARNINGS` and blocking happens only on each child's own scan. `A7` redaction and `Security` routing are unaffected. Enforced in the schema with an `if scope.type == epic` constraint. | D8 (scope narrowed to Story/Bug/Task), A-3 (Epic row added) |
| PRF-20 | **Schema bumped to 1.1, and any change to a required field or allowed value bumps the version** (history kept in the schema's `$comment`). A rescan against a persisted payload with a different `schema_version` refuses the delta, says why in one line, and runs a full scan. The four existing runs stay as history (`runs/README.md`) and get re-run after the remaining findings are resolved. | A3 (the renderer refuses any version it wasn't built for, not just an unknown major) |
| PRF-21 | **Reports are rendered from the payload by `scripts/render_report.py`; the model never hand-writes them.** All report prose moved into a new required `report` block, plus `finding.testing_impact`. The renderer validates, lints wording (blocked phrases, percentages), fixes section set/order/tiering, uses full payload ids in the decision layer, and computes the decided-items total. The sample reports are now its output on `samples/demo-*.payload.json`. In Epic mode the child inventory and status mix move to Tier 2 (expanded). | D1 (still self-contained HTML, now generated); PRF-05/PRF-06 samples regenerated |
| PRF-11 | **The skill's phrase list is authoritative.** `MANUAL.md` no longer promises the bare words "blocked"/"failed" never appear. Verbatim quotes of source text are exempt. The Data sources label for a `failed` source is now "Could not read" (payload value unchanged). The renderer lint skips quoted segments. | RV1 / D10 blocked-phrase wording |
| PRF-15 | **Lifecycle-aware wording for shipped Epics.** New `scope.lifecycle` (`pre_delivery`/`post_delivery`): Done or Waiting for Release/Deploy → "Post-delivery review", readiness heading "Readiness for regression and sign-off", and a fixed lead sentence. Severities, readiness values and the gate are unchanged. | — |
| PRF-16 | **The Epic batch is every child that isn't Canceled — no cap.** Ranked: children named by the most open findings/questions first, then Waiting for Release / In Progress before To Do, then Done, then key order. `confirm batch` scans them all in that order, 8 at a time; `--batch keys` scans a subset; `--batch all-wfr` is dropped. The renderer lint checks the set and the order. *Amended same day:* first ruling was only "never a Canceled child" with the ≤8 cap kept. | RV4 (batch size), D4 limits table (batch row) |
| PRF-17 | **All ten question topics are valid in any scope**; the Epic topics are preferred for epic-level concerns. The fixed topic order is per scope (Epic topics first on an Epic). Question ids are assigned in display order (lint-checked). Epic-scope AC/scope questions default to `PO`. | Clarification Questions addendum (topic split) |
| PRF-13 | **A question that clears a HIGH+ finding is High priority, always.** If that exceeds 5 High: merge related questions first (one question may unblock several findings), then go up to 15 with `report.question_cap_reason`. Renderer lint enforces both. | Clarification Questions addendum (priority caps) |
| PRF-14 | **MEDIUM gives warnings.** `PASS` = 0 CRITICAL, 0 HIGH, 0 MEDIUM (LOW only, or none); `PASS_WITH_WARNINGS` = 0 CRITICAL and ≥1 HIGH or MEDIUM; `BLOCKED` = ≥1 CRITICAL. The renderer lint recomputes the gate from open severities. | A-3 (LOW alone no longer gives warnings) |
| PRF-19 | **New Epic-only checklist Group C**, category `epic_lifecycle`: C1 rollout / feature-flag plan, C2 verification evidence (post-delivery only), C3 tracking-field consistency (LOW at most). The category → allowed-rows table is now normative and lint-checked. Folded into schema 1.1 as a widening change (see note below). | RV3 (checklist gains a third group) |
| PRF-22 | **Owner shown on every question in both Jira templates, and the renderer writes `jira-comment-full.txt` and `jira-comment-short.txt`.** The model never hand-writes a Jira comment. | §9 Jira comment |
| PRF-23 | **Screenshots are read through the MCP:** `getJiraIssue` (attachment field) → `downloadJiraIssueAttachment` / `downloadConfluenceAttachment` → run `downloadCommand` to a temp path outside the repo → vision read → delete. Signed URLs and images are never persisted. **No browser fallback.** Verified on ONE-324524 attachment 1242785. | Second-pass screenshot resolution (mechanism now specified) |
| PRF-24 | **Links are routed by host across every connected Atlassian site.** The run maps host → MCP server + `cloudId` via `getAccessibleAtlassianResources` on each server and reads each link through the matching one, naming the site in `context_loaded[].detail`. Only when no connection covers the host is it recorded `unavailable`, with the fixed reason `linked page is on {host}; no connected Atlassian site covers it (connected: {sites})`. *Revised same day:* the first ruling (never attempt cross-site links) was superseded once two simultaneous site connections were confirmed working (`mcp-remote` setup, now in `MANUAL.md` §10). | R-G2 |
| PRF-25 | **Backlog:** roll up N payloads of the same schema version into one report. GitHub issue **not yet created** — draft ready in [`Output/Reviewer/gh-done.md`](Output/Reviewer/gh-done.md); run when `gh` is installed. | — |

**Schema note (PRF-13/16/19), user-confirmed:** the new category, the C1–C3 pattern, `report.question_cap_reason`, and the removed batch cap stay in 1.1. **PRF-20's rule is amended:** a change that makes previously valid payloads invalid bumps the version; a change that only widens what's allowed (new optional field, new allowed value, looser limit) doesn't, and is logged in the schema's `$comment`.

### C6 — Spec gaps surfaced by the ONE-354099 schema-1.1 re-run (2026-09-29)

**Source:** subagent re-run [`runs/2026-09-29-1151-ONE-354099/`](../Output/Reviewer/runs/2026-09-29-1151-ONE-354099/). Items 1–5 were fixed same day in the skill, checklist, reference, and renderer. Items 6–14 remain backlog unless noted.

| # | Gap | Status |
|---|---|---|
| 1 | Gate line "Child scans can start" on a zero-child Epic | **Fixed** — renderer + `reference.md` gate table |
| 2 | B12 on empty child inventory | **Fixed** — `checklist.md` zero-child note |
| 3 | `scan_label` on schema-mismatch full scan | **Fixed** — `SKILL.md` §11 |
| 4 | Stale tool names / Confluence summary-only | **Fixed** — `reference.md` tool mapping |
| 5 | Remote/web links missing from gather step 6 | **Fixed** — `SKILL.md` step 6 |
| 6 | Workflow boilerplate Confluence links | **Fixed** — `SKILL.md` step 8 exception |
| 7 | Epic parent Initiative — no gather rule / `context_loaded` type | Open — use `not_applicable` + detail until a parent row is added |
| 8 | `parent =` fallback for Epic child inventory | Open — document both JQL patterns in §6 (subagent already ran both) |
| 9 | AC field discovery without operator; no `config/` in repo | Open — product config is future; default + ask-once remains |
| 10 | Verbatim quote vs English-only on foreign source text | Open — translate + cite source; flag in finding |
| 11 | `requirement_fingerprint` algorithm unspecified | Open — document canonical JSON + hash in `reference.md` |
| 12 | Batch ranking field list | **Fixed** — limits table in `reference.md` |
| 13 | A5 design link MEDIUM vs HIGH | Open — judgment call; no schema change |
| 14 | `scope.lifecycle` not required in schema for Epic | Open — add schema `allOf` when demo payloads are updated |

### C7 — Spec gaps from the ONE-181964 schema-1.1 re-run (2026-09-29)

**Source:** [`runs/2026-09-29-1151-ONE-181964/`](../Output/Reviewer/runs/2026-09-29-1151-ONE-181964/). Fixed same day unless marked open.

| # | Gap | Status |
|---|---|---|
| 1 | Unreferenced Epic attachments | **Fixed** — gather step 10 reads every image on the target issue |
| 2 | Inline images in child descriptions | **Fixed** — §6 explicit v1 limit + finding instead of guess |
| 3 | Non-Confluence linked documents | **Fixed** — `external_document` in schema + step 8 wording |
| 4 | "With a severity" on unfetched doc | **Fixed** — A8 finding, not `context_loaded` severity |
| 5 | Schema-mismatch scan label | Already in §11 / C6 #3 |
| 6 | Link-only child descriptions | **Fixed** — `content_source` rules in §6 |
| 7 | Majority title-only on Done Epic / tie | **Fixed** — `reference.md` epic patterns |
| 8 | AC field without operator | **Fixed** — step 2 non-interactive fallback |
| 9 | Temp path vs tool schema | **Fixed** — step 10 note |
| 10 | `--strict` still writes on lint fail | **Fixed** — renderer skips writes when `--strict` and lint fails |
| 11 | LOW finding moves batch rank | **Fixed** — ranking counts CRITICAL/HIGH/MEDIUM findings only |
| 12 | Post-delivery lead `{status}` | **Fixed** — renderer fallback + reference note |
| 13 | JQL compact drops `description` | **Fixed** — §6 + tool mapping `view: "full"` |

### C8 — Spec gaps from the ONE-324524 schema-1.1 re-run (2026-09-29)

**Source:** [`runs/2026-09-29-1153-ONE-324524/`](../Output/Reviewer/runs/2026-09-29-1153-ONE-324524/). Overlaps C6/C7 where noted.

| # | Gap | Status |
|---|---|---|
| 1 | Search omits child `description` | **Fixed** — §6 `getJiraIssue` fallback + reference mapping |
| 2 | Confluence/Figma only on Epic body | **Fixed** — §6 child URL pass; step 8/11 Epic wording |
| 3 | Workflow boilerplate Confluence | **Fixed** — step 8 field-name skip (C6 #6 aligned) |
| 4 | No product `config/` in repo | Open — optional per-product config; runs use defaults + metadata discovery (step 2) |
| 5 | Schema-mismatch scan label | Already §11 / C6 |
| 6 | Batch rank double-counts fields | **Fixed** — renderer `mention_count` + limits table |
| 7 | B9/A6/C1/A2/A4/A5 edge cases | Open — judgment at scan time; no checklist renumber |
| 8 | Extra lint rules (8-question cap, gate counts, …) | Open — backlog; `--strict` covers gate, batch, categories, phrases |
| 9 | Signed URL in shell vs "never in chat" | **Fixed** — step 10 → "rendered reports" |
| 10 | Non-English sources | **Fixed** — §3 summarize-in-English rule |
| 11 | Single-quoted blocked-phrase exemption | **Fixed** — renderer lint + §7 bullet |

---

## Reviewer resolutions — Part 1 (requirements review)

**Date:** 2026-09-28 · **Source:** every Difference, Gap, Ambiguity, and Uncertainty raised in [INPUT-REVIEW.md](INPUT-REVIEW.md) Part 1 · **Scope:** The Reviewer only. Part 2 (test case creation / The Creator) is deliberately out of scope for this pass and its D20–D40, T-G1–T-G12, A-22–A-45, and U-9–U-17 remain unresolved.

Every item below got a ruling so Phase 3 has no open design questions left when it starts writing `The Reviewer/SKILL.md`. Rulings that change or sharpen a locked decision (D1–D9) or an architectural decision (A1–A10) say so explicitly; they supersede the older wording rather than contradicting it silently.

**Provenance note:** the first pass through this section (below) was written up as proposals without asking the user first. On 2026-09-28, the eight highest-leverage calls (the four headline rulings plus D12, D13/U-2, U-7, R-G1/R-G2) were put back to the user as explicit questions. Six were confirmed as proposed; two were **not** — Hive support and Confluence fetch both got a stronger answer than the original draft recommended. Those two are corrected in place below, with the original reasoning struck through in spirit (kept as history in the "Notes" column) rather than deleted.

### Headline rulings

These four resolve the highest-leverage tensions and are referenced by several of the line-item rulings below.

| # | Ruling | Resolves | Rationale |
|---|---|---|---|
| RV1 | **Gate stays technical; tone stops being adversarial.** `The Reviewer` keeps a real machine-readable gate (`PASS / PASS_WITH_WARNINGS / BLOCKED`, CRITICAL hard-blocks The Creator, `force` override) — D8 is not overturned. But the human-facing headline never uses "gate", "blocked", or "failed". It shows a readiness label (`Ready to build tests` / `Needs clarification before test design` / `Needs clarification before scope can be tested`) that maps 1:1 to the same enum. One boolean truth, two vocabularies for two audiences. | U-1, D2, D10, C3.1 | The disagreement was never technical — both contributions compute the same thing. It was about whether the PM-facing document is allowed to sound like a verdict. Splitting the vocabulary from the enforcement lets both be true at once. |
| RV2 | **One finding-severity scale, not two.** Findings use Marek's four levels (`CRITICAL/HIGH/MEDIUM/LOW`) directly — there is no second finding-severity scale to translate from. K&A's High/Medium/Optional survives only as `question_for_PM.priority`, a distinct field with a distinct meaning (urgency of an answer, not severity of a gap). | D3, R-G5 | A mapping table between two independently-invented scales is a standing maintenance burden and was never defined by either contribution. Removing the second scale removes the need for a mapping instead of inventing one under time pressure. |
| RV3 | **Nine sections and twelve dimensions merge into one versioned checklist.** `requirement_standard.md`'s 9 sections and `TestabilityScanner.MD`'s 12 dimensions become a single numbered list (target: dedupe to roughly 12–14 items), owned by this decision memory, versioned like this file (append-only, superseded entries marked not deleted). Every finding's `checklist_ref` (D15) points at exactly one row of this single list. | U-5, R-G9, D15 | Two overlapping rule sets with no stated relationship is exactly the "no cross-reference" problem persona P5 exists to fix. Merging now, before Phase 3 writes the skill body, is cheap; merging after two more contributions have added their own checklists is not. |
| RV4 | **Epic batch mode ships in v1, not Phase 5.** `ReviewPayload` supports single-issue and epic-batch scope from the first schema freeze. | U-6, D16, R-G10 | K&A's epic mode is materially complete (child inventory, status mix, `recommendedBatchKeys`) and three other rulings (D16, R-G8, persona P8) already assume it exists. Retrofitting scope into a schema after Phase 2 fixtures are written is the exact risk the working plan's own risk table calls out for payload churn. |

**User-confirmed 2026-09-28:** RV1, RV2, RV3, and RV4 were each put to the user as an explicit multiple-choice question and confirmed as written above — none changed.

### Differences (D1–D19)

| # | Decision | Notes |
|---|---|---|
| D1 | Adopt Marek's schema-valid `ReviewPayload` JSON as the source of truth; `render_report.py` renders it to self-contained HTML (per locked D1) and, on request, to flat Markdown for in-chat display. The JSON is always written to disk under `artifacts/{run_id}/`, closing R-G4's "half-solved" cross-session read. | Confirms the "Reconcilable? Yes" call already in the review table. |
| D2 | Resolved by **RV1**. | — |
| D3 | Resolved by **RV2**. | — |
| D4 | Adopt K&A's canonical limits table wholesale for The Reviewer's output: ≤8 questions per scan (≤5 High), overflow noted rather than silently dropped, ≤25 siblings, ≤3 Figma frames, ≤50 checklist-CSV rows. | Marek's contribution has no answer to report bloat; there is nothing to reconcile against. |
| D5 | Adopt K&A's rescan-delta concept (mark each finding Resolved / Open / New), but the diff target is the persisted `ReviewPayload` JSON on disk, not chat state. See R-G3. | |
| D6 | Union of both input breadths: Jira fields or a normalized bundle (Marek) **plus** all comments, siblings, epic children, screenshots (text only), spreadsheets (paste only, never auto-fetched), Figma (≤3 nodes) (K&A) **plus linked Confluence pages, fetched read-only (user-confirmed, see R-G2)**. Each source is a capability in the A8 capability table and degrades independently. | Confluence added 2026-09-28; PDF links remain unresolved. |
| D7 | Adopt K&A's Figma ingest protocol wholesale: URL detection, `fileKey`/`nodeId` parsing (`-`→`:`), ≤3 `get_design_context` calls, mandatory `Source: Figma` labels, "layout alone is not a rule." | |
| D8 | Adopt K&A's issue-type model: Story / Bug / Task / Epic handled explicitly; AC-gap dimensions are skipped (not penalised) when the issue type has no AC-equivalent field. Resolves U-3 the same way. | |
| D9 | Adopt Marek's redaction / `data_sensitivity: CRITICAL` rule, extended to the new K&A ingest paths per R-G6. | |
| D10 | Adopt K&A's blocked-phrases tone layer for all human-facing prose, per **RV1**. | |
| D11 | Adopt all five of K&A's classifications (testability, scope confidence, risk + rationale tags, automation candidate, readiness) into `ReviewPayload`. `readiness` becomes the human headline described in RV1; the gate enum stays a separate machine field. | |
| D12 | **User-confirmed.** Raw counts ("3 findings, 2 High") are always allowed in prose; derived scores, weighted totals, and percentages are payload-only fields, never rendered into narrative text. | Resolved together with A-13. |
| D13 | **User-confirmed 2026-09-28 — stronger than first proposed.** Hive is confirmed in production use. D2 is amended: Hive MCP is a fully supported third host, on equal footing with Cursor and Claude, not a defensive/best-effort add-on. The Reviewer implements Hive's execution contract (`result: "noop"` means execute, forbidden end states) as first-class behaviour, verified in Phase 3/6 alongside the other two hosts. | Original draft proposed "build defensively, don't commit" pending confirmation. The user confirmed Hive is real, so that hedge is removed. Closes Q8. |
| D14 | Adopt K&A's three-tier HTML presentation wholesale (fixed tier per section, empty-state instead of omission, item counts in every summary), **minus the Tailwind CDN** per C3.3 — inline CSS only. | |
| D15 | Adopt Marek's `checklist_ref` on every finding; per **RV3** it now points at the single merged checklist rather than one of two separate lists. | |
| D16 | Keep both: a cross-story rollup with `recommended_pm_order` for JQL/multi-issue scope, and an epic child inventory + status mix + `recommendedBatchKeys` for epic scope (now in v1 per **RV4**) — they serve different scopes, not the same one twice. | |
| D17 | Adopt K&A's QA readiness checklist output, CSV-exportable, ≤50 rows, each row tied to Source / `F#` / `Pending Q#` (renamed to the merged checklist's finding ids per RV3/RV2). | |
| D18 | Adopt K&A's rule: English by default, no exceptions, including for the blocked-phrases list in any rendered translation. | |
| D19 | Adopt K&A's concrete AC precedence: AC custom field → AC bullets in description → explicit "AC template empty — no story-specific criteria" → unavailable. Closes the deferred question in `requirements-template.md` §4. | |

### Gaps (R-G1–R-G10)

| # | Decision | Notes |
|---|---|---|
| R-G1 | Accepted as a stated v1 limitation, not solved. The Reviewer's "what this skill does NOT do" section states plainly that it does not verify against product code. Revisit only if a code-grounded contribution is added later (mirrors U-11 on the Creator side). | |
| R-G2 | **User-confirmed 2026-09-28 — stronger than first proposed: Confluence fetch is in v1.** Since the Atlassian MCP surface is already in use for Jira, The Reviewer also resolves a linked Confluence page, fetches its content read-only, and includes it in `context_loaded[]` with the same redaction rules as Jira (D9). This is a new capability in the D6 input-breadth set and the A8 capability table. **PDF links stay out of scope** — no PDF-parsing capability was confirmed, so those remain "linked but not fetched" findings per K&A's existing pattern. | Original draft proposed "neither Confluence nor code-grounding in v1." The user picked Confluence specifically; code-grounding (R-G1) was not selected and stays deferred as originally proposed. |
| R-G3 | Resolved by D5: rescan diffs the persisted payload, and works across sessions and operators because the payload is a file, not chat memory. | |
| R-G4 | Resolved by D1 plus a new field: `ReviewPayload` carries a `requirement_fingerprint` (hash of the normalized bundle) and `generated_at`. Any later read — a rescan or The Creator's gate check — re-fetches the live requirement, recomputes the fingerprint, and flags `STALE` before trusting a cached PASS. Also answers U-8. | |
| R-G5 | Resolved by **RV2** — there is no second scale to map. | |
| R-G6 | Resolved by D9 — redaction extends to screenshot quotes, spreadsheet pastes, and Figma text. | |
| R-G7 | Adopt K&A's dimension 9 (NFR: performance, accessibility, i18n, security) as a mandatory row in the merged checklist (RV3). `requirement_standard.md`'s successor gets an explicit NFR section, and the `non_functional` bundle field is actually inspected instead of only defined. | |
| R-G8 | Add an `owner_hint` field per finding (`PM` / `UX` / `EM` / `Security` / …), generalising K&A's epic-mode PO/UX/EM routing to story scope too. Gives personas P7 (UX) and P8 (release manager) a route that Marek's PM-only model didn't have. | |
| R-G9 | Resolved by **RV3**. | |
| R-G10 | `story-epic-batch-orchestrator` stays out of `Input/` for v1. The Reviewer's epic-batch mode (RV4) implements its own batching directly rather than depending on an uncontributed skill. Flag for K&A to locate the original if epic-batch complexity outgrows what's reviewed here. | |

### Ambiguities — Marek's contribution (A-1–A-10)

| # | Decision | Notes |
|---|---|---|
| A-1 | Already resolved by the existing architecture: A9's config resolution order and D6 (per-product config) mean The Reviewer has no hardcoded repo-layout paths. Nothing further to decide. | |
| A-2 | Standardise on JSON — that's the format that actually exists (`jira_xray_mapping.json`). Every reference to a `.yaml` variant is a documentation bug to fix during the port, not a real second format to support. | |
| A-3 | Ruled definitively, stated once in `The Reviewer/SKILL.md` and referenced (not restated) elsewhere: **PASS** = 0 CRITICAL and 0 HIGH. **PASS_WITH_WARNINGS** = 0 CRITICAL, ≥1 HIGH/MEDIUM/LOW. **BLOCKED** = ≥1 CRITICAL. *Amended 2026-09-29 by C5 PRF-14: MEDIUM also gives warnings; LOW alone gives `PASS`.* | |
| A-4 | `blocks_test_generation` becomes a computed, read-only field — `true` iff `severity == CRITICAL` — never authored by the model. Schema marks it accordingly so the constraint the field exists to protect can actually be validated. | |
| A-5 | Relax the schema: `requirement_keys` may be empty when `scope.type` is `bundle` (or a future `pdf`/non-Jira scope); add a free-text `source_ref` field for those cases so the payload stays traceable without a Jira key. | |
| A-6 | Redefine redaction as a **display-time** rule, not a pre-analysis one: the agent unavoidably reads raw data, but `excerpt_quote` and every rendered output must never surface a secret/PII verbatim. The rule moves from "before LLM analysis" to "before this data leaves the skill." | |
| A-7 | Fix the drift: every example and template uses the one canonical path — `{artifacts_dir}/{run_id}/...` resolved from config — no hardcoded `Skills/artifacts/...` anywhere. | |
| A-8 | `force_override_by` (plus a timestamp) becomes conditionally required whenever `force: true` — enforced structurally in the schema, not left to the example author to remember. | |
| A-9 | `Agent Skills Specification.md` is superseded, not deleted — noted here as historical. `The Reviewer/SKILL.md` is the current source of truth for what's decided and implemented. | |
| A-10 | Not fixed in `Input/` — it stays read-only per the working plan's repository layout. The **ported** copy under `shared/templates/` gets correct relative links for the new repo layout; the original is left as-is for provenance. | |

### Ambiguities — Karolina & Agata's contribution (A-11–A-21)

| # | Decision | Notes |
|---|---|---|
| A-11 | Inline the scoring rules directly into the merged checklist document (RV3). No external `scoring-reference.md` is created; the "self-contained" claim is made true instead of excepted. | |
| A-12 | Same resolution as A-11: `render_report.py` (A2) owns all HTML generation. No skill body references a companion `html-report-template.html`. | |
| A-13 | Resolved together with D12: the ban is on **derived** numbers (scores, percentages, weighted totals) in prose, not on raw counts. State that distinction explicitly in the merged checklist so a literal reader stops flagging the skill's own templates. | |
| A-14 | Full inventory wins. Drop every "(sample)" label from the epic template; if pagination is needed, page through to completion and label counts as "of N total," never "sample." | |
| A-15 | Ruled definitively, taking the stricter of the two definitions: **"Ready with clarifications"** = no High findings on core dimensions **and** only Optional questions open. Any open Medium question keeps the status at "Needs clarification before scope lock." | |
| A-16 | **User-confirmed 2026-09-28: no cumulative cap.** The ≤8/≤5-High cap stays per-scan only; ≤5 new per rescan. No additional ceiling on total open questions. | The agent's original ≤15-cumulative proposal was not confirmed and has been dropped — see the addendum above. |
| A-17 | Reword the rule instead of leaving it self-contradicting: sibling/epic **titles alone** cannot mark dimension 12 COVERED, but sibling/epic **acceptance criteria or explicit description text** can. The dimension can be COVERED — just not from a title. | |
| A-18 | Generalise: `automation_candidate.suggested_level` names a **logical** level (`UI E2E` / `API` / `Unit`), never a specific framework. The framework name (Playwright, Cypress, etc.) comes from per-product config, matching the pattern already set for other tooling in A8/A9. | |
| A-19 | Add explicit Bug/Task output template variants to the report spec (drop AC-gap sections, keep everything else) so the validation checklist stops requiring Story-only sections for non-Story issues. | |
| A-20 | Resolved by C3.3 already: inline CSS only, one visual language, no CDN branch. | |
| A-21 | Not fixable retroactively — accepted as a known gap for this contribution. Going forward, every **new** contribution folder under `Input/` must carry a `SOURCE.md` (mirroring Kacper's) stating origin repo, path, and date. This is a process rule for future intake, not a backfill requirement. | |

### Uncertainties (U-1–U-8)

| # | Decision | Notes |
|---|---|---|
| U-1 | Resolved by **RV1**. | |
| U-2 | **Resolved.** User-confirmed 2026-09-28: Hive is in production use. See D13. | |
| U-3 | Yes — resolved by D8 (adopt K&A's issue-type model; Bug and Task are first-class). | |
| U-4 | Config resolves it first (`jira.field_map.acceptance_criteria` per product). If unset, the skill discovers the field via MCP metadata at runtime, asks the operator once, and offers to persist the answer into that product's config so the question isn't asked again. | |
| U-5 | Resolved by **RV3**. | |
| U-6 | Resolved by **RV4**. | |
| U-7 | **Resolved — user-confirmed 2026-09-28.** The HTML report attaches to the Jira issue as a comment attachment, opt-in per config (ties to Q6). Closes Q7. | |
| U-8 | Resolved by R-G4: the rescan baseline is the payload's `requirement_fingerprint`, checked against a fresh fetch before trusting or diffing against a cached result. | |

### User addendum — Clarification Questions is a mandatory, fully-specified output (2026-09-28)

Flagged by the user: the line-item rulings above treated K&A's "Clarification questions" mechanism as background (folded into D4's limits and RV2's priority field) rather than locking it in as its own required section with K&A's full structure. Corrected — this is now explicit:

- **`ReviewPayload` gets a `questions[]` array**, one entry per question: `question_id` (`Q1`, `Q2`, …), `topic` (Behavior / Scope / Edge cases / Integrations / Permissions / Data — extendable per product config), `question`, `context`, `source`, `priority` (`High` / `Medium` / `Optional` — this is the `question_for_PM.priority` field from RV2), `unblocks` (finding ids and/or checklist_refs), `status` (`open` / `resolved`, maintained across rescans per D5).
- **Rendered as its own section**, grouped by topic, placed in **Tier 2** of the HTML report (expanded by default) immediately after the findings table — matching K&A's tier placement exactly, not left implicit.
- **Exportable as a copy-paste Jira comment block** in two densities, both adopted verbatim from K&A: a **full** version (`h3. Clarification questions`, grouped by topic, wiki-markup numbered list) and a **short** version (High-priority questions only, max 5) for the short-format Jira comment.
- **Epic scope groups questions for PO / UX / EM**, not just the PM, covering epic-level topics (definition of done, which PRD section is authoritative, canonical Figma node, child-story priority order, rollout/flag strategy) — ties to R-G8's `owner_hint`.
- Capped by D4's limits throughout (≤8 default / ≤5 High / ≤15 with a stated reason for genuinely complex stories; ≤5 new per rescan).

**This surfaced a real gap, not just a documentation oversight — see Q6 below, opened by the same check.**

### Q6 reopened — is Jira comment-back copy-paste-only, or does it also auto-post?

Re-checking the two contributions to write the addendum above surfaced a genuine unresolved conflict that the original Part 1 pass mischaracterised as consensus (Similarity #1 in `INPUT-REVIEW.md` calls both "opt-in," which hides the difference):

- **Marek's `requirements-review`** calls `addCommentToJiraIssue` directly — an actual MCP write — gated by "user opts in and policy allows." This is genuine automated writing to Jira, just behind a flag.
- **K&A's `story-testability`** has no write capability at all for this. "Jira comment mode" only ever formats a wiki-markup block for the human to copy and paste themselves. There is no `addComment` call anywhere in the skill.

These are two different capabilities, not one capability with two settings, and Q6 ("should The Reviewer comment findings back to Jira by default?") was never actually answered — it assumed the capability exists and only asked about the default. **Reopened, put back to the user below** rather than guessed at a second time.

**User-confirmed 2026-09-28: both capabilities exist.** The Reviewer always produces the copy-paste comment block (findings summary and/or clarification questions, in full and short Jira-wiki-markup densities per the addendum above) as part of every report — that part is unconditional, since it costs nothing and a human can ignore it. Separately, `policy.jira_comment` in the per-product config gets a third value beyond the working plan's original `"opt-in"` boolean-ish framing: **`"off"` (default) / `"copy-paste-only"` / `"auto-post"`.** Only `"auto-post"` causes The Reviewer to call `addCommentToJiraIssue` itself (Marek's mechanism, named as a capability in the A8 table, degrading to copy-paste-only if the write capability is unavailable). Closes Q6.

**User-confirmed 2026-09-28: no cumulative open-question cap.** A-16's ≤15-open-at-once ceiling is dropped. Only K&A's original caps apply: ≤8 questions per scan (≤5 High, ≤15 with a stated reason for genuine complexity), ≤5 new per rescan. If that turns out to let stale questions pile up across many rescans in practice, revisit in Phase 6 with real data rather than a number picked in advance.

### Second-pass findings — deep re-read, 2026-09-28

The first Part 1 pass worked from `INPUT-REVIEW.md`'s own summary. Asked directly whether anything was still loose, the source files were re-read line by line (Marek's `SKILL.md` / `reference.md` / `examples.md` / `requirement_standard.md` / `review_findings.schema.json` / `requirements-template.md`, all of K&A's `TestabilityScanner.MD`, `NOTES.md`) rather than trusting the earlier summary a second time. Three real conflicts turned up that the first pass either missed or parked in the persona table without ever converting to a ruling.

**P10 — Jira MCP total outage vs. partial failure (never actually resolved, only named).** `INPUT-REVIEW.md`'s persona table flagged this ("Marek aborts on Jira MCP failure … where K&A degrades — opposite reflexes, and the merged behaviour is unspecified") but it was never carried into the D/R-G/A/U lists or given a ruling. **User-confirmed:** split by failure type. Total Jira outage with no fallback bundle → abort, there is nothing to review. Total outage **with** a pre-supplied bundle or pasted content (Path B, D6) → proceed on that. Partial failure mid-gather (primary issue fetched, a secondary source like comments/siblings/Figma fails) → never abort; degrade and record it in `context_loaded[]`, per K&A and the already-adopted Similarity #10. This reconciles Marek's "no partial gate PASS" (a missing required source should never let the gate read a clean PASS — it should already surface as a finding under the existing severity rules) with K&A's graceful degradation, without either being overturned.

**Screenshot binaries reaching the model — a real capability conflict, not a wording difference.** K&A's screenshot protocol literally reads the image (`Read` tool on the binary) to quote visible text. Marek's checklist item 8.3 rates it a finding when "attachment index lists names only" isn't honoured — i.e. its original intent is that binaries never reach the LLM at all. Adopting D6/D7 (screenshot ingest, Figma ingest) already implied a decision here that was never stated. **User-confirmed:** allow it. Screenshot vision-reading is a real, adopted capability. Marek's rule 8.3 is reinterpreted as being about **output** redaction (ties to R-G6 — don't quote PII/secrets visible in a screenshot into the report) rather than blocking the model from viewing the image at all.

**Bundle richness — how much of `requirements-template.md`'s 17 sections does The Reviewer's own checklist enforce?** The bundle shape (`personas`, `fixtures`, `apis`, `ui.screens`, `non_functional` broken out by category, `dependencies`, `glossary`, `assumptions`, `attachments_index`) exists mainly to feed **The Creator's** test generation — `requirements-template.md` says so explicitly ("aligns with downstream TestCaseDraft expectations"). But `requirement_standard.md` §9 (`template_compliance`) checks "required sections … present or explicitly N/A" without distinguishing review-relevant sections from generation-only ones. **User-confirmed:** narrow scope. The Reviewer normalizes and checks only `work_item`, `description`, `acceptance_criteria`, `scope`, testability signals (environment/data/API/UI presence — not the full fixture/persona detail), `traceability`, `open_questions`, and `data_sensitivity`. The richer sections are populated later, for and by The Creator; their absence is not a Reviewer finding. This also sharpens R-G7: the NFR check is "is `non_functional` addressed at all," not "is every one of performance/security/accessibility/observability itemized."

**Correction to RV3's parenthetical.** RV3 said the merged checklist would "dedupe to roughly 12–14 items." Re-reading both lists in full shows they're not as overlapping as that implied — Marek's 9 sections are mostly **structural/document quality** (is there an AC, is it testable, is scope stated, is there a design link) while K&A's 12 dimensions are **behavioural coverage topics** (negative paths, boundaries, roles, NFR, observability…). Only a few genuinely overlap (testability data/environment ↔ dimensions 6/10; AC testability ↔ dimensions 1/2). The merged checklist is one numbered document with two clearly labelled groups — structural and behavioural — not a forced 1:1 merge; realistic count is closer to **16–18 rows**. RV3's substance (one versioned list, one `checklist_ref` namespace) stands; only the count estimate was wrong.

---

## Environment facts

| Fact | Detail | Impact |
|---|---|---|
| Xray MCP unavailable | The `user-xray` MCP namespace fails live tool discovery in this workspace | Phase 4 must open by fixing or replacing the connection. The GraphQL script fallback is a first-class path, not a theoretical one. |
| Atlassian MCP available | Jira and Confluence tools present | Requirement fetch and optional comment-back are viable. |
| Repo character | DOCS is a personal documentation repo, not an application codebase | Likely not the long-term home for shared skills — see open question Q2. |

---

## Open questions

Carried from the plan; none block Phase 1 except Q0.

| # | Question | Needed by |
|---|---|---|
| Q0 | What goes into `The Creator/Input/`? | Phase 1 — blocking |
| Q1 | Which two products pilot this, and can the second config be written without its team's help? | Phase 6 |
| Q2 | Where do the skills ultimately live? A shared QA tooling repo is the natural home — who owns it? | Phase 6 |
| Q3 | One Xray test project for all products, or one per product? Affects config and duplicate-search scope. | Phase 4 |
| Q4 | Is a sandbox Xray available per product, or is draft-label-in-production the only option for some? | Phase 4 |
| Q5 | Who approves submission — the QA engineer who ran it, or does a lead countersign P0 suites? Currently modelled single-approver. | Phase 4 |
| ~~Q6~~ | ~~Should The Reviewer comment findings back to Jira by default?~~ **Resolved 2026-09-28:** both capabilities ship — copy-paste block always generated; `addCommentToJiraIssue` auto-post is opt-in via `policy.jira_comment: "auto-post"`, default `"off"`. | Closed |
| ~~Q7~~ | ~~How do reports reach a PM without repo access?~~ **Resolved 2026-09-28 (U-7):** Jira attachment, opt-in per config. | Closed |
| ~~Q8~~ | ~~Is Hive MCP confirmed in production use?~~ **Resolved 2026-09-28 (D13/U-2):** confirmed — Hive is a fully supported third host. | Closed |

---

## Session log

| Date | Session | Outcome |
|---|---|---|
| 2026-09-25 | Planning kickoff | Established D1–D8 and A1–A10. Key discussion: Cursor Canvas portability, resolved in favour of self-contained HTML (D1). Wrote `working-plan.md` with a 6-phase delivery plan. |
| 2026-09-28 | Correction | Recorded C1 — consolidation inputs are `The Creator/Input/`, not `AI in QA/Skills/`. Created this memory file. |
| 2026-09-28 | Input staging | Copied Marek's two skills plus all their shared dependencies into `Input/Marek/`. Q0 partially answered; Phase 1 inventory can begin once contributions are confirmed complete. |
| 2026-09-28 | Input staging | Added Kacper's `TestCaseWriting` skill from `7pace/7pace.Timetracker` into `Input/Kacper/`, with provenance in `Input/Kacper/SOURCE.md`. First evidence of genuine conflict between contributions — see C2. |
| 2026-09-28 | Input staging | Pulled the sibling `AutomatingTestCases` skill, hub README, and `skills-overview.html` from the same repo. The hub documents a three-stage pipeline with a deliberate manual Jira import between drafting and automation. |
| 2026-09-28 | Input staging | Karolina & Agata's `story-testability` added to `Input/Karolina&Agata/`. Reviewed; contests D1, D2, D3, and D8 — see C3. Four decisions now need re-ruling before Phase 1 can produce a coherent port checklist. |
| 2026-09-28 | Full inventory review | Wrote `INPUT-REVIEW.md` — every file under `Input/` read in full, split into Part 1 (requirements review) and Part 2 (test case creation). Surfaced 19 differences, 10 gaps, 21 ambiguities, and 8 uncertainties in Part 1 alone. |
| 2026-09-28 | Reviewer resolution pass | Ruled on every Part 1 item from `INPUT-REVIEW.md` — see "Reviewer resolutions — Part 1" above. Four headline rulings (RV1–RV4): gate stays technical with a non-adversarial human-facing label (resolves U-1, the most consequential open question); one four-level severity scale, not two; Marek's 9 sections and K&A's 12 dimensions merge into one versioned checklist; epic-batch scope ships in v1, not Phase 5. Part 2 (The Creator) deliberately left untouched. Opened Q8 (Hive confirmation) and annotated Q7 with a provisional default. **Written up as proposals without asking the user — flagged and corrected in the next session.** |
| 2026-09-28 | User confirmation | Put the eight highest-leverage Part 1 calls to the user as explicit questions instead of assuming the prior session's proposals. Six confirmed as written (RV1–RV4, D12, R-G1/no-code-grounding). Two came back stronger than proposed: **Hive MCP is confirmed in production use** (amends D2, resolves D13/U-2, closes Q8) and **Confluence fetch is in scope for v1** (extends D6, resolves R-G2 — PDF links still out of scope). U-7/Q7 confirmed and closed. |
| 2026-09-28 | Gap check, requested by user | User asked for K&A's Clarification Questions mechanism to be locked into the final skill explicitly, and asked directly whether Part 1 had any remaining loose ends. Re-reading the source to answer honestly surfaced a real one: Marek's skill can auto-write Jira comments (`addCommentToJiraIssue`, opt-in); K&A's cannot at all (copy-paste only) — the first Part 1 pass had mischaracterised these as the same capability with different defaults. Reopened as Q6, asked properly this time. **Resolved:** both capabilities ship (copy-paste always generated; auto-post opt-in via `policy.jira_comment: "auto-post"`, default `"off"`) — closes Q6. Also disclosed and resolved the ≤15 cumulative-question cap (A-16) that had been picked without asking — user dropped it, no cumulative cap. |
| 2026-09-28 | Second gap check, requested by user | User asked a second time whether Part 1 had loose ends and asked for a full re-read scoped to the Reviewer, not a re-check of the existing summary. Read every Marek Reviewer-side file and all of `TestabilityScanner.MD` line by line. Found three real conflicts the first pass missed entirely or parked in the persona table without a ruling: **P10's Jira-outage conflict** (never converted from the persona table into a decision — resolved: split by total-outage-with/without-fallback vs partial-failure-mid-gather), **screenshot binaries reaching the model** (K&A reads image bytes via vision; Marek's checklist 8.3 implies binaries should never reach the LLM — resolved: allow vision, reinterpret 8.3 as an output-redaction rule), and **bundle richness / `template_compliance` scope** (does the Reviewer enforce all 17 `requirements-template.md` sections or only the review-relevant ones — resolved: narrow scope, richer sections are the Creator's problem). All three confirmed as proposed. Also corrected RV3's "~12–14 items" estimate to "~16–18" after actually comparing the two lists — Marek's are structural, K&A's are behavioural, they don't fully overlap. |
| 2026-09-28 | Live-usage bug report, fixed | User reported the Epic-mode child inventory wasn't recursively reading children — only key/summary/status was ever fetched, even though B12's wording already implied description content. Traced to the workflow text never actually instructing a `description` fetch for children. **Fixed as C4**: the same paginated inventory call now also requests each child's `description` (no extra round trip); when empty, falls back to the child's summary/name as a lower-confidence signal, recorded per child as `content_source` and barred from marking B12 COVERED alone (extends A-17 to the Epic's own children). Updated `SKILL.md` §6, `checklist.md` B12, `reference.md`'s Epic finding patterns/limits table, the schema's `epic_child_inventory` items, `sample-report-epic.html`, `MANUAL.md` §7, and `examples.md` Example 4 to match. |
