#!/usr/bin/env python3
"""验收 A/B 平衡训练 pairs、完整性与挑战说明。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
try:from .build_training_pairs import analyze
except ImportError:from build_training_pairs import analyze
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def check(source,config,output,report):
    rows,expected=analyze(source,config)
    if read(output)!=rows or json.loads(report.read_text(encoding="utf-8"))!=expected:raise ValueError("training pairs 不可重建")
    groups={}
    for row in rows:groups.setdefault(row["pair_id"],[]).append(row)
    if any({row["arm"] for row in pair}!={"control","normalized"} or len({row["action_target_sha256"] for row in pair})!=1 for pair in groups.values()):raise ValueError("pair arm/label 不完整")
    return rows,expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("input","config","output","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_output,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_output,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("balanced sampling","relation coverage","contrast pair","control","normalized","same action target","pair label","sample weight","sampling seed","outcome-free","L0-only","incomplete pair","synthetic","training")
    if len(memo)<240 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 39 balanced normalized training pairs")
if __name__=="__main__":main()
