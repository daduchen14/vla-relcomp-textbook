#!/usr/bin/env python3
"""从混合 registry 构建严格 L0-only 数据清单并拒绝 split/provenance 泄漏。"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from collections import Counter
from pathlib import Path
INPUT=("sample_id","suite_name","level","task_id","episode_id","source_bddl_sha256","source_episode_sha256","split_group_id","requested_split","eligible_for_training","source_kind");OUTPUT=INPUT+("dataset_row_sha256",);HEX=set("0123456789abcdef")
def valid_hash(value):return len(value)==64 and not set(value)-HEX
def analyze(path:Path):
    with path.open(encoding="utf-8",newline="") as handle:reader=csv.DictReader(handle);raw=list(reader);fields=tuple(reader.fieldnames or ())
    if fields!=INPUT or not raw:raise ValueError("registry schema/rows 非法")
    seen_samples=set();seen_episodes=set();seen_hashes=set();groups={};selected=[];excluded=Counter()
    for row in raw:
        level=int(row["level"])
        if row["sample_id"] in seen_samples or row["episode_id"] in seen_episodes or row["source_episode_sha256"] in seen_hashes:raise ValueError("sample/episode/content 重复")
        seen_samples.add(row["sample_id"]);seen_episodes.add(row["episode_id"]);seen_hashes.add(row["source_episode_sha256"])
        if row["suite_name"]!="extrapolation_preposition_combinations" or level not in {0,1,2} or not re.fullmatch(fr"L{level}T[0-4]",row["task_id"]):raise ValueError("suite/level/task 非法")
        if not valid_hash(row["source_bddl_sha256"]) or not valid_hash(row["source_episode_sha256"]) or row["eligible_for_training"] not in {"0","1"} or not row["source_kind"].startswith("synthetic_l0_registry_"):raise ValueError("provenance/source 非法")
        groups.setdefault(row["split_group_id"],set()).add(row["requested_split"])
        if level==0:
            if row["eligible_for_training"]!="1" or row["requested_split"] not in {"train","validation"}:raise ValueError("L0 eligibility/split 非法")
            digest=hashlib.sha256("\x1f".join(row[key] for key in INPUT).encode()).hexdigest();selected.append({**row,"dataset_row_sha256":digest})
        else:
            if row["eligible_for_training"]!="0" or row["requested_split"]!="heldout_test":raise ValueError("L1/L2 泄漏到训练候选")
            excluded[f"L{level}"]+=1
    if any(len(splits)>1 for splits in groups.values()):raise ValueError("split_group 跨 split 泄漏")
    selected.sort(key=lambda row:(row["requested_split"],row["task_id"],row["sample_id"]));splits=Counter(row["requested_split"] for row in selected);report={"input_rows":len(raw),"output_rows":len(selected),"training_levels":[0],"output_level_counts":{"L0":len(selected)},"output_split_counts":dict(sorted(splits.items())),"excluded_heldout_counts":dict(sorted(excluded.items())),"l1_l2_in_output":0,"duplicate_content_count":0,"split_group_leakage_count":0,"provenance_fields":["source_bddl_sha256","source_episode_sha256","dataset_row_sha256"],"source_kind":"synthetic registry; not collected demonstrations","boundary":"L0-only manifest rehearsal; L1/L2 remain heldout and no training/GPU run"}
    return selected,report
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=OUTPUT);writer.writeheader();writer.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--registry",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=analyze(a.registry);write(a.output,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: rows={len(rows)} levels=[0] l1_l2_in_output=0 synthetic=true")
if __name__=="__main__":main()
