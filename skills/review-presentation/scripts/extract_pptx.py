#!/usr/bin/env python3
"""標準ライブラリを使い、PPTXから読めるスライド内容と基本診断を抽出する。"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def natural_key(name: str) -> tuple:
    return tuple(int(x) if x.isdigit() else x for x in re.split(r"(\d+)", name))


def xml_text(data: bytes) -> list[str]:
    root = ET.fromstring(data)
    paragraphs: list[str] = []
    for para in root.findall(".//a:p", NS):
        parts: list[str] = []
        for node in para.iter():
            if node.tag.endswith("}t") and node.text:
                parts.append(node.text)
            elif node.tag.endswith("}br"):
                parts.append("\n")
        value = "".join(parts).strip()
        if value:
            paragraphs.append(value)
    return paragraphs


def count_shapes(data: bytes) -> tuple[int, int]:
    root = ET.fromstring(data)
    pictures = len(root.findall(".//p:pic", NS))
    graphics = len(root.findall(".//a:graphic", NS))
    return pictures, graphics


def notes_for_slide(names: set[str], slide_no: int) -> str | None:
    candidate = f"ppt/notesSlides/notesSlide{slide_no}.xml"
    return candidate if candidate in names else None


def extract(path: Path) -> str:
    if not zipfile.is_zipfile(path):
        raise ValueError("入力ファイルは有効なZIPベースのPPTXではありません")
    lines = [f"# PPTX抽出結果: {path.name}", ""]
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        slides = sorted(
            (n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
            key=natural_key,
        )
        lines += [f"- スライド数: {len(slides)}", ""]
        if "docProps/core.xml" in names:
            try:
                core = ET.fromstring(archive.read("docProps/core.xml"))
                for node in core:
                    label = node.tag.rsplit("}", 1)[-1]
                    if node.text and label in {"title", "subject", "creator", "lastModifiedBy"}:
                        lines.append(f"- {label}: {node.text.strip()}")
                lines.append("")
            except ET.ParseError:
                lines.append("- 警告: コアメタデータXMLを解析できませんでした")
        for index, slide_name in enumerate(slides, 1):
            data = archive.read(slide_name)
            try:
                text = xml_text(data)
                pictures, graphics = count_shapes(data)
            except ET.ParseError as exc:
                lines += [f"## スライド {index}", "", f"- 解析エラー: {exc}", ""]
                continue
            chars = sum(len(item) for item in text)
            lines += [f"## スライド {index}", "", f"- 文字数: {chars}", f"- 画像数: {pictures}", f"- グラフィックオブジェクト数: {graphics}"]
            if chars > 700:
                lines.append("- 警告: 文字量が多いため、可読性を画面で確認してください")
            if not text and (pictures or graphics):
                lines.append("- 警告: 視覚要素または画像が中心のスライドのため、テキスト抽出は不完全です")
            lines.append("")
            lines.extend(f"- {item}" for item in text)
            note_name = notes_for_slide(names, index)
            if note_name:
                try:
                    notes = [x for x in xml_text(archive.read(note_name)) if x not in {str(index)}]
                except ET.ParseError:
                    notes = ["[ノートXMLの解析エラー]"]
                if notes:
                    lines += ["", "### 発表者ノート", ""]
                    lines.extend(f"- {item}" for item in notes)
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = extract(args.input)
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 2
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
