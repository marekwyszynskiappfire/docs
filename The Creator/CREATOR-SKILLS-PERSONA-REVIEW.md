# Test case creation skills — multi-persona review

**Status:** Ready for discussion and rulings (feeds Phase 1 decisions)  
**Date:** 2026-09-29  
**Method:** Read all contributed **test-case creation** skills and their supporting assets; evaluate through ten personas; cross-check [`INPUT-REVIEW.md`](INPUT-REVIEW.md) Part 2 (file-level inventory, 2026-09-28).  
**Not in scope here:** Re-running Reviewer (`requirements-review`, `story-testability`) — those feed Creator as **inputs**, not as merge sources for suite shape.  
**Locked already:** Step 0 in [`ACTION-PLAN.md`](ACTION-PLAN.md) / [`The Reviewer/DECISIONS.md`](../The%20Reviewer/DECISIONS.md) (CR0–CR3).

---

## 1. Is Phase 1 “reviewing all creation skills”?

**Partially.**

| What | What it is |
|------|------------|
| **`INPUT-REVIEW.md` Part 2** | Already a **line-by-line** inventory: similarities, D20–D40, gaps T-G1–T-G12, ambiguities A-22–A-45, uncertainties U-9–U-17, and a short persona table. |
| **Original Phase 1 in `ACTION-PLAN.md`** | **Not** a second full read — it assumes Part 2 exists and focuses on **DECISIONS rulings**, **PORT-CHECKLIST**, and **copying assets** into staging. |
| **This document** | The **multi-persona synthesis** you asked for: who each skill serves, where they clash, what **The Creator** must become, and an **ordered action list** before we edit schemas or SKILL bodies. |

**Recommendation:** Treat this file as **Phase 1a (review sign-off)**. Phase 1b is rulings + port checklist + asset copy, using §6 below as the agenda.

---

## 2. Inventory — what was reviewed

### Test-case creation (merge sources)

| Contributor | Primary skill(s) | Lines (approx.) | Role in pipeline |
|-------------|------------------|-----------------|------------------|
| **Marek** | `test-case-creation/SKILL.md` + `reference.md`, `coverage-catalog.md`, `examples.md`, templates | ~1,400+ skill stack | **Payload-first** suite: Markdown + JSON appendix, P0–P3, `CAT-*`, optional Reviewer JSON gate |
| **Kacper** | `TestCaseWriting/SKILL.md` | ~400 | **Timetracker manual** cases: 3-col Xray CSV, code-grounded Final draft, nine-item identifier gate |
| **Kacper** | `AutomatingTestCases/SKILL.md` | ~440 | **Downstream automation** (Playwright), not manual suite generation — handoff from approved `TTQA-*` |
| **K&A** | `story-ui-test-cases-SKILL.md` | ~360 | **Scan-dependent** UI tables, `TC-01` ids, Figma reuse, per-child epic flow |

### Supporting assets (Marek — part of Creator contract)

| Asset | Purpose |
|-------|---------|
| `TestCaseDraft.schema.json` | Machine contract (basis for `suite-payload`) |
| `golden/v1/style-rules.md` + examples | Style baseline (currently SPM-heavy) |
| `xray_graphql_import.py` | Submit fallback (create-only today) |
| `jira_xray_mapping.json` | Product-specific Xray/Jira field map |
| `requirements-template.md` | Full requirement bundle for generation |

### Hard dependency (K&A creation, not merged as Creator core)

| Skill | Relationship |
|-------|----------------|
| `story-testability` (`TestabilityScanner.MD`) | **Mandatory in chat** for K&A TC skill; merged Creator should use **persisted `review-payload.json`** from The Reviewer instead of same-chat scan state. |

### Explicitly not copied (Kacper — evidence only)

Per `Kacper/SOURCE.md`: Playwright specs, `jiraIssueIds.json`, E2E emails, `parallelTestDateIsolation.ts` — rules are **generalised**, not validated in DOCS.

---

## 3. Contributor summaries (what each optimises for)

### Marek — `test-case-creation`

