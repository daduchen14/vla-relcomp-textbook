#!/usr/bin/env python3
"""验收 A/B repair decision、唯一选择和边界说明。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
try:from .make_repair_decision import analyze
except ImportError:from make_repair_decision import analyze
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def check(spec,config,output,report):
    rows,expected=analyze(spec,config);rebuilt=[{key:str(value) for key,value in row.items()} for row in rows]
    if read(output)!=rebuilt or json.loads(report.read_text(encoding="utf-8"))!=expected:raise ValueError("repair decision 不可重建")
    if sum(row["selected"]=="true" for row in rows)!=1 or any(row["authorized_for_training"]!="false" for row in rows):raise ValueError("选择/授权边界非法")
    return rows,expected
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--config",type=Path,required=True)
    for prefix in ("example","challenge"):
        for name in ("spec","output","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_spec,a.config,a.example_output,a.example_report);right=check(a.challenge_spec,a.config,a.challenge_output,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("decision matrix","evidence gate","unique repair","STOP_NO_REPAIR","benefit","implementation cost","leakage risk","L0 damage","falsifiability","negative result","authorized_for_training","synthetic","causal")
    if len(memo)<240 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 36 single-repair-or-stop decision")
if __name__=="__main__":main()
