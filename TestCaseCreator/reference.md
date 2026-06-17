# test-case-creation — reference

## User-supplied external context (`external_context`)

When the user provides **`external_context`** (YAML parameter or explicit list in chat) with **paths** and/or **URLs**, process it in **SKILL.md §1 step 3** *before* Jira-embedded link crawling:

1. **Paths** — Read files under the workspace (or allowed absolute paths): PDF, Markdown, HTML, plain text, CSV; **images** — describe layout and flows for test expectations where relevant.
2. **URLs** — Fetch with the best available tool (`web_fetch`, Atlassian MCP, Figma MCP, etc.) consistent with permissions and safety.
3. **Failures** — Report each skipped path/URL to the user with reason; record in output **User-supplied external context** table.
4. **Conflicts** — If user material contradicts the primary Jira/bundle requirement, document in warnings / `generation_notes`; do not silently override ACs.

## Linked context (Jira and bundles)

After user-supplied context, when requirements are loaded from **Jira** (or a bundle lists external URLs not already consumed), **before** drafting tests:

1. Collect **remote links**, **issue links**, **Confluence URLs**, **Figma/design links**, **attachments**, and **plain URLs** in description, ACs, and relevant comments.
2. Resolve each using the best available tool (Atlassian MCP, Jira issue fetch, Figma MCP per product rules, `web_fetch` where allowed).
3. If resolution is **not possible**, state this **clearly to the user** (what was attempted, URL or key, reason: permissions, missing MCP, unsupported host, binary-only, timeout, etc.). Do not invent requirements from unreachable sources.
4. Summarize successes and failures in the testcase draft metadata (see SKILL.md §9).

Optional Figma-only refinement still applies when design context needs more detail after this pass.

## Gate check (requirements-review)

| Condition | Action |
|-----------|--------|
| `gate.blocks_test_generation: false` | Proceed |
| Gate `PASS` or `PASS_WITH_WARNINGS` | Proceed |
| Gate `BLOCKED` and no `force` (review artifact **present**) | **Refuse** unless user escalates with `force=true` and explicit QA confirmation |
| Gate `BLOCKED` and `force=true` + QA confirmed | Proceed; `gate_override: true` |
| No review artifact | **Proceed** — generation is always allowed; **strongly encourage** running `requirements-review` first. Record `review_artifact: none` in the output metadata and add a short **Recommendation** line to run review next time. Sample gate file: `templates/requirements-review.sample.json` |

---

## Execution tiers (P0–P3)

Assign **every test** an `execution_tier`. This is separate from Jira `priority` but mapped consistently.

| Tier | Name | `deferrable` | Run for | Skip when | Customer harm if fails |
|------|------|--------------|---------|-----------|------------------------|
| **P0** | Critical | `false` | Release gate, smoke | Never | Data loss, security breach, core feature unusable, widespread wrong data |
| **P1** | Mandatory | `false` | Full regression | Only catastrophic time crunch (document risk) | Primary admin/user workflows broken |
| **P2** | Medium | `false`* | Standard regression | Time-boxed release | Workaround exists; secondary surface degraded |
| **P3** | Deferrable | `true` | When capacity allows | Time-boxed release | Analytics/promo/cosmetic; low traffic |

\*P2 may set `deferrable: true` only with explicit `deferrable_rationale` (e.g. column layout persistence).

### Priority field mapping

| execution_tier | `priority` |
|----------------|------------|
| P0 | `Highest` or `High` |
| P1 | `High` |
| P2 | `Medium` |
| P3 | `Low` or `Lowest` |

### Customer impact (required string)

One sentence per test explaining **who hurts and how**. Examples:

- P0: "Admins cannot save policy; all users inherit incorrect access until fixed."
- P1: "Primary workflow blocked; users need a documented workaround."
- P3: "Telemetry event missing; no user-facing impact; analytics gap only."

### Deferrable rationale (required when P3 or deferrable P2)

Explain why skipping is acceptable under time pressure.

### Test data prerequisites (required on every test)

| Field | Type | Meaning |
|-------|------|---------|
| `test_data_required` | boolean | `true` if domain data (records, users, files, pre-seeded config) must exist before step 1 |
| `test_data_prerequisites` | string | Setup checklist for QA — always non-empty |

