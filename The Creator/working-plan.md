# The Reviewer & The Creator — working plan

**Status:** Draft for approval (Reviewer shipped; Creator execution in [ACTION-PLAN.md](ACTION-PLAN.md))
**Date:** 2026-09-25
**Owner:** Marek Wyszyński
**Goal:** Consolidate the skills in `The Creator/Input/` into two product-agnostic "super skills" — **The Reviewer** and **The Creator** — each producing an interactive report that a human uses to review and correct the outcome before anything is written to Xray.
**Decision memory:** [DECISIONS.md](DECISIONS.md)

---

## 1. Scope and locked decisions

These were agreed before planning and are treated as fixed. Anything that contradicts them is out of scope.

| Decision | Choice |
|---|---|
| Report format | Self-contained single-file HTML is the **required** output. Cursor Canvas is an optional extra layer, not a dependency. |
| Host support | Must run on **Cursor and Claude** (Code and desktop). Nothing host-specific in the critical path. |
| Edit loop | The report exports a **corrected JSON payload**; the operator points the agent at that file for import. |
| Xray writes | **The Creator submits**, but only after explicit human approval, via **Xray MCP** with `xray_graphql_import.py` as fallback. |
| Personas in scope | QA engineer, QA lead/manager, product manager/BA, automation engineer. |
| Portability | Product-agnostic skills plus a **per-product config file**. |
| Repo home | New `The Reviewer/` and `The Creator/` folders **supersede** the current skills; the old folders are archived. |
| Review gate | CRITICAL findings **keep hard-blocking** The Creator, with an explicit `force` override. |
| Source material | **Only** the skills placed in `The Creator/Input/` are inputs to the consolidation. |

### Out of scope for v1

Test execution and result reporting, automated test-code generation, Confluence publishing, CI/headless runs, and any write to a production Xray project without an allowlist entry.

---

## 2. Source material and why consolidation is needed

### The inputs

The **only** source skills for this consolidation are the ones placed in `The Creator/Input/`. At the time of writing that folder is empty, so the source inventory is pending. Phase 1 opens by cataloguing it.

Nothing in this plan should be read as a statement about the skills under `AI in QA/Skills/` — those are prior art and background, not the migration source, and they are not to be moved or archived on the basis of this plan.

### The problems consolidation solves

These are the structural problems the two super skills are designed to fix. They hold regardless of which specific skills land in `Input/`, but each one must be **re-confirmed against the actual inputs** during the Phase 1 inventory rather than assumed.

1. **Hardcoded paths.** Skills that reference one repo's layout for templates, schemas, style guides, and artifacts cannot run in another product's repo.
2. **Prose-only output.** A long Markdown deliverable is comprehensive but hard to triage, and offers no way to accept, reject, or edit an individual test.
3. **No correction loop.** Fixing a draft means editing prose by hand or re-prompting the agent, and any embedded machine-readable payload drifts from the human-readable body.
4. **Fragmented skills.** Review and creation are separate invocations with a hand-rolled hand-off, so the gate between them depends on the operator remembering to honour it.

The consolidation keeps whatever *rules* the input skills encode and replaces the *plumbing*: config-driven paths, a payload-first data contract, and a rendered report as the human interface.

---

## 3. Personas

Each persona gets a defined entry point and a defined view of the report. This is what drives the report design — a single undifferentiated report would serve none of them well.

### QA engineer — the primary operator

Runs both skills, triages drafts, owns the submission decision. Needs to move fast through a 15–40 test suite, spot the two or three tests that are wrong, fix them in place, and submit. Cares about step-level detail, test data prerequisites, and duplicates against the existing Xray suite.

*Report needs:* triage-first layout, keyboard-driven accept/reject, inline editing of titles, steps, and expected results, a visible count of undecided items, and an export button that is disabled until every test has a decision.

### QA lead / manager — oversight

Does not run the skills day to day. Wants to know whether a story is adequately covered, where the risk sits, and how much execution effort the suite implies. Reviews a sample rather than every test.

*Report needs:* a summary view above the detail — coverage percentage, P0–P3 distribution, uncovered P0/P1 items, execution-hour estimate, and the list of blockers needing PM input. Should be readable without expanding a single test.

