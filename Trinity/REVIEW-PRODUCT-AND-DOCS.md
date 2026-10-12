# Trinity — product & documentation review

**Date:** 2026-10-12  
**Purpose:** Capture a multi-persona review of the **Trinity product** (Reviewer, Studio, Creator, Importer) and **operator documentation**, with **open questions** for interactive resolution.  
**Method:** This review uses **three persona layers** (see §1): runtime Cursor prompts in `Trinity/personas/`, the **P1–P10** design-time matrix from solution consolidation, and **Reviewer audience roles** from `reviewer/MANUAL.md` §11. Findings draw on repo layout, Studio behaviour, and the E2E path on ONE-228469.

**Status:** **POC-complete when artifacts filled** — scorecard + Google Slides ([POC-GOOGLE-SLIDES-BULLETS.md](POC-GOOGLE-SLIDES-BULLETS.md)). IQ-01–IQ-17 implemented 2026-10-12 (commit `dc5b7ec`); open product gaps → §2 notes + [`parity-matrix.md`](parity-matrix.md).

---

## 1. Persona layers (which “personas” mean what)

Trinity uses different persona concepts at different stages. This review applies **all** of them where relevant.

### 1.1 Runtime agent prompts (`Trinity/personas/*.md`)

Loaded by Cursor skills and editable in Studio → **Personas**.

| File | Used by |
|------|---------|
| [`reviewer-expert-qa-automation.md`](personas/reviewer-expert-qa-automation.md) | **Reviewer** (default `persona_id` in run config) |
| [`creator-expert-qa-engineer.md`](personas/creator-expert-qa-engineer.md) | **Creator** (all three loaded per run) |
| [`creator-test-architect.md`](personas/creator-test-architect.md) | **Creator** |
| [`creator-expert-test-automation-engineer.md`](personas/creator-expert-test-automation-engineer.md) | **Creator** |

Sections **3–6** below map these four files to detailed findings.

### 1.2 Design-time personas **P1–P10** (solution design)

Used when **merging** Reviewer + Creator skills (2026-09). **Operator canonical:** [`personas/P1-P10.md`](personas/P1-P10.md). Also:

- [`The Creator/CREATOR-SKILLS-PERSONA-REVIEW.md`](../../The%20Creator/CREATOR-SKILLS-PERSONA-REVIEW.md) — §4 persona table, conflict register **C-01–C-15**  
- [`reviewer/MANUAL.md`](reviewer/MANUAL.md) §11 (audience roles, aligned to P1–P10)  
- [`reviewer/reference.md`](reviewer/reference.md) — e.g. **P10** → `context_loaded[]` in reports (PRF-04)

| ID | Role | Primary need from the pipeline |
|----|------|--------------------------------|
| **P1** | QA engineer | Triage, edit tests, trace to AC, runnable data |
| **P2** | QA lead / manager | Coverage, tiers, effort, release picture |
| **P3** | PM / BA | See assumptions; answer linked questions; no “gate” jargon |
| **P4** | Automation engineer | Candidates, stability, handoff metadata |
| **P5** | Skill maintainer | One contract, versioned rules, port checklist |
| **P6** | Test-data steward | Isolation, parallel workers, no invented users |
| **P7** | UX designer | Design-linked expectations from review, not re-fetch |
| **P8** | Release / delivery manager | Epic rollout, child inventory, batch status |
| **P9** | Security / compliance | No secrets/PII in exported artifacts |
| **P10** | Platform / MCP admin | Visible source load failures (`context_loaded`) |

**§2** scores Trinity **today** against P1–P10 (product + docs).

### 1.3 Reviewer audience roles (`reviewer/MANUAL.md` §11)

Same ecosystem as P1–P10, written for operators of **The Reviewer** report:

