#!/usr/bin/env python3
"""校验可撤销视觉 oracle 配对并重算阶段 recovery/damage。"""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path
STAGES=("target_contacted","target_lifted","reference_approached","relation_satisfied");FIELDS=("pair_id","level","task_id","seed","init_state_id","target_object_id","reference_object_id","control_success","oracle_success","success_transition","first_changed_stage","oracle_overlay_spec","overlay_source","cleanup_verified","source_kind")
def bit(value,name):
    if value not in {"0","1"}:raise ValueError(f"{name} 必须为 0/1")
    return int(value)
def overlay(row):return f"TARGET_BOX={row['target_object_id']} | REFERENCE_BOX={row['reference_object_id']}"
def effect(pairs,field):
    values=[(bit(pair["control"][field],field),bit(pair["visual_oracle"][field],field)) for pair in pairs];counts=Counter(f"{a}{b}" for a,b in values);failed=sum(a==0 for a,_ in values);succeeded=sum(a==1 for a,_ in values)
    return {"n00":counts["00"],"n01":counts["01"],"n10":counts["10"],"n11":counts["11"],"recovery_numerator":counts["01"],"recovery_denominator":failed,"recovery_rate":None if not failed else counts["01"]/failed,"damage_numerator":counts["10"],"damage_denominator":succeeded,"damage_rate":None if not succeeded else counts["10"]/succeeded}
def analyze(path:Path):
    with path.open(encoding="utf-8",newline="") as handle:raw=list(csv.DictReader(handle))
    groups={}
    for row in raw:
        if row.get("arm") not in {"control","visual_oracle"} or row["arm"] in groups.get(row["pair_id"],{}):raise ValueError("arm 非法/重复")
        groups.setdefault(row["pair_id"],{})[row["arm"]]=row
    if not groups or any(set(arms)!={"control","visual_oracle"} for arms in groups.values()):raise ValueError("pair 缺臂")
    pairs=[];output=[];identity=("level","task_id","seed","init_state_id","target_object_id","reference_object_id","instruction_text","source_kind")
    for pair_id,arms in sorted(groups.items()):
        control,oracle=arms["control"],arms["visual_oracle"]
        if any(control[key]!=oracle[key] for key in identity) or control["overlay_spec"]!="NONE" or control["overlay_source"]!="none" or oracle["overlay_spec"]!=overlay(oracle) or oracle["overlay_source"]!="simulator_ground_truth":raise ValueError("pair identity/overlay 非法")
        if control["overlay_removed_after_episode"]!="1" or oracle["overlay_removed_after_episode"]!="1" or not control["source_kind"].startswith("synthetic_visual_oracle_"):raise ValueError("reversibility/source boundary 非法")
        for row in (control,oracle):
            for field in (*STAGES,"success"):bit(row[field],field)
            if row["success"]!=row["relation_satisfied"]:raise ValueError("success/relation 冲突")
        pairs.append(arms);changed=next((stage for stage in STAGES if control[stage]!=oracle[stage]),"NONE");cs,os=control["success"],oracle["success"]
        output.append({"pair_id":pair_id,**{key:control[key] for key in identity[:6]},"control_success":cs,"oracle_success":os,"success_transition":cs+os,"first_changed_stage":changed,"oracle_overlay_spec":oracle["overlay_spec"],"overlay_source":oracle["overlay_source"],"cleanup_verified":"true","source_kind":control["source_kind"]})
    report={"pair_count":len(pairs),"success_effect":effect(pairs,"success"),"stage_effects":{stage:effect(pairs,stage) for stage in STAGES},"allowed_policy_input_change":"agentview RGB diagnostic overlay only","fixed_instruction":True,"overlay_source":"simulator_ground_truth","cleanup_verified_for_all_pairs":True,"privilege":"target/reference simulator truth; diagnostic only","boundary":"synthetic paired outcomes, not rendered images or a model run"}
    return output,report
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=analyze(a.input);write(a.output,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");e=report["success_effect"];print(f"PASS: pairs={len(rows)} recovery={e['recovery_numerator']}/{e['recovery_denominator']} damage={e['damage_numerator']}/{e['damage_denominator']} cleanup=true synthetic=true")
if __name__=="__main__":main()
