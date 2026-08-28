#!/usr/bin/env python3
"""验收 A/B 四段漏斗、条件分母与 synthetic 边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .analyze_stage_funnel import analyze
except ImportError:from analyze_stage_funnel import analyze
def check(source,config,report_path):
    expected=analyze(source,config)
    if json.loads(report_path.read_text(encoding="utf-8"))!=expected:raise ValueError("funnel report 不可重建")
    if not expected["monotonicity_pass"] or not expected["episode_keys_unique"] or expected["vla_arena_run"] or expected["stage_metrics_final"]:raise ValueError("funnel/evidence boundary 失败")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--example-input",type=Path,required=True);p.add_argument("--example-config",type=Path,required=True);p.add_argument("--example-report",type=Path,required=True);p.add_argument("--challenge-input",type=Path,required=True);p.add_argument("--challenge-config",type=Path,required=True);p.add_argument("--challenge-report",type=Path,required=True);p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_report)
    if left["conditions"]==right["conditions"]:raise ValueError("挑战必须换 episodes")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("four-stage funnel","target contacted","target lifted","reference approached","relation satisfied","reach rate","conversion rate","previous-stage denominator","drop-off","monotonicity","baseline","repair","stage delta","synthetic events","cannot claim")
    if len(memo)<270 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 56 four-stage funnels use correct denominators")
if __name__=="__main__":main()
