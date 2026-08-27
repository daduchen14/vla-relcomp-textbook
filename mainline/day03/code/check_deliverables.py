#!/usr/bin/env python3
"""机器验收 Day 3 的 observation 摘要、调用链和独立挑战。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .summarize_observation import build_summary
except ImportError:  # 允许从仓库根直接执行此脚本。
    from summarize_observation import build_summary

COMMIT = "babe582ebffc82b979b77964a7e56417d02f63a4"
RAW_KEYS = {
    "agentview_image", "robot0_eye_in_hand_image", "robot0_eef_pos",
    "robot0_eef_quat", "robot0_gripper_qpos",
}
ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_FIXTURE = ROOT / "shared/fixtures/day03_observation_fixture.json"
CHALLENGE_FIXTURE = ROOT / "shared/fixtures/day03_observation_challenge.json"


def check_summary(path: Path, expected_fixture: str | None = None) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if set(data.get("keys", [])) != RAW_KEYS:
        raise ValueError(f"{path}: observation key 不完整")
    if data.get("source_kind") != "local_fixture_not_vla_arena_run":
        raise ValueError(f"{path}: fixture/真实运行边界缺失")
    if expected_fixture and data.get("fixture_id") != expected_fixture:
        raise ValueError(f"{path}: 没有使用指定的新输入")
    for name in RAW_KEYS:
        if not data["arrays"][name].get("shape") or not data["arrays"][name].get("dtype"):
            raise ValueError(f"{path}: {name} 缺少 shape/dtype")
    return data


def check_chain(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    required = [COMMIT, "prepare_observation", "get_action", "process_action",
                "env.step", "BDDLBaseDomain.step", "_check_success", "is_success_done"]
    missing = [item for item in required if item not in text]
    if missing:
        raise ValueError(f"{path}: 调用链缺少 {missing}")


def check_challenge(path: Path, reasoning_path: Path) -> None:
    actual = check_summary(path, "day03_observation_changed_input")
    expected = build_summary(CHALLENGE_FIXTURE)
    if actual != expected:
        raise ValueError("独立挑战摘要必须由 challenge fixture 的真实内容计算，不能复制示例后改 ID")
    reasoning = reasoning_path.read_text(encoding="utf-8").strip()
    compact = "".join(reasoning.split())
    required = ["[2,3,3]", "[3,1,3]", "float64"]
    if not 120 <= len(compact) <= 500 or any(item not in compact for item in required):
        raise ValueError("独立说明需 120–500 字，并准确出现两路新图像 shape 与 float64")
    if not any(boundary in compact for boundary in ("未运行", "fixture", "非真实")):
        raise ValueError("独立说明必须写明 fixture 与真实 VLA-Arena 运行边界")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--call-chain", type=Path, required=True)
    parser.add_argument("--challenge", type=Path)
    parser.add_argument("--challenge-reasoning", type=Path)
    args = parser.parse_args()
    check_summary(args.summary)
    check_chain(args.call_chain)
    if bool(args.challenge) != bool(args.challenge_reasoning):
        raise ValueError("challenge 与 challenge-reasoning 必须同时提供")
    if args.challenge:
        check_challenge(args.challenge, args.challenge_reasoning)
    print("PASS: Day 3 machine deliverables")


if __name__ == "__main__":
    main()
