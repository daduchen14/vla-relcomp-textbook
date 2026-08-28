#!/usr/bin/env python3
"""验收 A/B final manifest 的矩阵、停止规则、hash 与未授权边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .freeze_final_manifest import analyze
except ImportError:from freeze_final_manifest import analyze
def check(config,path):
    expected=analyze(config)
    if json.loads(path.read_text(encoding="utf-8"))!=expected:raise ValueError("final manifest 不可重建")
    if expected["authorized_for_gpu"] or expected["runs_started"] or expected["formal_results_available"] or expected["status"]!="FROZEN_PLAN_NOT_AUTHORIZED":raise ValueError("authorization boundary 失败")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--example-config",type=Path,required=True);p.add_argument("--example-manifest",type=Path,required=True);p.add_argument("--challenge-config",type=Path,required=True);p.add_argument("--challenge-manifest",type=Path,required=True);p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_config,a.example_manifest);right=check(a.challenge_config,a.challenge_manifest)
    if left["manifest_sha256"]==right["manifest_sha256"]:raise ValueError("挑战必须换矩阵输入")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("final manifest","preregistration","matrix","baseline","repair","ablation","seed","L0/L1/L2","stop rule","budget exhaustion","failed run","negative result","canonical hash","frozen","not authorized")
    if len(memo)<270 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 51 final manifests are frozen and not authorized")
if __name__=="__main__":main()
