#!/usr/bin/env python3
"""从冻结 protocol spec 生成不夹带结果的 methods draft。"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
LOCKED="babe582ebffc82b979b77964a7e56417d02f63a4"
SECTIONS=("Research questions","System boundary","Operational definitions","Tasks and conditions","Episode protocol","Pairing and seeds","Measures and analysis","Resources and provenance","Evidence status")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(input_path:Path,config_path:Path,output_dir:Path)->dict:
    if output_dir.exists():raise FileExistsError("methods output 已存在；禁止覆盖")
    spec=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"))
    if spec["upstream_commit"]!=LOCKED or spec.get("result_claims")!=[]:raise ValueError("版本错误或 methods 夹带结果")
    if set(spec["operational_definitions"])!={"observation","action","success","failure"}:raise ValueError("操作定义不完整")
    if not spec["research_questions"] or not spec["tasks"] or not spec["conditions"] or not spec["seeds"]:raise ValueError("protocol 分母不完整")
    body={"Research questions":[f"RQ{i+1}. {q}" for i,q in enumerate(spec["research_questions"])],"System boundary":[spec["system_boundary"],f"Locked upstream commit: `{LOCKED}`."],"Operational definitions":[f"- **{k}**: {v}" for k,v in spec["operational_definitions"].items()],"Tasks and conditions":[f"Tasks: {', '.join(spec['tasks'])}.",f"Conditions: {', '.join(spec['conditions'])}."],"Episode protocol":[f"Trials per task: {spec['trials_per_task']}; initial-state rule: {spec['initial_state_rule']}; stopping rule: {spec['stopping_rule']}."],"Pairing and seeds":[f"Pair key: `{spec['pair_key']}`; frozen seeds: {', '.join(map(str,spec['seeds']))}."],"Measures and analysis":[f"Primary measure: {spec['primary_measure']}.",f"Secondary measures: {', '.join(spec['secondary_measures'])}.",f"Analysis: {spec['analysis_plan']}."],"Resources and provenance":[spec["resource_plan"],"Every raw episode, table, figure, checkpoint, config and script is linked by SHA-256."],"Evidence status":[f"{spec['evidence_mode']} teaching specification only. {spec['boundary']}"]}
    output_dir.mkdir(parents=True);draft=output_dir/"methods_draft.md";lines=[f"# {cfg['title']}",""]
    for section in SECTIONS:lines.extend([f"## {section}","",*body[section],""])
    draft.write_text("\n".join(lines),encoding="utf-8")
    manifest={"source_sha256":sha(input_path),"config_sha256":sha(config_path),"draft_sha256":sha(draft),"sections":list(SECTIONS),"research_question_count":len(spec["research_questions"]),"operational_definitions":sorted(spec["operational_definitions"]),"result_claims_in_methods":False,"upstream_commit":LOCKED,"formal_methods":False};(output_dir/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return manifest
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();m=build(a.input,a.config,a.output_dir);print(f"PASS: sections={len(m['sections'])} result_claims=false formal=false")
if __name__=="__main__":main()
