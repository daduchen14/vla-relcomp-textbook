#!/usr/bin/env python3
"""验算 synthetic 多 seed 最小消融的单变量与成本公平性。"""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));runs=data["runs"]
    if not data["source_kind"].startswith("synthetic_ablation_") or cfg.get("selected_factor")!="relation_normalization":raise ValueError("evidence/factor boundary 非法")
    conditions={row["condition"] for row in runs};seeds=set(cfg["registered_seeds"])
    if conditions!={"baseline","repair","ablation_no_normalization"}:raise ValueError("conditions 不完整")
    grouped={condition:{row["seed"]:row for row in runs if row["condition"]==condition} for condition in conditions}
    if any(set(rows)!=seeds for rows in grouped.values()):raise ValueError("每个 condition 必须含全部 seeds")
    repair_signature=data["signatures"]["repair"];ablation_signature=data["signatures"]["ablation_no_normalization"];changed=sorted(key for key in repair_signature if repair_signature[key]!=ablation_signature[key])
    if changed!=["relation_normalization"]:raise ValueError("消融必须只改 selected factor")
    paired=[]
    for seed in sorted(seeds):
        base=grouped["baseline"][seed];repair=grouped["repair"][seed];ablation=grouped["ablation_no_normalization"][seed]
        if len({row["split_sha256"] for row in (base,repair,ablation)})!=1 or len({row["steps"] for row in (repair,ablation)})!=1:raise ValueError("split/steps 不匹配")
        gap=abs(float(repair["gpu_hours"])-float(ablation["gpu_hours"]))/float(repair["gpu_hours"])
        paired.append({"seed":seed,"baseline_score":base["score"],"repair_score":repair["score"],"ablation_score":ablation["score"],"repair_gain":round(repair["score"]-base["score"],6),"component_effect":round(repair["score"]-ablation["score"],6),"relative_cost_gap":round(gap,6),"cost_matched":gap<=float(cfg["max_relative_cost_gap"])})
    effects=[row["component_effect"] for row in paired]
    report={"selected_factor":"relation_normalization","changed_factors":changed,"single_variable":True,"registered_seeds":sorted(seeds),"paired_rows":paired,"all_cost_matched":all(row["cost_matched"] for row in paired),"max_relative_cost_gap":cfg["max_relative_cost_gap"],"mean_component_effect":round(statistics.mean(effects),6),"sample_stdev_component_effect":round(statistics.stdev(effects),6),"all_seeds_reported":True,"best_seed_selection":False,"evidence":"synthetic run ledger only","formal_runs_available":False,"boundary":"not checkpoint, GPU, VLA-Arena, or causal model evidence"}
    return report
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();report=analyze(a.input,a.config);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: factor={report['selected_factor']} effect={report['mean_component_effect']:+.3f} cost_matched={str(report['all_cost_matched']).lower()} synthetic=true")
if __name__=="__main__":main()
