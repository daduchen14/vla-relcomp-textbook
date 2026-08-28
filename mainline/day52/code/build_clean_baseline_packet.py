#!/usr/bin/env python3
"""扫描 synthetic inventory，并生成未运行的 clean-room baseline packet。"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
LOCKED="babe582ebffc82b979b77964a7e56417d02f63a4"
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def analyze(inventory_path:Path,config_path:Path):
    inventory=json.loads(inventory_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));items=inventory["items"]
    if not inventory["source_kind"].startswith("synthetic_cleanroom_inventory_") or cfg["upstream_commit"]!=LOCKED or cfg["condition"]!="baseline":raise ValueError("clean-room boundary 非法")
    allowed=set(cfg["allowed_roles"]);required=set(cfg["required_roles"]);accepted=[row for row in items if row["role"] in allowed];rejected=[row for row in items if row["role"] not in allowed];present={row["role"] for row in accepted}
    if not required<=present or not rejected:raise ValueError("required inputs/rejection evidence 不完整")
    accepted_identity=[{"role":row["role"],"artifact_id":row["artifact_id"],"sha256":row["sha256"]} for row in accepted]
    cleanroom_id=digest({"accepted":accepted_identity,"commit":LOCKED,"condition":"baseline","manifest_sha256":cfg["final_manifest_sha256"]})
    packet={"condition":"baseline","upstream_commit":LOCKED,"final_manifest_sha256":cfg["final_manifest_sha256"],"inventory_source":"synthetic fixture","accepted_inputs":accepted_identity,"rejected_inputs":rejected,"required_roles_present":True,"repair_artifacts_accepted":any(row["role"].startswith("repair") for row in accepted),"old_results_accepted":any(row["role"]=="old_eval_result" for row in accepted),"cache_policy":{"model_cache":"read-only base model by hash","dataset_cache":"read-only raw dataset by hash","eval_cache":"new empty directory","output_dir":"new unique directory"},"cleanroom_id":cleanroom_id,"planned_command":["vla-arena","eval","--model","smolvla","--config",cfg["generated_eval_config"]],"status":"NOT_RUN_NO_AUTHORIZATION","command_run":False,"baseline_records":None,"vla_arena_run":False,"boundary":"clean-room packet from synthetic inventory; no baseline evaluation or data produced"}
    if packet["repair_artifacts_accepted"] or packet["old_results_accepted"]:raise ValueError("contaminated accepted inputs")
    return packet
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--inventory",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--packet",type=Path,required=True);a=p.parse_args();result=analyze(a.inventory,a.config);a.packet.parent.mkdir(parents=True,exist_ok=True);a.packet.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: accepted={len(result['accepted_inputs'])} rejected={len(result['rejected_inputs'])} status={result['status']}")
if __name__=="__main__":main()
