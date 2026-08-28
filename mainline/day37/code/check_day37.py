#!/usr/bin/env python3
"""验收 A/B L0-only manifest、血缘和泄漏说明。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
try:from .build_l0_dataset import analyze
except ImportError:from build_l0_dataset import analyze
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def check(registry,output,report):
    rows,expected=analyze(registry)
    if read(output)!=rows or json.loads(report.read_text(encoding="utf-8"))!=expected:raise ValueError("L0 dataset 产物不可重建")
    if any(row["level"]!="0" for row in rows) or expected["l1_l2_in_output"]!=0:raise ValueError("L1/L2 泄漏")
    return rows,expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("registry","output","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_registry,a.example_output,a.example_report);right=check(a.challenge_registry,a.challenge_output,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("L0-only","L1/L2","heldout_test","data lineage","source_bddl_sha256","source_episode_sha256","dataset_row_sha256","split group","duplicate content","leakage","validation","synthetic","training")
    if len(memo)<240 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 37 strict L0-only dataset manifest")
if __name__=="__main__":main()
