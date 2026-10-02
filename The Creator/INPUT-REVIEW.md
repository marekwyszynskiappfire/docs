# `Input/` review — requirements review and test case creation

**Status:** Phase 1 inventory review, for discussion
**Date:** 2026-09-28
**Reviewer:** agent-assisted read of every file under `The Creator/Input/`
**Feeds:** [working-plan.md](working-plan.md) Phase 1 port checklist · [DECISIONS.md](DECISIONS.md) C1–C3
**Resolved:** every Part 1 (requirements review) item below has a ruling in [The Reviewer/DECISIONS.md](../The%20Reviewer/DECISIONS.md) → "Reviewer resolutions — Part 1". Part 2 (test case creation): file-level inventory below; **persona synthesis and action agenda:** [CREATOR-SKILLS-PERSONA-REVIEW.md](CREATOR-SKILLS-PERSONA-REVIEW.md); execution: [ACTION-PLAN.md](ACTION-PLAN.md).

---

## Scope and method

Every file under `The Creator/Input/` was read in full: 33 files across three contributions, roughly 8,400 lines. Nothing was skipped, including schemas, templates, samples, the Python import script, and the HTML guide. Statements below cite the file they come from; where a contribution contradicts itself, both locations are named.

The review is split as requested into **Part 1 — requirements review** and **Part 2 — test case creation**. Assets that serve both (the Agent Skills Specification, the Jira/Xray mapping config, `requirements-template.md`) are discussed in whichever part they materially affect, and cross-referenced from the other.

### Inventory

| Contribution | Requirements-review side | Test-case side | Shared / supporting |
|---|---|---|---|
| **Marek** (`Input/Marek/`) | `requirements-review/` (SKILL, reference, examples), `_shared/templates/requirement_standard.md`, `_shared/templates/review_findings.schema.json` | `test-case-creation/` (SKILL, reference, README, examples, coverage-catalog, 4 templates), `_shared/schemas/TestCaseDraft.schema.json`, `_shared/golden/v1/` (style-rules + 2 examples), `_shared/scripts/xray_graphql_import.py` | `_shared/Agent Skills Specification.md`, `_shared/requirements-template.md`, `_shared/config/jira_xray_mapping.json`, `_shared/skills-hub-README.md` |
| **Kacper** (`Input/Kacper/`) | *(none — see gap R-G1)* | `TestCaseWriting/SKILL.md`, `AutomatingTestCases/SKILL.md` | `SOURCE.md`, `skills-hub-README.md`, `skills-overview.html` |
| **Karolina & Agata** (`Input/Karolina&Agata/`) | `TestabilityScanner.MD` (`story-testability`) | `story-ui-test-cases-SKILL.md` | `NOTES.md` |

### Two corrections to the decision memory, established by this read

1. **`story-ui-test-cases` is no longer missing.** [DECISIONS.md](DECISIONS.md) C2 and C3 both record it as an absent dependency that two contributions point at. It is now present at `Input/Karolina&Agata/story-ui-test-cases-SKILL.md` and is reviewed in Part 2. Kacper's comparison table against it (TestCaseWriting, "Comparison note") turns out to be **accurate on all six rows** now that the file can be checked — which is a useful signal about how reliable Kacper's self-description is elsewhere.
2. **All three contributions forbid automated writes, not two.** C3 says "two of three contributions forbid automated writes". Marek's `test-case-creation` also states "Does **not** import to Xray" and its output checklist ends with "Did **not** run xray-import"; writing is delegated to a separate script/skill that was not contributed. So the conflict with decision D4 is three-for-three, not two-for-three, which strengthens the case for submission being opt-in and off by default.

### Personas

The four personas locked in D5 are used throughout. Reading the inputs surfaced six more roles that the source skills actually address or implicitly depend on. Not all should become first-class report views; the table marks what I think each is worth.

| # | Persona | Status | Why the inputs force it | Recommendation |
|---|---|---|---|---|
| P1 | QA engineer | Existing (D5) | Primary operator of all five skills | Keep as primary |
| P2 | QA lead / manager | Existing (D5) | Marek's `execution_plan`, minimum release gate, tier counts | Keep |
| P3 | Product manager / BA | Existing (D5) | Marek's `question_for_PM`, K&A's clarification questions and Jira comment templates | Keep |
| P4 | Automation engineer | Existing (D5) | Kacper's `AutomatingTestCases` is an entire skill for this persona; K&A's E2E candidates table | **Promote from Phase 5.** Kacper's contribution is half automation-facing; deferring this persona means deferring half of one contribution |
| P5 | Skill maintainer / consolidation owner | **New** | Nobody is served by 8,400 lines of overlapping rules. This is the persona that needs the port checklist, the conflict register, and versioned checklists | Add as a documentation audience, not a report view |
| P6 | Test-data / environment steward | **New** | Kacper's parallel-worker date isolation, one shared E2E user, tenant seed state, `parallelTestDateIsolation.ts` registry. Cross-test interference is owned by someone, and no skill names them | Add; needs a config hook (see T-G6) |
| P7 | UX designer | **New** | Both K&A skills quote Figma strings verbatim and raise story-vs-design mismatches as findings. The designer answers those `Q#`, but no output section is addressed to them | Add as a recipient of a filtered view; cheap given the persona selector |
| P8 | Release / delivery manager | **New** | K&A's epic mode produces child inventory, status mix, rollout themes and explicitly targets "release / initiative test planning". Marek's minimum-release-gate line is the same reader | Add; largely overlaps P2 but the epic view is distinct |
| P9 | Security / compliance reviewer | **New** | Marek's `data_sensitivity` CRITICAL and redaction pass produce findings only this persona can action — and Kacper *mandates* real account emails inline in test steps. The tension needs an owner | Add as a policy owner, not a report view |
| P10 | Platform / MCP administrator | **New** | Every skill degrades on missing MCP; K&A's "Data sources unavailable" block with per-step reasons is, functionally, a ticket addressed to this persona | Add as the audience of the context/diagnostics section |

---

# Part 1 — Requirements review

Two contributions are in scope: **Marek's `requirements-review`** (plus `requirement_standard.md`, `review_findings.schema.json`, and the bundle shape in `requirements-template.md`) and **Karolina & Agata's `story-testability`**. Kacper contributed nothing here, which is itself a finding.

