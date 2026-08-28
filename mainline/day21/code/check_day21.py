#!/usr/bin/env python3
"""验收 A/B 配对重跑 manifest、reproducibility 表与证据说明。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from .analyze_reproducibility import analyze
    from .build_rerun_manifest import build
except ImportError:
    from analyze_reproducibility import analyze
    from build_rerun_manifest import build


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalized(rows: list[dict]) -> list[dict[str, str]]:
    return [{key: str(value) for key, value in row.items()} for row in rows]


def check(registry: Path, selection: Path, manifest: Path, raw: Path, details: Path, report: Path):
    expected_manifest = build(registry, selection)
    expected_details, expected_report = analyze(raw)
    if read_csv(manifest) != normalized(expected_manifest):
        raise ValueError("rerun manifest 不可由 registry/selection 精确重建")
    if read_csv(details) != normalized(expected_details) or json.loads(report.read_text(encoding="utf-8")) != expected_report:
        raise ValueError("reproducibility 表不可由配对结果精确重建")
    return expected_manifest, expected_details


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for prefix in ("example", "challenge"):
        for name in ("registry", "selection", "manifest", "raw", "details", "report"):
            parser.add_argument(f"--{prefix}-{name}", type=Path, required=True)
    parser.add_argument("--challenge-memo", type=Path, required=True)
    args = parser.parse_args()
    example = check(args.example_registry, args.example_selection, args.example_manifest,
                    args.example_raw, args.example_details, args.example_report)
    challenge = check(args.challenge_registry, args.challenge_selection, args.challenge_manifest,
                      args.challenge_raw, args.challenge_details, args.challenge_report)
    if example == challenge:
        raise ValueError("挑战不得复制 A 的选择或配对结果")
    memo = args.challenge_memo.read_text(encoding="utf-8").strip()
    required = ("repeat", "seed", "init_state", "success", "stage", "mismatch", "reproducibility")
    if len(memo) < 170 or not all(token in memo for token in required):
        raise ValueError("challenge memo 不完整")
    print("PASS: Day 21 paired rerun plan and reproducibility table")


if __name__ == "__main__":
    main()
