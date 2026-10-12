#!/usr/bin/env bash
# Create Trinity post-POC GitHub issues on marekwyszynskiappfire/docs.
set -euo pipefail

CREATE=false
if [[ "${1:-}" == "--create" ]]; then
  CREATE=true
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not found. Install GitHub CLI or create issues from Trinity/GITHUB-BACKLOG.md" >&2
  exit 1
fi

REPO="marekwyszynskiappfire/docs"
LABELS="trinity,post-poc"

create_issue() {
  local title="$1"
  local body="$2"
  local extra_labels="${3:-}"
  local labels="$LABELS"
  if [[ -n "$extra_labels" ]]; then
    labels="$labels,$extra_labels"
  fi
  if [[ "$CREATE" == true ]]; then
    gh issue create --repo "$REPO" --title "$title" --label "$labels" --body "$body"
  else
    echo "---"
    echo "TITLE: $title"
    echo "LABELS: $labels"
    echo "$body"
  fi
}

create_issue "Trinity: BigQuery telemetry ingest + Looker Studio" "$(cat <<'EOF'
## Goal
Ship preconfigured dashboards for Mateusz metrics (acceptance rate, rejection reasons, funnel).

## Scope
- Configure `TRINITY_TELEMETRY_URL` + API key (see `Trinity/METRICS.md`)
- Document BigQuery table schema matching telemetry envelope
- Looker Studio (or equivalent) on top of BQ

## Blocked by
GCP / ingest endpoint credentials

## References
- `Trinity/METRICS.md`
- `docs/adr/0002-trinity-importer-telemetry-decisions.md`
- `Trinity/MATEUSZ-POC-ANSWERS.md` §4 dashboards
EOF
)" "telemetry"

create_issue "Trinity: Hard block redaction on Importer execute" "$(cat <<'EOF'
## Context
Grill 2026-10-12 Q2: POC uses warn-only redaction (IQ-17).

## Acceptance
- When `export_preflight_warnings` include redaction hits, `execute_ready` is false unless explicit override (or hard block with no override).

## References
- `Trinity/shared/validate_for_xray.py`
- `Trinity/GRILL-SESSION-2026-10-12.md`
EOF
)" "importer"

create_issue "Trinity: Idempotency block/skip on Importer execute" "$(cat <<'EOF'
## Context
Grill Q4: plan warns when `xray_test_key` exists (`importer_idempotency.py`).

## Acceptance
- Execute skips or blocks creates for drafts that already have keys in Studio (configurable policy).

## References
- `Trinity/studio/server/importer_idempotency.py`
EOF
)" "importer"

create_issue "Trinity Studio: Open local review-report.html from run" "$(cat <<'EOF'
## Goal
RQ-02 parity: one-click open Reviewer HTML report alongside Studio.

## References
- `Trinity/parity-matrix.md`
EOF
)" "studio"

create_issue "Trinity: Map automation_fit to Xray Automated field" "$(cat <<'EOF'
## Context
TQ-02 deferred for POC (all Manual in TC). See `Trinity/importer/reference.md`.

## Acceptance
- Per-test mapping for Jira test-type custom field when `automation_fit` is full/partial.
EOF
)" "importer"

create_issue "Trinity: Wall-clock timing metrics for Mateusz §3" "$(cat <<'EOF'
## Goal
Measure time from batch import → review complete → Xray persist.

## Approach
Derive from `metric_event` timestamps or explicit duration fields in export.
EOF
)" "telemetry,mateusz-poc"

if [[ "$CREATE" != true ]]; then
  echo ""
  echo "Dry-run complete. Run with --create to open issues on $REPO"
fi
