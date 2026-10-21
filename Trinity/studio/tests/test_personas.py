"""Persona markdown is stored as written, with a hash and a restorable revision."""

from __future__ import annotations

SAMPLE = """# Title

- one
- two

See [docs](https://example.com/guide).

| A | B |
| --- | --- |
| 1 | 2 |

```python
print("ok")
```
"""


def test_list_label_is_the_heading_not_the_filename(monkeypatch, tmp_path):
    import personas

    monkeypatch.setattr(personas, "personas_dir", lambda: tmp_path)
    (tmp_path / "reviewer-expert-qa-automation.md").write_text(
        "# Persona: Expert QA Engineer (automation-first)\n\nBody\n",
        encoding="utf-8",
    )
    (tmp_path / "notes.md").write_text("No heading here.\n", encoding="utf-8")
    labels = {item["id"]: item["label"] for item in personas.list_persona_files()}
    assert labels["reviewer-expert-qa-automation.md"] == "Persona: Expert QA Engineer (automation-first)"
    assert labels["notes.md"] == "notes.md"


def test_save_keeps_lists_tables_code_and_links(studio_db, monkeypatch, tmp_path):
    import personas

    monkeypatch.setattr(personas, "personas_dir", lambda: tmp_path)
    path = tmp_path / "qa.md"
    path.write_text("# Title\n", encoding="utf-8")
    opened = personas.read_persona("qa.md")
    saved = personas.write_persona("qa.md", SAMPLE, opened["content_sha256"])
    assert path.read_text(encoding="utf-8") == SAMPLE
    assert saved["content_sha256"] == personas.persona_sha256(SAMPLE)
    again = personas.read_persona("qa.md")
    assert again["content"] == SAMPLE


def test_executable_html_is_rejected(studio_db, monkeypatch, tmp_path):
    import personas

    monkeypatch.setattr(personas, "personas_dir", lambda: tmp_path)
    path = tmp_path / "qa.md"
    path.write_text("# Title\n", encoding="utf-8")
    opened = personas.read_persona("qa.md")
    try:
        personas.write_persona("qa.md", "Hello <script>alert(1)</script>\n", opened["content_sha256"])
    except ValueError as error:
        assert "executable" in str(error)
    else:
        raise AssertionError("script should be rejected")
    assert path.read_text(encoding="utf-8") == "# Title\n"


def test_stale_hash_does_not_overwrite_and_restore_returns_previous(studio_db, monkeypatch, tmp_path):
    import personas

    monkeypatch.setattr(personas, "personas_dir", lambda: tmp_path)
    path = tmp_path / "qa.md"
    path.write_text("# First\n", encoding="utf-8")
    opened = personas.read_persona("qa.md")
    personas.write_persona("qa.md", "# Second\n", opened["content_sha256"])
    try:
        personas.write_persona("qa.md", "# Third\n", opened["content_sha256"])
    except personas.PersonaConflict as error:
        assert error.content == "# Second\n"
    else:
        raise AssertionError("stale hash should conflict")
    assert path.read_text(encoding="utf-8") == "# Second\n"
    revisions = personas.list_revisions("qa.md")
    assert revisions[0]["excerpt"] == "# First"
    current = personas.read_persona("qa.md")
    restored = personas.restore_revision("qa.md", int(revisions[0]["id"]), current["content_sha256"])
    assert restored["content"] == "# First\n"
    assert path.read_text(encoding="utf-8") == "# First\n"
