#!/usr/bin/env python3
"""验证 synthetic checkpoint provenance 并生成未运行 repair eval packet。"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
LOCKED="babe582ebffc82b979b77964a7e56417d02f63a4"
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def analyze(checkpoint_path:Path,config_path:Path):
    checkpoint=json.loads(checkpoint_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"))
    if not checkpoint["source_kind"].startswith("synthetic_checkpoint_provenance_") or cfg["upstream_commit"]!=LOCKED or cfg["condition"]!="repair":raise ValueError("provenance boundary 非法")
    expected={key:cfg[key] for key in ("checkpoint_sha256","parent_base_sha256","recipe_sha256","split_sha256","seed")};checks={key:checkpoint.get(key)==value for key,value in expected.items()};checks.update({"completed":checkpoint.get("status")=="complete","step_positive":int(checkpoint.get("step",0))>0,"required_contents":set(checkpoint.get("contents",[]))==set(cfg["required_checkpoint_contents"])})
    if not all(checks.values()):raise ValueError("checkpoint provenance 不匹配")
    protocol=cfg["evaluation_protocol"]
    packet={"condition":"repair","upstream_commit":LOCKED,"final_manifest_sha256":cfg["final_manifest_sha256"],"checkpoint_provenance":checkpoint,"provenance_checks":checks,"provenance_valid":True,"evaluation_protocol":protocol,"protocol_frozen":True,"cleanroom_id":digest({"checkpoint":checkpoint,"protocol":protocol,"manifest":cfg["final_manifest_sha256"]}),"planned_command":["vla-arena","eval","--model","smolvla","--config",cfg["generated_eval_config"]],"status":"NOT_RUN_NO_AUTHORIZATION","command_run":False,"repair_records":None,"vla_arena_run":False,"boundary":"synthetic provenance packet only; no repair checkpoint bytes loaded or final evaluation run"}
    return packet
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--checkpoint-metadata",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--packet",type=Path,required=True);a=p.parse_args();result=analyze(a.checkpoint_metadata,a.config);a.packet.parent.mkdir(parents=True,exist_ok=True);a.packet.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: provenance_valid=true seed={result['checkpoint_provenance']['seed']} status={result['status']}")
if __name__=="__main__":main()
