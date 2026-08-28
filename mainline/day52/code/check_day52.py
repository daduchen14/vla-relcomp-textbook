#!/usr/bin/env python3
"""验收 A/B clean-room allowlist、污染拒绝和 NOT_RUN 边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .build_clean_baseline_packet import analyze
except ImportError:from build_clean_baseline_packet import analyze
def check(inventory,config,packet_path):
    expected=analyze(inventory,config)
    if json.loads(packet_path.read_text(encoding="utf-8"))!=expected:raise ValueError("clean-room packet 不可重建")
    if expected["repair_artifacts_accepted"] or expected["old_results_accepted"] or expected["command_run"] or expected["vla_arena_run"] or expected["baseline_records"] is not None:raise ValueError("contamination/run boundary 失败")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--example-inventory",type=Path,required=True);p.add_argument("--example-config",type=Path,required=True);p.add_argument("--example-packet",type=Path,required=True);p.add_argument("--challenge-inventory",type=Path,required=True);p.add_argument("--challenge-config",type=Path,required=True);p.add_argument("--challenge-packet",type=Path,required=True);p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_inventory,a.example_config,a.example_packet);right=check(a.challenge_inventory,a.challenge_config,a.challenge_packet)
    if left["cleanroom_id"]==right["cleanroom_id"]:raise ValueError("挑战必须换 inventory/config")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("clean-room","baseline","allowlist","locked upstream","base model","raw dataset","repair checkpoint","old eval result","cache contamination","read-only","empty eval cache","unique output","artifact hash","NOT_RUN","cannot claim")
    if len(memo)<270 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 52 clean baseline packets reject contaminating artifacts")
if __name__=="__main__":main()
