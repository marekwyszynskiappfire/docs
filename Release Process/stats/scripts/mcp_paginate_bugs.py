#!/usr/bin/env python3
"""Print JQL bug-search commands for MCP pagination (operator runs via Atlassian MCP).

Reads manifest trains 8.62-8.73 and prints version, jql, and page count from count API
already gathered. Does not call Jira.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "Release Process" / "stats" / "trains_since_2025-10-01.json"
PAGES = {"8.68": 4, "8.70": 8}


def main() -> None:
    for entry in json.loads(MANIFEST.read_text()):
        v = entry["version"]
        if v not in PAGES:
            continue
        jql = (
            f'issuetype = Bug AND affectedVersion = "{entry["preprod_name"]}" '
            f'AND created >= "{entry["cutoff_date"]}" ORDER BY priority DESC, created ASC'
        )
        print(f"{v}\t{PAGES[v]}\t{jql}")


if __name__ == "__main__":
    main()
