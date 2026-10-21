"""Start or reuse the local Studio API.

A compatible health response is reused. Anything else already bound to the port
is left running; this module never stops another process.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from studio_paths import SERVER_DIR, STUDIO_DATA, STUDIO_ROOT, WEB_DIST

REQUIRED_FEATURES = ("importer_plan", "pipeline_manifest", "cursor_handoff")
Starter = Callable[[int], subprocess.Popen[Any]]


class StudioLaunchError(RuntimeError):
    pass


def studio_port() -> int:
    return int(os.environ.get("QA_STUDIO_PORT", "8765"))


def base_url(port: int) -> str:
    return f"http://127.0.0.1:{port}"


def python_bin() -> Path:
    return STUDIO_ROOT / ".venv" / "bin" / "python"


def ui_ready() -> bool:
    return (WEB_DIST / "index.html").is_file()


def _connection_refused(exc: urllib.error.URLError) -> bool:
    reason = exc.reason
    if isinstance(reason, ConnectionRefusedError):
        return True
    if isinstance(reason, OSError) and getattr(reason, "errno", None) in {61, 111}:
        return True
    return "connection refused" in str(reason).lower()


def read_health(port: int, timeout: float = 2.0) -> dict[str, Any] | None:
    """Return health JSON, or None when nothing is listening.

    Any other response raises StudioLaunchError and leaves that process alone.
    """
    request = urllib.request.Request(f"{base_url(port)}/api/health")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise StudioLaunchError(
            f"Port {port} did not return Studio health. This launcher will not stop that process."
        ) from exc
    except urllib.error.URLError as exc:
        if _connection_refused(exc):
            return None
        raise StudioLaunchError(
            f"Port {port} did not return Studio health. This launcher will not stop that process."
        ) from exc
    except (TimeoutError, socket.timeout, json.JSONDecodeError) as exc:
        raise StudioLaunchError(
            f"Port {port} did not return Studio health. This launcher will not stop that process."
        ) from exc
    if not isinstance(payload, dict):
        raise StudioLaunchError(
            f"Port {port} did not return Studio health. This launcher will not stop that process."
        )
    return payload


def compatible(health: dict[str, Any]) -> bool:
    features = health.get("features") or []
    return health.get("status") == "ok" and all(feature in features for feature in REQUIRED_FEATURES)


def start_background(port: int, log_path: Path | None = None) -> subprocess.Popen[Any]:
    python = python_bin()
    if not python.is_file():
        raise StudioLaunchError(
            "Studio virtualenv is missing. Run ./Trinity/studio/scripts/start.sh once, then retry."
        )
    destination = log_path or (STUDIO_DATA / "studio-api.log")
    destination.parent.mkdir(parents=True, exist_ok=True)
    log_handle = destination.open("a", encoding="utf-8")
    try:
        return subprocess.Popen(
            [
                str(python),
                "-m",
                "uvicorn",
                "app:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=str(SERVER_DIR),
            env={**os.environ, "PYTHONPATH": str(SERVER_DIR)},
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    finally:
        log_handle.close()


def ensure_studio(
    port: int | None = None,
    *,
    starter: Starter | None = None,
    poll_seconds: float = 20.0,
) -> dict[str, Any]:
    selected = studio_port() if port is None else port
    health = read_health(selected)
    url = base_url(selected)
    if health is not None:
        if compatible(health):
            return {
                "action": "reused",
                "base_url": url,
                "port": selected,
                "ui_ready": ui_ready(),
                "health": health,
            }
        missing = [feature for feature in REQUIRED_FEATURES if feature not in (health.get("features") or [])]
        raise StudioLaunchError(
            f"Studio on port {selected} is missing features: {', '.join(missing)}. "
            "Restart it with STUDIO_FORCE=1 ./Trinity/studio/scripts/start.sh. "
            "This launcher will not stop that process."
        )

    process = (starter or start_background)(selected)
    deadline = time.time() + poll_seconds
    while time.time() < deadline:
        if process.poll() is not None:
            raise StudioLaunchError(
                f"Studio exited during startup (code {process.returncode}). "
                f"See {STUDIO_DATA / 'studio-api.log'}."
            )
        try:
            health = read_health(selected, timeout=1)
        except StudioLaunchError:
            health = None
        if health is not None and compatible(health):
            pid_path = STUDIO_DATA / "studio-api.pid"
            pid_path.parent.mkdir(parents=True, exist_ok=True)
            pid_path.write_text(str(process.pid), encoding="utf-8")
            return {
                "action": "started",
                "base_url": url,
                "port": selected,
                "pid": process.pid,
                "ui_ready": ui_ready(),
                "health": health,
            }
        if health is not None:
            raise StudioLaunchError(
                f"Studio on port {selected} is not compatible. This launcher will not stop that process."
            )
        time.sleep(0.2)
    raise StudioLaunchError(
        f"Studio did not become healthy on port {selected}. This launcher will not stop that process."
    )


def manifest_api_path(path: Path) -> str:
    from pipeline_manifest import repo_root

    resolved = path.expanduser().resolve()
    try:
        return resolved.relative_to(repo_root().resolve()).as_posix()
    except ValueError:
        return str(resolved)


def post_json(url: str, payload: dict[str, Any], timeout: float = 60.0) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise StudioLaunchError(f"Studio import failed ({exc.code}): {detail}") from exc
    if not isinstance(body, dict):
        raise StudioLaunchError("Studio import did not return a JSON object.")
    return body


def bootstrap_workspace(manifest: Path, port: int | None = None) -> dict[str, Any]:
    launched = ensure_studio(port)
    imported = post_json(
        f"{launched['base_url']}/api/import/pipeline-manifest",
        {"path": manifest_api_path(manifest)},
    )
    workspace_path = imported.get("workspace_path") or f"/workspace/{imported['pipeline_run_id']}"
    return {
        "action": launched["action"],
        "base_url": launched["base_url"],
        "port": launched["port"],
        "pid": launched.get("pid"),
        "ui_ready": launched["ui_ready"],
        "pipeline_run_id": imported["pipeline_run_id"],
        "import_kind": imported.get("import_kind"),
        "revisions_added": imported.get("revisions_added", imported.get("units_imported")),
        "workspace_url": f"{launched['base_url']}{workspace_path}",
    }
