#!/usr/bin/env python3
"""检查 V2 目录、70 天地图和 Markdown 本地链接。"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
DAY_ROW = re.compile(r"^\|\s*(\d{1,2})\s*\|", re.MULTILINE)


def check_structure() -> list[str]:
    errors = []
    for number in range(1, 19):
        if (ROOT / f"day{number:02d}").exists():
            errors.append(f"旧主线目录仍存在：day{number:02d}")
    modules = sorted((ROOT / "foundation_library").glob("f[0-1][0-9]_*"))
    if len(modules) != 18 or any(not (path / "README.md").is_file() for path in modules):
        errors.append("foundation_library 必须恰好含 F01–F18 及 README")
    unexpected = {path.name for path in (ROOT / "mainline").glob("day*")} - {
        "day00_diagnostic", "day03",
    }
    if unexpected:
        errors.append(f"本轮出现未授权 mainline 目录：{sorted(unexpected)}")
    days = [int(value) for value in DAY_ROW.findall((ROOT / "COURSE_MAP.md").read_text())]
    if days != list(range(1, 71)):
        errors.append("COURSE_MAP 必须按顺序恰好列出 Day 1–70")
    return errors


def check_markdown_links() -> list[str]:
    errors = []
    for markdown in ROOT.rglob("*.md"):
        if any(part.startswith(".") or part == "learner_outputs" for part in markdown.parts):
            continue
        for raw in LINK.findall(markdown.read_text(encoding="utf-8")):
            target = raw.strip().split()[0].strip("<>").split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (markdown.parent / target).resolve().exists():
                errors.append(f"{markdown.relative_to(ROOT)} -> {raw}")
    return errors


def main() -> None:
    errors = check_structure() + check_markdown_links()
    if errors:
        print("FAIL: V2 validation")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("PASS: V2 structure, 70-day map, and local Markdown links")


if __name__ == "__main__":
    main()
