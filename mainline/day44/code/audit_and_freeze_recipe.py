#!/usr/bin/env python3
"""跨 seed 运行 CPU toy 稳定性审计、注入 NaN，并冻结带 hash 的 recipe。"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import torch
from torch import nn

class TinyStableModel(nn.Module):
    def __init__(self):
        super().__init__();self.backbone=nn.Linear(4,4);self.relation_adapter=nn.Linear(4,4,bias=False);self.action_head=nn.Linear(4,2)
    def forward(self,x):return self.action_head(self.relation_adapter(self.backbone(x)))
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def module_hash(module):return hashlib.sha256(b"".join(t.detach().cpu().contiguous().numpy().tobytes() for t in module.state_dict().values())).hexdigest()
def make_batch(data):
    inputs=[];targets=[]
    for row in data["pairs"]:inputs.extend((row["control_features"],row["normalized_features"]));targets.extend((row["action_target"],row["action_target"]))
    return torch.tensor(inputs,dtype=torch.float32),torch.tensor(targets,dtype=torch.float32)
def make_model(seed):
    torch.manual_seed(seed);model=TinyStableModel()
    for name,p in model.named_parameters():p.requires_grad=name.startswith("relation_adapter.")
    return model
def seed_run(seed,cfg,x,y):
    model=make_model(int(cfg["model_init_seed"]));generator=torch.Generator().manual_seed(seed);optimizer=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=float(cfg["learning_rate"]));initial=None;maximum_norm=0.0;clipped=0
    for _ in range(int(cfg["steps"])):
        indices=torch.randint(0,len(x),(int(cfg["batch_size"]),),generator=generator);optimizer.zero_grad();loss=nn.functional.mse_loss(model(x[indices]),y[indices])
        if not torch.isfinite(loss):raise FloatingPointError("non-finite loss before backward")
        if initial is None:initial=loss.item()
        loss.backward();norm=torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],float(cfg["grad_clip_norm"]),error_if_nonfinite=True);maximum_norm=max(maximum_norm,norm.item());clipped+=int(norm.item()>float(cfg["grad_clip_norm"]));optimizer.step()
    final=nn.functional.mse_loss(model(x),y).item();return {"seed":seed,"initial_loss":round(initial,10),"final_loss":round(final,10),"max_preclip_grad_norm":round(maximum_norm,10),"clipped_steps":clipped,"finite":math.isfinite(final)}
def anomaly_run(seed,cfg,x,y):
    model=make_model(int(cfg["model_init_seed"]));optimizer=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=float(cfg["learning_rate"]));bad=y.clone();bad[0,0]=float("nan");before=module_hash(model.relation_adapter);optimizer.zero_grad();loss=nn.functional.mse_loss(model(x),bad);caught=not torch.isfinite(loss);after=module_hash(model.relation_adapter);return {"kind":"nan_target","caught_before_backward":caught,"optimizer_step_executed":False,"adapter_unchanged":before==after}
def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"))
    if not data["source_kind"].startswith("synthetic_stability_") or cfg.get("method")!="adapter_only" or cfg.get("nonfinite_policy")!="abort_before_step" or cfg.get("runtime")!="free_cpu_toy":raise ValueError("stability boundary 非法")
    x,y=make_batch(data);runs=[seed_run(int(seed),cfg,x,y) for seed in cfg["seeds"]];finals=[row["final_loss"] for row in runs];mean=sum(finals)/len(finals);spread=(max(finals)-min(finals))/mean if mean else 0.0;anomaly=anomaly_run(int(cfg["seeds"][0]),cfg,x,y)
    frozen={"recipe_id":cfg["recipe_id"],"method":cfg["method"],"trainable_prefix":"relation_adapter","model_init_seed":cfg["model_init_seed"],"learning_rate":cfg["learning_rate"],"batch_size":cfg["batch_size"],"steps":cfg["steps"],"grad_clip_norm":cfg["grad_clip_norm"],"precision":"float32","seeds":cfg["seeds"],"nonfinite_policy":cfg["nonfinite_policy"],"input_sha256":hashlib.sha256(input_path.read_bytes()).hexdigest(),"candidate_config_sha256":hashlib.sha256(config_path.read_bytes()).hexdigest(),"changes_require_new_recipe_id":True,"authorized_for_formal_training":False,"runtime":"free CPU toy only"};frozen["recipe_sha256"]=digest(frozen)
    report={"seed_runs":runs,"all_finite":all(row["finite"] for row in runs),"relative_final_loss_spread":round(spread,6),"spread_limit":cfg["relative_final_loss_spread_limit"],"within_spread_limit":spread<=float(cfg["relative_final_loss_spread_limit"]),"anomaly_test":anomaly,"recipe_id":cfg["recipe_id"],"recipe_sha256":frozen["recipe_sha256"],"frozen":True,"vla_model_run":False,"gpu_run":False,"boundary":"synthetic CPU stability audit; not SmolVLA, CUDA, or formal training authorization"}
    return report,frozen
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--report",type=Path,required=True);p.add_argument("--frozen-recipe",type=Path,required=True);a=p.parse_args();report,recipe=analyze(a.input,a.config)
    for path,value in ((a.report,report),(a.frozen_recipe,recipe)):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if not report["all_finite"] or not report["within_spread_limit"] or not report["anomaly_test"]["caught_before_backward"]:raise SystemExit("FAIL: stability criteria")
    print(f"PASS: seeds={len(report['seed_runs'])} spread={report['relative_final_loss_spread']} anomaly_caught=true recipe_sha256={report['recipe_sha256'][:12]} cpu_toy=true")
if __name__=="__main__":main()
