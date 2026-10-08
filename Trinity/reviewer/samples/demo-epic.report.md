# Requirement Review — 2026-09-28-0044

**Scanned:** Initial scan — 2026-09-28  
**Scope:** Epic — [DEMO-4500](https://example.atlassian.net/browse/DEMO-4500) — "OKR custom fields, phase 2" · Status: In Progress  
**Product:** Demo product · schema 1.1  
**Data sources analyzed:** Target issue (DEMO-4500) · Child inventory + content · Comments · Issue links · Confluence PRD · Figma (epic's own link)  
**Data sources unavailable or failed:** none

**Readiness for test planning:** Needs clarification before test design  
_1 High finding (RR-DEMO-4500-01) and 1 open High question (Q1) stand between this epic and a testable rollout definition._  
Child scans can start; the findings below should travel with them.

**Testability:** Medium · **Test scope confidence:** Medium · **Risk:** Medium (integration dependency) · **Automation candidate:** TBD

## Findings

| ID | Severity | Checklist ref | Finding | Testing impact | Owner |
|----|----------|---------------|---------|----------------|-------|
| RR-DEMO-4500-01 | HIGH | A3 | Epic description states the goal but gives no testable completion criterion — no cohort, rollout scope, or exit criterion for "phase 2" being done. | Cannot define an epic-level acceptance test independent of child-level tests. | PO |
| RR-DEMO-4500-02 | MEDIUM | B12 | DEMO-4536 (bulk import — the reverse of DEMO-4522's export) is Waiting for Release while DEMO-4522 is still In Progress — the export→import round trip has no window where it can be tested end-to-end yet. | An epic-level end-to-end pass must wait for both children; flag this dependency before scheduling one. | EM |
| RR-DEMO-4500-03 | LOW | B12 | DEMO-4531's description covers an export destination/trigger that may overlap DEMO-4529 ("Scheduled / recurring export") — but DEMO-4529 has no description (`content_source: title_only`), so the overlap is named from its title only, not established as a fact. | Low impact now; worth asking for a description on DEMO-4529 before both are picked up in the same sprint. | PO |

## Clarification questions

### Definition of done

#### Q1. What does "phase 2 complete" mean — all customers, or a staged rollout behind a feature flag?
- Context: The epic goal is qualitative only. · Source: Epic description · Priority: High · Unblocks: RR-DEMO-4500-01 · Owner: PO

### PRD authority

#### Q2. The linked Confluence PRD says export defaults to CSV; DEMO-4531 assumes XLSX is also in scope for phase 2 — which document is authoritative?
- Context: Confluence page fetched; conflicts with a child story. · Source: Confluence PRD §3; DEMO-4531 description · Priority: Medium · Unblocks: RR-DEMO-4500-03 · Owner: PO

### Design authority

#### Q3. The epic's Figma link has no node-id; a root metadata scan shortlisted two frames matching the epic title — "Export flow (v1, deprecated)" and "Export flow (v2, current)". Which is canonical?
- Context: Name-overlap shortlist returned 2 candidates, not 1. · Source: Figma — root metadata scan, figma.com/design/abc123/OKR-fields · Priority: Optional · Unblocks: — · Owner: UX

## Not stated in epic

- A concrete definition of "phase 2 complete."
- Canonical export file format if CSV and XLSX both ship (Confluence PRD vs. DEMO-4531 disagree).

## Known or suspected risks

- The export→import round trip (DEMO-4522 ↔ DEMO-4536) is the epic's highest-value regression surface and currently untestable end-to-end — flag before release planning locks a date. *(Source: Child status mix)*

## Suggested testing focus

- Once DEMO-4522 and DEMO-4536 are both Done, run one end-to-end export→import journey before any epic-level sign-off. *(waits on: RR-DEMO-4500-02)*
- Confirm CSV-vs-XLSX scope with the PO before writing format-specific assertions for DEMO-4531. *(waits on: Q2)*

## Information identified

- Epic goal: "let teams get their custom-field data out of the product for reporting." *(Source: Epic description)*
- The linked PRD states CSV as the default export format. *(Source: Confluence PRD §3)*

## Design observations (Figma)

_Design reference only — not verified on build._

- The epic's Figma link has no node-id, so no single frame was fetched. A root get_metadata scan shortlisted 2 frames whose names overlap the epic title: "Export flow (v1, deprecated)" and "Export flow (v2, current)". *(Source: Figma — figma.com/design/abc123/OKR-fields, root metadata scan)*

## Child inventory & status mix

**Full inventory — 10 children, paginated to `isLast`, never a sample.**  
**Status mix:** Done — 3 · In Progress — 2 · Open — 3 · Waiting for Release — 2

| Key | Type | Status | Summary | Content |
|-----|------|--------|---------|---------|
| DEMO-4510 | Story | Done | Add custom field picker to export dialog | description |
| DEMO-4515 | Story | Done | Field-level permission check in export service | description |
| DEMO-4518 | Story | Done | CSV formatting for multi-select custom fields | description |
| DEMO-4522 | Story | In Progress | Bulk CSV export for OKR custom fields | description |
| DEMO-4525 | Story | In Progress | Export audit log entry | description |
| DEMO-4529 | Story | Open | Scheduled / recurring export | title_only |
| DEMO-4531 | Story | Open | Export to Confluence page | description |
| DEMO-4534 | Story | Open | Localize export column headers | title_only |
| DEMO-4536 | Story | Waiting for Release | Bulk import counterpart (reverse of 4522) | description |
| DEMO-4540 | Story | Waiting for Release | Deprecate legacy single-field export UI | description |

## Epic batch handoff

Every child except Canceled ones is scanned. DEMO-4529 and DEMO-4531 come first because the open questions name them; the three Done children go last.

**Batch (every non-Canceled child, in scan order):** `DEMO-4522` · `DEMO-4536` · `DEMO-4531` · `DEMO-4525` · `DEMO-4540` · `DEMO-4529` · `DEMO-4534` · `DEMO-4510` · `DEMO-4515` · `DEMO-4518`

- `confirm batch` — scan all 10 children in the order shown, 8 at a time
- `--batch keys <comma-separated>` — scan a specific subset

The batch does not run automatically.

## Recommended next action

Ask the PO Q1 and Q2, then run the batch for the non-Done children. Epic-level end-to-end testing waits until DEMO-4522 and DEMO-4536 are both Done.

---
_This review supports shift-left preparation. It does not approve or reject the requirement._
