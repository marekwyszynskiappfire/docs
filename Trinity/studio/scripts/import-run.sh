#!/usr/bin/env bash
set -euo pipefail
STUDIO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$STUDIO_ROOT/../.." && pwd)"
RUN_PATH="${1:?Usage: $0 Trinity/reviewer/runs/<your-run-folder>}"
cd "$STUDIO_ROOT/server"
export PYTHONPATH=.
PYTHON="${STUDIO_ROOT}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then PYTHON=python3; fi
"$PYTHON" -c "
from pathlib import Path
from import_review import import_reviewer_run
r = import_reviewer_run(Path('$REPO_ROOT') / '$RUN_PATH')
print(r)
"
