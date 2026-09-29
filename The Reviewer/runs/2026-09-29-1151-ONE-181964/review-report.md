# Requirement Review — 2026-09-29-1151-ONE-181964

**Scanned:** Post-delivery review — 2026-09-29  
**Scope:** Epic — [ONE-181964](https://appfire.atlassian.net/browse/ONE-181964) — "[Q2] Risk management: metrics as fields in Jira" · Status: Done  
**Product:** BigPicture / Hedge PPM (built-in defaults; no per-product config found) · schema 1.1  
**Data sources analyzed:** ONE-181964 (target issue) · Acceptance Criteria field (customfield_10901) on ONE-181964 · Comments on ONE-181964 · Child inventory + content ("Epic Link" = ONE-181964) · Issue links on ONE-181964 · Parent AEPORT-1488 "SPM: Risk management H1 2026" · Subtasks of ONE-181964 · Confluence: "2026-Q2 - Omega team tasks estimation" (page 98351710248) · Confluence: "Risk management: Link custom fields to metrics - Q2 26'" (page 98456928717) · Confluence: "Product development strategy (2026-H1) - Streamliners" (page 99641175907) · Confluence: "Product development strategy - Streamliners - 2026" (page 3216605280) · Confluence: "Risks (App configuration)" (page 1918505973) · Attachments on ONE-181964: "Screenshot 2026-03-12 at 13.29.05.png", "Screenshot 2026-03-12 at 13.30.05.png"  
**Data sources unavailable or failed:** Google Drive file linked from ONE-181964 web links (Linked but not fetched: a non-Confluence document (drive.google.com), never auto-fetched. Its content type and content are unknown.)

**Readiness for regression and sign-off:** Needs clarification before test design  
_This epic is already Done: the findings below are gaps to close for regression coverage and sign-off, not reasons to hold back the build. 2 High findings (RR-ONE-181964-01, RR-ONE-181964-02) and 2 High questions (Q1, Q6) stand between this Epic and a complete regression and sign-off scope._  
Child scans can start; the findings below should travel with them.

**Testability:** Medium · **Test scope confidence:** Medium · **Risk:** Medium (data integrity, integration dependency) · **Automation candidate:** TBD

## Findings

| ID | Severity | Checklist ref | Finding | Testing impact | Owner |
|----|----------|---------------|---------|----------------|-------|
| RR-ONE-181964-01 | HIGH | A3 | The Epic's only acceptance criterion covers the multiple-contexts edge case. The core outcome in "After the change" (a metric mapped to a Jira field, configured in Risk Register settings → Metrics) has no epic-level completion criterion; the detail lives in individual child descriptions only. | Regression and sign-off can't be checked against one epic-level definition of done; QA has to rebuild it from ten child descriptions. | PO |
| RR-ONE-181964-02 | HIGH | B12 | The Epic names two paths: a Jira field created automatically by BigPicture, and a user-selected field. Every child description with matching terms covers the user-selected path only (listing fields, a field dropdown, context options). No child description mentions creating a Jira field, and no source states that path was dropped or deferred. | Regression scope for the automatic-field path can't be set: it is unknown whether it shipped, so it is neither tested nor explicitly excluded. | PO |
| RR-ONE-181964-03 | MEDIUM | A6 | Elena Kolesnik's comment (2026-07-17) lists two items: reopening the configuration after values change, and adding the field to the screen so it is visible in Risk Management. There is no reply or linked follow-up. Both match behaviour in child descriptions (ONE-249893, ONE-320856, ONE-257569), but whether they were acted on, for example in the documentation request DOCBP-4395, isn't recorded. | Sign-off can't confirm whether these two items are expected product behaviour to regress, or documentation notes only. | PO |
| RR-ONE-181964-04 | MEDIUM | B8 | A value changed directly in the Jira field reaches BigPicture only when the risk register issues table is listed (ONE-320856). The listener story ONE-257529 was Canceled, and ONE-257576 states that recalculation covers only the listed issues, leaving the stored values outdated for the rest. The expected state of Risk Score and Risk Level for issues not yet listed, for example on the Risk matrix, is not stated. | Regression can cover the listed-table sync, but not what other views should show before an issue is listed. | EM |
| RR-ONE-181964-05 | MEDIUM | B4 | ONE-320856 has the frontend update the Jira field for one issue on selection, and for every affected issue when a metric option changes in the configuration. No source states what happens when a Jira update fails or only some issues update. | Failure and partial-update cases can't be given expected results. | EM |
| RR-ONE-181964-06 | MEDIUM | B5 | ONE-249893 asks who can change the metric configuration and which custom fields are listed. The answers are recorded only as images, which Epic mode does not read, and no child states a role rule in text. | Role-based regression cases (who may link a field to a metric) can't be written from text sources. | PO |
| RR-ONE-181964-07 | MEDIUM | B12 | ONE-272341 implements the Epic's only acceptance criterion (default context only), and ONE-293797 covers configuration persistence, but both have an empty description (title only). Their alignment with the Epic rests on the title alone. | The default-context and persistence regressions have no child-level expected result to check against. | PO |
| RR-ONE-181964-08 | MEDIUM | C1 | No source says how the feature reached users: no feature flag, staged rollout, or explicit release to everyone. The Confluence project page plans release 8.74 for frontend and backend, and the children's fix versions include hedgeppm-cloud-1.0.0 (released 2026-08-03) and bigpicture-cloud-8.74.0.2 (released 2026-07-30). | Regression can't target the right audience or configuration without knowing whether the feature is on for everyone. | PO |
| RR-ONE-181964-09 | MEDIUM | C2 | The Epic is Done, but no testing child, QA acceptance record, or linked Xray execution was found on the Epic. The Confluence project page names a QA owner and makes QA and Product acceptance the completion step, with no record of either. | Sign-off can't state what was verified, so regression scope has to start from nothing. | PO |
| RR-ONE-181964-10 | LOW | B9 | No performance consideration is stated for updating every affected issue from the frontend when a metric option changes (ONE-320856), or for adding editmeta to the bulk issue fetch. | No load expectation to check for large risk registers. | EM |
| RR-ONE-181964-11 | LOW | B11 | No logging, audit, or changelog entry is mentioned for linking a metric to a Jira field or for the resulting Jira field updates. | Support has no stated signal to check when a mapped value looks wrong. | EM |
| RR-ONE-181964-12 | LOW | C3 | Tracking fields disagree. The "Epic Status" field reads "To Do" while the status is Done. The Epic has no fix version, while its children span hedgeppm-cloud-1.0.0, bigpicture-cloud-8.74.0.2, and preprod 8.74, plus the unreleased preprod 8.73 (ONE-257528, ONE-257570); ONE-257527 has none. | Release-based regression filters will miss or misplace this Epic. | EM |
| RR-ONE-181964-13 | LOW | A8 | A Google Drive file is linked from the Epic's web links and was not fetched (non-Confluence document). Nothing in the analyzed text says what it holds, so it is not treated as a likely source of acceptance criteria. | Low impact; if it is a spec or recording, the facts above may be incomplete. | PO |

## Clarification questions

### Definition of done

#### Q1. What epic-level acceptance criteria define "metrics as fields in Jira" as delivered: which field types can be linked, what the user configures per option, and which direction values sync?
- Context: The Epic's only acceptance criterion covers the multiple-contexts case; the core behaviour is spread across child descriptions. · Source: AC field (customfield_10901); Epic description, "After the change" · Priority: High · Unblocks: RR-ONE-181964-01 · Owner: PO

#### Q2. Where is the QA and Product acceptance for this Epic recorded, and was any path skipped or deferred during verification?
- Context: The Confluence project page makes QA and Product acceptance the completion step; no testing child, acceptance record, or Xray execution is linked to the Epic. · Source: Confluence — "Risk management: Link custom fields to metrics - Q2 26'" (appfireteam.atlassian.net) · Priority: Medium · Unblocks: RR-ONE-181964-09 · Owner: PO

#### Q3. Were the two items in Elena Kolesnik's 2026-07-17 comment (reopening the configuration after values change; adding the field to the screen) handled as product behaviour, as documentation (DOCBP-4395), or not at all?
- Context: No reply or linked follow-up; both items match behaviour in child descriptions. · Source: Comment @Elena Kolesnik, 2026-07-17 · Priority: Medium · Unblocks: RR-ONE-181964-03 · Owner: PO

### Rollout

#### Q4. How did this reach users: behind a flag, staged, or on for everyone with the 8.74 / hedgeppm-cloud-1.0.0 releases?
- Context: Only release versions are named; no rollout statement exists. · Source: Confluence project page release table; child fix versions · Priority: Medium · Unblocks: RR-ONE-181964-08 · Owner: PO

### Behavior

#### Q5. With the listener story ONE-257529 Canceled, what should the Risk matrix and other views show for an issue whose Jira field changed but which hasn't been listed in the risk register table since?
- Context: ONE-320856 syncs on listing; ONE-257576 states stored values go outdated for unlisted issues. · Source: ONE-320856 description; ONE-257576 description; child inventory · Priority: Medium · Unblocks: RR-ONE-181964-04 · Owner: EM

### Scope

#### Q6. The Epic lists a Jira field "created automatically by BigPicture" as one of two paths. Was that path delivered, deferred, or dropped?
- Context: Every child description with matching terms covers the user-selected field path only. · Source: Epic description, "After the change"; child inventory · Priority: High · Unblocks: RR-ONE-181964-02 · Owner: PO

### Edge cases

#### Q7. What should the user see when a Jira field update fails, or succeeds for only some issues, after a metric option changes in the configuration?
- Context: ONE-320856 updates every affected issue from the frontend; no failure handling is stated. · Source: ONE-320856 description · Priority: Medium · Unblocks: RR-ONE-181964-05 · Owner: EM

### Permissions

#### Q8. Can the permissions answer recorded as an image in ONE-249893 (who can change the configuration; which custom fields are listed) be stated in text on the Epic?
- Context: The question is in text; the answer is image-only. · Source: ONE-249893 description · Priority: Medium · Unblocks: RR-ONE-181964-06 · Owner: PO

## Not stated in epic

- An epic-level completion criterion for the core mapping flow.
- Whether the automatically created Jira field path shipped.
- What views other than the risk register table show for issues not yet re-listed after a Jira-side change.
- Error and partial-failure handling for Jira field updates.
- Who may link a Jira field to a metric (answer exists only as an image in ONE-249893).
- How the feature was rolled out (flag, staged, or everyone).
- A QA or Product acceptance record.
- Performance expectations for bulk updates, and any audit or logging of mapping changes.
- What the linked Google Drive file contains.
- Descriptions for 10 of 20 children, including ONE-272341 and ONE-293797.

## Known or suspected risks

- Values can drift between Jira and BigPicture for issues that aren't re-listed, because the listener story was Canceled. This is the Epic's main data-integrity regression surface. *(Source: ONE-320856, ONE-257576, ONE-257529)*
- Bulk frontend updates of every affected issue on a configuration change have no stated failure handling. *(Source: ONE-320856)*
- If the automatically created field path was expected by customers (the strategy page lists field mapping as a Hedge need), its absence would surface as a support issue rather than in regression. *(Source: Gap analysis; Confluence strategy page)*

## Suggested testing focus

- Round trip: select a metric option in BigPicture and confirm the Jira field; change the Jira field and confirm the risk register table, Risk Score, and Risk Level after listing. *(waits on: Q5)*
- Default-context-only behaviour and the two messages in ONE-326432 for fields without a default context or options.
- Dropdown disabled states from editmeta, across team-managed and company-managed projects.
- Changing or removing an option in the metric configuration and its effect on every affected issue. *(waits on: Q7)*
- Role coverage for linking a field to a metric. *(waits on: Q8)*
- Automatically created Jira field path, once its status is confirmed. *(waits on: Q6)*

## Information identified

- Goal: metrics from the Risk Management module can be mapped to a Jira field, either created automatically by BigPicture or selected by the user, configured in Risk Register settings → Metrics. *(Source: Epic description)*
- Acceptance criterion: "In case multiple contexts - Risk matrix should display only default context for this first iteration." *(Source: AC field (customfield_10901))*
- Weekly sync decision: "We will not support multiple custom field contexts. Only default context will be used." *(Source: Confluence — "Risk management: Link custom fields to metrics - Q2 26'" (appfireteam.atlassian.net))*
- Planned scope: "We will list custom fields of type select"; "User will be allowed to select a color for each option"; "User will be allowed to select a numeric value for each option"; "By default no custom field is linked to a metric". *(Source: Confluence — "2026-Q2 - Omega team tasks estimation" (appfireteam.atlassian.net))*
- Owners named: Product Elena Kolesnik, UX Karolina Chrzanowska, Engineering Leo Nunes / Valter Junior / Przemysław Dziedzic, QA Chai Prasad K. Release 8.74 planned for both frontend and backend. *(Source: Confluence — "Risk management: Link custom fields to metrics - Q2 26'" (appfireteam.atlassian.net))*
- Selected metric values are stored in the Jira issue entity property and, for linked metrics, also in the Jira custom field. Jira-side changes are synced when the risk register issues table is listed. *(Source: ONE-320856 description)*
- Options added to or deleted from the Jira field appear on the configuration page and reach the select list once the configuration is saved. *(Source: ONE-249893 description)*
- Out of scope for this work: "Add/Remove more values when using Jira fields". *(Source: ONE-249893 description, "Future requirements [Not on this task]")*
- The listener for Jira-side field changes (ONE-257529, stretch goal) was Canceled with resolution Won't Do on 2026-06-16. *(Source: Child inventory)*
- Screenshot 1 shows "RR - Settings" with a Metrics section: Likelihood (Rare to Certain, values 1 to 5) and Consequence (Insignificant to Severe, values 1 to 5). Screenshot 2 is a Confluence "Risks configuration" capture labelled "Old Risks mapping example". *(Source: Screenshot — Epic attachments dated 2026-03-12)*
- Linked design and delivery issues: UX-378 "Risk management: columns as fields in Jira" (Done), HED-288 "Metrics can be synchronized with Jira fields (single select)" (Done), DOCBP-4395 "Risk management: Metrics as fields in Jira" (Done). *(Source: Issue links on ONE-181964)*

## QA readiness checklist (preliminary)

| # | Check | Source | Owner | Done |
|---|-------|--------|-------|------|
| 1 | A single-select Jira custom field can be linked to a metric in Risk Register settings → Metrics | Epic description; Confluence estimation page ("custom fields of type select") | QA | ☐ |
| 2 | Only options from the field's default context are listed when the field has multiple contexts | AC field (customfield_10901); ONE-272341 (title only) | QA | ☐ |
| 3 | The two messages for no default context and for a default context without options appear as worded in ONE-326432 | ONE-326432 description | QA | ☐ |
| 4 | Selecting a metric option on an issue updates the linked Jira field; changing the value in Jira updates BigPicture when the risk register table is listed | ONE-320856 description | QA | ☐ |
| 5 | The metric dropdown is disabled when the field is missing from editmeta or has empty allowedValues (team-managed and company-managed projects) | ONE-320856 description | QA | ☐ |
| 6 | Metric option names are read-only when they come from a Jira field | ONE-257573 (title only) | QA | ☐ |
| 7 | Behaviour for unlisted issues after a Jira-side change | Pending Q5 | QA | ☐ |
| 8 | Automatically created Jira field path | Pending Q6 | QA | ☐ |

## Child inventory & status mix

**Full inventory — 20 children, paginated to `isLast`, never a sample.**  
**Status mix:** Done — 19 · Canceled — 1

| Key | Type | Status | Summary | Content |
|-----|------|--------|---------|---------|
| ONE-249893 | Task | Done | [MetricCustomFields] Prepare to define the API Contract with BP | description |
| ONE-257527 | Task | Done | [Backend] - Create function to list fields | description |
| ONE-257528 | Story | Done | [Backend] - Create function to list values once field is selected | description |
| ONE-257529 | Story | Canceled | [Backend] - (Stretch goal) Listen to changes on issue custom fields to update the value of our metrics | description |
| ONE-257569 | Story | Done | [MetricCustomFields][Frontend] Add dropdown with a list of Jira custom fields in Metric configuration | description |
| ONE-257570 | Story | Done | [MetricCustomFields][Frontend] Get the list of Jira custom fields from BigPicture backend | title_only |
| ONE-257571 | Story | Done | [MetricCustomFields][Frontend] Get Jira field context options and show them in Metric configuration | title_only |
| ONE-257572 | Story | Done | [MetricCustomFields][Frontend] Get the list of Jira field context options from BigPicture backend | title_only |
| ONE-257573 | Story | Done | [MetricCustomFields][Frontend] Make metric options name read-only when they are from Jira field | title_only |
| ONE-257574 | Story | Done | [MetricCustomFields][Frontend] Save the selected metric Jira field and options in the Metric configuration | title_only |
| ONE-257575 | Story | Done | [MetricCustomFields][Frontend] Modify metrics dropdown in the risk register issues list table to work with Jira field options | title_only |
| ONE-257576 | Story | Done | [MetricCustomFields][Frontend] Recalculate 'Risk Score' and 'Risk Level' on the frontend when loading the issues list table | description |
| ONE-257577 | Story | Done | [MetricCustomFields][Frontend] Align changes with UI design | description |
| ONE-272341 | Story | Done | [MetricCustomFields][Frontend] Only list custom field options from the default context | title_only |
| ONE-293797 | Story | Done | [MetricCustomFields][Frontend] Make sure risk configuration is persisting correctly | title_only |
| ONE-320854 | Story | Done | [MetricCustomFields][Frontend] Add getFieldGlobalContextOptionValues endpoint into the risks bridge | description |
| ONE-320856 | Story | Done | [MetricCustomFields][Frontend] Sync metric selected value with metric Jira custom field | description |
| ONE-326432 | Story | Done | [MetricCustomFields][Frontend] Display message when no default context or options are available | description |
| ONE-334626 | Story | Done | [MetricCustomFields] Modify test-host-app to work with the the custom fields implementation | title_only |
| ONE-340101 | Story | Done | [MetricCustomFields] Bump hedge-app package version in ppm | title_only |

## Epic batch handoff

Every child except the Canceled ONE-257529 is in the batch. Children named by open findings and questions come first; the rest follow in key order, since all are Done.

**Batch (every non-Canceled child, in scan order):** `ONE-320856` · `ONE-249893` · `ONE-257576` · `ONE-257569` · `ONE-272341` · `ONE-293797` · `ONE-257527` · `ONE-257528` · `ONE-257570` · `ONE-257571` · `ONE-257572` · `ONE-257573` · `ONE-257574` · `ONE-257575` · `ONE-257577` · `ONE-320854` · `ONE-326432` · `ONE-334626` · `ONE-340101`

- `confirm batch` — scan all 19 children in the order shown, 8 at a time
- `--batch keys <comma-separated>` — scan a specific subset

The batch does not run automatically.

## Recommended next action

Ask the PO Q1 and Q6 first, then the Medium questions. Run the child batch starting with ONE-320856 and the title-only children that carry the Epic's acceptance criterion (ONE-272341, ONE-293797).

---
_This review supports shift-left preparation. It does not approve or reject the requirement._
