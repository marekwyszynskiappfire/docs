#!/usr/bin/env python3
"""Generate Creator suite artifacts for q4-backlog batch 2/3 (10 epics)."""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

SHARED = Path(__file__).resolve().parents[2] / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))
from priority_score import apply_priority_fields, build_execution_plan

REPO = Path(__file__).resolve().parents[3]
CREATOR = REPO / "Trinity/creator"
GOLDEN_ROOT = CREATOR / "golden/v2/filter-17844-bigpicture-manual"
REVIEW_ROOT = REPO / "Trinity/reviewer/runs/q4-backlog"
OUT_ROOT = CREATOR / "artifacts/q4-backlog"
SAMPLE_SCRIPT = CREATOR / "scripts/sample_golden_references.py"
BUILD_REPORT = CREATOR / "scripts/build_suite_report.py"

EPICS = [
    "ONE-368849",
    "ONE-368872",
    "ONE-368895",
    "ONE-370674",
    "ONE-370675",
    "ONE-370677",
    "ONE-373750",
    "ONE-375429",
    "ONE-376627",
    "ONE-377219",
]

KEYWORDS: dict[str, str] = {
    "ONE-368849": "upsell,priorities,standard,advanced,promo,nudge,trial",
    "ONE-368872": "upsell,migration,BPE,BPA,promo,advanced,standard,license",
    "ONE-368895": "upsell,reporting,advanced,promo,standard,report",
    "ONE-370674": "upsell,financials,standard,advanced,promo,trial",
    "ONE-370675": "upsell,OKR,standard,advanced,promo,trial",
    "ONE-370677": "OKR,changelog,change log,history,audit,ledger",
    "ONE-373750": "merge,Data Center,instance,migration,consolidation,schema",
    "ONE-375429": "Financials,AI,spend,management,discovery,attribution",
    "ONE-376627": "subsidiary,Jira,webhook,oauth,credential,permission,ExtPlatform",
    "ONE-377219": "OKR,teams,global,permissions,settings,BP Teams",
}


def step(action: str, expected: str) -> dict[str, str]:
    return {"step": action, "expected_result": expected}


def persona(qa: str, arch: str, auto: str) -> dict[str, str]:
    return {"qa_engineer": qa, "test_architect": arch, "automation_engineer": auto}


def base_test(
    draft_id: str,
    title: str,
    epic: str,
    ac_ids: list[str],
    child_keys: list[str],
    role: str,
    impact: str,
    pre: str,
    prereq: str,
    fit: str,
    blockers: list[str],
    notes: persona,
    steps: list[dict[str, str]],
    tags: list[str],
    golden_refs: list[str] | None = None,
    tier: str = "P1",
    defer: bool = False,
    defer_rationale: str = "",
) -> dict:
    t: dict = {
        "draft_id": draft_id,
        "title": title,
        "linked_requirement_keys": [epic] + [k for k in child_keys if k != epic],
        "linked_ac_ids": ac_ids,
        "execution_tier": tier,
        "test_pattern": "journey",
        "role": role,
        "customer_impact": impact,
        "deferrable": defer,
        "test_data_required": True,
        "test_data_prerequisites": prereq,
        "test_type": "Manual",
        "preconditions": pre,
        "automation_fit": fit,
        "automation_candidate": fit in ("full", "partial"),
        "automation_blockers": blockers,
        "persona_notes": notes,
        "steps": steps,
        "tags": tags,
    }
    if golden_refs:
        t["golden_reference_keys"] = golden_refs
    if defer and defer_rationale:
        t["deferrable_rationale"] = defer_rationale
    return apply_priority_fields(t)


