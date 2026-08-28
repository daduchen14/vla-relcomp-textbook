#!/usr/bin/env python3
"""验收 A/B resource denominators、失败成本和 synthetic 边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .summarize_resources import analyze
except ImportError:from summarize_resources import analyze
def check(source,config,path):
    expected=analyze(source,config)
    if json.loads(path.read_text(encoding="utf-8"))!=expected:raise ValueError("resource report 不可重建")
    if not expected["failed_cost_included"] or expected["real_gpu_measurements"]:raise ValueError("resource boundary 失败")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--example-input",type=Path,required=True);p.add_argument("--example-config",type=Path,required=True);p.add_argument("--example-report",type=Path,required=True);p.add_argument("--challenge-input",type=Path,required=True);p.add_argument("--challenge-config",type=Path,required=True);p.add_argument("--challenge-report",type=Path,required=True);p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_report)
    if left["denominators"]==right["denominators"] and left["total_gpu_hours_including_failures"]==right["total_gpu_hours_including_failures"]:raise ValueError("挑战必须换 ledger")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("resource ledger","planned","attempted","completed","failed","not run","failure denominator","wall time","GPU-hours","peak memory","storage","failed cost","hourly rate","synthetic measurements","cannot claim")
    if len(memo)<270 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 59 resource tables include failed runs and honest denominators")
if __name__=="__main__":main()
