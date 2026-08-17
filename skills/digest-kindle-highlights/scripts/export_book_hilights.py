#!/usr/bin/env python3
"""すべてのKindleハイライトを00_self/book_hilight.mdへ出力する。"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


FIELD = re.compile(r"^(kindle-(?:title|author|lastAnnotatedDate)):\s*(.*)$")
TRAILER = re.compile(
    r"\s+—\s+location:\s+\[[^]]+]\((?P<link>[^)]+)\)"
    r"(?:\s+\^ref-[A-Za-z0-9-]+)?\s*$"
)


def clean(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def parse(path: Path) -> tuple[dict[str, str], list[tuple[str, str]]]:
    text = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    if text.startswith("---\n"):
        for line in text.split("---\n", 2)[1].splitlines():
            match = FIELD.match(line)
            if match:
                metadata[match.group(1)] = clean(match.group(2))

    if "## Highlights" not in text:
        return metadata, []
    highlights: list[tuple[str, str]] = []
    for chunk in re.split(r"\n---\s*(?:\n|$)", text.split("## Highlights", 1)[1]):
        chunk = chunk.strip()
        if not chunk:
            continue
        match = TRAILER.search(chunk)
        quote = chunk[: match.start()].strip() if match else chunk
        link = match.group("link") if match else ""
        if quote:
            highlights.append((quote, link))
    return metadata, highlights


def cell(value: str) -> str:
    return " ".join(value.split()).replace("\\", "\\\\").replace("|", "\\|")


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
    args = parser.parse_args()
    source_dir = resolve_source(args.root, args.source)
    target = args.root / "00_self" / "book_hilight.md"
    if not source_dir.is_dir():
        parser.error(f"見つかりません: {source_dir}")

    rows = ["# Kindleハイライト", "", "| 日付 | 言葉 | 出典 |", "| --- | --- | --- |"]
    books = highlights_count = 0
    for path in sorted(source_dir.glob("*.md")):
        meta, highlights = parse(path)
        if not highlights:
            continue
        books += 1
        title = cell(meta.get("kindle-title", path.stem))
        author = cell(meta.get("kindle-author", "不明"))
        annotated = meta.get("kindle-lastAnnotatedDate", "")
        date = "—" if not annotated or annotated == "Invalid date" else cell(annotated)
        for quote, link in highlights:
            source = f"『{title}』— {author}"
            if link:
                source = f"[『{title}』]({link}) — {author}"
            rows.append(f"| {date} | {cell(quote)} | {source} |")
            highlights_count += 1

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"{books}冊・{highlights_count}件を {target} に出力しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