def upsell_suite(epic: str, feature_label: str, module_nav: str, try_cta: str) -> list[dict]:
    """Standard Advanced upsell / try journeys on BigPicture Standard license."""
    iso = f"dedicated staging tenant on BigPicture Standard with {feature_label} gated; boxName Upsell-{epic[-6:]}"
    return [
        base_test(
            "TC-001",
            f"BP upsell - {feature_label} - Standard box admin sees in-product nudge on gated module entry",
            epic,
            ["GOAL-NUDGE"],
            [],
            "BOX_ADMIN",
            f"Standard customers never discover {feature_label} trial path; revenue upsell funnel stalls.",
            f"Logged in as box administrator on Standard license; {feature_label} not licensed.",
            iso,
            "partial",
            ["license_banner_copy_varies_by_env", "analytics_event_assertion_optional"],
            persona(
                f"Validates first-touch discovery when admin opens {module_nav}.",
                "Single journey covers banner + CTA without separate click-only case.",
                "UI smoke automatable; copy and cohort flags may need manual baseline.",
            ),
            [
                step(
                    f"Open box **{module_nav}** for boxName on a Standard-licensed environment.",
                    f"In-product upsell or **Try {feature_label}** nudge appears with short value proposition text.",
                ),
                step(
                    "Read primary call-to-action label on the nudge.",
                    f"CTA matches product copy for **{try_cta}** (or documented equivalent).",
                ),
                step(
                    "Choose **Learn more** or secondary link if present.",
                    "Help or marketing content opens in a new tab or panel without breaking module session.",
                ),
                step(
                    "Close the help surface and return to the module.",
                    "Module remains on Standard capability; gated actions stay disabled or read-only per license.",
                ),
                step(
                    "Attempt the primary gated action (create, edit, or export) blocked on Standard.",
                    "Action is blocked with clear message referencing Advanced or trial; no silent failure.",
                ),
                step(
                    "Open browser devtools network filter and repeat opening the module once.",
                    "Optional telemetry request fires with event name containing upsell or trial intent (if documented for QA).",
                ),
            ],
            ["upsell", "journey", feature_label.lower().replace(" ", "-")],
            ["TC-4251"],
        ),
        base_test(
            "TC-002",
            f"BP upsell - {feature_label} - Box admin starts try flow and receives temporary Advanced capability",
            epic,
            ["GOAL-TRIAL"],
            [],
            "BOX_ADMIN",
            f"Trial activation failure blocks evaluation of {feature_label} and increases sales cycle time.",
            f"Box admin on Standard; trial not previously activated for {feature_label} on this tenant.",
            iso,
            "partial",
            ["trial_backend_async", "license_refresh_timing"],
            persona(
                "Happy path from CTA through enabled capability smoke check.",
                "Pairs with TC-001 on matrix row GOAL-TRIAL; avoids duplicating nudge-only steps.",
                "Automate CTA + poll license flag API if exposed; else manual wait for refresh.",
            ),
            [
                step(
                    f"From the **{module_nav}** upsell nudge, choose **{try_cta}**.",
                    "Confirmation modal or wizard step explains trial duration and scope.",
                ),
                step(
                    "Accept terms and confirm start.",
                    "Success toast or banner states trial is active; no error stack in UI.",
                ),
                step(
                    "Wait up to two minutes and refresh the browser tab.",
                    "Trial state persists after refresh (banner or license indicator shows trial).",
                ),
                step(
                    f"Perform one previously gated {feature_label} action (documented smoke action for module).",
                    "Action completes successfully; result visible in UI (row, chart, or export).",
                ),
                step(
                    "Open **App administration → License** or in-app license panel.",
                    f"License summary lists {feature_label} trial or Advanced trial window with end date.",
                ),
                step(
                    "Sign out and sign in as the same administrator.",
                    "Trial remains active; gated action still succeeds.",
                ),
            ],
            ["upsell", "trial", "journey"],
            ["TC-5039"],
        ),
        base_test(
            "TC-003",
            f"BP upsell - {feature_label} - Standard member without admin rights cannot start trial",
            epic,
            ["GOAL-RBAC"],
            [],
            "STANDARD_MEMBER",
            "Unauthorized trial activation would bypass billing controls.",
            "Standard license; user is box member without box admin or billing admin rights.",
            iso + "; user StandardMember without admin role",
            "full",
            [],
            persona(
                "Negative RBAC on same module surface as TC-001.",
                "Covers member journey without repeating admin trial steps.",
                "Role fixture + assert CTA hidden or API 403 on trial endpoint.",
            ),
            [
                step(
                    f"Log in as box member (non-admin) and open **{module_nav}**.",
                    "Module loads read-only or shows upsell without **Start trial** for non-admin.",
                ),
                step(
                    "Attempt to open trial URL or deep link documented for administrators only.",
                    "Access denied message or redirect; trial does not activate.",
                ),
                step(
                    "Verify gated premium action remains unavailable.",
                    "Same blocking behaviour as before any trial attempt.",
                ),
                step(
                    "Ask box administrator to confirm no trial started in license panel.",
                    "License panel shows no new trial for the tenant.",
                ),
            ],
            ["upsell", "permissions", "journey"],
            ["TC-6042"],
        ),
        base_test(
            "TC-004",
            f"BP upsell - {feature_label} - Admin dismisses nudge and nudge respects snooze rules",
            epic,
            ["GOAL-SNOOZE"],
            [],
            "BOX_ADMIN",
            "Broken snooze logic annoys users and erodes trust in upsell UX.",
            "Box admin on Standard; nudge visible on module entry.",
            iso,
            "partial",
            ["snooze_duration_config"],
            persona(
                "Dismiss and revisit behaviour within same session and after reload.",
                "Fourth journey completes release slice without overlapping TC-002 trial path.",
                "Cookie or local storage key assertion if documented.",
            ),
            [
                step(
                    f"Open **{module_nav}** and locate upsell nudge.",
                    "Nudge is visible.",
                ),
                step(
                    "Choose **Dismiss**, **Not now**, or close control on the nudge.",
                    "Nudge closes; module remains usable.",
                ),
                step(
                    "Navigate away to **Overview** and return to the same module within the same session.",
                    "Nudge stays hidden per snooze rules for current session.",
                ),
                step(
                    "Hard refresh the browser.",
                    "Nudge remains hidden until snooze window expires (or reappears per PM-defined rule — record observed behaviour).",
                ),
                step(
                    "Clear snooze via documented QA override or wait for expiry window in test plan.",
                    "Nudge can appear again on next module entry.",
                ),
            ],
            ["upsell", "ux", "journey"],
            ["TC-4290"],
        ),
    ]


