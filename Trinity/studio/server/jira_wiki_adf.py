"""Convert Reviewer Jira wiki markup to Atlassian Document Format (subset)."""

from __future__ import annotations

import re
from typing import Any

_EMPH = re.compile(r"_(.+?)_")


def _text_node(text: str, *, bold: bool = False, italic: bool = False) -> dict[str, Any]:
    node: dict[str, Any] = {"type": "text", "text": text[:32767]}
    marks: list[dict[str, str]] = []
    if bold:
        marks.append({"type": "strong"})
    if italic:
        marks.append({"type": "em"})
    if marks:
        node["marks"] = marks
    return node


def _inline_content(line: str) -> list[dict[str, Any]]:
    """Parse _italic_ segments in a line of plain text."""
    parts: list[dict[str, Any]] = []
    pos = 0
    for match in _EMPH.finditer(line):
        if match.start() > pos:
            parts.append(_text_node(line[pos : match.start()]))
        parts.append(_text_node(match.group(1), italic=True))
        pos = match.end()
    if pos < len(line):
        parts.append(_text_node(line[pos:]))
    return parts or [_text_node("")]


def _paragraph(line: str) -> dict[str, Any]:
    return {"type": "paragraph", "content": _inline_content(line)}


def _heading(level: int, title: str) -> dict[str, Any]:
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": _inline_content(title.strip()),
    }


def _bullet_list(items: list[str]) -> dict[str, Any]:
    return {
        "type": "bulletList",
        "content": [
            {
                "type": "listItem",
                "content": [_paragraph(item)],
            }
            for item in items
        ],
    }


def wiki_to_adf_document(wiki: str) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    bullet_buf: list[str] = []

    def flush_bullets() -> None:
        nonlocal bullet_buf
        if bullet_buf:
            blocks.append(_bullet_list(bullet_buf))
            bullet_buf = []

    for raw in wiki.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_bullets()
            continue
        if stripped in ("----", "—", "---"):
            flush_bullets()
            blocks.append({"type": "rule"})
            continue
        if stripped.startswith("h3."):
            flush_bullets()
            blocks.append(_heading(3, stripped[3:].strip()))
            continue
        if stripped.startswith("h4."):
            flush_bullets()
            blocks.append(_heading(4, stripped[3:].strip()))
            continue
        if stripped.startswith("* "):
            bullet_buf.append(stripped[2:].strip())
            continue
        flush_bullets()
        blocks.append(_paragraph(stripped))

    flush_bullets()
    if not blocks:
        blocks.append(_paragraph("(empty comment)"))
    return {"type": "doc", "version": 1, "content": blocks}
