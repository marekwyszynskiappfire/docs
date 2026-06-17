# test-case-creation — examples

Illustrations below use one historical Epic and domain catalog as **concrete samples**; other requirements use the same workflow with a run-scoped `CAT-*` checklist and a **justified** suite size (see [SKILL.md](SKILL.md) §3).

## Example 1 — Refuse when gate BLOCKED

**Context:** Optional `requirements-review` artifact has `gate.status: BLOCKED` (see [`templates/requirements-review.sample.json`](templates/requirements-review.sample.json) for a passing sample).

**Agent response:**
```
Cannot run test-case-creation: requirements review gate is BLOCKED (3 CRITICAL findings).
See: path/to/requirements-review-summary.md

Options:
1. PM resolves CRITICAL findings and re-run requirements-review
2. QA sets force=true with explicit acknowledgment
```

---

## Example 1b — No requirements-review file (still allowed)

**Context:** User supplies only `scope=PROJ-456` (Jira); no `requirements-review.json`.

**Agent:**

1. State that **`requirements-review` is highly recommended** before next run; generation proceeds.
2. Run §1 linked-context pass on the Jira issue (Confluence, linked issues, Figma, URLs); report any link that could not be fetched.
3. Continue with assessment and tests; output metadata includes `review_artifact: none` and **Recommendation** to run review later.

---

## Example 2 — Assessment-first plan (before generation)

**Input:** Epic ONE-232514 + PRD + `6113-extraction.json` as depth reference; domain catalog applies.

**Agent plan (chat):**
```
Scope: admin-defined fields × 7 types, settings CRUD, permissions, overview/table extras, API (TBD), telemetry — in scope per PRD.

Risk: misconfiguration and data loss on delete are P0-class; analytics P3.

Coverage: domain catalog → 42 applicable rows (N/A items excluded with quotes).
  P0: 14 | P1: 16 | P2: 8 | P3: 4

Suite shape: 14 journey + 28 atomic = 42 tests (1:1 with catalog rows for this Epic type — not a default size for other features).

Blockers: CAT-API-* UNCOVERED (GOAL-03 TBD); `{UNKNOWN_CONFIG}` placeholder until PM confirms

Effort (first run): ~18–24 h total; P0+P1 ~14 h minimum release gate
```

---

## Example 3 — Journey test (P0 create Text)

See [golden/v1/examples/example-journey-create-text.md](golden/v1/examples/example-journey-create-text.md).

**JSON fragment:**
```json
{
  "draft_id": "TC-001",
  "title": "SPM - OKR - Creating Text type custom field",
  "coverage_catalog_id": "CAT-CREATE-TEXT",
  "execution_tier": "P0",
  "test_pattern": "journey",
  "role": "OKR_ADMIN",
  "customer_impact": "Customers cannot create or use Text custom fields across OKR views",
  "test_data_required": false,
  "test_data_prerequisites": "Environment only: OKR Admin, staging tenant, feature enabled per test plan. Empty dedicated test box (step 1).",
  "deferrable": false,
  "linked_requirement_keys": ["ONE-232514"],
  "linked_ac_ids": ["GOAL-01", "GOAL-02-TYPES"],
  "priority": "High",
  "steps": [
    {
      "step": "Navigate to OKR Settings → Fields for boxName",
      "expected_result": "Fields settings page displays with Create new button",
      "test_data": "boxName: QA-JOURNEY-CREATE-TEXT TC-001"
    }
  ],
  "tags": ["journey", "p0-critical", "field-type-text"],
  "possible_duplicate_of": "TC-6117"
}
```

---

## Example 4 — Atomic P3 deferrable (Amplitude)

