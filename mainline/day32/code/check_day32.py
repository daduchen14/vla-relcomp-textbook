#!/usr/bin/env python3
"""验收 A/B object-combination pair set、覆盖与 defense。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
try:from .build_object_pair_set import build,OUTPUT
except ImportError:from build_object_pair_set import build,OUTPUT
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def check(spec,output,report):
    rows,expected=build(spec)
    if read(output)!=rows or json.loads(report.read_text(encoding="utf-8"))!=expected:raise ValueError("object pair set 不可重建")
    for left,right in zip(rows[::2],rows[1::2]):
        changed={key for key in OUTPUT if left[key]!=right[key]}
        allowed={"arm","target_object_id","reference_object_id","object_combination","instruction_text","init_state_id"}
        if changed-allowed or not {"arm","object_combination","instruction_text","init_state_id"}.issubset(changed):raise ValueError("两臂变化字段越界")
    return rows,expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("spec","output","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-defense",type=Path,required=True);a=p.parse_args();left=check(a.example_spec,a.example_output,a.example_report);right=check(a.challenge_spec,a.challenge_output,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    memo=a.challenge_defense.read_text(encoding="utf-8").strip();required=("object combination","target","reference","relation fixed","object multiset","matching stratum","visibility","reachability","coverage","confound","planned","synthetic","causal")
    if len(memo)<240 or not all(token in memo for token in required):raise ValueError("challenge defense 不完整")
    print("PASS: Day 32 object-combination matching plan")
if __name__=="__main__":main()
