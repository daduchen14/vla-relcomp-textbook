#!/usr/bin/env python3
"""验收 A/B Wilson、恢复/损伤与 exact McNemar 结果。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .compute_paired_statistics import analyze
except ImportError:from compute_paired_statistics import analyze
def check(source,config,report_path):
    expected=analyze(source,config)
    if json.loads(report_path.read_text(encoding="utf-8"))!=expected:raise ValueError("statistics report 不可重建")
    if not expected["effect_interval_significance_separated"] or expected["formal_statistics_available"]:raise ValueError("statistics boundary 失败")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--example-input",type=Path,required=True);p.add_argument("--example-config",type=Path,required=True);p.add_argument("--example-report",type=Path,required=True);p.add_argument("--challenge-input",type=Path,required=True);p.add_argument("--challenge-config",type=Path,required=True);p.add_argument("--challenge-report",type=Path,required=True);p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_report)
    if left["counts"]==right["counts"]:raise ValueError("挑战必须换 counts")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("Wilson interval","paired table","n01 recovery","n10 damage","baseline failures","baseline successes","effect size","confidence interval","exact McNemar","discordant pairs","two-sided p-value","alpha","not significant","not no effect","synthetic counts")
    if len(memo)<280 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 57 paired statistics separate effects, intervals, and tests")
if __name__=="__main__":main()