### Product manager / BA — consumer of The Reviewer

Receives review findings and fixes the requirement. Usually has no AI tooling and may not open the repo at all. This persona is the main reason the report must be shareable HTML rather than a Canvas.

*Report needs:* findings grouped by severity with the verbatim requirement quote next to each, the suggested AC patch in copyable form, and one clear question per finding. No QA jargon, no coverage matrices, no test steps.

### Automation engineer — downstream consumer

Scans the approved suite for automation candidates: stable, high-value, data-light tests. Works after submission, not before.

*Report needs:* a filter on tier, pattern (journey vs atomic), and `test_data_required`, plus an export of the selected subset. Deferred to Phase 5 — noted here so the payload carries the fields they need from day one.

### Design consequence

The report has one summary section plus a filterable test/finding list, and a persona selector that presets the filters and section visibility. Same file, same payload, four entry points. No persona-specific builds.

---

## 4. Target architecture

The core idea: **the skill produces a payload, a script renders the payload, the browser collects corrections.** The agent never hand-writes HTML, so report quality does not vary run to run and does not consume context.

```
                    per-product config
                           │
   Jira / Confluence ──────┤
   PDFs, images, URLs ─────┤
   Existing Xray suite ────┤
                           ▼
              ┌────────────────────────┐
              │  The Reviewer (skill)  │
              └───────────┬────────────┘
                          │  review-payload.json
                          ├──────────────► render_report.py ──► review-report.html
                          │                                        │ (PM reads, QA gates)
                          ▼
              ┌────────────────────────┐
              │  The Creator (skill)   │  ◄── gate: BLOCKED on CRITICAL unless force
              └───────────┬────────────┘
                          │  suite-payload.json
                          ├──────────────► render_report.py ──► suite-report.html
                          │                                        │
                          │                    QA triages, edits, exports
                          │                                        ▼
                          │                              suite-payload.approved.json
                          ▼                                        │
              ┌────────────────────────────────────────────────────┘
              │  The Creator — submit mode
              │  Xray MCP (primary) │ xray_graphql_import.py (fallback)
              └───────────┬────────────┘
                          ▼
                   import-report.html + Xray test keys
```

### Components

| Component | Form | Notes |
|---|---|---|
| `The Reviewer/SKILL.md` | Markdown skill | Requirement quality analysis and the gate. Successor to `requirements-review`. |
| `The Creator/SKILL.md` | Markdown skill | Suite generation, triage handoff, and gated submission. Successor to `test-case-creation`. |
| `shared/render_report.py` | Python 3, **stdlib only** | Payload JSON → self-contained HTML. One script, three report kinds. |
| `shared/schemas/*.json` | JSON Schema | Payload contracts, validated before rendering. |
| `shared/golden/` | Markdown | Style rules and example tests, product-overridable. |
| `config/<product>.json` | JSON | Per-product Jira/Xray settings, terminology, catalogs. |

### Why a script and not agent-authored HTML

A deterministic renderer gives identical output on Cursor, Claude, and a terminal; costs no tokens; can be unit-tested; and cannot silently drop a test while "summarising". Stdlib-only Python keeps it runnable anywhere without an install step. The agent's job ends at producing a schema-valid payload.

---

## 5. Data contracts

Three payloads, versioned with `payload_version`. The renderer and the submitter validate against schema and refuse to proceed on failure.

### `ReviewPayload`

Evolves `templates/review_findings.schema.json`. Keeps `findings[]` with `finding_id`, `severity`, `category`, `excerpt_quote`, `finding_summary`, `question_for_PM`, `suggested_AC_patch`, `blocks_test_generation`, plus `rollup` and `gate`. Adds:

- `product` — config id the run used.
- `requirements[]` — the normalized bundle actually analysed, so the report can show the requirement next to the finding.
- `context_loaded[]` — every file, URL, and link attempted, with outcome. Makes "the agent never read the PRD" visible instead of invisible.

### `SuitePayload`

Evolves `schemas/TestCaseDraft.schema.json`. Keeps `tests[]`, `coverage_report` (`matrix[]` + `catalog_coverage[]`), and `execution_plan` unchanged — these already work. Adds:

