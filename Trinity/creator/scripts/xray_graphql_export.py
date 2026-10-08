#!/usr/bin/env python3
"""Export Xray tests (steps, folder, coverable issues) for Creator golden / RAG corpora.

Uses Xray Cloud GraphQL getTests in small issueId batches with a worker pool.
Jira issue keys + numeric ids must be supplied (--issues-json); collect them with
Jira filter/search (e.g. filter=17844) separately.

Auth:
  XRAY_CLIENT_ID, XRAY_CLIENT_SECRET (Xray Global Settings API keys)

Usage:
  python3 xray_graphql_export.py \\
    --issues-json path/to/issues.json \\
    --out-dir Trinity/creator/golden/v2/filter-17844 \\
    --workers 6 --batch-size 8
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = (
    SCRIPT_DIR.parent.parent.parent
    / "The Creator/Input/Marek/_shared/config/jira_xray_mapping.json"
)

GET_TESTS_QUERY = """
query ExportTests($issueIds: [String], $limit: Int!) {
  getTests(issueIds: $issueIds, limit: $limit) {
    total
    results {
      issueId
      testType { name kind }
      unstructured
      gherkin
      folder { path name }
      steps {
        id
        action
        data
        result
      }
      preconditions(limit: 20, start: 0) {
        total
        results {
          issueId
          definition
          jira(fields: ["key", "summary"])
        }
      }
      coverableIssues(limit: 50, start: 0) {
        total
        results {
          issueId
          jira(fields: ["key", "summary", "issuetype"])
        }
      }
      jira(fields: [
        "key", "summary", "description", "status", "priority",
        "assignee", "reporter", "created", "updated", "labels"
      ])
    }
  }
}
""".strip()

_INSECURE_SSL = False
_token_lock = threading.Lock()
_cached_token: str | None = None


def ssl_context() -> ssl.SSLContext:
    if _INSECURE_SSL or os.environ.get("XRAY_INSECURE_SSL", "").lower() in ("1", "true", "yes"):
        return ssl._create_unverified_context()
    return ssl.create_default_context()


def urlopen(req: urllib.request.Request, *, timeout: int = 120):
    return urllib.request.urlopen(req, timeout=timeout, context=ssl_context())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    return load_json(path)


def authenticate(config: dict[str, Any]) -> str:
    global _cached_token
    with _token_lock:
        if _cached_token:
            return _cached_token
        client_id = os.environ.get("XRAY_CLIENT_ID")
        client_secret = os.environ.get("XRAY_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise RuntimeError("Set XRAY_CLIENT_ID and XRAY_CLIENT_SECRET")
        url = config["xray"]["auth_url"]
        payload = json.dumps({"client_id": client_id, "client_secret": client_secret}).encode()
        req = urllib.request.Request(
            url,
            data=payload,
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
        _cached_token = token
        return token


def graphql_request(
    config: dict[str, Any],
    token: str,
    query: str,
    variables: dict[str, Any],
    *,
    retries: int = 5,
) -> dict[str, Any]:
    url = config["xray"]["graphql_url"]
    payload = json.dumps({"query": query, "variables": variables}).encode()
    last_err: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=180) as resp:
                body = json.loads(resp.read().decode())
            if body.get("errors"):
                msg = json.dumps(body["errors"])[:800]
                raise RuntimeError(f"GraphQL errors: {msg}")
            return body
        except (urllib.error.HTTPError, TimeoutError, RuntimeError) as exc:
            last_err = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in (429, 502, 503, 504):
                err_body = exc.read().decode(errors="replace")[:500]
                raise RuntimeError(f"HTTP {exc.code}: {err_body}") from exc
            time.sleep(min(2 ** attempt, 30))
    raise RuntimeError(f"GraphQL request failed after {retries} attempts: {last_err}")


def jira_person_name(field: Any) -> str | None:
    if not field or not isinstance(field, dict):
        return None
    return field.get("displayName") or field.get("name")


def jira_status_name(field: Any) -> str | None:
    if not field or not isinstance(field, dict):
        return None
    return field.get("name")


def jira_priority_name(field: Any) -> str | None:
    if not field or not isinstance(field, dict):
        return None
    return field.get("name")


def normalize_test(raw: dict[str, Any], site_url: str) -> dict[str, Any]:
    jira = raw.get("jira") or {}
    key = jira.get("key")
    folder = raw.get("folder") or {}
    folder_path = folder.get("path") or folder.get("name") or ""
    steps_out: list[dict[str, Any]] = []
    for idx, step in enumerate(raw.get("steps") or [], start=1):
        steps_out.append({
            "step": idx,
            "action": (step.get("action") or "").strip(),
            "data": (step.get("data") or "").strip(),
            "result": (step.get("result") or "").strip(),
        })
    coverable: list[dict[str, str]] = []
    for cov in (raw.get("coverableIssues") or {}).get("results") or []:
        cj = cov.get("jira") or {}
        if cj.get("key"):
            coverable.append({
                "key": cj["key"],
                "summary": cj.get("summary") or "",
                "issuetype": (cj.get("issuetype") or {}).get("name") or "",
            })
    preconditions: list[dict[str, Any]] = []
    for pre in (raw.get("preconditions") or {}).get("results") or []:
        pj = pre.get("jira") or {}
        preconditions.append({
            "key": pj.get("key"),
            "summary": pj.get("summary") or "",
            "definition": (pre.get("definition") or "").strip(),
        })
    test_type = (raw.get("testType") or {}).get("name") or "Manual"
    return {
        "key": key,
        "issue_id": raw.get("issueId"),
        "url": f"{site_url}/browse/{key}" if key else None,
        "summary": jira.get("summary") or "",
        "description": jira.get("description") or "",
        "status": jira_status_name(jira.get("status")),
        "priority": jira_priority_name(jira.get("priority")),
        "assignee": jira_person_name(jira.get("assignee")),
        "reporter": jira_person_name(jira.get("reporter")),
        "created": jira.get("created"),
        "updated": jira.get("updated"),
        "labels": jira.get("labels") or [],
        "test_type": test_type,
        "folder": folder_path,
        "unstructured": (raw.get("unstructured") or "").strip(),
        "gherkin": (raw.get("gherkin") or "").strip(),
        "steps": steps_out,
        "preconditions": preconditions,
        "coverable_issues": coverable,
        "step_count": len(steps_out),
    }


def rag_document(test: dict[str, Any], filter_meta: dict[str, Any]) -> dict[str, Any]:
    """One RAG-ready record per test (JSONL line)."""
    lines = [
        f"Test: {test.get('key')} — {test.get('summary')}",
        f"Priority: {test.get('priority')} | Status: {test.get('status')} | Type: {test.get('test_type')}",
        f"Folder: {test.get('folder')}",
    ]
    if test.get("labels"):
        lines.append(f"Labels: {', '.join(test['labels'])}")
    if test.get("description"):
        lines.append("")
        lines.append("Description:")
        lines.append(test["description"])
    if test.get("preconditions"):
        lines.append("")
        lines.append("Preconditions:")
        for p in test["preconditions"]:
            lines.append(f"- {p.get('key')}: {p.get('summary')}")
            if p.get("definition"):
                lines.append(p["definition"])
    if test.get("coverable_issues"):
        lines.append("")
        lines.append("Covers:")
        for c in test["coverable_issues"]:
            lines.append(f"- {c['key']} ({c.get('issuetype')}): {c.get('summary')}")
    if test.get("steps"):
        lines.append("")
        lines.append("Steps:")
        for s in test["steps"]:
            lines.append(f"{s['step']}. {s['action']}")
            if s.get("data"):
                lines.append(f"   Data: {s['data']}")
            lines.append(f"   Expected: {s['result']}")
    text = "\n".join(lines).strip()
    return {
        "id": test.get("key"),
        "text": text,
        "metadata": {
            "jira_key": test.get("key"),
            "issue_id": test.get("issue_id"),
            "summary": test.get("summary"),
            "priority": test.get("priority"),
            "status": test.get("status"),
            "test_type": test.get("test_type"),
            "folder": test.get("folder"),
            "labels": test.get("labels"),
            "step_count": test.get("step_count"),
            "filter_id": filter_meta.get("filter_id"),
            "filter_name": filter_meta.get("filter_name"),
            "source": "xray_graphql_export",
        },
    }


def load_issues(path: Path) -> list[dict[str, str]]:
    data = load_json(path)
    if isinstance(data, dict) and "issues" in data:
        issues = data["issues"]
    elif isinstance(data, list):
        issues = data
    else:
        raise ValueError("issues-json must be a list or {\"issues\": [...]}")
    out: list[dict[str, str]] = []
    for item in issues:
        if isinstance(item, str):
            out.append({"key": item, "id": ""})
            continue
        key = item.get("key") or item.get("jira_key")
        issue_id = str(item.get("id") or item.get("issue_id") or item.get("issueId") or "")
        if not key:
            continue
        out.append({"key": key, "id": issue_id})
    return out


def fetch_batch(
    batch_index: int,
    issue_ids: list[str],
    config: dict[str, Any],
    token: str,
    batch_size: int,
    raw_dir: Path,
) -> list[dict[str, Any]]:
    variables = {"issueIds": issue_ids, "limit": min(batch_size, len(issue_ids))}
    body = graphql_request(config, token, GET_TESTS_QUERY, variables)
    raw_path = raw_dir / f"batch-{batch_index:05d}.json"
    raw_path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    results = (body.get("data") or {}).get("getTests", {}).get("results") or []
    return results


def write_markdown_index(path: Path, meta: dict[str, Any], tests: list[dict[str, Any]]) -> None:
    total_steps = sum(t.get("step_count", 0) for t in tests)
    lines = [
        f"# Xray extract — filter {meta.get('filter_id')}",
        "",
        f"**Run ID:** `{meta.get('run_id')}`  ",
        f"**Extracted:** {meta.get('extracted_at', '')[:10]}  ",
        f"**Source:** Xray Cloud GraphQL API  ",
        f"**Tests:** {len(tests)}  ",
        f"**Total steps:** {total_steps}  ",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Filter | [{meta.get('filter_name')}]({meta.get('filter_url')}) |",
        f"| Tests extracted | {len(tests)} |",
        f"| Total steps | {total_steps} |",
        "",
        "## Test index",
        "",
        "| # | Title | Priority | Steps | Key |",
        "|---|-------|----------|-------|-----|",
    ]
    for i, t in enumerate(sorted(tests, key=lambda x: x.get("key") or ""), start=1):
        title = (t.get("summary") or "").replace("|", "\\|")[:80]
        lines.append(
            f"| {i} | {title} | {t.get('priority') or ''} | {t.get('step_count', 0)} | {t.get('key')} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Xray tests via GraphQL (batched workers)")
    parser.add_argument("--issues-json", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--filter-id", type=str, default="")
    parser.add_argument("--filter-name", type=str, default="")
    parser.add_argument("--filter-jql", type=str, default="")
    parser.add_argument("--resume", action="store_true", help="Skip batches whose raw JSON already exists")
    args = parser.parse_args()

    if args.batch_size < 1 or args.batch_size > 25:
        print("batch-size must be between 1 and 25", file=sys.stderr)
        return 2
    if args.workers < 1 or args.workers > 16:
        print("workers must be between 1 and 16", file=sys.stderr)
        return 2

    config = load_config(args.config)
    site_url = config.get("jira", {}).get("site_url", "https://appfire.atlassian.net").rstrip("/")
    issues = load_issues(args.issues_json)
    if not issues:
        print("No issues in issues-json", file=sys.stderr)
        return 1

    # Resolve missing numeric ids via key-only batches (Xray accepts jql key=TC-1)
    missing_id = [i for i in issues if not i["id"]]
    if missing_id:
        print(f"Warning: {len(missing_id)} issues missing Jira id; export uses issueIds only when present", file=sys.stderr)

    issue_ids = [i["id"] for i in issues if i["id"]]
    if len(issue_ids) != len(issues):
        print("All issues must include Jira numeric id for getTests(issueIds)", file=sys.stderr)
        return 1

    out_dir = args.out_dir
    raw_dir = out_dir / "raw-batches"
    rag_dir = out_dir / "rag"
    by_key_dir = rag_dir / "by-key"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    rag_dir.mkdir(parents=True, exist_ok=True)
    by_key_dir.mkdir(parents=True, exist_ok=True)

    run_id = f"xray-filter-{args.filter_id or 'export'}"
    extracted_at = datetime.now(timezone.utc).isoformat()
    filter_meta = {
        "filter_id": args.filter_id,
        "filter_name": args.filter_name,
        "filter_jql": args.filter_jql,
        "filter_url": f"{site_url}/issues/?filter={args.filter_id}" if args.filter_id else "",
        "run_id": run_id,
        "extracted_at": extracted_at,
    }

    batches: list[tuple[int, list[str]]] = []
    for i in range(0, len(issue_ids), args.batch_size):
        chunk = issue_ids[i : i + args.batch_size]
        batches.append((i // args.batch_size, chunk))

    token = authenticate(config)
    all_raw: list[dict[str, Any]] = []
    errors: list[str] = []

    def work(item: tuple[int, list[str]]) -> tuple[int, list[dict[str, Any]] | None, str | None]:
        batch_index, ids = item
        raw_path = raw_dir / f"batch-{batch_index:05d}.json"
        if args.resume and raw_path.exists():
            body = load_json(raw_path)
            results = (body.get("data") or {}).get("getTests", {}).get("results") or []
            return batch_index, results, None
        try:
            results = fetch_batch(batch_index, ids, config, token, args.batch_size, raw_dir)
            return batch_index, results, None
        except Exception as exc:  # noqa: BLE001
            return batch_index, None, str(exc)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(work, b) for b in batches]
        for fut in as_completed(futures):
            batch_index, results, err = fut.result()
            if err:
                errors.append(f"batch {batch_index}: {err}")
            elif results is not None:
                all_raw.extend(results)

    if errors:
        err_path = out_dir / "export-errors.json"
        err_path.write_text(json.dumps(errors, indent=2) + "\n", encoding="utf-8")
        print(f"{len(errors)} batch errors (see {err_path})", file=sys.stderr)

    tests = [normalize_test(r, site_url) for r in all_raw]
    tests.sort(key=lambda t: t.get("key") or "")

    manifest = {
        **filter_meta,
        "source": "Xray Cloud GraphQL API",
        "issue_count_requested": len(issue_ids),
        "test_count": len(tests),
        "total_steps": sum(t.get("step_count", 0) for t in tests),
        "batch_count": len(batches),
        "workers": args.workers,
        "batch_size": args.batch_size,
        "errors": errors,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    corpus = {
        "extracted_at": extracted_at,
        "source": "Xray Cloud GraphQL API",
        "filter": filter_meta,
        "test_count": len(tests),
        "tests": tests,
    }
    (out_dir / "extraction.json").write_text(json.dumps(corpus, indent=2) + "\n", encoding="utf-8")
    write_markdown_index(out_dir / "extraction.md", filter_meta, tests)

    chunks_path = rag_dir / "chunks.jsonl"
    with chunks_path.open("w", encoding="utf-8") as fh:
        for test in tests:
            doc = rag_document(test, filter_meta)
            fh.write(json.dumps(doc, ensure_ascii=False) + "\n")
            key = test.get("key")
            if key:
                (by_key_dir / f"{key}.json").write_text(
                    json.dumps({"test": test, "rag": doc}, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )

    print(
        f"Exported {len(tests)} tests ({manifest['total_steps']} steps) → {out_dir}",
        file=sys.stderr,
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
