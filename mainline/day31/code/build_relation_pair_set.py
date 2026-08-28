#!/usr/bin/env python3
"""从 relation-pair spec 生成两臂计划表；不运行 VLA-Arena。"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path
INPUT=("pair_key","level","relation_slot","target_object_id","reference_object_id","relation_a","relation_b","instruction_a","instruction_b","init_state_a","init_state_b","scene_asset_sha256","camera_config_sha256","object_multiset_sha256","matched_state_group_sha256","seed","model_revision","inference_config_sha256","goal_sync_review","reachability_review","source_kind")
OUTPUT=("pair_id","arm","pair_key","level","relation_slot","target_object_id","reference_object_id","relation","instruction_text","init_state_id","scene_asset_sha256","camera_config_sha256","object_multiset_sha256","matched_state_group_sha256","seed","model_revision","inference_config_sha256","state_difference_whitelist","goal_sync_review","reachability_review","execution_status","real_environment_run","source_kind")
RELATIONS={"next_to","on_top_of","in"}
def digest(*parts):return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()
def load(path:Path):
    with path.open(encoding="utf-8",newline="") as handle:reader=csv.DictReader(handle);rows=list(reader);fields=tuple(reader.fieldnames or ())
    if fields!=INPUT or not rows:raise ValueError("spec schema/rows 非法")
    return rows
def build(path:Path):
    specs=load(path);output=[];seen=set()
    for spec in specs:
        relations=(spec["relation_a"],spec["relation_b"])
        if spec["pair_key"] in seen or set(relations)-RELATIONS or relations[0]==relations[1]:raise ValueError("pair/relation 非法")
        seen.add(spec["pair_key"])
        if spec["init_state_a"]==spec["init_state_b"] or spec["instruction_a"]==spec["instruction_b"]:raise ValueError("relation treatment 未同步")
        hashes=(spec["scene_asset_sha256"],spec["camera_config_sha256"],spec["object_multiset_sha256"],spec["matched_state_group_sha256"],spec["inference_config_sha256"])
        if any(len(value)!=64 or set(value)-set("0123456789abcdef") for value in hashes):raise ValueError("sha256 非法")
        if spec["level"] not in {"0","1","2"} or not spec["target_object_id"] or not spec["reference_object_id"]:raise ValueError("level/object identity 非法")
        if spec["goal_sync_review"]!="pending_human_review" or spec["reachability_review"]!="pending_replay" or not spec["model_revision"].startswith("placeholder_") or not spec["source_kind"].startswith("synthetic_relation_pair_"):raise ValueError("review/source boundary 非法")
        pair_id="rp-"+digest(spec["level"],spec["relation_slot"],spec["target_object_id"],spec["reference_object_id"],*hashes[:4],spec["seed"],*relations)[:12]
        for arm in ("a","b"):
            output.append({"pair_id":pair_id,"arm":arm.upper(),"pair_key":spec["pair_key"],"level":spec["level"],"relation_slot":spec["relation_slot"],"target_object_id":spec["target_object_id"],"reference_object_id":spec["reference_object_id"],"relation":spec[f"relation_{arm}"],"instruction_text":spec[f"instruction_{arm}"],"init_state_id":spec[f"init_state_{arm}"],"scene_asset_sha256":hashes[0],"camera_config_sha256":hashes[1],"object_multiset_sha256":hashes[2],"matched_state_group_sha256":hashes[3],"seed":spec["seed"],"model_revision":spec["model_revision"],"inference_config_sha256":hashes[4],"state_difference_whitelist":"relation_geometry_only","goal_sync_review":spec["goal_sync_review"],"reachability_review":spec["reachability_review"],"execution_status":"PLANNED_NOT_RUN","real_environment_run":"false","source_kind":spec["source_kind"]})
    contrasts=Counter(f"{row['relation_a']}->{row['relation_b']}" for row in specs);report={"pair_count":len(specs),"arm_count":len(output),"relation_contrasts":dict(sorted(contrasts.items())),"all_goal_sync_reviews":"pending_human_review","all_reachability_reviews":"pending_replay","real_environment_runs":0,"boundary":"synthetic relation-pair plan; synchronized instruction/init changes encode one effective relation factor"}
    return output,report
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=OUTPUT);writer.writeheader();writer.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--spec",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=build(a.spec);write(a.output,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: pairs={report['pair_count']} arms={report['arm_count']} execution=planned_not_run")
if __name__=="__main__":main()
