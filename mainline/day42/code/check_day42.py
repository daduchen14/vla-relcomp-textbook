#!/usr/bin/env python3
"""验收 A/B one-batch loss 轨迹、参数变化和证据边界。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
try:from .run_one_batch_overfit import analyze
except ImportError:from run_one_batch_overfit import analyze
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def check(source,config,trajectory,report):
    rows,expected=analyze(source,config);actual=json.loads(report.read_text(encoding="utf-8"))
    rebuilt=[{key:str(value) for key,value in row.items()} for row in rows]
    if read(trajectory)!=rebuilt or actual!=expected:raise ValueError("one-batch evidence 不可重建")
    if not expected["target_reached"] or expected["loss_reduction_factor"]<50 or not expected["adapter_changed"] or not expected["frozen_hashes_unchanged"] or expected["vla_model_run"] or expected["generalization_measured"]:raise ValueError("overfit/boundary 验收失败")
    return rows,expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("input","config","trajectory","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_trajectory,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_trajectory,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("one batch","overfit","initial loss","final loss","reduction factor","target loss","optimizer step","adapter changed","frozen hash","data pipeline","loss implementation","capacity","CPU toy","SmolVLA","generalization")
    if len(memo)<240 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 42 one-batch overfit smoke evidence")
if __name__=="__main__":main()