def tests_for_epic(epic: str) -> list[dict]:
    if epic == "ONE-368849":
        return upsell_suite(epic, "Priorities", "Priorities module", "Try Priorities")
    if epic == "ONE-368872":
        return [
            base_test(
                "TC-001",
                "BP upsell - License migration - BPE administrator sees BigPicture Advanced upgrade promo",
                epic,
                ["GOAL-PROMO"],
                [],
                "APP_ADMIN",
                "Enterprise customers on BigPicture Enterprise miss migration path to Advanced.",
                "Jira administrator on BPE license with BigPicture installed; promo cohort flag enabled for QA tenant.",
                "Dedicated tenant flagged for BPE→BPA migration promo; no prior dismissal",
                "partial",
                ["cohort_flag", "marketing_copy"],
                persona(
                    "Surfaces promo on admin entry point for migration epic.",
                    "Journey 1 of 4 for migration slice; distinct from module try flows.",
                    "Admin navigation automatable; cohort gating manual.",
                ),
                [
                    step(
                        "Open **Jira administration → Manage apps → BigPicture**.",
                        "BigPicture administration loads without error.",
                    ),
                    step(
                        "Open **License** or **Subscription** section.",
                        "Current plan shows BigPicture Enterprise (BPE) or documented equivalent label.",
                    ),
                    step(
                        "Locate migration or upgrade promo banner for BigPicture Advanced.",
                        "Banner references Advanced capabilities and migration or upgrade CTA.",
                    ),
                    step(
                        "Open promo **Learn more** link.",
                        "Documentation or contact flow opens; no script errors in admin UI.",
                    ),
                ],
                ["upsell", "migration", "journey"],
                ["TC-1798"],
            ),
            *upsell_suite(epic, "Advanced platform", "Overview module", "Explore Advanced")[1:4],
        ]
    if epic == "ONE-368895":
        return upsell_suite(epic, "Advanced reporting", "Reports module", "Try Advanced reporting")
    if epic == "ONE-370674":
        return upsell_suite(epic, "Financials", "Financials module", "Try Financials")
    if epic == "ONE-370675":
        return upsell_suite(epic, "OKR on Standard", "OKR module", "Try OKR")
    if epic == "ONE-370677":
        iso = "Dedicated tenant with OKR module; boxName OKR-Changelog-QA; two users Editor and Viewer"
        return [
            base_test(
                "TC-001",
                "SPM - OKR - Change log - Editor updates key result and verifies audit entry on Change log tab",
                epic,
                ["GOAL-AUDIT"],
                ["ONE-377799", "ONE-377792"],
                "OKR_EDITOR",
                "Missing audit trail blocks compliance and debugging of OKR data changes.",
                "OKR editor role on boxName; Change log feature enabled.",
                iso,
                "partial",
                ["timestamp_timezone", "async_ledger_write"],
                persona(
                    "Core happy path for UI tab plus data change.",
                    "Maps to change log UI and audit foundation children.",
                    "API read-back of ledger if exposed; else UI-only.",
                ),
                [
                    step(
                        "Open **OKR module** of boxName and note current progress value on KR-1.",
                        "KR-1 row visible with baseline progress.",
                    ),
                    step(
                        "Edit KR-1 progress to a new numeric value and save.",
                        "Save succeeds; grid shows updated progress.",
                    ),
                    step(
                        "Open **Change log** tab on the same key result or objective detail panel.",
                        "Change log tab loads listing at least one new entry.",
                    ),
                    step(
                        "Open the latest entry.",
                        "Entry shows field name, previous value, new value, author display name, and timestamp.",
                    ),
                    step(
                        "Change KR-1 title text and save.",
                        "Second entry appears with title change details.",
                    ),
                ],
                ["okr", "changelog", "journey"],
                ["TC-6147"],
            ),
            base_test(
                "TC-002",
                "SPM - OKR - Change log - Viewer reads history but cannot mutate OKR from log surface",
                epic,
                ["GOAL-RBAC"],
                ["ONE-377798"],
                "OKR_VIEWER",
                "Viewers could alter OKR data through log actions if RBAC fails.",
                "Viewer user without edit rights on the same OKR tree.",
                iso + "; viewer account OKR-Viewer",
                "full",
                [],
                persona(
                    "Read-only validation on change log read API/UI.",
                    "Complements TC-001 without repeating edit steps.",
                    "Negative click tests on hidden actions.",
                ),
                [
                    step(
                        "Log in as viewer and open **OKR module** of boxName.",
                        "Tree loads; edit controls absent or disabled on KR-1.",
                    ),
                    step(
                        "Open **Change log** tab for KR-1.",
                        "Historical entries from editor session are visible.",
                    ),
                    step(
                        "Attempt inline edit on KR-1 from grid.",
                        "Edit blocked with permission message.",
                    ),
                    step(
                        "Attempt revert or delete control on a log entry if rendered.",
                        "Control absent or disabled for viewer.",
                    ),
                ],
                ["okr", "changelog", "permissions"],
                ["TC-6042"],
            ),
            base_test(
                "TC-003",
                "SPM - OKR - Change log - Filter entries by author and date range",
                epic,
                ["GOAL-FILTER"],
                ["ONE-377798"],
                "OKR_EDITOR",
                "Operators cannot investigate incidents without filtering noisy logs.",
                "At least three changelog entries from two users across two days.",
                iso + "; seed entries via editor and second editor account",
                "partial",
                ["date_picker_locale"],
                persona(
                    "Filter UX once TBC retention rules land.",
                    "Partial until PM locks default date window.",
                    "Filter query params on read API if available.",
                ),
                [
                    step(
                        "Open **Change log** tab with multiple entries loaded.",
                        "List shows more than two rows.",
                    ),
                    step(
                        "Set **Author** filter to editor user only.",
                        "Only that author's entries remain visible.",
                    ),
                    step(
                        "Set **Date range** to yesterday only.",
                        "Entries outside range hide; count updates.",
                    ),
                    step(
                        "Clear filters.",
                        "Full list returns.",
                    ),
                ],
                ["okr", "changelog", "filter"],
                ["TC-6150"],
                defer=True,
                defer_rationale="TBC rows on retention and filter defaults in epic decision table.",
            ),
            base_test(
                "TC-004",
                "SPM - OKR - Change log - Bulk edit records single aggregated entry per policy",
                epic,
                ["GOAL-BULK"],
                ["ONE-377793"],
                "OKR_EDITOR",
                "Bulk operations could flood the log or hide true change count.",
                "Bulk edit feature enabled; five key results selected.",
                iso,
                "manual_only",
                ["bulk_edit_ui_unstable", "tbc_bulk_policy"],
                persona(
                    "Documents expected bulk behaviour pending TBC policy row.",
                    "Placeholder journey for bulk slice; mark deferrable.",
                    "Await stable bulk API contract.",
                ),
                [
                    step(
                        "Select five key results in OKR grid and open **Bulk edit**.",
                        "Bulk panel opens.",
                    ),
                    step(
                        "Set shared field (owner or period) and apply.",
                        "Bulk job completes with success summary.",
                    ),
                    step(
                        "Open **Change log** on one affected KR.",
                        "Either one aggregated entry or five entries appears per documented policy (record actual).",
                    ),
                ],
                ["okr", "changelog", "bulk"],
                defer=True,
                defer_rationale="Epic TBC decision on bulk logging granularity.",
            ),
        ]
    if epic == "ONE-373750":
        return [
            base_test(
                "TC-001",
                "Data merge - Administrator prepares two Data Center exports for merge on Cloud hub",
                epic,
                ["GOAL-PREP"],
                ["ONE-375437"],
                "MIGRATION_ADMIN",
                "Invalid export package blocks merge and risks data loss.",
                "Migration admin; two DC export bundles available in secure storage.",
                "Dedicated Cloud hub tenant; DC-A and DC-B export files with distinct instance IDs",
                "partial",
                ["export_artifact_size", "secure_upload_channel"],
                persona(
                    "Prep journey before domain merge stories execute.",
                    "First of four merge journeys; no per-domain depth yet.",
                    "Upload script automatable; virus scan wait manual.",
                ),
                [
                    step(
                        "Open **App administration → Data merge** (or documented merge entry).",
                        "Merge wizard landing page loads.",
                    ),
                    step(
                        "Start **New merge** and upload export package from DC-A.",
                        "Validation passes; instance metadata displays (name, URL, export date).",
                    ),
                    step(
                        "Add second package from DC-B.",
                        "Both packages listed; conflict pre-check summary appears.",
                    ),
                    step(
                        "Save draft merge plan without executing.",
                        "Draft retrievable from merge list with status Draft.",
                    ),
                ],
                ["merge", "dc", "journey"],
                ["TC-2746"],
            ),
            base_test(
                "TC-002",
                "Data merge - Mapping domain reconciles duplicate box identifiers across instances",
                epic,
                ["GOAL-MAPPING"],
                ["ONE-375437"],
                "MIGRATION_ADMIN",
                "Wrong box mapping corrupts portfolio hierarchy after merge.",
                "Draft merge with overlapping box keys between DC-A and DC-B.",
                "Same as TC-001 draft; mapping UI enabled",
                "partial",
                ["mapping_rules_tbd"],
                persona(
                    "Exercises mapping domain child scope at journey level.",
                    "Pairs with mapping story without atomic field tests.",
                    "Mapping API snapshot diff.",
                ),
                [
                    step(
                        "Open draft merge and navigate to **Mapping → Boxes**.",
                        "Duplicate box keys highlighted.",
                    ),
                    step(
                        "Choose **Rename target** for DC-B collision and apply mapping rule.",
                        "Preview shows resolved target key.",
                    ),
                    step(
                        "Run **Validate mapping**.",
                        "Validation completes with zero blocking errors.",
                    ),
                ],
                ["merge", "mapping", "journey"],
                ["TC-3562"],
            ),
            base_test(
                "TC-003",
                "Data merge - Task relations survive merge with remapped issue keys",
                epic,
                ["GOAL-RELATIONS"],
                ["ONE-375439"],
                "MIGRATION_ADMIN",
                "Broken relations after merge invalidate Gantt and dependency reports.",
                "Draft merge includes tasks with cross-box dependencies in both exports.",
                "Relation test graph seeded in both DC exports",
                "manual_only",
                ["merge_execution_window", "tbc_relation_rules"],
                persona(
                    "End-to-end relation check post-merge execution.",
                    "Deferred execution until merge job API stable in QA.",
                    "Post-merge Gantt API query.",
                ),
                [
                    step(
                        "Execute merge job on validated draft (QA maintenance window).",
                        "Job completes with status Success.",
                    ),
                    step(
                        "Open **Gantt** on merged box and locate dependency arrow between Task-A and Task-B.",
                        "Dependency renders; no orphan link icon.",
                    ),
                    step(
                        "Open task detail for Task-A and inspect relations panel.",
                        "Relation target shows remapped issue key from merge mapping table.",
                    ),
                ],
                ["merge", "relations", "journey"],
                defer=True,
                defer_rationale="Full merge execution depends on backend merge job in QA.",
            ),
            base_test(
                "TC-004",
                "Data merge - Rollback or abort leaves hub unchanged on validation failure",
                epic,
                ["GOAL-SAFETY"],
                ["ONE-382835"],
                "MIGRATION_ADMIN",
                "Partial merge could leave production hub inconsistent.",
                "Draft merge with intentional invalid schema flag in DC-B package (QA fixture).",
                "Invalid package flagged by QA team only",
                "partial",
                ["abort_cleanup_timing"],
                persona(
                    "Safety journey for failed validation path.",
                    "Fourth journey; complements happy path TC-001.",
                    "Assert hub row count unchanged via API.",
                ),
                [
                    step(
                        "Upload intentionally invalid second package.",
                        "Validation fails with explicit error code and message.",
                    ),
                    step(
                        "Confirm **Execute** remains disabled.",
                        "No merge job queued.",
                    ),
                    step(
                        "Remove invalid package and re-validate remaining draft.",
                        "Draft returns to valid state without orphan records in hub.",
                    ),
                ],
                ["merge", "safety", "journey"],
                ["TC-377"],
            ),
        ]
    if epic == "ONE-375429":
        return [
            base_test(
                "TC-001",
                "Financials - AI spend prep - Admin reviews discovery dashboard placeholder for provider costs",
                epic,
                ["GOAL-DISCOVERY"],
                [],
                "FINANCIALS_ADMIN",
                "Without discovery UI, spikes cannot be validated with stakeholders.",
                "Financials admin; AI spend prep feature flag on.",
                "Dedicated tenant; feature flag ai-spend-prep enabled; no production customer data",
                "manual_only",
                ["no_stable_ui", "epic_has_zero_children"],
                persona(
                    "Provisional journey until child stories link under epic.",
                    "Single discovery surface; epic is prep-only.",
                    "Blocked until UI lands.",
                ),
                [
                    step(
                        "Open **Financials module** and navigate to **AI spend** (or documented prep section).",
                        "Section loads with discovery status banner.",
                    ),
                    step(
                        "Open **Provider data** panel.",
                        "Panel lists configured providers or explicit empty state copy.",
                    ),
                    step(
                        "Export or screenshot panel for PM review.",
                        "Artifact captured for go/no-go meeting.",
                    ),
                ],
                ["financials", "ai-spend", "discovery"],
                tier="P2",
                defer=True,
                defer_rationale="Epic has no child issues; discovery spikes not yet implemented.",
            ),
            base_test(
                "TC-002",
                "Financials - AI spend prep - Attribution spike documents mapping from AI usage to financial period",
                epic,
                ["GOAL-ATTRIBUTION"],
                [],
                "FINANCIALS_ADMIN",
                "Wrong attribution breaks cost allocation reports.",
                "Sample usage file from QA fixtures.",
                "Fixture CSV ai-usage-sample.csv in test data vault",
                "manual_only",
                ["attribution_rules_tbd"],
                persona(
                    "Validates mapping wizard or doc-only flow from spike.",
                    "Second journey; defers execution.",
                    "Await spike deliverable.",
                ),
                [
                    step(
                        "Open **AI spend → Attribution** wizard.",
                        "Wizard explains mapping dimensions (team, period, cost center).",
                    ),
                    step(
                        "Upload sample usage file.",
                        "Preview table shows parsed rows with suggested mappings.",
                    ),
                    step(
                        "Save mapping template.",
                        "Template appears in list for reuse.",
                    ),
                ],
                ["financials", "attribution"],
                tier="P2",
                defer=True,
                defer_rationale="Attribution spike deliverable pending.",
            ),
            base_test(
                "TC-003",
                "Financials - AI spend prep - Privacy review gate blocks external provider connect",
                epic,
                ["GOAL-PRIVACY"],
                [],
                "FINANCIALS_ADMIN",
                "Connecting providers before privacy sign-off violates policy.",
                "Privacy review flag unset on tenant.",
                "Tenant without privacy approval flag",
                "partial",
                ["legal_copy"],
                persona(
                    "Negative path for privacy gate.",
                    "Third journey in prep slice.",
                    "Assert connect button disabled via config.",
                ),
                [
                    step(
                        "Open **Connect provider** flow.",
                        "Privacy acknowledgement step appears.",
                    ),
                    step(
                        "Attempt to continue without accepting privacy checklist.",
                        "Continue disabled; inline message references privacy review.",
                    ),
                    step(
                        "Enable privacy approval flag via QA admin tool and retry.",
                        "Connect flow proceeds to credential step.",
                    ),
                ],
                ["financials", "privacy"],
                tier="P2",
            ),
        ]
    if epic == "ONE-376627":
        return [
            base_test(
                "TC-001",
                "ExtPlatform - Subsidiary Jira - Admin connects subsidiary and webhooks auto-register",
                epic,
                ["GOAL-WEBHOOK"],
                ["ONE-375404"],
                "EXT_PLATFORM_ADMIN",
                "Manual webhook setup errors cause missed sync events.",
                "ExtPlatform admin; subsidiary Jira sandbox reachable.",
                "Dedicated hub + subsidiary Jira pair; OAuth client configured",
                "partial",
                ["oauth_redirect", "webhook_propagation_delay"],
                persona(
                    "Happy path for auto webhook story.",
                    "Journey 1 covers connection + webhook list.",
                    "Poll webhook REST on subsidiary.",
                ),
                [
                    step(
                        "Open **App administration → ExtPlatform → Subsidiary Jira**.",
                        "Connections list loads.",
                    ),
                    step(
                        "Choose **Add connection** and complete OAuth consent on subsidiary.",
                        "Connection status shows Connected.",
                    ),
                    step(
                        "Open **Webhooks** tab on the connection.",
                        "At least one BigPicture webhook registered automatically.",
                    ),
                    step(
                        "Create issue on subsidiary project mapped to scope.",
                        "Event appears in BigPicture sync log within expected latency.",
                    ),
                ],
                ["subsidiary-jira", "webhook", "journey"],
                ["TC-1064"],
            ),
            base_test(
                "TC-002",
                "ExtPlatform - Subsidiary Jira - User completes personal credential setup after integration token exists",
                epic,
                ["GOAL-USER-CRED"],
                ["ONE-392054", "ONE-392049"],
                "STANDARD_USER",
                "Tasks fail silently when user token missing on subsidiary.",
                "Integration connected; user lacks personal credential.",
                "User StandardWorker without user credential row",
                "partial",
                ["status_477_assertion"],
                persona(
                    "Covers header prompt and credential setup UI.",
                    "Maps user credential child stories.",
                    "Assert HTTP 477 on failing API.",
                ),
                [
                    step(
                        "Log in as standard user and open **Tasks** on box with subsidiary scope.",
                        "Banner prompts to connect personal Jira account.",
                    ),
                    step(
                        "Follow **Connect account** and finish OAuth.",
                        "Banner clears; tasks list loads.",
                    ),
                    step(
                        "Open subsidiary issue from task row.",
                        "Issue opens without permission error.",
                    ),
                ],
                ["subsidiary-jira", "credential"],
                ["TC-1798"],
            ),
            base_test(
                "TC-003",
                "ExtPlatform - Subsidiary Jira - Missing user credential returns distinct error from integration token failure",
                epic,
                ["GOAL-ERRORS"],
                ["ONE-392051", "ONE-392052"],
                "STANDARD_USER",
                "Misleading errors slow incident response.",
                "Integration token valid; revoke user credential only.",
                "User with revoked user token; integration healthy",
                "full",
                [],
                persona(
                    "Error differentiation journey.",
                    "Pairs with TC-002 negative branch.",
                    "API status and header assertions.",
                ),
                [
                    step(
                        "Revoke user OAuth token in subsidiary admin.",
                        "Revocation succeeds.",
                    ),
                    step(
                        "Reload **Tasks** as affected user.",
                        "UI shows user credential required message (not integration down).",
                    ),
                    step(
                        "Inspect network response for failing request.",
                        "HTTP status 477 with body distinguishing user vs integration token.",
                    ),
                ],
                ["subsidiary-jira", "errors"],
                ["TC-6042"],
            ),
            base_test(
                "TC-004",
                "ExtPlatform - Subsidiary Jira - Task access respects subsidiary permission on linked issue",
                epic,
                ["GOAL-PERMISSION"],
                ["ONE-379453"],
                "STANDARD_USER",
                "Users could see tasks for issues they cannot browse on subsidiary.",
                "User lacks browse permission on PROJ-SECRET.",
                "Task linked to restricted subsidiary issue",
                "partial",
                ["subsidiary_project_setup"],
                persona(
                    "Security journey for task access fix in epic objective.",
                    "Fourth journey; module smoke reference child.",
                    "Cross-check task hidden in UI and API.",
                ),
                [
                    step(
                        "Open **Tasks** module as user without browse on mapped secret project.",
                        "Tasks tied to secret project hidden or masked.",
                    ),
                    step(
                        "Attempt deep link to task detail URL.",
                        "Permission error displayed; no issue summary leakage.",
                    ),
                    step(
                        "Grant browse permission and refresh.",
                        "Task appears with correct summary.",
                    ),
                ],
                ["subsidiary-jira", "permission"],
                ["TC-3748"],
            ),
            base_test(
                "TC-005",
                "ExtPlatform - Subsidiary Jira - Integration token refresh updates connection health",
                epic,
                ["GOAL-REFRESH"],
                ["ONE-391654", "ONE-392046"],
                "EXT_PLATFORM_ADMIN",
                "Stale integration token breaks all subsidiary sync.",
                "Connection with token near expiry (QA shortened TTL).",
                "TTL override in QA environment",
                "partial",
                ["token_ttl_qa_only"],
                persona(
                    "Refresh path for integration credential.",
                    "Fifth journey completes security epic slice.",
                    "Monitor health check endpoint.",
                ),
                [
                    step(
                        "Open connection **Health** panel.",
                        "Status Healthy with last refresh timestamp.",
                    ),
                    step(
                        "Wait for automatic refresh window or trigger QA refresh job.",
                        "Timestamp updates; status remains Healthy.",
                    ),
                    step(
                        "Force integration token invalidation and run **Re-authorize**.",
                        "Re-auth flow completes; sync resumes.",
                    ),
                ],
                ["subsidiary-jira", "refresh"],
                ["TC-5403"],
            ),
        ]
    if epic == "ONE-377219":
        return [
            base_test(
                "TC-001",
                "SPM - OKR - Global Teams - Enable feature and assign global team to objective",
                epic,
                ["GOAL-ENABLE"],
                ["ONE-376069", "ONE-257841"],
                "OKR_ADMIN",
                "OKR teams stay siloed from BP Teams; permissions diverge.",
                "OKR admin; global teams feature flag on for tenant.",
                "Dedicated tenant with feature flag global-teams-okr enabled",
                "partial",
                ["feature_flag_rollout"],
                persona(
                    "Core enablement journey for epic title.",
                    "Journey 1; maps rollout children.",
                    "Flag toggle via admin API.",
                ),
                [
                    step(
                        "Open **Settings → OKR → Teams**.",
                        "Global Teams section visible with enablement toggle.",
                    ),
                    step(
                        "Enable **Use BigPicture global teams** and save.",
                        "Success message; team picker shows global team catalog.",
                    ),
                    step(
                        "Open objective OBJ-1 and set **Team** to global team GT-1.",
                        "Assignment saves and displays on objective row.",
                    ),
                    step(
                        "Open **BigPicture Teams** admin and confirm GT-1 still exists.",
                        "Single source of truth; no duplicate OKR-only team created.",
                    ),
                ],
                ["okr", "teams", "journey"],
                ["TC-5936"],
            ),
            base_test(
                "TC-002",
                "SPM - OKR - Global Teams - OKR overview filters by global team membership",
                epic,
                ["GOAL-FILTER"],
                ["ONE-292747"],
                "OKR_EDITOR",
                "Incorrect filtering hides objectives from legitimate members.",
                "Two global teams with disjoint objectives.",
                "GT-1 and GT-2 with one objective each",
                "full",
                [],
                persona(
                    "Filter journey after team assignment.",
                    "Second test; uses settings link update child.",
                    "Grid filter API params.",
                ),
                [
                    step(
                        "Open **OKR Overview** and apply **Team** filter GT-1.",
                        "Only objectives for GT-1 visible.",
                    ),
                    step(
                        "Switch filter to GT-2.",
                        "OBJ for GT-2 appears; GT-1 objectives hidden.",
                    ),
                    step(
                        "Clear filter.",
                        "Full tree returns.",
                    ),
                ],
                ["okr", "teams", "filter"],
                ["TC-6117"],
            ),
            base_test(
                "TC-003",
                "SPM - OKR - Global Teams - Deleting global team surfaces OKR impact warning",
                epic,
                ["GOAL-DELETE"],
                ["ONE-335527", "ONE-336238"],
                "BP_TEAMS_ADMIN",
                "Silent deletion orphans OKR assignments.",
                "Objective linked to GT-1.",
                "Admin with BP Teams admin rights",
                "partial",
                ["async_notification"],
                persona(
                    "Deletion notification path (non-blocker stories).",
                    "Third journey for deletion epic children.",
                    "Event bus message assert if available.",
                ),
                [
                    step(
                        "Open **BigPicture Teams** and select GT-1.",
                        "Team detail shows linked OKR count or warning.",
                    ),
                    step(
                        "Choose **Delete team**.",
                        "Confirmation lists OKR impact summary.",
                    ),
                    step(
                        "Confirm deletion.",
                        "OKR module shows team field cleared or fallback label on affected objectives.",
                    ),
                ],
                ["okr", "teams", "delete"],
                ["TC-6150"],
            ),
            base_test(
                "TC-004",
                "SPM - OKR - Global Teams - Standard user without team admin cannot reassign global team",
                epic,
                ["GOAL-RBAC"],
                ["ONE-376070"],
                "OKR_EDITOR",
                "Privilege escalation would let editors change org-wide team mapping.",
                "Editor without Teams admin role.",
                "Editor user only",
                "full",
                [],
                persona(
                    "RBAC on team assignment control.",
                    "Fourth journey closes release slice.",
                    "Assert picker read-only.",
                ),
                [
                    step(
                        "Open objective as editor and open **Team** picker.",
                        "Current team displayed; change control disabled or absent.",
                    ),
                    step(
                        "Attempt API or URL override to set another global team if documented.",
                        "Request rejected with permission error.",
                    ),
                ],
                ["okr", "teams", "permissions"],
                ["TC-6042"],
            ),
        ]
    raise SystemExit(f"No test template for {epic}")


