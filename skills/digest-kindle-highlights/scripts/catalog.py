#!/usr/bin/env python3
"""Kindleハイライトのファイルと書籍ノートの作成状況を一覧表示する。"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


FIELD_PATTERN = re.compile(r"^(kindle-(?:title|author|asin|highlightsCount)):\s*(.*)$")


def clean(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def metadata(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    with path.open(encoding="utf-8") as source:
        if source.readline().strip() != "---":
            return result
        for line in source:
            if line.strip() == "---":
                break
            match = FIELD_PATTERN.match(line.rstrip("\n"))
            if match:
                result[match.group(1)] = clean(match.group(2))
    return result


def resolve_source(root: Path, explicit: Path | None) -> Path:
    source = explicit
    if source is None and os.environ.get("KINDLE_HIGHLIGHTS_SOURCE"):
        source = Path(os.environ["KINDLE_HIGHLIGHTS_SOURCE"])
    if source is None:
        source = root.resolve().parent / "03_lib" / "kindle_hilights"
    return source.expanduser().resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path, help="Kindleハイライトの原典ディレクトリ")
    parser.add_argument("--query", default="", help="タイトルまたは著者で絞り込む")
    args = parser.parse_args()

    source_dir = resolve_source(args.root, args.source)
    output_dir = args.root / "04_knowledge" / "books"
    if not source_dir.is_dir():
        parser.error(f"見つかりません: {source_dir}")

    query = args.query.casefold()
    rows: list[tuple[str, str, str, str]] = []
    for path in sorted(source_dir.glob("*.md")):
        data = metadata(path)
        title = data.get("kindle-title", path.stem)
        author = data.get("kindle-author", "")
        if query and query not in f"{title} {author}".casefold():
            continue
        count = data.get("kindle-highlightsCount", "?")
        status = "済" if (output_dir / path.name).exists() else "未"
        rows.append((status, count, title, author))

    print("状態\t件数\tタイトル\t著者")
    for row in rows:
        print("\t".join(row))
    print(f"合計: {len(rows)}冊")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
