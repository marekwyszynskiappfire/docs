"""Read/write Trinity persona markdown under Trinity/personas/."""

from __future__ import annotations

from pathlib import Path


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


def list_persona_files() -> list[dict[str, str]]:
    root = personas_dir()
    if not root.is_dir():
        return []
    items: list[dict[str, str]] = []
    for path in sorted(root.glob("*.md")):
        if path.name == "README.md":
            continue
        items.append({"id": path.name, "label": path.stem.replace("-", " ").title()})
    return items


def read_persona(filename: str) -> dict[str, str]:
    name = validate_filename(filename)
    path = personas_dir() / name
    if not path.is_file():
        raise FileNotFoundError(name)
    return {"id": name, "content": path.read_text(encoding="utf-8")}


def write_persona(filename: str, content: str) -> dict[str, str]:
    name = validate_filename(filename)
    root = personas_dir()
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    path.write_text(content, encoding="utf-8")
    return {"id": name, "saved": True}
