# The Reviewer — unified review checklist

**Version:** 1.1 · **Owner:** Marek Wyszyński (skill maintainer, persona P5) until a formal owner is assigned · **Status:** append-only — when a criterion changes, add a dated note under it rather than rewriting it, and never renumber a `checklist_ref` that has already shipped.

This checklist merges **Marek's `requirement_standard.md`** (9 sections, structural/document quality) and **Karolina & Agata's `story-testability`** (12 gap dimensions, behavioural coverage) into one numbered list, per decision **RV3** in [`DECISIONS.md`](DECISIONS.md). Every finding The Reviewer emits carries a `checklist_ref` pointing at exactly one row below — there is no second checklist to cross-reference.

The two groups stay labelled because they check different things, not because they're two layers: **Group A** asks "is this requirement document well-formed?"; **Group B** asks "does its content cover these behavioural topics?" A requirement can pass every Group A row and still fail most of Group B (a beautifully structured story that never mentions error handling), and vice versa (a messy paragraph that happens to cover every edge case).

**Scope note:** this checklist covers what **The Reviewer** itself enforces — the review-relevant subset of the requirement. It deliberately does **not** enforce the fuller `requirements-template.md` bundle (personas, fixtures, API/UI detail beyond presence, dependencies, glossary) — those sections exist to feed **The Creator**'s test generation and their absence is not a Reviewer finding. See `DECISIONS.md` → "bundle richness" resolution.

---

## Group A — Structural and documentation quality

Adapted from `requirement_standard.md`. Applies to Story, Bug, Task, and Epic alike, with the exceptions noted per row (per decision D8: never silently treat a non-Story type as a Story).

| Ref | Criterion | COVERED when | Severity if failed |
|-----|-----------|--------------|---------------------|
| **A1** | **Identity and issue type** | `jira_key` resolves to a real, accessible issue; the issue type (Story/Bug/Task/Epic) is read and the correct workflow branch is used — Epic → Epic scan mode; Bug/Task → Story workflow with the type name substituted and AC-gap checks skipped unless an AC-equivalent field exists | CRITICAL if the key doesn't resolve; MEDIUM if the type is ambiguous or misrouted |
| **A2** | **Summary and description** | Summary describes a user-visible outcome; description (or summary, if description is genuinely thin) explains context, actor, and desired outcome; description does not contradict the acceptance criteria; an explicit **out of scope** note exists when the change touches shared systems | CRITICAL if both summary and description are empty or contradict the AC; HIGH if summary is missing; HIGH if out-of-scope is missing on a shared-system change |
| **A3** | **Acceptance criteria exist and are testable** | At least one AC item exists; each is **atomic** (one verifiable behaviour), **testable** (observable pass/fail without inventing behaviour), and **concrete** (no vague terms — see Ambiguity detection below); when AC appears in two places, resolve by precedence: AC custom field → AC bullets in description → explicit "AC template empty — no story-specific criteria" → unavailable (decision D19) | CRITICAL if no AC and no equivalent exists anywhere; CRITICAL if an AC item is present but not testable; HIGH if an AC item is vague, non-atomic, or duplicated |
| **A4** | **Scope stated and non-contradictory** | In-scope and out-of-scope are both named for complex features; neither contradicts the AC or description | CRITICAL on contradiction; HIGH if missing on a complex feature |
| **A5** | **Traceability** | Parent Epic is linked when the work item is a Story/Bug/Task; a design reference (Figma or spec link) is present when the AC implies UI validation — presence alone is the check here, ingest of the linked design happens under A8/B-ingest rules | HIGH if either is missing when implied |
| **A6** | **Open questions and assumptions** | No `open_questions` with `blocking: true` remain unanswered; material assumptions that affect test validity are stated explicitly, not left implicit | CRITICAL if a blocking open question is unresolved; HIGH for an unflagged material assumption |
| **A7** | **Data sensitivity** | No live secrets, API keys, or production credentials appear in analyzed text; PII visible in examples, screenshots, or spreadsheet pastes is not quoted verbatim into the report (redaction is a **display-time** rule — reading a screenshot with vision to find text is allowed; the redaction happens before that text reaches `excerpt_quote` or any rendered output, not before the model looks at the image) | CRITICAL for live secrets/credentials; HIGH for unredacted PII in output |
| **A8** | **Source completeness (review-relevant subset only)** | `work_item`, `description`, `acceptance_criteria`, `scope`, testability *signals* (environment/data/API/UI **named**, not fully detailed), `traceability`, `open_questions`, and `data_sensitivity` are each present or explicitly stated as unavailable/`N/A` with a reason. A linked Confluence page is fetched (decision R-G2) and its absence-of-fetch is never silent; a linked PDF or other non-Confluence document is reported as "linked but not fetched" rather than skipped without comment | MEDIUM per missing/unexplained section; HIGH if a linked Confluence page that plausibly holds the AC was not fetched |