| MANUAL role | Maps to | Trinity touchpoint |
|-------------|---------|-------------------|
| QA engineer | P1 | Reviewer run, Studio unit review, Creator triage |
| QA lead / manager | P2 | Report Tier 1, Creator summary, no multi-epic rollup in Studio |
| PM / BA | P3 | Clarification questions, readiness label |
| UX designer | P7 | `owner_hint: UX` on findings |
| Release / delivery manager | P8 | Epic child inventory in Reviewer HTML |
| Security / compliance | P9 | `data_sensitivity` findings |
| Skill maintainer | P5 | `checklist.md`, personas, schemas |
| Platform / MCP admin | P10 | Data sources section in report |
| Automation engineer | P4 | Creator `automation_*` fields (Reviewer signal only) |
| Test-data steward | P6 | Creator prerequisites / config (not Reviewer) |

### 1.4 Adjacent corpora (not Trinity runtime)

| Document | Use |
|----------|-----|
| [`BP QA/personas.md`](../../BP%20QA/personas.md) | Seven lenses for **Ways of Working** pages (Tomasz, Priya, …) — useful for **process** docs, not loaded by Trinity skills |
| [`The Creator/INPUT-REVIEW.md`](../../The%20Creator/INPUT-REVIEW.md) | Evidence behind P1–P10 and port decisions |

**Gap (closed IQ-15):** [`personas/importer-xray-operator.md`](personas/importer-xray-operator.md) + [`personas/P1-P10.md`](personas/P1-P10.md) lead table for Importer governance.

---

## 2. Design-time P1–P10 — Trinity fulfillment (product + docs)

Legend: **M** met well · **P** partial · **G** gap

| ID | Product | Documentation | Notes |
|----|---------|---------------|--------|
| **P1** | **P** | **P** | Studio triage for review + Creator; Importer plan/execute in Studio; **Profile B** suite HTML via export (IQ-13), not in-app suite triage |
| **P2** | **M** | **P** | Dashboard **portfolio rollup** (PQ-01) + per-run coverage (IQ-11); see [METRICS.md](METRICS.md) |
| **P3** | **P** | **P** | Reviewer Q# for PM; blocked “gate” in HTML; Importer opaque to PM |
| **P4** | **M** | **P** | `automation_fit` / blockers; AutomatingTestCases still separate skill (by design) |
| **P5** | **M** | **M** | Schemas, SKILL.md, GUIDE, CONTRACTS; DECISIONS local to maintainer |
| **P6** | **P** | **G** | Prerequisites in tests; no `test_data_isolation` config hook (T-G6) |
| **P7** | **P** | **P** | Reviewer gathers Figma; Creator consumes review_ref; Studio no design preview |
| **P8** | **P** | **G** | Epic inventory in Reviewer; Studio run page light on release mix; Importer no rollout gate |
| **P9** | **P** | **G** | Reviewer redaction culture; export to Xray can leak staging names; no export redaction gate |
| **P10** | **M** | **P** | `context_loaded[]` in Reviewer; Creator batch `golden_sampling`; Studio import errors generic |

### P1–P10 questions (design personas)

| ID | Question | Owner |
|----|----------|--------|
| **PQ-01** (P2) | Should Studio **Dashboard** show portfolio-level readiness / test-count rollup? | **Done** — portfolio rollup panel (grill R2) |
| **PQ-02** (P3) | PM-safe summary on Importer handoff | **Done** — `pm_safe_summary` in plan + prompt |
| **PQ-03** (P6) | Add `test_data_isolation` to `creator/config/*.json` as in C-06/T-G6? | Creator maintainers |
| **PQ-04** (P8) | Block Importer export until Epic **Reviewer gate** is green on linked `review_ref`? | Release + QA |
| **PQ-05** (P9) | Redaction pass on `importer-payload.json` before execute (emails, internal URLs)? | Security |
| **PQ-06** (P10) | Surface `context_loaded` / import failures on Studio **Dashboard** for operators? | **Done** — Dashboard alerts panel (grill R5) |

---

## 3. Documentation audit — Jira project selector

Does each doc explain **what** the selector does, **TC default**, **override vs mapping**, **API**, and **`project.id` / createFolder** caveat?

