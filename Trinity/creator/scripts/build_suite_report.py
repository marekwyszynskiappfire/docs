#!/usr/bin/env python3
"""CLI: TestCaseDraft batch → Profile B suite-report folder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CREATOR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CREATOR_ROOT))

from suite_report.build import build_report_payload, write_suite_report  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="Build Creator Profile B suite report")
    ap.add_argument("--batch", required=True, help="Path to suite JSON (TestCaseDraft batch)")
    ap.add_argument("--out", required=True, help="Output folder (e.g. …/suite-report)")
    ap.add_argument("--run-id", default="", help="Override run id in report title")
    args = ap.parse_args()

    batch_path = Path(args.batch).resolve()
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    run_id = args.run_id or batch.get("run_id") or batch_path.stem
    payload = build_report_payload(run_id=run_id, batch=batch)
    index = write_suite_report(Path(args.out).resolve(), payload)
    print(json.dumps({"index_html": str(index), "test_count": len(payload["rows"])}, indent=2))


if __name__ == "__main__":
    main()
