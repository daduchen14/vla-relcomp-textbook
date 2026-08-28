#!/usr/bin/env python3
"""验收 A/B relation normalizer 输出、模块边界和 memo。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
try:from .apply_relation_normalizer import analyze
except ImportError:from apply_relation_normalizer import analyze
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def check(source,output,report):
    rows,expected=analyze(source)
    if read(output)!=rows or json.loads(report.read_text(encoding="utf-8"))!=expected:raise ValueError("normalizer 产物不可重建")
    if expected["upstream_files_modified"] or expected["model_or_gpu_run"]:raise ValueError("module boundary 非法")
    return rows,expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("input","output","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_output,a.example_report);right=check(a.challenge_input,a.challenge_output,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("single repair module","L0","TARGET","START","ACTION","GOAL","canonical relation","pure function","input unchanged","unknown relation","regression test","upstream","synthetic","model run")
    if len(memo)<240 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 38 single relation-normalization module")
if __name__=="__main__":main()
