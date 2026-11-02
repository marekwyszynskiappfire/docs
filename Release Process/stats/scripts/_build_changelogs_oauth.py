#!/usr/bin/env python3
"""Build changelogs.json using Atlassian OAuth (same session as MCP)."""

from __future__ import annotations

import importlib.util
import json
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "Release Process" / "stats" / "data"
OUT = DATA / "changelogs.json"
FC_PATH = ROOT / "Release Process" / "stats" / "scripts" / "fetch_changelog_cache.py"
SITE = "https://appfire.atlassian.net"
AUTH_DIR = Path.home() / ".mcp-auth" / "mcp-remote-v1"


def ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    strict = getattr(ssl, "VERIFY_X509_STRICT", 0)
    if strict:
        ctx.verify_flags &= ~strict
    if sys.platform == "darwin":
        keychain = Path("/Library/Keychains/System.keychain")
        if keychain.is_file():
            proc = subprocess.run(
                ["security", "find-certificate", "-a", "-c", "goskope", "-p", str(keychain)],
                capture_output=True,
                text=True,
                check=False,
            )
            if "BEGIN CERTIFICATE" in proc.stdout:
                ctx.load_verify_locations(cadata=proc.stdout)
    return ctx


CTX = ssl_context()


def bearer_token() -> str:
    tokens = sorted(AUTH_DIR.glob("*_tokens.json"))
    if not tokens:
        raise SystemExit(f"No MCP OAuth tokens under {AUTH_DIR}")
    for path in tokens:
        data = json.loads(path.read_text())
        token = data.get("access_token")
        if token:
            return token
    raise SystemExit("No access_token in MCP OAuth token files")


def jira_changelog(key: str, token: str) -> list[dict]:
    values: list[dict] = []
    start = 0
    while True:
        url = (
            f"{SITE}/rest/api/3/issue/{urllib.parse.quote(key)}/changelog?"
            + urllib.parse.urlencode({"startAt": start, "maxResults": 100})
        )
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=60, context=CTX) as resp:
            page = json.loads(resp.read().decode())
        values.extend(page.get("values") or [])
        if page.get("isLast", True):
            return values
        start += page.get("maxResults") or 100
        if start >= (page.get("total") or 0):
            return values


def defect_keys() -> list[str]:
    keys: set[str] = set()
    for v in ("8.74", "8.75", "8.76"):
        report = json.loads((DATA / f"{v}.json").read_text())
        keys.update((report.get("test_run") or {}).get("defect_keys") or [])
    return sorted(keys)


def main() -> int:
    spec = importlib.util.spec_from_file_location("fc", FC_PATH)
    fc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fc)

    token = bearer_token()
    cache: dict[str, list] = {}
    for key in defect_keys():
        try:
            values = jira_changelog(key, token)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:300]
            raise SystemExit(f"{key}: HTTP {exc.code} {detail}") from exc
        slim = [fc.slim_entry(v) for v in values]
        cache[key] = sorted(slim, key=lambda e: e.get("created") or "")
        print(f"{key}: {len(cache[key])}")

    OUT.write_text(json.dumps(cache, indent=2) + "\n")
    print(f"wrote {OUT} ({len(cache)} issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