- `review_ref` — path and gate status of the Reviewer payload, or `not_used`.
- `context_loaded[]` — as above.
- `tests[].decision` — `{ status: pending | approved | rejected | edited, decided_by, decided_at, note }`. Absent or `pending` on generation; filled by the report.
- `tests[].origin` — `generated | edited_in_report | added_in_report`, for audit.

Putting decisions inside the same object as the test is deliberate: one file round-trips, and nothing has to be re-joined by id.

### `ImportPayload`

Per-test `action` (`created | updated | skipped | failed | would_create | would_update`), resulting `xray_key`, errors, the requirement links made, and a `mode` of `dry_run | write`.

### Round-trip rules

1. The report only ever writes to `decision`, `origin`, and the editable test fields. Coverage, traceability, and tier math are recomputed by the agent on ingest, never trusted from the browser.
2. Export is blocked while any test is `pending`, so an unreviewed suite cannot reach Xray by accident.
3. On ingest the agent diffs approved-vs-generated and reports what the human changed. Edits that break traceability (a step that no longer matches its `source_quotes`) surface as warnings, not silent acceptance.

---

## 6. Per-product configuration

The single mechanism that makes these skills work in any Appfire product. One file, no skill edits.

```json
{
  "config_version": "1.0",
  "product": { "id": "spm", "name": "Appfire SPM", "terminology_notes": "..." },
  "jira": {
    "cloud_id": "...",
    "projects": ["ONE", "SPM"],
    "field_map": { "acceptance_criteria": "customfield_XXXXX" }
  },
  "xray": {
    "environment": "sandbox",
    "test_project_key": "TC",
    "production_allowlist": [],
    "folder": "/AI drafts",
    "draft_label": "ai-draft",
    "channel": "mcp"
  },
  "assets": {
    "golden": "shared/golden/v1",
    "coverage_catalog": null,
    "requirement_standard": "shared/templates/requirement_standard.md"
  },
  "policy": {
    "gate_blocks_on": ["CRITICAL"],
    "figma_policy": "link-only",
    "jira_comment": "opt-in",
    "require_approval_before_write": true
  },
  "output": { "artifacts_dir": "artifacts", "report_kinds": ["html"] }
}
```

Resolution order: explicit session parameter, then `config/<product>.json`, then `config/default.json`, then documented built-in defaults. The skill announces which config it resolved and aborts if a product config names an Xray project outside the allowlist while `environment` is `production`.

The DOCS repo ships `config/spm.json` as the reference implementation and pilot config.

---

## 7. Report specification

Shared shell, three report kinds. Self-contained: inlined CSS and vanilla JS, payload embedded as a JSON blob, no network requests, no build step, opens by double-click.

### Common behaviour

A persona selector presetting filters and section visibility; a summary band that reads correctly with everything collapsed; filter and free-text search; deep-linkable anchors per item so a reviewer can send "look at TC-014"; and a print stylesheet so the report survives being turned into a PDF for a stakeholder.

### Review report (The Reviewer)

Gate status as the headline — a BLOCKED run must be unmissable. Findings grouped by severity, each showing the verbatim quote beside the requirement it came from, the PM question, and a copy button on the suggested AC patch. A rollup section with the recommended fix order. A context table showing what was and was not loaded.

Interaction is deliberately light: PMs mark findings `accepted | rejected | needs discussion` with a comment and export a decisions file. No inline requirement editing — the requirement's home is Jira.

### Suite report (The Creator)

The workhorse. Summary band: test count with justification, coverage percentage, tier distribution, uncovered P0/P1 items, execution estimate, blockers.

Then a test list, each row collapsible to a full detail panel with objective, preconditions, test data prerequisites, customer impact, traceability (linked ACs, `CAT-*` id, `source_quotes`), the step table, and any duplicate hint. Per row: approve, reject with reason, or edit. Editing covers title, objective, preconditions, tier, role, test data fields, and the step table (edit, reorder, add, delete, respecting the 15-step cap). A new test can be added by hand and is tagged `added_in_report`.

Supporting views: the requirement→test traceability matrix, the `CAT-*` catalog coverage table, and bulk actions (approve all P0, reject all P3).

