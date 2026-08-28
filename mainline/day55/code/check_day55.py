#!/usr/bin/env python3
"""验收 A/B oracle 分栏、完整性和 synthetic 边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .analyze_final_oracles import analyze
except ImportError:from analyze_final_oracles import analyze
def check(source,config,report_path):
    expected=analyze(source,config)
    if json.loads(report_path.read_text(encoding="utf-8"))!=expected:raise ValueError("oracle report 不可重建")
    if not expected["records_complete"] or expected["oracle_in_primary_result"] or expected["oracle_deployable"] or expected["vla_arena_run"] or expected["final_oracle_data_available"]:raise ValueError("oracle/evidence boundary 失败")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--example-input",type=Path,required=True);p.add_argument("--example-config",type=Path,required=True);p.add_argument("--example-report",type=Path,required=True);p.add_argument("--challenge-input",type=Path,required=True);p.add_argument("--challenge-config",type=Path,required=True);p.add_argument("--challenge-report",type=Path,required=True);p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_report)
    if left["diagnostic_oracles"]==right["diagnostic_oracles"]:raise ValueError("挑战必须换 oracle records")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("oracle","diagnostic only","deployable method","baseline","repair","language oracle","visual oracle","privileged information","recovery","damage","headroom","primary result","separate column","synthetic records","cannot claim")
    if len(memo)<270 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 55 oracles remain diagnostic and non-deployable")
if __name__=="__main__":main()
