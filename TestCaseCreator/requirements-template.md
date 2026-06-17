# Ideal requirement input template (LLM ingestion for test case creation)

This file defines a **canonical shape** for requirement data fed into an LLM (directly or after normalization from Jira). It aligns with downstream **TestCaseDraft** expectations (`schemas/TestCaseDraft.schema.json` in this package).

> **Standalone package:** If sibling initiative docs are not in your repo, ignore any historical cross-links in copies of this file; the YAML structure below is authoritative.

**Rules of use**

- One file **= one primary work item** (Epic **or** Story). For Epics, optionally embed **child stories** under `children` when the LLM session is scoped to the Epic.
- Use **explicit empties**: `null`, `[]`, or the string `"N/A"` — never omit a **required** key. Unknown values block generation until resolved.
- **Redaction:** Replace secrets/PII per governance; keep structure identical.

---

## 1. Required top-level sections (checklist)

| Section | Why the LLM needs it |
|---------|----------------------|
| `document` | Versioning, traceability, audit (`bundle_id`, `schema_version`). |
| `work_item` | Identity, type, status — anchors tests to Jira keys and scope. |
| `summary` | One-line intent; titles tests and disambiguates duplicates. |
| `description` | Context, actors, background — informs scenarios and data. |
| `acceptance_criteria` | Primary source of **pass/fail** tests; must be atomic and testable. |
| `scope` | In/out — reduces hallucinated negative tests. |
| `testability` | Data, states, interfaces, environments — turns ACs into executable steps. |
| `traceability` | Parent Epic, design links — coverage and NFR/design tests. |

**Strongly recommended** (mark `N/A` if truly not applicable): `constraints`, `non_functional`, `dependencies`, `open_questions`, `attachments_index`, `glossary`.

---

## 2. Ideal data file — YAML (normative example)

Copy this block as `PROJ-456.requirement.yaml` (or equivalent). Replace placeholder content; keep all keys.

```yaml
# =============================================================================
# Canonical requirement record for LLM → TestCaseDraft generation
# =============================================================================

document:
  schema_version: "1.0"                    # bump when structure changes
  bundle_id: "bundle-2026-05-11-001"         # extraction / session batch id
  source_system: "Jira"
  extracted_at: "2026-05-11T14:00:00Z"
  redaction_applied: false                 # true if secrets/PII stripped
  language: "en"                           # primary language of text fields

work_item:
  jira_key: "PROJ-456"                     # REQUIRED — pattern per org
  issue_type: "Story"                      # "Story" | "Epic" | (custom type name)
  project_key: "PROJ"
  summary: >-
    Short imperative title: what the user can do after this is delivered.
  status: "In Progress"                    # workflow state for context only
  priority: "High"
  labels:
    - payments
    - api
  components:
    - Checkout Service
  fix_versions:
    - "Release 9.0"

# Parent when work_item is a Story; null for top-level Epic
parent:
  epic_key: "PROJ-100"
  epic_summary: "N/A"                     # or short echo for LLM context

summary: >-
  One paragraph (3–6 sentences): problem, user, outcome. No paste of full AC here.

description: |-
  ## Context
  Who is affected and why now.

  ## Current behaviour
  What happens today (symptoms, metrics).

  ## Desired behaviour
  What should happen after delivery (business outcome).

  ## Flow (bullet or numbered)
  1. User opens …
  2. System calls …
  3. User sees …

  ## Out of scope (explicit)
  - …

acceptance_criteria:
  format: "Gherkin"                       # "Gherkin" | "checklist" | "mixed"
  items:
    - id: "AC-01"
      text: |-
        Given a logged-in customer with a saved card
        When they submit checkout for a cart total under the contactless limit
        Then payment is authorized without step-up challenge
        And order status becomes "Paid"
      testable: true
      priority: "must"
    - id: "AC-02"
      text: |-
        Given a cart over the contactless limit
        When the customer submits checkout
        Then the flow requires step-up authentication before authorization
      testable: true
      priority: "must"

scope:
  in_scope:
    - "REST POST /v1/checkout/authorize behaviour for happy path and decline codes A1, A2"
    - "UI confirmation screen for success and soft-decline retry"
  out_of_scope:
    - "3DS step-up UI internals (owned by Identity team)"
    - "Reporting dashboards"

constraints:
  regulatory: []
  business_rules:
    - id: "BR-01"
      text: "Contactless limit is configurable per merchant; use staging value 100 EUR."
  technical:
    - "Idempotency-Key header required on authorize; duplicate requests return same outcome."

testability:
  environments:
    - name: "staging"
      base_url: "https://api-staging.example.com"
      notes: "Test merchant MT-001; cards in 1Password vault QA-Checkout"
  personas:
    - id: "customer"
      description: "Registered B2C shopper with saved card"
    - id: "admin"
      description: "N/A"
  data:
    fixtures:
      - id: "CARD_OK"
        description: "Visa that returns authorized in sandbox simulator"
      - id: "CARD_DECLINE_A1"
        description: "Card that returns decline code A1"
    enumerations:
      order_status:
        - "Draft"
        - "Paid"
        - "Failed"
  apis:                                     # empty list if UI-only
    - name: "Authorize checkout"
      method: "POST"
      path: "/v1/checkout/authorize"
      idempotent: true
      relevant_error_codes:
        - code: "A1"
          meaning: "Insufficient funds (example)"
  ui:
    screens:
      - name: "Checkout confirmation"
        route_or_url: "/checkout/confirm"
    figma_or_design_links:
      - "https://www.figma.com/file/…"     # or "N/A"

non_functional:
  performance: >-
    P95 authorize call < 800 ms under nominal load (staging SLO).
  security: >-
    PCI scope unchanged; no PAN in logs; follow OWASP API top 10 for input validation.
  accessibility: "N/A"
  observability: >-
    Structured log field `checkout_session_id` must propagate to authorize span.

dependencies:
  upstream:
    - jira_key: "PROJ-400"
      relationship: "depends on"
      note: "Payment token service must be on v2 in staging"
  downstream: []
  external_systems:
    - name: "Acquirer simulator"
      owner_team: "Platform"

traceability:
  related_jira_keys:
    - "PROJ-401"                            # bugs, spikes, design tasks
  confluence_or_doc_links:
    - "https://confluence.example.com/…/Checkout+authorize"
  design_references:
    - type: "figma"
      url: "https://www.figma.com/file/…"

open_questions:
  - id: "OQ-01"
    text: "Retry policy after soft-decline — max attempts?"
    blocking: true
    owner: "PM"
  - id: "OQ-02"
    text: "Copy for decline messaging — final from UX?"
    blocking: false
    owner: "UX"

assumptions:
  - "Staging acquirer returns same codes as contract table v3.1"

attachments_index:                        # names/types only if binaries redacted
  - name: "authorize-sequence.png"
    type: "image/png"
    jira_attachment_id: "12345"

glossary:
  soft_decline: "Recoverable decline where user may retry with different instrument"

# Optional: only when file represents an Epic and session is Epic-scoped
children: []
#  - jira_key: "PROJ-457"
#    summary: "…"
#    acceptance_criteria: { format: "checklist", items: [ … ] }
```