| Pattern | Typical `test_data_required` |
|---------|------------------------------|
| Create journey (builds entities during test) | `false` — environment + empty isolation context |
| Update/delete journey on existing state | `true` — known records and values per AC |
| Settings / admin mutation | `true` — existing configuration or disposable tenant |
| Single-concern test with clean entry point only | `false` |
| Search, filter, sort, aggregate, report | `true` — dataset with variety per spec |
| Access control | `true` — principals per role or tenant |
| Integration / callback | `true` — mocks, URLs, or credentials per spec |

Markdown: index column **Pre-test data**; per-test **Pre-test data required** + **Pre-test data setup**.

---

## Roles

Use **short, consistent codes** that match how QA talks about the product (`ADMIN`, `END_USER`, `VIEWER`, `API_CLIENT`, `UNAUTHENTICATED`, `SYSTEM`, etc.). The schema stores `role` as a string — pick values that appear in requirements or team conventions.

Generate **at least one test per applicable role** when the spec splits privileged vs standard access, or API vs UI.

**Example codes** from a domain-specific catalog (e.g. admin-heavy modules) may still appear in historical artifacts; reuse those literals only when they match the current requirement’s personas.

---

## Test patterns

| `test_pattern` | Max steps | When |
|----------------|-----------|------|
| `journey` | **15** | End-to-end flows: create/configure, primary task, admin paths with data dependencies |
| `atomic` | **15** | Single concern: one error path, permission boundary, API behaviour, query/report behaviour, telemetry, or other isolated behaviour named in the spec |

**Hard rule:** no test case (journey or atomic) may exceed **15** steps. Split or decompose if the flow is longer; document splits in the generation plan.

When a domain [coverage-catalog.md](coverage-catalog.md) applies, use it to decide journey vs atomic per row. Otherwise derive patterns from the run-scoped `CAT-*` checklist.

### Journey test data convention

Use a dedicated **isolation label** per journey (workspace, box, project slug, etc.) so runs do not collide:

```
{isolation_key}: {draft_id} {short summary fragment}
```

Match naming style of existing Xray tests when an extract is provided.

### Existing Xray extract as benchmark

When the user provides an extract JSON/MD:

1. Match journey **step count and surface order** for equivalent scenarios where intent aligns.
2. Set `possible_duplicate_of: TC-xxxx` when intent matches.
3. **Still satisfy** the active coverage checklist — do not shrink coverage to match an older suite if ACs require more.

---

## Coverage checklist (`CAT-*`)

Every test’s `coverage_catalog_id` must match `^CAT-[A-Z0-9-]+$` (see schema).

**Domain catalog:** If the feature matches [coverage-catalog.md](coverage-catalog.md), load applicable rows and use those ids.

**Run-scoped checklist:** Otherwise define rows in the generation plan (e.g. `CAT-ABC12345-JOURNEY-MAIN`, `CAT-ABC12345-PERM-DENY`) and cover each in `catalog_coverage`.

**`catalog_coverage[]` entry:**

```json
{
  "catalog_id": "CAT-EXAMPLE-JOURNEY-01",
  "tier": "P0",
  "covered_by": ["{Product} - {Feature} - Primary happy path"],
  "status": "Covered"
}
```

Statuses: `Covered`, `UNCOVERED`, `PARTIAL`, `N/A`.

**100% rule:** Every applicable checklist row appears in `catalog_coverage`. P0/P1 `UNCOVERED` requires `blocker` string (e.g. "AC-04 API contract TBD").

---

## Requirement input sources

| Source | How to load |
|--------|-------------|
| Normalized YAML bundle | `TestCaseCreator/requirements-template.md` (or `requirements-template.md` at package root) |
| Jira live fetch | MCP normalize |
| Epic + PRD | Map goals to `GOAL-NN` |
| Xray extract | Depth/dedup reference |

When formal AC missing: synthetic `GOAL-NN` + warning.

---

## Figma policy

Unchanged — `link-only` default. Journey tests name screens in expected results.

---

## Negative and corner case policy

**Comprehensive mode (default):** Cover negative paths, access rules, and edge cases **called out in the requirement set** or in the applicable domain catalog. Embed them in journeys when they belong to one coherent flow; otherwise use atomic tests.

| Category (examples) | Tier typical | Pattern |
|----------------------|--------------|---------|
| Required inputs or preconditions missing | P1 | atomic |
| Invalid or out-of-range values (when spec defines behaviour) | P1–P2 | journey embed and/or atomic |
| Destructive actions with warnings / confirm | P0 | journey |
| Irreversible or data-loss scenarios | P0 | journey |
| Permission denied | P0 | atomic |
| Search, filter, sort, report edge cases | P1–P2 | atomic |
| Analytics / promo / cosmetic | P3 | atomic |

