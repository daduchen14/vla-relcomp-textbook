#!/usr/bin/env python3
"""机器验收 Day 3 的 observation 摘要、调用链和独立挑战。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

COMMIT = "babe582ebffc82b979b77964a7e56417d02f63a4"
RAW_KEYS = {
    "agentview_image", "robot0_eye_in_hand_image", "robot0_eef_pos",
    "robot0_eef_quat", "robot0_gripper_qpos",
}


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--call-chain", type=Path, required=True)
    parser.add_argument("--challenge", type=Path)
    args = parser.parse_args()
    check_summary(args.summary)
    check_chain(args.call_chain)
    if args.challenge:
        challenge = check_summary(args.challenge, "day03_observation_changed_input")
        if challenge["fixture_id"] == json.loads(args.summary.read_text())["fixture_id"]:
            raise ValueError("独立挑战不能复用示例 fixture")
    print("PASS: Day 3 machine deliverables")


if __name__ == "__main__":
    main()
