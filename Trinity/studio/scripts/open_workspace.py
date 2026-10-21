#!/usr/bin/env python3
"""Import a pipeline manifest into Studio and print the workspace URL.

Starts Studio only when the port is free. A compatible Studio is reused.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from studio_launcher import StudioLaunchError, bootstrap_workspace  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Path to pipeline-manifest.json")
    args = parser.parse_args()
    try:
        result = bootstrap_workspace(Path(args.manifest))
    except StudioLaunchError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
