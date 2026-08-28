#!/usr/bin/env python3
"""验收两组 pilot 的中断恢复、早停与未中断等价性。"""
from __future__ import annotations
import argparse,csv,json,tempfile
from pathlib import Path
try:from .run_cpu_training_pilot import run
except ImportError:from run_cpu_training_pilot import run
def csv_rows(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle))
def check(source,config,log,checkpoint,report):
    actual=json.loads(report.read_text(encoding="utf-8"));rows=csv_rows(log)
    if actual["status"]!="complete" or not actual["resumed"] or not actual["early_stopped"] or actual["resume_from_step"]<=0 or not actual["frozen_hashes_unchanged"] or actual["vla_model_run"] or actual["gpu_run"]:raise ValueError("resume/early-stop/boundary 失败")
    if not checkpoint.is_file() or len(rows)!=actual["logged_evaluations"]:raise ValueError("checkpoint/log 缺失")
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);expected,expected_rows=run(source,config,root/"full.csv",root/"full.pt",root/"full.json")
    keys=("final_step","early_stopped","best_step","best_val_loss","adapter_sha256","frozen_hashes_unchanged","input_sha256","config_sha256")
    if any(actual[key]!=expected[key] for key in keys) or rows!=[{key:str(value) for key,value in row.items()} for row in expected_rows]:raise ValueError("resume 与未中断基线不等价")
    return actual
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("input","config","log","checkpoint","report"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_log,a.example_checkpoint,a.example_report);right=check(a.challenge_input,a.challenge_config,a.challenge_log,a.challenge_checkpoint,a.challenge_report)
    if left["input_sha256"]==right["input_sha256"] or left["config_sha256"]==right["config_sha256"]:raise ValueError("挑战必须更换 input 和 config")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("pilot","training log","validation loss","early stopping","patience","min_delta","checkpoint","optimizer state","resume","uninterrupted baseline","model hash","CPU toy","SmolVLA","GPU","formal training")
    if len(memo)<260 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 43 interruption/resume matches uninterrupted baselines")
if __name__=="__main__":main()
