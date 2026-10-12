#!/usr/bin/env bash
# Import committed demo Reviewer run into Studio SQLite (no Jira).
set -euo pipefail
STUDIO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$STUDIO_ROOT/../.." && pwd)"
FIXTURE_REL="Trinity/studio/fixtures/demo-reviewer-run"
FIXTURE="$REPO_ROOT/$FIXTURE_REL"

if [[ ! -f "$FIXTURE/ONE-90001/review-payload.json" ]]; then
  echo "ERROR: missing $FIXTURE/ONE-90001/review-payload.json" >&2
  exit 1
fi

echo "Importing demo Reviewer run from $FIXTURE_REL …"
"$STUDIO_ROOT/scripts/import-run.sh" "$FIXTURE_REL"
echo ""
echo "Open Studio → Dashboard — pipeline run should list the demo import."
echo "Creator tab → import: Trinity/creator/samples/demo-story.suite.json"