## 1.1 What each contributes, in one paragraph

**Marek's `requirements-review`** is a checklist-driven, artifact-producing gate. It normalizes Jira issues into a bundle shape, walks nine numbered checklist sections, emits findings with `CRITICAL/HIGH/MEDIUM/LOW` severities and a `checklist_ref`, writes a schema-validated JSON plus a Markdown report into `artifacts/{run_id}/`, and ends with a `PASS / PASS_WITH_WARNINGS / BLOCKED` gate that hard-blocks `test-case-creation` on any CRITICAL unless `force=true` is confirmed in chat.

**K&A's `story-testability`** is a 1,442-line single-file skill for shift-left analysis. It gathers ten source types read-only (issue, AC field, all comments, parent epic, siblings, links, subtasks, spreadsheets, screenshots, Figma), runs a twelve-dimension gap sweep marking each COVERED-with-source or GAP, emits `F#` findings and `Q#` questions under strict volume limits, classifies testability / scope confidence / risk / automation candidate / readiness, supports a rescan delta that marks each `F#` Resolved or Open, and renders a three-tier HTML report. It is deliberately advisory: the words "gate", "Not ready" and "Blocked by QA" are on a blocked-phrases list.

## 1.2 Similarities

These are the rules both encode independently, and they are the safest candidates for the merged Reviewer because two teams converged on them.

1. **Read-only on Jira.** Neither edits the requirement. Both allow a Jira comment only as a copy-paste or opt-in step, never as an automatic write.
2. **Verbatim-quote grounding.** Marek requires `excerpt_quote` to be "**verbatim** from the bundle — never paraphrase as a quote". K&A requires `*(Source: …)*` on every fact bullet. Same anti-hallucination mechanism, different syntax.
3. **Absence is reported, never filled.** Marek: "Do not invent product behaviour; ask PM via `question_for_PM`." K&A: "If not in story → **Not stated in story** (not an assumption bullet)."
4. **A question-to-a-human is a first-class output**, separate from the finding: `question_for_PM` vs the `Q#` block with Context / Source / Priority / Unblocks.
5. **Stable finding identifiers** — `RR-{KEY}-{NN}` vs `F#` — with the intent that they survive into downstream conversation.
6. **Checklist-driven sweep**, so coverage of the review itself is deterministic: nine numbered sections vs twelve numbered dimensions.
7. **Severity-graded findings** with the severity meaning "how much this blocks test planning", not "how bad the bug is".
8. **An explicit downstream handoff** and a refusal to do test design: Marek's "Does not generate tests"; K&A's "**Do not** include UI test case drafts — use `@story-ui-test-cases`".
9. **Both handle Epic scope as a distinct thing**, not just a bigger Story — Marek via child-story fetch plus a `rollup` with `recommended_pm_order`, K&A via a dedicated Epic scan mode with its own template and gap interpretation.
10. **Both degrade rather than abort on a partial source failure.** Marek: per-key `errors[]`, continue the batch. K&A: record the failed step in "Data sources unavailable" with the reason, continue gather.
11. **Both ship a pre-output validation checklist** the agent must self-run.
12. **Same Atlassian MCP surface and the same epic JQL** (`"Epic Link" = {KEY}`, with K&A adding a `parent = {KEY}` fallback that Marek lacks).
13. **Both end with explicit "what this skill does NOT do"**, which is a good discipline to carry into the merged skill.

## 1.3 Differences

| # | Dimension | Marek `requirements-review` | K&A `story-testability` | Reconcilable? |
|---|---|---|---|---|
| D1 | Output contract | Schema-validated JSON **plus** Markdown, written to disk under `artifacts/{run_id}/` | Markdown in chat; optional HTML; Jira wiki-markup comment. **No machine-readable payload at all** | Yes — adopt Marek's payload, K&A's presentation |
| D2 | Verdict semantics | Hard gate: `PASS / PASS_WITH_WARNINGS / BLOCKED`, `blocks_test_generation`, `force` override | Advisory readiness: `Ready with clarifications / Needs clarification before scope lock / Cannot plan scope yet`; "gate" is a **blocked word** | **No.** Political, not technical — see U-1 |
| D3 | Severity scale | 4 levels (CRITICAL/HIGH/MEDIUM/LOW) on one axis | 3 levels for findings (High/Medium/Low) **plus** 3 for questions (High/Medium/Optional) — two axes | Mappable, but no mapping exists yet (R-G5) |
| D4 | Volume control | None. Unbounded findings | Canonical limits table: ≤8 questions, ≤5 High, ≤15 if justified, ≤5 new per rescan, ≤25 siblings, ≤3 Figma frames, ≤50 checklist rows | Adopt K&A's — Marek has no answer to report bloat |
| D5 | Re-run after fix | None. Each run is a fresh `run_id` with no diff | Rescan delta marking each `F#` Resolved/Open, classification changes, ≤5 new questions, duplicate-request guard | Adopt K&A's, but see R-G3 |
| D6 | Input breadth | Jira fields, or a normalized YAML/MD bundle on disk | Jira + **all comments** + siblings + epic children + screenshots (text only) + Google Sheets (paste only, never auto-fetch) + Figma (≤3 nodes) | Union of both; note Marek has no screenshot/spreadsheet/sibling concept and K&A has no bundle-file concept |
| D7 | Figma | Presence of a design link is checklist criterion 6.2; **no fetching** in the review skill | Full ingest protocol: URL detection, `fileKey`/`nodeId` parsing with `-`→`:`, ≤3 `get_design_context` calls, mandatory `Source: Figma` labels, explicit "layout alone is not a rule" | Adopt K&A's wholesale |
| D8 | Issue types | `scope.type` enum is `epic / story / stories / jql / bundle`; checklist 1.3 marks a non-Story/Epic type a MEDIUM finding | Story / Bug / Task / Epic, with an explicit instruction not to silently treat non-Story types as Stories and to skip AC gaps when no AC-equivalent field exists | Adopt K&A's; Marek effectively penalises Bugs for being Bugs |
| D9 | Data sensitivity | Redaction pass, `document.redaction_applied`, `data_sensitivity` CRITICAL for secrets/PII | **Nothing.** No redaction, no PII rule — while ingesting screenshots and spreadsheets | Adopt Marek's; see R-G6 |
| D10 | Tone / politics | Neutral-technical; "BLOCKED" is the headline | Blocked-phrases list, collaborative framing, "supports shift-left preparation — it does not approve or reject the story" | Adopt K&A's tone layer; it has no counterpart in Marek |
| D11 | Classification outputs | Only gate status and severity counts | Five classifications: testability, test scope confidence, risk (+ rationale tags), automation candidate, readiness — each with a written decision tree | Adopt K&A's; Marek has no risk or automation concept at all |
| D12 | Numbers | Counts everywhere; `critical_unresolved_count` is a schema field | "Numeric scores / percentages / weighted totals in any output — **0, never**" | Partially — see A-13, the ban is narrower than it reads |
| D13 | Host / invocation | Cursor, `disable-model-invocation: true`, Atlassian MCP | Hive MCP execution contract (`run_skill` / `load_skill`, `result: "noop"` means execute, forbidden end states) **plus** Cursor | Extend D2 of the decision memory to three hosts |
| D14 | Report presentation | One flat Markdown template | Three-tier HTML: Tier 1 always visible, Tier 2 `<details open>`, Tier 3 `<details>`; fixed tier per section with empty-state rather than omission; item counts in every summary; KPI colour mapping | Adopt K&A's, minus the Tailwind CDN |
| D15 | Finding → checklist link | `checklist_ref` field pointing at a numbered criterion | Dimensions are numbered 1–12 but findings carry **no** dimension reference field | Adopt Marek's; it is needed to make coverage of the review auditable |
| D16 | Multi-item rollup | Cross-story rollup, common patterns, `recommended_pm_order` | No multi-story rollup for story scans (siblings are facts only); epic mode instead produces a child inventory, status mix, and a `recommendedBatchKeys` ≤8 batch handoff | Both, for different scopes |
| D17 | Checklist artifact | None | QA readiness checklist, auto-included at ≥3 testing-focus items, exportable as ≤50-row CSV, each row tied to Source / `F#` / `Pending Q#` | Adopt K&A's |
| D18 | Language | Unspecified for the review output | "English by default, **with no exceptions**", including translated variants keeping the blocked-phrase rules | Adopt K&A's |
| D19 | Precedence when AC lives in two places | Deferred: `requirements-template.md` §4 says "define once in your inventory and repeat that rule" — the rule is never defined | Concrete: AC field → AC bullets in description → "AC template empty — no story-specific criteria" → unavailable | Adopt K&A's; Marek deferred a question K&A answered |

