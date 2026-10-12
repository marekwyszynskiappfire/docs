from pathlib import Path

from reviewer_reports import resolve_epic_report_path, resolve_portfolio_report_path


def test_resolve_epic_and_portfolio_paths(tmp_path, monkeypatch):
    run = tmp_path / "run-2026"
    epic = run / "ONE-1"
    epic.mkdir(parents=True)
    (epic / "review-report.html").write_text("<html></html>", encoding="utf-8")
    (run / "portfolio").mkdir()
    (run / "portfolio" / "index.html").write_text("<html></html>", encoding="utf-8")

    monkeypatch.setattr(
        "reviewer_reports.docs_repo_root",
        lambda: tmp_path,
    )
    assert resolve_epic_report_path(str(run), "ONE-1") == epic / "review-report.html"
    assert resolve_portfolio_report_path(str(run)) == run / "portfolio" / "index.html"