The footer is the export gate — undecided count, then a download of `suite-payload.approved.json` with the exact command to hand it back to the agent.

### Import report

Per-test action and resulting Xray key, links created, failures with the API error, and a re-run hint for the failed subset only.

### Accessibility and robustness floor

Keyboard navigable, no colour-only status encoding, legible at 100% zoom, and functional in Chrome, Firefox, and Safari. Export uses a Blob download, which works from a `file://` page in all three.

---

## 8. Submission flow

The Creator runs in three explicit modes, never implicitly chained.

| Mode | Trigger | Effect |
|---|---|---|
| `generate` | Default | Produces payload plus suite report. No writes. |
| `dry-run` | Operator asks, after an approved payload exists | Resolves duplicates, validates the Xray mapping, reports `would_create` / `would_update`. No writes. |
| `submit` | Operator asks, after dry-run, with explicit chat confirmation | Creates or updates tests, links requirements, files them in the configured folder with the draft label. |

Preconditions for `submit`: a schema-valid approved payload, zero `pending` decisions, a completed dry-run in the same session, `environment` resolved from config with production requiring an allowlist entry, and an explicit human "yes" in chat. Missing any one is a hard stop.

Channel selection is `mcp` first. **Prerequisite:** the Xray MCP server in this workspace currently fails tool discovery, so Phase 4 must begin by fixing or replacing that connection. `xray_graphql_import.py` remains the fallback and is the reason the fallback exists rather than being theoretical.

Idempotency: rejected tests are never submitted; a fingerprint over requirement key, normalized title, and normalized steps drives create-vs-update so a re-run after partial failure does not duplicate. Default on partial failure is continue-and-report.

---

## 9. Portability across Cursor and Claude

| Concern | Approach |
|---|---|
| Skill discovery | `SKILL.md` with `name` + `description` frontmatter works in both. Install docs cover `.cursor/skills/` and `.claude/skills/`; a `make install` symlinks into whichever exists. |
| Host-specific frontmatter | Keep `disable-model-invocation: true` for Cursor; Claude ignores unknown keys. Document it as Cursor-only. |
| Paths | No absolute paths in skill bodies. Everything resolves from the config file relative to a `skill_root` the skill determines at runtime. |
| Tooling assumptions | Skills name **logical** capabilities ("fetch a Jira issue"), with a capability table mapping them to Atlassian MCP, Xray MCP, or script fallbacks. A missing capability degrades with a stated warning instead of aborting. |
| Rendering | The Python renderer runs identically on both. Canvas is an optional Cursor-only add-on in Phase 5. |
| Verification | Phase 6 runs the same pilot story on both hosts and diffs the payloads. |

---

## 10. Phased delivery

Phases 1–4 are the minimum shippable product. Each phase has a demo you can watch.

### Phase 1 — Inventory and foundations

**Start by inventorying `The Creator/Input/`.** Catalogue every skill, template, schema, style guide, and example there, and produce a rule-by-rule port checklist: which rules carry over unchanged, which need generalising to be product-agnostic, which conflict between the input skills, and which are dropped. Nothing downstream is designed until that checklist exists, because the payload schemas have to cover the real rules.

Then freeze the three payload schemas with `payload_version`; write `config/default.json` plus one pilot product config and the resolution rules; create the `The Reviewer/` and `The Creator/` skeletons; and move the shared assets the inventory identified into `shared/`. Archive the input skills with a pointer to their successors.

*Done when:* the port checklist is reviewed and signed off, and a real artifact produced by one of the input skills converts into a schema-valid `SuitePayload` with no data loss.

### Phase 2 — Renderer

Build `render_report.py` with the shared shell and all three report kinds, including edit, decision, and export behaviour. Add a fixtures-based test that a payload survives render → edit → export → re-ingest unchanged.

*Done when:* the Phase 1 converted payload renders as a report you can triage end to end, and the exported file re-ingests cleanly.

### Phase 3 — The two skills

Rewrite both skills against the config and payload contracts, preserving the current gate model, coverage model, traceability rules, tier system, and test-data rules. Each skill ends by producing a payload, rendering the report, and stopping at the human checkpoint.

