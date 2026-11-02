#!/usr/bin/env python3
"""Strip MCP searchJiraIssuesUsingJql payload to key + issuelinks (minimal fields)."""

from __future__ import annotations

import json
import sys


def slim_wrap(wrap: dict) -> dict:
    data = wrap.get("data") or wrap
    if wrap.get("error"):
        raise SystemExit(f"MCP error: {wrap.get('message')}")
    slim_issues = []
    for issue in data.get("issues") or []:
        links = (issue.get("fields") or {}).get("issuelinks") or []
        slim_links = []
        for link in links:
            slim_link: dict = {"type": {"name": (link.get("type") or {}).get("name")}}
            for side in ("inwardIssue", "outwardIssue"):
                other = link.get(side)
                if other and other.get("key"):
                    slim_link[side] = {"key": other["key"]}
            slim_links.append(slim_link)
        slim_issues.append({"key": issue["key"], "fields": {"issuelinks": slim_links}})
    return {"data": {"issues": slim_issues}}


def main() -> int:
    wrap = json.loads(sys.stdin.read())
    sys.stdout.write(json.dumps(slim_wrap(wrap), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