## 1.4 Gaps

**R-G1 — No requirements-review practice from Kacper's side of the organisation.** The Timetracker pipeline has no requirement-quality step; its equivalent is a nine-item interrogation about identifiers ("Ask before drafting"). That means the merged Reviewer has zero evidence from a code-grounded, mature-automation context, and the risk is that it is designed entirely around requirements-as-documents when one of the three contributing teams treats code as the authority.

**R-G2 — No requirement source beyond Jira is actually resolvable.** K&A records "PRD/Confluence linked but not fetched" as an explicit Medium finding and treats "epic completion criteria only in linked PRD — body not analyzed" as High. Marek's review skill does not crawl links either; link-following exists only in `test-case-creation` §1 step 4. So for any requirement whose real content is in Confluence or a PDF, both reviewers produce a finding that says "we could not read the requirement" — which is honest but not useful. This is a structural blind spot, not a bug.

**R-G3 — Rescan has no persisted state.** K&A's delta mode depends on a prior scan "in this chat" and explicitly refuses to pretend otherwise. Once the merged Reviewer writes a payload, delta should diff payload-to-payload and work across sessions and across operators. Nothing in either input does this.

**R-G4 — Cross-session gate consumption is only half-solved.** Marek's JSON artifact is readable by a later session (good). K&A's readiness exists only in chat. The merged contract needs the gate/readiness to be a file, and needs to define what happens when the requirement changed after the payload was written (staleness).

**R-G5 — No severity mapping between the two scales.** Four levels versus three-plus-three. Nothing anywhere states whether K&A `F# High` equals Marek `CRITICAL` or `HIGH`. Since the gate keys off CRITICAL, this mapping *is* the gate, and it is currently undefined.

**R-G6 — No data-sensitivity rules on the new ingest paths.** Marek's redaction rules predate screenshot, spreadsheet and Figma ingest. K&A instructs the agent to quote exact strings read from screenshots and to paste spreadsheet rows into a checklist, with no rule against carrying customer names or account data into a report that is explicitly designed to be shared with people who have no repo access.

**R-G7 — No NFR criterion in Marek's checklist.** `requirement_standard.md` §5 Testability covers environment, data, API, UI, enumerations — but performance, accessibility, i18n and security appear only in `requirements-template.md` under `non_functional`, which the checklist never inspects. K&A's dimension 9 covers exactly this. Marek's reviewer will pass a story with no accessibility requirement and no performance budget without comment.

**R-G8 — Finding ownership is PM-only in Marek.** Every finding routes to `question_for_PM`. K&A's epic mode routes to "PO / UX / EM" and its recommended-next-action names suggested owners. Personas P7 (UX) and P8 (RM) have no route in Marek's model at all.

**R-G9 — Checklist governance is undefined.** `requirement_standard.md` is marked "Version 1.0" with no owner or change process; K&A's twelve dimensions are inline and unversioned. After the merge there will be two overlapping rule sets (nine sections and twelve dimensions) and no statement about whether they become one list, two layers, or a checklist plus heuristics.

**R-G10 — A referenced skill is still missing.** `story-epic-batch-orchestrator` is named four times in `TestabilityScanner.MD` as the thing that actually executes the epic batch, and it is not in `Input/`. The `story-ui-test-cases` gap closed; this one opened.

## 1.5 Ambiguities and internal inconsistencies

### Marek's contribution

