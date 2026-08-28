#!/usr/bin/env python3
"""按预注册 L1/L2 层级分析 synthetic 配对 OOD 结果。"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));rows=data["episodes"]
    if not data["source_kind"].startswith("synthetic_ood_") or cfg.get("registered_levels")!=["L1","L2"] or cfg.get("primary_metric")!="paired_success_rate_delta" or cfg.get("registered_before_results") is not True:raise ValueError("preregistration/evidence boundary 非法")
    ids=[row["episode_id"] for row in rows]
    if len(ids)!=len(set(ids)) or {row["level"] for row in rows}!={"L1","L2"}:raise ValueError("episode/levels 非法")
    levels={}
    for level in cfg["registered_levels"]:
        group=[row for row in rows if row["level"]==level];n=len(group);base=sum(bool(row["baseline_success"]) for row in group);repair=sum(bool(row["repair_success"]) for row in group);improved=sum(not row["baseline_success"] and row["repair_success"] for row in group);regressed=sum(row["baseline_success"] and not row["repair_success"] for row in group);delta=(repair-base)/n;threshold=float(cfg["minimum_delta_by_level"][level]);levels[level]={"episodes":n,"baseline_success_rate":round(base/n,6),"repair_success_rate":round(repair/n,6),"paired_success_rate_delta":round(delta,6),"failure_to_success":improved,"success_to_failure":regressed,"net_discordant":improved-regressed,"minimum_delta":threshold,"passes_minimum_delta":delta>=threshold}
    report={"analysis_config_sha256":hashlib.sha256(config_path.read_bytes()).hexdigest(),"registered_levels":["L1","L2"],"primary_metric":"paired_success_rate_delta","levels":levels,"all_levels_pass":all(row["passes_minimum_delta"] for row in levels.values()),"pooling_for_primary_conclusion":False,"best_level_selection":False,"held_out_source":"synthetic fixture only","checkpoint_status":"NOT_RUN","vla_arena_run":False,"boundary":"synthetic OOD labels; not held-out VLA-Arena L1/L2 model evidence"}
    return report
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--analysis-config",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();report=analyze(a.input,a.analysis_config);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: L1_delta={report['levels']['L1']['paired_success_rate_delta']:+.3f} L2_delta={report['levels']['L2']['paired_success_rate_delta']:+.3f} all_levels_pass={str(report['all_levels_pass']).lower()} synthetic=true")
if __name__=="__main__":main()
