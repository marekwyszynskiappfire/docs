#!/usr/bin/env python3
"""Cursor hooks: bind Agent sessions to Trinity pipeline stages and record usage."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SESSION_FILE = REPO_ROOT / "Trinity" / "studio" / "data" / ".cursor-session.json"
DEFAULT_STUDIO = "http://127.0.0.1:8765"


def _load_session() -> dict:
    if not SESSION_FILE.is_file():
        return {}
    try:
        return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def session_start(_payload: dict) -> None:
    session = _load_session()
    env: dict[str, str] = {"TRINITY_STUDIO_URL": os.environ.get("TRINITY_STUDIO_URL", DEFAULT_STUDIO)}
    if session.get("pipeline_run_id"):
        env["TRINITY_PIPELINE_RUN_ID"] = str(session["pipeline_run_id"])
    if session.get("creator_run_id"):
        env["TRINITY_CREATOR_RUN_ID"] = str(session["creator_run_id"])
    if session.get("stage"):
        env["TRINITY_CURSOR_STAGE"] = str(session["stage"])
    print(json.dumps({"env": env}))
    sys.exit(0)


def session_end(payload: dict) -> None:
    studio = os.environ.get("TRINITY_STUDIO_URL", DEFAULT_STUDIO).rstrip("/")
    session = _load_session()
    stage = os.environ.get("TRINITY_CURSOR_STAGE") or session.get("stage") or "unscoped"
    body = {
        "stage": stage,
        "conversation_id": payload.get("conversation_id") or payload.get("session_id"),
        "generation_id": payload.get("generation_id"),
        "model": payload.get("model"),
        "model_id": payload.get("model_id"),
        "duration_ms": payload.get("duration_ms"),
        "status": payload.get("status") or payload.get("final_status") or payload.get("reason"),
        "pipeline_run_id": os.environ.get("TRINITY_PIPELINE_RUN_ID") or session.get("pipeline_run_id"),
        "creator_run_id": os.environ.get("TRINITY_CREATOR_RUN_ID") or session.get("creator_run_id"),
        "source": "cursor_hook",
    }
    if not body["conversation_id"]:
        sys.exit(0)
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{studio}/api/cursor-usage",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status >= 400:
                sys.stderr.write(f"Trinity cursor-usage HTTP {resp.status}\n")
    except (urllib.error.URLError, TimeoutError) as exc:
        sys.stderr.write(f"Trinity cursor-usage failed: {exc}\n")
    sys.exit(0)


def main() -> None:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    event = payload.get("hook_event_name") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if event == "sessionStart":
        session_start(payload)
    elif event in ("sessionEnd", "stop"):
        session_end(payload)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
