#!/usr/bin/env python3
"""验收从空目录生成的 A/B mini baseline package 与 Gate 4 memo。"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

try: from .reproduce_mini_baseline import ARTIFACTS, reproduce
except ImportError: from reproduce_mini_baseline import ARTIFACTS, reproduce

FILES = ARTIFACTS + ("reproduction_receipt.json",)


def check(spec: Path, submitted: Path):
    if {path.name for path in submitted.iterdir()} != set(FILES): raise ValueError("package 文件集合不精确")
    with tempfile.TemporaryDirectory() as tmp:
        expected_dir = Path(tmp) / "package"; expected_receipt = reproduce(spec, expected_dir)
        for name in FILES:
            if (submitted / name).read_bytes() != (expected_dir / name).read_bytes(): raise ValueError(f"package artifact 不可重建：{name}")
    return expected_receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for prefix in ("example", "challenge"):
        parser.add_argument(f"--{prefix}-spec", type=Path, required=True); parser.add_argument(f"--{prefix}-dir", type=Path, required=True)
    parser.add_argument("--challenge-memo", type=Path, required=True); args = parser.parse_args()
    a = check(args.example_spec, args.example_dir); b = check(args.challenge_spec, args.challenge_dir)
    if a == b: raise ValueError("挑战不得复制 A package")
    memo = args.challenge_memo.read_text(encoding="utf-8").strip()
    required = ("empty", "manifest", "protocol lock", "registry", "task_stats", "SHA-256", "synthetic adapter", "Gate 4", "GPU", "claim")
    if len(memo) < 220 or not all(token in memo for token in required): raise ValueError("Gate 4 memo 不完整")
    print("PASS: Day 25 clean-room mini baseline reproduction and Gate 4 evidence")


if __name__ == "__main__": main()
