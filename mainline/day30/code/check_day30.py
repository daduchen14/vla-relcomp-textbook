#!/usr/bin/env python3
"""验收 A/B relation detector、信号冲突与挑战 memo。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
try:from .analyze_relation_probe import analyze
except ImportError:from analyze_relation_probe import analyze
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def check(trace,config,output,report):
    rows,expected=analyze(trace,config)
    rebuilt=[{key:str(value) for key,value in row.items()} for row in rows]
    if read(output)!=rebuilt or json.loads(report.read_text(encoding="utf-8"))!=expected:raise ValueError("relation 产物不可重建")
    return rows,expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("trace","config","output","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_trace,a.example_config,a.example_output,a.example_report);right=check(a.challenge_trace,a.challenge_config,a.challenge_output,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("official predicate","On","In","target","reference","sustained","gripper release","geometric proxy","signal conflict","terminal relation","causal","synthetic")
    if len(memo)<220 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 30 stable terminal-relation detector")
if __name__=="__main__":main()
