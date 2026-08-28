#!/usr/bin/env python3
"""验收 A/B bounded config、显存余量、checkpoint 与 memo。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .validate_bounded_train_config import analyze
except ImportError:from validate_bounded_train_config import analyze
def check(config,report):
    expected=analyze(config);actual=json.loads(report.read_text(encoding="utf-8"))
    if actual!=expected:raise ValueError("bounded train report 不可重建")
    if expected["lora_enabled"] or expected["planning_headroom_fraction"]<0.20 or expected["authorized_for_training"] or expected["command_run"]:raise ValueError("method/memory/authorization boundary 非法")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        p.add_argument(f"--{prefix}-config",type=Path,required=True);p.add_argument(f"--{prefix}-report",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_config,a.example_report);right=check(a.challenge_config,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("adapter-only","LoRA","single repair","micro batch","gradient accumulation","global batch","mixed precision","memory estimate","headroom","checkpoint","resume","max steps","authorized","CUDA","not profiled")
    if len(memo)<240 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 41 bounded lightweight-train config")
if __name__=="__main__":main()
