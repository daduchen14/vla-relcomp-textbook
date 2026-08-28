#!/usr/bin/env python3
"""验收 A/B 结果锁、随机三条映射和证据边界。"""
from __future__ import annotations
import argparse, json
from pathlib import Path
try:
    from .build_results_lock import analyze
except ImportError:
    from build_results_lock import analyze

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        parser.add_argument(f"--{prefix}-input",type=Path,required=True);parser.add_argument(f"--{prefix}-config",type=Path,required=True);parser.add_argument(f"--{prefix}-report",type=Path,required=True)
    parser.add_argument("--challenge-memo",type=Path,required=True);args=parser.parse_args();reports=[]
    for prefix in ("example","challenge"):
        expected=analyze(getattr(args,f"{prefix}_input"),getattr(args,f"{prefix}_config"));actual=json.loads(getattr(args,f"{prefix}_report").read_text(encoding="utf-8"))
        if actual!=expected or expected["outcome"]!="停止扩张" or expected["gate7_passed"] or expected["learner_gate_status"]!="REHEARSAL_ONLY_NOT_PASSED":
            raise ValueError("Gate 7 results lock/status 失败")
        if len(expected["selected_claims"])!=3 or not expected["criteria"]["claim_evidence_links_complete"]:
            raise ValueError("三条 claim-evidence 映射不完整")
        reports.append(expected)
    if reports[0]["source_sha256"]==reports[1]["source_sha256"]:
        raise ValueError("挑战必须使用新输入")
    memo=args.challenge_memo.read_text(encoding="utf-8").strip();required=("Gate 7","random sample","claim","table","raw episode","version","allowed claim","stronger claim","negative result","formal evidence","synthetic","停止扩张","learner status","results lock","cannot claim")
    if len(memo)<280 or not all(token in memo for token in required):
        raise ValueError("challenge memo 不完整")
    print("PASS: Day 60 results lock preserves traceability and refuses unsupported claims")

if __name__ == "__main__":
    main()
