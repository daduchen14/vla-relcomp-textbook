#!/usr/bin/env python3
"""从配对 synthetic L0 结果计算保持率与 catastrophic regressions。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));rows=data["episodes"]
    if not data["source_kind"].startswith("synthetic_l0_retention_") or cfg.get("evidence_level")!="synthetic_fixture_not_model_eval":raise ValueError("evidence boundary 非法")
    ids=[row["episode_id"] for row in rows]
    if len(ids)!=len(set(ids)) or not rows:raise ValueError("episode id 必须非空唯一")
    baseline=sum(bool(row["baseline_success"]) for row in rows);repair=sum(bool(row["repair_success"]) for row in rows);retained=sum(bool(row["baseline_success"] and row["repair_success"]) for row in rows);regressions=[row["episode_id"] for row in rows if row["baseline_success"] and not row["repair_success"]];recoveries=[row["episode_id"] for row in rows if not row["baseline_success"] and row["repair_success"]]
    if baseline==0:raise ValueError("无法定义保持率")
    paired=[{"episode_id":row["episode_id"],"baseline_success":bool(row["baseline_success"]),"repair_success":bool(row["repair_success"]),"transition":("kept_success" if row["baseline_success"] and row["repair_success"] else "catastrophic_regression" if row["baseline_success"] else "recovered" if row["repair_success"] else "kept_failure")} for row in rows]
    report={"episode_count":len(rows),"baseline_successes":baseline,"repair_successes":repair,"baseline_success_rate":round(baseline/len(rows),6),"repair_success_rate":round(repair/len(rows),6),"success_rate_delta":round((repair-baseline)/len(rows),6),"retained_baseline_successes":retained,"retention_rate":round(retained/baseline,6),"minimum_retention_rate":cfg["minimum_retention_rate"],"retention_pass":retained/baseline>=float(cfg["minimum_retention_rate"]),"catastrophic_regressions":regressions,"recoveries":recoveries,"paired_episode_ids":ids,"checkpoint_status":"NOT_RUN_SYNTHETIC_FIXTURE_ONLY","vla_arena_run":False,"boundary":"synthetic paired labels only; not checkpoint or VLA-Arena L0 evaluation"}
    return paired,report
def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:w=csv.DictWriter(handle,fieldnames=("episode_id","baseline_success","repair_success","transition"));w.writeheader();w.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--paired-table",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=analyze(a.input,a.config);write_csv(a.paired_table,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: retention={report['retention_rate']} delta={report['success_rate_delta']:+.3f} regressions={len(report['catastrophic_regressions'])} synthetic=true")
if __name__=="__main__":main()