| # | Location | Issue |
|---|---|---|
| A-1 | `requirements-review/SKILL.md` "Paths" table | Every path is hardcoded to one repo layout (`AI in QA/Skills/templates/…`). In the staged `Input/Marek/` layout every one of them is already wrong. This is the exact problem the working plan calls out, confirmed against the real input |
| A-2 | SKILL.md Paths vs `_shared/config/` | The skill loads `config/jira_xray_mapping.**yaml**`; the file that exists is `jira_xray_mapping.**json**`. Different name and different format |
| A-3 | SKILL.md §6 vs `reference.md` gate table | SKILL says "0 CRITICAL → PASS or PASS_WITH_WARNINGS" without distinguishing; reference says PASS requires 0 CRITICAL **and** 0 HIGH. `requirement_standard.md` "Gate rules (summary)" mentions neither PASS_WITH_WARNINGS nor the HIGH condition. Three statements of one rule, two of them incomplete |
| A-4 | `review_findings.schema.json` | `blocks_test_generation` is an unconstrained boolean on every finding, while the skill says it may be `true` **only** for CRITICAL. The schema cannot catch the violation it most cares about |
| A-5 | `review_findings.schema.json` | `requirement_keys` requires `minItems: 1` **and** matches `^[A-Z][A-Z0-9]+-[0-9]+$`. A review of a bundle or PDF with no Jira key cannot produce a schema-valid artifact, even though `scope.type: "bundle"` is an allowed scope |
| A-6 | SKILL.md §2 / `reference.md` redaction | "Apply redaction **before LLM analysis**" is not achievable in an agent-driven fetch — the agent *is* the model, and it has already read the raw Jira response by the time it could redact. As written the rule is unimplementable; it only works on the pre-supplied-bundle path |
| A-7 | `examples.md` Example 4 | Writes artifacts to `Skills/artifacts/2026-06-09-001/`, while SKILL.md mandates `AI in QA/Skills/artifacts/{run_id}/` |
| A-8 | `examples.md` Example 3 / schema | The force-override example never sets `force_override_by`, though the schema defines it and audit is the whole point of the field |
| A-9 | `Agent Skills Specification.md` §2.6 and §8 | Still lists "Confirm whether HIGH should hard-block" and nine other decisions as open, and states "**not yet implemented** as Cursor Skill files". The skills were implemented and the decision was made (CRITICAL-only). The spec shipped into `Input/` is stale relative to the skills shipped beside it |
| A-10 | `requirement_standard.md` links | Links to `../requirements-review/reference.md` and `../../requirements-template.md` resolve in the original repo, not in `Input/Marek/_shared/templates/`. `requirements-template.md` itself links to `01 - Requirement data discovery…` and `ai_test_creation.md`, neither of which was copied |

### K&A's contribution

| # | Location | Issue |
|---|---|---|
| A-11 | Scan output template, "Scoring rationale" | Instructs the agent to use "qualitative rules from **scoring-reference.md**" — an external file that does not exist, in a skill whose Platform note says "This file is **self-contained**. Do not expect companion `.md` or `.html` files" |
| A-12 | TC handoff block | Comment reads `Inner HTML for {{TC_HANDOFF_HTML}} in **html-report-template.html**` — a second reference to a companion file the same document says does not exist |
| A-13 | Limits table vs HTML spec | "Numeric scores / percentages / weighted totals in any output — 0, never" sits beside a mandatory Tier 1 line reading "3 findings — 2 High, 1 Medium · 2 open questions", a children summary bar of counts, and "an item count in every `<summary>`". The intended distinction is *derived scores* versus *raw counts*, but the skill never says so, and a literal reader would flag its own template. This also means [DECISIONS.md](DECISIONS.md) C3 point 2 overstates the conflict: counts are fine, only the computed coverage percentage is at stake |
| A-14 | Limits table vs epic output template | Limits say epic children must "paginate until `isLast`; **full inventory required**"; the epic template renders "_Sample: {n} issues … truncated: yes/no_" and "**Status mix (sample)**". Full inventory and sample are asserted in the same skill |
| A-15 | Severity model "Readiness mapping" vs Scoring "Readiness for test planning" | Two definitions of the same value. One says *Ready with clarifications* = "No High findings on dimensions 1–6; **Optional questions only**"; the other says "Testability High or Medium; no High findings on core behavior; **Optional/Medium** questions only". Medium questions are disqualifying in one and permitted in the other |
| A-16 | Question limits | "≤8 default, ≤5 High" for a scan, "≤5 new" per rescan. Whether the cumulative total across rescans may exceed 8 is unstated — and after three rescans it certainly will |
| A-17 | Gap heuristics "Do not" vs dimension 12 | "Do not use sibling epic titles to mark dimensions COVERED", yet dimension 12 is *Epic consistency*, whose only evidence is epic and sibling text. The dimension can apparently never be COVERED |
| A-18 | Scoring → Automation candidate | "Suggested approach must match evidence: UI verbs → **Playwright UI E2E only**". A specific automation stack is hardcoded into a skill that is otherwise product-agnostic |
| A-19 | Scope note vs templates | Bug/Task handling is specified in prose ("replace 'story' with the actual issue type", skip AC gaps) but no Bug/Task output template exists, and the validation checklist still requires the Story sections |
| A-20 | HTML export | "Use **Tailwind CDN or simple semantic HTML**", but the entire colour specification is Tailwind utility classes (`bg-emerald-500`, `text-rose-600`). The semantic-HTML branch has no visual specification at all — and the CDN branch breaks D1's self-containment |
| A-21 | Provenance | `NOTES.md` records "Provenance: Not recorded — source repo/path unknown". Unlike Kacper's contribution there is no commit, branch, or path, so there is no way to check for a newer version or identify the owner |

## 1.6 Uncertainties

These are open questions, not defects — they cannot be resolved by reading the files.

- **U-1 — Advisory or authoritative?** Whether QA tooling may tell a team it cannot proceed. Marek's skill hard-blocks; K&A forbids the vocabulary of blocking. D8 currently sides with Marek by having been decided first. This single question determines the Reviewer's verdict model, the Creator's precondition, and the tone of the whole report, and it should be ruled on explicitly rather than inherited.
- **U-2 — Is Hive a supported host?** K&A's execution contract is substantial (the `result: "noop"` rule in particular). If Hive is in production use, D2's two-host matrix is wrong.
- **U-3 — Does the merged Reviewer support Bug and Task?** K&A does; Marek's schema enum does not.
- **U-4 — Does the AC custom field ID vary per project?** Both skills punt: Marek says "ask the user which field holds acceptance criteria"; K&A says "request project AC field(s) via MCP (custom field names vary)". Whether the per-product config can pin this, or whether discovery is needed per project, is unknown.
- **U-5 — One checklist or two layers?** Nine checklist sections and twelve gap dimensions overlap heavily but not cleanly (testability splits across both; NFR exists only in one; data sensitivity only in the other).
- **U-6 — Is epic batch mode in v1?** It is a well-developed feature in K&A, entirely absent from the plan's single-issue payload contracts, and retrofitting it later means changing the schema.
- **U-7 — Who receives the report?** Open question Q7 in the decision memory, but it is more pressing here than for the Creator, because the Reviewer's primary audience (P3, the PM) is the persona least likely to have repo access.
- **U-8 — Is the rescan baseline the payload or the Jira issue?** If a requirement changes without a rescan, nothing detects it.

