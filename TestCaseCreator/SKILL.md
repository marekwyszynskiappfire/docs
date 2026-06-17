---
name: test-case-creation
description: >-
  Generates a single comprehensive testcase draft markdown file from approved
  requirements: assessment-first suite sizing, requirement-to-test traceability,
  journey + atomic patterns, P0–P3 execution tiers, and coverage reporting. Optional
  domain coverage catalog when one applies; otherwise a run-scoped CAT-* checklist.
  Use for Stories or Epics. Requirements-review JSON is optional but highly encouraged.
  Output is always TestCaseCreator/artifacts/{JIRA-KEY} - testcase-draft.md (includes
  appendix JSON for tooling). Accepts optional user external_context (PDFs, images,
  URLs). Does not import to Xray.
disable-model-invocation: true
---

# Test case creation

Generate a **structured, QA-ready** TestCaseDraft batch from approved requirement context, delivered as **one Markdown file** (see Output below). The skill targets **minimal QA rework**: clear traceability, realistic steps, admin and user perspectives where the spec splits them, explicit **P0–P3 execution tiers**, and a **coverage report** that shows what is covered, partial, N/A, or blocked — without assuming a fixed suite size or any particular product module.

Does **not** import to Xray.

## Session inputs (minimal)

Only the **mandatory** row is required to start. Everything else is optional. For each input type, use the linked **template or sample**.

| Input | Mandatory? | What it is | Template or sample |
|-------|------------|------------|---------------------|
| **Requirement source** | **Yes** | Either a **primary Jira key** (Epic or Story) / JQL for live fetch, **or** one normalized bundle file on disk | Bundle shape and YAML example: [`requirements-template.md`](requirements-template.md) |
| **Requirements review (gate)** | No | JSON from `requirements-review` — **highly encouraged** before generation; improves AC quality and gate signal | [`templates/requirements-review.sample.json`](templates/requirements-review.sample.json) |
| **External context (files & URLs)** | No | Workspace paths and/or URLs **you** supply (PDF, images, MD, HTML, spreadsheets, online docs) to merge with Jira/bundle before drafting tests | [`templates/external-context.sample.md`](templates/external-context.sample.md) |
| **Xray extract** | No | Existing suite export for depth and dedupe hints | [`templates/xray-extract.sample.md`](templates/xray-extract.sample.md) |
| **Domain coverage catalog** | No | Extra checklist when the feature matches that domain | [coverage-catalog.md](coverage-catalog.md) |

**Operator guide (prompts and steps):** [README.md](README.md)

**Index:** [templates/README.md](templates/README.md) lists templates including external context.

**Repository assets (loaded by the agent, not supplied as session files):** `TestCaseCreator/schemas/TestCaseDraft.schema.json`, `TestCaseCreator/golden/v1/style-rules.md`, `TestCaseCreator/golden/v1/examples/`.

## Output (single deliverable)

Write **exactly one** file per run (no separate JSON file on disk unless the user explicitly asks for an extra export):

`TestCaseCreator/artifacts/{JIRA-KEY} - testcase-draft.md`

- **`{JIRA-KEY}`** — the **primary** requirement issue key for this batch (the Epic or Story the suite is anchored to). If `scope` resolves to multiple keys, use the user-designated primary key; if none given, use the first key in `source_requirement_keys` (Epic preferred when present).
- This Markdown file is the **only** artifact QA needs: it must hold the full operation outcome, including **how each test maps to requirements** (see §9).
- **Appendix:** at the end of the same file, include one fenced `json` code block containing the full **TestCaseDraftBatch** object (valid per schema) so import or validation tools can consume it without another document. If a script expects a standalone file (e.g. `xray_graphql_import.py --batch`), save the appendix payload to a temporary `.json` path; the canonical deliverable remains the Markdown file.

## Other paths (reference)

| Resource | Path |
|----------|------|
| **Operator guide (steps + prompts)** | [README.md](README.md) |
| Reference | [reference.md](reference.md) |
| Examples | [examples.md](examples.md) |
| Optional domain catalog | [coverage-catalog.md](coverage-catalog.md) |

