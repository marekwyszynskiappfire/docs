#!/usr/bin/env python3
"""Render release-stats JSON files into the Cursor canvas.

Reads Release Process/stats/data/*.json (schema_version 1).
Writes the release comparison table plus one collapsible section per release, newest first.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "Release Process" / "stats" / "data"
DEFAULT_CANVAS = (
    Path.home()
    / ".cursor/projects/Users-marek-wyszynski-repo-DOCS/canvases/release-stats.canvas.tsx"
)
SCRIPTS = ROOT / "Release Process" / "stats" / "scripts"


def resolve_canvas_path(raw: str) -> Path:
    """Map operator paste (path, file://, or Cursor canvas URL) to a .canvas.tsx file."""
    text = raw.strip().strip('"').strip("'")
    if not text:
        return DEFAULT_CANVAS
    if text.startswith("file://"):
        parsed = urlparse(text)
        return Path(unquote(parsed.path))
    if "://" in text:
        # Cursor canvas links often end with a slug; match known release-stats canvas files.
        slug = text.rstrip("/").split("/")[-1]
        if slug.endswith(".canvas.tsx"):
            candidate = DEFAULT_CANVAS.parent / slug
            if candidate.is_file():
                return candidate
        for path in DEFAULT_CANVAS.parent.glob("*.canvas.tsx"):
            if "release-stats" in path.name or "release_stats" in path.name:
                return path
        raise SystemExit(
            f"Could not map canvas URL to a file under {DEFAULT_CANVAS.parent}. "
            "Paste the filesystem path to the .canvas.tsx file instead."
        )
    path = Path(text).expanduser()
    if path.is_dir():
        for name in ("release-stats.canvas.tsx", "release_stats.canvas.tsx"):
            candidate = path / name
            if candidate.is_file():
                return candidate
        raise SystemExit(f"No release-stats .canvas.tsx in directory {path}")
    if not path.suffix:
        path = path.with_suffix(".canvas.tsx")
    return path


def canvas_exists(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        body = path.read_text(encoding="utf-8", errors="replace")[:8000]
    except OSError:
        return False
    return "Release comparison" in body or "const RELEASES" in body


def load_gather():
    spec = importlib.util.spec_from_file_location("gather_release_stats", SCRIPTS / "gather_release_stats.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

PRIORITY_TONE = {
    "Highest": "danger",
    "High": "warning",
    "Medium": "info",
    "Low": "neutral",
    "Lowest": "neutral",
}


def pretty(iso: str | None) -> str | None:
    if not iso:
        return None
    return date.fromisoformat(iso[:10]).strftime("%-d %b %Y")


def bug_slices(release: dict) -> dict[str, Any]:
    bugs_block = release.get("bugs") or {}
    issues = bugs_block.get("issues") or []
    run = release.get("test_run") or {}
    defect_keys = run.get("defect_keys") or []
    gather = load_gather()
    slices = gather.build_bug_jql_slices(
        bugs_block.get("jql"),
        issues,
        run.get("key"),
        defect_keys,
    )
    tr = slices["test_run"]
    other = slices["other"]
    linked_set = set(defect_keys)
    other_from_issues = len([b for b in issues if b["key"] not in linked_set])
    return {
        "testRunCount": len(defect_keys),
        "testRunUrl": tr.get("url"),
        "testRunKey": tr.get("execution_key") or run.get("key"),
        "testRunJql": tr.get("jql"),
        "otherCount": other_from_issues,
        "otherUrl": other.get("url"),
    }


def load_releases() -> list[dict]:
    files = sorted(DATA_DIR.glob("*.json"), key=lambda path: path.stem, reverse=True)
    releases = []
    for path in files:
        if path.name == "changelogs.json":
            continue
        payload = json.loads(path.read_text())
        if payload.get("schema_version") != 1:
            continue
        releases.append(payload)
    releases.sort(key=lambda item: [int(part) for part in item["version"].split(".")], reverse=True)
    return releases


def _effective_release(release: dict) -> tuple[str | None, bool, int | None]:
    """Production date and days: Done+fix changelog signal, else cloud fix-version dates."""
    metrics = release.get("metrics") or {}
    production = release.get("production") or {}
    signal = production.get("release_signal") or {}
    first = production.get("first_released") or {}
    version = release.get("version") or ""

    rs = importlib.util.spec_from_file_location(
        "release_signal",
        SCRIPTS / "release_signal.py",
    )
    release_signal = importlib.util.module_from_spec(rs)
    assert rs.loader
    rs.loader.exec_module(release_signal)

    release_date = metrics.get("release_date") or signal.get("release_date")
    if not release_date and first.get("release_date"):
        release_date = first["release_date"]
    if not release_date and version:
        release_date = release_signal.earliest_cloud_fix_date(production, version)

    released = bool(
        metrics.get("released")
        or signal.get("released")
        or production.get("released")
        or release_date
    )

    days = metrics.get("days_in_preprod")
    cutoff = metrics.get("cutoff_date")
    if days is None and cutoff and release_date:
        days = (date.fromisoformat(release_date) - date.fromisoformat(cutoff)).days
    return release_date, released, days


def view_model(releases: list[dict]) -> list[dict]:
    models = []
    for release in releases:
        metrics = release["metrics"]
        bugs = release["bugs"]["issues"]
        slices = []
        for name, count in release["bugs"]["by_priority"].items():
            if count:
                slices.append({"label": name, "value": count, "tone": PRIORITY_TONE.get(name, "neutral")})
        run = release.get("test_run")
        candidates = release.get("test_run_candidates") or []
        if run:
            runs = [run]
        else:
            runs = candidates
        signal = (release.get("production") or {}).get("release_signal") or {}
        release_date_iso, released, days_in_preprod = _effective_release(release)
        slices_bugs = bug_slices(release)
        linked_bugs, other_bugs = split_bug_lists(release, bugs)
        defect_keys = (run or {}).get("defect_keys") or []
        linked_count = len(defect_keys) if defect_keys else len(linked_bugs)
        other_count = metrics.get("bugs_other_since_cutoff")
        if other_count is None:
            other_count = len(other_bugs)
        else:
            other_count = int(other_count)
        customer = (release.get("bugs") or {}).get("customer_reported") or {}
        customer_rows = _customer_bug_rows(customer)
        run_stats = (run or {}).get("stats") or {}

        def _xray_count(metric_key: str, stats_key: str) -> int | None:
            val = metrics.get(metric_key)
            if val is not None:
                return int(val)
            raw = run_stats.get(stats_key)
            return int(raw) if raw is not None else None

        models.append({
            "version": release["version"],
            "cutoff": pretty(metrics.get("cutoff_date")),
            "cutoffIso": metrics.get("cutoff_date"),
            "released": released,
            "releaseDate": pretty(release_date_iso),
            "releaseDateLast": pretty(
                metrics.get("release_date_last") or signal.get("release_date_last")
            ),
            "releaseTriggerKey": signal.get("trigger_issue"),
            "releaseTriggerUrl": signal.get("trigger_url"),
            "releaseRule": signal.get("rule"),
            "days": days_in_preprod,
            "planned": _planned(release, signal),
            "preprodName": (release.get("cutoff") or {}).get("name"),
            "cloudVersions": [
                {
                    "name": item["name"],
                    "released": item["released"],
                    "releaseDate": pretty(item.get("release_date")),
                    "statusLabel": _cloud_version_status(item, signal, release_date_iso),
                    "url": item["url"],
                }
                for item in release["production"]["versions"]
            ],
            "runs": [
                {
                    "key": item["key"],
                    "summary": item["summary"],
                    "status": item["status"],
                    "created": pretty((item.get("created") or "")[:10]),
                    "url": item["url"],
                    "linkedBugs": len(item.get("defect_keys") or []),
                    "stats": item.get("stats"),
                }
                for item in runs
            ],
            "singleRun": run is not None,
            "bugsLinked": linked_bugs,
            "bugsOther": other_bugs,
            "bugCount": linked_count + other_count,
            "bugsTestRunCount": linked_count,
            "bugsTestRunUrl": slices_bugs["testRunUrl"],
            "bugsTestRunKey": slices_bugs.get("testRunKey"),
            "bugsTestRunJql": slices_bugs.get("testRunJql"),
            "bugsOtherCount": other_count,
            "bugsOtherUrl": slices_bugs["otherUrl"],
            "bugsCustomerReportedCount": metrics.get("bugs_customer_reported")
            if metrics.get("bugs_customer_reported") is not None
            else customer.get("count", 0),
            "bugsCustomerReportedUrl": customer.get("url"),
            "bugsCustomerReportedJql": customer.get("jql"),
            "bugsCustomerReportedRule": customer.get("rule"),
            "bugsCustomerReported": customer_rows,
            "slices": slices,
            "bugUrl": release["bugs"]["url"],
            "notes": [
                note for note in (release.get("notes") or [])
                if not note.startswith("Test-run counts were not loaded")
            ],
            "gatheredAt": pretty((release.get("gathered_at") or "")[:10]),
            "testRunDurationDays": metrics.get("test_run_duration_days"),
            "testRunFirstStatus": pretty((metrics.get("test_run_first_status_change") or "")[:10]),
            "testRunLastStatus": pretty((metrics.get("test_run_last_status_change") or "")[:10]),
            "testRunTimingRule": ((release.get("test_run") or {}).get("stats") or {}).get("timing", {}).get("rule"),
            "testsTotal": _xray_count("tests_total", "total"),
            "testsExecuted": _xray_count("tests_executed", "executed"),
            "testsPassed": _xray_count("tests_passed", "passed"),
            "testsFailed": _xray_count("tests_failed", "failed"),
            "testsSkipped": _xray_count("tests_skipped", "skipped"),
            "testsTodo": _xray_count("tests_todo", "todo"),
            "qaEngineersCount": metrics.get("qa_engineers_count"),
            "qaEngineerNames": ((release.get("test_run") or {}).get("stats") or {}).get("qa_engineers", {}).get("names") or [],
            "failedTests": [
                {
                    "key": item["key"],
                    "summary": item.get("summary") or "",
                    "url": item.get("url") or "",
                }
                for item in (run or {}).get("failed_tests") or []
            ],
            "failedTestsSource": (run or {}).get("failed_tests_source"),
            "knownIssuesName": (release.get("known_issues") or {}).get("name"),
            "knownIssuesJql": (release.get("known_issues") or {}).get("jql"),
            "knownIssuesUrl": (release.get("known_issues") or {}).get("url"),
            "knownIssuesRule": (release.get("known_issues") or {}).get("rule"),
            "knownIssuesBreakdown": [
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "gitBranch": item.get("git_branch"),
                    "count": item.get("count") or len(item.get("keys") or []),
                    "keys": item.get("keys") or [],
                    "jql": item.get("jql"),
                    "url": item.get("url"),
                    "bugs": _known_issue_table_rows(item, release.get("site") or "https://appfire.atlassian.net"),
                }
                for item in (release.get("known_issues") or {}).get("breakdown") or []
            ],
        })
    return models


def _shipped_fix_names(signal: dict) -> set[str]:
    names: set[str] = set()
    for event in signal.get("qualifying_events") or []:
        names.update(event.get("fix_versions") or [])
    for name in signal.get("trigger_fix_versions") or []:
        names.add(name)
    return names


def _cloud_version_status(item: dict, signal: dict, release_date_iso: str | None) -> str:
    if item.get("released"):
        return "Released in Jira"
    shipped = _shipped_fix_names(signal)
    if item.get("name") in shipped and release_date_iso:
        return f"Production ({pretty(release_date_iso)})"
    return "Unreleased in Jira"


def _planned(release: dict, signal: dict | None = None) -> str | None:
    signal = signal or {}
    if signal.get("released") or release["metrics"].get("release_date"):
        return None
    dated = [item for item in release["production"]["versions"] if item.get("release_date")]
    if not dated:
        return None
    first = min(dated, key=lambda item: item["release_date"])
    return f"{first['name']} planned {pretty(first['release_date'])}"


def _customer_bug_rows(customer_block: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    site = "https://appfire.atlassian.net"
    for bug in customer_block.get("issues") or []:
        tickets = bug.get("support_tickets") or []
        ticket_label = ", ".join(tickets) if tickets else "—"
        ticket_url = (bug.get("support_ticket_urls") or [None])[0]
        rows.append(
            {
                "key": bug["key"],
                "summary": bug.get("summary"),
                "priority": bug.get("priority") or "None",
                "status": bug.get("status"),
                "created": pretty(bug.get("created")),
                "url": bug.get("url") or f"{site}/browse/{bug['key']}",
                "supportTickets": ticket_label,
                "supportTicketUrl": ticket_url,
                "tone": {"Highest": "danger", "High": "warning"}.get(
                    bug.get("priority") or "", "neutral"
                ),
            }
        )
    return rows


def _bug_view_row(bug: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": bug["key"],
        "summary": bug["summary"],
        "priority": bug["priority"],
        "status": bug["status"],
        "created": pretty(bug["created"]),
        "url": bug["url"],
        "tone": {"Highest": "danger", "High": "warning"}.get(bug["priority"], "neutral"),
    }


def _known_issue_table_rows(group: dict[str, Any], site: str) -> list[dict[str, Any]]:
    """Rows for known_issues.breakdown tables (order follows group keys)."""
    stored = {item["key"]: item for item in group.get("issues") or []}
    rows: list[dict[str, Any]] = []
    for key in group.get("keys") or []:
        item = stored.get(key)
        if not item:
            rows.append(
                {
                    "key": key,
                    "summary": "—",
                    "priority": "—",
                    "status": "—",
                    "created": "",
                    "url": f"{site}/browse/{key}",
                    "tone": "neutral",
                }
            )
            continue
        rows.append(
            _bug_view_row(
                {
                    "key": item["key"],
                    "summary": item.get("summary") or "—",
                    "priority": item.get("priority") or "None",
                    "status": item.get("status") or "—",
                    "created": (item.get("created") or "")[:10],
                    "url": item.get("url") or f"{site}/browse/{key}",
                }
            )
        )
    return rows


def split_bug_lists(release: dict, bugs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    site = release.get("site") or "https://appfire.atlassian.net"
    by_key = {bug["key"]: bug for bug in bugs}
    linked_keys = (release.get("test_run") or {}).get("defect_keys") or []
    linked_set = set(linked_keys)
    linked_rows: list[dict[str, Any]] = []
    for key in linked_keys:
        if key in by_key:
            linked_rows.append(_bug_view_row(by_key[key]))
        else:
            linked_rows.append(
                {
                    "key": key,
                    "summary": "—",
                    "priority": "—",
                    "status": "—",
                    "created": "",
                    "url": f"{site}/browse/{key}",
                    "tone": "neutral",
                }
            )
    other_rows = [_bug_view_row(bug) for bug in bugs if bug["key"] not in linked_set]
    return linked_rows, other_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--canvas",
        help="Output .canvas.tsx path or URL (default: DOCS project release-stats canvas)",
    )
    args = parser.parse_args()
    canvas_path = resolve_canvas_path(args.canvas) if args.canvas else DEFAULT_CANVAS

    releases = load_releases()
    if not releases:
        raise SystemExit(f"No JSON files in {DATA_DIR}")
    model = view_model(releases)
    payload = json.dumps(model, indent=2, ensure_ascii=False)
    gathered = model[0]["gatheredAt"] or "unknown"
    tsx = TEMPLATE.replace("__PAYLOAD__", payload).replace("__GATHERED__", gathered)
    canvas_path.parent.mkdir(parents=True, exist_ok=True)
    canvas_path.write_text(tsx)
    print(f"Wrote {canvas_path} ({len(releases)} releases)")


TEMPLATE = r'''import {
  Callout,
  CollapsibleSection,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Link,
  PieChart,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  UsageBar,
  useHostTheme,
} from "cursor/canvas";

type CloudVersion = {
  name: string;
  released: boolean;
  releaseDate: string | null;
  statusLabel: string;
  url: string;
};

type RunStats = {
  total: number;
  executed: number;
  passed: number;
  failed: number;
  skipped: number;
  todo: number;
};

type TestRun = {
  key: string;
  summary: string;
  status: string;
  created: string | null;
  url: string;
  linkedBugs: number;
  stats: RunStats | null;
};

type Bug = {
  key: string;
  summary: string;
  priority: string;
  status: string;
  created: string | null;
  url: string;
  tone: "danger" | "warning" | "info" | "neutral";
};

type FailedTest = {
  key: string;
  summary: string;
  url: string;
};

type Slice = {
  label: string;
  value: number;
  tone: "danger" | "warning" | "info" | "neutral";
};

type CustomerBug = Bug & {
  supportTickets: string;
  supportTicketUrl: string | null;
};

type KnownIssuesGroup = {
  id: string;
  title: string;
  description: string | null;
  gitBranch: string | null;
  count: number;
  keys: string[];
  jql: string | null;
  url: string | null;
  bugs: Bug[];
};

type Release = {
  version: string;
  cutoff: string | null;
  cutoffIso: string | null;
  released: boolean;
  releaseDate: string | null;
  releaseDateLast: string | null;
  releaseTriggerKey: string | null;
  releaseTriggerUrl: string | null;
  releaseRule: string | null;
  days: number | null;
  planned: string | null;
  preprodName: string | null;
  cloudVersions: CloudVersion[];
  runs: TestRun[];
  singleRun: boolean;
  bugsLinked: Bug[];
  bugsOther: Bug[];
  bugCount: number;
  bugsTestRunCount: number;
  bugsTestRunUrl: string | null;
  bugsTestRunKey: string | null;
  bugsTestRunJql: string | null;
  bugsOtherCount: number;
  bugsOtherUrl: string | null;
  bugsCustomerReportedCount: number;
  bugsCustomerReportedUrl: string | null;
  bugsCustomerReportedJql: string | null;
  bugsCustomerReportedRule: string | null;
  bugsCustomerReported: CustomerBug[];
  slices: Slice[];
  bugUrl: string | null;
  notes: string[];
  gatheredAt: string | null;
  testRunDurationDays: number | null;
  testRunFirstStatus: string | null;
  testRunLastStatus: string | null;
  testRunTimingRule: string | null;
  testsTotal: number | null;
  testsExecuted: number | null;
  testsPassed: number | null;
  testsFailed: number | null;
  testsSkipped: number | null;
  testsTodo: number | null;
  qaEngineersCount: number | null;
  qaEngineerNames: string[];
  failedTests: FailedTest[];
  failedTestsSource: string | null;
  knownIssuesName: string | null;
  knownIssuesUrl: string | null;
  knownIssuesBreakdown: KnownIssuesGroup[];
};

const RELEASES: Release[] = __PAYLOAD__;

function CustomerBugTable({ bugs }: { bugs: CustomerBug[] }) {
  if (bugs.length === 0) {
    return <Text size="small" tone="tertiary">None in gathered data.</Text>;
  }
  return (
    <Table
      headers={["Key", "Summary", "SUPPORT ticket(s)", "Priority", "Status", "Created"]}
      columnAlign={["left", "left", "left", "left", "left", "left"]}
      striped
      stickyHeader
      style={{ width: "100%", minWidth: 960 }}
      rows={bugs.map((bug) => [
        <Text key={bug.key} as="span" style={{ whiteSpace: "nowrap" }}>
          <Link href={bug.url}>{bug.key}</Link>
        </Text>,
        <Text truncate style={{ minWidth: 280, maxWidth: 480, display: "block" }}>{bug.summary}</Text>,
        bug.supportTicketUrl ? (
          <Link href={bug.supportTicketUrl}>{bug.supportTickets}</Link>
        ) : (
          bug.supportTickets
        ),
        <Text as="span" style={{ whiteSpace: "nowrap" }}>{bug.priority}</Text>,
        <Text as="span" style={{ whiteSpace: "nowrap" }}>{bug.status}</Text>,
        <Text as="span" style={{ whiteSpace: "nowrap" }}>{bug.created ?? ""}</Text>,
      ])}
      rowTone={bugs.map((bug) => (bug.tone === "neutral" ? undefined : bug.tone))}
    />
  );
}

function BugTable({ bugs }: { bugs: Bug[] }) {
  if (bugs.length === 0) {
    return <Text size="small" tone="tertiary">None in gathered data.</Text>;
  }
  return (
    <Table
      headers={["Key", "Summary", "Priority", "Status", "Created"]}
      columnAlign={["left", "left", "left", "left", "left"]}
      striped
      stickyHeader
      style={{ width: "100%", minWidth: 960 }}
      rows={bugs.map((bug) => [
        <Text key={bug.key} as="span" style={{ whiteSpace: "nowrap" }}>
          <Link href={bug.url}>{bug.key}</Link>
        </Text>,
        <Text truncate style={{ minWidth: 320, maxWidth: 560, display: "block" }}>{bug.summary}</Text>,
        <Text as="span" style={{ whiteSpace: "nowrap" }}>{bug.priority}</Text>,
        <Text as="span" style={{ whiteSpace: "nowrap" }}>{bug.status}</Text>,
        <Text as="span" style={{ whiteSpace: "nowrap" }}>{bug.created ?? ""}</Text>,
      ])}
      rowTone={bugs.map((bug) => (bug.tone === "neutral" ? undefined : bug.tone))}
    />
  );
}

function FailedTestsTable({ tests }: { tests: FailedTest[] }) {
  if (tests.length === 0) {
    return <Text size="small" tone="tertiary">No failed tests in Xray for this execution.</Text>;
  }
  return (
    <Table
      headers={["Test", "Summary"]}
      columnAlign={["left", "left"]}
      striped
      stickyHeader
      style={{ width: "100%", minWidth: 960 }}
      rows={tests.map((test) => [
        <Text key={test.key} as="span" style={{ whiteSpace: "nowrap" }}>
          <Link href={test.url}>{test.key}</Link>
        </Text>,
        <Text truncate style={{ minWidth: 320, maxWidth: 720, display: "block" }}>{test.summary}</Text>,
      ])}
      rowTone={tests.map(() => "danger" as const)}
    />
  );
}

function RunStatsBar({ stats }: { stats: RunStats }) {
  return (
    <Stack gap={8} style={{ minWidth: 0, width: "100%" }}>
      <UsageBar
        total={stats.total}
        topLeftLabel="Major Release Test Run results"
        topRightLabel={`${stats.executed} executed / ${stats.total} tests`}
        segments={[
          { id: "passed", value: stats.passed, color: "green" },
          { id: "failed", value: stats.failed, color: "red" },
          { id: "skipped", value: stats.skipped, color: "yellow" },
          { id: "todo", value: stats.todo, color: "gray" },
        ]}
      />
      <Row gap={16} wrap>
        <Stat value={String(stats.total)} label="Tests" />
        <Stat value={String(stats.executed)} label="Executed" />
        <Stat value={String(stats.passed)} label="Passed" tone="success" />
        <Stat value={String(stats.failed)} label="Failed" tone="danger" />
        <Stat value={String(stats.skipped)} label="Skipped" tone="warning" />
      </Row>
      <Text size="small" tone="tertiary">
        Passed, failed, and skipped are Xray status names. Skipped includes ABORTED. Executed excludes TO DO and EXECUTING. Source: Xray Cloud.
      </Text>
    </Stack>
  );
}

function formatCount(value: number | null | undefined): string {
  return value != null ? String(value) : "—";
}

function comparisonValue(release: Release, metric: string): string {
  switch (metric) {
    case "days":
      if (release.days != null) {
        return String(release.days);
      }
      return release.released ? "—" : "Not released";
    case "tests_total":
      return formatCount(release.testsTotal);
    case "tests_executed":
      return formatCount(release.testsExecuted);
    case "tests_passed":
      return formatCount(release.testsPassed);
    case "tests_failed":
      return formatCount(release.testsFailed);
    case "tests_skipped":
      return formatCount(release.testsSkipped);
    case "tests_todo":
      return formatCount(release.testsTodo);
    case "linked":
      return String(release.bugsTestRunCount);
    case "other":
      return String(release.bugsOtherCount);
    case "duration":
      if (release.testRunDurationDays == null) {
        return "—";
      }
      return `${release.testRunDurationDays} day${release.testRunDurationDays === 1 ? "" : "s"}`;
    case "qa":
      return release.qaEngineersCount != null ? String(release.qaEngineersCount) : "—";
    case "customer":
      return String(release.bugsCustomerReportedCount);
    default:
      return "—";
  }
}

const COMPARISON_METRICS: { id: string; label: string }[] = [
  { id: "days", label: "Days cut-off → production" },
  { id: "tests_total", label: "Test run — tests" },
  { id: "tests_executed", label: "Test run — executed" },
  { id: "tests_passed", label: "Test run — passed" },
  { id: "tests_failed", label: "Test run — failed" },
  { id: "tests_skipped", label: "Test run — skipped" },
  { id: "tests_todo", label: "Test run — to do" },
  { id: "duration", label: "Test run duration (weekdays)" },
  { id: "linked", label: "Linked bugs" },
  { id: "other", label: "Other bugs since cut-off" },
  { id: "customer", label: "Customer-reported (SUPPORT link)" },
  { id: "qa", label: "QA engineers (test executors)" },
];

function ComparisonTable() {
  const theme = useHostTheme();
  const border = `1px solid ${theme.stroke.primary}`;
  const releaseHeaders = RELEASES.map((release) => (
    <Text key={release.version} as="span" weight="semibold" style={{ whiteSpace: "nowrap" }}>
      {release.version}
    </Text>
  ));
  const valueRows = COMPARISON_METRICS.map((metric) =>
    RELEASES.map((release) => comparisonValue(release, metric.id))
  );

  return (
    <Stack gap={8} style={{ width: "100%", maxWidth: "100%", minWidth: 0 }}>
      <H2>Release comparison</H2>
      <div
        style={{
          display: "flex",
          width: "100%",
          maxWidth: "100%",
          minWidth: 0,
          border,
          borderRadius: 8,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            flexShrink: 0,
            width: 272,
            borderRight: border,
            background: theme.bg.editor,
          }}
        >
          <Table
            headers={["Metric"]}
            columnAlign={["left"]}
            striped
            stickyHeader
            framed={false}
            style={{ width: 272 }}
            rows={COMPARISON_METRICS.map((metric) => [
              <Text key={metric.id} as="span" style={{ whiteSpace: "nowrap" }}>
                {metric.label}
              </Text>,
            ])}
          />
        </div>
        <div
          style={{
            flex: 1,
            minWidth: 0,
            overflowX: "auto",
            WebkitOverflowScrolling: "touch",
          }}
        >
          <Table
            headers={releaseHeaders}
            columnAlign={RELEASES.map(() => "right")}
            striped
            stickyHeader
            framed={false}
            style={{ minWidth: RELEASES.length * 76 }}
            rows={valueRows}
          />
        </div>
      </div>
      <Text size="small" tone="tertiary">
        Metric labels stay fixed; scroll release columns horizontally. Test run counts from Xray (Major Release Test Run). Other bugs = cut-off JQL minus test-run links (0 when Jira returns no preprod affectedVersion bugs).
      </Text>
    </Stack>
  );
}

function ReleaseSection({ release, open }: { release: Release; open: boolean }) {
  const trailing = release.released
    ? `Released ${release.releaseDate}`
    : "Not released";
  return (
    <CollapsibleSection
      title={`Cloud ${release.version}`}
      count={release.bugCount}
      defaultOpen={open}
      trailing={<Text size="small">{trailing}</Text>}
    >
      <Stack gap={16} style={{ minWidth: 0, width: "100%" }}>
        <Row gap={20} wrap>
          <Stat value={release.cutoff ?? "Unknown"} label="Cut off from develop" />
          <Stat
            value={release.released ? (release.releaseDate ?? "Released") : "Not released"}
            label={release.released ? "Production release (first Done signal)" : "Production release"}
            tone={release.released ? "success" : "warning"}
          />
          {release.released && release.releaseTriggerUrl && release.releaseTriggerKey && (
            <Stack gap={4}>
              <Text size="small" tone="secondary">Trigger bug (test run → Done + cloud fix)</Text>
              <Link href={release.releaseTriggerUrl}>{release.releaseTriggerKey}</Link>
            </Stack>
          )}
          {release.days != null && (
            <Stat value={String(release.days)} label="Days from cut-off to production" />
          )}
          <Stat
            value={String(release.bugsTestRunCount)}
            label="Linked bugs"
            tone="info"
          />
          <Stat value={String(release.bugsOtherCount)} label="Other bugs since cut-off" />
          <Stat
            value={String(release.bugsCustomerReportedCount)}
            label="Customer-reported (SUPPORT)"
            tone={release.bugsCustomerReportedCount > 0 ? "warning" : "neutral"}
          />
          <Stat
            value={
              release.testRunDurationDays != null
                ? `${release.testRunDurationDays} day${release.testRunDurationDays === 1 ? "" : "s"}`
                : "Unknown"
            }
            label="Test run duration (weekdays)"
            tone={release.testRunDurationDays != null ? "info" : "warning"}
          />
          <Stat
            value={release.qaEngineersCount != null ? String(release.qaEngineersCount) : "Unknown"}
            label="QA engineers (test executors)"
            tone={release.qaEngineersCount != null ? "info" : "warning"}
          />
        </Row>
        {release.qaEngineerNames.length > 0 && (
          <Text size="small" tone="tertiary">
            {`Distinct executors: ${release.qaEngineerNames.join(", ")}.`}
          </Text>
        )}
        {release.testRunFirstStatus && release.testRunLastStatus && (
          <Text size="small" tone="tertiary">
            {release.testRunTimingRule
              ? `${release.testRunTimingRule} First status change: ${release.testRunFirstStatus}; last: ${release.testRunLastStatus}.`
              : `First test status change: ${release.testRunFirstStatus}; last: ${release.testRunLastStatus}.`}
          </Text>
        )}

        <Grid columns="minmax(0, 1fr) minmax(200px, 280px)" gap={20} align="start">
          <Stack gap={8}>
            <H3>{release.singleRun ? "Major Release Test Run" : "Major Release Test Runs"}</H3>
            {release.runs.map((run) => (
              <Stack key={run.key} gap={6}>
                <Text>
                  <Link href={run.url}>{run.key}</Link>
                  {" · "}
                  {run.status}
                  {run.created ? ` · created ${run.created}` : ""}
                  {` · ${run.linkedBugs} linked bugs`}
                </Text>
                <Text tone="secondary">{run.summary}</Text>
                {run.stats ? <RunStatsBar stats={run.stats} /> : null}
              </Stack>
            ))}
            {release.runs.length > 0 && release.runs.every((run) => run.stats == null) && (
              <Text size="small" tone="tertiary">
                Pass, fail, and skipped counts come from the Xray API. They are not on the Jira issue.
              </Text>
            )}
            {release.preprodName && (
              <Text size="small" tone="tertiary">
                Cut-off is the date in the ONE version {release.preprodName}. Branch creation time is not available from Jira.
              </Text>
            )}
          </Stack>
          <Stack gap={8}>
            <H3>Bugs by priority</H3>
            <PieChart donut data={release.slices} />
            <Text size="small" tone="tertiary">
              {`Cut-off scope: Affected Version ${release.preprodName ?? release.version}, created on or after ${release.cutoff}. Source: Jira, gathered ${release.gatheredAt}.`}
            </Text>
          </Stack>
        </Grid>

        <Stack gap={24} style={{ width: "100%" }}>
          <CollapsibleSection
            title="Failed tests (Xray test runs)"
            count={release.failedTests.length}
            defaultOpen={release.failedTests.length > 0 && release.failedTests.length <= 8}
          >
            <Stack gap={8} style={{ width: "100%" }}>
              <Text size="small" tone="tertiary">
                {release.failedTestsSource
                  ?? "Latest status FAILED in the Major Release Test Execution. Links open the Xray Testing Board test run."}
                {release.bugsTestRunKey
                  ? ` Execution: ${release.bugsTestRunKey}.`
                  : ""}
              </Text>
              <FailedTestsTable tests={release.failedTests} />
            </Stack>
          </CollapsibleSection>
          <CollapsibleSection
            title="Linked bugs (Major Release Test Run)"
            count={release.bugsTestRunCount}
            defaultOpen={false}
          >
            <Stack gap={8} style={{ width: "100%" }}>
              {release.bugsTestRunKey && (
                <Text size="small" tone="tertiary">
                  {`${release.bugsTestRunCount} defects · issue in linkedIssues("${release.bugsTestRunKey}")`}
                </Text>
              )}
              <BugTable bugs={release.bugsLinked} />
              {release.bugsTestRunUrl && (
                <Text size="small">
                  <Link href={release.bugsTestRunUrl}>Open in Jira</Link>
                </Text>
              )}
            </Stack>
          </CollapsibleSection>
          <CollapsibleSection
            title="Other bugs since cut-off"
            count={release.bugsOtherCount}
            defaultOpen={false}
          >
            <Stack gap={8} style={{ width: "100%" }}>
              <Text size="small" tone="tertiary">
                {`Preprod affectedVersion + created ≥ cut-off, not linked from ${release.bugsTestRunKey ?? "test run"}.`}
              </Text>
              <BugTable bugs={release.bugsOther} />
              {release.bugsOtherUrl && (
                <Text size="small">
                  <Link href={release.bugsOtherUrl}>Open in Jira</Link>
                </Text>
              )}
            </Stack>
          </CollapsibleSection>
          <CollapsibleSection
            title="Customer-reported bugs (linked SUPPORT)"
            count={release.bugsCustomerReportedCount}
            defaultOpen={false}
          >
            <Stack gap={8} style={{ width: "100%" }}>
              <Text size="small" tone="tertiary">
                {release.bugsCustomerReportedRule
                  ?? "Bugs with this train's preprod Affected Version and a Jira link to a SUPPORT ticket."}
              </Text>
              <CustomerBugTable bugs={release.bugsCustomerReported} />
              {release.bugsCustomerReportedUrl && (
                <Text size="small">
                  <Link href={release.bugsCustomerReportedUrl}>Open in Jira</Link>
                </Text>
              )}
            </Stack>
          </CollapsibleSection>
          {release.knownIssuesBreakdown.length > 0 && (
            <Stack gap={12} style={{ width: "100%" }}>
              <H3>Known issues after release (Git placement)</H3>
              {release.knownIssuesUrl && (
                <Text size="small" tone="tertiary">
                  Dynamic filter ({release.knownIssuesName ?? "known issues"}):{" "}
                  <Link href={release.knownIssuesUrl}>Open all in Jira</Link>
                </Text>
              )}
              {release.knownIssuesBreakdown.map((group) => (
                <CollapsibleSection
                  key={group.id}
                  title={group.title}
                  count={group.count}
                  defaultOpen={false}
                >
                  <Stack gap={8} style={{ width: "100%" }}>
                    {group.description && (
                      <Text size="small" tone="tertiary">{group.description}</Text>
                    )}
                    {group.gitBranch && (
                      <Text size="small" tone="tertiary">
                        {`Git branch: ${group.gitBranch}`}
                      </Text>
                    )}
                    {group.url && (
                      <Text size="small">
                        <Link href={group.url}>Open in Jira</Link>
                        {group.jql ? ` · ${group.jql}` : ""}
                      </Text>
                    )}
                    <BugTable bugs={group.bugs ?? []} />
                  </Stack>
                </CollapsibleSection>
              ))}
            </Stack>
          )}
        </Stack>

        {release.cloudVersions.length > 0 && (
          <Stack gap={8}>
            <H3>bigpicture-cloud versions</H3>
            <Table
              headers={["Version", "Status", "Planned / Jira date"]}
              columnAlign={["left", "left", "left"]}
              style={{ width: "100%", minWidth: 0 }}
              rows={release.cloudVersions.map((item) => [
                <Link key={item.name} href={item.url}>{item.name}</Link>,
                item.statusLabel,
                item.releaseDate ?? "",
              ])}
              rowTone={release.cloudVersions.map((item) =>
                item.statusLabel.startsWith("Production") || item.released ? "success" : "warning"
              )}
            />
            {release.planned && (
              <Text size="small" tone="tertiary">
                {release.planned}. Jira planned dates on unreleased cloud versions are informational only.
              </Text>
            )}
            {release.releaseRule && (
              <Text size="small" tone="tertiary">
                {release.releaseRule}
                {release.releaseDateLast && release.releaseDateLast !== release.releaseDate
                  ? ` Last qualifying Done: ${release.releaseDateLast}.`
                  : ""}
              </Text>
            )}
          </Stack>
        )}

        {release.bugUrl && (
          <Text size="small" tone="tertiary">
            <Link href={release.bugUrl}>Open full cut-off bug query in Jira</Link>
          </Text>
        )}

        {release.notes.map((note) => (
          <Callout key={note} tone="warning">{note}</Callout>
        ))}
      </Stack>
    </CollapsibleSection>
  );
}

export default function ReleaseStats() {
  return (
    <Stack gap={20} style={{ width: "100%", maxWidth: "none", alignSelf: "stretch" }}>
      <Stack gap={6}>
        <H1>BigPicture Cloud release stats</H1>
        <Text tone="secondary">
          One section per Cloud train. Cut-off, Major Release Test Run, bugs since cut-off, and production release date from the first test-run bug Done with a matching bigpicture-cloud fix version.
        </Text>
        <Text size="small" tone="tertiary">
          Source: Jira project ONE and TC on appfire.atlassian.net. Gathered __GATHERED__. Test counts from Xray Cloud (`Trinity/studio/.env.production`).
        </Text>
      </Stack>
      <Divider />
      <ComparisonTable />
      <Divider />
      <Stack gap={4}>
        {RELEASES.map((release, index) => (
          <ReleaseSection key={release.version} release={release} open={index === 0} />
        ))}
      </Stack>
    </Stack>
  );
}
'''


if __name__ == "__main__":
    raise SystemExit(main())