**Note (2026-09-29, PRF-12) — Epic scope:** every "CRITICAL" in the severity column above reads as **HIGH** when the target is an Epic. Epics never block The Creator; blocking happens only on each child's own scan. `checklist_ref`s are unchanged. `A7`'s redaction rule and `Security` routing apply in full regardless of the cap.

**Note (2026-09-29, zero-child Epic):** when the paginated child inventory is **empty**, **B12** per-child alignment is **N/A** — there is nothing to compare. Still raise **B12** at **HIGH** when the Epic (or a linked PRD) describes deliverable work but **no child owns any part of the journey** (zero children in Jira). Do not treat an empty inventory alone as COVERED for B12.

### Ambiguity detection (feeds A3)

Flag vague terms as a finding, not as a rewrite: `natural order`, `appropriate`, `fast`, `soon`, `works correctly`, `etc.`, `as usual`, `similar to before`, and equivalents. Finding text: `Term "{term}" is ambiguous — pass criteria cannot be defined without clarification.`

---

## Group B — Behavioural coverage

Adopted from K&A's 12 gap dimensions, unchanged in substance. Run against whichever of AC / description / comments / linked design is available. **Never invent an answer** — each dimension is either **COVERED** (with `*(Source: …)*`) or a **GAP** (a bullet in "Not stated in story" and/or a finding).

