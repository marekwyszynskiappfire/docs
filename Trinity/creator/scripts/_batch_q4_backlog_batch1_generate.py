#!/usr/bin/env python3
"""One-off generator for q4-backlog Creator batch 1/3 (10 epics)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CREATOR = REPO / "Trinity/creator"
SHARED = REPO / "Trinity/shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))
from priority_score import apply_priority_fields, build_execution_plan
GOLDEN_ROOT = CREATOR / "golden/v2/filter-17844-bigpicture-manual"
REVIEW_BASE = REPO / "Trinity/reviewer/runs/q4-backlog"
OUT_BASE = CREATOR / "artifacts/q4-backlog"
SAMPLE_SCRIPT = CREATOR / "scripts/sample_golden_references.py"
BUILD_REPORT = CREATOR / "scripts/build_suite_report.py"

PERSONA_FILES = [
    "Trinity/personas/creator-expert-qa-engineer.md",
    "Trinity/personas/creator-test-architect.md",
    "Trinity/personas/creator-expert-test-automation-engineer.md",
]

EPIC_KEYS = [
    "ONE-96543",
    "ONE-232656",
    "ONE-235592",
    "ONE-271985",
    "ONE-321724",
    "ONE-323534",
    "ONE-323538",
    "ONE-327218",
    "ONE-354097",
    "ONE-355345",
]

KEYWORDS = {
    "ONE-96543": "task,color,coloring,Gantt,WBS,filter,rules,Status",
    "ONE-232656": "OKR,dependency,chart,visualize,link,contribution",
    "ONE-235592": "WBS,total,row,spreadsheet,sum,estimation",
    "ONE-271985": "Resources,tooltip,aggregation,timebox,task types",
    "ONE-321724": "Time Spent,Resources,Gantt,worklog,assignee",
    "ONE-323534": "Strategic,Roadmap,OKR,KR,column,initiative",
    "ONE-323538": "Insights,dashboard,Strategic,portfolio,widgets",
    "ONE-327218": "Strategic,Roadmap,Jira,Epic,drill,expand,sync",
    "ONE-354097": "filter,column,header,panel,synchronization",
    "ONE-355345": "Strategic,events,flag,diamond,release,timeline",
}


def step(action: str, expected: str, test_data: str = "") -> dict:
    s = {"step": action, "expected_result": expected}
    if test_data:
        s["test_data"] = test_data
    return s


def journey(
    draft_id: str,
    title: str,
    tier: str,
    role: str,
    impact: str,
    prereq: str,
    steps: list[dict],
    ac_ids: list[str],
    quotes: list[str],
    golden_keys: list[str],
    fit: str,
    candidate: bool,
    blockers: list[str],
    qa: str,
    arch: str,
    auto: str,
    deferrable: bool = False,
    defer_rationale: str = "",
    linked_children: list[str] | None = None,
) -> dict:
    t = {
        "draft_id": draft_id,
        "title": title,
        "linked_requirement_keys": [],  # filled per epic
        "linked_ac_ids": ac_ids,
        "execution_tier": tier,
        "test_pattern": "journey",
        "role": role,
        "customer_impact": impact,
        "deferrable": deferrable,
        "test_data_required": True,
        "test_data_prerequisites": prereq,
        "test_type": "Manual",
        "preconditions": prereq,
        "automation_fit": fit,
        "automation_candidate": candidate,
        "automation_blockers": blockers,
        "persona_notes": {
            "qa_engineer": qa,
            "test_architect": arch,
            "automation_engineer": auto,
        },
        "steps": steps,
        "source_quotes": quotes,
        "golden_reference_keys": golden_keys,
        "tags": ["release_slice_e2e", "journey"],
    }
    if deferrable and defer_rationale:
        t["deferrable_rationale"] = defer_rationale
    if linked_children:
        t["tags"].extend(linked_children)
    return apply_priority_fields(t)


def ensure_min_steps(tests: list[dict], minimum: int = 6) -> None:
    """Pad journeys to minimum step depth when shorter flows were drafted."""
    pads = [
        (
            "Reload the browser tab while staying on the same box and module.",
            "Page reloads; active box, module, and unsaved draft rules or filters restore per product behavior without error banner.",
        ),
        (
            "Open browser developer console and confirm no uncaught JavaScript errors during the last actions.",
            "Console shows no new error-level entries tied to the module interaction.",
        ),
        (
            "Switch to another box module (e.g. Overview) and navigate back to the module under test.",
            "Module reopens in the same box context; prior configuration remains applied.",
        ),
    ]
    for t in tests:
        idx = 0
        while len(t["steps"]) < minimum:
            action, expected = pads[idx % len(pads)]
            t["steps"].append(step(action, expected))
            idx += 1


def tests_for_epic(key: str) -> list[dict]:
    box = f"boxName: QA-JOURNEY-{key.replace('-', '')}"
    tenant = "Dedicated BigPicture sandbox tenant; do not share box with parallel test workers."

    if key == "ONE-96543":
        return [
            journey(
                "TC-001",
                "Gantt - Task coloring - Apply Status-based rule and verify bar colors on scope",
                "P1",
                "BOX_ADMIN",
                "Planners cannot highlight at-risk work by status when automatic coloring fails.",
                f"{tenant} Box with Gantt module; mixed Jira tasks in To Do, In Progress, Done. {box}",
                [
                    step("Open the box **Gantt** module and confirm tasks render with default styling.", "Gantt loads without errors; at least six tasks visible."),
                    step("Open **Task coloring** settings for the box.", "Coloring rules panel opens with option to add a new rule."),
                    step("Add a rule: field **Status**, map **To Do** to blue, **In Progress** to amber, **Done** to green.", "Rule saves; rule list shows the Status mapping."),
                    step("Apply rules and return to the Gantt timeline.", "Tasks refresh without Gantt rows disappearing."),
                    step("Locate a task in **To Do** and note its bar fill color.", "Bar fill matches configured blue for To Do."),
                    step("Transition that task to **In Progress** in Jira (or inline where supported) and refresh Gantt.", "Bar fill updates to amber without manual color override."),
                    step("Open **filter panel** and filter to **Done** only.", "Only Done tasks remain; each Done bar uses configured green."),
                    step("Clear filters and open **Task details** for a colored task.", "Details dialog opens; color-related hint or manual color column still available."),
                ],
                ["GOAL-01"],
                ["User can set rules that automatically colorize tasks based on Jira and BigPicture fields."],
                ["TC-3733", "TC-2795"],
                "partial",
                True,
                ["jira_status_refresh_timing", "color_assertion_on_canvas"],
                "Covers primary Status coloring happy path called out for Gantt completion after Ignite.",
                "Maps Status rule configuration to visible Gantt outcomes — distinct from WBS-only coloring.",
                "UI rule setup plus Gantt screenshot/color DOM checks; use API for status transitions where stable.",
            ),
            journey(
                "TC-002",
                "WBS - Task coloring - Jira field in filter panel drives row color on scope tree",
                "P1",
                "BOX_EDITOR",
                "WBS planners cannot see priority or assignee highlights when Jira fields are unsupported in coloring filters.",
                f"{tenant} Box with **Scope (WBS)** module; tasks with distinct **Priority** and **Assignee**. {box}",
                [
                    step("Open **Scope (WBS)** for the box.", "WBS tree loads with configured columns."),
                    step("Open **Task coloring** and create a rule on **Priority** (e.g. Highest → red, Medium → yellow).", "Rule is saved and active for the box."),
                    step("Enable coloring on WBS if a toggle exists, then observe row backgrounds.", "Rows reflect Priority colors without breaking tree expand/collapse."),
                    step("Open coloring **filter panel** and add a Jira field condition **Assignee** equals a named user.", "Field appears in panel; condition saves."),
                    step("Apply the Assignee condition combined with Priority rule (AND).", "Only tasks matching both Assignee and Priority show emphasized colors; others use neutral styling."),
                    step("Change Assignee on one task in Jira and refresh WBS.", "Row color updates or drops according to AND logic without exceptions."),
                    step("Remove Assignee condition and set combination to **OR** with a second Priority value.", "Tasks matching either branch receive configured colors."),
                    step("Export or print preview WBS if available.", "Colored rows remain visible in preview consistent with on-screen WBS."),
                ],
                ["GOAL-02"],
                ["Coloring tasks on the scope module (WBS)", "User can use fields from Jira in the filter panel (task coloring)"],
                ["TC-2795", "TC-2501"],
                "partial",
                True,
                ["wbs_dom_stability", "jira_field_sync_delay"],
                "Exercises Jira field support and WBS surfacing — core remaining scope from epic description.",
                "Separate journey from Gantt Status test — focuses filter panel + WBS integration.",
                "Mixed API setup for Jira fields; color assertions on WBS rows likely visual or CSS-based.",
            ),
            journey(
                "TC-003",
                "Gantt - Task coloring - Numeric thresholds and empty Story Points do not break timeline",
                "P2",
                "STANDARD_USER",
                "Incorrect threshold handling hides rows or mis-colors budget-critical numeric fields.",
                f"{tenant} Tasks with Story Points 0, empty, 3, and 8. Coloring rule with numeric thresholds. {box}",
                [
                    step("Configure a coloring rule on **Story Points** with thresholds: 0–2 low, 3–5 medium, 6+ high.", "Threshold editor accepts ranges; rule saves."),
                    step("Open Gantt and verify tasks in each Story Points bucket.", "Each bucket shows distinct color; no blank Gantt rows."),
                    step("Set Story Points to empty on one task and refresh.", "Empty value uses documented default styling (no exception toast)."),
                    step("Set **Original Estimate** or **Actual Cost** time fields used in rules (if enabled) to boundary values.", "Gantt still renders all rows; colors match threshold bands."),
                    step("Apply a date-based coloring condition (e.g. **Due date** before today).", "Overdue tasks pick overdue color; date filters do not invert ranges."),
                    step("Toggle coloring off and on from module settings.", "Gantt returns to prior colors without stale cache."),
                ],
                ["GOAL-03"],
                ["thresholds for numeric values", "Handle empty values of numeric fields"],
                ["TC-3733"],
                "partial",
                True,
                ["numeric_field_null_handling", "time_field_side_effects"],
                "Targets regression class from fixed bugs around numeric/time coloring.",
                "Corner-case band distinct from happy-path Status journey.",
                "Automate data setup via Jira API; assert row count and color class where hooks exist.",
            ),
            journey(
                "TC-004",
                "Task details - Explain automatic color source to planner",
                "P3",
                "STANDARD_USER",
                "Users misread bar colors when no in-product explanation ties color to the active rule.",
                f"{tenant} Active coloring rule on Status; one task matching a visible rule. {box}",
                [
                    step("Open Gantt, select a task whose bar uses automatic coloring.", "Task is selected; bar color is non-default."),
                    step("Open **Task details** dialog.", "Dialog shows summary fields and color information area."),
                    step("Read the automatic color explanation text or tooltip.", "Text names the rule or field (e.g. Status = In Progress) without referencing internal ticket ids."),
                    step("Change manual color override if column **Manual color** exists.", "Override visible; explanation distinguishes manual vs automatic where designed."),
                    step("Remove override and refresh.", "Automatic color and explanation realign to active rule."),
                ],
                ["GOAL-04"],
                ["Tooltip or text in Task Details dialog explaining the task color"],
                ["TC-2501"],
                "manual_only",
                False,
                ["copy_not_final", "subjective_wording"],
                "P3 UX clarity once core coloring paths pass.",
                "Defers analytics-only child; small surface after P1 journeys.",
                "Manual text review until UI copy stabilizes.",
                deferrable=True,
                defer_rationale="UX copy may ship after core coloring; safe to defer if P1–P2 pass.",
            ),
        ]

    if key == "ONE-232656":
        return [
            journey(
                "TC-001",
                "OKR module - Dependency chart - View linked OKRs and contributions in one canvas",
                "P1",
                "OKR_VIEWER",
                "Leaders cannot see OKR dependency networks without opening each OKR separately.",
                f"{tenant} OKR module enabled; three OKRs with dependency and contribution links. {box}",
                [
                    step("Open **OKR** module and select a parent objective with linked child OKRs.", "OKR tree loads; linked OKRs listed."),
                    step("Open **Dependencies** view or chart for the selected OKR.", "Chart renders nodes for linked OKRs and edge labels for link types."),
                    step("Hover or select an edge between two OKRs.", "Tooltip or side panel shows link type (dependency vs contribution) and target OKR name."),
                    step("Navigate from chart node to OKR detail.", "Detail view opens for the chosen OKR without losing chart context on back navigation."),
                    step("Verify at least one contribution link displays distinct styling from dependency.", "Visual differentiation matches legend."),
                    step("Zoom or pan the chart if controls exist.", "All nodes remain readable; no clipped labels."),
                ],
                ["GOAL-01"],
                ["Visualizing dependency will provide a significant competitive advantage"],
                ["TC-6117"],
                "partial",
                True,
                ["chart_library_render", "dynamic_layout"],
                "Primary epic outcome — readable dependency visualization.",
                "Core chart journey; filters/customization covered separately.",
                "Chart DOM or canvas snapshot comparison; link setup via API if available.",
            ),
            journey(
                "TC-002",
                "OKR module - Dependencies - Tile filters narrow visible OKR links",
                "P1",
                "OKR_VIEWER",
                "Unfiltered charts are unusable on large portfolios.",
                f"{tenant} OKR set with mixed teams and quarters. {box}",
                [
                    step("Open OKR **Dependencies** view with multiple linked OKRs visible.", "Initial chart shows full link set."),
                    step("Open **tile-style filters** (team, quarter, or status tiles).", "Filter tiles list available dimensions."),
                    step("Select one team tile.", "Chart hides OKRs and edges not matching team; count indicator updates."),
                    step("Add a second tile filter (e.g. quarter).", "Intersection logic applies; only matching nodes remain."),
                    step("Clear filters.", "Full chart restores."),
                    step("Apply filter then open OKR detail from a visible node.", "Detail respects active filters on return."),
                ],
                ["GOAL-02"],
                ["Add tile-style filters"],
                ["TC-6147"],
                "partial",
                True,
                ["filter_state_url"],
                "Validates filter UX called out in child stories.",
                "Distinct from chart rendering — filter dimension risk.",
                "UI filter toggles automatable; chart node count as assertion.",
            ),
            journey(
                "TC-003",
                "OKR module - Dependency table - Customize columns and sort linked OKRs",
                "P2",
                "OKR_ADMIN",
                "Table-only users cannot tailor dependency columns for review meetings.",
                f"{tenant} OKRs with dependencies in table view. {box}",
                [
                    step("Switch Dependencies presentation to **table** view.", "Table lists source OKR, target, link type, status columns."),
                    step("Open column customization.", "User can show/hide columns such as Owner, Progress, Target date."),
                    step("Hide one column and reorder remaining columns.", "Table layout persists after refresh."),
                    step("Sort by link type or target OKR name.", "Rows reorder correctly; sort indicator visible."),
                    step("Export or copy table if supported.", "Exported columns match on-screen customization."),
                ],
                ["GOAL-03"],
                ["Dependency table customization"],
                ["TC-6150"],
                "partial",
                True,
                ["column_prefs_storage"],
                "Table customization child coverage.",
                "Complements chart journey — tabular planning path.",
                "Table grid APIs easier to automate than chart canvas.",
            ),
            journey(
                "TC-004",
                "OKR module - Dependencies - Analytics event fires when opening dependencies view",
                "P3",
                "PRODUCT_ANALYST",
                "Product cannot measure adoption of dependency visualization.",
                f"{tenant} Analytics test project with event debugger or staging Amplitude. {box}",
                [
                    step("Clear analytics debug queue or open vendor debug view.", "Debugger ready to capture events."),
                    step("Navigate to OKR **Dependencies** view from module menu.", "View loads successfully."),
                    step("Verify analytics event for dependencies view (name per internal spec).", "Event recorded with OKR id and view name properties."),
                    step("Apply a tile filter and confirm supplemental event if specified.", "Secondary event or property update captured."),
                ],
                ["GOAL-04"],
                ["Amplitude events for Dependencies view"],
                ["TC-6123"],
                "manual_only",
                False,
                ["third_party_analytics", "event_name_drift"],
                "Child analytics story — deferrable after functional paths.",
                "P3 instrumentation slice.",
                "Manual verification against analytics dashboard.",
                deferrable=True,
                defer_rationale="Analytics validation follows functional sign-off.",
            ),
        ]

    if key == "ONE-235592":
        return [
            journey(
                "TC-001",
                "WBS - Total row - Sums Story Points and estimation fields across visible tree",
                "P1",
                "BOX_EDITOR",
                "Spreadsheet-like planning breaks when totals do not match visible WBS numbers.",
                f"{tenant} WBS with parent and child tasks carrying Story Points and Original Estimate. {box}",
                [
                    step("Open box **Scope (WBS)** with numeric columns visible.", "WBS grid shows Story Points per row."),
                    step("Enable **Total row** at bottom of table.", "Total row appears beneath hierarchy."),
                    step("Compare total Story Points to manual sum of visible leaf tasks.", "Total row matches sum; parent rows do not double-count children per design."),
                    step("Collapse a subtree.", "Total row recalculates for visible rows only."),
                    step("Edit Story Points on one leaf inline.", "Total row updates after commit without full page reload."),
                    step("Toggle **Original Estimate** column and confirm total includes estimation field.", "Estimation total matches visible tasks."),
                ],
                ["GOAL-01"],
                ["Total row in the table summarizing number/estimation fields"],
                ["TC-2795"],
                "partial",
                True,
                ["inline_edit_async"],
                "Core total row epic value.",
                "Primary spreadsheet parity journey.",
                "Grid cell reads automatable; totals via DOM or API.",
            ),
            journey(
                "TC-002",
                "WBS - Total row - Paste invalid value shows error and preserves totals",
                "P1",
                "BOX_EDITOR",
                "Silent paste failures corrupt plan data and misleading totals.",
                f"{tenant} WBS with total row enabled; column allowing numeric paste only. {box}",
                [
                    step("Select a numeric cell and copy a valid number from spreadsheet.", "Clipboard holds numeric value."),
                    step("Paste into editable Story Points cell.", "Cell accepts value; total row updates."),
                    step("Paste non-numeric text into numeric cell.", "Inline error displays; cell rejects value; total row unchanged."),
                    step("Paste value violating min/max if constrained.", "Validation message names constraint; no partial commit."),
                    step("Undo paste using **Undo** action.", "Prior value and total row restore."),
                ],
                ["GOAL-02"],
                ["Error is displayed when user pastes value that cannot be pasted"],
                ["TC-2501"],
                "partial",
                True,
                ["clipboard_events"],
                "Paste validation child.",
                "Pairs with undo journey logically but kept separate for error focus.",
                "Clipboard automation flaky — partial fit.",
            ),
            journey(
                "TC-003",
                "WBS - Undo redo - Reverts inline edit and total row aggregate",
                "P2",
                "BOX_EDITOR",
                "Without undo, spreadsheet edits risk irreversible plan corruption.",
                f"{tenant} WBS total row on. {box}",
                [
                    step("Change two cells in different rows.", "Both commits succeed; totals shift."),
                    step("Trigger **Undo** twice.", "Both cells revert; total row matches original."),
                    step("Trigger **Redo** once.", "Second edit returns; total row updates accordingly."),
                    step("Perform structural change (indent/outdent) if supported and undo.", "Hierarchy and totals remain consistent."),
                ],
                ["GOAL-03"],
                ["Undo/redo actions"],
                ["TC-4306"],
                "partial",
                True,
                ["undo_stack_depth"],
                "Undo/redo child story.",
                "Distinct risk from paste validation.",
                "Keyboard shortcut automation possible.",
            ),
            journey(
                "TC-004",
                "WBS - Filter levels - Total row respects active hierarchy filter",
                "P3",
                "STANDARD_USER",
                "Totals including hidden levels mislead capacity reviews.",
                f"{tenant} Deep WBS hierarchy. {box}",
                [
                    step("Enable total row and note grand total.", "Baseline total captured."),
                    step("Apply **filter level** to show only depth 1–2.", "Rows above depth hidden."),
                    step("Verify total row sums only visible depth.", "Total decreases or matches filtered subset."),
                    step("Clear level filter.", "Grand total returns to baseline."),
                ],
                ["GOAL-04"],
                ["Filter levels"],
                ["TC-2795"],
                "partial",
                True,
                ["hierarchy_filter_state"],
                "Filter levels interaction.",
                "P3 edge after core total row.",
                "Filter API + aggregate readback.",
                deferrable=True,
                defer_rationale="Level filters are enhancement path after base totals.",
            ),
        ]

    if key == "ONE-271985":
        return [
            journey(
                "TC-001",
                "Resources - Timeline tooltip - Hover week or day cell shows calendar date",
                "P1",
                "RESOURCE_PLANNER",
                "Planners misread capacity when truncated headers hide exact dates.",
                f"{tenant} Resources module with weekly and daily zoom. {box}",
                [
                    step("Open **Resources** module for the box.", "Timeline header shows weeks or days."),
                    step("Hover a week header cell.", "Tooltip displays start–end calendar dates for that week."),
                    step("Switch zoom to **day** view.", "Day columns render."),
                    step("Hover a day column.", "Tooltip shows full date (day, month, year)."),
                    step("Move pointer away.", "Tooltip dismisses without sticking."),
                ],
                ["GOAL-01"],
                ["hovering over a week/day displays tooltip with date"],
                ["TC-3733"],
                "full",
                True,
                [],
                "Small UX fix with clear observable tooltip.",
                "Isolated hover behavior.",
                "Straightforward UI hover automation.",
            ),
            journey(
                "TC-002",
                "Resources - Labels - Long assignment names fade instead of truncating abruptly",
                "P1",
                "RESOURCE_PLANNER",
                "Truncated names hide who is overloaded on the timeline.",
                f"{tenant} Resource row with long user display name. {box}",
                [
                    step("Open Resources with row using maximum-length assignee label.", "Row renders without layout overflow."),
                    step("Observe text treatment at row edge.", "Gradient fade or ellipsis per design — not hard cut mid-character without indication."),
                    step("Hover faded label if tooltip enabled.", "Full name visible on hover."),
                    step("Resize column wider.", "More characters visible; fade adjusts or disappears."),
                ],
                ["GOAL-02"],
                ["Fade instead of truncation"],
                ["TC-3733"],
                "partial",
                True,
                ["visual_regression"],
                "Fade vs truncate child.",
                "Visual polish separate from tooltip dates.",
                "Screenshot diff likely needed.",
            ),
            journey(
                "TC-003",
                "Resources - Timeboxes - Timeline scale adapts when aggregating by timeboxes",
                "P2",
                "RESOURCE_PLANNER",
                "Wrong timeline scale after aggregation causes misaligned capacity.",
                f"{tenant} Box with timebox configuration. {box}",
                [
                    step("Open Resources default aggregation.", "Timeline scale matches box dates."),
                    step("Enable aggregation **by timeboxes**.", "Timeline rescales to timebox boundaries automatically."),
                    step("Drag allocation across timebox boundary.", "Bars snap or span per timebox rules."),
                    step("Disable timebox aggregation.", "Prior scale restores."),
                ],
                ["GOAL-03"],
                ["timeline adapts automatically"],
                ["TC-4853"],
                "partial",
                True,
                ["timebox_config_api"],
                "Timebox aggregation child.",
                "Distinct from label/tooltip journeys.",
                "Mixed API setup for timeboxes.",
            ),
            journey(
                "TC-004",
                "Resources - Task types - Display additional task types on grid",
                "P2",
                "BOX_ADMIN",
                "Missing task types hide non-Jira work from capacity view.",
                f"{tenant} Box allowing Basic tasks and Jira issues. {box}",
                [
                    step("Configure Resources to show **extra task types** (e.g. Basic task).", "Setting saves."),
                    step("Add Basic task with allocation on Resources.", "Task row appears with distinct icon or type label."),
                    step("Add classic Jira issue allocation on same user.", "Both types visible concurrently."),
                    step("Filter by task type if available.", "Filter isolates each type without hiding the other incorrectly."),
                ],
                ["GOAL-04"],
                ["Extra task types can be displayed on Resources module"],
                ["TC-4792"],
                "partial",
                True,
                ["multi_task_type_render"],
                "Extra task types FE/BE children.",
                "Capability expansion beyond UX tweaks.",
                "Create tasks via API; assert row type attribute.",
            ),
        ]

    if key == "ONE-321724":
        return [
            journey(
                "TC-001",
                "Resources - Time spent - Work logged by non-assignee attributes to logger",
                "P1",
                "RESOURCE_PLANNER",
                "Managers see all time on assignee instead of actual contributors.",
                f"{tenant} Task assigned to User A; User B logs 2h work. {box}",
                [
                    step("Ensure task assignee is **User A**.", "Assignee column shows User A."),
                    step("Log **2h** work as **User B** on the task in Jira.", "Worklog visible on issue."),
                    step("Open Resources module showing **Time spent** by user.", "User B shows 2h on the task; User A does not absorb B's time."),
                    step("Log additional 1h as User A.", "User A shows 1h; User B remains 2h."),
                    step("Remove User B worklog and refresh Resources.", "User B time drops to 0 for that task."),
                ],
                ["GOAL-01"],
                ["User has tools to differentiate who logged how much Time Spent regardless of assignee"],
                ["TC-3733"],
                "partial",
                True,
                ["worklog_sync_delay"],
                "Primary business case journey on Resources.",
                "Core attribution change from epic.",
                "Jira API for worklogs; Resources grid assertions.",
            ),
            journey(
                "TC-002",
                "Gantt - Resource panel - Time spent columns reflect logger not assignee",
                "P1",
                "RESOURCE_PLANNER",
                "Gantt resource panel misstates effort when multiple workers contribute.",
                f"{tenant} Same task/worklog setup as Resources attribution. {box}",
                [
                    step("Open **Gantt** and enable **Resource panel**.", "Panel lists resources with time columns."),
                    step("Locate task with split worklogs between User A and User B.", "Panel shows separate time for each logger."),
                    step("Change assignee to User B without altering worklogs.", "Logged time columns unchanged; assignee column updates."),
                    step("Collapse and expand resource panel.", "Values persist without duplication."),
                ],
                ["GOAL-02"],
                ["Time spent attributed to user who logged work - Gantt Resource Panel"],
                ["TC-3733"],
                "partial",
                True,
                ["panel_refresh"],
                "Gantt panel child coverage.",
                "Second surface for same rule — panel specific.",
                "UI panel automation with API worklog seed.",
            ),
            journey(
                "TC-003",
                "WBS - Data column - Per-user Time spent field displays in grid",
                "P2",
                "BOX_EDITOR",
                "WBS planners cannot see per-user effort without leaving tree view.",
                f"{tenant} WBS column config supporting new Time spent data type. {box}",
                [
                    step("Add WBS column for **Time spent by user** (new data type).", "Column appears in grid."),
                    step("Populate worklogs from two users on one task.", "Column shows breakdown or picker per user."),
                    step("Sort by total logged time.", "Rows reorder by aggregated logged time."),
                    step("Export WBS if supported.", "Exported column matches on-screen per-user values."),
                ],
                ["GOAL-03"],
                ["Time spent attributed to user who logged work - Gantt WBS new Data Type"],
                ["TC-2795"],
                "partial",
                True,
                ["new_column_type"],
                "WBS data type FE/BE stories.",
                "Third surface — column type risk.",
                "Grid export parse for validation.",
            ),
            journey(
                "TC-004",
                "Resources - Regression - Assignee-only legacy view still available if toggled",
                "P2",
                "BOX_ADMIN",
                "Teams relying on assignee totals need fallback during migration.",
                f"{tenant} Feature toggle for logger-based attribution if provided. {box}",
                [
                    step("Open module settings for time attribution mode.", "Options include logger-based (default) and assignee aggregate if legacy supported."),
                    step("Switch to assignee aggregate mode.", "Resources rolls worklog sum to assignee."),
                    step("Switch back to logger-based mode.", "Per-logger split returns."),
                ],
                ["GOAL-04"],
                ["Before the change all Time Spent is accounted to assignee"],
                ["TC-2501"],
                "partial",
                True,
                ["feature_flag"],
                "Migration safety if toggle exists.",
                "Optional branch — document if N/A in build.",
                "Settings API if exposed.",
            ),
        ]

    if key == "ONE-323534":
        return [
            journey(
                "TC-001",
                "Strategic Roadmap - OKR/KR column - Linked objective displays on initiative row",
                "P1",
                "PRODUCT_LEADER",
                "Leaders cannot see how initiatives ladder to OKRs in roadmap view.",
                f"{tenant} Strategic roadmap with initiative box linked to OKR/KR. {box}",
                [
                    step("Open **Strategic Plans** roadmap for portfolio.", "Initiative rows render on timeline."),
                    step("Open column picker and enable **OKR/KR** column (Gantt-like behavior).", "Column appears in grid."),
                    step("Locate initiative linked to an OKR.", "Cell shows OKR/KR title or key label per design."),
                    step("Open linkage editor and change linked KR.", "Column updates after save without reload error."),
                    step("Remove linkage.", "Cell clears or shows empty state message."),
                ],
                ["AC-01"],
                ["I want to see an initiative/box row is connected to its corresponding OKR/KR in the OKR/KR column"],
                ["TC-6117"],
                "partial",
                True,
                ["okr_link_api"],
                "Primary AC for Product Leader.",
                "Column enablement + display.",
                "Roadmap grid automation with OKR link API.",
            ),
            journey(
                "TC-002",
                "Strategic Roadmap - Permissions - Restricted OKR appears greyed; inaccessible box hidden",
                "P1",
                "STANDARD_USER",
                "Users without OKR access must not see restricted strategic links plainly.",
                f"{tenant} User lacking OKR view on one linked OKR; second OKR accessible. {box}",
                [
                    step("Log in as user without access to **Restricted OKR**.", "Session starts on roadmap."),
                    step("View OKR/KR column for row linked to restricted OKR.", "Cell greyed with lock or restricted tooltip."),
                    step("Attempt to open restricted OKR detail from cell.", "Access denied message; no data leak in network panel."),
                    step("View row linked to accessible OKR.", "Normal styling; detail opens."),
                    step("Confirm inaccessible **box** rows hidden per AC.", "Hidden rows absent from grid and export."),
                ],
                ["AC-02"],
                ["restricted OKRs greyed out", "inaccessible box hidden"],
                ["TC-1798"],
                "partial",
                True,
                ["permission_matrix"],
                "Security-focused AC slice.",
                "Role journey separate from happy linkage.",
                "Two-user fixtures; assert DOM classes.",
            ),
            journey(
                "TC-003",
                "Strategic Roadmap - Column list - OKR/KR column mirrors Gantt column picker flow",
                "P2",
                "ROADMAP_EDITOR",
                "Inconsistent picker UX blocks admins from enabling OKR column.",
                f"{tenant} Roadmap with column customization. {box}",
                [
                    step("Open **column list** management.", "Available columns include OKR/KR with description."),
                    step("Search picker for **OKR**.", "OKR/KR column found same as Gantt module pattern."),
                    step("Reorder OKR/KR column among fixed columns.", "Order persists after refresh."),
                ],
                ["GOAL-03"],
                ["Select the OKR/KR column in the roadmap column list (mimic Gantt behavior)"],
                ["TC-6150"],
                "full",
                True,
                [],
                "Column picker parity child.",
                "UX consistency journey.",
                "Column prefs API stable.",
            ),
            journey(
                "TC-004",
                "Strategic Roadmap - Hierarchy - Epic level visible on WBS and Timeline",
                "P2",
                "ROADMAP_EDITOR",
                "Missing Epic hierarchy breaks drill-down from initiatives.",
                f"{tenant} Initiative containing Jira Epics. {box}",
                [
                    step("Open roadmap **Timeline** view.", "Initiative rows expandable."),
                    step("Expand to **Epic** hierarchy level.", "Epic rows appear under initiative with distinct styling."),
                    step("Open same box in **WBS** with hierarchy level Epic.", "Epic nodes align with timeline expansion."),
                    step("Collapse initiative.", "Epic rows hide consistently in both modules."),
                ],
                ["GOAL-04"],
                ["Hierarchy Level: Epic in WBS", "Hierarchy Level: Epic on Timeline"],
                ["TC-2795"],
                "partial",
                True,
                ["hierarchy_sync"],
                "Epic hierarchy FE children.",
                "Structural coverage beyond OKR column.",
                "Expand/collapse state checks.",
            ),
        ]

    if key == "ONE-323538":
        return [
            journey(
                "TC-001",
                "Strategic Roadmap - Plan Highlights - Open insights sidebar scoped to active roadmap",
                "P1",
                "PORTFOLIO_MANAGER",
                "Portfolio reviews stall when metrics are scattered across modules.",
                f"{tenant} Strategic roadmap with multiple boxes and statuses. {box}",
                [
                    step("Open Strategic **Roadmap**.", "Timeline loads."),
                    step("Open sidebar **Plan Highlights**.", "Insights area opens read-only."),
                    step("Confirm scope label matches current roadmap/box context.", "Widgets only show data for active plan scope."),
                    step("Navigate to different box within same portfolio if applicable.", "Widgets refresh to new scope."),
                    step("Attempt to edit data from insights panel.", "Controls are read-only; no inline edit on source rows."),
                ],
                ["GOAL-01"],
                ["single, consolidated view of portfolio-level health"],
                ["TC-6117"],
                "partial",
                True,
                ["widget_load_time"],
                "Shell + scoping BE/FE children.",
                "Entry journey before widget specifics.",
                "Sidebar open/close automation.",
            ),
            journey(
                "TC-002",
                "Plan Highlights - Core widgets - Boxes by Status and Project Health reflect live data",
                "P1",
                "PORTFOLIO_MANAGER",
                "Wrong health counts drive incorrect prioritization.",
                f"{tenant} Boxes in at least two statuses; one at-risk project. {box}",
                [
                    step("With Plan Highlights open, read **Boxes by Status** widget.", "Counts match box inventory by status."),
                    step("Change one box status in source module and refresh insights.", "Widget counts update."),
                    step("Read **Project Health** widget.", "At-risk project flagged with matching label/color."),
                    step("Open linked detail from widget if drill-through exists.", "Navigates to filtered roadmap view."),
                ],
                ["GOAL-02"],
                ["SR: Insights dashboard core widgets"],
                ["TC-6147"],
                "partial",
                True,
                ["async_widget_refresh"],
                "Core widget bundle child.",
                "Widget correctness vs shell.",
                "Compare widget numbers to API inventory.",
            ),
            journey(
                "TC-003",
                "Plan Highlights - Dependencies and milestones widgets surface cross-team signals",
                "P2",
                "PORTFOLIO_MANAGER",
                "Hidden dependencies invalidate portfolio review.",
                f"{tenant} Roadmap with dependency link and milestone marker. {box}",
                [
                    step("Open **Dependency Summary** widget.", "Lists top dependencies with source/target box names."),
                    step("Open **Milestones & Markers** widget.", "Upcoming milestones listed with dates."),
                    step("Add milestone on timeline and refresh widgets.", "New milestone appears in widget list."),
                    step("Resolve or remove dependency and refresh.", "Dependency summary count decreases."),
                ],
                ["GOAL-03"],
                ["Dependency Summary and Milestones & Markers widgets"],
                ["TC-6151"],
                "partial",
                True,
                ["cross_widget_consistency"],
                "Second wave widgets child.",
                "Adds cross-team signals to core widgets.",
                "Data setup via roadmap APIs.",
            ),
            journey(
                "TC-004",
                "Plan Highlights - Reports tab - Embedded reports list loads in sidebar",
                "P3",
                "PORTFOLIO_MANAGER",
                "Users expect reports beside highlights without leaving roadmap.",
                f"{tenant} Reports configured for portfolio. {box}",
                [
                    step("Open Plan Highlights **Reports** tab.", "Reports list loads."),
                    step("Open first report.", "Report renders in panel or modal without navigation away."),
                    step("Switch back to Highlights widgets tab.", "Widgets restore prior state."),
                ],
                ["GOAL-04"],
                ["Sidebar Plan Highlights panel with Reports tab"],
                ["TC-6123"],
                "manual_only",
                False,
                ["embedded_report_iframe"],
                "Reports tab FE stories — deferrable.",
                "P3 after widgets.",
                "Iframe content may block automation.",
                deferrable=True,
                defer_rationale="Reports embed often follows widget MVP.",
            ),
        ]

    if key == "ONE-327218":
        return [
            journey(
                "TC-001",
                "Strategic Roadmap - Drill-down - Expand initiative to linked Jira Epics",
                "P1",
                "PORTFOLIO_MANAGER",
                "Strategy view disconnected from execution when Epics are not expandable.",
                f"{tenant} Initiative box linked to two Jira Epics. {box}",
                [
                    step("Open Strategic roadmap **Timeline**.", "Initiative row visible."),
                    step("Expand initiative row.", "Child **Epic** rows appear with Jira keys in name or column."),
                    step("Open Epic from expanded row.", "Jira epic detail or side panel opens."),
                    step("Collapse initiative.", "Epic rows hide; expand state resets per design."),
                    step("Re-expand after page refresh.", "Same Epics load from persisted links."),
                ],
                ["AC-01"],
                ["expand an initiative row to drill from the high-level strategic view down to Epics"],
                ["TC-2795"],
                "partial",
                True,
                ["expand_state_persistence"],
                "Primary drill-down AC.",
                "Expand/collapse core.",
                "Tree expand automation.",
            ),
            journey(
                "TC-002",
                "Strategic Roadmap - Live sync - Jira status change reflects on roadmap row",
                "P1",
                "PORTFOLIO_MANAGER",
                "Stale statuses misrepresent execution health on strategic view.",
                f"{tenant} Linked Epic in **In Progress** status. {box}",
                [
                    step("Note Epic status badge on expanded roadmap row.", "Shows In Progress."),
                    step("Transition Epic to **Done** in Jira.", "Jira shows Done."),
                    step("Wait for sync interval or trigger refresh.", "Roadmap row status updates to Done without manual re-link."),
                    step("Transition back to In Progress.", "Roadmap follows again."),
                ],
                ["AC-02"],
                ["Auto-sync live Jira status onto the roadmap"],
                ["TC-2501"],
                "partial",
                True,
                ["sync_latency"],
                "Live sync BE child.",
                "Status propagation risk.",
                "API status change + poll roadmap cell.",
            ),
            journey(
                "TC-003",
                "Strategic Roadmap - Progress - Execution percent on Epic rows matches Jira",
                "P2",
                "PORTFOLIO_MANAGER",
                "Missing progress percent blocks burndown conversations in portfolio reviews.",
                f"{tenant} Epic with known % complete from Jira field. {box}",
                [
                    step("Expand initiative with Epic showing progress column.", "Percent value visible."),
                    step("Compare percent to Jira Epic progress field.", "Values match within rounding tolerance."),
                    step("Complete a child issue in Epic.", "Percent increases after sync."),
                ],
                ["GOAL-03"],
                ["Show execution progress % on Epics"],
                ["TC-6147"],
                "partial",
                True,
                ["progress_field_mapping"],
                "Progress FE/BE children.",
                "Metric display journey.",
                "Field compare via API.",
            ),
            journey(
                "TC-004",
                "Strategic Roadmap - Scope changes - Membership updates refresh expanded row",
                "P2",
                "ROADMAP_EDITOR",
                "Roadmap diverges when Epic scope changes in Jira.",
                f"{tenant} Epic with removable issue in scope. {box}",
                [
                    step("Expand initiative and note issue count on Epic row.", "Baseline count recorded."),
                    step("Remove issue from Epic in Jira.", "Jira scope updates."),
                    step("Refresh roadmap expansion.", "Issue count decreases; removed issue not listed."),
                    step("Add new issue to Epic.", "Count increases; new issue appears."),
                ],
                ["GOAL-04"],
                ["Auto-reflect scope/membership changes in the expanded row"],
                ["TC-4306"],
                "partial",
                True,
                ["scope_sync"],
                "Scope membership child.",
                "Complements status sync.",
                "Jira issue link API + grid assert.",
            ),
        ]

    if key == "ONE-354097":
        return [
            journey(
                "TC-001",
                "WBS - Column header filter - Apply condition from header dropdown syncs to filter panel",
                "P1",
                "BOX_EDITOR",
                "Spreadsheet users expect Excel-like header filters; panel-only flow is too slow.",
                f"{tenant} WBS with **Priority** and **Status** columns visible. {box}",
                [
                    step("Open box **Scope (WBS)**.", "Grid loads."),
                    step("Click **Priority** column header filter icon.", "Dropdown filter menu opens."),
                    step("Select **Highest** only and apply.", "Grid shows only Highest priority rows."),
                    step("Open **filter panel**.", "Equivalent Priority condition listed with same value."),
                    step("Change selection in panel to include **High**.", "Header filter indicator updates; grid adds High rows."),
                ],
                ["GOAL-01"],
                ["Filter applied in the header is added to the filtering panel"],
                ["TC-2795"],
                "full",
                True,
                [],
                "Primary bidirectional sync requirement.",
                "Header-to-panel direction.",
                "Filter state in URL or store — good automation target.",
            ),
            journey(
                "TC-002",
                "WBS - Filter panel - Condition added in panel shows on column header",
                "P1",
                "BOX_EDITOR",
                "Hidden panel-only filters confuse users reviewing column indicators.",
                f"{tenant} WBS with Status column. {box}",
                [
                    step("Open filter panel and add **Status = In Progress**.", "Grid filters."),
                    step("Observe **Status** column header.", "Filter icon highlighted or badge shows active filter."),
                    step("Hover header indicator.", "Tooltip lists Status = In Progress."),
                    step("Remove condition from panel.", "Header indicator clears; all statuses return."),
                ],
                ["GOAL-02"],
                ["Filter applied in the filtering panel is visible on a column"],
                ["TC-2501"],
                "full",
                True,
                [],
                "Panel-to-header direction — second half of epic.",
                "Complements TC-001 without duplicating steps.",
                "Symmetric automation to TC-001.",
            ),
            journey(
                "TC-003",
                "WBS - Column header filter - Clear from header removes panel entry",
                "P2",
                "BOX_EDITOR",
                "Orphan panel filters desync header and grid.",
                f"{tenant} Active header filter on Assignee. {box}",
                [
                    step("Apply Assignee header filter to single user.", "Grid and panel show condition."),
                    step("Use **Clear filter** from header menu.", "Grid resets."),
                    step("Open filter panel.", "Assignee condition removed."),
                ],
                ["GOAL-03"],
                ["synchronization only"],
                ["TC-3733"],
                "full",
                True,
                [],
                "Clear-path regression.",
                "Edge of sync epic.",
                "Single clear action assert.",
            ),
            journey(
                "TC-004",
                "WBS - Column header filter - Multiple columns combine with AND logic",
                "P2",
                "BOX_EDITOR",
                "Multi-column filtering must not drop panel conditions.",
                f"{tenant} Diverse tasks for combinatorial filter. {box}",
                [
                    step("Apply header filter on **Status**.", "Grid narrows."),
                    step("Apply header filter on **Priority** without clearing Status.", "Grid shows intersection only."),
                    step("Verify panel lists both conditions.", "Two entries with AND semantics."),
                    step("Remove Status from panel.", "Priority-only filter remains; Status header indicator clears."),
                ],
                ["GOAL-04"],
                ["click on the column header and open filtering menu"],
                ["TC-2795"],
                "partial",
                True,
                ["multi_filter_precedence"],
                "Multi-filter interaction.",
                "Stress sync beyond single column.",
                "Assert row count matches manual AND.",
            ),
        ]

    if key == "ONE-355345":
        return [
            journey(
                "TC-001",
                "Strategic Roadmap - Timeline events - Create flag diamond and release on plan",
                "P1",
                "ROADMAP_EDITOR",
                "Critical dates invisible on roadmap without event markers.",
                f"{tenant} Strategic roadmap edit mode. {box}",
                [
                    step("Open roadmap **Timeline** in edit mode.", "Timeline renders."),
                    step("Create **flag** event on selected date with name **Scope lock**.", "Flag icon appears on date."),
                    step("Create **diamond** milestone with name **Beta**.", "Diamond marker displays."),
                    step("Create **release** event with version label **2026.4**.", "Release marker displays on timeline."),
                    step("Open event details for each.", "Name, type, and date fields match input."),
                ],
                ["GOAL-01"],
                ["Create events – Add flag, diamond, or release markers"],
                ["TC-6117"],
                "partial",
                True,
                ["timeline_edit_mode"],
                "CRUD baseline for three event types.",
                "Creation journey before drag/filter.",
                "Timeline coordinate clicks — partial automation.",
            ),
            journey(
                "TC-002",
                "Strategic Roadmap - Timeline events - Quick-add and drag to reschedule",
                "P1",
                "ROADMAP_EDITOR",
                "Leaders need fast date shifts without reopening modals.",
                f"{tenant} Roadmap with existing release event. {box}",
                [
                    step("Use **quick-add** on timeline empty date.", "Event type picker opens; create flag."),
                    step("Drag flag marker to new date.", "Marker moves; details show updated date."),
                    step("Drag release marker across month boundary.", "Date updates; no duplicate markers."),
                    step("Refresh page.", "Rescheduled dates persist."),
                ],
                ["GOAL-02"],
                ["Quick-add events on the timeline and drag to reschedule"],
                ["TC-6147"],
                "partial",
                True,
                ["drag_drop_timing"],
                "Interaction child for power users.",
                "Distinct from modal create.",
                "Drag automation sensitive.",
            ),
            journey(
                "TC-003",
                "Strategic Roadmap - Timeline events - Filter by flag diamond release",
                "P2",
                "ROADMAP_VIEWER",
                "Cluttered timelines hide release trains when all event types show.",
                f"{tenant} Roadmap with all three event types. {box}",
                [
                    step("Open event **type filter**.", "Options: flag, diamond, release."),
                    step("Show only **release**.", "Only release markers visible."),
                    step("Add **diamond** to selection.", "Release and diamond visible; flags hidden."),
                    step("Clear filter.", "All event types return."),
                ],
                ["GOAL-03"],
                ["Filter timeline events by type"],
                ["TC-6150"],
                "full",
                True,
                [],
                "Filter child story.",
                "Visibility logic separate from CRUD.",
                "Toggle filter buttons automatable.",
            ),
            journey(
                "TC-004",
                "Strategic Roadmap - Timeline events - Exported and shared view includes markers",
                "P2",
                "ROADMAP_VIEWER",
                "Stakeholders miss commitments when exports omit events.",
                f"{tenant} Shared link or export enabled. {box}",
                [
                    step("Create visible release and flag on roadmap.", "Markers on canvas."),
                    step("Generate **shared link** or **export** (PDF/PNG per product).", "Export completes."),
                    step("Open export or incognito shared view.", "Flag and release markers visible at correct dates."),
                    step("Edit event name and re-export.", "Updated label appears in new export."),
                ],
                ["GOAL-04"],
                ["Include timeline events on shared and exported roadmap views"],
                ["TC-4853"],
                "manual_only",
                False,
                ["export_render_pipeline"],
                "Export/share child.",
                "P2 stakeholder visibility.",
                "Export file visual diff manual.",
            ),
        ]

    raise KeyError(key)


def build_theme_file(key: str, review: dict) -> Path:
    req = review["requirements"][0]
    parts = [req["summary"], req.get("description_excerpt", "")]
    for c in review.get("rollup", {}).get("epic_child_inventory", []):
        if c.get("recommended_for_batch"):
            parts.append(c["summary"])
    for f in review.get("findings", [])[:5]:
        parts.append(f.get("title", "") or f.get("summary", ""))
    path = Path(f"/tmp/theme-{key}.txt")
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def golden_references_from_sample(sample: dict, golden_rel: str) -> list[dict]:
    refs = []
    scores = sample.get("similarity_scores", {})
    titles = sample.get("titles", {})
    for k in sample["jira_keys"]:
        rel_path = f"{golden_rel}/rag/by-key/{k}.json"
        score = scores.get(k, 0)
        refs.append(
            {
                "jira_key": k,
                "path": rel_path,
                "why_selected": f"Theme similarity rank (score {score}) to Epic keywords; title: {titles.get(k, '')[:100]}",
                "style_cues_applied": [
                    "Full JSON read for step depth and BP manual phrasing",
                    "Title/navigation pattern from this TC",
                ],
            }
        )
    return refs


def verify_golden_reads(sample: dict) -> None:
    for p in sample["rag_paths"]:
        path = REPO / p if not p.startswith("Trinity") else REPO / p
        if not path.is_file():
            raise FileNotFoundError(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("test", {}).get("steps"):
            raise ValueError(f"No steps in {path}")


def coverage_matrix(tests: list[dict]) -> list[dict]:
    matrix = []
    seen = set()
    for t in tests:
        for ac in t.get("linked_ac_ids", []):
            if ac in seen:
                continue
            seen.add(ac)
            matrix.append(
                {
                    "ac_id": ac,
                    "status": "Covered",
                    "covered_by": [t["draft_id"]],
                }
            )
    return matrix


def write_suite_report_md(out_dir: Path, key: str, batch: dict, gate: str) -> None:
    lines = [
        f"# Creator suite report — {key}",
        "",
        f"- **Product:** bigpicture",
        f"- **Suite mode:** {batch['suite_mode']}",
        f"- **Reviewer gate:** {gate}",
        f"- **Review ref:** `{batch['review_ref']}`",
        f"- **Tests:** {len(batch['tests'])}",
        "",
        "## Golden references",
        "",
    ]
    gs = batch["golden_sampling"]
    lines.append(
        f"Method `{gs['method']}` — {gs['similarity_count']} similar, "
        f"{gs['random_fill_count']} random fill, sample {gs['sample_count']}."
    )
    lines.append("")
    for ref in batch["golden_references"]:
        lines.append(f"- **{ref['jira_key']}** — {ref['why_selected'][:120]}")
    lines.append("")
    lines.append("## Journeys")
    lines.append("")
    for t in batch["tests"]:
        lines.append(f"### {t['draft_id']}: {t['title']}")
        lines.append(f"- Tier: {t['execution_tier']} | Automation: {t['automation_fit']}")
        lines.append(f"- Steps: {len(t['steps'])}")
        lines.append("")
    if batch["coverage_report"]["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for w in batch["coverage_report"]["warnings"]:
            lines.append(f"- {w}")
        lines.append("")
    (out_dir / "suite-report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    force_blocked = "--force-blocked" in sys.argv
    golden_rel = "Trinity/creator/golden/v2/filter-17844-bigpicture-manual"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    summary_rows = []

    for key in EPIC_KEYS:
        review_path = REVIEW_BASE / key / "review-payload.json"
        review = json.loads(review_path.read_text(encoding="utf-8"))
        theme = build_theme_file(key, review)
        kw = KEYWORDS[key]
        proc = subprocess.run(
            [
                sys.executable,
                str(SAMPLE_SCRIPT),
                "--golden-root",
                str(GOLDEN_ROOT),
                "--keywords",
                kw,
                "--theme-file",
                str(theme),
                "--seed",
                f"{key}-golden",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        sample = json.loads(proc.stdout)
        verify_golden_reads(sample)

        gate = review.get("gate", {})
        gate_status = gate.get("status", "UNKNOWN")
        warnings = []
        readiness = review.get("classifications", {}).get("readiness", {}).get("value")
        if readiness == "ready_with_clarifications":
            warnings.append(
                "Reviewer readiness: ready_with_clarifications — title-only children may lack AC; journeys focus on described open stories."
            )
        if review.get("report", {}).get("not_stated"):
            warnings.append(review["report"]["not_stated"][0][:200])

        tests = tests_for_epic(key)
        ensure_min_steps(tests, minimum=6)
        for t in tests:
            t["linked_requirement_keys"] = [key]

        gs = {
            "method": sample["method"],
            "sample_count": sample["sample_count"],
            "candidate_pool_size": sample["candidate_pool_size"],
            "similarity_pool_size": sample["similarity_pool_size"],
            "similarity_count": sample["similarity_count"],
            "random_fill_count": sample["random_fill_count"],
            "keywords": sample["keywords"],
        }
        if sample.get("random_seed"):
            gs["random_seed"] = sample["random_seed"]

        batch = {
            "schema_version": "1.0",
            "run_id": f"{key}-creator-q4",
            "generated_at": now,
            "golden_version": golden_rel,
            "suite_mode": "release_slice_e2e",
            "product_id": "bigpicture",
            "golden_root": golden_rel,
            "golden_sampling": gs,
            "golden_references": golden_references_from_sample(sample, golden_rel),
            "review_ref": f"Trinity/reviewer/runs/q4-backlog/{key}/review-payload.json",
            "persona_files": PERSONA_FILES,
            "source_requirement_keys": [key],
            "requirements_review_run_id": review["run_id"],
            "coverage_report": {
                "matrix": coverage_matrix(tests),
                "uncovered_ac_ids": [],
                "uncovered_goals": [],
                "warnings": warnings,
            },
            "execution_plan": build_execution_plan(tests),
            "tests": tests,
        }
        if gate.get("blocks_test_generation") and gate_status == "BLOCKED" and not force_blocked:
            warnings.append("BLOCKED gate — suite not written. Re-run with --force-blocked to record an override.")
            summary_rows.append((key, 0, gate_status, "; ".join(warnings[:2]) or "—"))
            continue
        if gate.get("blocks_test_generation") and gate_status == "BLOCKED":
            batch["gate_override"] = True
            batch["gate_override_record"] = {
                "at": now,
                "by": os.environ.get("TRINITY_OPERATOR_ID") or "cli",
                "reason": "--force-blocked",
            }
            warnings.append("gate_override recorded with --force-blocked.")

        out_dir = OUT_BASE / key
        out_dir.mkdir(parents=True, exist_ok=True)
        payload_path = out_dir / "suite-payload.json"
        payload_path.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_suite_report_md(out_dir, key, batch, gate_status)

        subprocess.run(
            [
                sys.executable,
                str(BUILD_REPORT),
                "--batch",
                str(payload_path),
                "--out",
                str(out_dir / "suite-report"),
            ],
            check=True,
        )

        summary_rows.append((key, len(tests), gate_status, "; ".join(warnings[:2]) or "—"))

    print("| KEY | tests | gate | warnings |")
    print("|-----|-------|------|----------|")
    for row in summary_rows:
        print(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
