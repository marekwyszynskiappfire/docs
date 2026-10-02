# The Creator — action plan

**Status:** Approved for step-by-step execution (hub and staging tracked in git)  
**Date:** 2026-09-29  
**Owner:** Marek Wyszyński  
**Hub:** `The Creator/` (Input, working plan, staging under `Output/`)  
**Decision memory:** [`The Reviewer/DECISIONS.md`](../The%20Reviewer/DECISIONS.md) — append **Creator resolutions — Part 2** here (same file as Reviewer; keeps one project record)  
**Source inventory:** [`INPUT-REVIEW.md`](INPUT-REVIEW.md) Part 2 (test case creation)  
**Architecture:** [`working-plan.md`](working-plan.md) §4–§8  

---

## 1. What we are repeating

The Reviewer was delivered in a fixed rhythm. The Creator follows the same rhythm, applied to **Part 2** of the input review and to the **suite / import** payloads the working plan already names.

| Reviewer (done) | Creator (this plan) |
|-----------------|---------------------|
| `INPUT-REVIEW.md` Part 1 | `INPUT-REVIEW.md` Part 2 (written; **not** ruled on yet) |
| Resolutions → `DECISIONS.md` § Reviewer resolutions | Resolutions → `DECISIONS.md` § **Creator resolutions — Part 2** |
| Staging: `The Creator/Output/Reviewer/` | Staging: `The Creator/Output/Creator/` (scaffolded) |
| Ship package: repo-root [`The Reviewer/`](../The%20Reviewer/) | Ship package: see §3 (naming constraint) |
| `review-payload.schema.json` v1.1 | `suite-payload.schema.json` + `import-payload.schema.json` |
| `scripts/render_report.py` (review only today) | Extend renderer: **suite** + **import** report kinds |
| `SKILL.md`, `reference.md`, `checklist.md`, `MANUAL.md` | Same doc set, Creator-specific |
| Pilot Jira runs → triage doc (PRF-xx) | Pilot runs → `PERSONA-CREATOR-RUNS.md` (PRF-Cxx) |
| Gate + handoff to The Creator | **Consume** Reviewer `review_ref` + `gate` + staleness fingerprint |

**Lessons from Reviewer (carry forward):**

1. **Payload first, HTML never by the model** — agent writes JSON only; `render_report.py` owns section order, tiers, and lint rules.
2. **User confirmation on political merges** — do not inherit D20–D40 by “first skill wins”; each conflict gets an explicit ruling (U-9–U-17).
3. **Pilot before polish** — real Jira keys exposed gaps (epic child descriptions, dual Atlassian MCP, batch semantics). Budget 3–5 pilot suites before calling v1 done.
4. **PRF-style decision IDs** — each pilot-driven change gets an id in `PERSONA-CREATOR-RUNS.md` and a matching line in `SKILL.md` / `reference.md`.
5. **Strict renderer lint** — `--strict` blocks shipping a bad payload (blocked phrases, pending decisions, schema drift).
6. **Config, not skill forks** — product id, Xray project, golden path, code-grounding, isolation vocabulary live in `config/<product>.json`.
7. **Staging then promotion** — build under `Output/Creator/` until cutover; leave a short README pointer after promotion (as `Output/Reviewer/README.md` does).

---

## 2. Naming and final ship location

The hub folder is already `The Creator/`. The Reviewer shipped as a **sibling** package `The Reviewer/` because the name was free.

**Recommended v1 ship path (mirror Reviewer ergonomics):**

- **During build:** `The Creator/Output/Creator/`
- **After cutover:** repo-root **`Creator/`** (CR0, confirmed 2026-09-29). Placeholder README exists; promotion copies staging → `Creator/`.

**Decision gate (Step 0):** ~~pick one target~~ **Resolved:** CR0 = `Creator/`. Until promotion, **`The Creator/Output/Creator/`** remains `skill_root` for development.

---

## 3. Staging layout (created)

