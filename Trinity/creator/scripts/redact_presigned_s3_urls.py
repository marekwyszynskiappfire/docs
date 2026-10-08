#!/usr/bin/env python3
"""Strip query strings from S3 URLs (presigned URLs may contain STS tokens)."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

# Match S3-style URLs through the path; drop ?query (credentials live in query).
S3_URL = re.compile(
    r"https://[a-zA-Z0-9.-]+\.s3\.amazonaws\.com/[^\s\"'<>)\]]+",
    re.IGNORECASE,
)


def redact_text(text: str) -> tuple[str, int]:
    count = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal count
        url = m.group(0)
        if "?" in url:
            count += 1
            return url.split("?", 1)[0]
        return url

    return S3_URL.sub(repl, text), count


def redact_object(obj: Any) -> tuple[Any, int]:
    """Recursively strip presigned query strings from strings inside JSON-like trees."""
    if isinstance(obj, str):
        return redact_text(obj)
    if isinstance(obj, list):
        total = 0
        out: list[Any] = []
        for item in obj:
            redacted, n = redact_object(item)
            total += n
            out.append(redacted)
        return out, total
    if isinstance(obj, dict):
        total = 0
        out: dict[Any, Any] = {}
        for key, value in obj.items():
            redacted, n = redact_object(value)
            total += n
            out[key] = redacted
        return out, total
    return obj, 0


def process_file(path: Path) -> int:
    raw = path.read_text(encoding="utf-8", errors="replace")
    new, n = redact_text(raw)
    if n:
        path.write_text(new, encoding="utf-8")
    return n


def main(argv: list[str]) -> int:
    roots = [Path(p) for p in argv[1:]] or [Path("Trinity/creator/golden")]
    total = 0
    for root in roots:
        if not root.exists():
            print(f"skip missing {root}", file=sys.stderr)
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix in {".png", ".jpg", ".zip"}:
                continue
            total += process_file(path)
    print(f"redacted query strings on {total} URL occurrence(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
