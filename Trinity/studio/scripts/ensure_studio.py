#!/usr/bin/env python3
"""Reuse a compatible Studio, or start one. Never stops another process on the port."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from studio_launcher import StudioLaunchError, ensure_studio  # noqa: E402


def main() -> int:
    try:
        result = ensure_studio()
    except StudioLaunchError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    public = {key: value for key, value in result.items() if key != "health"}
    json.dump(public, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
