#!/usr/bin/env python3
"""验收 A/B diagnosis table 与 Gate 5 有限结论。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
try:from .build_diagnosis_table import analyze
except ImportError:from build_diagnosis_table import analyze
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def check(source,table,report):
    rows,expected=analyze(source);rebuilt=[{key:str(value) for key,value in row.items()} for row in rows]
    if read(table)!=rebuilt or json.loads(report.read_text(encoding="utf-8"))!=expected:raise ValueError("diagnosis 产物不可重建")
    return rows,expected
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("input","table","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--gate-submission",type=Path,required=True);p.add_argument("--oral-note",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_table,a.example_report);right=check(a.challenge_input,a.challenge_table,a.challenge_report)
    if left==right:raise ValueError("挑战不得复制 A")
    submission=json.loads(a.gate_submission.read_text(encoding="utf-8"));required_metrics={"baseline.largest_conversion_drop","relation_pair.pair_asymmetry","language_oracle.net_effect","visual_oracle.net_effect"}
    if submission.get("prediction_timestamp_order")!="before_running_challenge" or len(submission.get("prediction_before_analysis",""))<40:raise ValueError("缺少事前预测")
    if submission.get("selected_conclusion")!=right[1]["pattern_label"] or set(submission.get("evidence_metrics",[]))!=required_metrics:raise ValueError("Gate 5 conclusion/evidence 非法")
    alternatives=submission.get("alternative_explanations",[])
    if len(alternatives)<2 or any(len(item)<30 for item in alternatives) or len(submission.get("falsifier",""))<50:raise ValueError("替代解释/falsifier 不完整")
    if "synthetic" not in submission.get("allowed_claim","") or "causal" not in submission.get("forbidden_claim",""):raise ValueError("claim boundary 不完整")
    oral=a.oral_note.read_text(encoding="utf-8").strip();tokens=("conversion funnel","pair asymmetry","language oracle","visual oracle","recovery","damage","alternative","falsifier","insufficient evidence","synthetic","causal")
    if len(oral)<260 or not all(token in oral for token in tokens):raise ValueError("Gate 5 oral note 不完整")
    print("PASS: Day 35 diagnosis table and Gate 5 reasoning")
if __name__=="__main__":main()
