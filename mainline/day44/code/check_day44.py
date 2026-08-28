#!/usr/bin/env python3
"""验收 A/B 稳定性报告、NaN guard 与冻结 recipe。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .audit_and_freeze_recipe import analyze
except ImportError:from audit_and_freeze_recipe import analyze
def check(source,config,report_path,recipe_path):
    report,recipe=analyze(source,config);actual_report=json.loads(report_path.read_text(encoding="utf-8"));actual_recipe=json.loads(recipe_path.read_text(encoding="utf-8"))
    if actual_report!=report or actual_recipe!=recipe:raise ValueError("stability/recipe evidence 不可重建")
    anomaly=report["anomaly_test"]
    if not report["all_finite"] or not report["within_spread_limit"] or not anomaly["caught_before_backward"] or anomaly["optimizer_step_executed"] or not anomaly["adapter_unchanged"] or recipe["authorized_for_formal_training"] or report["vla_model_run"] or report["gpu_run"]:raise ValueError("稳定性、异常或边界验收失败")
    return report,recipe
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for prefix in ("example","challenge"):
        for name in ("input","config","report","recipe"):p.add_argument(f"--{prefix}-{name}",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_input,a.example_config,a.example_report,a.example_recipe);right=check(a.challenge_input,a.challenge_config,a.challenge_report,a.challenge_recipe)
    if left[1]["recipe_sha256"]==right[1]["recipe_sha256"]:raise ValueError("挑战 recipe 必须是新输入")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("numerical stability","seed","finite loss","gradient clipping","pre-clip norm","NaN","abort before step","anomaly injection","spread","frozen recipe","recipe hash","silent change","CPU toy","SmolVLA","formal training")
    if len(memo)<260 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 44 stability audits and frozen recipes")
if __name__=="__main__":main()
