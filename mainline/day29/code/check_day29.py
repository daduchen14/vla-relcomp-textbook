#!/usr/bin/env python3
"""验收 A/B approach detector、错误参照物与 memo。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
try:from .analyze_approach_probe import analyze
except ImportError:from analyze_approach_probe import analyze
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def check(trace,config,output,report):
    rows,expected=analyze(trace,config)
    if read(output)!=[{k:str(v) for k,v in row.items()} for row in rows] or json.loads(report.read_text(encoding="utf-8"))!=expected:raise ValueError("approach 产物不可重建")
    return rows,expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("trace","config","output","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_trace,a.example_config,a.example_output,a.example_report);right=check(a.challenge_trace,a.challenge_config,a.challenge_output,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("lifted segment","reference_object_id","distance trajectory","net progress","entry threshold","sustained","wrong reference","decrease fraction","approach","causal","synthetic")
    if len(memo)<220 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 29 reference-approach trajectory detector")
if __name__=="__main__":main()