---

## 3. Same structure as Markdown (human-first variant)

If you use **markdown** instead of YAML, keep **these headings** in order so parsers (and humans) stay aligned:

1. `# {jira_key} — {summary}`  
2. `## Metadata` — schema version, bundle id, source, extracted at, redaction flag  
3. `## Work item` — key, type, project, status, priority, labels, components, fix versions  
4. `## Parent Epic` — key + summary (or “N/A”)  
5. `## Summary` — short paragraph  
6. `## Description` — context, current/desired, flow, explicit out-of-scope  
7. `## Acceptance criteria` — numbered ACs; each line testable  
8. `## Scope` — In scope / Out of scope  
9. `## Constraints` — regulatory, business rules, technical  
10. `## Testability` — environments, personas, fixtures, enums, APIs, UI  
11. `## Non-functional requirements`  
12. `## Dependencies` — Jira keys + systems  
13. `## Traceability` — links, related keys  
14. `## Open questions` — blocking flag + owner  
15. `## Assumptions`  
16. `## Attachments` — index only if redacted  
17. `## Glossary`  

---

## 4. Field mapping hints (Jira → template)

Map your Jira **custom** and **system** fields into the YAML keys above; store the mapping in `jira_xray_mapping` (Epic 07). Typical mapping:

| Jira (examples) | YAML path |
|-----------------|-----------|
| Summary | `work_item.summary` |
| Description | `description` |
| Acceptance Criteria (custom field) | `acceptance_criteria` |
| Epic Link / parent | `parent.epic_key` |
| Labels, Components, Fix Version/s | `work_item.labels` / `components` / `fix_versions` |
| Priority | `work_item.priority` |
| Attachments | `attachments_index` |
| Linked issues / “depends on” | `dependencies` |

Priority order when several fields overlap (e.g. AC in custom field **and** bullets in Description): define once in your **inventory** (Epic 01) and **repeat that rule** in `document.notes` if needed.

---

## 5. Quality bar before sending to the LLM

- Every **must** AC is **testable** without inventing product behaviour.  
- **Open questions** with `blocking: true` are resolved or explicitly waived with approver.  
- **API/UI** sections contain enough **concrete** names (paths, screens, codes) to write steps and expected results.  
- At least one **traceability** link back to design or spec exists **or** `traceability` states `N/A` with reason.

---

## 6. Relationship to TestCaseDraft

The LLM consumes **this requirement record** and produces **TestCaseDraft** JSON (see [ai_test_creation.md](ai_test_creation.md) §7): titles, `linked_requirement_keys`, steps, preconditions, etc. Keeping requirement **AC ids** (`AC-01`) stable helps QA map failing tests back to requirements without renumbering churn.
