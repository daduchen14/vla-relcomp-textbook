#!/usr/bin/env python3
"""用官方 BDDL predicate 检测稳定终态，并保留 proxy/release 冲突。"""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path
FIELDS=("episode_id","relation","target_object_id","reference_object_id","step_count","first_predicate_step","first_stable_relation_step","final_official_predicate","final_geometric_proxy","relation_detected","signal_conflict","probe_status")
def bit(value,name):
    if value not in {"0","1"}:raise ValueError(f"{name} 必须为 0/1")
    return value=="1"
def first_run(values,length):
    run=0
    for i,value in enumerate(values):
        run=run+1 if value else 0
        if run==length:return i-length+1
    return None
def analyze(trace_path:Path,config_path:Path):
    with trace_path.open(encoding="utf-8",newline="") as handle:raw=list(csv.DictReader(handle))
    cfg=json.loads(config_path.read_text(encoding="utf-8"));sustain=int(cfg["sustained_relation_steps"]);require_release=cfg["require_gripper_release"] is True;relations=set(cfg["allowed_relations"]);source=cfg.get("source_kind","")
    if sustain<=0 or not relations or not relations.issubset({"On","In"}) or not source.startswith("synthetic_relation_"):raise ValueError("relation config 非法")
    groups={}
    for row in raw:
        if not row.get("episode_id"):raise ValueError("episode_id 不能为空")
        groups.setdefault(row["episode_id"],[]).append(row)
    if not groups:raise ValueError("trace 不能为空")
    output=[]
    for episode_id,rows in sorted(groups.items()):
        rows.sort(key=lambda row:int(row["step"]));steps=[int(row["step"]) for row in rows]
        if steps!=list(range(len(rows))):raise ValueError("step 必须从 0 连续")
        # 关系及两个对象都来自任务定义，不能逐帧改成“最近对象”。
        identities={(row["relation"],row["target_object_id"],row["reference_object_id"]) for row in rows}
        if len(identities)!=1:raise ValueError("relation/target/reference 必须在 episode 内固定")
        relation,target,reference=next(iter(identities))
        if relation not in relations or not target or not reference:raise ValueError("relation identity 非法")
        official=[bit(row["official_predicate"],"official_predicate") for row in rows];proxy=[bit(row["geometric_proxy"],"geometric_proxy") for row in rows];held=[bit(row["gripper_target_contact"],"gripper_target_contact") for row in rows]
        # BDDL predicate 是权威；release 只约束“稳定终态”，proxy 不覆盖官方值。
        valid=[passed and (not contact if require_release else True) for passed,contact in zip(official,held)]
        first_predicate=next((i for i,value in enumerate(official) if value),None);stable=first_run(valid,sustain)
        final_official=official[-1];final_proxy=proxy[-1];conflict="NONE" if final_official==final_proxy else ("OFFICIAL_ONLY" if final_official else "PROXY_ONLY")
        # proxy 只暴露边界冲突；分类和稳定窗口始终由 official 决定。
        if stable is not None:status="STABLE_RELATION"
        elif any(official) and require_release and all(contact for passed,contact in zip(official,held) if passed):status="PREDICATE_TRUE_NOT_RELEASED"
        elif any(official):status="TRANSIENT_RELATION"
        elif any(proxy):status="PROXY_ONLY_CONFLICT"
        else:status="NO_RELATION"
        output.append({"episode_id":episode_id,"relation":relation,"target_object_id":target,"reference_object_id":reference,"step_count":len(rows),"first_predicate_step":"" if first_predicate is None else first_predicate,"first_stable_relation_step":"" if stable is None else stable,"final_official_predicate":str(final_official).lower(),"final_geometric_proxy":str(final_proxy).lower(),"relation_detected":str(stable is not None).lower(),"signal_conflict":conflict,"probe_status":status})
    counts=Counter(row["probe_status"] for row in output);conflicts=Counter(row["signal_conflict"] for row in output);report={"episode_count":len(output),"sustained_relation_steps":sustain,"require_gripper_release":require_release,"probe_status_counts":dict(sorted(counts.items())),"signal_conflict_counts":dict(sorted(conflicts.items())),"source_kind":source,"boundary":"synthetic predicate trace; official BDDL predicate is authoritative and proxy is diagnostic only"}
    return output,report
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--trace",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=analyze(a.trace,a.config);write(a.output,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: episodes={len(rows)} official_predicate_authoritative=true statuses={report['probe_status_counts']}")
if __name__=="__main__":main()
