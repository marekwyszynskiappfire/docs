# Requirement Review — 2026-09-29-1153-ONE-324524

**Scanned:** Initial scan — 2026-09-29  
**Scope:** Epic — [ONE-324524](https://appfire.atlassian.net/browse/ONE-324524) — "Create box work items structure using recurring issue links" · Status: In Progress  
**Product:** BigPicture · schema 1.1  
**Data sources analyzed:** ONE-324524 (target issue) · Acceptance Criteria field (customfield_10901) · Comments on ONE-324524 · Child inventory ("Epic Link" = ONE-324524) · Issue links on ONE-324524 · Parent AEPORT-1240 · Confluence: Scope definition based on parents keys (97184810059) · Confluence: Requirements and Issue Sizing (96217858423) · Confluence: Manage Product Category Initiatives (96266356168) and Plan Initiatives Across the Organization (96266125367) · Attachment: image-20260530-200944.png (inline in the Epic description as "Example from Structure")  
**Data sources unavailable or failed:** none

**Readiness for test planning:** Needs clarification before scope can be tested  
_The epic has no acceptance criteria, and its children leave open what "recurringly" means after save and which relationships are traversed (RR-ONE-324524-01, RR-ONE-324524-03; Q1, Q2)._  
Child scans can start; the findings below should travel with them.

**Testability:** Medium · **Test scope confidence:** Low · **Risk:** Medium (regression surface, integration dependency) · **Automation candidate:** TBD

## Findings

| ID | Severity | Checklist ref | Finding | Testing impact | Owner |
|----|----------|---------------|---------|----------------|-------|
| RR-ONE-324524-01 | HIGH | A3 | The Acceptance Criteria field is empty on the Epic and on all three children, and no description holds AC bullets. The epic has a one-line goal and no testable completion criterion. | No epic-level acceptance test can be defined; pass criteria have to come from each child's own scan. | PO |
| RR-ONE-324524-02 | HIGH | B8 | Nothing states whether "recurringly" means the box keeps following the hierarchy after the scope is saved. ONE-356784 persists a flag on the scope definition, but no source says whether descendants that are added, removed or re-parented later join or leave the box on the next refresh, or only the tree present at save time counts. The Structure screenshot shows a "Choose type of extend rule" dialog, but its layout is not a rule for BigPicture. | The core state transition (hierarchy changes after save) has no expected result, so neither a one-time nor a live-rule test can be written. | PO |
| RR-ONE-324524-03 | HIGH | A4 | The sources disagree on which relationship is traversed. The epic summary and linked Idea PPMR-342 say "recurring issue links"; the customer quote in ONE-36236 says issues are linked "via normal issue linking"; the Structure example offers both "Child Work Items" and "Linked Items". Yet ONE-36236 strikes through the "other Jira link" option, leaving only the Parent field. The epic never states that link-based traversal is out of scope. | QA cannot tell whether issue-link hierarchies are in the test matrix or are an expected non-feature. | PO |
| RR-ONE-324524-04 | HIGH | B12 | The children describe two different user interactions. ONE-36236 has the user enter task keys, with structure builders adjusted automatically. ONE-350189 adds one toggle below "Refresh search list", and ONE-356784 stores one boolean for the whole scope definition. No source says whether the toggle applies only to entered keys or also to projects, boards and filters in the same scope, or how it combines with Narrow Down. | The primary flow cannot be written end to end: the inputs the toggle acts on are undefined. | PO |
| RR-ONE-324524-05 | HIGH | A6 | The spike opened to check this epic's impact on the Scope Def data-storage refactor (ONE-357566) is Canceled, and the related refactor epic ONE-235869 is still Open. No outcome is recorded on this epic, so "no impact" is an unstated assumption. | Regression scope for the persisted flag is unknown if ONE-235869 later changes how scope definitions are stored. | EM |
| RR-ONE-324524-06 | MEDIUM | B7 | The Jira edition matrix is unsettled. ONE-36236 specifies Data Center behaviour and DC structure builders; the linked Confluence analysis says the DC variant is probably not worth implementing for performance reasons; the epic's Host platform field lists only Atlassian Cloud. The same page lists different query options for Cloud Standard, Cloud Premium and team-managed projects, and no child says which are supported. | The environment matrix (DC, Cloud Standard, Cloud Premium, team-managed) cannot be fixed, which sets how many configurations need a pass. | EM |
| RR-ONE-324524-07 | MEDIUM | B3 | No depth limit, item-count limit or time target is stated for building the descendant tree. ONE-36236 acknowledges a negative performance impact, and the Confluence analysis lists a criterion requiring the user to also enter a project to narrow the search, but ONE-36236 does not carry that criterion forward. | Boundary and large-hierarchy tests have no pass threshold. | EM |
| RR-ONE-324524-08 | MEDIUM | B2 | No behaviour is stated for an entered key that doesn't exist, is mistyped, or points to an issue the user cannot browse. | Negative-path tests for key entry have no expected result. | PO |
| RR-ONE-324524-09 | MEDIUM | B5 | No source says who may enable the toggle, or what happens to descendants the box's scope context user cannot see in Jira. | Role and visibility tests cannot be scoped. | PO |
| RR-ONE-324524-10 | MEDIUM | B12 | The child status mix rules out an epic-level end-to-end pass for now. The toggle (ONE-350189) and flag persistence (ONE-356784) are Waiting for Release, but the query change that actually uses the flag (ONE-36236) is still In Progress. | An end-to-end check (toggle on, scope built with descendants) waits until ONE-36236 is delivered. | EM |
| RR-ONE-324524-11 | MEDIUM | C1 | A feature flag is named only on the front-end child ONE-350189, with status DISABLED. The epic's own flag fields are empty, nobody is named as owner of switching it on, and no source says whether the same flag also controls the back-end query change in ONE-36236. | QA cannot plan flag-on and flag-off coverage or know when the feature becomes testable in a shared environment. | PO |
| RR-ONE-324524-12 | LOW | C3 | Tracking fields disagree: the legacy Epic Status field reads To Do while the status is In Progress, the migrated end date of 2026-08-31 has passed, no fix version is set, and the Idea this epic implements (PPMR-342) is in Parking lot. | Low impact; release planning cannot rely on these fields. | PO |

## Clarification questions

### Definition of done

#### Q1. What observable outcome marks this epic done? In particular: once "Include all children recurringly" is saved, should descendants that are added, removed or re-parented later join or leave the box on its next refresh, or does only the tree present at save time count?
- Context: No Acceptance Criteria anywhere in the epic or its children. The flag is persisted on the scope definition (ONE-356784), but no source says whether later hierarchy changes are followed. · Source: Acceptance Criteria field (Epic and children); ONE-350189 and ONE-356784 descriptions · Priority: High · Unblocks: RR-ONE-324524-01, RR-ONE-324524-02 · Owner: PO

### PRD authority

#### Q2. The epic summary, Idea PPMR-342, the customer quote in ONE-36236 and the Structure example all refer to issue links, but ONE-36236 strikes out the "other Jira link" option. Which is authoritative: is traversal by Jira issue links out of scope for this epic, leaving only the Parent field?
- Context: If links are out of scope, the epic summary no longer describes what ships, and the customer case quoted in ONE-36236 is not covered. · Source: Epic summary; issue link PPMR-342; ONE-36236 description; screenshot image-20260530-200944.png · Priority: High · Unblocks: RR-ONE-324524-03 · Owner: PO

### Rollout

#### Q3. Who switches ScopeDefinitionIncludeAllChildrenRecurringly on, and when? Does that flag also control the back-end query change in ONE-36236, or only the toggle?
- Context: The flag is named only on ONE-350189 (status DISABLED); the epic's own flag fields are empty. · Source: ONE-350189 FF Name / FF Status fields; Epic FF fields · Priority: Medium · Unblocks: RR-ONE-324524-11 · Owner: PO

### Behavior

#### Q4. What does the toggle act on? Only the task keys entered as described in ONE-36236, or every source in the scope definition (projects, boards, filters)? And how does it combine with Narrow Down?
- Context: ONE-36236 describes key entry with automatic builder adjustment; ONE-350189 and ONE-356784 describe one toggle and one boolean for the whole scope definition. · Source: ONE-36236, ONE-350189, ONE-356784 descriptions · Priority: High · Unblocks: RR-ONE-324524-04 · Owner: PO

### Edge cases

#### Q5. Is there a maximum depth, item count or build-time target for the descendant tree, and must the user also select a project to narrow the search, as the Confluence analysis proposed?
- Context: ONE-36236 states the change "will have a negative impact on performance" but sets no threshold. · Source: ONE-36236 description; Confluence 'Scope definition based on parents keys' · Priority: Medium · Unblocks: RR-ONE-324524-07 · Owner: EM

### Integrations

#### Q6. The spike ONE-357566 (impact on the Scope Def refactor) was Canceled and ONE-235869 is still Open. Was the impact confirmed elsewhere, and does the refactor change how includeAllChildrenRecurringly is stored?
- Context: No outcome is recorded on this epic. · Source: Issue links ONE-357566, ONE-235869 · Priority: High · Unblocks: RR-ONE-324524-05 · Owner: EM

#### Q7. Which Jira editions and project types does this epic support: Cloud Standard, Cloud Premium, team-managed projects, Data Center?
- Context: ONE-36236 specifies Data Center builders; the Confluence analysis says the DC variant is probably not worth implementing; Host platform lists only Atlassian Cloud. · Source: ONE-36236 description; Confluence 'Scope definition based on parents keys'; Epic Host platform field · Priority: Medium · Unblocks: RR-ONE-324524-06 · Owner: EM

### Permissions

#### Q8. Who may enable the toggle? What happens when an entered key doesn't exist or can't be browsed, or when some descendants are not visible to the box's scope context user?
- Context: No roles, visibility rules or error behaviour are stated in any source. · Source: Epic description; ONE-36236 description · Priority: Medium · Unblocks: RR-ONE-324524-08, RR-ONE-324524-09 · Owner: PO

## Not stated in epic

- Acceptance criteria for the epic or any child.
- Whether the box follows hierarchy changes made after the scope is saved.
- An explicit out-of-scope note for issue-link traversal, which the epic summary still names.
- Error handling for scope builds that time out or fail (B4).
- Test data or environment for multi-level hierarchies, including which Jira edition is used (B10).
- Logging or audit of scope changes made through this feature (B11).
- A design reference for the toggle: UX Design status is 'To decide' and the Figma field is empty.

## Known or suspected risks

- The mechanism acts on box scope definitions, which every box uses; with no stated performance threshold and an acknowledged negative impact, large hierarchies are the main regression risk. *(Source: ONE-36236 description)*
- If link-based traversal is out of scope, the customer case quoted in ONE-36236 (issues linked "via normal issue linking") is not served, which may surface late as a scope dispute. *(Source: ONE-36236 description; Epic summary)*
- A canceled impact spike next to an open refactor of the same data storage leaves the persisted flag exposed to a later storage change. *(Source: Issue links ONE-357566, ONE-235869)*

## Suggested testing focus

- Once Q1 is answered, test a hierarchy change after save (add, remove and re-parent a descendant) and check box scope on the next refresh. *(waits on: Q1)*
- Combine key entry and the toggle with a project, board or filter source and with Narrow Down, to confirm what the toggle acts on. *(waits on: Q4)*
- Run a large and deep hierarchy against a stated time or size limit. *(waits on: Q5)*
- Cover both flag states for ScopeDefinitionIncludeAllChildrenRecurringly, and the default False on existing boxes. *(waits on: Q3)*
- One end-to-end pass (toggle on, save, scope built with descendants) after ONE-36236 is delivered. *(waits on: RR-ONE-324524-10)*

## Information identified

- Epic goal: "Business goal is to enable user to add all the children and children of children (etc) of selected work items to the scope of box." *(Source: Epic description)*
- The Epic description's only illustration, captioned "Example from Structure", shows a dialog titled "Create Extend Generator" with the prompt "Choose type of extend rule:" and two options: "Child Work Items — Pull in child work items using the Parent field." and "Linked Items — Pull in work items that are linked to work items already in the structure." *(Source: Screenshot — image-20260530-200944.png (attachment 1242785))*
- ONE-36236: the user can enter Key IDs for multiple tasks; BigPicture adds those tasks and "all descendants of these tasks to the scope (the whole tree)", adjusts structure builders, and the result can be combined with projects, boards and filters and narrowed with Narrow Down. *(Source: ONE-36236 description)*
- ONE-36236 strikes through the option "other Jira link (user can select 1 link - determination of descendant tasks will be done based on that link)"; the remaining option is the Parent link. *(Source: ONE-36236 description)*
- ONE-36236 states "This change will have a negative impact on performance". *(Source: ONE-36236 description)*
- ONE-350189: a new toggle on the scopeDefinition module below "Refresh search list", described as "Include all children recurringly"; the flag is passed in area/task/scope/def/update and persisted in the database. *(Source: ONE-350189 description)*
- ONE-350189 carries feature flag ScopeDefinitionIncludeAllChildrenRecurringly with status DISABLED; the epic's own flag fields are empty. *(Source: ONE-350189 FF Name / FF Status fields)*
- ONE-356784: includeAllChildrenRecurringly has default value False, is stored as a boolean, and is added to the scope definition DTO. *(Source: ONE-356784 description)*
- The Confluence analysis compares Parent-field and Jira-link approaches across Cloud Standard, Cloud Premium and Data Center, notes that team-managed projects lack some queries, and says the Data Center variant is probably not worth implementing for performance reasons (Cloud only). *(Source: Confluence — Scope definition based on parents keys, appfireteam.atlassian.net)*
- Epic Host platform: Atlassian Cloud. UX Design status: To decide. Figma (URL): empty. *(Source: Epic custom fields)*

## QA readiness checklist (preliminary)

| # | Check | Source | Owner | Done |
|---|-------|--------|-------|------|
| 1 | Confirm the epic's completion criterion and whether the box follows hierarchy changes after save | Pending Q1 | PO | ☐ |
| 2 | Confirm whether issue-link traversal is in or out of scope | Pending Q2 | PO | ☐ |
| 3 | Confirm what the toggle acts on and how it combines with key entry and Narrow Down | Pending Q4 | PO | ☐ |
| 4 | Confirm the supported Jira editions and project types for the environment matrix | Pending Q7 | EM | ☐ |
| 5 | Confirm flag owner and whether the flag also covers ONE-36236 | Pending Q3 | PO | ☐ |
| 6 | Run one end-to-end pass once ONE-36236 is delivered | Child status mix | QA | ☐ |

## Child inventory & status mix

**Full inventory — 3 children, paginated to `isLast`, never a sample.**  
**Status mix:** In Progress — 1 · Waiting for Release — 2

| Key | Type | Status | Summary | Content |
|-----|------|--------|---------|---------|
| ONE-36236 | Story | In Progress | [BE] Value of includeAllChildrenRecurringly is used while quering tasks | description |
| ONE-350189 | Story | Waiting for Release | [FE] Add switcher on scope def to add issues recurringly | description |
| ONE-356784 | Story | Waiting for Release | [BE] Flag includeAllChildrenRecurringly is persisted on backend | description |

## Epic batch handoff

All three children are in the batch. ONE-36236 comes first because the most findings and questions name it; ONE-350189 and ONE-356784 follow.

**Batch (every non-Canceled child, in scan order):** `ONE-36236` · `ONE-350189` · `ONE-356784`

- `confirm batch` — scan all 3 children in the order shown, 8 at a time
- `--batch keys <comma-separated>` — scan a specific subset

The batch does not run automatically.

## Recommended next action

Ask the PO Q1, Q2 and Q4 and the EM Q6, then run the batch starting with ONE-36236. Plan the epic-level end-to-end pass for after ONE-36236 is delivered.

---
_This review supports shift-left preparation. It does not approve or reject the requirement._
