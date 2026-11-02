#!/usr/bin/env python3
"""Gather BigPicture Cloud release stats for one or more trains.

Reads Jira and Xray credentials from Trinity/studio/.env (or the environment).
Writes one JSON file per version under Release Process/stats/data/.
Does not print secrets. Read-only against Jira and Xray.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = ROOT / "Trinity" / "studio" / ".env"
PRODUCTION_ENV_PATH = ROOT / "Trinity" / "studio" / ".env.production"
MCP_AUTH_DIR = Path.home() / ".mcp-auth" / "mcp-remote-v1"
DATA_DIR = ROOT / "Release Process" / "stats" / "data"
SITE_DEFAULT = "https://appfire.atlassian.net"
XRAY_AUTH = "https://xray.cloud.getxray.app/api/v2/authenticate"
XRAY_GRAPHQL = "https://xray.cloud.getxray.app/api/v2/graphql"
PROJECT_VERSIONS = "ONE"
PROJECT_TESTS = "TC"

PASSED = {"PASSED", "PASS", "OK"}
FAILED = {"FAILED", "FAIL"}
TODO = {"TODO", "TO DO"}
EXECUTING = {"EXECUTING"}
SKIPPED = {"ABORTED", "SKIPPED", "N/A", "NA", "NOT APPLICABLE"}

TESTS_QUERY = """
query ReleaseTestExecution($issueId: String!, $start: Int!, $limit: Int!) {
  getTestExecution(issueId: $issueId) {
    issueId
    testRuns(start: $start, limit: $limit) {
      total
      results {
        finishedOn
        startedOn
        executedById
        status { name }
        test { issueId }
      }
    }
  }
}
"""

TESTS_QUERY_WITH_JIRA = """
query ReleaseTestExecution($issueId: String!, $start: Int!, $limit: Int!) {
  getTestExecution(issueId: $issueId) {
    issueId
    testRuns(start: $start, limit: $limit) {
      total
      results {
        finishedOn
        startedOn
        status { name }
        test { issueId jira(fields: ["key", "summary"]) }
      }
    }
  }
}
"""

EXECUTION_TEST_RUNS_QUERY = """
query ExecutionTestRuns($issueId: String!, $start: Int!, $limit: Int!) {
  getTestExecution(issueId: $issueId) {
    testRuns(start: $start, limit: $limit) {
      total
      results {
        activity(limit: 100) {
          results { field date }
        }
      }
    }
  }
}
"""

STATUS_ACTIVITY_FIELD = "status"


def load_env(path: Path, *, override: set[str] | None = None) -> None:
    if not path.is_file():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key or not value:
            continue
        if override is not None:
            if key in override:
                os.environ[key] = value
            continue
        if key not in os.environ:
            os.environ[key] = value


def ssl_context() -> ssl.SSLContext:
    """Trust public CAs plus the Netskope CA from the macOS system keychain.

    This Python build does not use the macOS keychain. Appfire's proxy
    (Netskope) intercepts some hosts, and its CA has no keyUsage extension,
    which Python 3.13's strict mode rejects. The chain is still checked.
    """
    try:
        import certifi

        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    strict = getattr(ssl, "VERIFY_X509_STRICT", 0)
    if strict:
        ctx.verify_flags &= ~strict
    keychain = Path("/Library/Keychains/System.keychain")
    if sys.platform == "darwin" and keychain.is_file():
        proc = subprocess.run(
            ["security", "find-certificate", "-a", "-c", "goskope", "-p", str(keychain)],
            capture_output=True,
            text=True,
            check=False,
        )
        if "BEGIN CERTIFICATE" in proc.stdout:
            ctx.load_verify_locations(cadata=proc.stdout)
    return ctx


CTX = ssl_context()


def request_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    timeout: int = 60,
) -> Any:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        hint = ""
        if exc.code == 404 and "/project/ONE/" in url:
            hint = " The Jira account in Trinity/studio/.env cannot see project ONE on production."
        raise RuntimeError(f"HTTP {exc.code} {method} {url.split('?')[0]}: {detail}{hint}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{method} {url.split('?')[0]} failed: {exc.reason}") from exc
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw.strip().strip('"')


def jira_bearer_token() -> str | None:
    if not MCP_AUTH_DIR.is_dir():
        return None
    for path in sorted(MCP_AUTH_DIR.glob("*_tokens.json")):
        token = json.loads(path.read_text()).get("access_token")
        if token:
            return token
    return None


def jira_headers() -> dict[str, str]:
    bearer = jira_bearer_token()
    if bearer:
        return {
            "Authorization": f"Bearer {bearer}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    email = os.environ.get("JIRA_EMAIL")
    token = os.environ.get("JIRA_API_TOKEN")
    if not email or not token:
        raise RuntimeError(
            "Set JIRA_EMAIL and JIRA_API_TOKEN (Trinity/studio/.env) or sign in to Atlassian MCP OAuth"
        )
    basic = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {
        "Authorization": f"Basic {basic}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def site_url() -> str:
    # Release stats are for production. Trinity/studio/.env often points at the sandbox.
    return SITE_DEFAULT


def jira_get(path: str, params: dict[str, Any] | None = None) -> Any:
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    return request_json(site_url() + path + query, headers=jira_headers())


def jira_search(jql: str, fields: list[str]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    token: str | None = None
    while True:
        body: dict[str, Any] = {"jql": jql, "maxResults": 100, "fields": fields}
        if token:
            body["nextPageToken"] = token
        payload = request_json(
            site_url() + "/rest/api/3/search/jql",
            method="POST",
            headers=jira_headers(),
            body=body,
        )
        issues.extend(payload.get("issues") or [])
        if payload.get("isLast", True):
            return issues
        token = payload.get("nextPageToken")
        if not token:
            return issues


def list_versions(version: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    start = 0
    while True:
        page = jira_get(
            f"/rest/api/3/project/{PROJECT_VERSIONS}/version",
            {"query": version, "maxResults": 50, "startAt": start, "orderBy": "name"},
        )
        found.extend(page.get("values") or [])
        start += page.get("maxResults") or 50
        if page.get("isLast", True) or start >= (page.get("total") or 0):
            return found


def list_all_preprod_versions() -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    start = 0
    while True:
        page = jira_get(
            f"/rest/api/3/project/{PROJECT_VERSIONS}/version",
            {"query": "preprod/", "maxResults": 100, "startAt": start, "orderBy": "name"},
        )
        found.extend(page.get("values") or [])
        start += page.get("maxResults") or 100
        if page.get("isLast", True) or start >= (page.get("total") or 0):
            return found


def discover_trains_since(since: date) -> list[str]:
    """Cloud trains with preprod/YYYY-MM-DD/{version} cut-off on or after `since`."""
    trains: dict[str, date] = {}
    for item in list_all_preprod_versions():
        name = item.get("name") or ""
        match = re.fullmatch(r"preprod/(\d{4}-\d{2}-\d{2})/(\d+\.\d+)", name)
        if not match:
            continue
        cutoff = date.fromisoformat(match.group(1))
        if cutoff < since:
            continue
        version = match.group(2)
        if version not in trains or cutoff > trains[version]:
            trains[version] = cutoff
    return sorted(trains.keys(), key=lambda value: [int(part) for part in value.split(".")])


def jira_user_display_names(account_ids: set[str]) -> dict[str, str]:
    names: dict[str, str] = {}
    for account_id in sorted(account_ids):
        try:
            payload = jira_get("/rest/api/3/user", {"accountId": account_id})
        except RuntimeError:
            continue
        if isinstance(payload, dict):
            names[account_id] = payload.get("displayName") or payload.get("emailAddress") or account_id
    return names


def parse_preprod(name: str, version: str) -> str | None:
    match = re.fullmatch(rf"preprod/(\d{{4}}-\d{{2}}-\d{{2}})/{re.escape(version)}", name)
    return match.group(1) if match else None


def cloud_name(version: str) -> re.Pattern[str]:
    return re.compile(rf"^bigpicture-cloud-{re.escape(version)}\.")


def version_token(version: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![\d.]){re.escape(version)}(?![\d.])")


def xray_token() -> str:
    client_id = os.environ.get("XRAY_CLIENT_ID")
    client_secret = os.environ.get("XRAY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "Set XRAY_CLIENT_ID and XRAY_CLIENT_SECRET for appfire.atlassian.net "
            "in Trinity/studio/.env.production"
        )
    token = request_json(
        XRAY_AUTH,
        method="POST",
        headers={"Content-Type": "application/json"},
        body={"client_id": client_id, "client_secret": client_secret},
    )
    if not isinstance(token, str) or not token:
        raise RuntimeError("Xray authenticate returned an empty token")
    return token


def xray_issue_id(token: str, issue_key: str) -> str:
    """Xray getTestExecution accepts the numeric Jira id, not the issue key."""
    if issue_key.isdigit():
        return issue_key
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = request_json(
        XRAY_GRAPHQL,
        method="POST",
        headers=headers,
        body={
            "query": "query($jql: String!) { getTestExecutions(jql: $jql, limit: 1) { results { issueId } } }",
            "variables": {"jql": f"key = {issue_key}"},
        },
    )
    if payload.get("errors"):
        message = "; ".join(err.get("message", "") for err in payload["errors"])
        raise RuntimeError(f"Xray could not resolve {issue_key}: {message}")
    results = ((payload.get("data") or {}).get("getTestExecutions") or {}).get("results") or []
    issue_id = (results[0] or {}).get("issueId") if results else None
    if not issue_id:
        raise RuntimeError(f"Xray has no test execution {issue_key}")
    return str(issue_id)


def xray_latest_run_statuses(
    token: str,
    issue_id: str,
) -> tuple[dict[str, str], int, set[str]]:
    """Latest test-run status per test; distinct test executors (executedById)."""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    latest: dict[str, tuple[datetime | None, str]] = {}
    executor_ids: set[str] = set()
    start = 0
    runs_total = 0
    while True:
        payload = request_json(
            XRAY_GRAPHQL,
            method="POST",
            headers=headers,
            body={
                "query": TESTS_QUERY,
                "variables": {"issueId": issue_id, "start": start, "limit": 100},
            },
            timeout=120,
        )
        if payload.get("errors"):
            message = "; ".join(err.get("message", "") for err in payload["errors"])
            raise RuntimeError(f"Xray GraphQL testRuns for {issue_id}: {message}")
        execution = (payload.get("data") or {}).get("getTestExecution")
        if not execution or not execution.get("testRuns"):
            raise RuntimeError(f"Xray returned no test runs for execution {issue_id}")
        block = execution["testRuns"]
        runs_total = int(block.get("total") or 0)
        results = block.get("results") or []
        if not results:
            break
        for run in results:
            if not run:
                continue
            executed_by = run.get("executedById")
            if executed_by:
                executor_ids.add(str(executed_by))
            test_id = str((run.get("test") or {}).get("issueId") or id(run))
            finished = parse_instant(run.get("finishedOn") or run.get("startedOn"))
            name = ((run.get("status") or {}).get("name") or "UNKNOWN").strip()
            prev = latest.get(test_id)
            if prev is None or (finished and (prev[0] is None or finished >= prev[0])):
                latest[test_id] = (finished, name)
        start += len(results)
        if start >= runs_total:
            break
    return {test_id: status for test_id, (_, status) in latest.items()}, runs_total, executor_ids


def xray_qa_engineers(token: str, issue_id: str, executor_ids: set[str]) -> dict[str, Any]:
    names_map = jira_user_display_names(executor_ids)
    ordered_ids = sorted(executor_ids)
    return {
        "count": len(executor_ids),
        "account_ids": ordered_ids,
        "names": [names_map.get(account_id, account_id) for account_id in ordered_ids],
        "source": "getTestExecution.testRuns executedById (distinct)",
    }


def xray_counts(token: str, issue_key: str, execution_created: str | None = None) -> dict[str, Any]:
    issue_id = xray_issue_id(token, issue_key)
    latest_statuses, runs_total, executor_ids = xray_latest_run_statuses(token, issue_id)
    counts = {"passed": 0, "failed": 0, "skipped": 0, "todo": 0, "executing": 0, "other": 0}
    by_status: dict[str, int] = {}
    for name in latest_statuses.values():
        key = name.upper()
        by_status[name] = by_status.get(name, 0) + 1
        if key in PASSED:
            counts["passed"] += 1
        elif key in FAILED:
            counts["failed"] += 1
        elif key in TODO:
            counts["todo"] += 1
        elif key in EXECUTING:
            counts["executing"] += 1
        elif key in SKIPPED:
            counts["skipped"] += 1
        else:
            counts["other"] += 1
    total = len(latest_statuses) or runs_total
    executed = counts["passed"] + counts["failed"] + counts["skipped"] + counts["other"]
    first_status, last_status = xray_execution_status_bounds(token, issue_id)
    timing: dict[str, Any] = {
        "execution_created": execution_created,
        "first_status_change": first_status.isoformat() if first_status else None,
        "last_status_change": last_status.isoformat() if last_status else None,
        "duration_days": weekday_span_days(first_status, last_status),
        "duration_kind": "weekdays",
        "source": "xray_execution_test_runs",
        "rule": (
            "Weekdays only (Mon–Fri), from the first to the last status change on any "
            "test in this Test Execution (getTestExecution.testRuns activity, field status). "
            "Same calendar day counts as 0."
        ),
    }
    return {
        "total": total,
        "executed": executed,
        "passed": counts["passed"],
        "failed": counts["failed"],
        "skipped": counts["skipped"],
        "todo": counts["todo"],
        "executing": counts["executing"],
        "other": counts["other"],
        "by_status": by_status,
        "status_buckets": {
            "passed": sorted(PASSED),
            "failed": sorted(FAILED),
            "skipped": sorted(SKIPPED),
            "todo": sorted(TODO),
            "executing": sorted(EXECUTING),
            "other": "any remaining status name",
        },
        "counts_source": "getTestExecution.testRuns latest status per test",
        "qa_engineers": xray_qa_engineers(token, issue_id, executor_ids),
        "timing": timing,
    }


def defect_keys(issue: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    for link in (issue.get("fields") or {}).get("issuelinks") or []:
        if (link.get("type") or {}).get("name") != "Defect":
            continue
        outward = link.get("outwardIssue") or {}
        key = outward.get("key")
        if key:
            keys.append(key)
    return keys


def browse(key: str) -> str:
    return f"{site_url()}/browse/{key}"


def xray_testing_board_url(execution_key: str, test_key: str) -> str:
    """Xray Testing Board deep link to one test run inside a Test Execution."""
    base = f"{site_url()}/projects/{PROJECT_TESTS}"
    plugin = "com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board"
    qs = (
        f"selectedItem={plugin}"
        f"&ac.testExecutionKey={execution_key}&ac.testKey={test_key}"
    )
    frag = f"#!page=test-run&testExecutionKey={execution_key}&testKey={test_key}&testPlanId="
    return f"{base}?{qs}{frag}"


def xray_test_jira(token: str, test_issue_id: str) -> tuple[str, str]:
    """Resolve Xray test issueId to Jira key + summary (single-test lookup)."""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = request_json(
        XRAY_GRAPHQL,
        method="POST",
        headers=headers,
        body={
            "query": """
            query TestJira($issueId: String!) {
              getTest(issueId: $issueId) {
                jira(fields: ["key", "summary"])
              }
            }
            """,
            "variables": {"issueId": test_issue_id},
        },
        timeout=60,
    )
    if payload.get("errors"):
        return test_issue_id, ""
    jira = ((payload.get("data") or {}).get("getTest") or {}).get("jira") or {}
    return str(jira.get("key") or test_issue_id), str(jira.get("summary") or "")


def xray_failed_tests(token: str, execution_key: str) -> list[dict[str, str]]:
    """Tests whose latest status in this execution is FAILED/FAIL (same rule as xray_counts)."""
    issue_id = xray_issue_id(token, execution_key)
    latest_statuses, _, _ = xray_latest_run_statuses(token, issue_id)
    failed_ids = [tid for tid, status in latest_statuses.items() if status.upper() in FAILED]

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    jira_by_test_id: dict[str, tuple[str, str]] = {}
    start = 0
    use_jira_inline = True
    while use_jira_inline:
        payload = request_json(
            XRAY_GRAPHQL,
            method="POST",
            headers=headers,
            body={
                "query": TESTS_QUERY_WITH_JIRA,
                "variables": {"issueId": issue_id, "start": start, "limit": 100},
            },
            timeout=120,
        )
        if payload.get("errors"):
            use_jira_inline = False
            break
        execution = (payload.get("data") or {}).get("getTestExecution")
        if not execution or not execution.get("testRuns"):
            use_jira_inline = False
            break
        block = execution["testRuns"]
        total = int(block.get("total") or 0)
        results = block.get("results") or []
        if not results:
            break
        for run in results:
            test = run.get("test") or {}
            test_id = str(test.get("issueId") or "")
            if not test_id:
                continue
            jira = test.get("jira") or {}
            if jira.get("key"):
                jira_by_test_id[test_id] = (str(jira["key"]), str(jira.get("summary") or ""))
        start += len(results)
        if start >= total:
            break

    failed: list[dict[str, str]] = []
    for test_id in sorted(failed_ids, key=lambda tid: jira_by_test_id.get(tid, (tid,))[0]):
        if test_id in jira_by_test_id:
            test_key, summary = jira_by_test_id[test_id]
        else:
            test_key, summary = xray_test_jira(token, test_id)
        failed.append(
            {
                "key": test_key,
                "summary": summary,
                "url": xray_testing_board_url(execution_key, test_key),
            }
        )
    return failed


SUPPORT_LINK_TYPE_NAMES = frozenset(
    {
        "Support Ticket - Notify Client",
        "Support Ticket - Don't Notify Client",
    }
)


def support_keys_from_issuelinks(issuelinks: list[dict[str, Any]] | None) -> list[str]:
    """Return SUPPORT (or Support Ticket link type) keys linked from a bug."""
    found: list[str] = []
    for link in issuelinks or []:
        ltype = (link.get("type") or {}).get("name") or ""
        for side in ("inwardIssue", "outwardIssue"):
            issue = link.get(side)
            if not issue:
                continue
            key = issue.get("key") or ""
            if not key:
                continue
            if key.upper().startswith("SUPPORT-"):
                found.append(key)
            elif ltype in SUPPORT_LINK_TYPE_NAMES:
                found.append(key)
    return sorted(set(found))


def customer_reported_jql(bug_keys: list[str], preprod_name: str | None = None) -> str | None:
    if not bug_keys:
        return None
    keys = f"key in ({', '.join(sorted(bug_keys))})"
    if preprod_name:
        return f'issuetype = Bug AND affectedVersion = "{preprod_name}" AND {keys}'
    return keys


def affected_version_names_from_fields(fields: dict[str, Any] | None) -> list[str]:
    names: list[str] = []
    for item in (fields or {}).get("versions") or []:
        name = item.get("name")
        if name:
            names.append(name)
    return names


def bug_has_train_affected_version(
    bug: dict[str, Any],
    preprod_name: str | None,
    affected_versions_by_key: dict[str, list[str]] | None,
) -> bool:
    if not preprod_name:
        return True
    names = bug.get("affected_versions")
    if names is None and affected_versions_by_key:
        names = affected_versions_by_key.get(bug["key"])
    if names is not None:
        return preprod_name in names
    return not bug.get("outside_cutoff_query")


def apply_customer_reported_block(
    report: dict[str, Any],
    support_by_bug: dict[str, list[str]],
    affected_versions_by_key: dict[str, list[str]] | None = None,
) -> None:
    """Attach customer-reported bugs (SUPPORT-linked, train preprod affectedVersion) to a release report."""
    preprod_name = (report.get("cutoff") or {}).get("name")
    rows: list[dict[str, Any]] = []
    for bug in report.get("bugs", {}).get("issues") or []:
        tickets = support_by_bug.get(bug["key"]) or []
        if not tickets:
            continue
        if not bug_has_train_affected_version(bug, preprod_name, affected_versions_by_key):
            continue
        rows.append(
            {
                **bug,
                "support_tickets": tickets,
                "support_ticket_urls": [browse(k) for k in tickets],
            }
        )
    keys = [row["key"] for row in rows]
    jql = customer_reported_jql(keys, preprod_name)
    block = {
        "count": len(rows),
        "affected_version": preprod_name,
        "support_ticket_count": len({t for row in rows for t in row["support_tickets"]}),
        "jql": jql,
        "url": jql_url(jql) if jql else None,
        "rule": (
            f'Bug with Affected Version "{preprod_name}" and a Jira issue link to a SUPPORT-* ticket '
            "(includes Relates and Support Ticket link types)."
            if preprod_name
            else "Bug with SUPPORT link and matching train affected version."
        ),
        "issues": rows,
    }
    report.setdefault("bugs", {})["customer_reported"] = block
    report.setdefault("metrics", {})["bugs_customer_reported"] = block["count"]


def known_issues_jql(preprod_name: str) -> str:
    """Open internal bugs on a train preprod Affected Version (release known-issues list)."""
    return (
        f"project = {PROJECT_VERSIONS} AND affectedVersion = \"{preprod_name}\" "
        f"AND status NOT IN (Done, Canceled) AND issuetype = Bug "
        f'AND "Bug Type[Dropdown]" = Internal'
    )


def jql_url(jql: str) -> str:
    return f"{site_url()}/issues/?jql={urllib.parse.quote(jql)}"


def key_in_jql(keys: list[str]) -> str:
    """JQL `key in (...)` for saved links to a fixed issue set."""
    ordered = sorted(set(keys), key=lambda k: (int(k.split("-")[1]), k))
    return "key in (" + ", ".join(ordered) + ")"


def key_in_jql_url(keys: list[str]) -> str:
    return jql_url(key_in_jql(keys))


def jql_and_clause(jql: str, clause: str) -> str:
    """Append AND clause before ORDER BY if present."""
    marker = " order by "
    lower = jql.lower()
    idx = lower.find(marker)
    if idx >= 0:
        return f"{jql[:idx]} AND {clause}{jql[idx:]}"
    return f"{jql} AND {clause}"


def build_bug_jql_slices(
    base_jql: str | None,
    bugs: list[dict[str, Any]],
    test_run_key: str | None,
    defect_keys: list[str] | None = None,
) -> dict[str, Any]:
    """JQL: all Defect links from the test run vs cut-off bugs not linked from that run."""
    linked = sorted(set(defect_keys or []))
    if not linked and test_run_key:
        linked = sorted(b["key"] for b in bugs if b.get("found_by_test_run"))

    jql_test_run: str | None = None
    jql_other: str | None = None
    if test_run_key:
        jql_test_run = f'issuetype = Bug AND issue in linkedIssues("{test_run_key}")'
    elif linked:
        keys = ", ".join(linked)
        jql_test_run = f"key in ({keys})"

    other_count = sum(1 for bug in bugs if bug["key"] not in set(linked))
    if base_jql:
        if test_run_key:
            jql_other = jql_and_clause(
                base_jql,
                f'issue not in linkedIssues("{test_run_key}")',
            )
        elif linked:
            keys = ", ".join(linked)
            jql_other = jql_and_clause(base_jql, f"key not in ({keys})")
        else:
            jql_other = base_jql

    return {
        "test_run": {
            "count": len(linked),
            "jql": jql_test_run,
            "url": jql_url(jql_test_run) if jql_test_run else None,
            "execution_key": test_run_key,
        },
        "other": {
            "count": other_count,
            "jql": jql_other,
            "url": jql_url(jql_other) if jql_other else None,
        },
    }


def iso_date(value: str | None) -> str | None:
    if not value:
        return None
    return value[:10]


def bug_row_from_issue(
    issue: dict[str, Any],
    *,
    found_by_test_run: bool = False,
    outside_cutoff_query: bool = False,
) -> dict[str, Any]:
    fields = issue.get("fields") or {}
    return {
        "key": issue["key"],
        "summary": fields.get("summary"),
        "priority": (fields.get("priority") or {}).get("name") or "None",
        "status": (fields.get("status") or {}).get("name"),
        "created": iso_date(fields.get("created")),
        "found_by_test_run": found_by_test_run,
        "outside_cutoff_query": outside_cutoff_query,
        "url": browse(issue["key"]),
    }


def cutoff_scope_bugs(bugs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [bug for bug in bugs if not bug.get("outside_cutoff_query")]


def supplement_linked_defects(
    bugs: list[dict[str, Any]],
    defect_keys: list[str] | None,
) -> list[dict[str, Any]]:
    """Load Jira fields for test-run-linked defects outside the cut-off bug JQL."""
    if not defect_keys:
        return bugs
    have = {bug["key"] for bug in bugs}
    missing = [key for key in defect_keys if key not in have]
    if not missing:
        return bugs
    out = list(bugs)
    for start in range(0, len(missing), 50):
        chunk = missing[start : start + 50]
        jql = f"key in ({', '.join(chunk)})"
        try:
            issues = jira_search(jql, ["summary", "priority", "status", "created"])
        except RuntimeError:
            return out
        for issue in issues:
            out.append(bug_row_from_issue(issue, found_by_test_run=True, outside_cutoff_query=True))
    return out


def parse_instant(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        match = re.match(r"^(.+)([+-]\d{2})(\d{2})$", raw)
        if match:
            try:
                return datetime.fromisoformat(match.group(1) + match.group(2) + ":" + match.group(3))
            except ValueError:
                return None
    return None


def weekday_span_days(first: datetime | None, last: datetime | None) -> int | None:
    """Weekdays from first to last calendar day inclusive, minus one (same day → 0)."""
    if not first or not last or last < first:
        return None
    start = first.date()
    end = last.date()
    if start == end:
        return 0 if start.weekday() < 5 else None
    weekdays = 0
    day = start
    while day <= end:
        if day.weekday() < 5:
            weekdays += 1
        day += timedelta(days=1)
    return max(0, weekdays - 1)


def xray_execution_status_bounds(token: str, issue_id: str) -> tuple[datetime | None, datetime | None]:
    """Earliest and latest status activity in this Test Execution only."""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    first: datetime | None = None
    last: datetime | None = None
    start = 0
    total = None
    while total is None or start < total:
        payload = request_json(
            XRAY_GRAPHQL,
            method="POST",
            headers=headers,
            body={
                "query": EXECUTION_TEST_RUNS_QUERY,
                "variables": {"issueId": issue_id, "start": start, "limit": 100},
            },
            timeout=120,
        )
        if payload.get("errors"):
            message = "; ".join(err.get("message", "") for err in payload["errors"])
            raise RuntimeError(f"Xray GraphQL testRuns for {issue_id}: {message}")
        block = ((payload.get("data") or {}).get("getTestExecution") or {}).get("testRuns")
        if not block:
            return first, last
        total = int(block.get("total") or 0)
        results = block.get("results") or []
        if not results:
            break
        for test_run in results:
            for item in (test_run.get("activity") or {}).get("results") or []:
                if (item.get("field") or "").strip().lower() != STATUS_ACTIVITY_FIELD:
                    continue
                changed = parse_instant(item.get("date"))
                if not changed:
                    continue
                if first is None or changed < first:
                    first = changed
                if last is None or changed > last:
                    last = changed
        start += len(results)
    return first, last


def days_between(start: str | None, end: str | None) -> int | None:
    if not start or not end:
        return None
    return (date.fromisoformat(end) - date.fromisoformat(start)).days


def choose_test_run(candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if not candidates:
        return None, []
    if len(candidates) == 1:
        return candidates[0], []
    manual = [
        item
        for item in candidates
        if "jira cloud manual" in item["summary"].lower()
        and "automated" not in item["summary"].lower()
        and "bigpicture" in item["summary"].lower()
    ]
    if len(manual) == 1:
        chosen = manual[0]
        rest = [item for item in candidates if item["key"] != chosen["key"]]
        return chosen, rest
    return None, candidates


def gather(version: str, token: str | None) -> dict[str, Any]:
    versions = list_versions(version)
    preprod = []
    for item in versions:
        cutoff = parse_preprod(item.get("name") or "", version)
        if cutoff:
            preprod.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "cutoff_date": cutoff,
                "released": bool(item.get("released")),
            })
    preprod.sort(key=lambda item: item["cutoff_date"])
    chosen = preprod[-1] if preprod else None
    cutoff_date = chosen["cutoff_date"] if chosen else None

    cloud_re = cloud_name(version)
    cloud = []
    for item in versions:
        name = item.get("name") or ""
        if not cloud_re.match(name):
            continue
        cloud.append({
            "id": item.get("id"),
            "name": name,
            "released": bool(item.get("released")),
            "release_date": iso_date(item.get("releaseDate")),
            "url": f"{site_url()}/projects/{PROJECT_VERSIONS}/versions/{item.get('id')}",
        })
    cloud.sort(key=lambda item: (item["release_date"] or "9999", item["name"]))
    released = [item for item in cloud if item["released"] and item["release_date"]]
    first = min(released, key=lambda item: item["release_date"]) if released else None

    notes: list[str] = []
    if len(preprod) > 1:
        names = ", ".join(item["name"] for item in preprod)
        notes.append(f"Several preprod versions match {version}; using the latest cut-off ({names}).")
    if not chosen:
        notes.append(f"No ONE version named preprod/YYYY-MM-DD/{version}.")

    test_run = None
    candidates: list[dict[str, Any]] = []
    if cutoff_date:
        jql = (
            f'project = {PROJECT_TESTS} AND issuetype = "Test Execution" '
            f'AND summary ~ "\\"Major Release Test Run\\"" AND summary ~ "\\"{version}\\"" '
            f"ORDER BY created ASC"
        )
        token_re = version_token(version)
        for issue in jira_search(jql, ["summary", "status", "created", "issuelinks"]):
            summary = (issue.get("fields") or {}).get("summary") or ""
            if "major release test run" not in summary.lower():
                continue
            if not token_re.search(summary):
                continue
            fields = issue["fields"]
            candidates.append({
                "key": issue["key"],
                "summary": summary,
                "status": (fields.get("status") or {}).get("name"),
                "created": fields.get("created"),
                "url": browse(issue["key"]),
                "defect_keys": defect_keys(issue),
            })
        chosen_run, remaining = choose_test_run(candidates)
        if chosen_run:
            if token:
                chosen_run["stats"] = xray_counts(token, chosen_run["key"], chosen_run.get("created"))
            else:
                chosen_run["stats"] = None
                notes.append(
                    "Test-run counts were not loaded. Xray API keys in Trinity/studio/.env "
                    "did not authenticate for appfire.atlassian.net."
                )
            test_run = chosen_run
            candidates = remaining
        elif candidates:
            notes.append(
                "Several Major Release Test Runs match this version. "
                "None was selected. Pass --execution KEY to choose one."
            )
        else:
            notes.append(f"No Major Release Test Run in {PROJECT_TESTS} contains {version}.")

    bugs: list[dict[str, Any]] = []
    bug_jql = None
    if cutoff_date:
        bug_jql = (
            f'issuetype = Bug AND affectedVersion = "{chosen["name"]}" '
            f'AND created >= "{cutoff_date}" ORDER BY priority DESC, created ASC'
        )
        found = set(test_run["defect_keys"]) if test_run else set()
        for issue in jira_search(bug_jql, ["summary", "priority", "status", "created"]):
            bugs.append(
                bug_row_from_issue(
                    issue,
                    found_by_test_run=issue["key"] in found,
                )
            )
        if test_run:
            bugs = supplement_linked_defects(bugs, test_run.get("defect_keys"))

    cutoff_bugs = cutoff_scope_bugs(bugs)
    priority_order = ["Highest", "High", "Medium", "Low", "Lowest"]
    by_priority: dict[str, int] = {}
    for bug in cutoff_bugs:
        by_priority[bug["priority"]] = by_priority.get(bug["priority"], 0) + 1
    ordered_priorities = [name for name in priority_order if name in by_priority]
    ordered_priorities += sorted(name for name in by_priority if name not in priority_order)

    stats = (test_run or {}).get("stats") or {}
    timing = stats.get("timing") or {}
    release_date = first["release_date"] if first else None
    bug_slices = build_bug_jql_slices(
        bug_jql,
        bugs,
        test_run["key"] if test_run else None,
        (test_run or {}).get("defect_keys"),
    )
    metrics = {
        "version": version,
        "cutoff_date": cutoff_date,
        "release_date": release_date,
        "released": bool(first),
        "days_in_preprod": days_between(cutoff_date, release_date),
        "tests_total": stats.get("total"),
        "tests_executed": stats.get("executed"),
        "tests_passed": stats.get("passed"),
        "tests_failed": stats.get("failed"),
        "tests_skipped": stats.get("skipped"),
        "tests_todo": stats.get("todo"),
        "test_run_duration_days": timing.get("duration_days"),
        "test_run_first_status_change": timing.get("first_status_change"),
        "test_run_last_status_change": timing.get("last_status_change"),
        "qa_engineers_count": (stats.get("qa_engineers") or {}).get("count"),
        "bugs_total": len(cutoff_bugs),
        "bugs_found_by_test_run": len((test_run or {}).get("defect_keys") or []),
        "bugs_other_since_cutoff": bug_slices["other"]["count"],
        "bugs_by_priority": {name: by_priority[name] for name in ordered_priorities},
    }
    known_jql = known_issues_jql(chosen["name"]) if chosen else None
    return {
        "schema_version": 1,
        "gathered_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "version": version,
        "site": site_url(),
        "cutoff": chosen,
        "preprod_versions": preprod,
        "known_issues": {
            "name": f"Known issues after release {version}",
            "jql": known_jql,
            "url": jql_url(known_jql) if known_jql else None,
            "rule": (
                "Open internal bugs with Affected Version = train preprod "
                "(matches Jira saved-filter pattern for post-release known issues)."
            ),
        },
        "production": {
            "product": "bigpicture-cloud",
            "released": bool(first),
            "first_released": first,
            "versions": cloud,
        },
        "test_run": test_run,
        "test_run_candidates": candidates if candidates else [],
        "bugs": {
            "jql": bug_jql,
            "url": jql_url(bug_jql) if bug_jql else None,
            "rule": "Affected Version is the preprod version, created on or after the cut-off date.",
            "by_priority": metrics["bugs_by_priority"],
            "found_by_test_run": metrics["bugs_found_by_test_run"],
            "test_run": bug_slices["test_run"],
            "other": bug_slices["other"],
            "issues": bugs,
        },
        "metrics": metrics,
        "notes": notes,
    }


def apply_execution_override(report: dict[str, Any], key: str, token: str | None) -> None:
    """Replace the selected test run when the operator passes --execution."""
    matches = [item for item in report["test_run_candidates"] if item["key"] == key]
    if report["test_run"] and report["test_run"]["key"] == key:
        return
    if not matches and report["test_run"] is None:
        issue = jira_get(f"/rest/api/3/issue/{key}", {"fields": "summary,status,created,issuelinks"})
        fields = issue["fields"]
        matches = [{
            "key": issue["key"],
            "summary": fields.get("summary"),
            "status": (fields.get("status") or {}).get("name"),
            "created": fields.get("created"),
            "url": browse(issue["key"]),
            "defect_keys": defect_keys(issue),
        }]
    if not matches:
        raise RuntimeError(f"{key} is not a candidate for {report['version']}")
    chosen = matches[0]
    chosen["stats"] = xray_counts(token, chosen["key"], chosen.get("created")) if token else None
    report["test_run"] = chosen
    report["test_run_candidates"] = [
        item for item in report["test_run_candidates"] if item["key"] != key
    ]
    found = set(chosen["defect_keys"])
    for bug in report["bugs"]["issues"]:
        bug["found_by_test_run"] = bug["key"] in found
    stats = chosen["stats"] or {}
    timing = stats.get("timing") or {}
    report["metrics"].update({
        "tests_total": stats.get("total"),
        "tests_executed": stats.get("executed"),
        "tests_passed": stats.get("passed"),
        "tests_failed": stats.get("failed"),
        "tests_skipped": stats.get("skipped"),
        "tests_todo": stats.get("todo"),
        "test_run_duration_days": timing.get("duration_days"),
        "test_run_first_status_change": timing.get("first_status_change"),
        "test_run_last_status_change": timing.get("last_status_change"),
        "qa_engineers_count": (stats.get("qa_engineers") or {}).get("count"),
        "bugs_found_by_test_run": len(chosen.get("defect_keys") or []),
    })
    report["bugs"]["found_by_test_run"] = report["metrics"]["bugs_found_by_test_run"]
    slices = build_bug_jql_slices(
        report["bugs"]["jql"],
        report["bugs"]["issues"],
        key,
        chosen.get("defect_keys"),
    )
    report["bugs"]["test_run"] = slices["test_run"]
    report["bugs"]["other"] = slices["other"]
    report["metrics"]["bugs_other_since_cutoff"] = slices["other"]["count"]
    report["notes"] = [
        note for note in report["notes"] if "Several Major Release Test Runs" not in note
    ]
    report["notes"].append(f"Test run selected with --execution {key}.")


# Canonical Major Release Test Run (Jira Cloud Manual) when several TC executions match.
EXECUTION_OVERRIDES: dict[str, str] = {
    "8.75": "TC-6504",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Gather BigPicture Cloud release stats")
    parser.add_argument(
        "versions",
        nargs="*",
        help="Release trains, e.g. 8.76 (omit when using --since)",
    )
    parser.add_argument(
        "--since",
        metavar="YYYY-MM-DD",
        help="Gather every train whose preprod cut-off is on or after this date",
    )
    parser.add_argument(
        "--execution",
        action="append",
        default=[],
        metavar="VERSION=KEY",
        help="Force the Test Execution for a train, e.g. 8.76=TC-6690",
    )
    args = parser.parse_args()
    overrides = {}
    for item in args.execution:
        if "=" not in item:
            raise SystemExit(f"--execution must look like 8.76=TC-6690, got {item}")
        version, key = item.split("=", 1)
        overrides[version] = key
    overrides.update(EXECUTION_OVERRIDES)

    if args.since and args.versions:
        raise SystemExit("Use either explicit version tokens or --since, not both")
    if args.since:
        version_list = discover_trains_since(date.fromisoformat(args.since))
        if not version_list:
            raise SystemExit(f"No preprod trains found with cut-off on/after {args.since}")
    elif args.versions:
        version_list = args.versions
    else:
        raise SystemExit("Pass version tokens (8.76 …) or --since YYYY-MM-DD")

    load_env(ENV_PATH)
    load_env(PRODUCTION_ENV_PATH, override={"XRAY_CLIENT_ID", "XRAY_CLIENT_SECRET"})
    token: str | None
    try:
        token = xray_token()
    except RuntimeError as exc:
        token = None
        print(f"warning: {exc}", file=sys.stderr)
        print("warning: test-run counts will be omitted until production Xray keys are set.", file=sys.stderr)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for version in version_list:
        if not re.fullmatch(r"\d+\.\d+", version):
            raise SystemExit(f"Version must look like 8.76, got {version}")
        report = gather(version, token)
        if version in overrides:
            apply_execution_override(report, overrides[version], token)
        out = DATA_DIR / f"{version}.json"
        out.write_text(json.dumps(report, indent=2) + "\n")
        metrics = report["metrics"]
        print(
            f"{version}: cutoff={metrics['cutoff_date']} "
            f"run={report['test_run']['key'] if report['test_run'] else 'NONE'} "
            f"tests={metrics['tests_total']} bugs={metrics['bugs_total']} "
            f"released={metrics['release_date'] or 'no'}"
        )
        for note in report["notes"]:
            print(f"  note: {note}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
