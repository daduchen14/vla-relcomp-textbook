#!/usr/bin/env python3
"""验收 A/B registry 重建、schema/report 与缺失值说明。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .build_registry import build
    from .validate_registry import read, validate
except ImportError:
    from build_registry import build
    from validate_registry import read, validate


def normalized(rows): return [{key: str(value) for key, value in row.items()} for row in rows]


def check_one(spec, runs, episodes, schema_path, report):
    expected_runs, expected_episodes, expected_schema = build(spec)
    if read(runs) != normalized(expected_runs) or read(episodes) != normalized(expected_episodes):
        raise ValueError("registry 必须从对应 spec 重建")
    if json.loads(schema_path.read_text()) != expected_schema: raise ValueError("schema 不一致")
    expected_report = validate(runs, episodes, schema_path)
    if json.loads(report.read_text()) != expected_report: raise ValueError("validation report 不一致")
    return expected_runs, expected_episodes


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for prefix in ("example", "challenge"):
        p.add_argument(f"--{prefix}-spec", type=Path, required=True); p.add_argument(f"--{prefix}-runs", type=Path, required=True)
        p.add_argument(f"--{prefix}-episodes", type=Path, required=True); p.add_argument(f"--{prefix}-schema", type=Path, required=True)
        p.add_argument(f"--{prefix}-report", type=Path, required=True)
    p.add_argument("--challenge-memo", type=Path, required=True); args = p.parse_args()
    a = check_one(args.example_spec, args.example_runs, args.example_episodes, args.example_schema, args.example_report)
    b = check_one(args.challenge_spec, args.challenge_runs, args.challenge_episodes, args.challenge_schema, args.challenge_report)
    if a == b: raise ValueError("挑战不得复制 A registry")
    note = args.challenge_memo.read_text(encoding="utf-8").strip()
    required = ("primary key", "foreign key", "PLANNED", "missing", "success=0", "evidence")
    if len(note) < 150 or not all(word in note for word in required): raise ValueError("registry memo 不完整")
    print("PASS: Day 16 changed registry, schema, missing values and evidence naming")


if __name__ == "__main__": main()
