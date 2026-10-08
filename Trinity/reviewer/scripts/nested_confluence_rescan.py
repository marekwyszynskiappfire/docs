#!/usr/bin/env python3
"""Nested Confluence hop (SKILL step 8) — discover, cache, apply to ReviewPayloads.

Workflow:
  1. discover — scan payloads; write _gather/nested-rescan/fetch-queue.json
  2. (MCP) fetch each queue item → _gather/nested-rescan/cache/{pageId}.json
     Use getConfluenceContent for version, then executeRead getConfluenceContentVersion markdown.
  3. apply — per epic: parse parent bodies, fetch nested from cache (max 10/epic), merge context_loaded

Usage:
  python3 nested_confluence_rescan.py discover --run-dir PATH
  python3 nested_confluence_rescan.py apply --run-dir PATH
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PAGE_ID_RE = re.compile(r"/pages/(\d+)", re.I)
WIKI_HOST_RE = re.compile(
    r"https://(?P<host>appfire(?:team)?\.atlassian\.net)/wiki[^\s\)\]\"']+",
    re.I,
)
EXTERNAL_RE = re.compile(
    r"https://(?:docs\.google\.com|drive\.google\.com|[^\s]+?\.pdf)(?:[^\s\)\]\"']*)",
    re.I,
)
MAX_NESTED_PER_EPIC = 10
CLOUD_BY_HOST = {
    "appfire.atlassian.net": "8e83c2b4-97ae-4335-8a8f-bbdff09d62dd",
    "appfireteam.atlassian.net": "47e8fae1-6b9b-428b-9308-1e15fde8fe5f",
}


def epic_dirs(run_dir: Path) -> list[Path]:
    out = []
    for child in run_dir.iterdir():
        if not child.is_dir():
            continue
        if re.match(r"^[A-Z][A-Z0-9]+-\d+$", child.name):
            p = child / "review-payload.json"
            if p.is_file():
                out.append(child)
    return sorted(out, key=lambda p: p.name)


def text_blob(p: dict) -> str:
    parts: list[str] = []
    req = (p.get("requirements") or [{}])[0]
    parts.append(req.get("description_excerpt") or "")
    for c in (p.get("rollup") or {}).get("epic_child_inventory") or []:
        parts.append(c.get("summary") or "")
        parts.append(c.get("description_excerpt") or "")
    for cl in p.get("context_loaded") or []:
        parts.append(cl.get("source") or "")
        parts.append(cl.get("detail") or "")
    rep = p.get("report") or {}
    for key in ("facts", "risks", "design_observations", "epic_context"):
        for item in rep.get(key) or []:
            parts.append(item.get("text") or "")
    return "\n".join(parts)


def page_ids_in_text(text: str) -> set[str]:
    return set(PAGE_ID_RE.findall(text or ""))


def known_page_ids(p: dict) -> set[str]:
    ids = page_ids_in_text(text_blob(p))
    for cl in p.get("context_loaded") or []:
        if cl.get("type") in ("confluence_page", "external_document"):
            ids |= page_ids_in_text((cl.get("source") or "") + " " + (cl.get("detail") or ""))
    return ids


def extract_links(markdown: str) -> tuple[set[str], set[str]]:
    wiki_ids: set[str] = set()
    externals: set[str] = set()
    for m in PAGE_ID_RE.finditer(markdown or ""):
        wiki_ids.add(m.group(1))
    for m in WIKI_HOST_RE.finditer(markdown or ""):
        wiki_ids |= page_ids_in_text(m.group(0))
    for m in EXTERNAL_RE.finditer(markdown or ""):
        externals.add(m.group(0)[:200])
    return wiki_ids, externals


def load_cache(cache_dir: Path, page_id: str) -> dict | None:
    path = cache_dir / f"{page_id}.json"
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def all_page_ids_in_payload(p: dict) -> set[str]:
    blob = json.dumps(p, ensure_ascii=False)
    ids = set(PAGE_ID_RE.findall(blob))
    ids |= {m for m in re.findall(r"\b(\d{9,12})\b", blob) if m.startswith(("99", "97", "98", "37", "29", "30", "20"))}
    return ids


def host_for_page(p: dict, pid: str) -> str:
    blob = json.dumps(p, ensure_ascii=False)
    if f"appfire.atlassian.net/wiki" in blob and pid in blob:
        # prefer appfire if that host appears near the id
        idx = blob.find(pid)
        window = blob[max(0, idx - 120) : idx + 40]
        if "appfire.atlassian.net" in window and "appfireteam" not in window:
            return "appfire.atlassian.net"
    return "appfireteam.atlassian.net"


def cache_write(run_dir: Path, page_id: str, title: str, version: int, markdown: str) -> Path:
    cache_dir = run_dir / "_gather" / "nested-rescan" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{page_id}.json"
    payload = {
        "pageId": page_id,
        "title": title,
        "version": version,
        "markdown": markdown,
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def discover_nested_from_cache(run_dir: Path) -> None:
    """Queue Confluence page IDs linked from cached bodies but not yet cached."""
    out_dir = run_dir / "_gather" / "nested-rescan"
    cache_dir = out_dir / "cache"
    queue_path = out_dir / "fetch-queue.json"
    existing = json.loads(queue_path.read_text(encoding="utf-8")) if queue_path.is_file() else {"pages": []}
    seen = {item["pageId"] for item in existing.get("pages") or []}
    for path in cache_dir.glob("*.json"):
        cached = json.loads(path.read_text(encoding="utf-8"))
        child_ids, _ = extract_links(cached.get("markdown") or "")
        for nid in child_ids:
            if nid in seen or load_cache(cache_dir, nid):
                continue
            seen.add(nid)
            existing.setdefault("pages", []).append(
                {
                    "pageId": nid,
                    "host": "appfireteam.atlassian.net",
                    "cloudId": CLOUD_BY_HOST["appfireteam.atlassian.net"],
                    "epic_hint": f"nested-from-{path.stem}",
                }
            )
    existing["generated_at"] = datetime.now(timezone.utc).isoformat()
    queue_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    pending = [p for p in existing["pages"] if not load_cache(cache_dir, p["pageId"])]
    print(f"discover_nested: {len(pending)} page(s) still need fetch → {queue_path}")


def discover(run_dir: Path) -> None:
    out_dir = run_dir / "_gather" / "nested-rescan"
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = out_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    queue: list[dict] = []
    seen: set[str] = set()
    for epic_dir in epic_dirs(run_dir):
        with (epic_dir / "review-payload.json").open(encoding="utf-8") as f:
            p = json.load(f)
        for pid in all_page_ids_in_payload(p):
            if pid in seen or load_cache(cache_dir, pid):
                continue
            seen.add(pid)
            host = host_for_page(p, pid)
            queue.append(
                {
                    "pageId": pid,
                    "host": host,
                    "cloudId": CLOUD_BY_HOST.get(host, CLOUD_BY_HOST["appfireteam.atlassian.net"]),
                    "epic_hint": epic_dir.name,
                }
            )
    (out_dir / "fetch-queue.json").write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "pages": queue}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"discover: {len(queue)} page(s) to fetch → {out_dir / 'fetch-queue.json'}")


def merge_context(p: dict, entry: dict) -> None:
    src = entry["source"]
    for cl in p.get("context_loaded") or []:
        if cl.get("source") == src and cl.get("type") == "confluence_page":
            cl["status"] = entry["status"]
            cl["detail"] = entry["detail"]
            return
    p.setdefault("context_loaded", []).append(entry)


def has_a8_external(p: dict) -> bool:
    return any(
        f.get("checklist_ref") == "A8" and f.get("status", "open") == "open"
        for f in p.get("findings") or []
    )


def apply(run_dir: Path) -> None:
    cache_dir = run_dir / "_gather" / "nested-rescan" / "cache"
    if not cache_dir.is_dir():
        raise SystemExit(f"Missing cache dir: {cache_dir} — run MCP fetch first")
    updated = 0
    for epic_dir in epic_dirs(run_dir):
        path = epic_dir / "review-payload.json"
        with path.open(encoding="utf-8") as f:
            p = json.load(f)
        epic_key = epic_dir.name
        known = all_page_ids_in_payload(p) | known_page_ids(p)
        nested_added = 0
        externals_found: set[str] = set()
        parents = sorted(known)
        for parent_id in parents:
            cached = load_cache(cache_dir, parent_id)
            if not cached:
                continue
            md = cached.get("markdown") or ""
            child_ids, ext = extract_links(md)
            externals_found |= ext
            for nid in sorted(child_ids):
                if nid in known or nested_added >= MAX_NESTED_PER_EPIC:
                    continue
                nc = load_cache(cache_dir, nid)
                if not nc:
                    continue
                title = nc.get("title") or f"page {nid}"
                excerpt = (nc.get("markdown") or "")[:280].replace("\n", " ")
                merge_context(
                    p,
                    {
                        "source": f"Confluence nested ({nid}) — {title}",
                        "type": "confluence_page",
                        "status": "analyzed",
                        "detail": (
                            f"Nested hop from parent {parent_id}; getConfluenceContentVersion markdown; "
                            f"excerpt: {excerpt}…"
                        ),
                    },
                )
                rep = p.setdefault("report", {})
                facts = rep.setdefault("facts", [])
                fact_text = f"Nested Confluence ({nid}): {title} — {excerpt[:160]}…"
                if not any(f.get("text") == fact_text for f in facts):
                    facts.append(
                        {
                            "text": fact_text,
                            "source": f"Confluence nested page {nid} (parent {parent_id})",
                        }
                    )
                known.add(nid)
                nested_added += 1

        if externals_found and not has_a8_external(p):
            sample = next(iter(externals_found))
            p.setdefault("findings", []).append(
                {
                    "finding_id": f"RR-{epic_key}-N8",
                    "jira_key": epic_key,
                    "severity": "MEDIUM",
                    "category": "traceability",
                    "checklist_ref": "A8",
                    "excerpt_quote": sample[:120],
                    "finding_summary": (
                        "Nested Confluence pages link external documents that may hold scope or AC; "
                        "content was not auto-fetched."
                    ),
                    "testing_impact": "Confirm whether linked external docs are binding before locking tests.",
                    "owner_hint": "PM",
                    "source": "nested_confluence_scan",
                    "blocks_test_generation": False,
                    "status": "open",
                }
            )

        if nested_added > 0 or externals_found:
            p["scan_label"] = "Rescan"
            note = (
                f"Nested Confluence rescan {datetime.now(timezone.utc).date()}: "
                f"+{nested_added} nested page(s) from parent bodies (max {MAX_NESTED_PER_EPIC}/epic)."
            )
            handoff = (p.get("report") or {}).get("handoff_note") or ""
            if note not in handoff:
                p.setdefault("report", {})["handoff_note"] = f"{handoff} {note}".strip()
            with path.open("w", encoding="utf-8") as f:
                json.dump(p, f, indent=2, ensure_ascii=False)
                f.write("\n")
            updated += 1
            print(f"{epic_key}: +{nested_added} nested")
    print(f"apply: updated {updated} payload(s)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Nested Confluence hop for Reviewer portfolio runs")
    ap.add_argument("command", choices=("discover", "discover_nested", "cache_write", "apply"))
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--page-id", type=str, default="")
    ap.add_argument("--title", type=str, default="")
    ap.add_argument("--version", type=int, default=0)
    ap.add_argument("--markdown-file", type=Path, default=None)
    args = ap.parse_args()
    run_dir = args.run_dir.resolve()
    if args.command == "discover":
        discover(run_dir)
    elif args.command == "discover_nested":
        discover_nested_from_cache(run_dir)
    elif args.command == "cache_write":
        if not args.page_id or not args.markdown_file:
            raise SystemExit("cache_write requires --page-id and --markdown-file")
        md = args.markdown_file.read_text(encoding="utf-8")
        path = cache_write(run_dir, args.page_id, args.title or f"page {args.page_id}", args.version, md)
        print(path)
    else:
        apply(run_dir)


if __name__ == "__main__":
    main()
