#!/usr/bin/env python3
"""Write one nested-rescan cache entry from getConfluenceContent JSON (file or stdin)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from nested_confluence_rescan import cache_write


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--input", type=Path, default=None, help="JSON file; default stdin")
    args = ap.parse_args()
    raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
    data = json.loads(raw)
    if data.get("error"):
        raise SystemExit(str(data["error"]))
    wrapper_title = data.get("title")
    wrapper_page_id = data.get("contentId") or data.get("pageId")
    page = data.get("data") or {}
    if "version" in page and "body" in page and "id" not in page:
        # getConfluenceContentVersion response
        version = int((page.get("version") or {}).get("number", 0))
        body = page.get("body") or {}
        markdown = body.get("value") or ""
        page_id = str(wrapper_page_id or "")
        title = wrapper_title or f"page {page_id}"
        if not page_id:
            raise SystemExit("version response missing page id; pass contentId in JSON wrapper")
    else:
        page_id = str(page["id"])
        title = page.get("title") or f"page {page_id}"
        version = int((page.get("metadata") or {}).get("version", {}).get("number", 0))
        body = page.get("body") or {}
        markdown = body.get("value") or ""
        if body.get("format") == "html" and markdown:
            markdown = re.sub(r"<[^>]+>", " ", markdown)
            markdown = re.sub(r"\s+", " ", markdown).strip()
    path = cache_write(args.run_dir.resolve(), page_id, title, version, markdown)
    print(path)


if __name__ == "__main__":
    main()