| Ref | Dimension | COVERED when | Typical GAP |
|-----|-----------|--------------|-------------|
| **B1** | Happy path | Expected success behaviour is stated | Main outcome undefined |
| **B2** | Negative paths | Failure/rejection cases are mentioned | Invalid input, denied access not described |
| **B3** | Boundaries | Limits, min/max, empty state, max items are stated | Sort order, pagination, empty state absent |
| **B4** | Error / failure handling | Error messages, fallback, timeout are mentioned | Service down, validation errors absent |
| **B5** | Roles / permissions | Who can/cannot use the feature is stated | Role matrix, guest vs admin absent |
| **B6** | Data | Inputs, outputs, persistence, formats are stated | Field mapping, ID format, audit absent |
| **B7** | Integrations | External systems/APIs are named with expected interaction | Contract, sync direction absent |
| **B8** | States / transitions | Lifecycle (e.g. draft → published) is described | Toggle persistence, undo absent |
| **B9** | NFR | Performance, accessibility, i18n, or security is **addressed at all** — not itemised across every category (narrow scope, see header note) | Load time, locale, WCAG entirely unaddressed |
| **B10** | Test data / environment | Environment, fixtures, or seed data are mentioned | Staging flag, test account absent |
| **B11** | Observability | Logging, metrics, or audit are mentioned | Support/debug signals absent |
| **B12** | Epic consistency | **Story scope:** epic facts align with story facts (factual diff only — cite both sources). **Epic scope:** renamed **child ↔ epic alignment**: terms in epic goal vs **each child's description**, fetched for every child in the same paginated inventory call as `key`/`summary`/`status` (decision C4 — no extra round trip); when a child's description is empty, fall back to its summary for a lower-confidence keyword-overlap signal only — a title-only fallback never marks this row COVERED by itself (A-17 applies to an Epic's own children, not only Story-scope siblings); empty-description children vs an active epic is named as its own GAP pattern regardless | Same term used differently between epic and story; end-to-end journey step not owned by any child (do not assign it); a child counted only via `content_source: title_only` |

**Severity for a Group B GAP → finding:** **HIGH** if it blocks defining pass criteria or the primary test scope; **MEDIUM** if it affects edge/regression/integration scope but the core path stays testable; **LOW** if it's a nice-to-have clarity improvement.

**Do not, for Group B:**
- Generate test steps or expected results during the review — that is The Creator's job.
- Fill a GAP with "typical" or industry-default behaviour.
- Use sibling or epic **titles alone** to mark a dimension COVERED — sibling/epic **acceptance criteria or explicit description text** can (decision A-17); a title cannot.
- Express any dimension as a percentage or score (decision D12/A-13 — raw counts are fine, derived numbers are payload-only).

---

## Group C — Epic delivery (Epic scope only)

Added 2026-09-29 (PRF-19). These rows check things only an Epic carries: how the feature reaches users and whether its delivery was verified. They are **never** raised in Story/Bug/Task scope. Category is always `epic_lifecycle`. Severities are already within the Epic cap (PRF-12).

| Ref | Criterion | COVERED when | Severity if failed |
|-----|-----------|--------------|---------------------|
| **C1** | **Rollout / feature-flag plan** | The epic or a child names how the feature is released: a feature flag (name, default, who flips it), a staged/percentage rollout, or an explicit "released to everyone at once" | MEDIUM when missing; HIGH when `scope.lifecycle` is `post_delivery` and a flag is mentioned but its state or owner is not |
| **C2** | **Verification evidence** | Post-delivery only: a testing child, QA acceptance record, or linked Xray execution shows what was verified, and any skipped or deferred path is named with where it will be covered | HIGH when a testing child is Canceled or a verification record states a skipped path with no replacement; MEDIUM when no verification evidence exists at all. Not evaluated (`N/A`) when `pre_delivery` |
| **C3** | **Tracking-field consistency** | Epic status, fix versions, and child statuses tell the same story (e.g. the epic isn't In Progress with every child Done, fix versions match the children) | LOW at most — a hygiene signal, never a question unless it hides a real scope gap |

---

## Question linkage (both groups)

- A HIGH finding → a finding row **and** a clarification question (if a PM/dev can plausibly answer it).
- A MEDIUM finding → a finding row; a question only if the scope is still outlineable without one.
- A LOW finding → "Not stated in story" only; a question only if there's user-facing impact.

## Traceability

- Every checklist row cited in a finding uses its `checklist_ref` (`A1`–`A8`, `B1`–`B12`, `C1`–`C3`) — never a free-text description of the rule.
- A question's `unblocks` field names the finding id(s) and/or checklist row(s) it resolves.
- On rescan, a finding is marked **Resolved** or remains **Open** against the same `checklist_ref` — the ref never changes across rescans of the same issue.

---

## Change log

| Date | Change |
|------|--------|
| 2026-09-28 | v1.0 — initial merge of `requirement_standard.md` (9 sections / 33 sub-criteria, consolidated to A1–A8) and `TestabilityScanner.MD`'s 12 dimensions (B1–B12), per `DECISIONS.md` RV3 and the "bundle richness" and "second-pass findings" resolutions. |
| 2026-09-28 | B12 (Epic scope) sharpened per `DECISIONS.md` C4: the epic-scope alignment check now runs against each child's actual `description` (fetched in the same paginated inventory call, not title/status only), with a title-only fallback when a child's description is empty — never sufficient alone to mark the row COVERED. `checklist_ref` unchanged. |
| 2026-09-29 | Group A severities capped at HIGH in Epic scope (PRF-12 — Epics never block). No row renumbered. |
| 2026-09-29 | v1.1 — Group C added (C1 rollout plan, C2 verification evidence, C3 tracking-field consistency), Epic scope only, category `epic_lifecycle` (PRF-19). No existing row renumbered. |
