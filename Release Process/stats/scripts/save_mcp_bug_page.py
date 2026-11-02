#!/usr/bin/env python3
"""Save MCP searchJiraIssuesUsingJql JSON (stdin) to _fetch/{version}/bugs_page_{n}.json and append."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FETCH = ROOT / "Release Process" / "stats" / "mcp_import" / "_fetch"
APPEND = ROOT / "Release Process" / "stats" / "scripts" / "append_mcp_bugs.py"


def main() -> int:
    if len(sys.argv) not in (3, 4):
        print("usage: save_mcp_bug_page.py VERSION PAGE_INDEX [mcp.json]", file=sys.stderr)
        return 2
    version, page_idx = sys.argv[1], sys.argv[2]
    if len(sys.argv) == 4:
        payload = json.loads(Path(sys.argv[3]).read_text())
    else:
        payload = json.load(sys.stdin)
    vdir = FETCH / version
    vdir.mkdir(parents=True, exist_ok=True)
    path = vdir / f"bugs_page_{int(page_idx):03d}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    subprocess.run([sys.executable, str(APPEND), version, str(path)], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
