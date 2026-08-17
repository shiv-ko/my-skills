#!/bin/sh
set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
SKILLS_DIR="$REPO_DIR/skills"
CODEX_DIR=${CODEX_HOME:-"$HOME/.codex"}
TARGET_PARENT="$CODEX_DIR/skills"
STATUS=0

if [ "$#" -eq 0 ]; then
  SELECTED=""
  for source_dir in "$SKILLS_DIR"/*; do
    [ -d "$source_dir" ] || continue
    SELECTED="$SELECTED ${source_dir##*/}"
  done
else
  SELECTED=""
  for skill in "$@"; do
    SELECTED="$SELECTED $skill"
  done
fi

for skill in $SELECTED; do
  source_dir="$SKILLS_DIR/$skill"
  target_dir="$TARGET_PARENT/$skill"

  if [ ! -d "$source_dir" ]; then
    echo "repo-missing  $skill"
    STATUS=1
  elif [ ! -d "$target_dir" ]; then
    echo "not-installed $skill"
    STATUS=1
  elif diff -qr "$source_dir" "$target_dir" >/dev/null 2>&1; then
    echo "in-sync       $skill"
  else
    echo "different     $skill"
    STATUS=1
  fi
done

exit "$STATUS"
