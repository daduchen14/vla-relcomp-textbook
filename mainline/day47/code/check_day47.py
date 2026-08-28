#!/usr/bin/env python3
"""验收 A/B 配对 L0 retention 及 synthetic 边界。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
try:from .analyze_l0_retention import analyze
except ImportError:from analyze_l0_retention import analyze
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def check(source,config,table,report_path):
    rows,report=analyze(source,config);expected=[{key:str(value) for key,value in row.items()} for row in rows]
    if read(table)!=expected or json.loads(report_path.read_text(encoding="utf-8"))!=report:raise ValueError("retention evidence 不可重建")
    if not report["retention_pass"] or report["vla_arena_run"] or report["checkpoint_status"]!="NOT_RUN_SYNTHETIC_FIXTURE_ONLY":raise ValueError("retention/boundary 失败")
    return report
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("input","config","table","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_table,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_table,a.challenge_report)
    if left["paired_episode_ids"]==right["paired_episode_ids"]:raise ValueError("挑战必须换 episodes")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("L0 retention","paired episode","baseline success","repair success","retention rate","success-rate delta","catastrophic regression","recovery","minimum threshold","same initial state","synthetic fixture","checkpoint","VLA-Arena","cannot claim")
    if len(memo)<260 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 47 paired L0 retention evidence")
if __name__=="__main__":main()
