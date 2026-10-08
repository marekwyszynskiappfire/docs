# Requirement Review — 2026-09-28-0031

**Scanned:** Initial scan — 2026-09-28  
**Scope:** Story — [DEMO-4522](https://example.atlassian.net/browse/DEMO-4522) — "Bulk CSV export for OKR custom fields" · Status: In Progress  
**Product:** Demo product · schema 1.1  
**Data sources analyzed:** Target issue (DEMO-4522) · Acceptance criteria field · Comments · Parent Epic (DEMO-4500) · Sibling stories · Issue links · Figma node 118:4402  
**Data sources unavailable or failed:** none

**Readiness for test planning:** Needs clarification before test design  
_2 High findings (RR-DEMO-4522-01, RR-DEMO-4522-02) and 2 open High questions (Q1, Q2) stand between this story and test design._  
Test case drafting can start; the findings below should travel with it.

**Testability:** Medium · **Test scope confidence:** Medium · **Risk:** Medium (data integrity) · **Automation candidate:** TBD

## Findings

| ID | Severity | Checklist ref | Finding | Testing impact | Owner |
|----|----------|---------------|---------|----------------|-------|
| RR-DEMO-4522-01 | HIGH | A3 | AC says export must complete "in a reasonable time" — no threshold stated. | Cannot define a pass/fail latency assertion. | PM |
| RR-DEMO-4522-02 | HIGH | B4 | Failure AC exists ("show an error") but not what the message says or whether retry is possible. | Cannot write the negative-path assertion or a retry test. | PM |
| RR-DEMO-4522-03 | MEDIUM | B5 | No statement of which roles can trigger a bulk export (all users? admins only?). | Permission-boundary tests cannot be scoped yet. | PM |
| RR-DEMO-4522-04 | LOW | B9 | No accessibility note for the export progress indicator. | Low impact on initial scope; worth a follow-up question only. | UX |

## Clarification questions

### Behavior

#### Q1. What does "reasonable time" mean for the export, in seconds or a row-count-scaled budget?
- Context: AC-02 uses the phrase with no number. · Source: AC field, AC-02 · Priority: High · Unblocks: RR-DEMO-4522-01 · Owner: PM

### Edge cases

#### Q2. If a field mapping errors mid-export, does the partial file download anyway, or is it withheld entirely — and can the user retry?
- Context: Failure behaviour and retry are undefined. · Source: Gap analysis · Priority: High · Unblocks: RR-DEMO-4522-02 · Owner: EM

### Permissions

#### Q3. Is bulk export available to all authenticated users, or restricted to Admins?
- Context: No role stated anywhere in analyzed sources. · Source: Gap analysis · Priority: Medium · Unblocks: RR-DEMO-4522-03 · Owner: PM

## Not stated in story

- Numeric or scaled time budget for "reasonable time."
- Which roles may trigger a bulk export.
- Whether a partially-failed export downloads a partial file or nothing.

## Known or suspected risks

- Bulk export touches the same field-mapping service as the single-record export — regression surface if mapping logic is shared. *(Source: Description, "reuses the existing field mapper")*
- Exported CSV may contain values from custom fields with restricted visibility — data integrity/permissions risk if the export doesn't re-check field-level permissions per row. *(Source: Gap analysis — no statement either way)*

## Suggested testing focus

- Verify export completion time once a numeric budget is confirmed. *(waits on: Q1)*
- Verify the failure message text and retry behaviour once defined. *(waits on: Q2)*
- Verify field-level permission enforcement on every exported row, regardless of who triggers the export. *(waits on: Q3)*

## Information identified

- Feature adds a "Bulk export" action on the OKR custom-fields list view. *(Source: Description)*
- Export format is CSV, generated server-side. *(Source: Description)*
- Reuses the existing field-mapping service used by the single-record export. *(Source: Description)*
- AC-01: "User can select which custom fields to include before exporting." *(Source: AC field)*
- AC-02: "Export completes in a reasonable time and downloads automatically." *(Source: AC field)*

## Design observations (Figma)

_Design reference only — not verified on build._

- Button labelled "Export selected fields". *(Source: Figma — figma.com/design/abc123/OKR-fields, node 118:4402)*

## Epic context

- DEMO-4500 — "OKR custom fields, phase 2" — In Progress. *(Source: Epic description)*
- Epic goal: "let teams get their custom-field data out of the product for reporting." No factual inconsistency found between epic and story text. *(Source: Epic description)*

## QA readiness checklist (preliminary)

| # | Check | Source | Owner | Done |
|---|-------|--------|-------|------|
| 1 | Field selection UI includes/excludes fields correctly before export | AC-01 | QA | ☐ |
| 2 | Export completes within the confirmed time budget | Pending Q1 | QA | ☐ |
| 3 | Failure shows the confirmed message and retry path | Pending Q2 | QA | ☐ |
| 4 | Field-level permission is enforced per row in the exported CSV | Pending Q3 / RR-DEMO-4522-03 | QA | ☐ |

## Recommended next action

Ask the PM Q1 and the EM Q2, then rescan DEMO-4522. The Creator can start now on AC-01 if the team prefers to draft in parallel.

---
_This review supports shift-left preparation. It does not approve or reject the requirement._