```
The Creator/Output/Creator/
  README.md                 # staging notice + link to this plan
  artifacts/.gitkeep        # run outputs (gitignored when .gitignore added)
  config/README.md          # per-product JSON; start from The Reviewer/config/default.json
  schemas/README.md         # suite + import JSON Schema (to be added)
  scripts/README.md         # render_report extension + xray import fallback
  samples/.gitkeep          # demo suite-payload + rendered suite-report.html
  runs/README.md            # committed pilot metadata policy (like Reviewer runs/)
  golden/README.md          # pointer: copy from Input/Marek/_shared/golden in Step 2
  templates/README.md       # requirement bundle + review_ref samples
  PORT-CHECKLIST.md         # rule-by-rule port table (filled in Step 1)
```

Optional later (match Reviewer): `checklist.md` (coverage catalog rules), `coverage-catalog.md` (generic + product overlays), `MANUAL.md`.

---

## 4. Phased execution

Each phase ends with a **demo you can watch** and a **done-when** checklist. Execute in order; do not skip Step 0.

### Step 0 — Ship path and scope lock (human, ~30 min)

- [x] Confirm final package path (CR0 in `DECISIONS.md`) — **repo-root `Creator/`** (2026-09-29).
- [x] Confirm v1 scope — **Epic, Story, Bug, Task**; Epic uses **one merged suite** on the Epic key (CR2); child-key runs stay per-story.
- [x] Confirm submission — **no Xray write unless explicitly requested** after human triage (CR3).
- [x] Creator-only amendments to D1–D9 / A1–A10 recorded in `DECISIONS.md` § Step 0.

**Done when:** CR0 + CR1–CR3 recorded; no open “which folder is home?” question. **Complete.**

---

### Phase 1a — Multi-persona skills review (sign-off)

**Deliverable:** [`CREATOR-SKILLS-PERSONA-REVIEW.md`](CREATOR-SKILLS-PERSONA-REVIEW.md) — all test-case creation contributions (Marek, Kacper, K&A) read through personas P1–P10, conflict register **C-01–C-15**, and ordered action list.

**Note:** `INPUT-REVIEW.md` Part 2 is the **file-level** inventory (2026-09-28). Phase 1a is the **persona synthesis** to agree what to merge before rulings and code.

- [ ] Maintainer sign-off on §4–§6 and §8 in `CREATOR-SKILLS-PERSONA-REVIEW.md`.

**Done when:** You confirm the review (or list disputes); Phase 1b may start.

---

### Phase 1b — Resolutions and port checklist

**Inputs:** `INPUT-REVIEW.md` §2.3–2.6 + [`CREATOR-SKILLS-PERSONA-REVIEW.md`](CREATOR-SKILLS-PERSONA-REVIEW.md) §5–§7.

**Work:**

1. Add **`Creator resolutions — Part 2`** to `The Reviewer/DECISIONS.md` — one ruling per row in the inventory (same discipline as Reviewer Part 1). Headline calls to decide early:
   - **CR1 — Internal id vs Xray key** (D24 / U-15): stable `draft_id` / `TC-NNN` internal only; never presented as Jira/Xray keys (Kacper).
   - **CR2 — Step model** (D23): adopt Marek/Kacper per-step `action`/`data`/`expected` as canonical; K&A single-cell steps become import/view variant only.
   - **CR2 — Epic scope** (D33): *locked Step 0* — merged suite on Epic key; per-child when scope is a child Story.
   - **CR4 — Quality axes** (T-G3): keep `execution_tier` P0–P3, add `grounding_status` (Final/Preliminary), add `traceability_priority` (High/Med/Low) as separate fields.
   - **CR5 — API / NFR tests** (U-16): policy per product config (`generate_api_tests`, `generate_nfr_tests`).
   - **CR6 — Code grounding** (U-11): optional `policy.code_grounding: required|off` per product.
   - **CR7 — Coverage %** (C3): counts in HTML; `catalog_coverage_pct` in payload only unless product config enables summary %.
   - **CR8 — Handoff** (D20): `review_ref` required unless `force` or `review_skipped` with reason; honor Reviewer `requirement_fingerprint` staleness.
2. Fill [`Output/Creator/PORT-CHECKLIST.md`](Output/Creator/PORT-CHECKLIST.md): for each rule in the three input skills → **carry | generalize | conflict-resolved | drop** with source file + DECISIONS id.
3. Copy shared assets into staging (not moved out of `Input/`):
   - `Input/Marek/_shared/schemas/TestCaseDraft.schema.json` → starting point for `suite-payload.schema.json`
   - `Input/Marek/_shared/golden/v1/` → `Output/Creator/golden/v1/`
   - `Input/Marek/_shared/scripts/xray_graphql_import.py` → `Output/Creator/scripts/` (fix step-cap drift A-22 in Phase 4)
   - `templates/*` from Marek test-case-creation → `Output/Creator/templates/`
