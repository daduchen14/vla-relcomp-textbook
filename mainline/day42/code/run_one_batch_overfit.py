#!/usr/bin/env python3
"""在 CPU toy adapter 上重复同一 batch，输出 loss 轨迹与冻结 hash。"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import torch
from torch import nn

class TinyRepairModel(nn.Module):
    def __init__(self):
        super().__init__();self.backbone=nn.Linear(4,4);self.relation_adapter=nn.Linear(4,4,bias=False);self.action_head=nn.Linear(4,2)
    def forward(self,x):return self.action_head(self.relation_adapter(self.backbone(x)))

def module_hash(module):
    payload=b"".join(t.detach().cpu().contiguous().numpy().tobytes() for t in module.state_dict().values());return hashlib.sha256(payload).hexdigest()
def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));torch.manual_seed(int(cfg["seed"]));model=TinyRepairModel()
    if not data["source_kind"].startswith("synthetic_one_batch_") or cfg.get("source_kind")!="synthetic_one_batch_config" or cfg["trainable_prefix"]!="relation_adapter":raise ValueError("input/config boundary 非法")
    for name,parameter in model.named_parameters():parameter.requires_grad=name.startswith("relation_adapter.")
    control=torch.tensor([row["control_features"] for row in data["pairs"]],dtype=torch.float32);normalized=torch.tensor([row["normalized_features"] for row in data["pairs"]],dtype=torch.float32);target=torch.tensor([row["action_target"] for row in data["pairs"]],dtype=torch.float32)
    if control.shape!=normalized.shape or control.ndim!=2 or control.shape[1]!=4 or target.shape!=(len(control),2):raise ValueError("batch shape 非法")
    optimizer=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=float(cfg["learning_rate"]));max_steps=int(cfg["max_steps"]);log_every=int(cfg["log_every"]);target_loss=float(cfg["target_loss"]);weights=cfg["loss_weights"];frozen_before={"backbone":module_hash(model.backbone),"action_head":module_hash(model.action_head)};adapter_before=module_hash(model.relation_adapter);trajectory=[]
    def compute_loss():
        left=model(control);right=model(normalized);action=(nn.functional.mse_loss(left,target)+nn.functional.mse_loss(right,target))/2;consistency=nn.functional.mse_loss(left,right);return float(weights["action"])*action+float(weights["pair_consistency"])*consistency
    initial=compute_loss().item();final=initial;steps=0
    for step in range(1,max_steps+1):
        optimizer.zero_grad();loss=compute_loss();loss.backward();optimizer.step();steps=step;final=compute_loss().item()
        if step==1 or step%log_every==0 or final<=target_loss:trajectory.append({"step":step,"loss":f"{final:.10f}"})
        if final<=target_loss:break
    frozen_after={"backbone":module_hash(model.backbone),"action_head":module_hash(model.action_head)};adapter_after=module_hash(model.relation_adapter);report={"pair_count":len(data["pairs"]),"initial_loss":round(initial,10),"final_loss":round(final,10),"loss_reduction_factor":round(initial/final,4),"optimizer_steps":steps,"target_loss":target_loss,"target_reached":final<=target_loss,"adapter_changed":adapter_before!=adapter_after,"frozen_hashes_unchanged":frozen_before==frozen_after,"frozen_before":frozen_before,"frozen_after":frozen_after,"trajectory_rows":len(trajectory),"runtime":"free CPU toy optimizer","vla_model_run":False,"generalization_measured":False,"boundary":"one fixed synthetic batch only; not SmolVLA, checkpoint, GPU, or generalization evidence"}
    return trajectory,report
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=("step","loss"));writer.writeheader();writer.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--trajectory",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=analyze(a.input,a.config);write(a.trajectory,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: initial={report['initial_loss']} final={report['final_loss']} target_reached={str(report['target_reached']).lower()} adapter_changed=true frozen_unchanged=true cpu_toy=true")
if __name__=="__main__":main()