```json
{
  "draft_id": "TC-042",
  "title": "Amplitude event fired when OKR Admin creates custom field",
  "coverage_catalog_id": "CAT-AMP-CREATE",
  "execution_tier": "P3",
  "test_pattern": "atomic",
  "role": "OKR_ADMIN",
  "customer_impact": "No user-facing impact; product analytics gap only",
  "deferrable": true,
  "deferrable_rationale": "Instrumentation failure does not block OKR workflows; defer when release timeline is tight",
  "priority": "Low",
  "generation_notes": "Event name assumed — confirm with instrumentation spec",
  "steps": [
    {
      "step": "Create a Text custom field as OKR Admin with analytics capture enabled",
      "expected_result": "Amplitude receives `{EVENT_FIELD_CREATED}` with field type and goal types",
      "test_data": ""
    }
  ],
  "tags": ["amplitude", "p3-deferrable", "instrumentation"]
}
```

---

## Example 5 — Catalog UNCOVERED with blocker (API TBD)

```json
{
  "catalog_id": "CAT-API-DEFINITIONS",
  "tier": "P1",
  "status": "UNCOVERED",
  "blocker": "GOAL-03 API endpoint TBD per requirements review RR-ONE-232514-02",
  "covered_by": []
}
```

**Warning in batch:**
```json
"warnings": [
  "3 API catalog items UNCOVERED — endpoint contract not in requirements",
  "Formal AC missing — coverage mapped to GOAL-01..GOAL-06"
]
```

---

## Example 6 — Execution plan in batch JSON

```json
{
  "execution_plan": {
    "p0_critical": {
      "count": 14,
      "estimated_hours": 8.5,
      "tests": ["SPM - OKR - Creating Text type custom field", "..."]
    },
    "p1_mandatory": {
      "count": 16,
      "estimated_hours": 6.0,
      "tests": ["SPM - OKR - Updating Text custom field values across OKR views", "..."]
    },
    "p2_medium": { "count": 8, "estimated_hours": 2.5, "tests": [] },
    "p3_deferrable": { "count": 4, "estimated_hours": 1.0, "tests": [] },
    "minimum_release_gate": "All P0 + P1 (30 tests, ~14.5 hours first run)",
    "time_boxed_release": "P0 + P1 + selected P2; defer all P3"
  }
}
```

---

## Example 7 — force override after BLOCKED review

**User:** `force=true — generate comprehensive draft for QA workshop`

**Agent:**
1. Confirm QA intent.
2. Set `gate_override: true`.
3. Run full catalog pass; extra warnings per CRITICAL finding.
4. Still mark API catalog UNCOVERED if TBD — do not fabricate.
5. Do **not** auto-run xray-import.

---

## Example 8 — Regeneration with Xray extract reference

**User:** `Regenerate comprehensive suite for ONE-232514 using 6113-extraction.json as benchmark`

**Agent:**
1. Load `6113-extraction.json`.
2. Match journey depth for CAT-CREATE-* and CAT-UPDATE-* items.
3. Set `possible_duplicate_of` where intent aligns.
4. Add atomic tests for catalog items absent from Xray (e.g. overview filters, permission breadth) when the domain catalog lists them.
5. Output execution plan highlighting minimum release set vs full suite.
6. Write the single deliverable: `TestCaseCreator/artifacts/ONE-232514 - testcase-draft.md` (traceability sections + appendix JSON).

---

## Example 9 — Output path (always)

**After a successful run:**

- **Only file:** `TestCaseCreator/artifacts/{JIRA-KEY} - testcase-draft.md`
- Example: `TestCaseCreator/artifacts/PROJ-456 - testcase-draft.md`
- No separate `testcase-draft.json` unless the user explicitly requests an extra export; the JSON batch is inside the Markdown appendix.

---

## Example 10 — `external_context` (PDF + image + URL)

**User prompt excerpt:**

```text
scope: PROJ-789
external_context:
  paths:
    - AI in QA/Specs/PROJ-789-prd.pdf
    - AI in QA/mockups/error-state.png
  urls:
    - https://confluence.example.com/display/PROJ/Error+handling
```

**Agent:**

1. Run §1 step 3: read PDF and image paths; fetch URL; record failures in chat and in **User-supplied external context** in the output file.
2. Continue with Jira fetch for `PROJ-789` and §1 step 4 link crawl.
3. Generate tests citing PRD / mockup / Confluence where they add acceptance detail; keep `linked_requirement_keys` anchored to `PROJ-789`.
