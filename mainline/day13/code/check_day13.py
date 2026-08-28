#!/usr/bin/env python3
"""验收 A/B 新规格生成的匹配 pair 和独立设计说明。"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .build_pair_manifest import build
    from .validate_pair_manifest import read_rows, validate
except ImportError:
    from build_pair_manifest import build
    from validate_pair_manifest import read_rows, validate


def normalized(rows: list[dict]) -> list[dict]: return [{key: str(value) for key, value in row.items()} for row in rows]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--task-table", type=Path, required=True)
    parser.add_argument("--example-spec", type=Path, required=True); parser.add_argument("--example-manifest", type=Path, required=True)
    parser.add_argument("--challenge-spec", type=Path, required=True); parser.add_argument("--challenge-manifest", type=Path, required=True)
    parser.add_argument("--challenge-defense", type=Path, required=True); args = parser.parse_args()
    expected_a, expected_b = build(args.task_table, args.example_spec), build(args.task_table, args.challenge_spec)
    if read_rows(args.example_manifest) != normalized(expected_a): raise ValueError("A manifest 必须从 A spec 重建")
    if read_rows(args.challenge_manifest) != normalized(expected_b): raise ValueError("B manifest 必须从新 selector/spec 重建")
    report_a = validate(args.example_manifest, args.task_table); report_b = validate(args.challenge_manifest, args.task_table)
    if report_a["pair_id"] == report_b["pair_id"]: raise ValueError("挑战不能复用 A pair")
    note = args.challenge_defense.read_text(encoding="utf-8").strip()
    required = ("pair_id", "seed", "init_state", "instruction", "semantic", "human review")
    if len(note) < 140 or not all(token in note for token in required):
        raise ValueError("设计说明须≥140字并覆盖匹配键、唯一变化与语义人工复核")
    print("PASS: Day 13 changed-input matched pair manifests and anti-copy defense")


if __name__ == "__main__": main()
