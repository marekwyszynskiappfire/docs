"""Jira wiki → ADF conversion."""

from jira_wiki_adf import wiki_to_adf_document


def test_heading_and_bullet():
    doc = wiki_to_adf_document("h3. QA feedback\n\n* Item one\n* Item two")
    types = [b["type"] for b in doc["content"]]
    assert types[0] == "heading"
    assert types[1] == "bulletList"
    assert len(doc["content"][1]["content"]) == 2


def test_italic_inline():
    doc = wiki_to_adf_document("_Context:_ details")
    para = doc["content"][0]
    marks = {m["type"] for n in para["content"] for m in n.get("marks", [])}
    assert "em" in marks


def test_horizontal_rule():
    doc = wiki_to_adf_document("line\n----\nend")
    assert any(b["type"] == "rule" for b in doc["content"])