| Document | Project selector covered? | Notes |
|----------|---------------------------|--------|
| [`GUIDE.md`](GUIDE.md#getting-started) | **Yes** | Getting Started table + §6.3 detailed steps |
| [`README.md`](README.md) | **Partial** | Points to GUIDE Getting Started |
| [`importer/README.md`](importer/README.md) | **Yes** | Steps 3–5 + link to GUIDE |
| [`importer/reference.md`](importer/reference.md) | **Yes** | `jira-projects` API, `project_key_override`, TC rationale |
| [`importer/config/mappings/README.md`](importer/config/mappings/README.md) | **Yes** | Per-project mapping + override limits |
| [`importer/SKILL.md`](importer/SKILL.md) | **Yes** | Studio workflow + project key override + coverage in prompt |
| [`TESTING.md`](TESTING.md) | **Yes** | §4 Importer → GUIDE §6 |
| [`MANUAL.md`](MANUAL.md) | **Yes** | Importer chapter (Studio → Xray) |
| [`PIPELINE.md`](PIPELINE.md) | **Yes** | Importer step links GUIDE §6 |
| [`studio/README.md`](studio/README.md) | **Yes** | API endpoints listed |
| [`PREFLIGHT.md`](PREFLIGHT.md) | **Yes** | Health features + GUIDE §6 link |

**Doc actions (done or recommended):**

- [x] Central **Getting Started** in GUIDE with project selector quick reference  
- [x] Extend **MANUAL.md** with Importer chapter (instance, mapping, project key, folder, prompt)  
- [x] Extend **importer/SKILL.md** with Studio selector + `project.id` warning  
- [ ] Screenshot or annotated UI mock in GUIDE (optional)

---

## 4. Runtime persona — Reviewer Expert QA (automation-first)

### Strengths

- Clear Epic-only Creator handoff; Studio blocks `not_fit` from Creator prompt.
- Review payload + HTML report separation (`render_report.py`) is testable and deterministic.
- Portfolio run configs + JQL resolve prompts reduce ad-hoc scope errors.

### Gaps / risks

- **R1:** Reviewer output does not surface “recommended Importer project” or environment — operator must infer from product (BigPicture → TC vs product team project).
- **R2:** No explicit **test environment** field in handoff to Creator/Importer (staging vs prod Xray) beyond operator memory.
- **R3:** Hollow-epic rules in persona are strong; Studio does not visually flag “hollow” epics on import.

### Questions (Reviewer lens)

| ID | Question | Owner |
|----|----------|--------|
| **RQ-01** | Suggested project/folder for Importer | **`creator/config` `importer.*` defaults**; Reviewer stays agnostic | **Done** |
| **RQ-02** | Do we require `environment` / `tenant` in Reviewer export before Creator runs on security epics? | QA + EM |
| **RQ-03** | Reviewer gate on Importer page | **Done** (IQ-16 soft gate + ack) |

---

## 5. Runtime persona — Creator Expert QA Engineer

### Strengths

- Journey-style batches with roles, test data, and `persona_notes` support human execution.
- Golden sampling (CR-GOLDEN-01) is auditable in batch JSON.
- Studio edit loop for steps, approve/reject, Xray mark fits QA workflow.

### Gaps / risks

- **C1:** `coverage_catalog_id` was missing on Epic runs — fixed at export/enrich time; schema still optional while Importer legacy validator required it (confusing for operators).
- **C2:** `test_type: Generic` on a journey caused Xray failure until coerced to Manual — Creator allows values Xray does not.
- **C3:** Golden is TC-centric; teams importing to **non-TC** projects may get naming/folder conventions that do not match target project norms.

### Questions (QA Engineer lens)

| ID | Question | Owner |
|----|----------|--------|
| **CQ-01** | Should Creator **enforce** `test_type: Manual` for `release_slice_e2e` unless config allows Cucumber? | **Done** — coerce at import; show `test_type_coercion` in Importer plan (grill R3) |
| **CQ-02** | Should `coverage_catalog_id` be **required** in schema when `linked_ac_ids` exist (derive one canonical field)? | **Grill R4:** `coverage_catalog_id` canonical when present; document `linked_ac_ids` as legacy |
| **CQ-03** | Default Importer folder in `creator/config`? | **Done** — `importer.default_folder_template` |

---

## 6. Runtime persona — Creator Test Architect

### Strengths

- `release_slice_e2e` cap (3–5 journeys) matches Epic planning scale.
- CR-STEP-01 self-contained steps enforced in skill; reduces execution ambiguity.
- Coverage matrix intent in skill/reference is clear.

### Gaps / risks

- **A1:** ~~Studio does not visualize coverage_report.matrix~~ — **Resolved (IQ-11)** on Creator run page.
- **A2:** Importer plan validates **legacy** Xray import rules, not full `TestCaseDraft.schema.json` — two validation worlds.
- **A3:** ~~Deferrable mark without warning~~ — **Warn** on bulk mark + export preflight (IQ-08).

### Questions (Architect lens)

| ID | Question | Owner |
|----|----------|--------|
| **AQ-01** | Deferrable tests at export | **Warn** (IQ-08) |
| **AQ-02** | Unify validation | **Done** (IQ-04) |
| **AQ-03** | Coverage matrix in Importer Cursor prompt | **Done** — `coverage_matrix_markdown` in plan/prompt |

---

## 7. Runtime persona — Creator Test Automation Engineer

### Strengths

- `automation_fit`, `automation_candidate`, `automation_blockers` on each test.
- Production mapping sets **Automated** custom field to Manual for import — aligns with manual tests.

### Gaps / risks

- **T1:** No round-trip: after Xray create, Studio does not store **TC-xxxx** keys on `test_case_row` (stats `test_cases_imported_xray` not wired).
- **T2:** Project selector does not expose whether target project supports **automation** fields / Xray test types for future CI imports.
- **T3:** M2M/API-heavy journeys marked `automation_fit: full` but steps include browser UI — inconsistent for backlog prioritization.

### Questions (Automation lens)

| ID | Question | Owner |
|----|----------|--------|
| **TQ-01** | Persist `xray_key` after import | **Done** (IQ-05) |
| **TQ-02** | Map `automation_fit` → Xray **Automated** field value when partial/full? | **POC deferred** — all TC imports Manual; `automation_fit` in Studio/telemetry only (grill R3) |
| **TQ-03** | Separate **automation backlog export** (JSON/CSV) from Importer handoff? | QA + automation |

---

## 8. Cross-cutting product review

### Studio & operator UX

| Area | Assessment |
|------|------------|
| **Start/stop scripts** | Improved; `STUDIO_FORCE` documented |
| **Import feedback** | New/updated runs visible |
| **Importer** | Plan + **Execute import batch** + prompt (PM summary + coverage matrix) |
| **Project selector** | Key override + Jira project search; **mapping `project.id` decoupled** from override (footgun) |
| **Credentials** | Split `.env` / `.env.production`; easy to mismatch instance vs mapping |
| **Static UI on :8765** | React on 5173 is primary; static shell may lag |

### Importer & Xray

| Area | Assessment |
|------|------------|
| **Production path** | Proven (ONE-228469 → TC-6704–6708) |
| **Sandbox** | Xray keys / license not resolved |
| **Batch execute** | Studio **Execute import batch** + CLI; idempotency still manual |
| **Requirement links** | Jira REST; Epic vs Story link policy not documented |
| **Folder taxonomy** | Operator-defined paths; no validation against existing Xray tree |

### Security & compliance

| Area | Assessment |
|------|------------|
| **Secrets** | Gitignored env files; Cursor history risk called out in ops |
| **Production writes** | High risk tier; UI label present — no second confirmation modal |
| **PII in tests** | Export preflight **warnings** (IQ-17); no hard block |

### Documentation set

| Area | Assessment |
|------|------------|
| **GUIDE.md** | Primary operator doc; Getting Started + project selector |
| **Fragmentation** | MANUAL + GUIDE §6 centralize Importer; TESTING/PIPELINE link there — see [`NEXT-STEPS.md`](NEXT-STEPS.md) |
| **Agent skills** | SKILL.md files exist; install script links importer |
| **Review meta** | This file for open questions |

---

## 9. Interactive question backlog

Decisions from the 2026-10-12 session → **[ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md)**. Pilot evidence → **[FAQ.md](FAQ.md)**, **[POC-TC-GENERATOR.md](POC-TC-GENERATOR.md)**, **[METRICS.md](METRICS.md)**, **[SCORECARD-TC-GENERATOR.md](SCORECARD-TC-GENERATOR.md)**.

### Priority P0 (blocks safe scaling)

| ID | Topic | Summary | Decision |
|----|--------|---------|----------|
| **IQ-01** | `project.id` vs `project_key_override` | Auto-resolve via Jira REST; block on mapping conflict | **Done** — Importer plan + execute_ready |
| **IQ-02** | Production import guard | Typed `PRODUCTION` confirmation + badge | **Done** — Studio Importer UI |
| **IQ-03** | Sandbox strategy | Prod-only Xray import policy | **Accepted** — document in GUIDE/POC |
| **IQ-04** | Validation single source | Shared schema validation | **Done** — `shared/validate_for_xray.py` |

### Priority P1 (quality & traceability)

| ID | Topic | Summary |
|----|--------|---------|
| **IQ-05** | Post-import linkage | Store Xray keys in Studio after execute | **Done** — record-results API + Importer UI |
| **IQ-06** | MANUAL.md Importer chapter | Same depth as Getting Started project selector | **Done** — MANUAL §Importer |
| **IQ-07** | Importer persona | Add `personas/importer-xray-operator.md`? | **Done** |
| **IQ-08** | Deferrable tests | Warn on export when `deferrable: true` | **Done** — warn only |
| **IQ-09** | Mapping per product | Who maintains `jira_required_fields` when project ≠ TC? | **QA lead per product line** (GUIDE) |

### Priority P2 (nice to have)

| ID | Topic | Summary | Decision |
|----|--------|---------|----------|
| **IQ-10** | Studio Execute batch | `POST /api/importer/execute` + UI button | **Done** |
| **IQ-11** | Coverage UI | Show matrix gaps in Creator run view | **Done** — Creator run coverage panel |
| **IQ-12** | Golden for non-TC products | Second golden corpus or filter per product line | **Done** — neutral corpus + `requirements` product + registry |
| **IQ-13** | HTML suite reports | Creator Profile B parity | **Done** — suite-report template + Studio export |
| **IQ-14** | CI for Studio | pytest + Vitest in GitHub Actions | **Done** |
| **IQ-15** | P1–P10 in GUIDE | Link design personas + MANUAL §11 | **Done** — `personas/P1-P10.md` + GUIDE § + MANUAL §11 |
| **IQ-16** | PQ-04 gate | Reviewer gate on `review_ref` | **Done** — soft warn + ack in Importer plan |
| **IQ-17** | PQ-05 redaction | Pre-Xray export lint (warn) | **Done** — export_preflight_warnings |

---

## 10. Suggested session agenda (interactive)

**Done (2026-10-12):** IQ-01–IQ-17, grill Round 1 → [GRILL-SESSION-2026-10-12.md](GRILL-SESSION-2026-10-12.md).

**Next interactive topics:**

1. **PQ-01** — Portfolio dashboard vs per-run coverage (P2 lead)  
2. **PQ-03 / CQ-02** — `test_data_isolation` in Creator config  
3. **RQ-02** — Studio parity gaps ([parity-matrix.md](parity-matrix.md))  
4. **Post-POC** — hard redaction block, execute idempotency block (grill Q2/Q4)

---

## 11. Changelog

| Date | Change |
|------|--------|
| 2026-10-12 | Initial multi-persona review; doc audit for project selector |
| 2026-10-12 | Added P1–P10 design personas, MANUAL §11 map, PQ-01–06 |
| 2026-10-12 | ADR 0002 decisions; POC/METRICS/SCORECARD docs; Studio local telemetry |
| 2026-10-12 | IQ-14 Trinity Studio CI (pytest + vitest + GHA) |
| 2026-10-12 | §2 refresh (IQ-11/13); agenda → PQ-01+; P2 wave committed |