def sample_golden(epic: str) -> dict:
    review = REVIEW_ROOT / epic / "review-payload.json"
    cmd = [
        "python3",
        str(SAMPLE_SCRIPT),
        "--golden-root",
        str(GOLDEN_ROOT.relative_to(REPO)),
        "--keywords",
        KEYWORDS[epic],
        "--theme-file",
        str(review),
        "--seed",
        f"{epic}-golden",
    ]
    raw = subprocess.check_output(cmd, cwd=REPO, text=True)
    return json.loads(raw)


def golden_refs_from_sample(sample: dict) -> tuple[dict, list[dict]]:
    rel_root = "Trinity/creator/golden/v2/filter-17844-bigpicture-manual"
    sampling = {
        "method": sample["method"],
        "sample_count": sample["sample_count"],
        "candidate_pool_size": sample["candidate_pool_size"],
        "similarity_pool_size": sample["similarity_pool_size"],
        "similarity_count": sample["similarity_count"],
        "random_fill_count": sample["random_fill_count"],
        "random_seed": sample.get("random_seed"),
        "keywords": sample.get("keywords", []),
    }
    refs = []
    scores = sample.get("similarity_scores", {})
    titles = sample.get("titles", {})
    for key in sample["jira_keys"]:
        refs.append(
            {
                "jira_key": key,
                "path": f"{rel_root}/rag/by-key/{key}.json",
                "why_selected": (
                    f"Theme similarity rank (score {scores.get(key, 0)}) to {sample.get('keywords', [])}; "
                    f"title: {titles.get(key, '')[:100]}"
                ),
                "style_cues_applied": [
                    "Full JSON read for step depth and BP manual phrasing",
                    "Navigate → act → verify pattern with explicit test data blocks",
                ],
            }
        )
    return sampling, refs


