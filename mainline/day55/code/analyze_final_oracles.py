#!/usr/bin/env python3
"""验证 synthetic final oracle 完整性，并把诊断与最终方法严格分栏。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));rows=data["records"]
    required=cfg["required_conditions"]
    if not data["source_kind"].startswith("synthetic_final_oracle_") or required!=["baseline","repair","language_oracle","visual_oracle"] or cfg.get("oracle_role")!="diagnostic_only":raise ValueError("oracle boundary 非法")
    episode_ids=sorted({row["episode_id"] for row in rows});expected={(episode,condition) for episode in episode_ids for condition in required};observed={(row["episode_id"],row["condition"]) for row in rows}
    if expected!=observed or len(rows)!=len(observed) or len(episode_ids)!=int(cfg["registered_episode_count"]):raise ValueError("oracle records 缺失/重复")
    grouped={condition:{row["episode_id"]:bool(row["success"]) for row in rows if row["condition"]==condition} for condition in required};rates={condition:round(sum(values.values())/len(episode_ids),6) for condition,values in grouped.items()}
    deployable={condition:{"success_rate":rates[condition],"deployable":True} for condition in ("baseline","repair")};diagnostic={}
    repair=grouped["repair"]
    for condition in ("language_oracle","visual_oracle"):
        oracle=grouped[condition];repair_failures=sum(not value for value in repair.values());repair_successes=sum(repair.values());recoveries=sum(not repair[e] and oracle[e] for e in episode_ids);damage=sum(repair[e] and not oracle[e] for e in episode_ids);diagnostic[condition]={"success_rate":rates[condition],"privileged_information":cfg["privileged_information"][condition],"deployable":False,"recovery_rate_among_repair_failures":round(recoveries/repair_failures,6) if repair_failures else None,"damage_rate_among_repair_successes":round(damage/repair_successes,6) if repair_successes else None,"headroom_over_repair":round(rates[condition]-rates["repair"],6)}
    return {"registered_episode_count":len(episode_ids),"records_complete":True,"deployable_results":deployable,"diagnostic_oracles":diagnostic,"oracle_role":"diagnostic_only","oracle_in_primary_result":False,"oracle_deployable":False,"missing_record_policy":"fail_closed","records_source":"synthetic fixture only","vla_arena_run":False,"final_oracle_data_available":False,"boundary":"oracle uses privileged information; no checkpoint, simulator, or final model evidence"}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();report=analyze(a.input,a.config);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: episodes={report['registered_episode_count']} deployable=2 diagnostic=2 oracle_primary=false synthetic=true")
if __name__=="__main__":main()
