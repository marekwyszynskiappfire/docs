#!/usr/bin/env bash
# Mechanical checks for OPERATOR-ONBOARDING.md — no Jira/MCP required.
set -euo pipefail
TRINITY_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$TRINITY_ROOT/.." && pwd)"
PASS=0
FAIL=0

ok() { echo "PASS: $*"; PASS=$((PASS + 1)); }
bad() { echo "FAIL: $*"; FAIL=$((FAIL + 1)); }

echo "Trinity pilot preflight (repo: $REPO_ROOT)"
echo "---"

if command -v python3 >/dev/null 2>&1; then
  ok "python3 $(python3 --version 2>&1)"
else
  bad "python3 not found"
fi

if command -v node >/dev/null 2>&1; then
  ok "node $(node --version)"
else
  bad "node not found"
fi

SKILLS="${HOME}/.cursor/skills"
for name in trinity-reviewer trinity-creator trinity-importer; do
  if [[ -L "${SKILLS}/${name}" ]] || [[ -e "${SKILLS}/${name}" ]]; then
    ok "skill linked: ${name}"
  else
    bad "skill missing: ${name} (run ./Trinity/scripts/install-trinity-skills.sh)"
  fi
done

DEMO_PAYLOAD="${TRINITY_ROOT}/reviewer/samples/demo-epic.payload.json"
if [[ -f "$DEMO_PAYLOAD" ]]; then
  if python3 "${TRINITY_ROOT}/reviewer/scripts/render_report.py" "$DEMO_PAYLOAD" --strict >/dev/null 2>&1; then
    ok "render_report.py --strict on demo payload"
  else
    bad "render_report.py --strict failed"
  fi
else
  bad "missing demo payload: $DEMO_PAYLOAD"
fi

if curl -sf "http://127.0.0.1:8765/api/health" >/dev/null 2>&1; then
  ok "Studio API health (8765)"
else
  echo "SKIP: Studio not running (start ./Trinity/studio/scripts/start.sh for live check)"
fi

echo "---"
echo "Summary: ${PASS} passed, ${FAIL} failed"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