*Done when:* a fresh run on a pilot story produces both a review report and a suite report with no hardcoded paths anywhere in either skill.

### Phase 4 — Submission

Fix the Xray MCP connection, then implement `dry-run` and `submit` with fingerprint-based upsert, approval preconditions, the script fallback, and the import report.

*Done when:* an approved suite reaches the sandbox Xray project with requirement links intact, and a deliberately re-run submission updates rather than duplicates.

### Phase 5 — Persona polish

Persona presets, the automation-candidate filter and subset export, the print stylesheet, the optional Cursor Canvas layer, and optional Jira comment-back.

### Phase 6 — Pilot and rollout

Run both skills on two stories per pilot product on both Cursor and Claude. Capture time-to-submit, edit rate per test, and coverage percentage as the baseline. Write the operator guide and a one-page PM guide. Onboard a second product using only its config file — if that requires a skill edit, the abstraction has failed and goes back to Phase 1.

---

## 11. Repository layout

```
The Reviewer/
  SKILL.md              reference.md          examples.md
The Creator/
  SKILL.md              reference.md          examples.md
  working-plan.md       DECISIONS.md
  Input/                source skills being consolidated (read-only)
shared/
  render_report.py
  schemas/              review-payload, suite-payload, import-payload
  templates/            requirement standard / checklists from the inventory
  golden/v1/            style rules, example tests
  scripts/              Xray import fallback script
  fixtures/             renderer test payloads
config/
  default.json          <pilot-product>.json
artifacts/              gitignored — run outputs
```

`Input/` stays intact as the archived source of record. Shared assets are **copied** out of it during Phase 1, not moved, so the port checklist can always be re-checked against the originals.

Artifacts are gitignored except for a small set of committed fixtures, selected in Phase 1 from real runs of the input skills.

---

## 12. Risks

| Risk | Mitigation |
|---|---|
| Xray MCP unavailable or unstable | Phase 4 starts by fixing it; the GraphQL script fallback is a first-class path, not an afterthought. |
| Payload schema churn breaks saved reports | `payload_version` on every payload; the renderer refuses an unknown major version with a clear message. |
| Browser export loop feels clunky | Accepted tradeoff for portability. If Phase 6 shows it is the bottleneck, add an optional local watcher — the payload contract does not change. |
| Rewrite loses hard-won rules from the input skills | Phase 1 produces a rule-by-rule port checklist from `Input/` and Phase 3 works through it; `Input/` is preserved so the originals stay checkable. |
| Design decisions made before the inputs were known | Phase 1's inventory is a gate: if the real inputs contradict an assumption here, the schemas and plan change before Phase 2 starts. Decisions and their revisions are tracked in [DECISIONS.md](DECISIONS.md). |
| Product teams fork the skills anyway | The Phase 6 exit criterion is explicitly "second product onboarded with config only". |
| Report becomes a second place where suites are authored | Editing is bounded to bounded fields; coverage and traceability are always recomputed by the agent, never authored in the browser. |

---

## 13. Open questions

Decision history and open items are tracked in [DECISIONS.md](DECISIONS.md). Only the first is blocking.

0. **What goes into `The Creator/Input/`?** The folder is empty; the Phase 1 inventory cannot start without it. *(Phase 1 — blocking)*
1. **Which two products pilot this**, and can the second one's config be written without its team's help? *(Phase 6)*
2. **Where do these skills ultimately live?** DOCS is a personal docs repo. A shared QA tooling repo is the natural home once the pilot proves out — who owns it? *(Phase 6)*
3. **Does every product import into one Xray test project, or one per product?** Affects `config.xray` and the duplicate search scope. *(Phase 4)*
4. **Is a sandbox Xray available per product**, or is the draft-label-in-production pattern the only option for some? *(Phase 4)*
5. **Who approves submission** — the QA engineer who ran it, or does a lead countersign for P0 suites? Currently modelled as single-approver. *(Phase 4)*
6. **Should The Reviewer comment findings back to Jira by default?** Currently opt-in per config. *(Phase 5)*
7. **How do reports reach a PM without repo access** — attach to the Jira issue, or shared drive? *(Phase 5)*
