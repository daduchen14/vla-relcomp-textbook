#!/usr/bin/env python3
"""验收 A/B Gate 6 从原始输入重建且未伪造通过。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .run_gate6 import analyze,parser
except ImportError:from run_gate6 import analyze,parser
def main():
    p=argparse.ArgumentParser(description=__doc__)
    names=("split","base-plan","repeat-plan","stability","candidate","l0-input","l0-config","ood-input","ood-config","ablation-input","ablation-config","report")
    for prefix in ("example","challenge"):
        for name in names:p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();reports=[]
    for prefix in ("example","challenge"):
        values={name.replace("-","_"):getattr(a,f"{prefix}_{name.replace('-','_')}") for name in names};report_path=values.pop("report");expected=analyze(argparse.Namespace(**values));actual=json.loads(report_path.read_text(encoding="utf-8"))
        if actual!=expected or expected["outcome"]!="停止扩张" or expected["gate6_passed"] or expected["learner_gate_status"]!="REHEARSAL_ONLY_NOT_PASSED":raise ValueError("Gate 6 rebuild/status 失败")
        reports.append(expected)
    if reports[0]["source_sha256"]==reports[1]["source_sha256"]:raise ValueError("挑战必须换原始输入")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("Gate 6","raw inputs","rebuild","L0 retention","L1/L2","multi-seed","ablation","cost matched","formal evidence","synthetic","通过","补做","停止扩张","learner status","next action")
    if len(memo)<280 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 50 Gate 6 rehearsals stop expansion without formal evidence")
if __name__=="__main__":main()