## Session parameters

| Parameter | Required | Notes |
|-----------|----------|-------|
| `scope` | Yes | Jira key(s), JQL, bundle path, or review artifact path |
| `run_id` | No | Correlation id for chat/logs; default to `{JIRA-KEY}` or a short timestamp if omitted |
| `jira_primary_key` | No | Overrides primary filename key when `scope` implies multiple issues |
| `golden_version` | No | Default `golden/v1` |
| `force` | No | When a **requirements-review** artifact is present and `gate.status` is `BLOCKED`, set `force=true` and QA must confirm in chat to proceed; see [reference.md](reference.md) |
| `figma_policy` | No | `link-only` (default), `export`, or `out` |
| `comprehensive` | No | Default **true** — full depth for the **assessed** scope (see workflow); not tied to a specific Epic type |
| `existing_xray_extract` | No | Path to Xray extract JSON/MD — use as depth reference and dedupe hints when available |
| `external_context` | No | Structured **or** narrative list from the user: `paths[]` (workspace-relative or absolute files: PDF, Markdown, HTML, images, CSV, etc.) and `urls[]` (docs the user wants fetched as input). Parsed from the chat message if the parameter block is omitted but the user lists files/URLs explicitly. See [templates/external-context.sample.md](templates/external-context.sample.md) and [README.md](README.md). |

## Preconditions (enforce before generating)

1. **Mandatory requirement source** resolved (see Session inputs).
2. **Gate check** — see [reference.md](reference.md). A missing requirements-review file **does not** block generation; still **strongly recommend** running `requirements-review` first and record in the output metadata when no review was used.
3. **Coverage source** — pick one or combine:
   - If the feature matches [coverage-catalog.md](coverage-catalog.md), load applicable catalog rows and instantiate them.
   - Otherwise build a **run-scoped coverage checklist**: each row gets a stable `CAT-*` id (schema pattern `^CAT-[A-Z0-9-]+$`), e.g. `CAT-PROJ-123-AC05-JOURNEY`, mapped to ACs/goals in `catalog_coverage`. Document the checklist in chat and in the output file (do not silently omit coverage rows).
4. Load repository assets: `golden/v1/style-rules.md`, **both** `golden/v1/examples/` examples (pattern only), and `schemas/TestCaseDraft.schema.json`.
5. If `existing_xray_extract` is provided, use it as a **depth benchmark** for equivalent scenarios (step granularity, naming), without shrinking traceability to the extract alone.
6. If **`external_context`** is provided (parameter or explicit user list), load each path and URL **before** drafting tests — extract text from documents, **describe** images and diagrams for expected UI/flow behaviour, fetch web pages when tools allow. Merge into the working spec. On failure, notify the user and record under output **User-supplied external context**. If user material **contradicts** Jira/bundle, document the conflict; do not silently overwrite primary ACs.

## Workflow

Execute in order. Do **not** invoke `xray-import` at the end.

### 1. Pre-flight

1. Confirm `{JIRA-KEY}` (filename), `golden_version`, and `comprehensive` (default true unless user narrows scope).
2. Acquire requirements (bundle, Jira MCP, Epic + PRD, or equivalent).
3. **Load user-supplied external context** — From `external_context` (`paths`, `urls`) **or** an explicit list in the user message: read workspace files (PDF, Markdown, HTML, text, CSV, images **describe** visuals), fetch listed URLs when permitted (`web_fetch`, Atlassian MCP, Figma MCP, etc.). Merge into the working requirement corpus. **Notify the user** for every path/URL that cannot be used (missing file, unsupported format, auth, timeout). Record outcomes in output metadata. Treat as **first-class** input alongside Jira/bundle; on **conflict** with primary requirements, note in `generation_notes` / warnings — do not fabricate resolution.
4. **Resolve linked context (Jira / bundle)** — When requirements come from **Jira** (or a bundle lists external URLs not already loaded in step 3), enumerate and follow remaining material links **before** §3–§4:
   - **Remote issue links** and **mentioned Jira keys** — fetch linked issues when tooling allows.
   - **Confluence** — open linked pages (e.g. PRD/spec) via available Confluence/Jira MCP or approved fetch; use content for ACs and scope.
   - **Design** — Figma or other design URLs: use Figma MCP / design policy per [reference.md](reference.md); cite screens in tests when retrieved.
   - **Attachments** — download or preview when the platform API or MCP exposes them; if only a filename is known, note it.
   - **Other URLs** in description, ACs, or comments — use `web_fetch` or equivalent when permitted and safe.
   - For **each** link or attachment you could not resolve, **tell the user explicitly** (URL or key, reason: no access, unsupported host, tool unavailable, binary-only attachment, etc.). Do not fail the whole run solely for a non-critical link, but do **not** invent spec from missing pages.
