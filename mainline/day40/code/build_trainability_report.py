#!/usr/bin/env python3
"""在 CPU toy model 上验证双项 loss 与参数冻结边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import torch
from torch import nn

class TinyRepairModel(nn.Module):
    """只模拟 backbone→relation adapter→action head 的接口。"""
    def __init__(self):
        super().__init__();self.backbone=nn.Linear(4,4);self.relation_adapter=nn.Linear(4,4,bias=False);self.action_head=nn.Linear(4,2)
    def forward(self,x):return self.action_head(self.relation_adapter(self.backbone(x)))

def analyze(input_path:Path,config_path:Path):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"));torch.manual_seed(int(cfg["seed"]));model=TinyRepairModel()
    trainable=tuple(cfg["trainable_prefixes"]);frozen=tuple(cfg["frozen_prefixes"])
    if trainable!=("relation_adapter",) or set(frozen)!={"backbone","action_head"} or cfg.get("source_kind")!="synthetic_trainability_config":raise ValueError("parameter boundary config 非法")
    for name,parameter in model.named_parameters():
        root=name.split(".",1)[0]
        if root not in set(trainable+frozen):raise ValueError("parameter 未分类")
        parameter.requires_grad=root in trainable
    control=torch.tensor([row["control_features"] for row in data["pairs"]],dtype=torch.float32);normalized=torch.tensor([row["normalized_features"] for row in data["pairs"]],dtype=torch.float32);target=torch.tensor([row["action_target"] for row in data["pairs"]],dtype=torch.float32)
    if control.ndim!=2 or control.shape!=normalized.shape or control.shape[1]!=4 or target.shape!=(control.shape[0],2) or not data["source_kind"].startswith("synthetic_trainability_"):raise ValueError("toy input shape/source 非法")
    pred_control=model(control);pred_normalized=model(normalized);action_loss=(nn.functional.mse_loss(pred_control,target)+nn.functional.mse_loss(pred_normalized,target))/2;consistency_loss=nn.functional.mse_loss(pred_control,pred_normalized);total=float(cfg["action_loss_weight"])*action_loss+float(cfg["pair_consistency_weight"])*consistency_loss;total.backward()
    params=[]
    for name,parameter in model.named_parameters():
        params.append({"name":name,"numel":parameter.numel(),"requires_grad":parameter.requires_grad,"grad_present":parameter.grad is not None,"grad_norm":None if parameter.grad is None else round(parameter.grad.norm().item(),8)})
    report={"pair_count":len(data["pairs"]),"loss":{"action_mse":round(action_loss.item(),8),"pair_consistency_mse":round(consistency_loss.item(),8),"total":round(total.item(),8),"weights":{"action":float(cfg["action_loss_weight"]),"pair_consistency":float(cfg["pair_consistency_weight"])}},"parameters":params,"trainable_parameter_names":[row["name"] for row in params if row["requires_grad"]],"frozen_parameter_names":[row["name"] for row in params if not row["requires_grad"]],"trainable_numel":sum(row["numel"] for row in params if row["requires_grad"]),"total_numel":sum(row["numel"] for row in params),"frozen_grad_count":sum(row["grad_present"] for row in params if not row["requires_grad"]),"optimizer_step_run":False,"runtime":"free CPU toy model only","boundary":"not SmolVLA weights, not a VLA forward pass, and not training evidence"}
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();report=analyze(a.input,a.config);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: trainable={report['trainable_parameter_names']} frozen_grad_count=0 optimizer_step=false runtime=cpu_toy")
if __name__=="__main__":main()
