#!/usr/bin/env python3
"""Build IQ-12 neutral golden corpus (v2 layout, product-agnostic journeys)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "Trinity/creator/golden/v2/neutral-manual-journeys"

TESTS = [
    {
        "key": "TC-99001",
        "summary": "Admin journey — create Select custom field and verify in entity form",
        "folder": "/Neutral/Admin - Custom fields",
        "steps": [
            ("Navigate to **Settings → Custom fields** as product admin", "", "Custom fields page opens with list or empty state"),
            ("Click **Add custom field**", "", "Create form opens"),
            ("Enter **Name** and choose **Select** type with two options", "Name: Work Area; options: A, B", "Values editor accepts options"),
            ("Save the field", "", "Success message; field appears in admin list"),
            ("Open **Create entity** flow for a supported record type", "", "Create modal shows the new field"),
            ("Set the Select value and submit", "Value: A", "Record is created; field value visible on detail view"),
        ],
    },
    {
        "key": "TC-99002",
        "summary": "Journey — Text custom field visible across parent and child records",
        "folder": "/Neutral/Journey - Field propagation",
        "steps": [
            ("Ensure a Text custom field exists for the workspace", "fieldName: Journey Text", "Field listed as active"),
            ("Create parent record with Text value", "value: Parent-1", "Parent saved; Text shown in panel"),
            ("Create child record under parent", "", "Child create form shows Text default Not set"),
            ("Set Text on child and save", "value: Child-1", "Child visible; Text correct in tree and panel"),
            ("Open parent detail **Info** section", "", "Parent Text value unchanged and correct"),
        ],
    },
    {
        "key": "TC-99003",
        "summary": "Admin exports configuration list to spreadsheet for audit",
        "folder": "/Neutral/Admin - Export",
        "steps": [
            ("Navigate to admin configuration list", "", "Table of configurable items is displayed"),
            ("Apply optional filter to a known subset", "filter: Active only", "Filtered rows match criteria"),
            ("Click **Export** and choose spreadsheet format", "", "Download starts"),
            ("Open file and verify headers and row count", "", "Columns match UI; row count matches filtered list"),
        ],
    },
    {
        "key": "TC-99004",
        "summary": "Standard user cannot access admin-only settings",
        "folder": "/Neutral/Security - Permissions",
        "steps": [
            ("Log in as user without admin role", "role: Standard user", "Home loads successfully"),
            ("Attempt direct URL to admin settings", "", "Access denied or redirect per product policy"),
            ("Confirm admin navigation entry is hidden", "", "No admin settings link in primary navigation"),
        ],
    },
    {
        "key": "TC-99005",
        "summary": "Feature flag off hides capability from navigation and API",
        "folder": "/Neutral/Feature flags",
        "steps": [
            ("Disable target feature flag in staging", "flag: example.feature.enabled = off", "Flag saved"),
            ("Refresh application as standard user", "", "Capability menu entry is not shown"),
            ("Enable flag and refresh", "flag: on", "Capability entry appears"),
            ("Smoke-check primary action once enabled", "", "Happy path loads without error"),
        ],
    },
]


def step_objects(pairs: list[tuple[str, str, str]]) -> list[dict]:
    out = []
    for i, (action, data, result) in enumerate(pairs, start=1):
        out.append({"step": i, "action": action, "data": data, "result": result})
    return out


def rag_text(key: str, summary: str, folder: str, steps: list[dict]) -> str:
    lines = [
        f"Test: {key} — {summary}",
        "Priority: High | Status: Reference | Type: Manual",
        f"Folder: {folder}",
        "Labels: neutral-golden, journey",
        "",
        "Steps:",
    ]
    for s in steps:
        lines.append(f"{s['step']}. {s['action']}")
        if s.get("data"):
            lines.append(f"   Data: {s['data']}")
        lines.append(f"   Expected: {s['result']}")
    return "\n".join(lines)


def main() -> None:
    extracted_at = datetime.now(timezone.utc).isoformat()
    rag_dir = OUT / "rag" / "by-key"
    rag_dir.mkdir(parents=True, exist_ok=True)

    tests_out = []
    for spec in TESTS:
        steps = step_objects(spec["steps"])
        test = {
            "key": spec["key"],
            "issue_id": spec["key"].replace("TC-", ""),
            "url": f"https://example.invalid/browse/{spec['key']}",
            "summary": spec["summary"],
            "description": "Synthetic neutral golden reference (IQ-12). Not a live Xray issue.",
            "status": "Reference",
            "priority": "High",
            "assignee": "",
            "reporter": "Trinity Creator",
            "created": extracted_at,
            "updated": extracted_at,
            "labels": ["neutral-golden", "journey"],
            "test_type": "Manual",
            "folder": spec["folder"],
            "unstructured": "",
            "gherkin": "",
            "steps": steps,
            "preconditions": [],
            "coverable_issues": [],
            "step_count": len(steps),
        }
        tests_out.append(test)
        text = rag_text(spec["key"], spec["summary"], spec["folder"], steps)
        payload = {
            "test": test,
            "rag": {
                "id": spec["key"],
                "text": text,
                "metadata": {
                    "jira_key": spec["key"],
                    "issue_id": test["issue_id"],
                    "summary": spec["summary"],
                    "priority": "High",
                    "status": "Reference",
                    "test_type": "Manual",
                    "folder": spec["folder"],
                    "labels": test["labels"],
                    "step_count": len(steps),
                    "filter_id": "neutral",
                    "filter_name": "Neutral manual journeys",
                    "source": "trinity_neutral_golden_builder",
                },
            },
        }
        (rag_dir / f"{spec['key']}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    manifest = {
        "corpus_id": "neutral-manual-journeys",
        "title": "Neutral manual journeys (product-agnostic)",
        "reference_jira_project": "TC",
        "product_lines": ["default", "requirements", "spm"],
        "run_id": "trinity-neutral-golden-v1",
        "extracted_at": extracted_at,
        "source": "Trinity IQ-12 builder (synthetic references)",
        "test_count": len(tests_out),
        "total_steps": sum(t["step_count"] for t in tests_out),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    extraction = {
        "extracted_at": extracted_at,
        "source": manifest["source"],
        "filter": {
            "filter_id": "neutral",
            "filter_name": manifest["title"],
            "filter_jql": "corpus=neutral-manual-journeys",
            "run_id": manifest["run_id"],
            "extracted_at": extracted_at,
        },
        "test_count": len(tests_out),
        "tests": tests_out,
    }
    (OUT / "extraction.json").write_text(
        json.dumps(extraction, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    md_lines = [
        "# Neutral manual journeys (synthetic golden)",
        "",
        f"**Run ID:** `{manifest['run_id']}`  ",
        f"**Tests:** {len(tests_out)}  ",
        "",
        "## Test index",
        "",
        "| # | Title | Priority | Steps | Key |",
        "|---|-------|----------|-------|-----|",
    ]
    for i, t in enumerate(tests_out, start=1):
        md_lines.append(
            f"| {i} | {t['summary']} | High | {t['step_count']} | {t['key']} |"
        )
    (OUT / "extraction.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(tests_out)} tests)")


if __name__ == "__main__":
    main()