5. Run gate check (only if a requirements-review artifact is supplied); see [reference.md](reference.md).
6. Redact secrets; announce `{JIRA-KEY} | summary | AC/goal count` (or equivalent traceability ids).
7. Decide coverage source (domain catalog vs run-scoped `CAT-*` checklist) and list applicable items. Skip items only with explicit **N/A** + requirement quote.

### 2. Optional Figma enrichment

Applies when design context was not already satisfied in §1 steps 3–4. Same detail rules as [reference.md](reference.md). Journey tests should cite screen names in expected results when design links exist.

### 3. Coverage assessment and generation plan (mandatory chat output)

**Do not target a predetermined test count** (e.g. a fixed 35–50). Derive suite size from the requirement set and risk.

Before writing tests, publish:

1. **Linked context summary** — what was loaded from **user-supplied** `external_context` (paths/URLs) vs skipped; what was fetched from **Jira/bundle-embedded** links vs skipped (see §1 steps 3–4).
2. **Scope summary** — in/out of scope boundaries from the spec (what this batch explicitly does *not* cover).
3. **Risk and criticality** — what must work for release (data integrity, security, core user path, admin misconfiguration, integrations, etc.).
4. **Traceability inventory** — AC/goal ids (or synthesized ids if formal ACs missing — with warnings).
5. **Coverage model** — either applicable **domain catalog** rows or the **run-scoped checklist** with `CAT-*` ids; count by tier (P0/P1/P2/P3) after assignment.
6. **Patterns** — expected journey count vs atomic count and **why** (e.g. “three primary end-to-end flows + six single-concern atoms for access control, error handling, and reporting”).
7. **Roles / personas** — which perspectives the spec requires (admin, standard user, unauthenticated, API, background job actor, etc.). Use concrete `role` strings appropriate to the product; see [reference.md](reference.md).
8. **Blockers** — checklist items that will be UNCOVERED (TBD API, unknown limits, missing AC).
9. **Estimated suite size** — a **justified range or count** tied to the assessment above (e.g. “12–18 tests: 4 journeys for main workflows, 6 atoms for edge cases and access control, 2 NFR or operational checks”). Revise if the user changes scope.

### 4. Generate tests

#### 4a. Non-negotiable rules

1. **Coverage-first** — every applicable checklist row (domain catalog **or** run-scoped `CAT-*`) maps to ≥1 test with matching `coverage_catalog_id`, **or** is `UNCOVERED` / `N/A` with documented reason in `catalog_coverage`.
2. **Traceability** — `linked_ac_ids` + `source_quotes` on every test when AC ids exist; if missing, use synthetic ids + `generation_notes` warning.
3. **Do not invent requirements** — TBD specs → warning + UNCOVERED, not fabricated behaviour.
4. **Two patterns:**
   - **Journey** (`test_pattern: journey`) — coherent end-to-end paths (setup, primary use, change or teardown, cross-surface or cross-system behaviour **as the spec defines**). Max **15** steps per test; if a flow needs more, split into a second test with a clear hand-off and rationale in the generation plan.
   - **Atomic** (`test_pattern: atomic`) — single concern: one error path, permission boundary, query or filter behaviour, API contract, idempotency, telemetry, or other isolated behaviour the spec calls out. Max **15** steps (same hard cap as journeys).