4. Add `config/default.json` (clone Reviewer defaults; extend `xray`, `assets`, `policy` for Creator modes).

**Done when:** Port checklist reviewed; one real Marek artifact (e.g. `AI in QA/Skills/artifacts/...testcase-draft.md` appendix JSON) converts to a **schema-valid `suite-payload.json`** with no field loss (T-G10 criterion).

---

### Phase 2 — Schemas and renderer (suite + import)

**Work:**

1. Freeze **`suite-payload.schema.json`** (`payload_version` / `schema_version` aligned with Reviewer 1.1 pattern).
   - Embed `review_ref`, `context_loaded[]`, `tests[].decision`, `tests[].origin`, automation fields for P4.
   - Tighten optional-vs-required per A-24, A-25 (coverage matrix, execution_plan, draft_id).
2. Freeze **`import-payload.schema.json`** for dry-run/submit results.
3. Extend **`scripts/render_report.py`** (or `render_suite_report.py` if split — prefer **one script**, three kinds, per A2):
   - Report kind `suite`: summary band, test list, traceability matrix, catalog coverage, export gate (A6).
   - Report kind `import`: per-test action, keys, errors.
   - Progressive enhancement (D3 / C3): readable with JS off; edit/export requires JS.
4. Add `samples/demo-story.suite-payload.json` + generated `suite-report.html` committed as golden renderer output.
5. Fixture test: render → synthetic browser export → re-ingest → agent recomputes coverage (manual script or pytest in `scripts/`).

**Done when:** Demo suite renders end-to-end; export blocked while any `decision.status == pending`; `--strict` passes on sample.

---

### Phase 3 — Skill body and operator docs

**Work:**

1. Write **`SKILL.md`** (successor to Marek `test-case-creation` + K&A `story-ui-test-cases` + selected Kacper rules):
   - Modes: `generate` | `dry-run` | `submit` (A7).
   - Preconditions: Reviewer gate, fingerprint staleness, epic scope rules.
   - Logical capability table (Jira, Confluence, Xray read, Xray write, code read, Figma link-only vs reuse from review payload).
   - Paths table: all assets under `skill_root`; no `AI in QA/Skills/...` literals.
2. **`reference.md`** — tiers, roles, step cap (resolve 15 vs script 18/13), catalog 100% rule, effort table, CSV export shapes (optional views).
3. **`examples.md`** — Story with review_ref, Story without review (force), API-only story, epic child handoff.
4. **`MANUAL.md`** — QA operator guide (parallel to Reviewer MANUAL): triage loop, export approved JSON, dry-run, submit confirmation, dual MCP note (reuse Reviewer doc).
5. **`README.md`** — install paths for Cursor / Claude / Hive.

**Done when:** Fresh `generate` on a pilot issue produces only `suite-payload.json` + rendered reports under `artifacts/{run_id}/`; no hardcoded product paths in skill text.

---

### Phase 4 — Submission and import hardening

**Work:**

1. Unblock **Xray MCP** or document fallback-only for pilot product (same as Reviewer Phase 4).
2. Implement **fingerprint upsert** (T-G1): search-before-create; `updateTest` path; idempotent re-submit.
3. Batch import in `xray_graphql_import.py` (T-G2): loop, partial failure policy, import report payload.
4. Align **step limits** across SKILL, schema, script, golden examples (A-22, A-23).
5. **`dry-run` mode** in skill: `would_create` / `would_update`, no writes.
6. **`submit` mode**: preconditions from working-plan §8 (approved payload, dry-run in session, chat yes, allowlist).

**Done when:** Approved pilot suite lands in sandbox Xray with requirement links; second submit updates, does not duplicate.

---

### Phase 5 — Persona polish and automation handoff

**Work:**

1. Persona presets in suite report (P1–P4, plus P6 test-data steward via config hook T-G6).
2. Automation candidate filter + subset export (Kacper / K&A tables → payload fields).
3. Optional CSV exports (3-col and 5-col) as **views**, not canonical storage.
4. Print stylesheet; optional Jira attach guidance for sharing reports (Q7).

