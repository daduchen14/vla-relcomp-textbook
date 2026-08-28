#!/usr/bin/env python3
"""验收 A/B L1 registry、冻结 guard 与反泄漏说明。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try: from .build_l1_registry import derive
except ImportError: from build_l1_registry import derive


def read(path):
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def normalized(rows): return [{key: str(value) for key, value in row.items()} for row in rows]


def check(table, l0, l1, registry, guard):
    rows, expected_guard = derive(table, l0, l1)
    if read(registry) != normalized(rows) or json.loads(guard.read_text()) != expected_guard:
        raise ValueError("L1 registry/guard 必须从锁定表和对应 L0/L1 spec 重建")
    return rows, expected_guard


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--task-table", type=Path, required=True)
    for prefix in ("example", "challenge"):
        p.add_argument(f"--{prefix}-l0-spec", type=Path, required=True); p.add_argument(f"--{prefix}-l1-spec", type=Path, required=True)
        p.add_argument(f"--{prefix}-registry", type=Path, required=True); p.add_argument(f"--{prefix}-guard", type=Path, required=True)
    p.add_argument("--challenge-memo", type=Path, required=True); args = p.parse_args()
    a = check(args.task_table, args.example_l0_spec, args.example_l1_spec, args.example_registry, args.example_guard)
    b = check(args.task_table, args.challenge_l0_spec, args.challenge_l1_spec, args.challenge_registry, args.challenge_guard)
    if a == b: raise ValueError("挑战不得复制 A held-out plan")
    note = args.challenge_memo.read_text(encoding="utf-8").strip()
    required = ("L1", "held-out", "checkpoint", "threshold", "prompt", "report_only", "leakage")
    if len(note) < 170 or not all(word in note for word in required): raise ValueError("held-out memo 不完整")
    print("PASS: Day 19 changed L1 registry with zero frozen-field drift")


if __name__ == "__main__": main()