---

# Part 2 — Test case creation

Three contributions: **Marek's `test-case-creation`** (with golden library, `TestCaseDraft` schema, coverage catalog, templates, and the GraphQL import script), **Kacper's `TestCaseWriting`** (with `AutomatingTestCases` downstream), and **K&A's `story-ui-test-cases`**.

## 2.1 What each contributes, in one paragraph

**Marek's `test-case-creation`** generates a structured suite from approved requirements. It is assessment-first (it publishes a plan justifying suite size before writing anything), enforces per-test `execution_tier` P0–P3 with a `customer_impact` sentence, `test_data_required` plus `test_data_prerequisites`, `journey` versus `atomic` patterns capped at 15 steps, and a `CAT-*` coverage checklist with a 100% accounting rule. Output is one Markdown file containing traceability tables, a coverage report, an execution plan with hour estimates, and an appendix holding the full `TestCaseDraftBatch` JSON.

**Kacper's `TestCaseWriting`** drafts Timetracker manual UI cases in a strict Action / Data / Expected Result shape for a three-column Xray CSV, with a separate plain-text Jira Description block for global preconditions. Its distinguishing features are an authority order that puts current product code and live UI above repo examples, a binary `Final draft` / `Preliminary draft` status keyed on code verification, a nine-item blocking interrogation before drafting, and the strictest identifier discipline in the whole input set: never invent or borrow `TTQA-*`, `KAN-*`, `SUG-*`, or users.

**K&A's `story-ui-test-cases`** is the downstream half of `story-testability`. It requires a prior scan in the same chat, derives each TC's priority from the severity of the finding it traces to, links every assumption to a `Q#` or `F#`, preserves `TC-0N` ids across regeneration, and prefers verbatim Figma strings from the scan as expected values. It refuses to generate a TC table for API-only stories and refuses to produce one merged table for an epic.

## 2.2 Similarities

1. **None of the three writes to Xray or Jira.** Marek: "Does not import to Xray"; Kacper: "Blocked actions: auto-create or auto-import … claiming 'tests saved to XRay'"; K&A: "**No changes are made in XRay or Jira**". Unanimous, and it contradicts D4.
2. **All three produce a copy/import-compatible artifact** rather than an API call.
3. **All three carry an explicit draft-quality label** the reader must see before trusting the output.
4. **All three have an assumptions escape hatch** rather than allowing invention: `generation_notes` plus warnings and `{PLACEHOLDER}` values; "Open assumptions"; "Open assumptions" linked to `Q#`/`F#`.
5. **All three forbid fabricated behaviour** — "If spec TBD … do not fabricate"; "Invented business rules without assumption label" is an anti-pattern; "Do **not** invent business rules — mark as assumption with Q# / F#".
6. **All three require observable expected results** and name vagueness as a defect ("Verify it works" is forbidden; "Vague expected results on system messages"; "Observable steps and expected results — no hidden state").
7. **All three separate automation candidates from manual cases** into their own list, and all three refuse to export automation rows as manual steps by default.
8. **All three keep preconditions out of the step list** — though they put them in three different places (see D27 below).
9. **All three ship an anti-pattern list and a human review checklist** to be run before anything reaches Jira.
10. **Kacper and K&A agree on suite size to the number**: 5–15 manual cases, 2–5 E2E candidates, skip the E2E section if none qualify. Identical phrasing suggests common ancestry. Marek deliberately refuses a fixed number and derives it from the requirement set instead.
11. **Kacper and K&A use the same two-value status vocabulary** (`Final draft` / `Preliminary draft`) with different trigger conditions — Kacper keys on code verification, K&A keys on whether any High `F#`/`Q#` is still open.

## 2.3 Differences

