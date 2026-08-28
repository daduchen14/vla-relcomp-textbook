#!/usr/bin/env python3
"""验收 A/B L2 registry/guard、失败分类与行为边界说明。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from .build_l2_registry import derive
    from .classify_failures import classify
except ImportError:
    from build_l2_registry import derive
    from classify_failures import classify


def read(path):
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def norm(rows): return [{key: str(value) for key, value in row.items()} for row in rows]


def check(table, l0, l2, registry, guard, raw, labels, report):
    erows, eguard = derive(table, l0, l2); lrows, lreport = classify(raw)
    if read(registry) != norm(erows) or json.loads(guard.read_text()) != eguard: raise ValueError("L2 plan/guard 不可重建")
    if read(labels) != norm(lrows) or json.loads(report.read_text()) != lreport: raise ValueError("failure labels/report 不可重建")
    return erows, lrows


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--task-table", type=Path, required=True)
    for prefix in ("example", "challenge"):
        for name in ("l0-spec", "l2-spec", "registry", "guard", "raw", "labels", "report"):
            p.add_argument(f"--{prefix}-{name}", type=Path, required=True)
    p.add_argument("--challenge-memo", type=Path, required=True); args = p.parse_args()
    a = check(args.task_table, args.example_l0_spec, args.example_l2_spec, args.example_registry, args.example_guard,
              args.example_raw, args.example_labels, args.example_report)
    b = check(args.task_table, args.challenge_l0_spec, args.challenge_l2_spec, args.challenge_registry, args.challenge_guard,
              args.challenge_raw, args.challenge_labels, args.challenge_report)
    if a == b: raise ValueError("挑战不得复制 A L2/labels")
    note = args.challenge_memo.read_text(encoding="utf-8").strip()
    required = ("L2", "strong OOD", "first unmet", "ENV_INVALID", "probe gap", "behavioral", "causal")
    if len(note) < 180 or not all(word in note for word in required): raise ValueError("L2 failure memo 不完整")
    print("PASS: Day 20 changed L2 plan and behavioral failure taxonomy")


if __name__ == "__main__": main()
