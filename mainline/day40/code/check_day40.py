#!/usr/bin/env python3
"""验收 A/B loss、参数组、梯度边界与 memo。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .build_trainability_report import analyze
except ImportError:from build_trainability_report import analyze
def check(source,config,report):
    expected=analyze(source,config);actual=json.loads(report.read_text(encoding="utf-8"))
    if actual!=expected:raise ValueError("trainability report 不可重建")
    if expected["trainable_parameter_names"]!=["relation_adapter.weight"] or expected["frozen_grad_count"]!=0 or expected["optimizer_step_run"]:raise ValueError("trainability boundary 非法")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("input","config","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("action loss","pair consistency","loss weight","relation_adapter","backbone","action_head","requires_grad","parameter group","gradient","frozen","optimizer step","CPU toy","SmolVLA","training evidence")
    if len(memo)<240 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 40 loss and trainability boundary")
if __name__=="__main__":main()
