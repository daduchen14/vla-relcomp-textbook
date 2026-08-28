#!/usr/bin/env python3
"""从 L0 normalized registry 确定性采样平衡关系，并生成完整对比两臂。"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
INPUT=("sample_id","level","split","relation","object_combination","raw_instruction","normalized_instruction","action_target_sha256","source_episode_sha256","source_kind");OUTPUT=("pair_id","arm","sample_id","level","split","relation","object_combination","instruction_text","action_target_sha256","source_episode_sha256","pair_label","sample_weight","source_kind");HEX=set("0123456789abcdef")
def valid_hash(value):return len(value)==64 and not set(value)-HEX
def analyze(input_path:Path,config_path:Path):
    with input_path.open(encoding="utf-8",newline="") as handle:reader=csv.DictReader(handle);raw=list(reader);fields=tuple(reader.fieldnames or ())
    cfg=json.loads(config_path.read_text(encoding="utf-8"));relations=tuple(cfg["required_relations"]);target=int(cfg["target_per_relation"]);seed=str(cfg["sampling_seed"])
    if fields!=INPUT or not raw or set(relations)!={"NextTo","On","In","Between"} or target<=0 or cfg.get("source_kind")!="synthetic_training_pair_config":raise ValueError("input/config 非法")
    groups=defaultdict(list);samples=set();episodes=set()
    for row in raw:
        if row["sample_id"] in samples or row["source_episode_sha256"] in episodes:raise ValueError("sample/episode 重复")
        samples.add(row["sample_id"]);episodes.add(row["source_episode_sha256"])
        if row["level"]!="0" or row["split"] not in {"train","validation"} or row["relation"] not in relations:raise ValueError("L0/split/relation 非法")
        if row["raw_instruction"]==row["normalized_instruction"] or not valid_hash(row["action_target_sha256"]) or not valid_hash(row["source_episode_sha256"]) or not row["source_kind"].startswith("synthetic_training_pair_"):raise ValueError("contrast/provenance/source 非法")
        groups[row["relation"]].append(row)
    if any(len(groups[relation])<target for relation in relations):raise ValueError("某关系不足以达到冻结 target")
    selected=[]
    for relation in relations:
        ranked=sorted(groups[relation],key=lambda row:hashlib.sha256(f"{seed}\x1f{row['sample_id']}".encode()).hexdigest());selected.extend(ranked[:target])
    output=[]
    for row in sorted(selected,key=lambda item:(item["relation"],item["sample_id"])):
        pair_id="tp-"+hashlib.sha256(f"{row['sample_id']}\x1f{row['source_episode_sha256']}".encode()).hexdigest()[:12]
        for arm,column in (("control","raw_instruction"),("normalized","normalized_instruction")):
            output.append({"pair_id":pair_id,"arm":arm,"sample_id":row["sample_id"],"level":"0","split":row["split"],"relation":row["relation"],"object_combination":row["object_combination"],"instruction_text":row[column],"action_target_sha256":row["action_target_sha256"],"source_episode_sha256":row["source_episode_sha256"],"pair_label":"same_action_instruction_contrast","sample_weight":"1.0","source_kind":row["source_kind"]})
    counts=Counter(row["relation"] for row in selected);report={"input_rows":len(raw),"selected_sample_count":len(selected),"pair_count":len(selected),"arm_count":len(output),"selected_relation_counts":dict(sorted(counts.items())),"relation_balance_gap":max(counts.values())-min(counts.values()),"complete_pair_count":len(selected),"incomplete_pair_count":0,"training_levels":[0],"heldout_levels_seen":[],"sampling_seed":seed,"target_per_relation":target,"selection_uses_outcomes":False,"boundary":"synthetic L0 contrast-pair manifest; no images/actions loaded and no model/GPU run"}
    return output,report
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=OUTPUT);writer.writeheader();writer.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=analyze(a.input,a.config);write(a.output,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: pairs={report['pair_count']} arms={report['arm_count']} balance_gap=0 levels=[0] synthetic=true")
if __name__=="__main__":main()
