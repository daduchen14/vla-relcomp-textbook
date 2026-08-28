#!/usr/bin/env python3
"""按 frozen strata/quota 和 salted hash 选择 synthetic casebook。"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def rank(salt,item):return hashlib.sha256(f"{salt}|{item}".encode()).hexdigest()
def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));rows=data["episodes"]
    if not data["source_kind"].startswith("synthetic_case_inventory_") or cfg.get("selection_method")!="salted_sha256_within_stratum" or cfg.get("strata")!=["stable_success","recovery","damage","stable_failure"]:raise ValueError("casebook boundary 非法")
    ids=[row["episode_id"] for row in rows]
    if len(ids)!=len(set(ids)):raise ValueError("episode duplicate")
    selected=[];coverage={}
    for stratum in cfg["strata"]:
        candidates=[row for row in rows if row["stratum"]==stratum];quota=int(cfg["quota_per_stratum"][stratum])
        if len(candidates)<quota:raise ValueError(f"stratum {stratum} 不足 quota")
        ranked=sorted(candidates,key=lambda row:(rank(cfg["salt"],row["episode_id"]),row["episode_id"]));chosen=ranked[:quota];coverage[stratum]={"available":len(candidates),"selected":quota,"unselected":len(candidates)-quota}
        for row in chosen:selected.append({"case_id":f"case-{len(selected)+1:02d}","episode_id":row["episode_id"],"stratum":stratum,"selection_rank_sha256":rank(cfg["salt"],row["episode_id"]),"baseline_video":row["baseline_video"],"repair_video":row["repair_video"],"episode_record_sha256":row["episode_record_sha256"],"selection_reason":"frozen stratum quota + lowest salted hash","video_review_status":"NOT_VIEWED_SYNTHETIC_PATH"})
    return {"selection_method":cfg["selection_method"],"selection_salt_sha256":hashlib.sha256(cfg["salt"].encode()).hexdigest(),"strata_order":cfg["strata"],"coverage":coverage,"selected_cases":selected,"manual_override":False,"outcome_based_manual_selection":False,"all_strata_covered":set(coverage)==set(cfg["strata"]),"video_paths_source":"synthetic fixture only","videos_viewed":False,"final_casebook_available":False,"boundary":"deterministic selection rehearsal; no real episode video viewed or final evidence chosen"}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--casebook",type=Path,required=True);a=p.parse_args();report=analyze(a.input,a.config);a.casebook.parent.mkdir(parents=True,exist_ok=True);a.casebook.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: cases={len(report['selected_cases'])} strata={len(report['coverage'])} manual_override=false videos_viewed=false")
if __name__=="__main__":main()