**Done when:** QA lead view usable without expanding every test; automation engineer can export a filtered JSON subset.

---

### Phase 6 — Pilot, parity, promotion

**Work:**

1. **Pilot matrix:** 2 stories + 1 epic child + 1 API-only story on default product config; repeat one story on Cursor and Claude (D2).
2. Capture metrics: time to approved export, edits per test, coverage counts, submit success rate.
3. Write **`PERSONA-CREATOR-RUNS.md`** — triage notes → PRF-Cxx entries → doc updates (same loop as Reviewer PRF-10…25).
4. **Promotion:** move `Output/Creator/*` to ship path (CR0); add pointer README in `Output/Creator/`; archive superseded `TestCaseCreator/` and `Input/` skills with “successor: …” lines.
5. Optional: separate git repo for the skill package (Reviewer has nested `.git`).

**Done when:** Second product onboarded with **config only**; promotion complete; operator + PM one-pagers exist.

---

## 5. Integration with The Reviewer

| Reviewer artifact | Creator use |
|-------------------|-------------|
| `review-payload.json` | `review_ref.path`, `gate.status`, `requirement_fingerprint` |
| Open `questions[]` / `findings[]` | Assumptions on tests; link `source_finding_id` / `source_question_id` |
| Epic batch | Run Creator **per** `recommended_batch_keys` child after that child’s review |
| `review-report.html` handoff block | Operator already trained; Creator MANUAL references same readiness/gate vocabulary |

**Staleness:** If fingerprint ≠ live Jira, Creator refuses `submit` and warns on `generate` unless `force` with audit fields.

---

## 6. Open questions (resolve in Step 0 / Phase 1)

Tracked in `INPUT-REVIEW.md` §2.6; blocking Phase 1 exit:

| Id | Question | Default if silent |
|----|----------|-------------------|
| U-9 | Which import contract is canonical? | GraphQL `createTest` + internal suite payload; CSV as export-only |
| U-10 | Submission in scope? | Yes, opt-in per config (off by default) |
| U-11 | Code grounding? | Off by default; `required` for Timetracker-style products |
| U-12 | P0–P3 tiers? | Keep (Marek); execution plan optional per product |
| U-15 | `TC-01` ids? | Internal `draft_id` only; display id separate from Xray |
| U-16 | API/NFR generation? | Config flags; default UI + happy-path API where AC implies it |
| U-17 | K&A → per-step conversion? | Define explicit transform; lossy paths flagged in `generation_notes` |

Working-plan Q3–Q5 remain for Phase 4–6.

---

## 7. Risks (Creator-specific)

| Risk | Mitigation |
|------|------------|
| Renderer scope doubles (3 report kinds) | One script, shared CSS shell; copy Reviewer tier patterns |
| Kacper rules unvalidated in DOCS (T-G9) | Pilot with Timetracker repo optional; generalize rules without claiming verification |
| Xray MCP still broken | Phase 4 starts with connection fix; script fallback first-class |
| Epic vs story suite semantics | CR2 (merged epic suite) vs Reviewer per-child handoff — document both in SKILL (see DECISIONS tension table) |
| `TestCaseCreator/` duplicate | Promotion step archives or merges into single package |

---

## 8. Execution log (fill as we go)

| Date | Step | Outcome |
|------|------|---------|
| 2026-09-29 | Plan + staging scaffold | `ACTION-PLAN.md`, `Output/Creator/` skeleton; no git commit |
| 2026-09-29 | Step 0 complete | CR0–CR3 + D7/D4 amendments in `DECISIONS.md`; placeholder `Creator/README.md` |
| 2026-09-29 | Part 2 rulings drafted | CV1–CV8, D20–D40, T-G*, A-22–A-45, U-9–U-17 in `DECISIONS.md` — pending your confirmation |

---

## 9. Next session (first execution step)

**Phase 1a:** Sign off [`CREATOR-SKILLS-PERSONA-REVIEW.md`](CREATOR-SKILLS-PERSONA-REVIEW.md).  
**Phase 1b:** Rulings C-01–C-14 in `DECISIONS.md`; fill `PORT-CHECKLIST.md`; copy assets into staging.
