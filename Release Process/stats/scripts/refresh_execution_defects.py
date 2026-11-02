#!/usr/bin/env python3
"""Refresh defect_keys on mcp_import/_fetch/{version}/execution_meta.json from a MCP dump.

Each dump file is getJiraIssue JSON (fields.issuelinks). Merge into meta, compose, materialize one version.

  python3 refresh_execution_defects.py 8.65 /path/to/TC-5841.json
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "Release Process" / "stats" / "trains_since_2025-10-01.json"
FETCH = ROOT / "Release Process" / "stats" / "mcp_import" / "_fetch"
COMPOSE = ROOT / "Release Process" / "stats" / "scripts" / "compose_mcp_import.py"
MATERIALIZE = ROOT / "Release Process" / "stats" / "scripts" / "materialize_trains.py"
COMPOSE_MOD = ROOT / "Release Process" / "stats" / "scripts" / "compose_mcp_import.py"


def load_compose():
    spec = importlib.util.spec_from_file_location("compose", COMPOSE_MOD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def defect_keys_from_issue(issue: dict) -> list[str]:
    fields = issue.get("fields") or issue
    links = fields.get("issuelinks") if isinstance(fields, dict) else None
    compose = load_compose()
    return compose.defect_keys(links)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: refresh_execution_defects.py VERSION ISSUE_JSON", file=sys.stderr)
        return 2
    version = sys.argv[1]
    payload = json.loads(Path(sys.argv[2]).read_text())
    issue = payload.get("data") or payload
    keys = defect_keys_from_issue(issue)
    meta_path = FETCH / version / "execution_meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
    meta["defect_keys"] = keys
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    subprocess.run([sys.executable, str(COMPOSE), version], check=True)
    subprocess.run([sys.executable, str(MATERIALIZE)], check=False)
    print(f"{version}: {len(keys)} defect links -> {meta_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
