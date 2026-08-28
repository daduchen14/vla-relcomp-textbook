#!/usr/bin/env python3
"""汇总四段漏斗、relation pair 与两类 oracle 的合成 Gate 5 证据。"""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path
STAGES=("target_contacted","target_lifted","reference_approached","relation_satisfied");FIELDS=("category","metric","numerator","denominator","value","boundary")
def bit(value,name):
    if value not in {"0","1"}:raise ValueError(f"{name} 必须为 0/1")
    return int(value)
def paired(groups,kind,arms):
    selected=[]
    for group_id,rows in groups.items():
        if rows[0]["record_type"]!=kind:continue
        by_arm={row["arm"]:row for row in rows}
        if len(rows)!=2 or set(by_arm)!=set(arms):raise ValueError(f"{kind} pair 缺臂/重复")
        selected.append(by_arm)
    return selected
def effect(pairs,left,right,field="success"):
    values=[(bit(pair[left][field],field),bit(pair[right][field],field)) for pair in pairs];counts=Counter(f"{a}{b}" for a,b in values);failed=sum(a==0 for a,_ in values);succeeded=sum(a==1 for a,_ in values)
    recovery=None if not failed else counts["01"]/failed;damage=None if not succeeded else counts["10"]/succeeded
    return {"n00":counts["00"],"n01":counts["01"],"n10":counts["10"],"n11":counts["11"],"recovery_numerator":counts["01"],"recovery_denominator":failed,"recovery_rate":recovery,"damage_numerator":counts["10"],"damage_denominator":succeeded,"damage_rate":damage,"net_effect":None if recovery is None or damage is None else recovery-damage}
def analyze(path:Path):
    with path.open(encoding="utf-8",newline="") as handle:raw=list(csv.DictReader(handle))
    if not raw:raise ValueError("evidence 不能为空")
    groups={}
    for row in raw:
        if row["record_type"] not in {"baseline","relation_pair","language_oracle","visual_oracle"}:raise ValueError("record_type 非法")
        if not row["source_kind"].startswith("synthetic_gate5_"):raise ValueError("source boundary 非法")
        for field in (*STAGES,"success"):bit(row[field],field)
        if row["success"]!=row["relation_satisfied"]:raise ValueError("success/relation 冲突")
        if groups.get(row["group_id"]) and groups[row["group_id"]][0]["record_type"]!=row["record_type"]:raise ValueError("group_id 跨类型复用")
        groups.setdefault(row["group_id"],[]).append(row)
    baseline=[rows[0] for rows in groups.values() if rows[0]["record_type"]=="baseline" and len(rows)==1 and rows[0]["arm"]=="baseline"]
    if not baseline:raise ValueError("baseline 缺失")
    counts={"episodes":len(baseline),**{stage:sum(bit(row[stage],stage) for row in baseline) for stage in STAGES}}
    chain=("episodes",*STAGES);funnel={}
    table=[]
    for before,after in zip(chain,chain[1:]):
        denominator=counts[before];numerator=counts[after];value=None if not denominator else numerator/denominator;name=f"{before}_to_{after}";funnel[name]={"numerator":numerator,"denominator":denominator,"rate":value};table.append({"category":"baseline_funnel","metric":name,"numerator":numerator,"denominator":denominator,"value":"" if value is None else f"{value:.6f}","boundary":"synthetic rehearsal"})
    relation=paired(groups,"relation_pair",("A","B"));asymmetric=sum(pair["A"]["success"]!=pair["B"]["success"] for pair in relation);asym_rate=None if not relation else asymmetric/len(relation);table.append({"category":"relation_pair","metric":"pair_asymmetry","numerator":asymmetric,"denominator":len(relation),"value":"" if asym_rate is None else f"{asym_rate:.6f}","boundary":"complete synthetic pairs only"})
    language=paired(groups,"language_oracle",("control","oracle"));visual=paired(groups,"visual_oracle",("control","oracle"));le=effect(language,"control","oracle");ve=effect(visual,"control","oracle")
    for name,data in (("language_oracle",le),("visual_oracle",ve)):
        for metric in ("recovery_rate","damage_rate","net_effect"):table.append({"category":name,"metric":metric,"numerator":data["recovery_numerator"] if metric=="recovery_rate" else (data["damage_numerator"] if metric=="damage_rate" else ""),"denominator":data["recovery_denominator"] if metric=="recovery_rate" else (data["damage_denominator"] if metric=="damage_rate" else ""),"value":"" if data[metric] is None else f"{data[metric]:.6f}","boundary":"diagnostic oracle; synthetic"})
    if len(relation)<4 or le["recovery_denominator"]<3 or ve["recovery_denominator"]<3 or le["net_effect"] is None or ve["net_effect"] is None or abs(le["net_effect"]-ve["net_effect"])<0.20:label="INSUFFICIENT_EVIDENCE"
    elif le["net_effect"]>ve["net_effect"]:label="LANGUAGE_RELATION_CANDIDATE"
    else:label="VISUAL_OBJECT_SELECTION_CANDIDATE"
    drops={name:1-data["rate"] for name,data in funnel.items() if data["rate"] is not None};largest=max(drops,key=drops.get);report={"baseline_episode_count":len(baseline),"funnel":funnel,"largest_conversion_drop":largest,"relation_pair":{"pair_count":len(relation),"asymmetric_pairs":asymmetric,"pair_asymmetry":asym_rate},"language_oracle":le,"visual_oracle":ve,"pattern_label":label,"decision_rule":"candidate only if >=4 relation pairs, each oracle has >=3 control failures, and absolute net-effect gap >=0.20","evidence_status":"SYNTHETIC_REHEARSAL_NO_RESEARCH_CONCLUSION","boundary":"all inputs synthetic; Gate 5 skills rehearsal, not model evidence"}
    return table,report
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--table",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=analyze(a.input);write(a.table,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: label={report['pattern_label']} largest_drop={report['largest_conversion_drop']} synthetic=true")
if __name__=="__main__":main()
