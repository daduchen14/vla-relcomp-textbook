#!/usr/bin/env python3
"""验收 A/B task stats、Wilson 区间、macro/micro 与缺失说明。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from .compute_baseline_stats import compute
except ImportError:
    from compute_baseline_stats import compute


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def normalized(rows: list[dict]) -> list[dict[str, str]]:
    return [{key: str(value) for key, value in row.items()} for row in rows]


def check(raw: Path, stats: Path, report: Path):
    expected_rows, expected_report = compute(raw)
    if read_csv(stats) != normalized(expected_rows): raise ValueError("task stats 不可由 raw episodes 精确重建")
    if json.loads(report.read_text(encoding="utf-8")) != expected_report: raise ValueError("summary report 不可精确重建")
    return expected_rows, expected_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for prefix in ("example", "challenge"):
        for name in ("raw", "stats", "report"):
            parser.add_argument(f"--{prefix}-{name}", type=Path, required=True)
    parser.add_argument("--challenge-memo", type=Path, required=True)
    args = parser.parse_args()
    example = check(args.example_raw, args.example_stats, args.example_report)
    challenge = check(args.challenge_raw, args.challenge_stats, args.challenge_report)
    if example == challenge: raise ValueError("挑战不得复制 A 的 episode 或统计")
    memo = args.challenge_memo.read_text(encoding="utf-8").strip()
    required = ("Wilson", "successes", "valid_n", "macro", "micro", "missing", "synthetic")
    if len(memo) < 170 or not all(token in memo for token in required): raise ValueError("challenge memo 不完整")
    print("PASS: Day 22 task-level Wilson and macro/micro statistics")


if __name__ == "__main__": main()
