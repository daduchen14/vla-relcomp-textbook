#!/usr/bin/env python3
"""验收 A/B seed-1 packet、test isolation 和未运行边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .prepare_seed1_launch import analyze
except ImportError:from prepare_seed1_launch import analyze
def check(split,plan,stability,candidate,packet_path,contract_path):
    packet,contract=analyze(split,plan,stability,candidate)
    if json.loads(packet_path.read_text(encoding="utf-8"))!=packet or json.loads(contract_path.read_text(encoding="utf-8"))!=contract:raise ValueError("launch evidence 不可重建")
    if not packet["test_isolated"] or packet["test_access_log"] or packet["authorized_for_gpu"] or packet["command_run"] or contract["checkpoint_sha256"] is not None or contract["formal_training_evidence"]:raise ValueError("isolation/NOT_RUN boundary 失败")
    return packet
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("split","plan","stability","candidate","packet","contract"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_split,a.example_plan,a.example_stability,a.example_candidate,a.example_packet,a.example_contract);right=check(a.challenge_split,a.challenge_plan,a.challenge_stability,a.challenge_candidate,a.challenge_packet,a.challenge_contract)
    if left["split_sha256"]==right["split_sha256"] or left["run_id"]==right["run_id"]:raise ValueError("挑战必须换 split/run id")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("seed 1","formal run","train split","validation split","held-out test","test isolation","resource budget","resource measurement","launch packet","checkpoint contract","NOT_RUN","authorization","recipe hash","split hash","GPU")
    if len(memo)<260 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 45 seed-1 launch packets preserve held-out tests")
if __name__=="__main__":main()