5. **Roles** — populate `role`; include negative or least-privilege tests when the spec defines permission boundaries.
6. **Execution tier** — every test has `execution_tier` (P0–P3) + `customer_impact` sentence (who is harmed and how).
7. **Test data prerequisites** — every test has `test_data_required` (boolean) + `test_data_prerequisites` (string). See §4d.
8. **Deferrable** — P3 always `deferrable: true` with `deferrable_rationale`; P0 never deferrable.
9. **Corner cases** — embed in journeys or atomic tests only when the requirement or checklist calls for them (e.g. empty states, conflicts, retries, concurrency, partial failure).
10. **Golden alignment** — observable expected results; **product terminology from the current requirements**, not from sample Epics.

#### 4b. Journey tests (generic)

- Derive journeys from **named user flows** in the requirement doc: first-time use, configuration or provisioning, happy path, critical change path, destructive or irreversible actions with safeguards, cross-page or cross-module behaviour **as specified**.
- Use golden journey example only for **structure** (clear preconditions, numbered steps, expected results, isolation naming). Replace all module-specific steps (e.g. a sample product’s settings hierarchy) with steps justified by **this** scope.
- When the spec lists multiple variants (types, templates, platforms), decide whether each variant needs its own journey or one parameterized journey plus atoms — document the choice in the generation plan.

#### 4c. Admin / configuration flows (when in scope)

If requirements include configuration or policy surfaces, include journeys or atoms for the behaviours the spec names (e.g. lifecycle of a setting, propagation to consumers, rollback, who can change what) — **as the spec defines**, not from a fixed universal template.

#### 4d. Test data prerequisites (required on every test)

Before writing steps, decide whether **domain test data** must exist before step 1.

| Field | Required | Meaning |
|-------|----------|---------|
| `test_data_required` | Yes | `true` if entities, users, files, external system state, or pre-seeded records must exist **before** step 1 |
| `test_data_prerequisites` | Yes | What to prepare. Always populated — even when `test_data_required` is `false` |

**Pattern guidance (adapt labels to the product — illustrative, not exhaustive):**

| Scenario | Typical `test_data_required` | Typical `test_data_prerequisites` |
|----------|------------------------------|-----------------------------------|
| Journey that creates all needed entities inside the test | `false` | Environment-only: appropriate account, tenant/workspace, and tooling access; no pre-seeded business data if the test creates it |
| Journey that updates or deletes existing state | `true` | Pre-existing records with known values; note dependencies (e.g. referenced by another entity) |
| Admin or policy change affecting others | `true` | Existing configuration or policy; disposable context if the spec requires it |
| Single-concern test that only needs a clean entry point | `false` | Environment + navigate or invoke the entry point during the test |
| Single-concern test that needs a specific prior state | `true` | State spelled out in the AC (e.g. quota at limit, locked record, fixture file) |
| Search, filter, sort, aggregate, or report over a population | `true` | Dataset with the variety the ACs require |
| Access control (least privilege, tenant isolation) | `true` | Accounts or tokens for each role or tenant; optional pre-built context |
| Integration or webhook | `true` | Partner mock, callback URL, or credentials per spec |

**Do not conflate** with step-level `test_data` or narrative `preconditions`. `test_data_prerequisites` is the **setup checklist for QA before executing the test**.

When `existing_xray_extract` is provided and step 1 starts with preconditions, set `test_data_required: true` when appropriate and align prerequisites with that language.

#### 4e. Test object shape (required fields)

Illustrative shape (replace titles, keys, and quotes with the active requirement):

