#!/usr/bin/env python3
"""生成 seed-1 launch packet、资源计划和 NOT_RUN checkpoint contract。"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
try:from mainline.day44.code.audit_and_freeze_recipe import analyze as freeze_recipe
except ModuleNotFoundError:
    sys.path.insert(0,str(Path(__file__).resolve().parents[3]));from mainline.day44.code.audit_and_freeze_recipe import analyze as freeze_recipe
LOCKED="babe582ebffc82b979b77964a7e56417d02f63a4"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def analyze(split_path:Path,plan_path:Path,stability_input:Path,candidate_recipe:Path):
    split=json.loads(split_path.read_text(encoding="utf-8"));plan=json.loads(plan_path.read_text(encoding="utf-8"));_,recipe=freeze_recipe(stability_input,candidate_recipe)
    if plan.get("seed")!=1 or plan.get("upstream_commit")!=LOCKED or plan.get("model")!="smolvla" or plan.get("authorized_for_gpu") or plan.get("command_run"):raise ValueError("seed/commit/model/authorization boundary 非法")
    sets={name:set(split[name]) for name in ("train_episode_ids","validation_episode_ids","test_episode_ids")};overlaps={"train_validation":sorted(sets["train_episode_ids"]&sets["validation_episode_ids"]),"train_test":sorted(sets["train_episode_ids"]&sets["test_episode_ids"]),"validation_test":sorted(sets["validation_episode_ids"]&sets["test_episode_ids"])}
    if any(overlaps.values()) or not all(sets.values()):raise ValueError("split 非空且必须互斥")
    training_reads=sorted(sets["train_episode_ids"]|sets["validation_episode_ids"]);test_access_log=plan["test_access_log"]
    if test_access_log or sets["test_episode_ids"]&set(training_reads):raise ValueError("test isolation 失败")
    packet={"run_id":plan["run_id"],"seed":1,"model":"smolvla","upstream_commit":LOCKED,"dataset_level":"L0","split_sha256":sha(split_path),"frozen_recipe_sha256":recipe["recipe_sha256"],"train_episode_count":len(sets["train_episode_ids"]),"validation_episode_count":len(sets["validation_episode_ids"]),"test_episode_count":len(sets["test_episode_ids"]),"split_overlaps":overlaps,"training_reads":training_reads,"test_access_log":test_access_log,"test_isolated":True,"resource_budget":plan["resource_budget"],"resource_measurements":None,"planned_command":["vla-arena","train","--model","smolvla","--config",plan["generated_config_path"]],"authorized_for_gpu":False,"command_run":False,"launch_status":"NOT_RUN_NO_GPU_AUTHORIZATION","boundary":"launch packet only; no SmolVLA, GPU, formal training, or checkpoint produced"}
    contract={"run_id":plan["run_id"],"checkpoint_label":"checkpoint_1","expected_path":plan["checkpoint_path"],"status":"NOT_RUN_NO_GPU_AUTHORIZATION","required_contents":["policy","optimizer","scheduler","step","config","recipe_sha256","split_sha256","resource_record"],"checkpoint_sha256":None,"completed_steps":0,"formal_training_evidence":False}
    return packet,contract
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--split",type=Path,required=True);p.add_argument("--plan",type=Path,required=True);p.add_argument("--stability-input",type=Path,required=True);p.add_argument("--candidate-recipe",type=Path,required=True);p.add_argument("--packet",type=Path,required=True);p.add_argument("--checkpoint-contract",type=Path,required=True);a=p.parse_args();packet,contract=analyze(a.split,a.plan,a.stability_input,a.candidate_recipe)
    for path,value in ((a.packet,packet),(a.checkpoint_contract,contract)):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"PASS: seed=1 test_isolated=true launch_status={packet['launch_status']} checkpoint_status={contract['status']}")
if __name__=="__main__":main()
