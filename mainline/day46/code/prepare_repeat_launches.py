#!/usr/bin/env python3
"""冻结 seed 2–3 重复运行，只允许 seed/run/output 改变。"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
try:from mainline.day44.code.audit_and_freeze_recipe import analyze as freeze_recipe
except ModuleNotFoundError:
    sys.path.insert(0,str(Path(__file__).resolve().parents[3]));from mainline.day44.code.audit_and_freeze_recipe import analyze as freeze_recipe
LOCKED="babe582ebffc82b979b77964a7e56417d02f63a4"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def analyze(split_path:Path,seed1_plan_path:Path,repeat_path:Path,stability_input:Path,candidate_path:Path):
    split=json.loads(split_path.read_text(encoding="utf-8"));base=json.loads(seed1_plan_path.read_text(encoding="utf-8"));repeat=json.loads(repeat_path.read_text(encoding="utf-8"));_,recipe=freeze_recipe(stability_input,candidate_path)
    if base["seed"]!=1 or base["upstream_commit"]!=LOCKED or repeat["repeat_seeds"]!=[2,3] or repeat["authorized_for_gpu"] or repeat["commands_run"]:raise ValueError("base/repeat boundary 非法")
    split_sets=[set(split[key]) for key in ("train_episode_ids","validation_episode_ids","test_episode_ids")]
    if any(split_sets[i]&split_sets[j] for i,j in ((0,1),(0,2),(1,2))):raise ValueError("split overlap")
    runs=[];contracts=[]
    for seed in repeat["repeat_seeds"]:
        run_id=f"{repeat['run_prefix']}-seed{seed}";path=f"{repeat['output_root']}/{run_id}";runs.append({"run_id":run_id,"seed":seed,"output_dir":path,"split_sha256":sha(split_path),"recipe_sha256":recipe["recipe_sha256"],"upstream_commit":LOCKED,"resource_budget":repeat["per_run_resource_budget"],"resource_measurements":None,"planned_command":["vla-arena","train","--model","smolvla","--config",f"{path}/config.yaml"],"status":"NOT_RUN_NO_GPU_AUTHORIZATION"});contracts.append({"checkpoint_label":f"checkpoint_{seed}","run_id":run_id,"expected_path":f"{path}/checkpoints/last","status":"NOT_RUN_NO_GPU_AUTHORIZATION","checkpoint_sha256":None,"completed_steps":0})
    total_gpu_hours=sum(float(row["resource_budget"]["max_gpu_hours"]) for row in runs)
    if total_gpu_hours>float(repeat["total_gpu_hours_cap"]):raise ValueError("repeat budget 超限")
    manifest={"base_seed":1,"repeat_seeds":[2,3],"all_registered_seeds":[1,2,3],"same_split_for_all":True,"same_recipe_for_all":True,"allowed_differences":["seed","run_id","output_dir"],"runs":runs,"checkpoint_contracts":contracts,"total_planned_gpu_hours":total_gpu_hours,"total_gpu_hours_cap":repeat["total_gpu_hours_cap"],"variance_policy":{"include_all_registered_seeds":True,"summary":["mean","sample_stdev","per_seed"],"best_seed_selection":False,"metrics":None},"authorized_for_gpu":False,"commands_run":False,"formal_checkpoints_produced":False,"boundary":"repeat launch plan only; no GPU, formal training, checkpoints, or variance results"}
    return manifest
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--split",type=Path,required=True);p.add_argument("--seed1-plan",type=Path,required=True);p.add_argument("--repeat-plan",type=Path,required=True);p.add_argument("--stability-input",type=Path,required=True);p.add_argument("--candidate-recipe",type=Path,required=True);p.add_argument("--manifest",type=Path,required=True);a=p.parse_args();result=analyze(a.split,a.seed1_plan,a.repeat_plan,a.stability_input,a.candidate_recipe);a.manifest.parent.mkdir(parents=True,exist_ok=True);a.manifest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: repeats={result['repeat_seeds']} same_recipe=true same_split=true status=NOT_RUN")
if __name__=="__main__":main()
