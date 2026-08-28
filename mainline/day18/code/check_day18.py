#!/usr/bin/env python3
"""验收 A/B L0 registry、planned video index 与未运行边界说明。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from .build_l0_registry import build as build_registry
    from .build_video_index import build as build_index
except ImportError:
    from build_l0_registry import build as build_registry
    from build_video_index import build as build_index


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def normalized(rows): return [{key: str(value) for key, value in row.items()} for row in rows]


def check_one(table, spec, registry, index, report, repo_root):
    expected_registry = build_registry(table, spec)
    if read(registry) != normalized(expected_registry): raise ValueError("L0 registry 必须从对应 spec 和锁定 task table 重建")
    expected_index, expected_report = build_index(registry, repo_root)
    if read(index) != normalized(expected_index) or json.loads(report.read_text()) != expected_report:
        raise ValueError("video index/report 必须从 registry 和实际文件状态重建")
    return expected_registry, expected_report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--task-table", type=Path, required=True)
    p.add_argument("--repo-root", type=Path, required=True)
    for prefix in ("example", "challenge"):
        p.add_argument(f"--{prefix}-spec", type=Path, required=True); p.add_argument(f"--{prefix}-registry", type=Path, required=True)
        p.add_argument(f"--{prefix}-index", type=Path, required=True); p.add_argument(f"--{prefix}-report", type=Path, required=True)
    p.add_argument("--challenge-memo", type=Path, required=True); args = p.parse_args()
    a = check_one(args.task_table, args.example_spec, args.example_registry, args.example_index, args.example_report, args.repo_root)
    b = check_one(args.task_table, args.challenge_spec, args.challenge_registry, args.challenge_index, args.challenge_report, args.repo_root)
    if a == b: raise ValueError("挑战不得复制 A L0 计划")
    note = args.challenge_memo.read_text(encoding="utf-8").strip()
    required = ("L0", "task", "seed", "init_state", "PLANNED", "video", "denominator")
    if len(note) < 160 or not all(word in note for word in required): raise ValueError("L0 memo 不完整")
    print("PASS: Day 18 changed L0 registry and honest planned-video boundary")


if __name__ == "__main__": main()
