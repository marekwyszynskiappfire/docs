#!/usr/bin/env bash
# Start Trinity Studio API (8765) and Vite dev server (5173).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_PORT="${QA_STUDIO_PORT:-8765}"
UI_PORT="${QA_STUDIO_UI_PORT:-5173}"

port_pids() {
  # Listeners only. A browser tab can keep a closed socket after Vite exits,
  # and that must not count as the port being in use.
  lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null || true
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

echo "Building React UI (web/dist) for API on :${API_PORT}…"
(cd web && npm run build)

free_port "$API_PORT"
free_port "$UI_PORT"

API_PID=""
VITE_PID=""
INGEST_PID=""
cleanup() {
  [[ -n "$API_PID" ]] && kill "$API_PID" 2>/dev/null || true
  [[ -n "$VITE_PID" ]] && kill "$VITE_PID" 2>/dev/null || true
  [[ -n "$INGEST_PID" ]] && kill "$INGEST_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Load only telemetry/BigQuery settings from .env; explicit shell values win.
eval "$(
  python3 - <<'PY'
import os
import shlex
from pathlib import Path

allowed = {
    "BQ_PROJECT",
    "BQ_DATASET",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "TRINITY_INGEST_PORT",
    "TRINITY_TELEMETRY_API_KEY",
    "TRINITY_TELEMETRY_URL",
}
path = Path(".env")
if path.is_file():
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in allowed and key not in os.environ:
            value = value.strip().strip('"').strip("'")
            print(f"export {key}={shlex.quote(value)}")
PY
)"

BQ_KEY="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/trinity/qa-coe-bigquery.json}"
INGEST_PORT="${TRINITY_INGEST_PORT:-8787}"
INGEST_KEY_FILE="$ROOT/data/.telemetry_ingest_key"
LOCAL_INGEST=0
if [[ -f "$BQ_KEY" ]] && {
  [[ -z "${TRINITY_TELEMETRY_URL:-}" ]] ||
  [[ "${TRINITY_TELEMETRY_URL}" == http://127.0.0.1:* ]] ||
  [[ "${TRINITY_TELEMETRY_URL}" == http://localhost:* ]]
}; then
  LOCAL_INGEST=1
  mkdir -p "$ROOT/data"
  if [[ ! -f "$INGEST_KEY_FILE" ]]; then
    python3 -c 'import secrets; print(secrets.token_urlsafe(32))' > "$INGEST_KEY_FILE"
    chmod 600 "$INGEST_KEY_FILE"
  fi
  INGEST_KEY="$(tr -d '[:space:]' < "$INGEST_KEY_FILE")"
  export GOOGLE_APPLICATION_CREDENTIALS="$BQ_KEY"
  export BQ_PROJECT="${BQ_PROJECT:-qa-coe}"
  export BQ_DATASET="${BQ_DATASET:-trinity}"
  export TRINITY_TELEMETRY_API_KEY="${TRINITY_TELEMETRY_API_KEY:-$INGEST_KEY}"
  export TRINITY_TELEMETRY_URL="${TRINITY_TELEMETRY_URL:-http://127.0.0.1:${INGEST_PORT}/v1/events}"
  INGEST_PY="$HOME/.config/trinity/venv/bin/python"
  if [[ ! -x "$INGEST_PY" ]]; then
    INGEST_PY="$ROOT/.venv/bin/python"
  fi
  free_port "$INGEST_PORT"
  echo "Starting BigQuery ingest on http://127.0.0.1:${INGEST_PORT}/v1/events"
  (cd "$ROOT" && "$INGEST_PY" "$ROOT/scripts/bq_ingest.py") &
  INGEST_PID=$!
  for _ in $(seq 1 200); do
    if curl -sf "http://127.0.0.1:${INGEST_PORT}/health" >/dev/null 2>&1; then
      break
    fi
    if ! kill -0 "$INGEST_PID" 2>/dev/null; then
      echo "ERROR: BigQuery ingest exited during startup." >&2
      exit 1
    fi
    sleep 0.2
  done
  if ! curl -sf "http://127.0.0.1:${INGEST_PORT}/health" >/dev/null 2>&1; then
    echo "ERROR: BigQuery ingest did not become healthy on :${INGEST_PORT}." >&2
    exit 1
  fi
fi

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
echo "  UI (dev):  http://127.0.0.1:${UI_PORT}  ← use this or web/dist on :${API_PORT}"
echo "  API:       http://127.0.0.1:${API_PORT}/api/health"
echo "  Statistics: nav → Statistics, or Dashboard run → Statistics link"
if [[ -n "$INGEST_PID" ]]; then
  echo "  BigQuery:  http://127.0.0.1:${INGEST_PORT}/v1/events (auto-flush after each Studio step)"
fi
echo "Press Ctrl+C to stop."
wait
