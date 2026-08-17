#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
SKILLS_DIR="$REPO_DIR/skills"
CODEX_DIR=${CODEX_HOME:-"$HOME/.codex"}
TARGET_PARENT="$CODEX_DIR/skills"
MODE=install

if [ "${1:-}" = "--replace" ]; then
  MODE=replace
  shift
fi

if [ ! -d "$SKILLS_DIR" ] || [ -z "$CODEX_DIR" ] || [ "$TARGET_PARENT" = "/" ]; then
  echo "エラー: Skillの配置元またはインストール先を安全に解決できませんでした" >&2
  exit 1
fi

SELECTED=""
if [ "$#" -eq 0 ]; then
  for source_dir in "$SKILLS_DIR"/*; do
    [ -d "$source_dir" ] || continue
    SELECTED="$SELECTED ${source_dir##*/}"
  done
else
  for skill in "$@"; do
    case "$skill" in
      ''|*[!a-z0-9-]*)
        echo "エラー: 無効なSkill名です: $skill" >&2
        exit 1
        ;;
    esac
    SELECTED="$SELECTED $skill"
  done
fi

if [ -z "$SELECTED" ]; then
  echo "エラー: インストール対象のSkillがありません" >&2
  exit 1
fi

STAMP=$(date +%Y%m%d%H%M%S)

# 全対象を先に検査し、途中までインストールされる状態を避ける。
for skill in $SELECTED; do
  source_dir="$SKILLS_DIR/$skill"
  target_dir="$TARGET_PARENT/$skill"
  backup_dir="$target_dir.backup-$STAMP"

  if [ ! -f "$source_dir/SKILL.md" ]; then
    echo "エラー: Skill本体が見つかりません: $source_dir" >&2
    exit 1
  fi

  if [ "$MODE" = "install" ] && [ -e "$target_dir" ]; then
    echo "エラー: インストール先が既に存在します: $target_dir" >&2
    echo "更新する場合は--replaceを指定してください。" >&2
    exit 2
  fi

  if [ "$MODE" = "replace" ] && [ -e "$backup_dir" ]; then
    echo "エラー: バックアップ先が既に存在します: $backup_dir" >&2
    exit 1
  fi
done

mkdir -p "$TARGET_PARENT"

for skill in $SELECTED; do
  source_dir="$SKILLS_DIR/$skill"
  target_dir="$TARGET_PARENT/$skill"
  backup_dir="$target_dir.backup-$STAMP"

  if [ "$MODE" = "replace" ] && [ -e "$target_dir" ]; then
    mv "$target_dir" "$backup_dir"
    echo "既存コピーを退避しました: $backup_dir"
  fi

  if ! cp -R "$source_dir" "$target_dir"; then
    echo "エラー: インストールに失敗しました: $skill" >&2
    if [ -e "$backup_dir" ] && [ ! -e "$target_dir" ]; then
      mv "$backup_dir" "$target_dir"
      echo "既存コピーを復元しました: $target_dir" >&2
    fi
    exit 1
  fi

  echo "インストールしました: $target_dir"
done
