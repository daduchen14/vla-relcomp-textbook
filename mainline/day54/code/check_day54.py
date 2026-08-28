#!/usr/bin/env python3
"""验收 A/B pair 完整性、missing policy 与 synthetic 边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .analyze_final_pairs import analyze
except ImportError:from analyze_final_pairs import analyze
def check(source,config,report_path):
    expected=analyze(source,config)
    if json.loads(report_path.read_text(encoding="utf-8"))!=expected:raise ValueError("pair report 不可重建")
    if not expected["integrity_pass"] or expected["missing_records"] or expected["duplicate_count"] or expected["vla_arena_run"] or expected["final_pair_data_available"]:raise ValueError("pair/evidence boundary 失败")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--example-input",type=Path,required=True);p.add_argument("--example-config",type=Path,required=True);p.add_argument("--example-report",type=Path,required=True);p.add_argument("--challenge-input",type=Path,required=True);p.add_argument("--challenge-config",type=Path,required=True);p.add_argument("--challenge-report",type=Path,required=True);p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_report)
    if left["pair_rows"]==right["pair_rows"]:raise ValueError("挑战必须换 pairs")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("counterfactual pair","control arm","counterfactual arm","baseline","repair","pair integrity","join key","missing record","duplicate","fail closed","paired success","outcome flip","same initial state","synthetic records","cannot claim")
    if len(memo)<270 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 54 final-pair rehearsals are complete and fail closed")
if __name__=="__main__":main()