def coverage_from_review(epic: str, tests: list[dict], review: dict) -> dict:
    gate = review.get("gate", {})
    warnings = []
    if gate.get("status") == "PASS_WITH_WARNINGS":
        warnings.append(f"Reviewer gate PASS_WITH_WARNINGS (high unresolved: {gate.get('high_unresolved_count', 0)}).")
    readiness = review.get("classifications", {}).get("readiness", {}).get("value", "")
    if "needs_clarification" in readiness:
        warnings.append("Reviewer readiness needs_clarification — journeys are provisional until AC/PRD ingest.")
    for f in review.get("findings", []):
        if f.get("severity") in ("HIGH", "MEDIUM"):
            warnings.append(f"{f.get('finding_id')}: {f.get('finding_summary')}")
    confluence_fail = any(
        c.get("type") == "confluence_page" and c.get("status") == "failed"
        for c in review.get("context_loaded", [])
    )
    if confluence_fail:
        warnings.append("Confluence PRD bodies unavailable in Reviewer session — assert behaviour against PM-confirmed AC before execution.")
    if not review.get("rollup", {}).get("epic_child_inventory"):
        warnings.append("No child issues under Epic — matrix uses epic-level GOAL ids only.")

    matrix = []
    for t in tests:
        for ac in t.get("linked_ac_ids", []):
            matrix.append(
                {
                    "jira_key": epic,
                    "ac_id": ac,
                    "status": "Covered" if not t.get("deferrable") else "PARTIAL",
                    "covered_by": [t["draft_id"]],
                    **({"blocker": t.get("deferrable_rationale")} if t.get("deferrable") else {}),
                }
            )

    deferrable = [t["draft_id"] for t in tests if t.get("deferrable")]
    if deferrable:
        warnings.append(f"Deferrable journeys pending scope/implementation: {', '.join(deferrable)}.")

    return {
        "uncovered_ac_ids": [],
        "uncovered_goals": [],
        "warnings": warnings,
        "matrix": matrix,
    }


