#!/usr/bin/env bash
# Prune local Reviewer folders, Studio SQLite test runs, and orphan export dirs.
# Default is dry-run; pass --apply to delete.
set -euo pipefail

APPLY=false
if [[ "${1:-}" == "--apply" ]]; then
  APPLY=true
fi

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DB="${ROOT}/Trinity/studio/data/qa-studio.db"
REVIEWER_RUNS="${ROOT}/Trinity/reviewer/runs"
EXPORTS="${ROOT}/Trinity/studio/data/exports/creator"

# Reviewer portfolio folders to keep (basename). Add more if needed.
KEEP_REVIEWER=(
  "2026-10-08-bp-q4-26-planning-feature"
)

run() {
  if [[ "$APPLY" == true ]]; then
    eval "$@"
  else
    echo "  would: $*"
  fi
}

echo "Trinity local run cleanup (apply=${APPLY})"
echo "DB: ${DB}"

if [[ ! -f "$DB" ]]; then
  echo "No Studio database at $DB — skipping SQLite."
else
  echo ""
  echo "SQLite — remove pytest / idempotency creator runs:"
  PATTERNS=(
    "cov-demo-*"
    "cr-idem-*"
    "idem-run*"
  )
  EXACT_IDS=(cov-demo-run t1 demo-story-suite-test)
  for pat in "${PATTERNS[@]}"; do
    ids=$(sqlite3 "$DB" "SELECT id FROM creator_run WHERE id GLOB '${pat}';" || true)
    if [[ -n "$ids" ]]; then
      while IFS= read -r id; do
        [[ -z "$id" ]] && continue
        run "sqlite3 \"$DB\" \"DELETE FROM creator_run WHERE id = '$id';\""
      done <<< "$ids"
    fi
  done
  for id in "${EXACT_IDS[@]}"; do
    run "sqlite3 \"$DB\" \"DELETE FROM creator_run WHERE id = '$id';\""
  done

  echo ""
  echo "SQLite — remove pipeline runs with missing source_path:"
  while IFS=$'\t' read -r id path; do
    [[ -z "$id" ]] && continue
    if [[ -z "$path" || ! -d "$path" ]]; then
      run "sqlite3 \"$DB\" \"DELETE FROM pipeline_run WHERE id = '$id';\""
    fi
  done < <(sqlite3 -separator $'\t' "$DB" "SELECT id, source_path FROM pipeline_run;")

  if [[ "$APPLY" == true ]]; then
    sqlite3 "$DB" "VACUUM;"
  fi
fi

echo ""
echo "Reviewer runs under ${REVIEWER_RUNS}:"
if [[ -d "$REVIEWER_RUNS" ]]; then
  for dir in "$REVIEWER_RUNS"/*; do
    [[ -d "$dir" ]] || continue
    base=$(basename "$dir")
    keep=false
    for k in "${KEEP_REVIEWER[@]}"; do
      if [[ "$base" == "$k" ]]; then
        keep=true
        break
      fi
    done
    if [[ "$keep" == false ]]; then
      run "rm -rf \"$dir\""
    else
      echo "  keep: $base"
    fi
  done
fi

echo ""
echo "Orphan export dirs (suite-* legacy or no matching creator_run):"
if [[ -d "$EXPORTS" ]]; then
  for dir in "$EXPORTS"/*; do
    [[ -d "$dir" ]] || continue
    base=$(basename "$dir")
    if [[ "$base" == suite-* ]]; then
      run "rm -rf \"$dir\""
      continue
    fi
    if [[ -f "$DB" ]]; then
      found=$(sqlite3 "$DB" "SELECT 1 FROM creator_run WHERE id = '$base' LIMIT 1;" || true)
      if [[ -z "$found" ]]; then
        run "rm -rf \"$dir\""
      fi
    fi
  done
fi

echo ""
if [[ "$APPLY" == true ]]; then
  echo "Done."
else
  echo "Dry-run complete. Re-run with: $0 --apply"
fi
