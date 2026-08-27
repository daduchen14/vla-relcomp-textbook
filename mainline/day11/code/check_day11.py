#!/usr/bin/env python3
"""验收锁定 state contract、A/B 快照与特权边界解释。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .build_state_contract import build, markdown
    from .snapshot_fixture import snapshot
except ImportError:
    from build_state_contract import build, markdown
    from snapshot_fixture import snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--task-table", type=Path, required=True)
    parser.add_argument("--contract-json", type=Path, required=True)
    parser.add_argument("--path-md", type=Path, required=True)
    parser.add_argument("--example-input", type=Path, required=True)
    parser.add_argument("--example-output", type=Path, required=True)
    parser.add_argument("--challenge-input", type=Path, required=True)
    parser.add_argument("--challenge-output", type=Path, required=True)
    parser.add_argument("--challenge-explanation", type=Path, required=True)
    args = parser.parse_args()

    expected_contract = build(args.upstream.resolve(), args.task_table)
    if json.loads(args.contract_json.read_text(encoding="utf-8")) != expected_contract:
        raise ValueError("state contract 必须从锁定源码重建")
    if args.path_md.read_text(encoding="utf-8") != markdown(expected_contract):
        raise ValueError("state path Markdown 与锁定契约不一致")
    expected_a = snapshot(args.task_table, args.example_input)
    expected_b = snapshot(args.task_table, args.challenge_input)
    if json.loads(args.example_output.read_text(encoding="utf-8")) != expected_a:
        raise ValueError("A snapshot 与 task table / fixture 不一致")
    actual_b = json.loads(args.challenge_output.read_text(encoding="utf-8"))
    if actual_b != expected_b or expected_b == expected_a:
        raise ValueError("挑战必须按新 task、新对象和新数值生成 B snapshot")
    note = args.challenge_explanation.read_text(encoding="utf-8").strip()
    required = ("target", "reference", "body_id", "wxyz", "privileged", "policy")
    if len(note) < 120 or not all(word in note for word in required):
        raise ValueError("挑战解释须≥120字，并解释名称/ID/四元数/特权边界")
    print("PASS: Day 11 locked state path and changed object/relation challenge")


if __name__ == "__main__":
    main()
