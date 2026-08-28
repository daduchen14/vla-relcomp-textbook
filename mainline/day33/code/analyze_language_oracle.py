#!/usr/bin/env python3
"""校验语言 oracle 配对并重算 success/四段 recovery 与 damage。"""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path
STAGES=("target_contacted","target_lifted","reference_approached","relation_satisfied");FIELDS=("pair_id","level","task_id","seed","init_state_id","target_object_id","start_relation","start_reference_id","goal_relation","goal_reference_id","control_success","oracle_success","success_transition","first_changed_stage","source_kind")
def bit(value,name):
    if value not in {"0","1"}:raise ValueError(f"{name} 必须为 0/1")
    return int(value)
def normalized(row):return f"TARGET={row['target_object_id']} | START={row['start_relation']}({row['start_reference_id']}) | ACTION=pick_and_place | GOAL={row['goal_relation']}({row['goal_reference_id']})"
def effect(pairs,field):
    values=[(bit(pair["control"][field],field),bit(pair["oracle"][field],field)) for pair in pairs]
    counts=Counter(f"{left}{right}" for left,right in values);failed=sum(left==0 for left,_ in values);succeeded=sum(left==1 for left,_ in values);recovered=counts["01"];damaged=counts["10"]
    return {"n00":counts["00"],"n01":recovered,"n10":damaged,"n11":counts["11"],"recovery_numerator":recovered,"recovery_denominator":failed,"recovery_rate":None if not failed else recovered/failed,"damage_numerator":damaged,"damage_denominator":succeeded,"damage_rate":None if not succeeded else damaged/succeeded}
def analyze(path:Path):
    with path.open(encoding="utf-8",newline="") as handle:raw=list(csv.DictReader(handle))
    groups={}
    for row in raw:
        if row.get("arm") not in {"control","oracle"}:raise ValueError("arm 非法")
        if row["arm"] in groups.get(row["pair_id"],{}):raise ValueError("pair arm 重复")
        groups.setdefault(row["pair_id"],{})[row["arm"]]=row
    if not groups or any(set(arms)!={"control","oracle"} for arms in groups.values()):raise ValueError("pair 缺臂/重复")
    pairs=[];output=[]
    identity=("level","task_id","seed","init_state_id","target_object_id","start_relation","start_reference_id","goal_relation","goal_reference_id","source_kind")
    for pair_id,arms in sorted(groups.items()):
        control,oracle=arms["control"],arms["oracle"]
        if any(control[key]!=oracle[key] for key in identity) or control["instruction_text"]==oracle["instruction_text"] or oracle["instruction_text"]!=normalized(oracle):raise ValueError("pair identity/oracle normalization 非法")
        if not control["source_kind"].startswith("synthetic_language_oracle_"):raise ValueError("source boundary 非法")
        for row in (control,oracle):
            for field in (*STAGES,"success"):bit(row[field],field)
            if row["success"]!=row["relation_satisfied"]:raise ValueError("success 必须等于 relation_satisfied")
        pairs.append(arms);changed=next((stage for stage in STAGES if control[stage]!=oracle[stage]),"NONE");cs,os=control["success"],oracle["success"]
        output.append({"pair_id":pair_id,**{key:control[key] for key in identity[:-1]},"control_success":cs,"oracle_success":os,"success_transition":cs+os,"first_changed_stage":changed,"source_kind":control["source_kind"]})
    report={"pair_count":len(pairs),"success_effect":effect(pairs,"success"),"stage_effects":{stage:effect(pairs,stage) for stage in STAGES},"oracle_instruction_schema":"TARGET | START | ACTION | GOAL","privilege":"BDDL truth; diagnostic oracle only, not final method","boundary":"synthetic paired outcomes, not a VLA-Arena/model run"}
    return output,report
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=analyze(a.input);write(a.output,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");e=report["success_effect"];print(f"PASS: pairs={len(rows)} recovery={e['recovery_numerator']}/{e['recovery_denominator']} damage={e['damage_numerator']}/{e['damage_denominator']} synthetic=true")
if __name__=="__main__":main()
