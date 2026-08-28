#!/usr/bin/env python3
"""从 synthetic run ledger 汇总时间、显存、失败、存储和成本。"""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
VALID=("completed","failed","not_run")
def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));runs=data["runs"]
    if not data["source_kind"].startswith("synthetic_resource_ledger_") or cfg.get("cost_currency")!="USD" or cfg.get("failure_cost_policy")!="include_all_attempted":raise ValueError("resource boundary 非法")
    ids=[row["run_id"] for row in runs]
    if len(ids)!=len(set(ids)) or set(ids)!=set(cfg["planned_run_ids"]) or any(row["status"] not in VALID for row in runs):raise ValueError("planned run ledger 不完整")
    attempted=[row for row in runs if row["status"]!="not_run"];completed=[row for row in attempted if row["status"]=="completed"];failed=[row for row in attempted if row["status"]=="failed"];not_run=[row for row in runs if row["status"]=="not_run"]
    if any(row["gpu_seconds"]<=0 or row["wall_seconds"]<=0 or row["peak_memory_gib"]<=0 for row in attempted) or any(row["gpu_seconds"]!=0 or row["wall_seconds"]!=0 for row in not_run):raise ValueError("resource measurement/status 不一致")
    gpu_hours=sum(float(row["gpu_seconds"])*int(row["gpu_count"]) for row in attempted)/3600;wall_hours=sum(float(row["wall_seconds"]) for row in attempted)/3600;rate=float(cfg["synthetic_hourly_rate_usd"])
    by_condition={}
    for condition in sorted({row["condition"] for row in runs}):
        group=[row for row in runs if row["condition"]==condition];by_condition[condition]={"planned":len(group),"attempted":sum(row["status"]!="not_run" for row in group),"completed":sum(row["status"]=="completed" for row in group),"failed":sum(row["status"]=="failed" for row in group),"not_run":sum(row["status"]=="not_run" for row in group)}
    return {"denominators":{"planned":len(runs),"attempted":len(attempted),"completed":len(completed),"failed":len(failed),"not_run":len(not_run)},"completion_rate_among_attempted":round(len(completed)/len(attempted),6) if attempted else None,"failure_rate_among_attempted":round(len(failed)/len(attempted),6) if attempted else None,"total_gpu_hours_including_failures":round(gpu_hours,6),"total_wall_hours_attempted":round(wall_hours,6),"max_peak_memory_gib_attempted":max(float(row["peak_memory_gib"]) for row in attempted) if attempted else None,"total_storage_gib_all_runs":round(sum(float(row["storage_gib"]) for row in runs),6),"estimated_cost_usd_including_failures":round(gpu_hours*rate,6),"synthetic_hourly_rate_usd":rate,"completed_wall_seconds_median":round(statistics.median(float(row["wall_seconds"]) for row in completed),6) if completed else None,"failed_runs":[{"run_id":row["run_id"],"condition":row["condition"],"exit_code":row["exit_code"],"failure_reason":row["failure_reason"],"gpu_seconds":row["gpu_seconds"]} for row in failed],"by_condition":by_condition,"failed_cost_included":True,"records_source":"synthetic ledger only","real_gpu_measurements":False,"boundary":"not cloud bill, nvidia-smi profile, or final experiment resource evidence"}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();report=analyze(a.input,a.config);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: planned={report['denominators']['planned']} attempted={report['denominators']['attempted']} failed={report['denominators']['failed']} gpu_hours={report['total_gpu_hours_including_failures']} synthetic=true")
if __name__=="__main__":main()
