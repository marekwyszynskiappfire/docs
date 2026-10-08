#!/usr/bin/env bash
# Symlink Trinity skill roots into Cursor user skills (or project .cursor/skills).
set -euo pipefail
TRINITY_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$TRINITY_ROOT/.." && pwd)"

TARGET="${1:-$HOME/.cursor/skills}"
mkdir -p "$TARGET"

link() {
  local name="$1"
  local src="$2"
  local dest="$TARGET/$name"
  if [[ -L "$dest" ]] || [[ -e "$dest" ]]; then
    echo "skip (exists): $dest"
    return
  fi
  ln -s "$src" "$dest"
  echo "linked $dest -> $src"
}

link "trinity-reviewer" "$TRINITY_ROOT/reviewer"
if [[ -f "$TRINITY_ROOT/creator/SKILL.md" ]]; then
  link "trinity-creator" "$TRINITY_ROOT/creator"
else
  echo "note: Trinity/creator has no SKILL.md yet — link when Creator cutover completes"
fi
if [[ -f "$TRINITY_ROOT/importer/SKILL.md" ]]; then
  link "trinity-importer" "$TRINITY_ROOT/importer"
fi

echo ""
echo "Trinity skills target: $TARGET"
echo "Repo root: $REPO_ROOT"
echo "Run preflight: $TRINITY_ROOT/PREFLIGHT.md"
