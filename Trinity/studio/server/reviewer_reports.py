"""Resolve on-disk Reviewer Profile A HTML next to imported run folders."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from personas import docs_repo_root


def _run_folder(source_path: str | None) -> Path | None:
    if not source_path:
        return None
    root = docs_repo_root()
    p = Path(source_path)
    if not p.is_absolute():
        p = root / p
    p = p.resolve()
    try:
        p.relative_to(root.resolve())
    except ValueError:
        return None
    return p if p.is_dir() else None


def epic_report_candidates(run_dir: Path, jira_key: str) -> list[Path]:
    return [
        run_dir / jira_key / "review-report.html",
        run_dir / "epics" / jira_key / "review-report.html",
    ]


def resolve_epic_report_path(source_path: str | None, jira_key: str) -> Path | None:
    run_dir = _run_folder(source_path)
    if not run_dir:
        return None
    for candidate in epic_report_candidates(run_dir, jira_key):
        if candidate.is_file():
            return candidate
    return None


def resolve_portfolio_report_path(source_path: str | None) -> Path | None:
    run_dir = _run_folder(source_path)
    if not run_dir:
        return None
    index = run_dir / "portfolio" / "index.html"
    return index if index.is_file() else None


def list_run_review_reports(conn: Any, pipeline_run_id: str) -> dict[str, Any]:
    run = conn.execute("SELECT source_path FROM pipeline_run WHERE id = ?", (pipeline_run_id,)).fetchone()
    if not run:
        raise KeyError("Run not found")
    source_path = run["source_path"]
    rel_source = source_path
    root = docs_repo_root()
    if source_path:
        p = Path(source_path)
        if p.is_absolute():
            try:
                rel_source = str(p.relative_to(root))
            except ValueError:
                rel_source = source_path
    portfolio = resolve_portfolio_report_path(source_path)
    units = conn.execute(
        "SELECT id, jira_key FROM review_unit WHERE pipeline_run_id = ? ORDER BY jira_key",
        (pipeline_run_id,),
    ).fetchall()
    epics: list[dict[str, Any]] = []
    for u in units:
        path = resolve_epic_report_path(source_path, u["jira_key"])
        epics.append(
            {
                "unit_id": u["id"],
                "jira_key": u["jira_key"],
                "report_exists": path is not None,
                "report_relative_path": (
                    str(path.relative_to(root)) if path else None
                ),
                "open_url": f"/api/units/{u['id']}/review-report.html" if path else None,
            }
        )
    return {
        "source_path": rel_source,
        "portfolio_report_exists": portfolio is not None,
        "portfolio_open_url": (
            f"/api/runs/{pipeline_run_id}/portfolio-report.html" if portfolio else None
        ),
        "epics": epics,
    }


def epic_report_for_unit(conn: Any, unit_id: str) -> Path:
    row = conn.execute(
        """
        SELECT u.jira_key, r.source_path
        FROM review_unit u
        JOIN pipeline_run r ON r.id = u.pipeline_run_id
        WHERE u.id = ?
        """,
        (unit_id,),
    ).fetchone()
    if not row:
        raise KeyError("Unit not found")
    path = resolve_epic_report_path(row["source_path"], row["jira_key"])
    if not path:
        raise FileNotFoundError("review-report.html not found beside imported run folder")
    return path


def portfolio_report_for_run(conn: Any, run_id: str) -> Path:
    row = conn.execute("SELECT source_path FROM pipeline_run WHERE id = ?", (run_id,)).fetchone()
    if not row:
        raise KeyError("Run not found")
    path = resolve_portfolio_report_path(row["source_path"])
    if not path:
        raise FileNotFoundError("portfolio/index.html not found")
    return path