| # | Dimension | Marek | Kacper | K&A |
|---|---|---|---|---|
| D20 | Precondition to run | Requirements-review JSON optional but "highly encouraged"; missing review never blocks | Nine-item interrogation on identifiers; blocks on missing Summary / `TTQA-*` / issue key+summary+id | **Mandatory** prior `@story-testability` scan in the same chat |
| D21 | Primary output | One Markdown file with a `TestCaseDraftBatch` JSON appendix | Markdown tables + a 3-column CSV per test + a separate plain-text Jira Description block | Markdown tables + an optional 5-column CSV |
| D22 | CSV contract | None directly; the script maps to Xray GraphQL `createTest` with `action`/`data`/`result` | `Action, Data, Expected Result` — exactly three columns, no key, no scenario | `Test Type, Test Summary, Test Step, Expected Result, Priority` — five columns, one row per step |
| D23 | Step data model | Object with `step` / `expected_result` / `test_data` — structurally identical to Kacper's three columns | Three columns; **every step must be runnable from its own Data cell**; `see Description` banned | One `Steps` cell holding `1. …<br>2. …` and **one** `Expected` for the whole case — no per-step data |
| D24 | Test identifiers | `TC-001` draft ids plus `CAT-*` catalog ids | Summary is the primary id; `TTQA-*` only when the user supplies it; "**Never use internal labels like `TC-01`**" | `TC-01` / `E2E-01` **mandatory**, with an explicit ID-stability rule across regeneration |
| D25 | Prioritisation | `execution_tier` P0–P3 + `customer_impact` + `deferrable` + `deferrable_rationale` | None. Risk is expressed by coverage layering, not per-case | `Priority` High/Medium/Low, **derived** from the severity of the linked `F#`, defaulting to Medium (or High if story risk is High) |
| D26 | Coverage model | `CAT-*` checklist with 100% accounting (`Covered / UNCOVERED / PARTIAL / N/A`), an AC matrix, and `catalog_coverage_pct` | Risk layering: access → platform shell → domain happy path → domain edges → regression, with "platform shell once per surface" | The scan's twelve `F#` dimensions; if >15 TCs would be needed, group by dimension and generate the High-linked groups first |
| D27 | Where preconditions live | Per-test `preconditions` field plus `test_data_prerequisites` | Jira **Description** block, bullet lists only — "**do not** use pipe tables; Jira Description breaks column alignment" | A `Preconditions` column, populated from scan facts or `Pending Q#` |
| D28 | Grounding authority | Requirements + user `external_context` + Jira link crawl + optional Xray extract. **No code reading** | Approved Jira steps → **current product code and live UI** → repo examples. Code grounding is required for `Final draft` | Scan facts and Figma observations only. **No code reading** |
| D29 | Test data discipline | Boolean + prose prerequisites per test, with a pattern table mapping scenario type to expected value | Deepest in the set: inline seed on every step, named periods (`month1: A month where no actions took place`), strict relative date labels (`10 weeks in the future`), canonical E2E emails, per-`TTQA-*` date isolation bands, never invent `KAN-*` | Preconditions from scan facts only, or `Pending Q#` |
| D30 | Effort model | Per-tier hour estimates, `minimum_release_gate`, `time_boxed_release` | None | None |
| D31 | Duplicate handling | `possible_duplicate_of` from an Xray extract or MCP search | A human-checklist item ("No duplicate cases that differ only by one filter value") | A duplicate-*request* guard: do not silently regenerate when the scan is unchanged |
| D32 | Automation handoff | Out of scope | A full downstream skill with seven required inputs, a Jira↔Playwright mapping, `testStep` literal rules, timezone/seed rules, and a reuse-before-create protocol | A candidates table with "Suggested level: Playwright UI" |
| D33 | Epic semantics | One merged suite anchored to the primary Epic key | Not addressed (works at feature-slice level) | **Explicitly forbidden**: "Do not generate a single merged TC table for the whole epic" — one Preliminary draft per child instead |
| D34 | Non-UI scope | Generates API tests (`CAT-API-*`), CSV import/export, feature flags, telemetry | "API/backend-only change → **No** UI TC table — bullets only" | "API/backend only → **Do not** generate TC table — testing focus + recommended areas only" |
| D35 | Max steps | Hard cap **15** for journey and atomic alike, stated in SKILL, reference, and style-rules | No cap; "30-step mega cases" is listed as an anti-pattern | No cap |
| D36 | Roles | `role` is a required schema field on every test | Users are concrete aliases with real E2E emails, not role codes | No role concept |
| D37 | Figma | `link-only` by default; journeys should name screens in expected results | None — code is truth | Reuse the scan's quoted strings as expected values; **do not** re-fetch Figma; tag rows `per Figma — {url}, node {nodeId}` |
| D38 | Regeneration | No concept | No concept | ID stability rule plus a note of which ids were updated in place versus newly added, "so a user who already copied IDs into XRay isn't silently desynced" |
| D39 | Output language | English "unless requirement specifies otherwise" | Unspecified | English, no exceptions |
| D40 | Model invocation | `disable-model-invocation: true` | **`false`** on both Kacper skills | `true` |

### The three head-on conflicts

- **Identifiers (D24).** Kacper forbids precisely the `TC-01` scheme that K&A mandates and Marek uses. This is not a style preference on Kacper's side — the rule exists because an invented id gets copied into Jira and then into `jiraIssueIds.json`. The merged payload needs a stable internal id *and* a rule that it must never be presented as a Jira/Xray key.
- **Step shape (D23).** Marek's and Kacper's shapes are isomorphic. K&A's is strictly less granular: one expected result per case, no per-step data. Converting K&A → the others is lossy in the wrong direction (it requires inventing per-step expected results), and K&A's own CSV block already has this problem (see A-30).
- **Epic scope (D33).** Marek produces one suite for the Epic; K&A forbids exactly that. The payload contract must carry a scope discriminator, and the plan currently assumes single-issue scope throughout.

## 2.4 Gaps

**T-G1 — Nothing supports updating an existing test.** All three skills are create-oriented, and `xray_graphql_import.py` implements only the `createTest` mutation — there is no update path, no fingerprint, and no search-before-create. The working plan's Phase 4 fingerprint-based upsert ("a re-run after partial failure does not duplicate") has no foundation in the contributed code. Re-running the current script would create duplicates.

**T-G2 — The script imports one test at a time.** `--batch` plus `--draft-id` is required and `main()` resolves exactly one test; there is no loop, no partial-failure policy, and no batch report despite `--batch` naming a batch file. The "continue-and-report" behaviour in the plan does not exist yet.

**T-G3 — No mapping between the three quality axes.** P0–P3 measures execution importance; `Final`/`Preliminary` measures grounding confidence; K&A's derived High/Medium/Low measures traceability to an open finding. They are three different things and no contribution has more than one of them. The merged payload probably needs all three as independent fields, which nobody has designed.

**T-G4 — No obsolescence rule.** When a requirement changes and a test no longer applies, no contribution says what happens. K&A gets closest with ID stability across regeneration, but says nothing about removal.

**T-G5 — No NFR or accessibility test generation anywhere.** K&A's *scan* has dimension 9 for NFR, but its TC skill produces none; Marek's style-rules and catalog have no NFR row; Kacper is explicitly UI-only. A merged skill that claims comprehensive coverage will systematically miss performance, a11y and i18n.

**T-G6 — Parallel-execution data isolation has nowhere to live.** Kacper's date-isolation model — eight workers, one shared E2E user, per-`TTQA-*` calendar bands, the TTQA-44/TTQA-70 clash worked through as a case study, and the rule that Jira step text must be updated *before* the Playwright literal — is real operational knowledge that neither other contribution knows exists. It is also the clearest evidence for persona P6. A product-agnostic skill needs a config-declared "test data isolation vocabulary" hook, or this rule is simply dropped.

**T-G7 — The golden library is single-product.** Both golden examples (`example-manual-ui-test.md`, `example-journey-create-text.md`) are SPM/OKR custom-field tests, and `style-rules.md` §10 instructs preserving "Text, Number, Hyperlink, Select, Multi-Select, User Picker, Date" as exact field-type names. The style baseline that is supposed to be product-agnostic is entirely one product.

