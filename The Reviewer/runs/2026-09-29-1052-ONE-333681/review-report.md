# Requirement Review — 2026-09-29-1052-ONE-333681

**Scanned:** Initial scan — 2026-09-29  
**Scope:** Epic — [ONE-333681](https://appfire.atlassian.net/browse/ONE-333681) — "Role-based resource management vol1. - Q3 2026" · Status: Waiting for Deploy  
**Product:** BigPicture · schema 1.1  
**Data sources analyzed:** ONE-333681 (target issue) · Comments on ONE-333681 · Parent Initiative AEPORT-1893 · Child inventory ("Epic Link" = ONE-333681) · Issue links on ONE-333681 · Subtasks on ONE-333681 · Confluence page mentioned in remote issue links · Figma links in description, comments, custom fields · Spreadsheet detection · Attachment detection on ONE-333681 itself  
**Data sources unavailable or failed:** none

**Readiness for test planning:** Needs clarification before test design  
_Two High findings (RR-ONE-333681-02, RR-ONE-333681-03) and their matching open High questions (Q3, Q6) — an unresolved export-format decision and unverified 'scenario mode' test coverage — stand between this epic and a fully testable, signed-off state, even though the epic is already Waiting for Deploy._  
Child scans can start; the findings below should travel with them.

**Testability:** Medium · **Test scope confidence:** Medium · **Risk:** High (data integrity, integration dependency) · **Automation candidate:** TBD

## Findings

| ID | Severity | Checklist ref | Finding | Testing impact | Owner |
|----|----------|---------------|---------|----------------|-------|
| RR-ONE-333681-01 | HIGH | A4 | The description gives three different signals about virtual-resource (VR) role support: an 'Includes' bullet crossing the item out (implying it's not a distinct deliverable), a 'Scope of work' note saying VR gets a role 'automatically' via team membership, and a Usecase note promising VR role assignment for capacity estimation. No sentence in the epic's own text reconciles the strikethrough with the other two — a reader has to infer that the strikethrough means 'not a separate workstream' rather than 'not in scope.' | QA cannot decide whether virtual-resource role assignment needs its own dedicated test, or is already covered incidentally by regular team-membership role tests, until the scope question is answered. | PO |
| RR-ONE-333681-02 | HIGH | A6 | This is an open product decision, raised by QA during acceptance testing on child task TC-6605 ('[QA Acceptance] Role-based resource management', status Done), that is never answered anywhere in the epic's own analyzed text — including the newly-fetched Confluence roadmap page, which does not mention export format at all. The epic itself states 'Roles are supported in BT exports' as a committed Includes item, but the acceptance evidence says the XLSX export path currently shows individuals, not roles — directly bearing on whether that Includes item is actually met. | QA cannot mark the 'Roles supported in BT exports' capability as fully tested until the PM confirms whether XLSX must show roles, or PDF-only is the accepted scope for vol1. | PM |
| RR-ONE-333681-03 | HIGH | A8 | The epic's own QA acceptance record (TC-6605, Done) states that 'scenario mode' verification of role-based workload/capacity was skipped because of a still-open bug (ONE-380032, status Waiting for Release). No later comment, child, or field records that scenario mode was re-checked after the fix. Separately, the epic's only dedicated testing story, ONE-337416 ('[BE] Create tests for Role functionality'), is Canceled rather than Done, and no replacement testing story exists in the 41-item child inventory. | The core role-based workload/capacity calculation cannot be signed off for its most complex mode ('scenario mode') until it is retested post-fix — this is the epic's single largest verification gap. | EM |
| RR-ONE-333681-04 | HIGH | B7 | The 'Includes' list attributes cost-per-role/Financial-module work to a different team on a different timeline ('Q4 team Orion'), but the same capability is restated in 'Scope of work' with no such caveat, reading as this epic's own commitment. No child in the full 41-item inventory owns either cost-per-role bullet either way, so ownership cannot be confirmed from the inventory alone. The newly-fetched Confluence roadmap page does not mention Financial-module or cost-per-role work either, so it does not resolve the ambiguity. | QA cannot scope a cost-per-role/Financial-module test pass for this epic until ownership (this epic vs. team Orion, on a separate timeline) is confirmed. | PO |
| RR-ONE-333681-05 | MEDIUM | A5 | Both design-tracking fields on the epic still read as if no design work has happened, despite the epic being in 'Waiting for Deploy' and several children (ONE-338358, ONE-338359, ONE-338360) embedding actual UI screenshots in their own descriptions. The formal tracking fields were never updated to reflect the design work that evidently did happen. The Confluence roadmap page names a UX owner (Karolina Chrzanowska) but does not link to any design artifact either, so it does not close this gap. | No direct testing impact; a documentation/traceability hygiene gap for future readers of this epic, including anyone trying to find the design source for a child-level UI test. | UX |
| RR-ONE-333681-06 | MEDIUM | A8 | The feature flag gating this entire epic is recorded as globally DISABLED while the epic itself sits at 'Waiting for Deploy' and 31 of 41 children are 'Waiting for Release'. No rollout/enablement plan (staged, all-at-once, per-customer) is stated anywhere in analyzed text, including the Confluence roadmap page. | QA needs the rollout plan to know whether to validate with the flag enabled immediately, or plan a later verification pass timed to a staged enablement window. | PO |
| RR-ONE-333681-07 | MEDIUM | A2 | A broken strikethrough mid-word ('~~to a Team a~~nd') garbles the sentence to read 'Add the concepts of a Role nd enable each team member to get a role assigned' when the strikethrough is rendered literally — a formatting/transcription defect independent of whichever meaning was intended. | No testing impact; a text-rendering defect in the epic's own description. | PM |
| RR-ONE-333681-08 | MEDIUM | B12 | Neither 'Nice to have' item has an owning child anywhere in the full 41-item inventory, and no comment, field, or the newly-fetched Confluence page states whether they were consciously deferred (e.g. to the cloned follow-on epic ONE-372206, 'vol2 - Q1 2027') or simply dropped without a decision. | QA should not spend time searching for tests of the two 'Nice to have' items until their fate (delivered, deferred, or dropped) is confirmed. | PO |
| RR-ONE-333681-09 | MEDIUM | B12 | The frontend-labelled child for 'New built-in field for Role assignment to Tasks in BP' is Canceled while the identically-named backend child proceeded to Waiting for Release, and a separate FE child (ONE-338362, 'Enable assigning role to a task from gantt column view or taskcard') also proceeded. It's unclear from the inventory alone whether ONE-338362 fully supersedes the canceled ONE-362647 or whether a UI surface is missing. | QA needs confirmation that ONE-338362 fully covers the frontend surface before treating the built-in Role-field-on-task capability as fully tested — both are named in this run's Epic batch handoff for that reason. | EM |
| RR-ONE-333681-10 | LOW | B11 | No logging, audit trail, or metrics are mentioned anywhere in analyzed text — Jira or the newly-fetched Confluence page — for role assignment or role-based capacity/cost changes. | No direct testing impact on functional test design; flag as a gap for a future observability/audit-focused test pass, if one is planned. | EM |
| RR-ONE-333681-11 | LOW | B9 | No performance target or NFR is stated for extending existing workload/capacity calculators with a per-role dimension, despite this touching a calculation path already used broadly across the Resources module. | No direct testing impact on functional test design; flag as a gap for a future performance-focused test pass, if one is planned. | EM |
| RR-ONE-333681-12 | LOW | A8 | The 'Includes' list mixes this epic's own committed scope with at least one item explicitly owned by another team/quarter, with no parallel out-of-scope section to make the boundary explicit at a glance. | No direct testing impact; a documentation clarity gap. | PO |
| RR-ONE-333681-13 | LOW | A5 | The Confluence roadmap page linked from this epic ('mentioned in') — newly readable this run via a second, appfireteam-scoped Atlassian connection — lists a second epic, ONE-307893, in the same release/milestone table as ONE-333681. No Jira issue link (parent, related, or otherwise) connects the two epics on ONE-333681's own record, and the page gives no further detail on how they relate. | No direct testing impact on this epic's own test scope; only relevant if ONE-307893 later turns out to share test surface (e.g. the Resources module or the role concept itself) with this epic. | PO |

## Clarification questions

### Definition of done

#### Q1. Were the two 'Nice to have' items (Jira-field mapping; multi-role planning) deferred to the cloned follow-on epic ONE-372206 (vol2), or dropped for this epic's scope?
- Context: Neither item has an owning child in the full 41-item inventory, and this epic was cloned to create ONE-372206. · Source: Description — Nice to have list; issue link to ONE-372206 · Priority: Medium · Unblocks: RR-ONE-333681-08 · Owner: PO

### Rollout

#### Q2. What is the enablement plan for ResourceRolesFeatureFlag now that the epic is Waiting for Deploy?
- Context: The flag is recorded as globally DISABLED while most children are already Waiting for Release. · Source: Custom fields — FF Name, FF Status · Priority: Medium · Unblocks: RR-ONE-333681-06 · Owner: PO

### Behavior

#### Q3. Has role-based workload/capacity calculation been re-verified in 'scenario mode' since bug ONE-380032 was fixed, and was the Canceled testing story (ONE-337416) intentionally dropped or replaced?
- Context: QA's own acceptance record states scenario mode was explicitly skipped due to an open bug; no later evidence of a retest exists in analyzed text. · Source: Child TC-6605 description; child ONE-337416 status · Priority: High · Unblocks: RR-ONE-333681-03 · Owner: EM

### Scope

#### Q4. Is virtual-resource role assignment in scope for vol1 (delivered automatically via team membership, per the 'Scope of work' note), or was it descoped as the struck-through 'Includes' bullet implies — and if delivered automatically, has that behaviour been verified end-to-end?
- Context: The 'Includes' list strikes the item out; 'Scope of work' and the Usecase section both describe it as delivered. The epic's own text never reconciles the two. · Source: Description — Includes list, Scope of work, Usecase §2 · Priority: High · Unblocks: RR-ONE-333681-01 · Owner: PO

### Integrations

#### Q5. Is cost-per-role / Financial-module integration in scope for this epic at all, or entirely owned by team Orion on a separate timeline?
- Context: One bullet attributes it to 'Q4 team Orion'; a near-identical bullet elsewhere has no such caveat. No child in the inventory owns either version, and the Confluence roadmap page doesn't mention this capability at all. · Source: Description — Includes list vs. Scope of work list · Priority: High · Unblocks: RR-ONE-333681-04 · Owner: PO

### Data

#### Q6. Has the XLSX-vs-PDF export-format decision raised in TC-6605 been made, and is 'Roles are supported in BT exports' considered met, partially met, or still open for vol1?
- Context: QA's own acceptance-testing note states XLSX exports currently show individuals, not roles, and explicitly defers the decision to the PM. TC-6605 is Done regardless. · Source: Child TC-6605 description · Priority: High · Unblocks: RR-ONE-333681-02 · Owner: PM

## Not stated in epic

- Whether 'Roles need to be ready to work with virtual resources' is genuinely descoped or delivered automatically — the text contradicts itself (RR-01/Q4).
- Resolution of the XLSX-vs-PDF export-format decision QA itself raised (RR-02/Q6).
- Confirmation that scenario-mode workload/capacity behaviour was retested after bug ONE-380032 shipped (RR-03/Q3).
- Ownership of cost-per-role / Financial-module work — this epic or team Orion (RR-04/Q5).
- Rollout/enablement plan for the currently-disabled feature flag (RR-06/Q2).
- Fate of the two 'Nice to have' items — delivered, deferred, or dropped (RR-08/Q1).
- Any explicit out-of-scope statement for this epic.
- How ONE-307893 (named alongside this epic on the Confluence roadmap page) relates to this epic's scope or timeline — no Jira link states this explicitly (RR-13).

## Known or suspected risks

- Data integrity — role assignment enforces 'only one role can be active in a given period' (per ONE-337406/ONE-337380); overlapping-period and back-to-back-period edge cases are a natural place for validation bugs.
- Integration dependency — cost-per-role / Financial-module reporting depends on a separate team (Orion) on a separate timeline, with the epic's own text inconsistent about whether that work is even part of this epic's scope.
- Regression surface — the feature touches Resources, Teams, Gantt/task views, Administration, and BigTemplate/Excel exports simultaneously, behind a single feature flag.
- Reduced verification confidence — 20 of 41 children carry no usable description, and the epic's own QA acceptance record documents a known-incomplete test path (scenario mode) with the dedicated testing story Canceled.

## Suggested testing focus

- Role assignment to individuals with date ranges, including overlapping/back-to-back period validation.
- Role-based workload/capacity calculation in 'scenario mode,' specifically after bug ONE-380032 ships. *(waits on: Q3)*
- Role field on Task across Gantt, column views, and taskcard, given the canceled FE ticket ONE-362647. *(waits on: RR-ONE-333681-09)*
- Swimlanes by Role in the Resources module (ONE-338361, title-only content — verify actual delivered behaviour before assuming full parity with skills-based swimlanes).
- Virtual Resources automatically receiving a role as a team member, matching a regular Individual. *(waits on: Q4)*
- Role export in BigTemplate/XLSX vs. PDF, once the format decision is resolved. *(waits on: Q6)*
- Predefined roles (Team Leader, Team Member) — editable and removable as stated.

## Information identified

- Roles don't replace skills — skills assign users to tickets, while roles are used to calculate capacity and workload. *(Source: Description — Business goal)*
- FF Name: ResourceRolesFeatureFlag; FF Status: DISABLED. *(Source: Custom fields — FF Name, FF Status)*
- UX Design status: To decide; Figma (text only, deprecated): None. *(Source: Custom fields)*
- Children of Epic count = 41; Bugs of Epic count = 13; Stories of Epic count = 27. *(Source: Custom fields)*
- This epic was cloned to create ONE-372206 ('Role-based resource management vol2. - Q1 2027', Open). *(Source: Issue links)*
- The parent is Initiative AEPORT-1893 ('Strategic Resource Management H2 2026', Open) — context only, not a parent Epic. *(Source: Jira parent field)*
- The linked Confluence roadmap page ('Role-based resource management', appfireteam.atlassian.net) names Product owner Grzegorz Radynski-Figlarz, UX owner Karolina Chrzanowska, Engineering owner Marcin Koman, and QA owner Monika Cecot. *(Source: Confluence — Role-based resource management)*
- The same Confluence page lists a second epic, ONE-307893, in the same milestone/release table as this epic — see RR-ONE-333681-13. *(Source: Confluence — Role-based resource management)*
- FTE capacity is set up once for all roles based on WP and HP in the app administration (technically overridable per box); workload can be converted to FTEs in a given timeframe. *(Source: Comment @Grzegorz Radynski-Figlarz, 2026-07-01)*
- Frontend estimate: M; Backend estimate: tbc. *(Source: Comment @Grzegorz Radynski-Figlarz, 2026-06-16)*

## QA readiness checklist (preliminary)

| # | Check | Source | Owner | Done |
|---|-------|--------|-------|------|
| 1 | Confirm whether virtual-resource role assignment is in scope (delivered automatically) or descoped, and verify it end-to-end | Pending Q4 | PO | ☐ |
| 2 | Confirm XLSX-vs-PDF export decision from TC-6605 and re-test the Roles-in-BT-exports capability accordingly | Pending Q6 | PM | ☐ |
| 3 | Re-verify role-based workload/capacity in 'scenario mode' now that ONE-380032 is fixed | Pending Q3 | QA | ☐ |
| 4 | Confirm ownership of cost-per-role / Financial module work (this epic vs. team Orion) | Pending Q5 | PO | ☐ |
| 5 | Confirm ResourceRolesFeatureFlag rollout/enablement plan post-deploy | Pending Q2 | PO | ☐ |
| 6 | Confirm fate of the two 'Nice to have' items (Jira field mapping; multi-role planning) — delivered, deferred to ONE-372206, or dropped | Pending Q1 | PO | ☐ |
| 7 | Verify the built-in Role field on tasks has a complete FE surface given ONE-362647 was canceled | RR-ONE-333681-09 | EM | ☐ |
| 8 | Test overlapping-period validation for role assignment (only one active role per period) with boundary/back-to-back cases | ONE-337406, ONE-337380 descriptions | QA | ☐ |
| 9 | Verify Virtual Resources get roles automatically as team members, matching a regular Individual | Description — Scope of work | QA | ☐ |
| 10 | Update 'UX Design status' / Figma tracking fields to reflect the design work evidenced in child screenshots | RR-ONE-333681-05 | UX | ☐ |

## Child inventory & status mix

**Full inventory — 41 children, paginated to `isLast`, never a sample.**  
**Status mix:** Done — 6 · Waiting for Release — 31 · Canceled — 4

| Key | Type | Status | Summary | Content |
|-----|------|--------|---------|---------|
| TC-6605 | Task | Done | [QA Acceptance] Role-based resource management | description |
| ONE-381158 | Bug | Waiting for Release | [FE] Roles - Resources Module - There is no Role field in 'Plan task' window | description |
| ONE-381152 | Bug | Waiting for Release | [BE+FE] Roles - Resources Module - It is impossible to reassign role by drag and drop | description |
| ONE-380553 | Bug | Waiting for Release | [FE] Roles - Resources Module - Roles are displayed in the Resource grid even when they are not assigned to a task or team member during the displayed period | description |
| ONE-380032 | Bug | Waiting for Release | [FE] Roles - Resources Module - Resources module fails to load when tasks with and without roles exist in the same period or when a task with a role is assigned to an individual | description |
| ONE-380021 | Bug | Waiting for Release | [FE] Roles - Administration/Resources/Individuals - Role bar is not visible on timeline in the Individual page details | title_only |
| ONE-380019 | Bug | Waiting for Release | Roles - Resources Module - Missing "Individuals' roles" view option | description |
| ONE-380018 | Bug | Waiting for Release | Roles - Teams Module - Members tab - Incorrect column name: "Roles" instead of "Role" | title_only |
| ONE-380017 | Bug | Waiting for Release | Roles - Administration/Resources/Individuals - "resource" instead of "individual" in the validation message | title_only |
| ONE-377785 | Bug | Waiting for Release | [FE] Roles - All modules - Column views - Role is displayed as a text not lozenge | title_only |
| ONE-377784 | Bug | Waiting for Release | [FE] Roles - Gantt/Resources Modules - Missing 'Required role' field in the Task details dialog | description |
| ONE-377783 | Bug | Waiting for Release | Roles - Administration/Resources/Individuals - It is impossible to add a new individual (roleId error) | title_only |
| ONE-377234 | Bug | Waiting for Release | [FE] Roles - Incorrect column name and role display | title_only |
| ONE-377233 | Bug | Waiting for Release | [FE] Roles - Teams Module columns shifted | title_only |
| ONE-370639 | Story | Waiting for Release | [FE] Adjust datatype ROLES -> ROLE | title_only |
| ONE-362647 | Story | Canceled | [FE] New built-in field for Role assignment to Tasks in BP | title_only |
| ONE-361112 | Story | Waiting for Release | [FE] Create dataType for Role | title_only |
| ONE-354647 | Story | Waiting for Release | [BE] Implement Resource Role Assignment CRUD backend for Administration | title_only |
| ONE-339201 | Story | Waiting for Release | Pre-defined roles | description |
| ONE-338362 | Story | Waiting for Release | [FE] Enable assigning role to a task from gantt column view or taskcard and add role in places where it's missing | title_only |
| ONE-338361 | Story | Waiting for Release | [FE] Add swimlanes by roles to the Resources module (similarly to swimlanes by skills) | title_only |
| ONE-338360 | Story | Waiting for Release | [FE] Roles should be visible in the calendar in the administration's resources individuals tab | description |
| ONE-338359 | Story | Waiting for Release | [FE] Add new column in teams module that displays user current role | description |
| ONE-338358 | Story | Done | [FE] Add new card to the individual view in the administration which allows user to assign role to individual with defined period | description |
| ONE-338357 | Story | Done | [FE] Create new roles tab in the administration (#administration/resources/roles) + roles domain | title_only |
| ONE-337416 | Story | Canceled | [BE] Create tests for Role functionality | title_only |
| ONE-337414 | Story | Waiting for Release | [BE] Add Roles to BigTemplate exports | description |
| ONE-337413 | Story | Waiting for Release | [BE] Members Role is displayed on Teams Module | title_only |
| ONE-337412 | Story | Waiting for Release | [BE] Use Workload and Capacity calculated for Role based assignment in ResourceTaskAssignment mechanism | title_only |
| ONE-337411 | Story | Canceled | [BE] Implement CRUD for Role management | description |
| ONE-337410 | Story | Canceled | [BE] Implement CRUD for Resource Role assignment | description |
| ONE-337409 | Story | Waiting for Release | [BE] Implement workload calculators for Role assignment based workloads | title_only |
| ONE-337408 | Story | Waiting for Release | [BE] Add persistence layer to Resource Role assignement | title_only |
| ONE-337407 | Story | Waiting for Release | [BE] Create dataType for Role | title_only |
| ONE-337406 | Story | Done | [BE] Design and implement ResourceRole assignment | description |
| ONE-337405 | Story | Waiting for Release | [BE] Add persistence layer for the Roles | description |
| ONE-337404 | Story | Done | [BE] Add Role to entity repository backend for Role management in Administration | description |
| ONE-337403 | Story | Waiting for Release | [BE] Calculate capacity based on Role assignment | description |
| ONE-337398 | Story | Waiting for Release | [BE] New built-in field for Role assignment to Tasks in BP | description |
| ONE-337380 | Story | Waiting for Release | [BE] Update Resource Aggregate with the Role | description |
| ONE-337369 | Story | Done | [BE] Design and implement Role in resources domain - basic services and in memory repository | description |

## Epic batch handoff

Every child except the four Canceled ones (37 in total) is scanned. The children the open findings and questions name come first (TC-6605, ONE-338362, ONE-380032, ONE-338359, ONE-338360, ONE-338358), then Waiting for Release and In Progress before To Do, then Done. Canceled children are left out: ONE-362647 and ONE-337416 are named in RR-ONE-333681-09 and RR-ONE-333681-03/Q3 instead; ONE-337411 and ONE-337410 aren't referenced by any finding.

**Batch (every non-Canceled child, in scan order):** `TC-6605` · `ONE-338362` · `ONE-380032` · `ONE-338359` · `ONE-338360` · `ONE-338358` · `ONE-337380` · `ONE-337398` · `ONE-337403` · `ONE-337405` · `ONE-337407` · `ONE-337408` · `ONE-337409` · `ONE-337412` · `ONE-337413` · `ONE-337414` · `ONE-338361` · `ONE-339201` · `ONE-354647` · `ONE-361112` · `ONE-370639` · `ONE-377233` · `ONE-377234` · `ONE-377783` · `ONE-377784` · `ONE-377785` · `ONE-380017` · `ONE-380018` · `ONE-380019` · `ONE-380021` · `ONE-380553` · `ONE-381152` · `ONE-381158` · `ONE-337369` · `ONE-337404` · `ONE-337406` · `ONE-338357`

- `confirm batch` — scan all 37 children in the order shown, 8 at a time
- `--batch keys <comma-separated>` — scan a specific subset

The batch does not run automatically.

## Recommended next action

Answer Q3–Q6 (the High-priority questions) with PM/PO/EM before treating this epic as fully closed for QA purposes, even though it already sits at Waiting for Deploy. The previously-unread Confluence roadmap page has now been fetched, via a second Atlassian connection scoped to appfireteam.atlassian.net; it does not resolve any of the open questions, but it adds named owners and surfaces one new, minor traceability item (ONE-307893, RR-ONE-333681-13). Once Q3–Q6 are answered, rescan ONE-333681 to update readiness. For deeper coverage on specific children, an Epic batch handoff is offered below — the batch does not run automatically.

---
_This review supports shift-left preparation. It does not approve or reject the requirement._
