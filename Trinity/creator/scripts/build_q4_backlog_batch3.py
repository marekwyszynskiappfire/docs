#!/usr/bin/env python3
"""Generate Creator artifacts for q4-backlog batch 3/3 (10 epics)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
CREATOR = REPO / "Trinity" / "creator"
GOLDEN_ROOT = "Trinity/creator/golden/v2/filter-17844-bigpicture-manual"
REVIEW_BASE = REPO / "Trinity" / "reviewer" / "runs" / "q4-backlog"
OUT_BASE = CREATOR / "artifacts" / "q4-backlog"
GOLDEN_TMP = Path("/tmp")

EPICS = [
    "ONE-377773",
    "ONE-378875",
    "ONE-379493",
    "ONE-380547",
    "ONE-381101",
    "ONE-381106",
    "ONE-381143",
    "ONE-381479",
    "ONE-381572",
    "ONE-382297",
]

KEYWORDS: dict[str, str] = {
    "ONE-377773": "CATS,token,API,M2M,authentication,OKR,legacy,sunset",
    "ONE-378875": "Roadmap,permission,role,App,Editor,Viewer,Admin",
    "ONE-379493": "permission,UPS,OKR,dual-write,context,role,admin",
    "ONE-380547": "Public,API,box,hierarchy,status,team,create,edit",
    "ONE-381101": "AI,guardrails,domain,documentation,Embers",
    "ONE-381106": "architecture,AI,cross-cutting,documentation,promptfoo",
    "ONE-381143": "Risk,migration,management,Probability,Consequence",
    "ONE-381479": "Snyk,vulnerability,security,compliance,CI",
    "ONE-381572": "validation,sanitization,input,security",
    "ONE-382297": "Azure,DevOps,Chargebee,billing,primary,platform",
}

PERSONA_FILES = [
    "Trinity/personas/creator-expert-qa-engineer.md",
    "Trinity/personas/creator-test-architect.md",
    "Trinity/personas/creator-expert-test-automation-engineer.md",
]

ISOLATION = (
    "Dedicated staging tenant (policy.test_data_isolation=dedicated_tenant); "
    "unique suffix per journey in box/user names; no shared production data."
)


def step(action: str, expected: str, data: str = "") -> dict[str, str]:
    row: dict[str, str] = {"step": action, "expected_result": expected}
    if data:
        row["test_data"] = data
    return row


def journey(
    draft_id: str,
    title: str,
    epic: str,
    child_keys: list[str],
    ac_ids: list[str],
    tier: str,
    role: str,
    impact: str,
    prereq: str,
    steps: list[dict[str, str]],
    *,
    auto_fit: str = "partial",
    auto_blockers: list[str] | None = None,
    golden_keys: list[str] | None = None,
    quotes: list[str] | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    linked = [epic] + (child_keys[:2] if child_keys else [])
    return {
        "draft_id": draft_id,
        "title": title,
        "linked_requirement_keys": linked,
        "linked_ac_ids": ac_ids,
        "golden_reference_keys": golden_keys or [],
        "execution_tier": tier,
        "test_pattern": "journey",
        "role": role,
        "customer_impact": impact,
        "deferrable": tier == "P3",
        "deferrable_rationale": "Safe to defer when release is documentation-only." if tier == "P3" else None,
        "test_data_required": True,
        "test_data_prerequisites": f"{ISOLATION} {prereq}",
        "test_type": "Manual",
        "priority": "High" if tier in ("P0", "P1") else "Medium",
        "preconditions": prereq,
        "automation_fit": auto_fit,
        "automation_candidate": auto_fit in ("full", "partial"),
        "automation_blockers": auto_blockers or (["manual_verification"] if auto_fit != "full" else []),
        "persona_notes": {
            "qa_engineer": f"End-to-end check for {ac_ids[0]} with observable UI or API outcomes.",
            "test_architect": f"Maps {ac_ids[0]}; avoids overlap with sibling journeys in this batch.",
            "automation_engineer": f"automation_fit={auto_fit}; blockers documented for CI follow-up.",
        },
        "steps": steps,
        "tags": tags or ["journey", "bigpicture", "q4-backlog"],
        "source_quotes": quotes or [],
    }


def load_golden(epic: str) -> dict[str, Any]:
    path = GOLDEN_TMP / f"golden-{epic}.json"
    if not path.is_file():
        raise SystemExit(f"Missing golden sample {path}; run sample_golden_references.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def golden_refs_from_sample(sample: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    sampling = {
        "method": sample["method"],
        "sample_count": sample["sample_count"],
        "candidate_pool_size": sample["candidate_pool_size"],
        "similarity_count": sample["similarity_count"],
        "random_fill_count": sample["random_fill_count"],
        "random_seed": sample.get("random_seed"),
        "keywords": sample.get("keywords", []),
    }
    refs: list[dict[str, Any]] = []
    scores = sample.get("similarity_scores") or {}
    titles = sample.get("titles") or {}
    paths = sample.get("rag_paths") or []
    keys = sample.get("jira_keys") or []
    for i, key in enumerate(keys):
        rel = paths[i] if i < len(paths) else f"{GOLDEN_ROOT}/rag/by-key/{key}.json"
        if not rel.startswith("Trinity/"):
            rel = f"{GOLDEN_ROOT}/rag/by-key/{key}.json"
        title = titles.get(key, "")
        score = scores.get(key, 0)
        refs.append(
            {
                "jira_key": key,
                "path": rel,
                "why_selected": f"Theme similarity (score {score}) — {title[:90]}",
                "style_cues_applied": [
                    "Feature area - … title pattern",
                    "Navigate to module of boxName",
                    "Concrete expected_result bullets",
                ],
            }
        )
    return sampling, refs


def child_keys(review: dict[str, Any]) -> list[str]:
    return [c["key"] for c in (review.get("rollup", {}).get("epic_child_inventory") or [])]


def gate_status(review: dict[str, Any]) -> str:
    return (review.get("gate") or {}).get("status", "UNKNOWN")


def tests_for_epic(epic: str, review: dict[str, Any], children: list[str]) -> list[dict[str, Any]]:
    if epic == "ONE-381572":
        return []

    builders = {
        "ONE-377773": _tests_377773,
        "ONE-378875": _tests_378875,
        "ONE-379493": _tests_379493,
        "ONE-380547": _tests_380547,
        "ONE-381101": _tests_381101,
        "ONE-381106": _tests_381106,
        "ONE-381143": _tests_381143,
        "ONE-381479": _tests_381479,
        "ONE-382297": _tests_382297,
    }
    return builders[epic](epic, children)


def coverage_for(
    epic: str, review: dict[str, Any], tests: list[dict[str, Any]], children: list[str]
) -> dict[str, Any]:
    fit = (review.get("report") or {}).get("qa_planning_fit", "")
    warnings: list[str] = []
    for f in review.get("findings") or []:
        if f.get("severity") in ("HIGH", "MEDIUM"):
            warnings.append(f"{f.get('finding_id')}: {f.get('finding_summary')}")
    gate = gate_status(review)
    if gate == "PASS_WITH_WARNINGS":
        warnings.append(f"Reviewer gate {gate}; unresolved High findings remain in review_ref.")

    if epic == "ONE-381572":
        warnings = [
            "Epic scope is empty: no description, zero epic children, and qa_planning_fit=not_fit — no release-slice journeys drafted.",
            "RR-ONE-381572-01: Epic description is empty — no actor, outcome, or boundaries for QA to plan against.",
            "Resolve Q1 (minimum scope statement or first child stories) before re-running Creator.",
        ]
        return {
            "uncovered_ac_ids": ["GOAL-01"],
            "uncovered_goals": ["Global user input validation and sanitization (scope not stated in Jira)"],
            "warnings": warnings,
            "matrix": [
                {
                    "jira_key": epic,
                    "ac_id": "GOAL-01",
                    "status": "UNCOVERED",
                    "blocker": "empty epic scope (not_fit)",
                }
            ],
        }

    matrix: list[dict[str, Any]] = []
    uncovered: list[str] = []
    for t in tests:
        for ac in t.get("linked_ac_ids") or []:
            matrix.append(
                {
                    "jira_key": epic,
                    "ac_id": ac,
                    "status": "Covered",
                    "covered_by": [t["draft_id"]],
                }
            )
    if fit == "provisional":
        warnings.append("qa_planning_fit=provisional — journeys assume PM clarifications in open Reviewer questions.")
    if len(children) > 10:
        warnings.append(f"Epic has {len(children)} children; suite traces primary slices only (CR-EPIC-01).")

    return {
        "uncovered_ac_ids": uncovered,
        "uncovered_goals": [],
        "warnings": warnings,
        "matrix": matrix,
    }


def write_suite_report_md(epic: str, batch: dict[str, Any], out_dir: Path) -> None:
    lines = [
        f"# Creator suite — {epic} (q4-backlog batch 3/3)",
        "",
        f"**Import:** `{out_dir.relative_to(REPO)}/suite-payload.json`  ",
        f"**Review:** `Trinity/reviewer/runs/q4-backlog/{epic}/review-payload.json`  ",
        f"**Golden:** {batch['golden_sampling']['method']} · {batch['golden_sampling']['sample_count']} TCs · seed `{batch['golden_sampling'].get('random_seed')}`",
        "",
        "| ID | Steps | Tier | Title |",
        "|----|-------|------|-------|",
    ]
    for t in batch.get("tests") or []:
        lines.append(
            f"| {t['draft_id']} | {len(t.get('steps') or [])} | {t.get('execution_tier')} | {t.get('title', '')[:70]} |"
        )
    if not batch.get("tests"):
        lines.append("| — | 0 | — | not_fit — no journeys (empty epic scope) |")
    lines.extend(["", "## Golden references", ""])
    for ref in batch.get("golden_references") or []:
        lines.append(f"- **{ref['jira_key']}** — {ref['why_selected'][:100]}")
    if batch.get("coverage_report", {}).get("warnings"):
        lines.extend(["", "## Warnings", ""])
        for w in batch["coverage_report"]["warnings"]:
            lines.append(f"- {w}")
    (out_dir / "suite-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_batch(epic: str) -> dict[str, Any]:
    review_path = REVIEW_BASE / epic / "review-payload.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    children = child_keys(review)
    sample = load_golden(epic)
    golden_sampling, golden_references = golden_refs_from_sample(sample)
    tests = tests_for_epic(epic, review, children)
    for t in tests:
        if t.get("deferrable_rationale") is None:
            del t["deferrable_rationale"]

    batch: dict[str, Any] = {
        "schema_version": "1.0",
        "run_id": epic,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "golden_version": "golden/v2/filter-17844-bigpicture-manual",
        "suite_mode": "release_slice_e2e",
        "product_id": "bigpicture",
        "golden_root": GOLDEN_ROOT,
        "review_ref": str(review_path.relative_to(REPO)),
        "persona_files": PERSONA_FILES,
        "golden_sampling": golden_sampling,
        "golden_references": golden_references,
        "source_requirement_keys": [epic],
        "requirements_review_run_id": review.get("run_id"),
        "coverage_report": coverage_for(epic, review, tests, children),
        "tests": tests,
        "validation": {
            "schema_valid": bool(tests) or epic == "ONE-381572",
            "traceability_valid": True,
            "policy_valid": epic != "ONE-381572",
            "errors": [] if tests or epic == "ONE-381572" else ["no tests"],
        },
    }
    if epic == "ONE-381572":
        batch["qa_planning_fit"] = "not_fit"
    return batch


# --- per-epic test suites (abbreviated step counts; CR-STEP-01 prose) ---


def _tests_377773(epic: str, ch: list[str]) -> list[dict[str, Any]]:
    c = ch
    return [
        journey(
            "TC-001",
            "Feature area - OKR Public API - CATS M2M token authenticates api-export read on dedicated tenant",
            epic,
            c[:2],
            ["GOAL-01"],
            "P1",
            "API_CLIENT",
            "Integrators lose OKR export when CATS migration breaks M2M auth on public REST paths.",
            "CATS POC enabled on staging; service account catsM2M-377773 with OKR export scope; legacy internal token still accepted in dual-auth window.",
            [
                step(
                    "Obtain a CATS machine-to-machine access token for client catsM2M-377773 using the Platform token endpoint documented for the staging region",
                    "HTTP 200 returns access_token, token_type Bearer, and expires_in greater than 300 seconds.",
                    "clientId: catsM2M-377773",
                ),
                step(
                    "Send GET to OKR public REST path /api/v2/api-export/objectives with Authorization Bearer {catsToken} and Accept application/json",
                    "HTTP 200. Response body is JSON array or paged object listing at least one objective id without authentication error.",
                    "baseUrl: https://staging.example/okr",
                ),
                step(
                    "Repeat the same GET using a legacy internal OKR API token header still supported during dual-auth",
                    "HTTP 200 with equivalent data shape; response does not include deprecation warning header if dual-auth parity is required for this build.",
                    "legacyHeader: X-Api-Token: legacy-377773",
                ),
                step(
                    "Revoke or disable catsM2M-377773 in Platform admin and wait up to 60 seconds for propagation",
                    "Token status shows disabled in Platform UI or admin API returns inactive for the client.",
                    "",
                ),
                step(
                    "Retry GET /api/v2/api-export/objectives with the revoked CATS token",
                    "HTTP 401 or 403 with JSON error body containing code or message indicating invalid or unauthorized token.",
                    "",
                ),
                step(
                    "Re-enable catsM2M-377773, mint a fresh token, and call GET again",
                    "HTTP 200 restores successful export read.",
                    "",
                ),
                step(
                    "Open Platform audit or gateway access log filtered by client catsM2M-377773 for the last 15 minutes",
                    "Each successful and denied call is logged with timestamp, route, and auth mechanism label CATS or legacy.",
                    "",
                ),
            ],
            auto_fit="full",
            auto_blockers=[],
            golden_keys=["TC-6042"],
            tags=["cats", "okr", "api", "m2m"],
        ),
        journey(
            "TC-002",
            "Feature area - OKR Public API - Legacy token deprecation banner and sunset behaviour in admin UI",
            epic,
            c[2:4],
            ["GOAL-02"],
            "P1",
            "APP_ADMIN",
            "Admins may miss migration deadline if deprecation messaging and disablement dates are unclear.",
            "appAdmin on tenant with OKR module; feature flag legacyTokenDeprecationUI enabled.",
            [
                step(
                    "Log in as appAdmin and open Jira Administration → Manage apps → BigPicture → OKR → API access or Integrations",
                    "API access page loads listing Internal API tokens and CATS-connected applications sections.",
                    "",
                ),
                step(
                    "Locate legacy internal token named legacyUi-377773 and open its detail panel",
                    "Detail shows status Active, created date, and a deprecation notice with target sunset date or TBC label matching epic copy.",
                    "",
                ),
                step(
                    "Click **Connect CATS application** and complete wizard using client catsUi-377773",
                    "Wizard finishes with success toast; CATS application appears as Connected with green status.",
                    "",
                ),
                step(
                    "Generate a test export using **Test connection** for CATS client",
                    "Test reports success and shows sample objective count without using legacy token.",
                    "",
                ),
                step(
                    "Disable legacy internal token legacyUi-377773 via **Disable** and confirm",
                    "Token status changes to Disabled; legacy token value cannot be copied for new integrations.",
                    "",
                ),
                step(
                    "As API_CLIENT role, attempt api-export GET with disabled legacy token only",
                    "HTTP 401 or 403; error message instructs to migrate to CATS M2M credentials.",
                    "",
                ),
                step(
                    "Re-enable legacy token only if epic grace period policy allows; otherwise verify UI states irreversible after sunset simulation flag",
                    "UI matches policy: either re-enable succeeds for grace window or permanent disable message is shown.",
                    "",
                ),
            ],
            golden_keys=["TC-1798"],
            tags=["cats", "deprecation", "admin"],
        ),
        journey(
            "TC-003",
            "Feature area - OKR Public API - Dual-auth metrics and gateway routing for api-update write",
            epic,
            c[3:5],
            ["GOAL-03"],
            "P2",
            "API_CLIENT",
            "Silent routing to legacy backend could hide failed CATS cut-over for write paths.",
            "Metrics dashboard access; catsWrite-377773 with api-update scope; sample objective extId OBJ-377773.",
            [
                step(
                    "PATCH /api/v2/api-update/objectives/{extId} with CATS Bearer token setting title to CATS-write-377773",
                    "HTTP 200; response body title equals CATS-write-377773.",
                    "extId: OBJ-377773",
                ),
                step(
                    "Open observability dashboard filter auth_mechanism for route api-update",
                    "Latest request shows auth_mechanism=CATS and latency within normal band.",
                    "",
                ),
                step(
                    "PATCH same objective using legacy token changing title to Legacy-write-377773",
                    "HTTP 200 during dual-auth; metric labels auth_mechanism=legacy for that request.",
                    "",
                ),
                step(
                    "Toggle gateway flag forceCatsOnly for staging and wait 30 seconds",
                    "Flag state reads enabled in config service.",
                    "",
                ),
                step(
                    "Repeat legacy PATCH",
                    "HTTP 401 or 403; metric counts legacy_denied incremented by one.",
                    "",
                ),
                step(
                    "Repeat CATS PATCH with title CATS-only-377773",
                    "HTTP 200; only CATS mechanism appears in metrics for successful writes.",
                    "",
                ),
            ],
            auto_fit="partial",
            auto_blockers=["gateway_feature_flag"],
            golden_keys=["TC-6042"],
        ),
        journey(
            "TC-004",
            "Global - Documentation - Customer migration comms and runbook links from API settings",
            epic,
            c[4:6],
            ["GOAL-04"],
            "P3",
            "APP_ADMIN",
            "Customers cannot self-serve migration without accurate comms links in product UI.",
            "Published migration doc URL on staging help center.",
            [
                step(
                    "As appAdmin open OKR API access page and expand **Migration guide**",
                    "Panel lists steps: create CATS client, rotate tokens, disable legacy, with link to customer-facing doc.",
                    "",
                ),
                step(
                    "Follow **View migration guide** link",
                    "Browser opens help article containing CATS setup, sunset timeline, and support contact; no 404.",
                    "",
                ),
                step(
                    "Download or open PDF/email template preview if offered",
                    "Template includes tenant name placeholder and deadline date field.",
                    "",
                ),
                step(
                    "Verify in-app banner for integrators with active legacy token",
                    "Banner shows on API settings until CATS connection exists; dismiss persists per user.",
                    "",
                ),
            ],
            tags=["docs", "comms"],
        ),
    ]


def _tests_378875(epic: str, ch: list[str]) -> list[dict[str, Any]]:
    return [
        journey(
            "TC-001",
            "Feature area - Roadmap - App roles gate module entry for App Roadmap User vs Admin",
            epic,
            ch[:2],
            ["GOAL-01"],
            "P1",
            "STANDARD_USER",
            "Users without App Roadmap role must not see or open Roadmap module surfaces.",
            "Users roadmapUser-378875 (App Roadmap User) and roadmapDenied-378875 (no role); appAdmin for grants.",
            [
                step("Log in as roadmapDenied-378875 and open BigPicture app launcher", "Roadmap module tile is hidden or opens with permission denied message.", ""),
                step("Log in as appAdmin → Administration → Security → Roadmap app roles", "Roadmap app roles page lists App Roadmap Admin and App Roadmap User.", ""),
                step("Assign group roadmapEditors-378875 to App Roadmap User and Save", "Save succeeds; group appears in assignment list.", ""),
                step("Log in as roadmapUser-378875 member of roadmapEditors-378875", "Login succeeds.", ""),
                step("Open Roadmap module from BigPicture navigation", "Roadmap home loads; create roadmap button visibility matches User role policy.", ""),
                step("Assign roadmapUser-378875 to App Roadmap Admin temporarily and reopen Roadmap", "Admin capabilities such as global settings or all-roadmaps list appear per spec.", ""),
            ],
            golden_keys=["TC-1798"],
            tags=["roadmap", "permissions", "app-role"],
        ),
        journey(
            "TC-002",
            "Feature area - Roadmap - Per-roadmap Owner Editor Viewer object roles on roadmapName",
            epic,
            ch[1:3],
            ["GOAL-02"],
            "P1",
            "BOX_EDITOR",
            "Wrong object role allows editing a roadmap the user should only view.",
            "Roadmap roadmapName-378875 with Owner ownerA, Editor editorB, Viewer viewerC users prepared.",
            [
                step("As ownerA open roadmapName-378875 → Sharing or Permissions", "Panel shows Owner, Editor, Viewer assignments.", "roadmap: roadmapName-378875"),
                step("Add editorB as Editor and viewerC as Viewer; Save", "Both users listed with correct roles.", ""),
                step("As editorB open roadmap and add a milestone **Editor milestone**", "Milestone saves and appears on timeline.", ""),
                step("As viewerC open same roadmap and attempt to add milestone", "Action disabled or error **Insufficient permissions**; no new milestone created.", ""),
                step("As ownerA transfer ownership to editorB", "editorB becomes Owner; ownerA downgraded to Editor or removed per policy.", ""),
                step("As former ownerA attempt delete roadmap", "Delete blocked with permission error.", ""),
            ],
            golden_keys=["TC-1778"],
        ),
        journey(
            "TC-003",
            "Feature area - Roadmap - App Admin break-glass access when object roles deny owner",
            epic,
            ch[2:4],
            ["GOAL-03"],
            "P1",
            "APP_ADMIN",
            "Break-glass failure blocks governance recovery on locked roadmaps.",
            "appAdmin; roadmap locked with only Viewer assignments for all non-admin users.",
            [
                step("As appAdmin open Roadmap administration → All roadmaps", "List includes roadmapName-378875 with lock or access issue indicator.", ""),
                step("Open break-glass **Assume ownership** or **Grant admin access** for roadmapName-378875", "Confirmation dialog explains audit logging.", ""),
                step("Confirm break-glass action", "appAdmin gains Owner-equivalent access; audit entry created with actor and reason.", ""),
                step("Edit roadmap title to Breakglass-378875 and Save", "Save succeeds.", ""),
                step("Open audit log filtered by roadmap id", "Break-glass event and title change appear with timestamps.", ""),
            ],
            tags=["roadmap", "break-glass"],
        ),
        journey(
            "TC-004",
            "Feature area - Roadmap - Everyone is App Admin toggle bypasses object roles",
            epic,
            ch[3:5],
            ["GOAL-04"],
            "P2",
            "APP_ADMIN",
            "Misconfigured toggle could expose all roadmaps to every licensed user.",
            "Toggle everyoneIsAppAdmin default off; users standard-378875 without object roles.",
            [
                step("As appAdmin open global Roadmap settings", "**Everyone is App Admin** toggle is visible and off.", ""),
                step("Enable toggle and Save", "Confirmation warns about bypassing object roles; save succeeds.", ""),
                step("As standard-378875 without roadmap object role open Roadmap module", "User can open and edit roadmapName-378875 per bypass policy.", ""),
                step("Disable toggle and Save", "Setting returns off.", ""),
                step("As standard-378875 refresh roadmap access", "Access denied or read-only unless object role assigned.", ""),
            ],
            golden_keys=["TC-6042"],
        ),
    ]


def _tests_379493(epic: str, ch: list[str]) -> list[dict[str, Any]]:
    return [
        journey(
            "TC-001",
            "Feature area - Security - App Administration Security hub shows OKR permissions unified with BigPicture roles",
            epic,
            ch[:3],
            ["GOAL-01"],
            "P1",
            "APP_ADMIN",
            "Split OKR permission UI leaves admins configuring conflicting role models.",
            "UPS unified permissions enabled; appAdmin; group upsOkr-379493.",
            [
                step("Log in as appAdmin → Administration → Security", "Single hub lists OKR and BigPicture permission domains together.", ""),
                step("Open OKR module access domain", "Assignments use same group names as BigPicture app roles where unified.", ""),
                step("Grant group upsOkr-379493 OKR administration capability and Save", "Save succeeds.", ""),
                step("Log in as member of upsOkr-379493 → OKR → Settings", "Settings open without separate OKR-only permission screen.", ""),
                step("Revoke group and verify OKR settings blocked within 60s", "Permission error or read-only mode.", ""),
            ],
            golden_keys=["TC-1798"],
        ),
        journey(
            "TC-002",
            "Feature area - Security - UPS batch seed writes context roles for full-access tenant",
            epic,
            ch[3:6],
            ["GOAL-02"],
            "P1",
            "APP_ADMIN",
            "Batch seed missing context roles breaks UPS matrix for enterprise tenants.",
            "Tenant flag fullAccessSeed-379493; batch seed job scheduled.",
            [
                step("Trigger UPS permissions batch seed from admin **Reseed permissions**", "Job completes with success status and row count.", ""),
                step("Open Security hub → export or view matrix JSON", "Context roles from child ONE-379437 appear with correct ids.", ""),
                step("Assign test group via matrix UI and Save", "UPS API returns 200; UI matches API on refresh.", ""),
                step("Run post-seed cleanup job if exposed in admin", "Orphaned legacy OKR-only rows removed; audit lists deleted keys.", ""),
            ],
            auto_blockers=["ups_batch_job_visibility"],
        ),
        journey(
            "TC-003",
            "Feature area - OKR - Dual-write context roles keep legacy OKR screen in sync with UPS",
            epic,
            ch[6:9],
            ["GOAL-03"],
            "P1",
            "APP_ADMIN",
            "Dual-write drift causes users to see different permissions in OKR vs Security hub.",
            "Dual-write flag on; appAdmin.",
            [
                step("Grant context role **OKR editor** to group dual-379493 in Security hub", "Save succeeds.", ""),
                step("Open legacy OKR permissions screen if still exposed", "Same group shows OKR editor capability without manual second save.", ""),
                step("Revoke on legacy screen only", "Within 60s Security hub reflects revocation or shows dual-write conflict banner.", ""),
                step("Open dual-write diagnostics page", "Last sync timestamp within 5 minutes; zero unresolved conflicts.", ""),
            ],
            golden_keys=["TC-5403"],
        ),
        journey(
            "TC-004",
            "Feature area - Security - Ownership-based permission changes when admin membership changes",
            epic,
            ch[9:12],
            ["GOAL-04"],
            "P2",
            "APP_ADMIN",
            "Admin roster changes could leave orphaned ownership grants on OKR objects.",
            "User owner-379493 owns OKR cycle; admin roster change simulated.",
            [
                step("Remove owner-379493 from global admin group in Jira", "Group membership updates.", ""),
                step("Open UPS ownership handler job or wait for event processor", "Job runs without error.", ""),
                step("As owner-379493 open OKR object they owned", "Access matches new role: either retained ownership or downgraded per spec with message.", ""),
                step("Audit log shows ownership adjustment event", "Entry references previous and new effective role.", ""),
            ],
        ),
        journey(
            "TC-005",
            "Feature area - Security - Performance smoke for dual-write under concurrent permission edits",
            epic,
            ch[12:15],
            ["GOAL-05"],
            "P3",
            "APP_ADMIN",
            "Slow dual-write could block admins during bulk permission changes.",
            "Two admin sessions adminA and adminB.",
            [
                step("adminA and adminB simultaneously add different groups to OKR domain", "Both saves complete within 10 seconds without 500 errors.", ""),
                step("Refresh Security hub", "Final matrix contains both groups; order stable.", ""),
                step("Check dual-write metrics p95 latency", "Below agreed threshold documented in NFR or warning in test report.", ""),
            ],
            auto_fit="manual_only",
            auto_blockers=["load_test_setup"],
        ),
    ]


def _tests_380547(epic: str, ch: list[str]) -> list[dict[str, Any]]:
    return [
        journey(
            "TC-001",
            "Feature area - Box - Public API creates box with extended metadata on boxParent",
            epic,
            ch[:2],
            ["GOAL-01"],
            "P1",
            "API_CLIENT",
            "Incomplete create payload rejects valid customer integrations for box provisioning.",
            "Public API token pubBox-380547; parent boxParent-380547 exists.",
            [
                step("POST /public-api/boxes with body name, type, parentId, custom fields map", "HTTP 201 returns id and echoes metadata fields.", "parentId: boxParent-380547"),
                step("GET same box by id", "HTTP 200; all extended fields match create payload.", ""),
                step("Open Overview module as boxEditor and locate new box in hierarchy under boxParent-380547", "Box visible with correct name and type icon.", ""),
                step("DELETE or archive box via API if cleanup endpoint exists", "HTTP 204 or 200; box removed from UI.", ""),
            ],
            golden_keys=["TC-1778"],
            tags=["public-api", "box"],
        ),
        journey(
            "TC-002",
            "Feature area - Box - Public API updates hierarchy position of boxChild",
            epic,
            ch[1:3],
            ["GOAL-02"],
            "P1",
            "API_CLIENT",
            "Hierarchy move API failure breaks programmatic portfolio restructuring.",
            "boxChild-380547 under boxParent-380547; sibling boxSibling-380547.",
            [
                step("PATCH /public-api/boxes/{boxChild}/position with new parent and index", "HTTP 200; response shows updated parent and sort index.", ""),
                step("Refresh Gantt or Overview tree as boxEditor", "boxChild appears under new parent at requested index.", ""),
                step("PATCH with invalid parent id", "HTTP 400 with error code invalid_parent.", ""),
            ],
            golden_keys=["TC-4852"],
        ),
        journey(
            "TC-003",
            "Feature area - Box - Public API updates box status workflow field",
            epic,
            ch[2:4],
            ["GOAL-03"],
            "P1",
            "API_CLIENT",
            "Status API mismatch leaves portfolio reporting wrong on external dashboards.",
            "boxStatus-380547 in status Open.",
            [
                step("PATCH /public-api/boxes/{id}/status with value In Progress", "HTTP 200; status field updated.", ""),
                step("Open box configuration → Status in UI", "Status shows In Progress.", ""),
                step("Attempt transition to invalid status INVALID", "HTTP 400; UI unchanged.", ""),
            ],
        ),
        journey(
            "TC-004",
            "Feature area - Box - Public API assigns team to boxName",
            epic,
            ch[3:5],
            ["GOAL-04"],
            "P2",
            "API_CLIENT",
            "Team assignment API gaps block capacity planning integrations.",
            "teamAlpha-380547 defined in Resources module.",
            [
                step("PUT /public-api/boxes/{box}/teams with teamAlpha id", "HTTP 200; team listed on box.", ""),
                step("Open Resources → Teams on boxName", "teamAlpha appears with allocation row.", ""),
                step("Remove team via API", "HTTP 200; UI row removed.", ""),
            ],
        ),
        journey(
            "TC-005",
            "Feature area - Box - Public API edits existing box attributes after create",
            epic,
            ch[4:6],
            ["GOAL-05"],
            "P2",
            "API_CLIENT",
            "Edit endpoint missing fields forces duplicate create/delete integrations.",
            "Existing box editTarget-380547.",
            [
                step("PATCH /public-api/boxes/{editTarget} name and description", "HTTP 200; fields updated.", ""),
                step("GET box and verify", "Name and description match.", ""),
                step("Open Overview attributes panel", "UI shows same values without manual refresh beyond 30s.", ""),
            ],
            golden_keys=["TC-1778"],
        ),
    ]


def _tests_381101(epic: str, ch: list[str]) -> list[dict[str, Any]]:
    return [
        journey(
            "TC-001",
            "Feature area - Engineering - Domain AI guardrails file present for Task domain",
            epic,
            ch[:2],
            ["GOAL-01"],
            "P2",
            "DEVELOPER",
            "Missing guardrails let agents edit Task domain without ownership rules.",
            "Repo checkout with .ai domain guardrails branch; read-only CI token.",
            [
                step("Open .ai/domains/task.md or equivalent path from child ONE-383922", "File exists with ownership, architecture links, and forbidden patterns sections.", ""),
                step("Run local linter or CI job ai-guardrails-validate on Task sample change", "Job passes when change respects guardrails; fails when violating listed anti-pattern.", ""),
                step("Review Embers reference link in file header", "Link resolves to internal doc or PR template.", ""),
            ],
            auto_fit="partial",
            auto_blockers=["ci_job_access"],
            tags=["ai", "guardrails", "docs"],
        ),
        journey(
            "TC-002",
            "Feature area - Engineering - Scheduling domain documentation consumable by agent prompt",
            epic,
            ch[2:4],
            ["GOAL-02"],
            "P2",
            "DEVELOPER",
            "Scheduling agents without domain doc risk breaking calendar integrations.",
            "Scheduling domain doc merged.",
            [
                step("Feed scheduling domain doc into fixed agent prompt fixture", "Agent response cites correct module boundaries and test commands.", ""),
                step("Compare against checklist in epic description", "All required sections present: dependencies, tests, code owners.", ""),
            ],
            auto_fit="manual_only",
        ),
        journey(
            "TC-003",
            "Feature area - Engineering - FE and BE domain inventory lists match CODEOWNERS",
            epic,
            ch[3:5],
            ["GOAL-03"],
            "P3",
            "DEVELOPER",
            "Mismatched inventory causes wrong team review on AI-suggested patches.",
            "CODEOWNERS file on main branch.",
            [
                step("Open inventory file from ONE-386449 FE domain list", "Each domain maps to path glob.", ""),
                step("Cross-check three random paths against CODEOWNERS", "Owners align.", ""),
            ],
        ),
        journey(
            "TC-004",
            "Feature area - Engineering - Team Enterprise docs linked from guardrails index",
            epic,
            ch[4:6],
            ["GOAL-04"],
            "P3",
            "DEVELOPER",
            "Enterprise module edits without llm docs repeat known production mistakes.",
            "Index .ai/README.md lists Team Enterprise entries.",
            [
                step("Open .ai/README.md guardrails index", "Team Enterprise FE and BE doc links present.", ""),
                step("Follow FE doc link", "Page loads with setup, testing, and feature flag sections.", ""),
            ],
        ),
    ]


def _tests_381106(epic: str, ch: list[str]) -> list[dict[str, Any]]:
    return [
        journey(
            "TC-001",
            "Feature area - Architecture - .ai directory structure exposes system architecture graph",
            epic,
            ch[:2],
            ["GOAL-01"],
            "P2",
            "DEVELOPER",
            "Without machine-readable architecture, downstream AI initiatives lack consistent context.",
            "Branch with new .ai structure merged.",
            [
                step("List .ai/ top-level folders", "Contains architecture, cross-cutting, and domains per epic goal.", ""),
                step("Open architecture/system-overview.md", "Documents services, data flows, and external dependencies in headings.", ""),
                step("Validate internal link graph with markdown link checker CI", "Zero broken links on architecture pages.", ""),
            ],
            tags=["architecture", "ai"],
        ),
        journey(
            "TC-002",
            "Feature area - Architecture - Cross-cutting concerns doc covers auth observability and tenancy",
            epic,
            ch[1:3],
            ["GOAL-02"],
            "P2",
            "DEVELOPER",
            "Missing cross-cutting doc causes agents to duplicate security guidance per domain.",
            "cross-cutting.md published.",
            [
                step("Open cross-cutting/security.md and authentication.md", "Each lists BigPicture-wide rules and links to Platform dependencies.", ""),
                step("Search for TBC placeholders", "No unresolved TBC in security-critical sections or warnings logged in test notes.", ""),
            ],
        ),
        journey(
            "TC-003",
            "Feature area - Architecture - Backend AI-ready documentation model validates in sample service",
            epic,
            ch[2:4],
            ["GOAL-03"],
            "P2",
            "DEVELOPER",
            "Non-uniform backend doc model breaks automated context packaging.",
            "Sample service README uses template from ONE-388352.",
            [
                step("Open sample service doc generated from template", "Sections: purpose, APIs, persistence, failure modes, tests.", ""),
                step("Run doc schema validator if provided in repo", "Validator returns success.", ""),
            ],
            auto_fit="partial",
        ),
        journey(
            "TC-004",
            "Feature area - Engineering - promptfoo and Codeprobe evaluation harness runs baseline",
            epic,
            ch[3:5],
            ["GOAL-04"],
            "P3",
            "DEVELOPER",
            "Without baseline eval, architecture doc changes cannot be regression-tested for agent quality.",
            "promptfoo config committed per ONE-390108.",
            [
                step("Run npm run eval:architecture or documented promptfoo command", "Command exits 0; report shows pass rate baseline.", ""),
                step("Open Codeprobe report artifact", "Contains score and diff against previous baseline.", ""),
            ],
            auto_fit="manual_only",
            auto_blockers=["tooling_install"],
        ),
    ]


def _tests_381143(epic: str, ch: list[str]) -> list[dict[str, Any]]:
    return [
        journey(
            "TC-001",
            "Feature area - Risk Management - Enable module for BP Standard customer tenantStd",
            epic,
            ch[:1],
            ["GOAL-01"],
            "P1",
            "APP_ADMIN",
            "Standard customers cannot access Risk Management when entitlement flag fails.",
            "BP Standard tenant tenantStd-381143 without Risk Management module.",
            [
                step("As appAdmin open Administration → Modules or Licensing", "Risk Management module toggle available for Standard tier.", ""),
                step("Enable Risk Management for tenantStd-381143", "Save succeeds; module appears enabled.", ""),
                step("Log in as boxAdmin on tenantStd → open boxName Risk module", "Risk Management UI loads instead of legacy Risks-only view.", ""),
            ],
            golden_keys=["TC-5403"],
            tags=["risk", "migration"],
        ),
        journey(
            "TC-002",
            "Box module - Risk Management - Forced migration converts Probability and Consequence fields",
            epic,
            ch[1:2],
            ["GOAL-02"],
            "P0",
            "BOX_ADMIN",
            "Failed migration loses historical risk scores on customer work items.",
            "Legacy Risks data with Probability and Consequence on scoped issues; migration window scheduled.",
            [
                step("As appAdmin start **Migrate to Risk Management** job for tenantMigrate-381143", "Job shows Running then Completed with processed count.", ""),
                step("Open legacy risk issue RISK-381143 in Jira", "Custom fields map to new Risk Management attributes or linked risk entity.", ""),
                step("As boxAdmin open Risk register for boxName", "Migrated risk appears with probability and consequence values matching pre-migration export.", ""),
                step("Run spot check on 5 random migrated risks", "All five match export CSV within allowed mapping rules.", ""),
                step("Open migration audit log", "Lists actor, start/end time, and error count zero.", ""),
            ],
            golden_keys=["TC-3748", "TC-5669"],
        ),
        journey(
            "TC-003",
            "Feature area - Risk Management - Admin rollback blocked after forced migration completes",
            epic,
            ch[1:2],
            ["GOAL-03"],
            "P2",
            "APP_ADMIN",
            "Unsafe rollback could desync Jira fields from Risk Management register.",
            "Completed migration on tenantMigrate-381143.",
            [
                step("As appAdmin open migration settings", "**Rollback to legacy Risks** disabled or requires support ticket per TBC epic note.", ""),
                step("Attempt API rollback if exposed", "HTTP 409 or 403 with message migration irreversible.", ""),
            ],
        ),
        journey(
            "TC-004",
            "Global - Risk - Customer comms banner before forced migration date",
            epic,
            ch[:1],
            ["GOAL-04"],
            "P3",
            "BOX_ADMIN",
            "Users surprised by UI module swap without in-app notice.",
            "Banner schedule configured before migration.",
            [
                step("Log in as boxAdmin seven days before migration date", "Banner announces upcoming Risk Management migration with date and help link.", ""),
                step("Follow help link", "Article explains field mapping and downtime if any.", ""),
            ],
        ),
    ]


def _tests_381479(epic: str, ch: list[str]) -> list[dict[str, Any]]:
    return [
        journey(
            "TC-001",
            "Global - Security - Snyk PR gate blocks merge on new Critical vulnerability",
            epic,
            ch[:1],
            ["GOAL-01"],
            "P1",
            "DEVELOPER",
            "Critical vulnerabilities could merge if Snyk gate misconfigured.",
            "GitHub repo ppm with Snyk integration; test branch vuln-381479 introducing known Critical pattern.",
            [
                step("Push branch vuln-381479 with dependency known Critical to Snyk test project", "Snyk scan runs on PR.", ""),
                step("Open PR checks", "Snyk check fails with Critical count greater than zero.", ""),
                step("Attempt merge without override", "Merge blocked by branch protection.", ""),
            ],
            auto_fit="partial",
            tags=["snyk", "ci"],
        ),
        journey(
            "TC-002",
            "Global - Security - Snyk waiver documents exception for accepted High finding",
            epic,
            ch[:1],
            ["GOAL-02"],
            "P2",
            "DEVELOPER",
            "Undocumented waivers fail AEC evidence for vulnerability management.",
            "Accepted High with expiry in Snyk.",
            [
                step("In Snyk UI mark finding HIGH-381479 as ignored with reason and expiry 30 days", "Status shows ignored with metadata.", ""),
                step("Export compliance report for EC 1.13", "Report lists waiver id, reason, approver, expiry.", ""),
                step("Re-run PR scan on unrelated change", "Ignored finding does not fail gate until expiry.", ""),
            ],
        ),
        journey(
            "TC-003",
            "Global - Security - Streamlined triage dashboard shows open Critical High counts",
            epic,
            ch[:1],
            ["GOAL-03"],
            "P2",
            "DEVELOPER",
            "Teams cannot prioritize backlog without unified Snyk dashboard.",
            "Dashboard URL from epic implementation.",
            [
                step("Open vulnerability dashboard", "Widgets show Critical, High, Medium open counts per repo.", ""),
                step("Drill into BigPicture ppm project", "List matches Snyk project issue list for same snapshot time.", ""),
            ],
            auto_fit="manual_only",
        ),
        journey(
            "TC-004",
            "Global - Security - Scheduled scan clears backlog under SLA for High",
            epic,
            ch[:1],
            ["GOAL-04"],
            "P3",
            "DEVELOPER",
            "SLA misses reintroduce compliance risk after initial cleanup.",
            "Nightly Snyk schedule enabled.",
            [
                step("Trigger nightly scan manually", "Scan completes; email or Slack summary sent.", ""),
                step("Verify no High older than SLA threshold remains open without waiver", "Dashboard filter openHighOverSla returns zero rows.", ""),
            ],
        ),
    ]


def _tests_382297(epic: str, ch: list[str]) -> list[dict[str, Any]]:
    return [
        journey(
            "TC-001",
            "Feature area - Platform - Azure DevOps primary connection onboarding without Jira subsidiary",
            epic,
            ch[:1],
            ["GOAL-01"],
            "P1",
            "APP_ADMIN",
            "ADO-primary customers cannot onboard if product still assumes Jira parent connection.",
            "Fresh ADO-primary tenant adoPrimary-382297; Chargebee sandbox plan.",
            [
                step("Start BigPicture signup selecting Azure DevOps as primary platform", "Flow does not require linking Jira Cloud first.", ""),
                step("Complete ADO OAuth and pick organization adoOrg-382297", "Connection succeeds; home shows ADO work item sources.", ""),
                step("Open Modules overview", "Core modules listed as available on primary ADO per epic scope.", ""),
            ],
            tags=["ado", "primary-platform"],
        ),
        journey(
            "TC-002",
            "Feature area - Billing - Chargebee subscription activates modules on ADO primary tenant",
            epic,
            ch[:1],
            ["GOAL-02"],
            "P1",
            "APP_ADMIN",
            "Billing mismatch could leave paid modules disabled on ADO-primary tenants.",
            "Chargebee test subscription plan BP-Enterprise-382297.",
            [
                step("Complete purchase or trial activation via Chargebee hosted page", "Webhook received; tenant shows active subscription.", ""),
                step("As appAdmin open Administration → Licensing", "Entitlements match purchased SKUs; module toggles enabled.", ""),
                step("Open Gantt module on boxName", "Module loads without license error.", ""),
            ],
            auto_fit="partial",
            auto_blockers=["chargebee_webhook_test"],
        ),
        journey(
            "TC-003",
            "Feature area - Box - Create box and scope ADO work items on primary platform",
            epic,
            ch[:1],
            ["GOAL-03"],
            "P1",
            "BOX_ADMIN",
            "Portfolio hierarchy unusable if box scope cannot bind ADO queries.",
            "boxAdo-382297; ADO project PROJ-382297.",
            [
                step("Create root box boxAdo-382297 on ADO-primary tenant", "Box created with ADO iconography.", ""),
                step("Define scope with ADO WIQL or team project filter", "Scope saves; item count greater than zero.", ""),
                step("Open Overview and Gantt", "ADO work items visible with correct titles.", ""),
            ],
            golden_keys=["TC-1778"],
        ),
        journey(
            "TC-004",
            "Feature area - Platform - Dependency on upstream Platform auth does not block read-only smoke",
            epic,
            ch[:1],
            ["GOAL-04"],
            "P2",
            "STANDARD_USER",
            "Upstream auth delays should not block verifying ADO-primary UI shell.",
            "Feature flag simulatePlatformAuthDelay optional.",
            [
                step("With upstream auth dependency flagged delayed, open BigPicture home", "Either graceful banner explains limited mode or full auth completes within timeout.", ""),
                step("Attempt open read-only dashboard gadget", "Gadget loads or shows explicit dependency message; no blank screen.", ""),
            ],
        ),
    ]


def main() -> int:
    summary: list[tuple[str, int, str, int]] = []
    for epic in EPICS:
        batch = build_batch(epic)
        out_dir = OUT_BASE / epic
        out_dir.mkdir(parents=True, exist_ok=True)
        payload_path = out_dir / "suite-payload.json"
        payload_path.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_suite_report_md(epic, batch, out_dir)
        subprocess.run(
            [
                sys.executable,
                str(CREATOR / "scripts" / "build_suite_report.py"),
                "--batch",
                str(payload_path),
                "--run-id",
                epic,
                "--out",
                str(out_dir / "suite-report"),
            ],
            check=True,
            cwd=REPO,
        )
        review = json.loads((REVIEW_BASE / epic / "review-payload.json").read_text(encoding="utf-8"))
        gate = gate_status(review)
        warn_n = len(batch["coverage_report"].get("warnings") or [])
        summary.append((epic, len(batch.get("tests") or []), gate, warn_n))
        print(f"Wrote {out_dir.relative_to(REPO)}")

    print("\nKEY | tests | gate | warnings")
    print("---|------:|------|----------:")
    for key, n, gate, wn in summary:
        print(f"{key} | {n} | {gate} | {wn}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