```json
{
  "draft_id": "TC-001",
  "title": "{Product} - {Feature area} - {Concise behaviour under test}",
  "linked_requirement_keys": ["ABC-12345"],
  "linked_ac_ids": ["AC-01", "AC-03"],
  "coverage_catalog_id": "CAT-ABC12345-JOURNEY-CREATE",
  "test_pattern": "journey",
  "execution_tier": "P0",
  "customer_impact": "Core deliverable — users cannot complete {primary task} if this fails",
  "test_data_required": false,
  "test_data_prerequisites": "Environment only: {role} account and {environment constraints}. No pre-seeded business data — create isolated {workspace} in step 1.",
  "deferrable": false,
  "role": "ADMIN",
  "source_quotes": ["Verbatim excerpt grounding behaviour..."],
  "objective": "Verify {primary flow} end-to-end per AC-01",
  "preconditions": "{Role} logged in; {environment notes}",
  "test_type": "Manual",
  "priority": "High",
  "steps": [
    {
      "step": "Navigate to {surface} for {isolation id}",
      "expected_result": "{Observable UI or API outcome}",
      "test_data": "{isolation id}: QA-JOURNEY-{short tag} TC-001"
    }
  ],
  "tags": ["journey", "p0-critical", "{feature-slug}"],
  "covers_design": true,
  "design_references": ["https://..."]
}
```

Run self-check from [reference.md](reference.md) on each test.

### 5. Coverage pass

Build `coverage_report` with **both**:

1. **`matrix[]`** — AC/goal id → tests → Covered | UNCOVERED | PARTIAL | N/A
2. **`catalog_coverage[]`** — checklist id (`CAT-*`) → tests → Covered | UNCOVERED | PARTIAL | N/A

**Completion rules:**

- All **P0** and **P1** checklist items must be `Covered` OR `UNCOVERED` with blocker warning (TBD spec).
- Report `catalog_coverage_pct` = covered applicable / total applicable.
- Never silently skip checklist rows.

### 6. Execution plan

Add `execution_plan` to batch JSON:

```json
{
  "execution_plan": {
    "p0_critical": { "count": 0, "estimated_hours": 0, "tests": [] },
    "p1_mandatory": { "count": 0, "estimated_hours": 0, "tests": [] },
    "p2_medium": { "count": 0, "estimated_hours": 0, "tests": [] },
    "p3_deferrable": { "count": 0, "estimated_hours": 0, "tests": [] },
    "minimum_release_gate": "All P0 + P1",
    "time_boxed_release": "P0 + P1 + selected P2; defer all P3"
  }
}
```

Estimate using [reference.md](reference.md) ranges; scale to **actual** journey/atomic counts from the assessment.

### 7. Optional deduplication

If Xray extract or MCP available: set `possible_duplicate_of` — do **not** drop checklist coverage.

### 8. Validate (in-memory, then embed)

Before writing the file:

1. Build the full **TestCaseDraftBatch** JSON (including `tests`, `coverage_report`, `execution_plan`, `validation`).
2. Validate against `schemas/TestCaseDraft.schema.json` — if invalid, fix or list errors in the Markdown **Validation** section and still document blockers; do not claim `schema_valid: true` unless fixed.
3. Every test has: `title`, `coverage_catalog_id`, `execution_tier`, `test_pattern`, `role`, `customer_impact`, `test_data_required`, `test_data_prerequisites`, `steps`.
4. Every test: **≤15 steps** (journey and atomic).
5. No forbidden phrases (style-rules §9).

### 9. Write artifact (single file)

Path (always):

`TestCaseCreator/artifacts/{JIRA-KEY} - testcase-draft.md`

Do **not** write `testcase-draft.json` alongside it unless the user explicitly requests a separate JSON export. The batch JSON lives **only** inside this file’s appendix (see below).

The Markdown body must be self-contained and **comprehensive**. Use this section order:

1. **Title and metadata** — `{JIRA-KEY}`, `generated_at`, `golden_version`, **requirements-review** path and gate status (or `not_used — review highly recommended`), **`gate_override`** if any, list of **session inputs** used, **User-supplied external context** (table: path or URL | outcome | how used in tests), and **Linked external context** from Jira/bundle (table: link | outcome | notes).
2. **Coverage assessment** — recap from §3 (scope, risk, suite size justification).
3. **Requirement → test traceability** (required) — tables that make coverage obvious:
   - **By AC/goal:** each `ac_id` (or goal id) → status (Covered / PARTIAL / UNCOVERED / N/A) → **test `draft_id` + title** that cover it → **how** (one short sentence: e.g. “journey exercises AC-02 steps 3–9; quotes: …”).
   - **By test:** each `draft_id` → `linked_requirement_keys` → `linked_ac_ids` → `coverage_catalog_id` → key `source_quotes` (abbreviate if long; full quotes in test detail).
