"""Jira comment POST with mocked HTTP."""

import os

import httpx
import pytest

from jira_client import post_issue_comment


@pytest.fixture()
def jira_env(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "ops@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")


def test_post_issue_comment_success(jira_env):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/rest/api/3/issue/EPIC-1/comment")
        body = request.read()
        assert b'"type":"doc"' in body or b'"type": "doc"' in body
        assert b"heading" in body
        return httpx.Response(201, json={"id": "10001", "self": "https://example/10001"})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        out = post_issue_comment("EPIC-1", "h3. Title\n\n* bullet", http_client=client)
    assert out["id"] == "10001"