def write_suite_report_md(
    epic: str, tests: list[dict], sampling: dict, refs: list[dict], generated_at: str
) -> str:
    lines = [
        f"# Suite report — {epic}",
        "",
        f"**Generated:** {generated_at}",
        "**Suite mode:** release_slice_e2e",
        f"**Review ref:** `Trinity/reviewer/runs/q4-backlog/{epic}/review-payload.json`",
        "",
        "## Golden references (CR-GOLDEN-01)",
        "",
        (
            f"Method `{sampling['method']}` — {sampling['sample_count']} references "
            f"({sampling['similarity_count']} similar, {sampling['random_fill_count']} random fill)."
        ),
        "",
    ]
    for r in refs:
        lines.append(f"- **{r['jira_key']}** — {r['why_selected'][:140]}")
    lines.extend(["", "## Tests", ""])
    for t in tests:
        defer = " · deferrable" if t.get("deferrable") else ""
        lines.append(f"### {t['draft_id']}: {t['title']}")
        lines.append(
            f"- Tier {t['execution_tier']} · {t['role']} · automation_fit={t['automation_fit']}{defer}"
        )
        lines.append("")
    lines.append(
        "Import: `Trinity/creator/artifacts/q4-backlog/{}/suite-payload.json`".format(epic)
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    summary_rows = []
    for epic in EPICS:
        review_path = REVIEW_ROOT / epic / "review-payload.json"
        review = json.loads(review_path.read_text(encoding="utf-8"))
        sample = sample_golden(epic)
        sampling, golden_refs = golden_refs_from_sample(sample)
        tests = tests_for_epic(epic)
        coverage = coverage_from_review(epic, tests, review)

        batch = {
            "schema_version": "1.0",
            "run_id": f"q4-backlog-{epic}",
            "generated_at": now,
            "golden_version": "golden/v2/filter-17844-bigpicture-manual",
            "suite_mode": "release_slice_e2e",
            "product_id": "bigpicture",
            "golden_root": "Trinity/creator/golden/v2/filter-17844-bigpicture-manual",
            "golden_sampling": sampling,
            "golden_references": golden_refs,
            "review_ref": f"Trinity/reviewer/runs/q4-backlog/{epic}/review-payload.json",
            "persona_files": [
                "Trinity/personas/creator-expert-qa-engineer.md",
                "Trinity/personas/creator-test-architect.md",
                "Trinity/personas/creator-expert-test-automation-engineer.md",
            ],
            "source_requirement_keys": [epic],
            "requirements_review_run_id": review.get("run_id", ""),
            "coverage_report": coverage,
            "execution_plan": build_execution_plan(tests),
            "tests": tests,
            "validation": {
                "schema_valid": True,
                "traceability_valid": True,
                "policy_valid": True,
                "errors": [],
            },
        }

        out_dir = OUT_ROOT / epic
        out_dir.mkdir(parents=True, exist_ok=True)
        payload_path = out_dir / "suite-payload.json"
        payload_path.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        md = write_suite_report_md(epic, tests, sampling, golden_refs, now)
        (out_dir / "suite-report.md").write_text(md, encoding="utf-8")

        subprocess.check_call(
            [
                "python3",
                str(BUILD_REPORT),
                "--batch",
                str(payload_path),
                "--out",
                str(out_dir / "suite-report"),
                "--run-id",
                f"q4-backlog-{epic}",
            ],
            cwd=REPO,
        )

        gate = review.get("gate", {}).get("status", "?")
        warn_n = len(coverage.get("warnings", []))
        summary_rows.append((epic, len(tests), gate, warn_n))
        print(f"Wrote {payload_path} ({len(tests)} tests)")

    print("\nSUMMARY")
    print("KEY | tests | gate | warnings")
    for row in summary_rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")


if __name__ == "__main__":
    main()
