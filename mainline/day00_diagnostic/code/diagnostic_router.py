#!/usr/bin/env python3
"""记录 Day 0 诊断结果，并生成最短补习路线。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "shared/schemas/day00_routes.json"
DEFAULT_OUTPUT = ROOT / "learner_outputs/mainline/day00_diagnostic/route.json"


def load_manifest() -> dict:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = {f"F{number:02d}" for number in range(1, 19)}
    actual = {route["id"] for route in data["routes"]}
    if actual != expected:
        raise ValueError(f"路由必须恰好覆盖 F01–F18，当前差异：{expected ^ actual}")
    for route in data["routes"]:
        if not (ROOT / route["path"]).is_file():
            raise FileNotFoundError(route["path"])
    return data


def initialise(output: Path, force: bool) -> None:
    if output.exists() and not force:
        raise FileExistsError(f"{output} 已存在；保留记录，或显式加 --force")
    routes = load_manifest()["routes"]
    payload = {"schema_version": 1, "results": {r["id"]: "untested" for r in routes}}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已初始化：{output}")


def record(output: Path, route_id: str, status: str) -> None:
    manifest = load_manifest()
    allowed = set(manifest["allowed_status"]) - {"untested"}
    if route_id not in {r["id"] for r in manifest["routes"]} or status not in allowed:
        raise ValueError("记录格式应为 F01–F18 与 pass/needs_review")
    data = json.loads(output.read_text(encoding="utf-8"))
    data["results"][route_id] = status
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已记录：{route_id} = {status}")


def report(output: Path) -> None:
    manifest = load_manifest()
    results = json.loads(output.read_text(encoding="utf-8"))["results"]
    lookup = {route["id"]: route for route in manifest["routes"]}
    gaps = [key for key, value in results.items() if value == "needs_review"]
    pending = [key for key, value in results.items() if value == "untested"]
    for key in gaps:
        print(f"补习 {key}：{lookup[key]['path']}")
    if pending:
        print("延迟诊断待完成：" + ", ".join(pending))
    if not gaps:
        print("入口诊断无补习项：可直接进入项目主线；延迟项到相关 Day 再检查。")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--init", action="store_true")
    actions.add_argument("--record", nargs=2, metavar=("FNN", "STATUS"))
    actions.add_argument("--report", action="store_true")
    actions.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.check:
        load_manifest(); print("PASS: F01–F18 路由与目标文件完整")
    elif args.init:
        initialise(args.output, args.force)
    elif args.record:
        record(args.output, *args.record)
    else:
        report(args.output)


if __name__ == "__main__":
    main()
