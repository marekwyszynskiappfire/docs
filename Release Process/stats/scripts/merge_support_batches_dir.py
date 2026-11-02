#!/usr/bin/env python3
"""Merge ordered batch JSON files from a directory into support_links_cache.json."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MERGE = ROOT / "Release Process/stats/scripts/merge_support_link_batch.py"


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} BATCH_DIR")
    batch_dir = Path(sys.argv[1])
    files = sorted(batch_dir.glob("batch_*.json"))
    if not files:
        print("no batch_*.json files", file=sys.stderr)
        return 1
    for path in files:
        subprocess.run([sys.executable, str(MERGE), str(path)], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
