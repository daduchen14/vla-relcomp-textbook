#!/usr/bin/env python3
"""验收 A/B target probe、阈值敏感性和对象选择边界。"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
try: from .analyze_target_probe import analyze
except ImportError: from analyze_target_probe import analyze
def read(path):
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))
def norm(rows): return [{key:str(value) for key,value in row.items()} for row in rows]
def check(trace,config,summary,sensitivity,report):
    a,b,c=analyze(trace,config)
    if read(summary)!=norm(a) or read(sensitivity)!=norm(b) or json.loads(report.read_text(encoding="utf-8"))!=c: raise ValueError("target probe 产物不可重建")
    return a,b,c
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("trace","config","summary","sensitivity","report"): p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True); a=p.parse_args()
    left=check(a.example_trace,a.example_config,a.example_summary,a.example_sensitivity,a.example_report); right=check(a.challenge_trace,a.challenge_config,a.challenge_summary,a.challenge_sensitivity,a.challenge_report)
    if left==right: raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip(); required=("target_object_id","distance","threshold","sustained","contact geom","wrong object","sensitivity","near","contact","causal","synthetic")
    if len(memo)<220 or not all(token in memo for token in required): raise ValueError("challenge memo 不完整")
    print("PASS: Day 27 target near/contact detector and threshold sensitivity")
if __name__=="__main__": main()
