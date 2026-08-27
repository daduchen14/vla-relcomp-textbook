#!/usr/bin/env python3
"""验收 A/B protocol lock 重算与冻结边界解释。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try: from .freeze_protocol import build
except ImportError: from freeze_protocol import build


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--upstream", type=Path, required=True); p.add_argument("--example-spec", type=Path, required=True)
    p.add_argument("--example-lock", type=Path, required=True); p.add_argument("--challenge-spec", type=Path, required=True)
    p.add_argument("--challenge-lock", type=Path, required=True); p.add_argument("--challenge-memo", type=Path, required=True)
    args = p.parse_args(); expected_a = build(args.repo, args.upstream, args.example_spec)
    expected_b = build(args.repo, args.upstream, args.challenge_spec)
    if json.loads(args.example_lock.read_text()) != expected_a or json.loads(args.challenge_lock.read_text()) != expected_b:
        raise ValueError("A/B lock 必须从当前 commit、锁定 upstream、spec 和文件内容重建")
    if expected_a["lock_sha256"] == expected_b["lock_sha256"]: raise ValueError("挑战不得复制 A lock")
    note = args.challenge_memo.read_text(encoding="utf-8").strip()
    required = ("commit", "revision", "sha256", "seed", "init_state", "L1/L2", "formal")
    if len(note) < 160 or not all(word in note for word in required): raise ValueError("冻结 memo 不完整")
    print("PASS: Day 15 changed lock and reproducibility boundary memo")


if __name__ == "__main__": main()
