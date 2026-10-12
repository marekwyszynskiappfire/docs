"""Pytest fixtures for Trinity Studio API tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

STUDIO_ROOT = Path(__file__).resolve().parents[1]
SERVER = STUDIO_ROOT / "server"
TRINITY_ROOT = STUDIO_ROOT.parent
SHARED = TRINITY_ROOT / "shared"

for path in (str(SERVER), str(SHARED)):
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.fixture()
def studio_db(tmp_path, monkeypatch):
    db_file = tmp_path / "qa-studio-test.db"
    monkeypatch.setenv("QA_STUDIO_DB", str(db_file))
    from db import init_db

    init_db()
    return db_file


@pytest.fixture()
def client(studio_db):
    from fastapi.testclient import TestClient
    from app import app

    with TestClient(app) as test_client:
        yield test_client
