#!/usr/bin/env python3
"""Write pipeline-manifest.json for a Reviewer run folder.

The manifest references each Epic review-payload.json. It does not copy payloads.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from pipeline_manifest import build_manifest, write_manifest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, help="Reviewer run folder")
    parser.add_argument("--portfolio-id", required=True)
    parser.add_argument("--label")
    parser.add_argument("--product-id")
    parser.add_argument("--persona-id")
    parser.add_argument(
        "--target-environment",
        choices=("sandbox", "production"),
        default="sandbox",
    )
    parser.add_argument(
        "--scope-kind",
        choices=("filter_url", "jql", "epic_keys", "epic_url"),
    )
    parser.add_argument("--scope-value")
    parser.add_argument("--pipeline-run-id")
    args = parser.parse_args()
    run_dir = Path(args.run_dir).expanduser().resolve()
    manifest = build_manifest(
        run_dir,
        args.portfolio_id,
        label=args.label,
        product_id=args.product_id,
        persona_id=args.persona_id,
        target_environment=args.target_environment,
        scope_kind=args.scope_kind,
        scope_value=args.scope_value,
        pipeline_run_id=args.pipeline_run_id,
    )
    destination = write_manifest(run_dir, manifest)
    json.dump(
        {"path": str(destination), "epics": len(manifest["epics"])},
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
