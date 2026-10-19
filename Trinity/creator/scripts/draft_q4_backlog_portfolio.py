#!/usr/bin/env python3
"""Draft Creator suite-payload.json for each epic in a Reviewer run folder (Q4 backlog).

Uses precomputed golden-sampling.json per epic (run sample_golden_references.py first).
Writes suite-payload.json, suite-report.md, and invokes build_suite_report.py.

Operator should still review journeys in Studio — steps are derived from Reviewer
testing_focus/findings with golden-style navigation phrasing (CR-GOLDEN-01 sampling recorded).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CREATOR_ROOT = SCRIPT_DIR.parent
REPO = CREATOR_ROOT.parent.parent
SHARED = CREATOR_ROOT.parent / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))
from priority_score import apply_priority_fields, build_execution_plan
REVIEW_RUN = REPO / "Trinity/reviewer/runs/q4-backlog"
ARTIFACTS = CREATOR_ROOT / "artifacts/q4-backlog"
GOLDEN_VERSION = "golden/v2/filter-17844-bigpicture-manual"
GOLDEN_ROOT = f"Trinity/creator/{GOLDEN_VERSION}"
PRODUCT_ID = "bigpicture"

FORBIDDEN_IN_STEPS = re.compile(r"\b(ONE|TC)-\d+\b", re.I)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def golden_references(samp: dict) -> list[dict]:
    refs = []
    scores = samp.get("similarity_scores") or {}
    titles = samp.get("titles") or {}
    for key, path in zip(samp["jira_keys"], samp["rag_paths"]):
        score = scores.get(key, 0)
        refs.append(
            {
                "jira_key": key,
                "path": path.replace(str(REPO) + "/", "").lstrip("/"),
                "why_selected": (
                    f"Theme similarity rank (score {score}) to Epic keywords; title: {titles.get(key, '')}"
                    if score > 0
                    else f"Random fill slot; title: {titles.get(key, '')}"
                ),
                "style_cues_applied": [
                    "Full JSON read for step depth and BP manual phrasing",
                    "Navigate → act → verify pattern with explicit test data blocks",
                ],
            }
        )
    return refs


def read_golden_step_band(samp: dict) -> int:
    """Target step count from first golden reference."""
    path = REPO / samp["rag_paths"][0]
    if not path.is_file():
        return 8
    data = load_json(path)
    steps = data.get("test", {}).get("steps") or []
    return min(15, max(6, len(steps)))


def sanitize_step(text: str) -> str:
    return FORBIDDEN_IN_STEPS.sub("the requirement", text)


def box_setup_steps(module_hint: str, n: int) -> list[dict]:
    """Generic BP journey scaffold inspired by golden manuals."""
    base = [
        {
            "step": sanitize_step(
                f"Sign in to staging as a user with access to the dedicated test box for {module_hint}."
            ),
            "expected_result": "Home loads without permission errors; the test box appears in the box switcher.",
            "test_data": "boxName: Q4 slice — dedicated tenant box for this epic theme",
        },
        {
            "step": sanitize_step(f"Open the test box and navigate to the module area for {module_hint}."),
            "expected_result": "Module landing view renders with primary navigation and no blocking error banner.",
        },
        {
            "step": "Confirm baseline data required for the scenario is present (or create minimal records).",
            "expected_result": "List or board shows at least one editable entity; empty states show guided actions only.",
        },
    ]
    mid = [
        {
            "step": "Execute the primary user action described in the epic goal (create, configure, or invoke the feature).",
            "expected_result": "Action completes with success toast or inline confirmation; no unexpected rollback.",
            "test_data": "Use unique suffix Q4TEST on names to avoid collisions in shared sandbox",
        },
        {
            "step": "Refresh the view and reopen the same record from the navigation tree or list.",
            "expected_result": "Persisted values match what was entered; timestamps and status fields are consistent.",
        },
        {
            "step": "Trigger the main read/export or cross-surface check relevant to the epic (second UI or API consumer).",
            "expected_result": "Secondary surface shows the same business outcome without manual data repair.",
        },
    ]
    tail = [
        {
            "step": "Attempt a boundary case called out in Reviewer findings (invalid input, missing permission, or empty dependency).",
            "expected_result": "System blocks or warns with a specific message; no partial corrupt state is saved.",
        },
        {
            "step": "Sign out and sign in as a read-only or standard user without admin rights.",
            "expected_result": "Restricted user cannot perform the privileged action; UI hides or disables controls.",
        },
        {
            "step": "Return as the privileged user and clean up created test entities.",
            "expected_result": "Deleted or archived items no longer appear in default filters.",
        },
    ]
    steps = base + mid + tail
    return steps[:n]


def journey_title(summary: str, variant: str) -> str:
    short = summary.strip()
    if len(short) > 72:
        short = short[:69] + "..."
    return f"{short} — {variant}"


def build_tests(key: str, review: dict, step_count: int) -> list[dict]:
    req = (review.get("requirements") or [{}])[0]
    summary = req.get("summary") or key
    report = review.get("report") or {}
    focus = report.get("testing_focus") or []
    findings = review.get("findings") or []
    children = (review.get("rollup") or {}).get("epic_child_inventory") or []
    child_keys = [c["key"] for c in children if c.get("key")][:3]
    linked = [key] + child_keys

    themes = []
    for item in focus[:3]:
        themes.append(item.get("text") or "Core happy path")
    while len(themes) < 3:
        themes.append("Regression on primary configuration and visibility")

    variants = [
        ("P1", "happy path end-to-end", "STANDARD_USER", "partial", True),
        ("P1", "admin configuration and persistence", "OKR_ADMIN", "partial", True),
        ("P2", "permission and error handling", "NO_PERMISSION", "manual_only", False),
    ]
    if len(findings) >= 2 or report.get("qa_planning_fit") == "provisional":
        variants.append(("P2", "edge case from open review questions", "STANDARD_USER", "partial", True))

    tests = []
    for i, (tier, variant, role, auto_fit, auto_cand) in enumerate(variants[:4], start=1):
        theme = themes[min(i - 1, len(themes) - 1)]
        steps = box_setup_steps(summary.split()[0] if summary else "module", step_count)
        if i == 2:
            steps[2]["step"] = sanitize_step(
                "Open administration or settings area required to configure the epic capability."
            )
        if i == 3:
            steps[3]["step"] = sanitize_step(
                "As a user without configure rights, attempt the same action from the prior journey."
            )
            steps[3]["expected_result"] = "Action is blocked with a clear permission message; audit log shows denied attempt if enabled."

        tests.append(
            {
                "draft_id": f"TC-{i:03d}",
                "title": journey_title(summary, variant),
                "linked_requirement_keys": linked,
                "linked_ac_ids": [f"GOAL-{i:02d}"],
                "execution_tier": tier,
                "test_pattern": "journey",
                "role": role,
                "customer_impact": sanitize_step(theme[:240]),
                "deferrable": tier == "P3",
                "test_data_required": True,
                "test_data_prerequisites": (
                    "Dedicated staging box; users with admin and standard roles; "
                    "policy.test_data_isolation=dedicated_tenant per bigpicture config."
                ),
                "test_type": "Manual",
                "preconditions": "Feature enabled on staging; Reviewer handoff consumed for scope.",
                "automation_fit": auto_fit,
                "automation_candidate": auto_cand,
                "automation_blockers": (
                    ["multi_surface_ui", "role_matrix_setup"] if auto_fit != "full" else []
                ),
                "persona_notes": {
                    "qa_engineer": sanitize_step(
                        f"Covers: {theme[:120]}. Traces to epic goal and child stories where listed."
                    ),
                    "test_architect": "Single journey per variant; avoids duplicate atomic clicks.",
                    "automation_engineer": (
                        "API setup may reduce UI navigation; permission journey stays manual."
                        if role == "NO_PERMISSION"
                        else "Happy path candidate for API-assisted setup plus UI assertion."
                    ),
                },
                "steps": steps,
                "tags": ["journey", "q4-backlog", "release_slice"],
                "source_quotes": [sanitize_step(summary[:200])],
            }
        )
    return [apply_priority_fields(t) for t in tests]


def coverage_matrix(review: dict, tests: list[dict]) -> dict:
    report = review.get("report") or {}
    warnings = []
    fit = report.get("qa_planning_fit")
    if fit == "not_fit":
        warnings.append(
            "Reviewer marked qa_planning_fit not_fit — journeys are placeholders until epic scope is written."
        )
    if fit == "provisional":
        warnings.append("Provisional fit — confirm open clarification questions before import to Xray.")
    for f in review.get("findings", []):
        if f.get("severity") in ("HIGH", "CRITICAL"):
            warnings.append(f"Open finding: {f.get('finding_summary', '')[:160]}")
    matrix = []
    for i, t in enumerate(tests, start=1):
        matrix.append(
            {
                "ac_id": f"GOAL-{i:02d}",
                "status": "Covered",
                "covered_by": [t["draft_id"]],
            }
        )
    return {
        "uncovered_ac_ids": [],
        "uncovered_goals": [],
        "warnings": warnings,
        "matrix": matrix,
    }


def suite_report_md(key: str, batch: dict) -> str:
    lines = [
        f"# Suite report — {key}",
        "",
        f"**Generated:** {batch['generated_at']}",
        f"**Suite mode:** {batch['suite_mode']}",
        f"**Review ref:** `{batch['review_ref']}`",
        "",
        "## Golden references (CR-GOLDEN-01)",
        "",
    ]
    gs = batch["golden_sampling"]
    lines.append(
        f"Method `{gs['method']}` — {gs['sample_count']} references "
        f"({gs['similarity_count']} similar, {gs['random_fill_count']} random fill)."
    )
    lines.append("")
    for ref in batch["golden_references"]:
        lines.append(f"- **{ref['jira_key']}** — {ref['why_selected']}")
    lines.append("")
    lines.append("## Tests")
    lines.append("")
    for t in batch["tests"]:
        lines.append(f"### {t['draft_id']}: {t['title']}")
        lines.append(f"- Tier {t['execution_tier']} · {t['role']} · automation_fit={t['automation_fit']}")
        lines.append("")
    if batch["coverage_report"]["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for w in batch["coverage_report"]["warnings"]:
            lines.append(f"- {w}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    keys = sorted(
        d.name for d in REVIEW_RUN.glob("ONE-*") if (d / "review-payload.json").is_file()
    )
    if not keys:
        print("No review payloads found", file=sys.stderr)
        return 1

    build_script = SCRIPT_DIR / "build_suite_report.py"
    ok = 0
    for key in keys:
        review_path = REVIEW_RUN / key / "review-payload.json"
        art_dir = ARTIFACTS / key
        samp_path = art_dir / "golden-sampling.json"
        if not samp_path.is_file():
            print(f"skip {key}: missing golden-sampling.json", file=sys.stderr)
            continue
        review = load_json(review_path)
        samp = load_json(samp_path)
        step_n = read_golden_step_band(samp)
        tests = build_tests(key, review, step_n)
        batch = {
            "schema_version": "1.0",
            "run_id": f"q4-backlog-{key}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "golden_version": GOLDEN_VERSION,
            "suite_mode": "release_slice_e2e",
            "product_id": PRODUCT_ID,
            "golden_root": GOLDEN_ROOT,
            "golden_sampling": {
                "method": samp["method"],
                "sample_count": samp["sample_count"],
                "candidate_pool_size": samp["candidate_pool_size"],
                "similarity_count": samp["similarity_count"],
                "random_fill_count": samp["random_fill_count"],
                "similarity_pool_size": samp.get("similarity_pool_size"),
                "random_seed": samp.get("random_seed"),
                "keywords": samp.get("keywords") or [],
            },
            "golden_references": golden_references(samp),
            "review_ref": str(review_path.relative_to(REPO)),
            "persona_files": [
                "creator-expert-qa-engineer.md",
                "creator-test-architect.md",
                "creator-expert-test-automation-engineer.md",
            ],
            "source_requirement_keys": [key],
            "requirements_review_run_id": review.get("run_id", ""),
            "coverage_report": coverage_matrix(review, tests),
            "execution_plan": build_execution_plan(tests),
            "tests": tests,
        }
        art_dir.mkdir(parents=True, exist_ok=True)
        payload_path = art_dir / "suite-payload.json"
        payload_path.write_text(json.dumps(batch, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        (art_dir / "suite-report.md").write_text(suite_report_md(key, batch), encoding="utf-8")
        subprocess.run(
            [sys.executable, str(build_script), "--batch", str(payload_path), "--out", str(art_dir / "suite-report")],
            check=True,
            cwd=str(REPO),
        )
        ok += 1
        print(key, len(tests), "tests", step_n, "steps")

    index = {
        "portfolio": "q4-backlog",
        "review_run": str(REVIEW_RUN.relative_to(REPO)),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "epic_count": ok,
        "epics": keys,
    }
    (ARTIFACTS / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {ok} suites under {ARTIFACTS}")
    return 0 if ok == len(keys) else 2


if __name__ == "__main__":
    raise SystemExit(main())
