#!/usr/bin/env python3
"""从 synthetic episode stages 计算 baseline/repair 四段漏斗。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
STAGES=("target_contacted","target_lifted","reference_approached","relation_satisfied")
def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));rows=data["episodes"]
    if not data["source_kind"].startswith("synthetic_stage_funnel_") or cfg.get("stages")!=list(STAGES) or cfg.get("conditions")!=["baseline","repair"]:raise ValueError("stage schema 非法")
    conditions={condition:[row for row in rows if row["condition"]==condition] for condition in cfg["conditions"]}
    if any(len(group)!=int(cfg["episodes_per_condition"]) for group in conditions.values()):raise ValueError("condition 分母不完整")
    all_ids=[];summaries={}
    for condition,group in conditions.items():
        ids=[row["episode_id"] for row in group];all_ids.extend((condition,item) for item in ids)
        if len(ids)!=len(set(ids)):raise ValueError("episode duplicate")
        for row in group:
            values=[bool(row[stage]) for stage in STAGES]
            if any(values[index] and not values[index-1] for index in range(1,len(values))):raise ValueError("stage monotonicity 失败")
        counts={stage:sum(bool(row[stage]) for row in group) for stage in STAGES};reach={stage:round(counts[stage]/len(group),6) for stage in STAGES};conversion={}
        for index in range(1,len(STAGES)):
            previous,current=STAGES[index-1],STAGES[index];denominator=counts[previous];conversion[f"{previous}_to_{current}"]={"numerator":counts[current],"denominator":denominator,"rate":round(counts[current]/denominator,6) if denominator else None,"dropoff_count":denominator-counts[current]}
        summaries[condition]={"episode_count":len(group),"stage_counts":counts,"stage_reach_rates":reach,"adjacent_conversion":conversion}
    deltas={stage:round(summaries["repair"]["stage_reach_rates"][stage]-summaries["baseline"]["stage_reach_rates"][stage],6) for stage in STAGES}
    return {"stages":list(STAGES),"conditions":summaries,"repair_minus_baseline_reach_delta":deltas,"conversion_denominator":"previous_stage_reached","monotonicity_pass":True,"episode_keys_unique":len(all_ids)==len(set(all_ids)),"records_source":"synthetic fixture only","vla_arena_run":False,"stage_metrics_final":False,"boundary":"not checkpoint, simulator-event, or final stage-metric evidence"}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();report=analyze(a.input,a.config);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: conditions=2 stages=4 monotonic=true final_stage_delta={report['repair_minus_baseline_reach_delta']['relation_satisfied']:+.3f} synthetic=true")
if __name__=="__main__":main()
