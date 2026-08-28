#!/usr/bin/env python3
"""验收 repeat manifest、公平性、预算和 NOT_RUN 边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .prepare_repeat_launches import analyze
except ImportError:from prepare_repeat_launches import analyze
def check(split,base,repeat,stability,candidate,manifest_path):
    expected=analyze(split,base,repeat,stability,candidate);actual=json.loads(manifest_path.read_text(encoding="utf-8"))
    if actual!=expected:raise ValueError("repeat manifest 不可重建")
    if not expected["same_split_for_all"] or not expected["same_recipe_for_all"] or expected["variance_policy"]["best_seed_selection"] or expected["variance_policy"]["metrics"] is not None or expected["authorized_for_gpu"] or expected["commands_run"] or expected["formal_checkpoints_produced"]:raise ValueError("repeat/variance boundary 失败")
    if any(row["checkpoint_sha256"] is not None for row in expected["checkpoint_contracts"]):raise ValueError("伪造 checkpoint")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("split","base","repeat","stability","candidate","manifest"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_split,a.example_base,a.example_repeat,a.example_stability,a.example_candidate,a.example_manifest);right=check(a.challenge_split,a.challenge_base,a.challenge_repeat,a.challenge_stability,a.challenge_candidate,a.challenge_manifest)
    if left["runs"][0]["recipe_sha256"]==right["runs"][0]["recipe_sha256"]:raise ValueError("挑战必须换 recipe/split 组合")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("seed 2","seed 3","repeat","same recipe","same split","allowed differences","variance","mean","sample standard deviation","per-seed","cherry-picking","resource cap","checkpoint 2","checkpoint 3","NOT_RUN")
    if len(memo)<260 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 46 repeats are fair, bounded, and honestly NOT_RUN")
if __name__=="__main__":main()
