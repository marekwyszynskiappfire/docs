from __future__ import annotations


class _NoStartThread:
    def __init__(self, target, args, daemon):  # noqa: ANN001
        self.target = target
        self.args = args
        self.daemon = daemon

    def start(self) -> None:
        pass


def test_activity_line_names_the_step():
    import cursor_agent_runner

    class Message:
        type = "tool_call"
        name = "getJiraIssue"

    class Event:
        sdk_message = Message()
        interaction_update = None

    assert cursor_agent_runner.activity_line(Event()) == "Reading Jira"

    class Thinking:
        type = "thinking"

    Event.sdk_message = Thinking()
    assert cursor_agent_runner.activity_line(Event()) == "Thinking through the requirement"


def test_status_requires_cursor_api_key(client, monkeypatch):
    monkeypatch.delenv("CURSOR_API_KEY", raising=False)
    response = client.get("/api/cursor-agents/status")
    assert response.status_code == 200
    assert response.json()["installed"] is True
    assert response.json()["configured"] is False


def test_launch_persists_and_cancel_marks_terminal(studio_db, monkeypatch):
    import cursor_agent_runner

    monkeypatch.setenv("CURSOR_API_KEY", "cursor_test")
    monkeypatch.setattr(cursor_agent_runner.threading, "Thread", _NoStartThread)
    created = cursor_agent_runner.launch_agent(
        stage="creator",
        prompt_text="Run trinity-creator",
        pipeline_run_id=None,
        creator_run_id="DEMO-4500",
        epic_key="DEMO-4500",
    )
    assert created["status"] == "queued"
    assert created["prompt_text"] == "Run trinity-creator"

    cancelled = cursor_agent_runner.cancel_agent_run(created["id"])
    assert cancelled["status"] == "cancelled"
    assert "operator" in cancelled["error"].lower()


def test_launch_rejects_duplicate_active_target(studio_db, monkeypatch):
    import cursor_agent_runner

    monkeypatch.setenv("CURSOR_API_KEY", "cursor_test")
    monkeypatch.setattr(cursor_agent_runner.threading, "Thread", _NoStartThread)
    cursor_agent_runner.launch_agent(
        stage="importer",
        prompt_text="Import",
        creator_run_id="DEMO-4500",
    )
    try:
        cursor_agent_runner.launch_agent(
            stage="importer",
            prompt_text="Import again",
            creator_run_id="DEMO-4500",
        )
    except RuntimeError as exc:
        assert "already active" in str(exc)
    else:
        raise AssertionError("a second active Importer agent should be rejected")


def test_cancelled_queued_run_does_not_start_agent(studio_db, monkeypatch):
    import sys
    import types

    import cursor_agent_runner

    monkeypatch.setenv("CURSOR_API_KEY", "cursor_test")
    monkeypatch.setattr(cursor_agent_runner.threading, "Thread", _NoStartThread)
    created = cursor_agent_runner.launch_agent(
        stage="creator",
        prompt_text="Run trinity-creator",
        creator_run_id="DEMO-4500",
        epic_key="DEMO-4500",
    )
    cursor_agent_runner.cancel_agent_run(created["id"])

    started: list[str] = []

    class _Agent:
        @staticmethod
        def create(**kwargs):  # noqa: ANN003
            started.append("create")
            raise RuntimeError("should not start")

    fake = types.ModuleType("cursor_sdk")
    fake.Agent = _Agent
    fake.CursorAgentError = type("CursorAgentError", (Exception,), {})
    fake.LocalAgentOptions = lambda **kwargs: None  # noqa: ARG005
    monkeypatch.setitem(sys.modules, "cursor_sdk", fake)

    cursor_agent_runner._worker(created["id"])
    assert started == []
    assert cursor_agent_runner.get_agent_run(created["id"])["status"] == "cancelled"


def test_launch_rejects_missing_key(studio_db, monkeypatch):
    import cursor_agent_runner

    monkeypatch.delenv("CURSOR_API_KEY", raising=False)
    try:
        cursor_agent_runner.launch_agent(stage="reviewer", prompt_text="Review")
    except RuntimeError as exc:
        assert "CURSOR_API_KEY" in str(exc)
    else:
        raise AssertionError("launch should require CURSOR_API_KEY")
