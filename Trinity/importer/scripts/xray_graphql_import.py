#!/usr/bin/env python3
"""Import TestCaseDraft entries into Xray Cloud via GraphQL createTest.

Reads testcase-draft.json batches, maps steps to Xray Manual format, and either
dry-runs (validate + emit payload/report) or executes createTest.

Auth (execute only):
  Xray:  XRAY_CLIENT_ID + XRAY_CLIENT_SECRET (API Keys in Xray Global Settings)
  Jira:  JIRA_EMAIL + JIRA_API_TOKEN (for requirement linking after create)
         https://id.atlassian.com/manage-profile/security/api-tokens
  Never commit credentials.

Usage:
  python3 xray_graphql_import.py \\
    --batch ../artifacts/2026-06-10-tc-one-232514-comprehensive/testcase-draft.json \\
    --draft-id TC-001 \\
    --dry-run

  python3 xray_graphql_import.py --batch ... --draft-id TC-001 --execute \\
    --folder "/Ignite 2026"

Docs: https://docs.getxray.app/display/XRAYCLOUD/GraphQL+API
      https://us.xray.cloud.getxray.app/doc/graphql/createtest.doc.html
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = SCRIPT_DIR.parent / "config" / "mappings" / "appfire-production.json"

CREATE_FOLDER_MUTATION = """
mutation CreateFolder($projectId: String, $path: String!) {
  createFolder(projectId: $projectId, path: $path) {
    folder { name path testsCount }
    warnings
  }
}
""".strip()


def normalize_folder_path(path: str) -> str:
    raw = (path or "").strip()
    if not raw:
        raise ValueError("folder_path is required")
    if not raw.startswith("/"):
        raw = f"/{raw}"
    return raw.rstrip("/") or "/"


def credentials_status() -> dict[str, bool]:
    return {
        "xray_client_id": bool(os.environ.get("XRAY_CLIENT_ID")),
        "xray_client_secret": bool(os.environ.get("XRAY_CLIENT_SECRET")),
        "jira_email": bool(os.environ.get("JIRA_EMAIL")),
        "jira_api_token": bool(os.environ.get("JIRA_API_TOKEN")),
    }


def folder_plan_for_target(
    config: dict[str, Any],
    folder_path: str,
    *,
    create_if_missing: bool,
) -> dict[str, Any]:
    normalized = normalize_folder_path(folder_path)
    project_id = (config.get("project") or {}).get("id")
    plan: dict[str, Any] = {
        "folder_path": normalized,
        "create_folder_if_missing": create_if_missing,
        "action": "use_path_on_create_test",
        "create_folder_mutation": None,
        "warnings": [],
    }
    if create_if_missing:
        plan["action"] = "create_folder_then_create_tests"
        if not project_id:
            plan["warnings"].append(
                "create_folder_if_missing is true but project.id is not set in mapping — "
                "add the numeric Jira project id to the mapping file or create the folder manually."
            )
        else:
            plan["create_folder_mutation"] = {
                "mutation": "createFolder",
                "variables": {"projectId": str(project_id), "path": normalized},
            }
    else:
        plan["warnings"].append(
            "Folder must already exist in the Xray Test Repository; createTest uses folderPath as-is."
        )
    return plan
CREATE_TEST_MUTATION = """
mutation CreateTest(
  $testType: UpdateTestTypeInput!
  $steps: [CreateStepInput!]
  $folderPath: String
  $jira: JSON!
) {
  createTest(
    testType: $testType
    steps: $steps
    folderPath: $folderPath
    jira: $jira
  ) {
    test {
      issueId
      testType { name }
      steps { action data result }
      jira(fields: ["key", "summary"])
    }
    warnings
  }
}
""".strip()

_INSECURE_SSL = False


def ssl_context() -> ssl.SSLContext:
    if _INSECURE_SSL or os.environ.get("XRAY_INSECURE_SSL", "").lower() in ("1", "true", "yes"):
        return ssl._create_unverified_context()
    return ssl.create_default_context()


def urlopen(req: urllib.request.Request, *, timeout: int = 120):
    return urllib.request.urlopen(req, timeout=timeout, context=ssl_context())


REQUIRED_TEST_FIELDS = (
    "title",
    "linked_requirement_keys",
    "steps",
    "coverage_catalog_id",
    "execution_tier",
    "test_pattern",
    "role",
    "customer_impact",
    "test_data_required",
    "test_data_prerequisites",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Mapping config not found: {path}")
    return load_json(path)


_VALID_XRAY_TEST_TYPES = frozenset({"Manual", "Automated", "Generic", "Cucumber"})


def enrich_test_for_import(test: dict[str, Any]) -> dict[str, Any]:
    out = dict(test)
    linked_ac = out.get("linked_ac_ids") or []
    if not out.get("coverage_catalog_id"):
        out["coverage_catalog_id"] = str(linked_ac[0]) if linked_ac else "TRINITY-IMPORT"
    test_type = (out.get("test_type") or "").strip()
    if test_type and test_type not in _VALID_XRAY_TEST_TYPES:
        out["test_type"] = "Manual"
    elif test_type == "Generic":
        out["test_type"] = "Manual"
    return out


def find_test(batch: dict[str, Any], draft_id: str) -> dict[str, Any]:
    for test in batch.get("tests", []):
        if test.get("draft_id") == draft_id:
            return enrich_test_for_import(test)
    available = [t.get("draft_id", t.get("title", "?")) for t in batch.get("tests", [])]
    raise KeyError(f"draft_id {draft_id!r} not found. Available: {', '.join(available[:10])}...")


def map_priority(test: dict[str, Any], config: dict[str, Any]) -> str:
    priority = test.get("priority") or "Medium"
    priority_map = config.get("defaults", {}).get("priority_map", {})
    return priority_map.get(priority, priority)


def build_labels(test: dict[str, Any], config: dict[str, Any]) -> list[str]:
    labels = list(config.get("defaults", {}).get("extra_labels", []))
    for tag in test.get("tags", []):
        if tag not in labels:
            labels.append(tag)
    draft_id = test.get("draft_id")
    if draft_id and draft_id not in labels:
        labels.append(draft_id.lower())
    return labels


def build_description(test: dict[str, Any], batch: dict[str, Any]) -> str:
    parts: list[str] = []
    if test.get("objective"):
        parts.append(test["objective"])
    if test.get("preconditions"):
        parts.append(f"*Preconditions:* {test['preconditions']}")
    if test.get("test_data_prerequisites"):
        parts.append(f"*Pre-test data setup:* {test['test_data_prerequisites']}")
    if test.get("customer_impact"):
        parts.append(f"*Customer impact:* {test['customer_impact']}")
    if test.get("coverage_catalog_id"):
        parts.append(f"*Catalog:* {test['coverage_catalog_id']} ({test.get('execution_tier', '')})")
    if test.get("linked_ac_ids"):
        parts.append(f"*AC/goal ids:* {', '.join(test['linked_ac_ids'])}")
    if test.get("linked_requirement_keys"):
        parts.append(f"*Requirements:* {', '.join(test['linked_requirement_keys'])}")
    if test.get("draft_id"):
        parts.append(f"*Draft id:* {test['draft_id']}")
    if batch.get("run_id"):
        parts.append(f"*Import run:* {batch['run_id']}")
    if test.get("possible_duplicate_of"):
        parts.append(f"*Benchmark / possible duplicate:* {test['possible_duplicate_of']}")
    return "\n\n".join(parts)


def map_steps(test: dict[str, Any]) -> list[dict[str, str]]:
    steps: list[dict[str, str]] = []
    for raw in test.get("steps", []):
        step: dict[str, str] = {
            "action": raw.get("step", "").strip(),
            "result": raw.get("expected_result", "").strip(),
        }
        data = (raw.get("test_data") or "").strip()
        if data:
            step["data"] = data
        steps.append(step)
    return steps


def validate_test(test: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_TEST_FIELDS:
        if field not in test:
            errors.append(f"Missing required field: {field}")
    if not test.get("title", "").strip():
        errors.append("title is empty")
    if not test.get("linked_requirement_keys"):
        errors.append("linked_requirement_keys must be non-empty")
    steps = test.get("steps", [])
    if not steps:
        errors.append("steps must be non-empty")
    pattern = test.get("test_pattern")
    max_steps = 18 if pattern == "journey" else 13
    if len(steps) > max_steps:
        errors.append(f"step count {len(steps)} exceeds max {max_steps} for pattern {pattern}")
    for i, step in enumerate(steps, 1):
        if not step.get("step", "").strip():
            errors.append(f"step {i}: action is empty")
        if not step.get("expected_result", "").strip():
            errors.append(f"step {i}: expected_result is empty")
    return errors


def build_create_variables(
    test: dict[str, Any],
    batch: dict[str, Any],
    config: dict[str, Any],
    *,
    project_key: str,
    folder_path: str,
) -> dict[str, Any]:
    test_type = test.get("test_type") or config.get("defaults", {}).get("test_type", "Manual")
    jira_fields: dict[str, Any] = {
        "summary": test["title"],
        "project": {"key": project_key},
        "priority": {"name": map_priority(test, config)},
        "labels": build_labels(test, config),
        "description": build_description(test, batch),
    }
    required_fields = config.get("defaults", {}).get("jira_required_fields", {})
    for field_id, value in required_fields.items():
        jira_fields[field_id] = value
    return {
        "testType": {"name": test_type},
        "steps": map_steps(test),
        "folderPath": folder_path,
        "jira": {"fields": jira_fields},
    }


def authenticate(config: dict[str, Any]) -> str:
    client_id = os.environ.get("XRAY_CLIENT_ID")
    client_secret = os.environ.get("XRAY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "Set XRAY_CLIENT_ID and XRAY_CLIENT_SECRET environment variables for --execute"
        )
    auth_url = config["xray"]["auth_url"]
    body = json.dumps({"client_id": client_id, "client_secret": client_secret}).encode()
    req = urllib.request.Request(
        auth_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=60) as resp:
        raw = resp.read().decode().strip()
    if not raw:
        raise RuntimeError("Xray authenticate returned empty token")
    try:
        token = json.loads(raw)
    except json.JSONDecodeError:
        token = raw.strip('"')
    if not isinstance(token, str) or not token:
        raise RuntimeError("Xray authenticate returned invalid token payload")
    return token


def requirement_link_endpoints(
    test_key: str,
    requirement_key: str,
    config: dict[str, Any],
) -> tuple[str, str]:
    """Return (inwardIssue, outwardIssue) for Xray Test coverage.

  Desired semantics: Test *tests* requirement; requirement *is tested by* Test.
  Jira createIssueLink convention (same as Blocks): the active/agent issue is
  inwardIssue, the passive/recipient is outwardIssue.
  """
    link_cfg = config.get("requirement_link", {})
    inward_role = link_cfg.get("inward_issue", "test")
    outward_role = link_cfg.get("outward_issue", "requirement")
    roles = {inward_role: test_key, outward_role: requirement_key}
    if "test" not in roles or "requirement" not in roles:
        raise ValueError("requirement_link config must map inward_issue/outward_issue to test and requirement")
    return roles["test"], roles["requirement"]


def build_requirement_link_plan(
    test_key: str,
    requirement_keys: list[str],
    config: dict[str, Any],
) -> list[dict[str, str]]:
    link_type = config.get("requirement_link", {}).get("link_type_name", "Test")
    planned: list[dict[str, str]] = []
    for req_key in requirement_keys:
        inward, outward = requirement_link_endpoints(test_key, req_key, config)
        planned.append({
            "type": link_type,
            "inwardIssue": inward,
            "outwardIssue": outward,
            "description": f"{test_key} tests {req_key}",
        })
    return planned


def jira_delete_issue_link(config: dict[str, Any], link_id: str) -> None:
    email = os.environ.get("JIRA_EMAIL")
    api_token = os.environ.get("JIRA_API_TOKEN")
    if not email or not api_token:
        raise RuntimeError("Set JIRA_EMAIL and JIRA_API_TOKEN to delete issue links")
    site_url = config.get("jira", {}).get("site_url", "https://appfire.atlassian.net").rstrip("/")
    url = f"{site_url}/rest/api/3/issueLink/{link_id}"
    credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Basic {credentials}", "Accept": "application/json"},
        method="DELETE",
    )
    with urlopen(req, timeout=60) as resp:
        if resp.status not in (200, 201, 204):
            raise RuntimeError(f"Unexpected Jira delete status: {resp.status}")


def jira_create_issue_link(
    config: dict[str, Any],
    *,
    link_type: str,
    inward_issue: str,
    outward_issue: str,
) -> None:
    email = os.environ.get("JIRA_EMAIL")
    api_token = os.environ.get("JIRA_API_TOKEN")
    if not email or not api_token:
        raise RuntimeError(
            "Set JIRA_EMAIL and JIRA_API_TOKEN for requirement linking "
            "(or pass --skip-requirement-link)"
        )
    site_url = config.get("jira", {}).get("site_url", "https://appfire.atlassian.net").rstrip("/")
    url = f"{site_url}/rest/api/3/issueLink"
    payload = {
        "type": {"name": link_type},
        "inwardIssue": {"key": inward_issue},
        "outwardIssue": {"key": outward_issue},
    }
    credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {credentials}",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=60) as resp:
            if resp.status not in (200, 201, 204):
                raise RuntimeError(f"Unexpected Jira link status: {resp.status}")
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode(errors="replace")
        if exc.code == 400 and "already exists" in err_body.lower():
            return
        raise RuntimeError(f"Jira issue link failed HTTP {exc.code}: {err_body[:500]}") from exc


def link_requirements(
    test_key: str,
    requirement_keys: list[str],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    link_type = config.get("requirement_link", {}).get("link_type_name", "Test")
    results: list[dict[str, Any]] = []
    for req_key in requirement_keys:
        inward, outward = requirement_link_endpoints(test_key, req_key, config)
        try:
            jira_create_issue_link(
                config,
                link_type=link_type,
                inward_issue=inward,
                outward_issue=outward,
            )
            results.append({
                "requirement_key": req_key,
                "test_key": test_key,
                "link_type": link_type,
                "status": "linked",
            })
        except Exception as exc:  # noqa: BLE001 — collect per-key failures
            results.append({
                "requirement_key": req_key,
                "test_key": test_key,
                "link_type": link_type,
                "status": "failed",
                "error": str(exc),
            })
    return results


def graphql_request(
    config: dict[str, Any],
    token: str,
    query: str,
    variables: dict[str, Any],
) -> dict[str, Any]:
    url = config["xray"]["graphql_url"]
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def write_report(
    out_dir: Path,
    report: dict[str, Any],
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "xray-import-report.json"
    md_path = out_dir / "xray-import-report.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    r = report
    lines = [
        f"# Xray import report — {r['draft_id']}",
        "",
        f"**Mode:** {r['mode']}",
        f"**Started:** {r['started_at']}",
        f"**Completed:** {r['completed_at']}",
        "",
        "## Summary",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Draft id | {r['draft_id']} |",
        f"| Title | {r['title']} |",
        f"| Project | {r['project_key']} |",
        f"| Folder | {r['folder_path']} |",
        f"| Steps | {r['step_count']} |",
        f"| Requirements | {', '.join(r['linked_requirement_keys'])} |",
        f"| Action | {r['action']} |",
    ]
    if r.get("xray_key"):
        lines.append(f"| Xray key | {r['xray_key']} |")
    if r.get("requirement_links"):
        lines.extend(["", "## Requirement links", ""])
        for link in r["requirement_links"]:
            status = link.get("status", "?")
            req = link.get("requirement_key", "?")
            if status == "linked":
                lines.append(f"- {req} ← linked ({link.get('link_type', 'Test')})")
            elif status == "planned":
                lines.append(f"- {req} ← would link ({link.get('link_type', 'Test')})")
            else:
                lines.append(f"- {req} ← {status}: {link.get('error', '')}")
    if r.get("errors"):
        lines.extend(["", "## Errors", ""])
        for err in r["errors"]:
            lines.append(f"- {err}")
    if r.get("warnings"):
        lines.extend(["", "## Warnings", ""])
        for w in r["warnings"]:
            lines.append(f"- {w}")
    if r.get("validation_errors"):
        lines.extend(["", "## Validation errors", ""])
        for err in r["validation_errors"]:
            lines.append(f"- {err}")
    if r.get("mode") == "dry_run":
        lines.extend([
            "",
            "## GraphQL payload",
            "",
            f"Full variables: `{json_path.name}` → `graphql_variables`",
        ])
    else:
        lines.extend([
            "",
            "## GraphQL response",
            "",
            f"See `{json_path.name}` → `graphql_response`",
        ])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import TestCaseDraft to Xray Cloud via GraphQL")
    parser.add_argument("--batch", type=Path, help="Path to testcase-draft.json")
    parser.add_argument("--draft-id", help="draft_id within batch e.g. TC-001")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="jira_xray_mapping.json")
    parser.add_argument("--project", help="Jira project key override (default from config)")
    parser.add_argument("--folder", help="Xray Test Repository folderPath e.g. '/Ignite 2026'")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Report output directory (default: batch parent / xray-import-{draft_id})",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Authenticate and call createTest (default: dry-run only)",
    )
    parser.add_argument(
        "--create-folder",
        action="store_true",
        help="Call createFolder for --folder before createTest (requires project.id in config)",
    )
    parser.add_argument(
        "--skip-requirement-link",
        action="store_true",
        help="Do not link linked_requirement_keys after create",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification (or set XRAY_INSECURE_SSL=1)",
    )
    parser.add_argument(
        "--delete-issue-link",
        help="Delete a Jira issue link by id (requires JIRA_EMAIL + JIRA_API_TOKEN)",
    )
    return parser.parse_args()


def main() -> int:
    global _INSECURE_SSL
    args = parse_args()
    _INSECURE_SSL = args.insecure
    started = datetime.now(timezone.utc).isoformat()

    config = load_config(args.config.resolve())
    if args.delete_issue_link:
        try:
            jira_delete_issue_link(config, args.delete_issue_link)
            print(json.dumps({"status": "deleted", "link_id": args.delete_issue_link}))
            return 0
        except Exception as exc:  # noqa: BLE001 — CLI boundary
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    if not args.batch or not args.draft_id:
        print("Error: --batch and --draft-id are required for import", file=sys.stderr)
        return 1

    batch = load_json(args.batch.resolve())
    test = find_test(batch, args.draft_id)

    project_key = args.project or config["project"]["key"]
    folder_path = args.folder or config["defaults"]["folder_path"]

    validation_errors = validate_test(test)
    variables = build_create_variables(
        test, batch, config, project_key=project_key, folder_path=folder_path
    )

    out_dir = args.output_dir
    if out_dir is None:
        safe_id = re.sub(r"[^\w-]", "_", args.draft_id)
        out_dir = args.batch.resolve().parent / f"xray-import-{safe_id}"

    report: dict[str, Any] = {
        "run_id": batch.get("run_id"),
        "draft_id": args.draft_id,
        "mode": "dry_run" if not args.execute else "execute",
        "started_at": started,
        "completed_at": None,
        "mapping_version": config.get("version"),
        "project_key": project_key,
        "folder_path": folder_path,
        "title": test["title"],
        "step_count": len(variables["steps"]),
        "linked_requirement_keys": test["linked_requirement_keys"],
        "validation_errors": validation_errors,
        "graphql_mutation": CREATE_TEST_MUTATION,
        "graphql_variables": variables,
        "action": "would_create" if not args.execute else "pending",
        "xray_key": None,
        "issue_id": None,
        "errors": [],
        "warnings": [],
        "requirement_links": [],
    }

    placeholder_test_key = f"{project_key}-NEW"
    if not args.skip_requirement_link:
        plan = build_requirement_link_plan(
            placeholder_test_key,
            test["linked_requirement_keys"],
            config,
        )
        report["requirement_links"] = [
            {**link, "status": "planned"} for link in plan
        ]

    if validation_errors:
        report["action"] = "failed_validation"
        report["completed_at"] = datetime.now(timezone.utc).isoformat()
        json_path, md_path = write_report(out_dir, report)
        print(f"Validation failed ({len(validation_errors)} errors). Reports:", file=sys.stderr)
        print(f"  {json_path}", file=sys.stderr)
        print(f"  {md_path}", file=sys.stderr)
        for err in validation_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    if not args.execute:
        report["action"] = "would_create"
        report["warnings"].append(
            "Dry run only — no GraphQL request sent. Re-run with --execute to create the Test."
        )
        if args.skip_requirement_link:
            report["warnings"].append("Requirement linking skipped (--skip-requirement-link).")
        else:
            report["warnings"].append(
                "Requirement links shown as planned; Jira 'Test' link created on --execute."
            )
        if test.get("possible_duplicate_of"):
            report["warnings"].append(
                f"possible_duplicate_of={test['possible_duplicate_of']} — confirm create vs update."
            )
        report["completed_at"] = datetime.now(timezone.utc).isoformat()
        json_path, md_path = write_report(out_dir, report)
        print(json.dumps({
            "status": "dry_run_ok",
            "draft_id": args.draft_id,
            "title": test["title"],
            "project_key": project_key,
            "folder_path": folder_path,
            "step_count": len(variables["steps"]),
            "action": "would_create",
            "report_json": str(json_path),
            "report_md": str(md_path),
        }, indent=2))
        return 0

    # Execute path
    try:
        token = authenticate(config)
        if args.create_folder:
            project_id = (config.get("project") or {}).get("id")
            if not project_id:
                raise RuntimeError("project.id required in mapping for --create-folder")
            norm_folder = normalize_folder_path(folder_path)
            folder_result = graphql_request(
                config,
                token,
                CREATE_FOLDER_MUTATION,
                {"projectId": str(project_id), "path": norm_folder},
            )
            report["create_folder_response"] = folder_result
        result = graphql_request(config, token, CREATE_TEST_MUTATION, variables)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        report["action"] = "failed"
        report["errors"].append(f"HTTP {exc.code}: {body[:500]}")
        report["completed_at"] = datetime.now(timezone.utc).isoformat()
        write_report(out_dir, report)
        print(f"HTTP error: {exc.code}\n{body}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        report["action"] = "failed"
        report["errors"].append(str(exc))
        report["completed_at"] = datetime.now(timezone.utc).isoformat()
        write_report(out_dir, report)
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if result.get("errors"):
        report["action"] = "failed"
        report["errors"] = [e.get("message", str(e)) for e in result["errors"]]
    else:
        data = result.get("data", {}).get("createTest", {})
        test_node = data.get("test") or {}
        jira = test_node.get("jira") or {}
        report["action"] = "created"
        report["xray_key"] = jira.get("key")
        report["issue_id"] = test_node.get("issueId")
        report["warnings"] = list(data.get("warnings") or [])

        if report["xray_key"] and not args.skip_requirement_link:
            link_results = link_requirements(
                report["xray_key"],
                test["linked_requirement_keys"],
                config,
            )
            report["requirement_links"] = link_results
            failed_links = [r for r in link_results if r["status"] != "linked"]
            if failed_links:
                report["action"] = "created_link_failed"
                for item in failed_links:
                    report["errors"].append(
                        f"Link {item['test_key']} → {item['requirement_key']}: {item.get('error')}"
                    )

    report["graphql_response"] = result
    report["completed_at"] = datetime.now(timezone.utc).isoformat()
    json_path, md_path = write_report(out_dir, report)
    print(json.dumps({
        "status": report["action"],
        "xray_key": report.get("xray_key"),
        "requirement_links": report.get("requirement_links"),
        "report_json": str(json_path),
        "report_md": str(md_path),
    }, indent=2))
    return 0 if report["action"] in ("created",) else 1


if __name__ == "__main__":
    sys.exit(main())
