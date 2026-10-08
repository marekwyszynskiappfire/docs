#!/usr/bin/env bash
# Start Trinity Studio API (8765) and Vite dev server (5173).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

if [[ ! -d web/node_modules ]]; then
  echo "Installing web dependencies (first run)…"
  (cd web && npm install)
fi

API_PID=""
VITE_PID=""
cleanup() {
  [[ -n "$API_PID" ]] && kill "$API_PID" 2>/dev/null || true
  [[ -n "$VITE_PID" ]] && kill "$VITE_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting API on http://127.0.0.1:8765"
(cd server && PYTHONPATH=. ../.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8765) &
API_PID=$!

for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8765/api/health >/dev/null; then
    break
  fi
  sleep 0.2
done

echo "Starting UI on http://127.0.0.1:5173"
(cd web && npm run dev -- --host 127.0.0.1 --port 5173) &
VITE_PID=$!

echo ""
echo "Trinity Studio ready:"
echo "  UI:  http://127.0.0.1:5173"
echo "  API: http://127.0.0.1:8765/api/health"
echo "Press Ctrl+C to stop both."
wait