**Strengths:** Only contribution with a **validated JSON batch** and coverage accounting; **assessment-first** suite sizing; **Epic-anchored merged suite** (matches your CR2); API/CSV/feature-flag paths in catalog; **execution plan** for leads; explicit link to Reviewer gate (JSON); import script exists.

**Weaknesses:** Output is **prose-first** — no interactive triage UI; hardcoded `AI in QA/Skills/...` paths; schema weaker than SKILL prose (A-24–A-28); step cap **15** vs import script **13/18** (A-22); golden library **OKR-only** (T-G7); no automation handoff skill; no code grounding.

**Best personas:** P1 (structure), P2 (effort/gate), P5 (schema anchor).

---

### Kacper — `TestCaseWriting` + `AutomatingTestCases`

**Strengths:** **Runnable steps** (Data cell must execute alone); strongest **identifier anti-invention**; **code/UI authority** for Final draft; **risk-layered** coverage without fixed catalog; **P4** automation path is the only complete one; **P6** parallel date isolation documented in source repo; self-contained **skills-overview.html** (D1 prior art).

**Weaknesses:** **No JSON suite**; Timetracker-specific (`TTQA-*`, `KAN-*`, real emails — **P9** conflict); blocks auto-import (aligned with CR3); **disable-model-invocation: false** (A-36); epic scope undefined; forbids `TC-01` labels (D24); cannot be run end-to-end in DOCS (T-G9).

**Best personas:** P4, P6; P1 for step discipline.

---

### K&A — `story-ui-test-cases`

**Strengths:** Tight **traceability to F#/Q#**; **ID stability** across regeneration (D38); **Figma** expected values without re-fetch; **5–15** manual + E2E candidate table; Hive execution contract; aligns with Reviewer **readiness** vocabulary for Final/Preliminary.

**Weaknesses:** **Chat-coupled** to scan (A-42); **one Expected per case** vs per-step CSV (A-41); **forbids merged epic table** (conflicts **CR2**); UI-only; no payload; blocked word **“gate”** (A-44); HTML report for TCs unspecified (A-43).

**Best personas:** P1 (story-level UI focus), P7 (Figma), P3 indirectly via linked questions on tests.

---

## 4. Persona-by-persona read

Legend: **S** served well today · **P** partial · **G** gap in all inputs · **M** must be in merged Creator

| Persona | What they need from test **creation** | Marek | Kacper | K&A | Merge must-have (M) |
|---------|----------------------------------------|-------|--------|-----|------------------------|
| **P1 QA engineer** | Fast triage, edit wrong tests, trace to AC, clear data setup | P — prose/JSON, no UI | S — CSV runnable | S — tables, assumptions | **M:** HTML suite report + payload decisions; approve/reject/export (D3, A6) |
| **P2 QA lead / manager** | Coverage picture, tier mix, effort, release gate, risk | S — execution_plan | G | P — priority from F# only | **M:** Summary band (counts; % in payload per CR7); P0–P3 kept (U-12) |
| **P3 PM / BA** | Understand what was assumed; answer linked questions | P — generation_notes | G | S — Q#/F# on rows | **M:** Surface open Reviewer questions on tests; no “gate” jargon in HTML (A-44) |
| **P4 Automation engineer** | Candidates, stability, pattern, handoff | G | S — AutomatingTestCases | P — E2E table | **M:** `automation_candidate`, `suggested_level`, `test_pattern`, export subset (Phase 5) |
| **P5 Skill maintainer** | One contract, port checklist, versioned rules | S — schema | P — CSV rules | P — scan coupling | **M:** `suite-payload` + DECISIONS Part 2 + PORT-CHECKLIST |
| **P6 Test-data steward** | Isolation, shared users, parallel workers | P — prose prerequisites | S — isolation bands | G | **M:** Config hook `test_data_isolation` (T-G6); never invent users (Kacper generalised) |
| **P7 UX designer** | Design-linked expectations, mismatch visibility | P — link-only Figma | G | S — Figma strings from scan/review | **M:** Reuse design facts from `review-payload` / bundle; no mandatory Figma MCP in Creator if Reviewer ran |
| **P8 Release manager** | Epic rollout, batch of stories, status mix | S — epic merged suite (CR2) | G | P — per-child only in skill text | **M:** Epic scope flag on payload; merged suite + optional child scope; align MANUAL with Reviewer batch |
| **P9 Security / compliance** | No secrets/PII in shared artifacts | S — redaction culture (Reviewer) | **Conflict** — real emails in steps (A-38) | G | **M:** Policy: sandbox emails or placeholders in **exported** reports; config for allowed test accounts |
| **P10 Platform / MCP admin** | See what failed to load | P — abort vs degrade (Reviewer fixed) | G | S — source status idiom | **M:** `context_loaded[]` on suite payload (same as Reviewer) |

