"""Read/write Trinity persona markdown under Trinity/personas/."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

_EXECUTABLE_HTML = re.compile(r"<\s*(script|iframe|object|embed)\b|javascript\s*:", re.IGNORECASE)
_REVISION_KEEP = 20


class PersonaConflict(Exception):
    def __init__(self, content: str, content_sha256: str) -> None:
        self.content = content
        self.content_sha256 = content_sha256
        super().__init__("Persona changed on disk")


def persona_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_persona_markdown(content: str) -> None:
    if "\x00" in content:
        raise ValueError("Persona markdown cannot contain null bytes")
    if _EXECUTABLE_HTML.search(content):
        raise ValueError("Persona markdown cannot contain executable HTML")


def docs_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def personas_dir() -> Path:
    return docs_repo_root() / "Trinity" / "personas"


def validate_filename(name: str) -> str:
    if not name or name != Path(name).name:
        raise ValueError("Invalid persona filename")
    if ".." in name or "/" in name or "\\" in name:
        raise ValueError("Invalid persona filename")
    if not name.endswith(".md"):
        raise ValueError("Persona files must be .md")
    return name


def persona_display_name(content: str, filename: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            if title:
                return title
    return filename


def list_persona_files() -> list[dict[str, str]]:
    root = personas_dir()
    if not root.is_dir():
        return []
    items: list[dict[str, str]] = []
    for path in sorted(root.glob("*.md"), key=lambda item: item.name):
        if path.name == "README.md":
            continue
        content = path.read_text(encoding="utf-8")
        items.append({"id": path.name, "label": persona_display_name(content, path.name)})
    items.sort(key=lambda item: item["label"].casefold())
    return items


def read_persona(filename: str) -> dict[str, str]:
    name = validate_filename(filename)
    path = personas_dir() / name
    if not path.is_file():
        raise FileNotFoundError(name)
    content = path.read_text(encoding="utf-8")
    return {"id": name, "content": content, "content_sha256": persona_sha256(content)}


def write_persona(filename: str, content: str, expected_sha256: str) -> dict[str, str]:
    validate_persona_markdown(content)
    name = validate_filename(filename)
    root = personas_dir()
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    previous = path.read_text(encoding="utf-8") if path.is_file() else None
    current_hash = persona_sha256(previous) if previous is not None else ""
    if previous is None:
        raise FileNotFoundError(name)
    if current_hash != expected_sha256:
        raise PersonaConflict(previous, current_hash)
    if previous != content:
        _remember(name, previous)
    path.write_text(content, encoding="utf-8")
    return {"id": name, "saved": True, "content_sha256": persona_sha256(content)}


def list_revisions(filename: str) -> list[dict[str, str | int]]:
    name = validate_filename(filename)
    from db import db

    with db() as conn:
        rows = conn.execute(
            """
            SELECT id, content_sha256, created_at, content
            FROM persona_revision WHERE filename = ? ORDER BY id DESC LIMIT ?
            """,
            (name, _REVISION_KEEP),
        ).fetchall()
    items: list[dict[str, str | int]] = []
    for row in rows:
        first = next((line.strip() for line in str(row["content"]).splitlines() if line.strip()), "")
        items.append(
            {
                "id": int(row["id"]),
                "content_sha256": str(row["content_sha256"]),
                "created_at": str(row["created_at"]),
                "excerpt": first[:120],
            }
        )
    return items


def restore_revision(filename: str, revision_id: int, expected_sha256: str) -> dict[str, str]:
    name = validate_filename(filename)
    from db import db

    with db() as conn:
        row = conn.execute(
            "SELECT content FROM persona_revision WHERE id = ? AND filename = ?",
            (revision_id, name),
        ).fetchone()
    if row is None:
        raise FileNotFoundError(f"Revision {revision_id} for {name}")
    write_persona(name, str(row["content"]), expected_sha256)
    return read_persona(name)


def _remember(filename: str, content: str) -> None:
    from db import db

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    digest = persona_sha256(content)
    with db() as conn:
        conn.execute(
            """
            INSERT INTO persona_revision (filename, content, content_sha256, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (filename, content, digest, now),
        )
        conn.execute(
            """
            DELETE FROM persona_revision
            WHERE filename = ? AND id NOT IN (
              SELECT id FROM persona_revision WHERE filename = ? ORDER BY id DESC LIMIT ?
            )
            """,
            (filename, filename, _REVISION_KEEP),
        )