**T-G8 — The generic coverage path is an afterthought.** `coverage-catalog.md` is ~200 lines of OKR-specific catalog (sections A–L) and ~10 lines of "Generic catalog (non-OKR features)". Since the domain catalog is optional and most runs will use the run-scoped path, the well-specified 95% of the document serves the rare case.

**T-G9 — Kacper's skill cannot be exercised here.** It depends on four files in a different private repo (`jiraIssueIds.json`, `e2eRequiredJiraUserEmails.ts`, `parallelTestDateIsolation.ts`, ~143 `TTQA-*.case.ts` specs). `SOURCE.md` documents this deliberately, but the consequence is that none of its rules can be validated in DOCS — they can only be read and generalised on faith.

**T-G10 — Two of three outputs are unparseable.** Only Marek emits a machine-readable payload. Kacper's and K&A's outputs are chat markdown and CSV blocks. Converting them into a `SuitePayload` is a one-way, lossy, undefined operation, which matters because Phase 1's exit criterion is "a real artifact produced by one of the input skills converts into a schema-valid `SuitePayload` **with no data loss**". That criterion is currently only satisfiable using Marek's artifact.

**T-G11 — No approver identity.** Open question Q5 in the decision memory; nothing in the inputs helps. Kacper's review checklist is addressed to "human", Marek's triage checkpoint to "QA", K&A's to the reader.

**T-G12 — Missing companions.** `Marek/_shared/skills-hub-README.md` points at a "Portable copy: `../TestCaseCreator/README.md`" that was not contributed. Kacper's hub documents a three-stage pipeline (`TestCaseWriting` → manual Jira import → `AutomatingTestCases`) whose middle stage is a human step with no written procedure.

## 2.5 Ambiguities and internal inconsistencies

### Marek's contribution

| # | Location | Issue |
|---|---|---|
| A-22 | SKILL.md §4a.4, reference.md, style-rules.md §2 **vs** `xray_graphql_import.py:180` | The skill states a hard cap of **15** steps for both patterns, three times. The import script enforces `max_steps = 18 if pattern == "journey" else 13`. So a 16-step journey is rejected by the skill and accepted by the tool, while a 14-step atomic is accepted by the skill and **rejected** by the tool. Two different rules for the same constraint |
| A-23 | `golden/v1/examples/example-journey-create-text.md` | The canonical golden journey — the file every run loads as the style reference — has **16 steps**, violating the 15-step cap it is meant to demonstrate. It passes the script's journey limit of 18, which is presumably why the drift went unnoticed |
| A-24 | `TestCaseDraft.schema.json` `coverage_report` | Requires only `uncovered_ac_ids` and `warnings`. `matrix` and `catalog_coverage` — the two tables the skill calls mandatory and the 100% rule depends on — are optional. A batch can be schema-valid with no coverage accounting at all |
| A-25 | `TestCaseDraft.schema.json` | `execution_plan` is optional in the schema, mandatory in SKILL §6. `deferrable` is optional in the schema although "P3 always `deferrable: true`" is a non-negotiable rule with no conditional to enforce it. `draft_id` is optional in the schema although `xray_graphql_import.py` **requires** `--draft-id` to locate a test |
| A-26 | `TestCaseDraft.schema.json` `role` | The field description enumerates `OKR_ADMIN, STANDARD_USER, NO_PERMISSION, API_CLIENT, SYSTEM` while `reference.md` says to pick product-appropriate codes. The schema's documentation is product-specific in a supposedly shared asset |
| A-27 | SKILL.md §5 vs schema | `catalog_coverage_pct` is defined in the skill as "covered applicable / total applicable" and in the schema as "Percentage of applicable catalog items **Covered or N/A**". Two different numerators |
| A-28 | `coverage_catalog_id` required-ness | The field is required by the schema with pattern `^CAT-[A-Z0-9-]+$`, while coverage catalogs are described as optional. Every test is therefore forced into a catalog abstraction even when the run invents the ids purely to satisfy the schema |
| A-29 | Output path | `AI in QA/Skills/artifacts/{JIRA-KEY} - testcase-draft.md` is hardcoded in SKILL.md (five times), reference.md, README.md, examples.md, and `templates/README.md`. The real artifacts in the repo do not follow it either (`ONE-232514 Custom fields (part 2) - testcase-draft-v2.md`), so the convention is already broken in practice |
| A-30 | `_shared/config/jira_xray_mapping.json` | Presented as a shared asset but hardcodes one cloud id, project `TC`, folder `/Ignite 2026`, and five `customfield_*` values specific to **BigPicture Enterprise / Horizon / Atlassian Cloud**. The working plan's example config uses folder `/AI drafts`, so even the plan and the shipped config disagree |
| A-31 | `xray_graphql_import.py` | `--insecure` / `XRAY_INSECURE_SSL` disables TLS certificate verification entirely. Worth an explicit decision before this becomes a first-class fallback path |
| A-32 | `xray_graphql_import.py` `requirement_link_endpoints` | The link direction is derived from config keys that must literally be `test` and `requirement`, with a comment reading like an empirically debugged result ("Pattern: 'Epic is tested by TC' → inwardIssue=TC"). Brittle, and the semantics are not verifiable without a working Xray connection |
| A-33 | `Agent Skills Specification.md` §2.3 vs the schema | The spec says `TestCaseDraft` requires `title`, `linked_requirement_keys`, `steps`. The shipped schema requires **ten** fields. The spec also describes a third skill, `xray-import`, which was never contributed — only the script |
| A-34 | `examples.md` Example 1 | Points the user at a `.md` artifact as the review source (`AI in QA/Skills/artifacts/ONE-232514 Custom fields (part 2).md`) when the gate is read from the review **JSON** |
| A-35 | `reference.md` effort table | "Journey (10–15 steps) 20–40 min" gives no rate for journeys shorter than 10 steps, which the skill permits |

### Kacper's contribution