### Persona headlines (one line each)

- **P1:** Nobody gives a **triage UI**; Marek is closest on structure; Creator’s main job is **interactive report + payload**.
- **P2:** Only Marek plans **hours and release gate**; leads need summary without opening every test.
- **P3:** K&A links tests to **open questions**; PM still lives mostly in Reviewer, not Creator.
- **P4:** **Kacper owns automation**; Marek/K&A only label candidates — payload fields are non-negotiable.
- **P5:** Three incompatible **id and quality models** — DECISIONS must pick one canonical shape with export views.
- **P6:** Critical knowledge sits in **one private repo** — config vocabulary or lose it.
- **P7:** K&A + Reviewer Figma path; Creator should **consume**, not re-fetch.
- **P8:** **CR2 (merged epic)** favours Marek over K&A TC epic rule — document in SKILL and examples.
- **P9:** **Email-in-steps vs redaction** needs a written policy before pilot.
- **P10:** Copy Reviewer’s **context_loaded** pattern into suite generation.

---

## 5. Conflict register (act on these in Phase 1b)

Already **locked** (Step 0): CR0 ship path, CR1 issue types, **CR2 merged epic suite**, **CR3 no submit unless explicit**.

| ID | Conflict | Inputs | Recommended ruling for Phase 1b | Personas most affected |
|----|----------|--------|--------------------------------|-------------------------|
| **C-01** | Internal `TC-NNN` vs “never TC-01” vs summary-as-id | D24, U-15 | Internal `draft_id` only; Xray key only after submit; CSV export uses Summary | P1, P5 |
| **C-02** | Per-step vs one-cell steps | D23, U-17 | Canonical: Marek/Kacper step objects; K&A table is **legacy view**; conversion may flag `generation_notes` | P1, P4 |
| **C-03** | Merged epic vs per-child only | D33 vs **CR2** | **CR2 wins**; K&A per-child flow remains for `scope.type=story` | P8, P1 |
| **C-04** | Three quality axes | T-G3 | `execution_tier` + `grounding_status` + `traceability_priority` independent | P2, P1 |
| **C-05** | Code grounding | U-11 | `policy.code_grounding: off` default; `required` for code-in-repo products | P4, P1 |
| **C-06** | API / NFR tests | U-16, T-G5 | Config flags; default UI + API when AC implies; NFR row in generic catalog optional | P2, P8 |
| **C-07** | Coverage % in HTML | C3, U-12 | Counts in report; % only in payload or if config enables | P2, P3 |
| **C-08** | Reviewer handoff | D20 | `review_ref` required unless `review_skipped` + reason; fingerprint staleness | P1, P5 |
| **C-09** | Real emails in steps | A-38 | Export/redaction policy; config `test_accounts` for sandbox literals | P9 |
| **C-10** | Submit vs inputs forbid write | U-10, D4, CR3 | Generate never writes; submit explicit + approved payload | P1, P9 |
| **C-11** | CSV as canonical vs GraphQL | U-9 | **Suite payload canonical**; 3- and 5-col CSV as export-only | P1, P4 |
| **C-12** | K&A “gate” blocked word | A-44 | User-facing copy avoids “gate”; technical `review_ref.gate` in payload only | P3 |
| **C-13** | Scan-in-chat prerequisite | D20, A-42 | Replace with **Reviewer JSON file** + optional force | P1, P5 |
| **C-14** | Step cap 15 vs script 13/18 | A-22, A-23 | Single cap in DECISIONS; fix script + golden in Phase 4 | P5 |
| **C-15** | Upsert / update tests | T-G1, T-G2 | Phase 4; not blocking schema freeze | P1, P10 |

