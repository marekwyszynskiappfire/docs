#!/usr/bin/env bash
# Stop processes commonly used by Trinity Studio (API :8765, Vite :5173).
set -euo pipefail
API_PORT="${QA_STUDIO_PORT:-8765}"
UI_PORT="${QA_STUDIO_UI_PORT:-5173}"

for port in "$API_PORT" "$UI_PORT" 5174; do
  pids="$(lsof -ti ":$port" 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo "Stopping :$port ($pids)"
    # shellcheck disable=SC2086
    kill $pids 2>/dev/null || true
  fi
done
echo "Done."
