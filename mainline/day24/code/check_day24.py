#!/usr/bin/env python3
"""验收 A/B 候选比较、预注册排序、held-out 边界与选择 memo。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try: from .select_primary_model import select
except ImportError: from select_primary_model import select


def read(path):
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def norm(rows): return [{key: str(value) for key, value in row.items()} for row in rows]


def check(stats, policy, comparison, decision):
    rows, expected = select(stats, policy)
    if read(comparison) != norm(rows) or json.loads(decision.read_text(encoding="utf-8")) != expected:
        raise ValueError("model comparison/decision 不可精确重建")
    return rows, expected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for prefix in ("example", "challenge"):
        for name in ("stats", "policy", "comparison", "decision"):
            parser.add_argument(f"--{prefix}-{name}", type=Path, required=True)
    parser.add_argument("--challenge-memo", type=Path, required=True); args = parser.parse_args()
    a = check(args.example_stats, args.example_policy, args.example_comparison, args.example_decision)
    b = check(args.challenge_stats, args.challenge_policy, args.challenge_comparison, args.challenge_decision)
    if a == b: raise ValueError("挑战不得复制 A 比较/选择")
    memo = args.challenge_memo.read_text(encoding="utf-8").strip()
    required = ("L0", "eligible", "valid_n", "macro", "worst_task", "tie-break", "L1", "L2", "held-out", "synthetic", "freeze")
    if len(memo) < 200 or not all(token in memo for token in required): raise ValueError("challenge memo 不完整")
    print("PASS: Day 24 fair L0 comparison and primary-model freeze record")


if __name__ == "__main__": main()