4. **Catalog / checklist coverage** — full `catalog_coverage` table (id, tier, status, tests, blockers).
5. **Execution plan** — tier counts, hours, minimum release gate.
6. **Test index** — compact table: `# | draft_id | title | tier | pattern | role | catalog id`.
7. **Full tests** — grouped by tier (P0 first); each test includes customer impact, deferrable, test data fields, objective, preconditions, **verbatim traceability** (`source_quotes`, AC links), and step tables.

**Appendix (required):** final section `## Appendix — TestCaseDraftBatch (JSON)` with a single fenced block containing the **entire** validated JSON object (same content a standalone `testcase-draft.json` would have had).

### 10. QA triage checkpoint

**Stop.** Report:

- Path to **`TestCaseCreator/artifacts/{JIRA-KEY} - testcase-draft.md`** (the only artifact)
- Any **linked resources** the user should fix manually (auth, tools) for a future rerun
- Tests by tier (P0/P1/P2/P3) and **total count with justification**
- Catalog / checklist coverage % and UNCOVERED P0/P1 items
- Blockers / placeholders needing PM input
- Suggested **minimum release set** (P0+P1) vs **full set**

QA should **adjust tiers and placeholders**, not rebuild traceability from scratch.

## Failure handling

| Failure | Action |
|---------|--------|
| Gate BLOCKED, no `force` (review artifact **was** supplied) | **Refuse** until `force=true` + QA confirmation |
| P0/P1 UNCOVERED without blocker | Fail validation; report gaps |
| Golden/schema path missing | Abort with setup instructions |
| Schema invalid | Report errors |

## Prompting guidance

- Prefer factual, low-temperature generation.
- **Assessment before volume** — justify count; avoid padding low-value duplicates.
- **Journey before atomic** when both apply — establish end-to-end paths first, then fill atomic gaps.
- **Linked context before tests** — load **user-supplied** `external_context` (§1 step 3), then Jira/bundle links (§1 step 4); notify the user on every failure.
- Rule: If spec TBD, checklist item stays UNCOVERED with warning — do not fabricate.
- Use placeholders (e.g. `{API_BASE}`, `{LIMIT_VALUE}`, `{EXTERNAL_ID}`) with `generation_notes` when values are unknown.
- Cite AC/goal ids and `CAT-*` ids in every test.

## Output checklist

- [ ] **User-supplied external_context** (if any): every path/URL attempted; user notified of failures; summary tables in output metadata
- [ ] **Linked external context** (Jira/bundle): attempted for applicable scope; user notified of unreachable links
- [ ] Gate honored when review file present (`PASS` / `PASS_WITH_WARNINGS`, or `BLOCKED` + `force`); or no review file — proceed with **recommendation** to run review next time
- [ ] Coverage assessment in the output file; suite size justified (not a fixed default)
- [ ] Domain catalog **or** run-scoped `CAT-*` checklist loaded; instance list built
- [ ] Journeys derived from **this** requirement’s flows; golden example used as pattern only
- [ ] Atomic tests for each single-concern checklist row per spec
- [ ] Every test has `execution_tier`, `customer_impact`, `coverage_catalog_id`, `role`, `test_pattern`, `test_data_required`, `test_data_prerequisites`
- [ ] `catalog_coverage` complete; P0/P1 addressed or blocked with reason
- [ ] **Requirement → test traceability** sections complete (by AC and by test)
- [ ] **Appendix** contains full TestCaseDraftBatch JSON; batch validates against schema (or errors documented)
- [ ] Single file written: `TestCaseCreator/artifacts/{JIRA-KEY} - testcase-draft.md` (no extra files)
- [ ] Did **not** run xray-import

## Additional resources

- Input templates index: [templates/README.md](templates/README.md)
- Optional domain catalog: [coverage-catalog.md](coverage-catalog.md)
- Tiers, roles, markdown templates: [reference.md](reference.md)
- Samples: [examples.md](examples.md)
