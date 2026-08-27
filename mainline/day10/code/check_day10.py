#!/usr/bin/env python3
"""验收锁定 success contract、A/B predicate fixture 和边界解释。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .build_success_contract import build, markdown
    from .evaluate_predicate_fixture import evaluate
except ImportError:
    from build_success_contract import build, markdown
    from evaluate_predicate_fixture import evaluate


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--task-table", type=Path, required=True); p.add_argument("--contract-json", type=Path, required=True)
    p.add_argument("--chain-md", type=Path, required=True); p.add_argument("--example-input", type=Path, required=True)
    p.add_argument("--example-output", type=Path, required=True); p.add_argument("--challenge-input", type=Path, required=True)
    p.add_argument("--challenge-output", type=Path, required=True); p.add_argument("--challenge-reflection", type=Path, required=True)
    args = p.parse_args(); contract = build(args.upstream.resolve(), args.task_table)
    if json.loads(args.contract_json.read_text()) != contract or args.chain_md.read_text() != markdown(contract):
        raise ValueError("success 契约/调用链必须由锁定源码和 Day 9 表重建")
    expected_a, expected_b = evaluate(args.example_input), evaluate(args.challenge_input)
    if json.loads(args.example_output.read_text()) != expected_a: raise ValueError("A predicate 输出与输入不一致")
    if json.loads(args.challenge_output.read_text()) != expected_b or expected_a == expected_b:
        raise ValueError("挑战必须重新计算 B 的严格阈值、timeout 和 success")
    note = args.challenge_reflection.read_text(encoding="utf-8")
    if len(note.strip()) < 100 or not all(word in note for word in ("0.07", "<", "done", "success", "timeout")):
        raise ValueError("挑战反思须≥100字并解释严格阈值与 done/success/timeout")
    print("PASS: Day 10 locked success path and changed predicate challenge")


if __name__ == "__main__": main()
