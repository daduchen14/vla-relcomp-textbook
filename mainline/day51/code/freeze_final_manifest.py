#!/usr/bin/env python3
"""验证最终矩阵/停止规则并生成 canonical hash 的未授权 manifest。"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
LOCKED="babe582ebffc82b979b77964a7e56417d02f63a4"
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def analyze(config_path:Path):
    cfg=json.loads(config_path.read_text(encoding="utf-8"))
    if cfg.get("upstream_commit")!=LOCKED or cfg.get("conditions")!=["baseline","repair","ablation_no_normalization"] or cfg.get("seeds")!=[1,2,3] or cfg.get("levels")!=["L0","L1","L2"]:raise ValueError("matrix identity/order 非法")
    required_rules={"max_total_gpu_hours","stop_on_budget_exhaustion","no_posthoc_conditions","retain_failed_runs","accept_negative_result","no_test_driven_tuning"}
    if set(cfg["stop_rules"])!=required_rules or not all(cfg["stop_rules"][key] for key in required_rules if key!="max_total_gpu_hours") or float(cfg["stop_rules"]["max_total_gpu_hours"])<=0:raise ValueError("stop rules 不完整")
    expected=len(cfg["conditions"])*len(cfg["seeds"])*len(cfg["levels"])*len(cfg["task_suites"])*int(cfg["trials_per_cell"])
    manifest={"manifest_version":cfg["manifest_version"],"upstream_commit":LOCKED,"conditions":cfg["conditions"],"seeds":cfg["seeds"],"levels":cfg["levels"],"task_suites":cfg["task_suites"],"trials_per_cell":cfg["trials_per_cell"],"expected_episode_rollouts":expected,"pair_evaluations":cfg["pair_evaluations"],"oracle_evaluations":cfg["oracle_evaluations"],"primary_metrics":cfg["primary_metrics"],"thresholds":cfg["thresholds"],"initial_state_policy":cfg["initial_state_policy"],"stop_rules":cfg["stop_rules"],"missing_run_policy":"retain failure/missing status; no replacement seed","status":"FROZEN_PLAN_NOT_AUTHORIZED","authorized_for_gpu":False,"runs_started":False,"formal_results_available":False,"boundary":"final matrix and stop rules only; Gate 6 not passed and no formal experiment authorized"};manifest["manifest_sha256"]=digest(manifest)
    return manifest
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--config",type=Path,required=True);p.add_argument("--manifest",type=Path,required=True);a=p.parse_args();result=analyze(a.config);a.manifest.parent.mkdir(parents=True,exist_ok=True);a.manifest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: cells={result['expected_episode_rollouts']} status={result['status']} sha256={result['manifest_sha256'][:12]}")
if __name__=="__main__":main()
