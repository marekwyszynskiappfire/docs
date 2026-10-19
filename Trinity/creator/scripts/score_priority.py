#!/usr/bin/env python3
"""Score or repair Creator suite payloads (CR-SCORE-01).

  python Trinity/creator/scripts/score_priority.py --payload path/to/suite-payload.json
  python Trinity/creator/scripts/score_priority.py --payload path.json --in-place
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SHARED = Path(__file__).resolve().parents[2] / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from priority_score import (  # noqa: E402
    apply_priority_fields,
    build_execution_plan,
    validate_priority_policy,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or fill Creator priority scores")
    parser.add_argument("--payload", required=True, help="Path to suite-payload.json")
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write filled scores, canonical priority, and execution_plan back to the file",
    )
    args = parser.parse_args()
    path = Path(args.payload)
    batch = json.loads(path.read_text(encoding="utf-8"))
    tests = batch.get("tests") or []
    errors: list[str] = []
    filled: list[dict] = []
    for test in tests:
        next_test = apply_priority_fields(test) if args.in_place else test
        filled.append(next_test)
        errors.extend(validate_priority_policy(next_test))

    if args.in_place:
        batch["tests"] = filled
        batch["execution_plan"] = build_execution_plan(filled)
        path.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for err in errors:
        print(err, file=sys.stderr)
    print(f"{path}: {len(filled)} tests, {len(errors)} priority policy error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
