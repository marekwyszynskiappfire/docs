"""Pipeline manifest build and idempotent import."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def _payload(key: str, summary: str = "Demo") -> dict:
    return {
        "scope": {"type": "epic", "value": key},
        "requirements": [{"summary": summary, "jira_key": key}],
    }


def _write_epic(run_dir: Path, key: str, summary: str = "Demo") -> None:
    epic = run_dir / key
    epic.mkdir(parents=True, exist_ok=True)
    (epic / "review-payload.json").write_text(
        json.dumps(_payload(key, summary)),
        encoding="utf-8",
    )


def _use_repo(monkeypatch, root: Path) -> None:
    import studio_paths

    monkeypatch.setattr(studio_paths, "DOCS_REPO_ROOT", root)


def _revision_count() -> int:
    from db import connect

    with connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM review_payload_revision").fetchone()[0]


def test_import_unchanged_manifest_does_not_add_revision(studio_db, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    run_dir = tmp_path / "runs" / "demo-portfolio"
    _write_epic(run_dir, "DEMO-4500")
    _write_epic(run_dir, "DEMO-4501", "Second")

    from pipeline_manifest import build_manifest, import_pipeline_manifest, write_manifest

    manifest = build_manifest(
        run_dir,
        "demo-portfolio",
        label="Demo portfolio",
        product_id="demo",
        persona_id="reviewer-expert-qa-automation.md",
        scope_kind="epic_keys",
        scope_value="DEMO-4500, DEMO-4501",
    )
    path = write_manifest(run_dir, manifest)

    first = import_pipeline_manifest(path)
    assert first["import_kind"] == "new"
    assert first["revisions_added"] == 2
    assert first["workspace_path"] == f"/workspace/{first['pipeline_run_id']}"
    assert json.loads(path.read_text(encoding="utf-8"))["pipeline_run_id"] == first["pipeline_run_id"]
    assert _revision_count() == 2

    second = import_pipeline_manifest(path)
    assert second["unchanged"] is True
    assert second["import_kind"] == "unchanged"
    assert second["pipeline_run_id"] == first["pipeline_run_id"]
    assert second["revisions_added"] == 0
    assert _revision_count() == 2


def test_changed_epic_adds_one_revision(studio_db, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    run_dir = tmp_path / "runs" / "demo-portfolio"
    _write_epic(run_dir, "DEMO-4500")
    _write_epic(run_dir, "DEMO-4501")

    from pipeline_manifest import build_manifest, import_pipeline_manifest, write_manifest

    def publish() -> Path:
        manifest = build_manifest(
            run_dir,
            "demo-portfolio",
            product_id="demo",
            persona_id="reviewer-expert-qa-automation.md",
            scope_kind="epic_keys",
            scope_value="DEMO-4500, DEMO-4501",
        )
        return write_manifest(run_dir, manifest)

    first_path = publish()
    first = import_pipeline_manifest(first_path)
    _write_epic(run_dir, "DEMO-4501", "Changed")
    second = import_pipeline_manifest(publish())

    assert second["pipeline_run_id"] == first["pipeline_run_id"]
    assert second["revisions_added"] == 1
    assert second["revisions_skipped"] == 1
    assert _revision_count() == 3

    from db import connect

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT u.jira_key, COUNT(r.id) AS revisions
            FROM review_unit u
            JOIN review_payload_revision r ON r.review_unit_id = u.id
            GROUP BY u.jira_key
            ORDER BY u.jira_key
            """
        ).fetchall()
    assert [(row["jira_key"], row["revisions"]) for row in rows] == [
        ("DEMO-4500", 1),
        ("DEMO-4501", 2),
    ]


def test_manifest_rejects_hash_mismatch_and_path_escape(studio_db, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    run_dir = tmp_path / "runs" / "demo-portfolio"
    _write_epic(run_dir, "DEMO-4500")

    from pipeline_manifest import build_manifest, import_pipeline_manifest, write_manifest

    manifest = build_manifest(
        run_dir,
        "demo-portfolio",
        product_id="demo",
        persona_id="reviewer-expert-qa-automation.md",
        scope_kind="epic_keys",
        scope_value="DEMO-4500",
    )
    manifest["epics"][0]["content_sha256"] = "a" * 64
    path = write_manifest(run_dir, manifest)
    with pytest.raises(ValueError, match="content_sha256"):
        import_pipeline_manifest(path)

    manifest["epics"][0]["review_payload_path"] = "../secrets/review-payload.json"
    with pytest.raises(ValueError, match="Schema validation failed"):
        write_manifest(run_dir, manifest)


def test_import_manifest_api(client, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    run_dir = tmp_path / "runs" / "demo-portfolio"
    _write_epic(run_dir, "DEMO-4500")

    from pipeline_manifest import build_manifest, write_manifest

    path = write_manifest(
        run_dir,
        build_manifest(
            run_dir,
            "demo-portfolio",
            product_id="demo",
            persona_id="reviewer-expert-qa-automation.md",
            scope_kind="epic_keys",
            scope_value="DEMO-4500",
        ),
    )
    relative = path.relative_to(tmp_path).as_posix()
    response = client.post("/api/import/pipeline-manifest", json={"path": relative})
    assert response.status_code == 200
    body = response.json()
    assert body["import_kind"] == "new"
    assert body["revisions_added"] == 1

    again = client.post(
        "/api/import/pipeline-manifest",
        json={"path": relative, "dry_run": True},
    )
    assert again.status_code == 200
    assert again.json()["unchanged"] is True
    assert _revision_count() == 1
