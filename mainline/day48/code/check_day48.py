#!/usr/bin/env python3
"""验收 A/B 预注册分层 OOD 报告和证据边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .analyze_ood_results import analyze
except ImportError:from analyze_ood_results import analyze
def check(source,config,report_path):
    expected=analyze(source,config)
    if json.loads(report_path.read_text(encoding="utf-8"))!=expected:raise ValueError("OOD report 不可重建")
    if not expected["all_levels_pass"] or expected["pooling_for_primary_conclusion"] or expected["best_level_selection"] or expected["vla_arena_run"] or expected["checkpoint_status"]!="NOT_RUN":raise ValueError("OOD/preregistration boundary 失败")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("input","config","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_report)
    if left["analysis_config_sha256"]==right["analysis_config_sha256"]:raise ValueError("挑战必须换预注册 config")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("held-out OOD","preregistered","L1","L2","paired success-rate delta","baseline rate","repair rate","failure-to-success","success-to-failure","minimum delta","stratified","pooling","best-level selection","synthetic fixture","cannot claim")
    if len(memo)<260 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 48 preregistered stratified OOD reports")
if __name__=="__main__":main()
