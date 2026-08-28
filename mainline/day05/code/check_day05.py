#!/usr/bin/env python3
"""验收真实 adapter 契约和 A/B 离线 shape/dtype 接口卡。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .build_interface_card import build_card
    from .trace_adapter import build_contract
except ImportError:
    from build_interface_card import build_card
    from trace_adapter import build_contract


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check(upstream: Path, contract: Path, example_input: Path, example_card: Path,
          challenge_input: Path, challenge_card: Path) -> None:
    if read(contract) != build_contract(upstream):
        raise ValueError("adapter contract 必须由锁定源码重新提取")
    expected_a, expected_b = build_card(example_input), build_card(challenge_input)
    if read(example_card) != expected_a: raise ValueError("示例接口卡与 A 输入不一致")
    if read(challenge_card) != expected_b:
        raise ValueError("挑战接口卡必须由 B 的新 shape/rotation/task 计算，不能复制 A 后改 ID")
    if expected_a["inputs"] == expected_b["inputs"] or expected_a["task"] == expected_b["task"]:
        raise ValueError("独立挑战没有真正改变输入")
    print("PASS: Day 5 locked adapter contract and changed-input interface card")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("upstream", "contract", "example-input", "example-card", "challenge-input", "challenge-card"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    check(args.upstream.resolve(), args.contract, args.example_input, args.example_card,
          args.challenge_input, args.challenge_card)


if __name__ == "__main__":
    main()