If spec TBD: checklist row `UNCOVERED` + warning — **do not fabricate**.

---

## Self-check (anti-hallucination)

For each test:

1. `coverage_catalog_id` maps to a row in the active checklist (domain catalog or run-scoped `CAT-*`).
2. `execution_tier` matches customer_impact severity.
3. `test_data_required` matches the setup the steps actually need.
4. `test_data_prerequisites` is non-empty and actionable for QA.
5. Expected results traceable to `source_quotes`.
6. Journeys include every surface / transition the mapped checklist row (or AC) requires.
7. No steps for out-of-scope features.

---

## Markdown output (single file)

Always write:

`TestCaseCreator/artifacts/{JIRA-KEY} - testcase-draft.md`

Use this structure (see SKILL.md §9 for rules). Traceability sections are **required**.

```markdown
# Test case draft — {JIRA-KEY}

**Primary requirement:** {JIRA-KEY}
**Generated:** {ISO-8601}
**Golden version:** {golden_version}
**Requirements review artifact:** {path to JSON | none — review highly recommended next time}
**Gate:** {PASS | PASS_WITH_WARNINGS | BLOCKED | not_applicable_no_review_file} {gate_override note if any}
**Session inputs used:** mandatory: {bundle path | Jira fetch}; optional: {requirements-review path}, {external_context paths/urls}, {xray extract path}, {domain catalog}

## User-supplied external context

| Path or URL | Outcome | How used in tests |
|-------------|---------|-------------------|
| …/spec.pdf | Loaded | PRD §3 → journey … |
| … | Not loaded | Reason |

## Linked external context (from Jira / bundle)

| Link / attachment | Outcome | Notes for user |
|-------------------|---------|----------------|
| https://… | Fetched | Used for AC-… |
| … | Not fetched | Reason (e.g. 403, no MCP) |

## Coverage assessment

{Scope, risk, suite size justification — same substance as SKILL §3}

## Requirement → test traceability

### By AC / goal

| AC or goal id | Status | Test id(s) | Title(s) | How this requirement is exercised |
|---------------|--------|------------|----------|-------------------------------------|
| AC-01 | Covered | TC-001 | … | Journey steps 1–6; asserts … |
| AC-02 | PARTIAL | TC-002 | … | Atomic test covers happy path only; … |

### By test

| Test id | Requirement keys | AC ids | Catalog id | Traceability (quotes / mechanism) |
|---------|------------------|--------|------------|-----------------------------------|
| TC-001 | PROJ-456 | AC-01, AC-03 | CAT-… | "…excerpt…"; journey |

## Catalog / checklist coverage

| Catalog id | Tier | Status | Test(s) | Blocker |
|------------|------|--------|----------|---------|

## Execution plan

| Tier | Count | Est. hours (first run) | Deferrable | Run when |
|------|-------|------------------------|------------|----------|
| P0 Critical | N | X | No | Every release |
| … | … | … | … | … |

**Minimum release gate:** All P0 + P1 ({N} tests, ~X hours)

## Test index

| # | Id | Title | Tier | Pattern | Role | Catalog id |
|---|-----|-------|------|---------|------|------------|

---

## P0 — Critical

### TC-001: {title}
**Customer impact:** …
**Linked requirements:** …
**Linked ACs:** …
**Coverage catalog id:** …
**Pre-test data required:** Yes | No
**Pre-test data setup:** …
**Deferrable:** No
**Source quotes:** …

| Step | Action | Expected result | Test data |
|------|--------|-----------------|----------|
```

Group full step tables by tier (P0 → P1 → P2 → P3).

After the last test section, append **Appendix — TestCaseDraftBatch (JSON)**: one ` ```json ` fenced block containing the entire serialized batch (same payload a standalone JSON file would have held).

---

## Effort estimation (for execution_plan)

| Pattern | First run | Regression |
|---------|-----------|------------|
| Journey (10–15 steps) | 20–40 min | 12–22 min |
| Atomic (3–15 steps) | 8–15 min | 5–10 min |

Add 10–15% for test-box setup on first journey run.

---

## What this skill does NOT do

- Import to Xray
- Modify Jira
- Auto-approve for import
- Skip the coverage checklist pass (every applicable `CAT-*` row must appear in `catalog_coverage`)
