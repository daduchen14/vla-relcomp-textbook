#!/usr/bin/env python3
"""验收 A/B evidence index、基数、孤儿规则与证据边界。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from .build_evidence_index import build
except ImportError:
    from build_evidence_index import build


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def check(registry, videos, stages, exceptions, output, report):
    rows, expected_report = build(registry, videos, stages, exceptions)
    if read(output) != rows: raise ValueError("evidence index 不可由四个输入精确重建")
    if json.loads(report.read_text(encoding="utf-8")) != expected_report: raise ValueError("evidence report 不可精确重建")
    return rows, expected_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for prefix in ("example", "challenge"):
        for name in ("registry", "videos", "stages", "exceptions", "output", "report"):
            parser.add_argument(f"--{prefix}-{name}", type=Path, required=True)
    parser.add_argument("--challenge-memo", type=Path, required=True); args = parser.parse_args()
    a = check(args.example_registry, args.example_videos, args.example_stages, args.example_exceptions, args.example_output, args.example_report)
    b = check(args.challenge_registry, args.challenge_videos, args.challenge_stages, args.challenge_exceptions, args.challenge_output, args.challenge_report)
    if a == b: raise ValueError("挑战不得复制 A evidence index")
    memo = args.challenge_memo.read_text(encoding="utf-8").strip()
    required = ("episode_id", "left join", "cardinality", "orphan", "video", "exception", "stage", "missing", "causal")
    if len(memo) < 180 or not all(token in memo for token in required): raise ValueError("challenge memo 不完整")
    print("PASS: Day 23 one-to-one evidence index and triage boundary")


if __name__ == "__main__": main()