---

## 6. What “The Creator” should be (target picture)

Synthesis across personas and your Step 0 choices:

1. **Single machine contract:** `suite-payload.json` (evolve Marek schema), versioned like Reviewer 1.1.
2. **Human interface:** Self-contained **suite-report.html** with per-test decisions and export gate (CR3).
3. **Inputs:** Jira/Confluence/bundle + **`review-payload.json`** (replaces K&A same-chat scan) + optional Xray extract + config.
4. **Scope:** Epic → **one merged suite** (CR2); Story/Bug/Task → single-issue suite; API-only → bullets/focus areas, no step table (union of Marek + K&A rules).
5. **Quality:** Three explicit fields (C-04); Reviewer gate respected (C-08); no Xray write on generate (CR3).
6. **Exports:** GraphQL submit path + **CSV views** (Kacper 3-col, K&A 5-col) without making CSV canonical (C-11).
7. **Automation:** Payload carries candidate metadata; **AutomatingTestCases** stays a **separate** product skill, not inside Creator v1 (P4).
8. **Ops:** `context_loaded[]`, config-driven golden/catalog, generalised identifier rules from Kacper.

**Explicit non-goals for v1:** Replacing Playwright skill; validating Timetracker specs in DOCS; mandatory code grounding for all products.

---

## 7. Ordered action list (start acting here)

Use this as the Phase 1b agenda after you sign off §4–§6.

| # | Action | Owner | Output |
|---|--------|-------|--------|
| 1 | **Sign off** this persona review (or mark sections disputed) | You | Comment in chat / short note in DECISIONS session log |
| 2 | Record **C-01–C-14** as CV1–CV8 + D20–D40 in `DECISIONS.md` § Creator resolutions — Part 2 | Done 2026-09-29 — **confirm or overturn** per row | Ruling table |
| 3 | Resolve **P9** email policy (C-09) with security/QA preference | You | One paragraph in DECISIONS |
| 4 | Fill **`PORT-CHECKLIST.md`** using Part 2 + this doc | Agent | Complete checklist |
| 5 | Copy golden, schema seed, templates, script into **`Output/Creator/`** | Agent | Staging tree populated |
| 6 | Draft **`config/default.json`** (Reviewer clone + Creator policy keys) | Agent | Config file |
| 7 | Convert one **ONE-232514** (or similar) appendix → **`suite-payload.json`** | Agent | Phase 1 exit fixture |

Then proceed to **Phase 2** (schema freeze + renderer) per `ACTION-PLAN.md`.

---

## 8. Sign-off checklist (for you)

- [ ] Persona coverage in §4 reflects how your team actually works (add/remove personas if needed).
- [ ] **CR2 merged epic** vs K&A per-child skill text — accept tension in C-03.
- [ ] **Kacper** rules generalised without claiming Timetracker validation in DOCS — accept T-G9.
- [ ] **AutomatingTestCases** stays separate from Creator v1 — accept §6 item 7.
- [ ] Ready to turn §7 into DECISIONS + PORT-CHECKLIST (Phase 1b).

---

## 9. Relationship to other docs

| Document | Role |
|----------|------|
| [`INPUT-REVIEW.md`](INPUT-REVIEW.md) Part 2 | Evidence and line-level citations |
| [`CREATOR-SKILLS-PERSONA-REVIEW.md`](CREATOR-SKILLS-PERSONA-REVIEW.md) (this file) | **Persona synthesis + action agenda** |
| [`ACTION-PLAN.md`](ACTION-PLAN.md) | Phases 2–6 execution |
| [`The Reviewer/DECISIONS.md`](../The%20Reviewer/DECISIONS.md) | CR0–CR3 done; C-01–C-14 pending |
