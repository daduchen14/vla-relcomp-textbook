#!/usr/bin/env python3
"""验收 A/B deterministic casebook、coverage 和未观看边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .build_casebook import analyze
except ImportError:from build_casebook import analyze
def check(source,config,path):
    expected=analyze(source,config)
    if json.loads(path.read_text(encoding="utf-8"))!=expected:raise ValueError("casebook 不可重建")
    if expected["manual_override"] or expected["outcome_based_manual_selection"] or not expected["all_strata_covered"] or expected["videos_viewed"] or expected["final_casebook_available"]:raise ValueError("selection/evidence boundary 失败")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--example-input",type=Path,required=True);p.add_argument("--example-config",type=Path,required=True);p.add_argument("--example-casebook",type=Path,required=True);p.add_argument("--challenge-input",type=Path,required=True);p.add_argument("--challenge-config",type=Path,required=True);p.add_argument("--challenge-casebook",type=Path,required=True);p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_casebook);right=check(a.challenge_input,a.challenge_config,a.challenge_casebook)
    if left["selected_cases"]==right["selected_cases"]:raise ValueError("挑战必须换 inventory/config")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("casebook","representative case","stratum quota","stable success","recovery","damage","stable failure","salted hash","deterministic selection","manual override","cherry-picking","video path","episode hash","not viewed","cannot claim")
    if len(memo)<270 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 58 casebooks avoid manual outcome cherry-picking")
if __name__=="__main__":main()
