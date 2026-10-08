#!/usr/bin/env bash
# Start Trinity Studio API (8765) and Vite dev server (5173).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_PORT="${QA_STUDIO_PORT:-8765}"
UI_PORT="${QA_STUDIO_UI_PORT:-5173}"

port_pids() {
  lsof -ti ":$1" 2>/dev/null || true
}

free_port() {
  local port="$1"
  local pids
  pids="$(port_pids "$port")"
  if [[ -z "$pids" ]]; then
    return 0
  fi
  if [[ "${STUDIO_FORCE:-}" == "1" ]]; then
    echo "Stopping process(es) on :$port ($pids)…"
    # shellcheck disable=SC2086
    kill $pids 2>/dev/null || true
    sleep 0.4
    pids="$(port_pids "$port")"
    if [[ -n "$pids" ]]; then
      # shellcheck disable=SC2086
      kill -9 $pids 2>/dev/null || true
      sleep 0.2
    fi
    return 0
  fi
  echo "ERROR: port $port is already in use (PID: $pids)." >&2
  echo "Stop that process, or restart Studio with:" >&2
  echo "  STUDIO_FORCE=1 $0" >&2
  return 1
}

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
echo "Syncing Python dependencies…"
.venv/bin/pip install -q -r requirements.txt

if [[ ! -d web/node_modules ]]; then
  echo "Installing web dependencies (first run)…"
  (cd web && npm install)
fi

free_port "$API_PORT"
free_port "$UI_PORT"

API_PID=""
VITE_PID=""
cleanup() {
  [[ -n "$API_PID" ]] && kill "$API_PID" 2>/dev/null || true
  [[ -n "$VITE_PID" ]] && kill "$VITE_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting API on http://127.0.0.1:${API_PORT}"
(cd server && PYTHONPATH=. ../.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port "$API_PORT") &
API_PID=$!
sleep 0.3
if ! kill -0 "$API_PID" 2>/dev/null; then
  echo "ERROR: API process exited immediately (port ${API_PORT} may still be held by another app)." >&2
  exit 1
fi

API_OK=0
HEALTH_JSON=""
for _ in $(seq 1 50); do
  if HEALTH_JSON="$(curl -sf "http://127.0.0.1:${API_PORT}/api/health" 2>/dev/null)"; then
    if echo "$HEALTH_JSON" | grep -q 'importer_plan'; then
      API_OK=1
      break
    fi
    echo "ERROR: Port ${API_PORT} is serving a different/old Studio API (health lacks importer_plan)." >&2
    echo "  Response: $HEALTH_JSON" >&2
    echo "Run: STUDIO_FORCE=1 $0" >&2
    kill "$API_PID" 2>/dev/null || true
    exit 1
  fi
  if ! kill -0 "$API_PID" 2>/dev/null; then
    break
  fi
  sleep 0.2
done
if [[ "$API_OK" != 1 ]]; then
  echo "ERROR: API did not become healthy on :${API_PORT} (check traceback above)." >&2
  wait "$API_PID" 2>/dev/null || true
  exit 1
fi

echo "Starting UI on http://127.0.0.1:${UI_PORT}"
(cd web && npm run dev -- --host 127.0.0.1 --port "$UI_PORT" --strictPort) &
VITE_PID=$!

echo ""
echo "Trinity Studio ready:"
echo "  UI:  http://127.0.0.1:${UI_PORT}"
echo "  API: http://127.0.0.1:${API_PORT}/api/health"
echo "Press Ctrl+C to stop both."
wait
