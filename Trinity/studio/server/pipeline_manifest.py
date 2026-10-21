"""Build and import a portfolio pipeline manifest.

The manifest points at per-Epic review-payload.json files. It does not copy them.
Re-importing the same payload hashes reuses the pipeline run and does not append
a review revision.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from db import db, init_db, utc_now
from import_review import EPIC_DIR_RE, import_reviewer_run

SCHEMA_VERSION = "1.0"
MANIFEST_NAME = "pipeline-manifest.json"


def repo_root() -> Path:
    from studio_paths import DOCS_REPO_ROOT

    return DOCS_REPO_ROOT


def schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / "pipeline-manifest.schema.json"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_set_hash(epics: list[dict[str, Any]]) -> str:
    lines = [
        f"{epic['jira_key']}:{epic['content_sha256']}"
        for epic in sorted(epics, key=lambda item: item["jira_key"])
    ]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def _load_schema() -> dict[str, Any]:
    with schema_path().open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_manifest(data: dict[str, Any]) -> None:
    try:
        import jsonschema
        from jsonschema import ValidationError
    except ImportError as exc:
        raise RuntimeError("jsonschema package required; pip install jsonschema") from exc
    try:
        jsonschema.Draft202012Validator(
            _load_schema(),
            format_checker=jsonschema.FormatChecker(),
        ).validate(data)
    except ValidationError as exc:
        raise ValueError(f"Schema validation failed: {exc.message}") from exc
    keys = [epic["jira_key"] for epic in data["epics"]]
    if len(keys) != len(set(keys)):
        raise ValueError("Manifest epics must have unique jira_key values")


def resolve_repo_path(relative: str) -> Path:
    if not relative or relative.startswith(("/", "\\")):
        raise ValueError(f"Path must be repository-relative: {relative}")
    if ".." in Path(relative).parts:
        raise ValueError(f"Path must not contain '..': {relative}")
    root = repo_root().resolve()
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path escapes the repository: {relative}") from exc
    return resolved


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(repo_root().resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"Path is outside the repository: {path}") from exc


def _run_config(portfolio_id: str) -> dict[str, Any]:
    path = (
        repo_root()
        / "Trinity"
        / "reviewer"
        / "config"
        / "runs"
        / f"{portfolio_id}.json"
    )
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def discover_epics(run_dir: Path) -> list[dict[str, Any]]:
    if not run_dir.is_dir():
        raise FileNotFoundError(run_dir)
    epics: list[dict[str, Any]] = []
    for epic_dir in sorted(path for path in run_dir.iterdir() if path.is_dir()):
        if not EPIC_DIR_RE.match(epic_dir.name):
            continue
        payload_path = epic_dir / "review-payload.json"
        if not payload_path.is_file():
            continue
        epics.append(
            {
                "jira_key": epic_dir.name,
                "review_payload_path": repo_relative(payload_path),
                "content_sha256": file_sha256(payload_path),
            }
        )
    if not epics:
        raise ValueError(f"No epic review payloads under {run_dir}")
    return epics


def build_manifest(
    run_dir: Path,
    portfolio_id: str,
    *,
    label: str | None = None,
    product_id: str | None = None,
    persona_id: str | None = None,
    target_environment: str = "sandbox",
    scope_kind: str | None = None,
    scope_value: str | None = None,
    pipeline_run_id: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    config = _run_config(portfolio_id)
    scope = config.get("scope") if isinstance(config.get("scope"), dict) else {}
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "portfolio_id": portfolio_id,
        "label": label or config.get("label") or portfolio_id,
        "product_id": product_id or config.get("product_id"),
        "persona_id": persona_id or config.get("persona_id"),
        "target_environment": target_environment,
        "scope": {
            "kind": scope_kind or scope.get("kind"),
            "value": scope_value or scope.get("value"),
        },
        "output_root": repo_relative(run_dir),
        "generated_at": generated_at
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "epics": discover_epics(run_dir),
    }
    if pipeline_run_id:
        manifest["pipeline_run_id"] = pipeline_run_id
    missing = [
        name
        for name in ("product_id", "persona_id")
        if not manifest.get(name)
    ]
    if not manifest["scope"].get("kind") or not manifest["scope"].get("value"):
        missing.append("scope")
    if missing:
        raise ValueError(
            "Manifest is missing "
            + ", ".join(missing)
            + f". Pass them explicitly or add reviewer/config/runs/{portfolio_id}.json."
        )
    validate_manifest(manifest)
    return manifest


def write_manifest(run_dir: Path, manifest: dict[str, Any]) -> Path:
    validate_manifest(manifest)
    destination = run_dir.resolve() / MANIFEST_NAME
    destination.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination


def _load_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Manifest is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError("Manifest must be a JSON object")
    validate_manifest(data)
    return data


def _verify_files(manifest: dict[str, Any]) -> tuple[Path, dict[str, str]]:
    output_root = resolve_repo_path(manifest["output_root"])
    if not output_root.is_dir():
        raise FileNotFoundError(output_root)
    current: dict[str, str] = {}
    for epic in manifest["epics"]:
        payload_path = resolve_repo_path(epic["review_payload_path"])
        try:
            payload_path.relative_to(output_root)
        except ValueError as exc:
            raise ValueError(
                f"{epic['jira_key']} payload is outside output_root"
            ) from exc
        if payload_path.parent.name != epic["jira_key"]:
            raise ValueError(
                f"{epic['jira_key']} payload folder is {payload_path.parent.name}"
            )
        if not payload_path.is_file():
            raise FileNotFoundError(payload_path)
        digest = file_sha256(payload_path)
        if digest != epic["content_sha256"]:
            raise ValueError(
                f"{epic['jira_key']} content_sha256 does not match {epic['review_payload_path']}"
            )
        current[epic["jira_key"]] = digest
    on_disk = {
        path.name
        for path in output_root.iterdir()
        if path.is_dir()
        and EPIC_DIR_RE.match(path.name)
        and (path / "review-payload.json").is_file()
    }
    declared = set(current)
    if on_disk != declared:
        extra = sorted(on_disk - declared)
        missing = sorted(declared - on_disk)
        raise ValueError(
            "Manifest epics do not match the run folder"
            + (f"; extra: {', '.join(extra)}" if extra else "")
            + (f"; missing: {', '.join(missing)}" if missing else "")
        )
    return output_root, current


def _result(
    pipeline_run_id: str,
    *,
    source_path: str,
    revisions_added: int,
    revisions_skipped: int,
    unchanged: bool,
    pipeline_is_new: bool,
    manifest_path: str,
) -> dict[str, Any]:
    if unchanged:
        import_kind = "unchanged"
    elif pipeline_is_new:
        import_kind = "new"
    else:
        import_kind = "updated"
    return {
        "pipeline_run_id": pipeline_run_id,
        "units_imported": revisions_added,
        "revisions_added": revisions_added,
        "revisions_skipped": revisions_skipped,
        "unchanged": unchanged,
        "pipeline_is_new": pipeline_is_new,
        "import_kind": import_kind,
        "source_path": source_path,
        "manifest_path": manifest_path,
        "workspace_path": f"/workspace/{pipeline_run_id}",
    }


def _record_review_handoff(
    pipeline_id: str, manifest: dict[str, Any], manifest_path: str
) -> None:
    from cursor_handoff import ensure_review_handoff

    with db() as conn:
        ensure_review_handoff(conn, pipeline_id, manifest, manifest_path)


def import_pipeline_manifest(path: str | Path, dry_run: bool = False) -> dict[str, Any]:
    init_db()
    manifest_path = Path(path).expanduser()
    if not manifest_path.is_absolute():
        manifest_path = repo_root() / manifest_path
    manifest_path = manifest_path.resolve()
    manifest = _load_manifest(manifest_path)
    output_root, current_hashes = _verify_files(manifest)
    source_path = str(output_root)
    set_hash = payload_set_hash(manifest["epics"])
    manifest_rel = repo_relative(manifest_path)

    with db() as conn:
        existing = conn.execute(
            "SELECT id FROM pipeline_run WHERE source_path = ?",
            (source_path,),
        ).fetchone()
        stored = None
        if existing:
            stored = conn.execute(
                "SELECT manifest_json, payload_set_hash FROM pipeline_manifest WHERE pipeline_run_id = ?",
                (existing["id"],),
            ).fetchone()
        declared_id = manifest.get("pipeline_run_id")
        if declared_id and existing and existing["id"] != declared_id:
            raise ValueError(
                f"Manifest pipeline_run_id {declared_id} does not match the run already imported from {source_path}"
            )

    previous: dict[str, str] = {}
    if stored and stored["manifest_json"]:
        previous_manifest = json.loads(stored["manifest_json"])
        previous = {
            epic["jira_key"]: epic["content_sha256"]
            for epic in previous_manifest.get("epics") or []
            if isinstance(epic, dict) and epic.get("jira_key") and epic.get("content_sha256")
        }
    unchanged = bool(stored) and stored["payload_set_hash"] == set_hash
    if dry_run:
        pipeline_id = (existing["id"] if existing else None) or declared_id
        return _result(
            pipeline_id or "",
            source_path=source_path,
            revisions_added=0 if unchanged else len(current_hashes) - sum(
                1 for key, digest in current_hashes.items() if previous.get(key) == digest
            ),
            revisions_skipped=len(current_hashes) if unchanged else sum(
                1 for key, digest in current_hashes.items() if previous.get(key) == digest
            ),
            unchanged=unchanged,
            pipeline_is_new=existing is None,
            manifest_path=manifest_rel,
        )
    if unchanged and existing:
        _record_review_handoff(existing["id"], manifest, manifest_rel)
        return _result(
            existing["id"],
            source_path=source_path,
            revisions_added=0,
            revisions_skipped=len(current_hashes),
            unchanged=True,
            pipeline_is_new=False,
            manifest_path=manifest_rel,
        )

    unchanged_hashes = {
        key: digest
        for key, digest in current_hashes.items()
        if previous.get(key) == digest
    }
    imported = import_reviewer_run(
        output_root,
        run_id=declared_id or (existing["id"] if existing else None),
        unchanged_hashes=unchanged_hashes or None,
    )
    pipeline_id = imported["pipeline_run_id"]
    if not manifest.get("pipeline_run_id"):
        manifest["pipeline_run_id"] = pipeline_id
        validate_manifest(manifest)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    with db() as conn:
        if imported["pipeline_is_new"]:
            conn.execute(
                "UPDATE pipeline_run SET label = ? WHERE id = ?",
                (manifest["label"], pipeline_id),
            )
        conn.execute(
            """
            UPDATE pipeline_run
            SET product_id = COALESCE(product_id, ?)
            WHERE id = ?
            """,
            (manifest["product_id"], pipeline_id),
        )
        conn.execute(
            """
            INSERT INTO pipeline_manifest (
              pipeline_run_id, manifest_path, manifest_json, payload_set_hash, imported_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(pipeline_run_id) DO UPDATE SET
              manifest_path = excluded.manifest_path,
              manifest_json = excluded.manifest_json,
              payload_set_hash = excluded.payload_set_hash,
              imported_at = excluded.imported_at
            """,
            (
                pipeline_id,
                manifest_rel,
                json.dumps(manifest, ensure_ascii=False),
                set_hash,
                utc_now(),
            ),
        )
    _record_review_handoff(pipeline_id, manifest, manifest_rel)
    return _result(
        pipeline_id,
        source_path=source_path,
        revisions_added=imported["units_imported"],
        revisions_skipped=imported["revisions_skipped"],
        unchanged=False,
        pipeline_is_new=imported["pipeline_is_new"],
        manifest_path=manifest_rel,
    )
