#!/usr/bin/env python3
"""验收 A/B lift probe、敏感性 CSV/SVG 与证据 memo。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
try: from .analyze_lift_probe import analyze
except ImportError: from analyze_lift_probe import analyze
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def norm(rows):return [{key:str(value) for key,value in row.items()} for row in rows]
def check(trace,config,summary,sensitivity,plot,report):
    a,b,c,d=analyze(trace,config)
    if read(summary)!=norm(a) or read(sensitivity)!=norm(b) or plot.read_text(encoding="utf-8")!=d or json.loads(report.read_text(encoding="utf-8"))!=c:raise ValueError("lift 产物不可重建")
    return a,b,c
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("trace","config","summary","sensitivity","plot","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_trace,a.example_config,a.example_summary,a.example_sensitivity,a.example_plot,a.example_report);right=check(a.challenge_trace,a.challenge_config,a.challenge_summary,a.challenge_sensitivity,a.challenge_plot,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("bilateral contact","support surface","baseline z","height gain","threshold","sustained","sensitivity","lift","probe gap","causal","synthetic")
    if len(memo)<220 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 28 grasp/lift detector and sensitivity plot")
if __name__=="__main__":main()
