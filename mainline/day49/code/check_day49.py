#!/usr/bin/env python3
"""验收 A/B 单变量、成本匹配和多 seed 消融报告。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .analyze_cost_matched_ablation import analyze
except ImportError:from analyze_cost_matched_ablation import analyze
def check(source,config,report_path):
    expected=analyze(source,config)
    if json.loads(report_path.read_text(encoding="utf-8"))!=expected:raise ValueError("ablation report 不可重建")
    if not expected["single_variable"] or not expected["all_cost_matched"] or not expected["all_seeds_reported"] or expected["best_seed_selection"] or expected["formal_runs_available"]:raise ValueError("ablation/fairness boundary 失败")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("input","config","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_report)
    if left["paired_rows"]==right["paired_rows"]:raise ValueError("挑战必须换 ledger")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("minimal ablation","single variable","relation normalization","repair","ablation","baseline","same split","same steps","cost matched","GPU-hours","relative cost gap","component effect","all seeds","cherry-picking","synthetic ledger")
    if len(memo)<260 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 49 cost-matched single-variable ablations")
if __name__=="__main__":main()
