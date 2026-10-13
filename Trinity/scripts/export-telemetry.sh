#!/usr/bin/env bash
# Save local Studio telemetry bundle for Mateusz scorecard / evidence (MATEUSZ-CRITERIA M1).
set -euo pipefail
API="${QA_STUDIO_URL:-http://127.0.0.1:8765}"
OUT="${1:-trinity-telemetry-export-$(date +%Y%m%d-%H%M%S).json}"
curl -sf "${API}/api/telemetry/export" -o "$OUT"
echo "Wrote $OUT"
curl -sf "${API}/api/health" | python3 -c "import json,sys; h=json.load(sys.stdin); print('trinity_version:', h.get('trinity_version'))"
