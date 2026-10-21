"""Studio launcher reuses a compatible API and never stops another process."""

from __future__ import annotations

import json
import urllib.error
from pathlib import Path

import pytest

import studio_launcher
from studio_launcher import StudioLaunchError, bootstrap_workspace, ensure_studio, read_health


HEALTHY = {
    "status": "ok",
    "features": ["importer_plan", "pipeline_manifest", "cursor_handoff"],
}


def test_reuses_compatible_studio_without_starting(monkeypatch):
    monkeypatch.setattr(studio_launcher, "read_health", lambda port, timeout=2.0: HEALTHY)
    started: list[int] = []
    result = ensure_studio(8765, starter=lambda port: started.append(port))
    assert result["action"] == "reused"
    assert result["base_url"] == "http://127.0.0.1:8765"
    assert started == []


def test_incompatible_studio_is_left_running(monkeypatch):
    monkeypatch.setattr(
        studio_launcher,
        "read_health",
        lambda port, timeout=2.0: {"status": "ok", "features": ["importer_plan"]},
    )

    def starter(_port):
        raise AssertionError("starter must not run")

    with pytest.raises(StudioLaunchError, match="will not stop"):
        ensure_studio(8765, starter=starter)


def test_non_studio_listener_is_left_running(monkeypatch):
    def explode(_port, timeout=2.0):
        raise StudioLaunchError(
            "Port 8765 did not return Studio health. This launcher will not stop that process."
        )

    monkeypatch.setattr(studio_launcher, "read_health", explode)

    def starter(_port):
        raise AssertionError("starter must not run")

    with pytest.raises(StudioLaunchError, match="will not stop"):
        ensure_studio(8765, starter=starter)


def test_connection_refused_means_port_is_free(monkeypatch):
    def urlopen(*_args, **_kwargs):
        raise urllib.error.URLError(ConnectionRefusedError(61, "Connection refused"))

    monkeypatch.setattr(studio_launcher.urllib.request, "urlopen", urlopen)
    assert read_health(8765) is None


def test_starts_when_port_is_free(monkeypatch, tmp_path):
    calls = {"n": 0}

    def health(_port, timeout=2.0):
        calls["n"] += 1
        if calls["n"] == 1:
            return None
        return HEALTHY

    class Process:
        pid = 4321

        def poll(self):
            return None

    monkeypatch.setattr(studio_launcher, "read_health", health)
    monkeypatch.setattr(studio_launcher, "STUDIO_DATA", tmp_path)
    result = ensure_studio(8765, starter=lambda _port: Process(), poll_seconds=2)
    assert result["action"] == "started"
    assert result["pid"] == 4321
    assert (tmp_path / "studio-api.pid").read_text(encoding="utf-8") == "4321"


def test_start_command_does_not_kill(monkeypatch, tmp_path):
    python = tmp_path / "python"
    python.write_text("", encoding="utf-8")
    captured: dict[str, list[str]] = {}

    class Process:
        pid = 1

    def popen(cmd, **_kwargs):
        captured["cmd"] = cmd
        return Process()

    monkeypatch.setattr(studio_launcher, "python_bin", lambda: python)
    monkeypatch.setattr(studio_launcher.subprocess, "Popen", popen)
    studio_launcher.start_background(8765, log_path=tmp_path / "studio-api.log")
    command = " ".join(captured["cmd"])
    assert "kill" not in command
    assert "--port" in captured["cmd"]
    assert "8765" in captured["cmd"]


def test_bootstrap_returns_one_workspace_url(monkeypatch, tmp_path):
    seen: dict[str, object] = {}

    monkeypatch.setattr(
        studio_launcher,
        "ensure_studio",
        lambda port=None: {
            "action": "reused",
            "base_url": "http://127.0.0.1:8765",
            "port": 8765,
            "ui_ready": True,
        },
    )

    def post_json(url, payload, timeout=60.0):
        seen["url"] = url
        seen["payload"] = payload
        return {
            "pipeline_run_id": "pr-1",
            "import_kind": "unchanged",
            "revisions_added": 0,
            "workspace_path": "/workspace/pr-1",
        }

    monkeypatch.setattr(studio_launcher, "post_json", post_json)
    monkeypatch.setattr(studio_launcher, "manifest_api_path", lambda path: "runs/demo/pipeline-manifest.json")
    result = bootstrap_workspace(tmp_path / "pipeline-manifest.json")
    assert result["workspace_url"] == "http://127.0.0.1:8765/workspace/pr-1"
    assert result["action"] == "reused"
    assert seen["url"] == "http://127.0.0.1:8765/api/import/pipeline-manifest"
    assert json.loads(json.dumps(result))["import_kind"] == "unchanged"
