#!/usr/bin/env python3
"""验证 adapter-only 有界训练计划；只做算术和边界检查，不启动训练。"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def analyze(path:Path):
    cfg=json.loads(path.read_text(encoding="utf-8"));method=cfg["method"];lora=cfg["lora"];batch=cfg["batch"];schedule=cfg["schedule"];memory=cfg["memory_plan"];checkpoint=cfg["checkpoint"];levels=cfg["levels"]
    if cfg.get("source_kind")!="synthetic_bounded_train_config" or cfg.get("model_family")!="smolvla" or cfg.get("device")!="cuda" or cfg.get("authorized_for_training") is not False:raise ValueError("config identity 非法")
    if method!="adapter_only" or cfg["trainable_prefixes"]!=["relation_adapter"] or lora!={"enabled":False,"rank":0,"reason":"not_selected_single_repair"}:raise ValueError("single repair/LoRA 边界非法")
    micro=int(batch["micro_batch_size"]);accum=int(batch["gradient_accumulation_steps"]);world=int(batch["world_size"]);global_batch=micro*accum*world
    if min(micro,accum,world)<=0 or batch["precision"] not in {"bf16","fp16"}:raise ValueError("batch/precision 非法")
    max_steps=int(schedule["max_steps"]);warmup=int(schedule["warmup_steps"]);save_every=int(checkpoint["save_every_steps"])
    if not 0<warmup<max_steps<=500 or float(schedule["learning_rate"])<=0 or float(schedule["gradient_clip_norm"])<=0 or save_every<=0 or max_steps%save_every or checkpoint["keep_last"]<1 or checkpoint["resume_supported"] is not True:raise ValueError("schedule/checkpoint 非法")
    if levels!={"train":[0],"validation":[0],"heldout_test":[1,2]}:raise ValueError("level boundary 非法")
    frozen=int(memory["planning_frozen_parameter_count"]);trainable=int(memory["planning_trainable_parameter_count"]);activation=float(memory["planning_activation_gib"]);factor=float(memory["safety_factor"]);budget=float(memory["device_budget_gib"])
    if min(frozen,trainable)<=0 or activation<=0 or factor<1.2:raise ValueError("memory assumptions 非法")
    parameter_bytes=frozen*int(memory["frozen_bytes_per_parameter"])+trainable*int(memory["trainable_weight_grad_optimizer_bytes"]);estimate=(parameter_bytes/1024**3+activation)*factor;headroom=budget-estimate
    if headroom<=0 or headroom/budget<0.20:raise ValueError("规划显存余量不足 20%")
    report={"model_family":"smolvla","method":"adapter_only","lora_enabled":False,"global_batch_size":global_batch,"max_steps":max_steps,"warmup_steps":warmup,"planned_checkpoint_count":max_steps//save_every,"checkpoint_keep_last":checkpoint["keep_last"],"resume_supported":True,"precision":batch["precision"],"planning_estimated_peak_gib":round(estimate,4),"device_budget_gib":budget,"planning_headroom_gib":round(headroom,4),"planning_headroom_fraction":round(headroom/budget,4),"memory_estimate_status":"ASSUMPTION_ONLY_NOT_PROFILED","training_levels":[0],"heldout_test_levels":[1,2],"authorized_for_training":False,"command_run":False,"boundary":"config validation only; parameter/activation counts are planning assumptions, no CUDA allocation or checkpoint created"}
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--config",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();report=analyze(a.config);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: method=adapter_only global_batch={report['global_batch_size']} estimated_peak_gib={report['planning_estimated_peak_gib']} authorized=false command_run=false")
if __name__=="__main__":main()
