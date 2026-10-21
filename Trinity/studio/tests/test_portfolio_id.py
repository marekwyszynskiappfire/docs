"""Match an imported run folder to its Reviewer portfolio config."""

from personas import docs_repo_root
from run_config import portfolio_id_for_source


def test_portfolio_id_follows_the_run_folder():
    root = docs_repo_root()
    assert portfolio_id_for_source(str(root / "Trinity/reviewer/runs/q4-backlog")) == "q4-backlog"
    assert portfolio_id_for_source(str(root / "Trinity/studio/fixtures/demo-reviewer-run")) is None
    assert portfolio_id_for_source(None) is None
    assert portfolio_id_for_source("") is None
