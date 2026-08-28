#!/usr/bin/env python3
"""验收锁定字段来源、冻结阈值、A/B 事件日志和误差解释。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .build_event_contract import build
    from .event_logger import summarize
except ImportError:
    from build_event_contract import build
    from event_logger import summarize


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True); parser.add_argument("--thresholds", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True); parser.add_argument("--example-input", type=Path, required=True)
    parser.add_argument("--example-output", type=Path, required=True); parser.add_argument("--challenge-input", type=Path, required=True)
    parser.add_argument("--challenge-output", type=Path, required=True); parser.add_argument("--challenge-explanation", type=Path, required=True)
    args = parser.parse_args()
    if json.loads(args.contract.read_text(encoding="utf-8")) != build(args.upstream.resolve()):
        raise ValueError("frame-field contract 必须从锁定源码重建")
    expected_a = summarize(args.example_input, args.thresholds); expected_b = summarize(args.challenge_input, args.thresholds)
    if json.loads(args.example_output.read_text(encoding="utf-8")) != expected_a:
        raise ValueError("A event log 与原始 frames / thresholds 不一致")
    actual_b = json.loads(args.challenge_output.read_text(encoding="utf-8"))
    if actual_b != expected_b or expected_a == expected_b:
        raise ValueError("挑战必须用 B 新轨迹完整重算")
    if expected_b["events"]["target_contacted"]["first_step"] != 5:
        raise ValueError("B 单帧 contact 闪烁没有被过滤")
    if expected_b["anomalies"] != ["relation_before_reference_approached"]:
        raise ValueError("B 必须保留 relation 先于 approach 的异常证据")
    note = args.challenge_explanation.read_text(encoding="utf-8").strip()
    required = ("false positive", "false negative", "contact", "lift", "approach", "relation")
    if len(note) < 140 or not all(word in note for word in required):
        raise ValueError("挑战解释须≥140字并覆盖四事件与假阳/假阴")
    print("PASS: Day 12 frozen thresholds and changed four-stage event challenge")


if __name__ == "__main__": main()
