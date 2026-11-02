#!/usr/bin/env python3
"""
Agent-driven support link cache population.

For each batch index, call Atlassian MCP searchJiraIssuesUsingJql (see enrich_customer_support.py
CLOUD_ID), save JSON to /tmp/mcp_support/batch_{idx:03d}.json, then:

  python3 merge_support_link_batch.py /tmp/mcp_support/batch_{idx:03d}.json

Or merge all saved batches:

  python3 merge_support_batches_dir.py /tmp/mcp_support

mcp-remote subprocess does NOT inherit Cursor OAuth for appfire.atlassian.net; use plugin MCP in chat.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MERGE = ROOT / "Release Process/stats/scripts/merge_support_link_batch.py"
BATCHES = Path("/tmp/support_batches.json")
OUT_DIR = Path("/tmp/mcp_support")


def main() -> int:
    batches = json.loads(BATCHES.read_text())
    if len(sys.argv) == 1:
        for i in range(len(batches)):
            jql = f"key in ({', '.join(batches[i])})"
            print(f"batch {i:02d}: {len(batches[i])} keys -> /tmp/support_jql_{i}.txt")
        print(f"save MCP JSON to {OUT_DIR}/batch_{{idx:03d}}.json then merge_support_batches_dir.py")
        return 0
    idx = int(sys.argv[1])
    path = OUT_DIR / f"batch_{idx:03d}.json"
    if not path.is_file():
        print(f"missing {path}", file=sys.stderr)
        return 1
    subprocess.run([sys.executable, str(MERGE), str(path)], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