| # | Location | Issue |
|---|---|---|
| A-36 | Frontmatter | `disable-model-invocation: **false**` on both skills, against `true` everywhere else. A test-writing skill that the model may invoke on its own initiative is a different risk profile, and the choice looks unintentional rather than argued |
| A-37 | "Test case anatomy" vs "Repo scenario ids" | The anatomy table gives `Scenario` as `TS-8 Smart Suggestions` (bare), while the section above insists "Repo scenario ids use letter suffixes — **not** bare `TS-5` / `TS-8`" and the review checklist re-checks it. The skill contradicts itself in adjacent sections |
| A-38 | Data conventions | Mandates real account addresses inline in step Data (`user1: timetracker-jira-e2e-first@appfire.com`) and names three canonical accounts in the skill body. Marek's rules forbid production credentials and require a redaction pass. Both positions are defensible; together they are a policy conflict that persona P9 has to settle |
| A-39 | "XRay CSV format (team standard)" | The three-column limit is asserted as a team standard, not as an Xray constraint — and K&A's five-column CSV is evidence that it is not a platform limit. Which of the two is a real import constraint is unverified |
| A-40 | "~143 Playwright cases" | A hard-coded count that drifts with the source repo, used as instruction ("grep ~143 cases") |

### K&A's `story-ui-test-cases`

| # | Location | Issue |
|---|---|---|
| A-41 | Table format vs CSV export | The manual TC table has one `Expected` per case, but the CSV export is "one **row per step** — repeat Test Summary for each step" with a per-row `Expected Result`. Producing the CSV therefore requires per-step expected results that the table never captured; the worked example papers over this by repeating a similar expectation on both rows |
| A-42 | "Self-contained single-file skill" | Declared in the frontmatter and Platform note, while the skill's hard prerequisite is another skill's output held in chat state |
| A-43 | HTML output | `reports/{KEY}-ui-test-cases-report.html` appears once, in the final row of the last table, with no specification — no tiers, no structure, nothing comparable to the scan skill's detailed HTML section |
| A-44 | Blocked phrases | The list includes "**gate**", which collides with Marek's gate vocabulary, the `SuitePayload` `gate` field, and the working plan's own language |
| A-45 | Figma reuse rule | "Do not call Figma MCP again if scan already included Design observations" depends entirely on same-chat state; with a persisted payload the rule needs restating in terms of what the payload contains |

## 2.6 Uncertainties

- **U-9 — Which import contract wins?** Three exist: Kacper's 3-column CSV, K&A's 5-column CSV, and Marek's GraphQL `createTest`. A-39 means we do not even know which CSV shapes are platform constraints versus team habits.
- **U-10 — Is submission in scope at all?** All three inputs forbid it; D4 requires it. C2 already proposed opt-in-per-config defaulting to off; the inputs unanimously support that resolution.
- **U-11 — Is code grounding adoptable?** It is Kacper's single strongest quality mechanism and the basis of his `Final draft` status. It requires the skill to run in a repo that contains the product, which DOCS is not, and which the SPM pilot may not be either.
- **U-12 — Do P0–P3 tiers survive?** They are Marek-only, they carry the execution plan and the release gate, and they are also the source of the coverage-percentage tension with K&A's no-numbers rule.
- **U-13 — Are the effort estimates real?** `reference.md` gives 20–40 minutes per journey and 8–15 per atomic with no stated measurement basis, and they feed the `estimated_hours` that a QA lead would plan against.
- **U-14 — Neither import path is verifiable right now.** Xray MCP fails tool discovery in this workspace, and the script's behaviour (including the requirement-link direction in A-32) cannot be tested without credentials.
- **U-15 — Are `TC-01`-style ids permitted?** Two contributions require them, one forbids them. Needs a ruling, not a compromise.
- **U-16 — Does the merged Creator generate API and NFR tests?** One says yes, two say explicitly no.
- **U-17 — What is the conversion rule from a K&A TC table to a per-step payload?** Until this is defined, T-G10's "no data loss" exit criterion cannot be met for two of three contributions.

---

## Persona read-across

How well each persona is served **today**, by contribution, and what the merge has to fix. `R` = requirements-review side, `T` = test-case side.

| Persona | Best served by | Worst gap |
|---|---|---|
| P1 QA engineer | K&A `story-testability` (R) and Marek `test-case-creation` (T) — both are written for this reader | No triage surface anywhere: three of five skills output prose the operator must edit by hand |
| P2 QA lead | Marek's execution plan and minimum release gate (T) | Nothing on the R side summarises risk across a set of stories except Marek's rollup; K&A's epic mode is closest but is release-planning, not quality oversight |
| P3 PM / BA | K&A's Jira comment templates, opening lines, and blocked phrases (R) | Marek's report has no tone layer at all, and its headline word for the PM is "BLOCKED" |
| P4 Automation engineer | Kacper's `AutomatingTestCases` (T), by a wide margin | Marek has no automation concept; K&A stops at a candidates table. The payload must carry `test_pattern`, stability, and `test_data_required` from day one or this persona gets nothing |
| P5 Skill maintainer | Nobody | Five skills, three id schemes, three status models, two severity scales, and no cross-reference — this document is the first artifact serving the persona |
| P6 Test-data steward | Kacper (T) | The knowledge exists in exactly one contribution and has no generic home (T-G6) |
| P7 UX designer | K&A Figma ingest (R and T) | Questions are raised about design, but no output is addressed to the designer and D5 excludes them |
| P8 Release manager | K&A epic mode (R) | Absent from the plan's single-issue payload contracts entirely (U-6) |
| P9 Security / compliance | Marek's redaction and `data_sensitivity` (R) | Directly contradicted by Kacper's mandated real account emails in step Data (A-38); nobody owns the conflict |
| P10 Platform admin | K&A's data-sources-unavailable block with per-step reasons (R) | Marek aborts on Jira MCP failure ("no partial gate PASS") where K&A degrades — opposite reflexes, and the merged behaviour is unspecified |

---

## What this review did not cover

- The ~143 Playwright specs, `jiraIssueIds.json`, `e2eRequiredJiraUserEmails.ts`, and `parallelTestDateIsolation.ts` referenced by Kacper's skills — they live in `7pace/7pace.Timetracker` and were deliberately not copied (`SOURCE.md`).
- Runtime behaviour. Nothing was executed: no skill was run, no payload validated against its schema, and `xray_graphql_import.py` was read but not invoked. Findings A-22, A-23, A-24 and A-25 are static contradictions between files, and should be reconfirmed the first time a real batch is validated.
- Prior art under `AI in QA/Skills/`, per decision C1 — the `Input/Marek/_shared/` copies were reviewed instead, as intended.
