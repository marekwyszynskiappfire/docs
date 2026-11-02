#!/usr/bin/env python3
"""Write stdin JSON to a path (for MCP batch capture)."""
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: store_mcp_json.py OUT_PATH < json")
Path(sys.argv[1]).write_text(sys.stdin.read())
