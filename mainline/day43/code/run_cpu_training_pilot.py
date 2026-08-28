#!/usr/bin/env python3
"""运行可中断/恢复的免费 CPU toy pilot，并输出可审计日志。"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import torch
from torch import nn

class TinyPilotModel(nn.Module):
    def __init__(self):
        super().__init__();self.backbone=nn.Linear(4,4);self.relation_adapter=nn.Linear(4,4,bias=False);self.action_head=nn.Linear(4,2)
    def forward(self,x):return self.action_head(self.relation_adapter(self.backbone(x)))

def bytes_hash(module):
    payload=b"".join(t.detach().cpu().contiguous().numpy().tobytes() for t in module.state_dict().values());return hashlib.sha256(payload).hexdigest()
def file_hash(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def tensors(rows):
    inputs=[];targets=[]
    for row in rows:
        inputs.extend((row["control_features"],row["normalized_features"]));targets.extend((row["action_target"],row["action_target"]))
    return torch.tensor(inputs,dtype=torch.float32),torch.tensor(targets,dtype=torch.float32)
def write_log(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=("step","train_loss","val_loss","best_val_loss","bad_evals","event"));writer.writeheader();writer.writerows(rows)
def save_state(path,state):path.parent.mkdir(parents=True,exist_ok=True);torch.save(state,path)

def run(input_path:Path,config_path:Path,log_path:Path,checkpoint_path:Path,report_path:Path,stop_after:int|None=None,resume:bool=False):
    data=json.loads(input_path.read_text(encoding="utf-8"));cfg=json.loads(config_path.read_text(encoding="utf-8"))
    if not data["source_kind"].startswith("synthetic_training_pilot_") or cfg.get("runtime")!="free_cpu_toy":raise ValueError("input/config evidence boundary 非法")
    torch.manual_seed(int(cfg["seed"]));model=TinyPilotModel()
    for name,p in model.named_parameters():p.requires_grad=name.startswith("relation_adapter.")
    optimizer=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=float(cfg["learning_rate"]));train_x,train_y=tensors(data["train_pairs"]);val_x,val_y=tensors(data["validation_pairs"])
    input_digest=file_hash(input_path);config_digest=file_hash(config_path);initial_frozen={"backbone":bytes_hash(model.backbone),"action_head":bytes_hash(model.action_head)}
    step=0;best=float("inf");best_step=0;bad_evals=0;rows=[];resume_from=None
    if resume:
        state=torch.load(checkpoint_path,map_location="cpu",weights_only=False)
        if state["input_sha256"]!=input_digest or state["config_sha256"]!=config_digest:raise ValueError("checkpoint 与 input/config 不匹配")
        model.load_state_dict(state["model"]);optimizer.load_state_dict(state["optimizer"]);step=state["step"];best=state["best_val_loss"];best_step=state["best_step"];bad_evals=state["bad_evals"];rows=state["rows"];initial_frozen=state["initial_frozen"];resume_from=step
    max_steps=int(cfg["max_steps"]);eval_every=int(cfg["eval_every"]);save_every=int(cfg["save_every"]);patience=int(cfg["early_stopping_patience"]);min_delta=float(cfg["min_delta"]);early_stopped=False;interrupted=False
    for current in range(step+1,max_steps+1):
        optimizer.zero_grad();prediction=model(train_x);loss=nn.functional.mse_loss(prediction,train_y);loss.backward();optimizer.step();step=current
        if current%eval_every==0:
            with torch.no_grad():val_loss=nn.functional.mse_loss(model(val_x),val_y).item()
            train_loss=loss.item()
            if val_loss<best-min_delta:best=val_loss;best_step=current;bad_evals=0;event="improved"
            else:bad_evals+=1;event="no_improvement"
            if bad_evals>=patience:event="early_stop";early_stopped=True
            rows.append({"step":current,"train_loss":f"{train_loss:.10f}","val_loss":f"{val_loss:.10f}","best_val_loss":f"{best:.10f}","bad_evals":bad_evals,"event":event})
        state={"schema_version":1,"step":step,"model":model.state_dict(),"optimizer":optimizer.state_dict(),"best_val_loss":best,"best_step":best_step,"bad_evals":bad_evals,"rows":rows,"initial_frozen":initial_frozen,"input_sha256":input_digest,"config_sha256":config_digest}
        if current%save_every==0 or early_stopped:save_state(checkpoint_path,state)
        if early_stopped:break
        if stop_after is not None and current>=stop_after:save_state(checkpoint_path,state);interrupted=True;break
    final_frozen={"backbone":bytes_hash(model.backbone),"action_head":bytes_hash(model.action_head)};write_log(log_path,rows)
    report={"status":"interrupted" if interrupted else "complete","resumed":resume,"resume_from_step":resume_from,"final_step":step,"max_steps":max_steps,"early_stopped":early_stopped,"best_step":best_step,"best_val_loss":round(best,10),"logged_evaluations":len(rows),"checkpoint_exists":checkpoint_path.is_file(),"checkpoint_state_fields":["step","model","optimizer","best_val_loss","best_step","bad_evals","rows","input_sha256","config_sha256"],"adapter_sha256":bytes_hash(model.relation_adapter),"frozen_hashes_unchanged":initial_frozen==final_frozen,"input_sha256":input_digest,"config_sha256":config_digest,"runtime":"free CPU toy pilot","vla_model_run":False,"gpu_run":False,"boundary":"synthetic pilot only; not SmolVLA, VLA-Arena environment, CUDA, or formal training evidence"}
    report_path.parent.mkdir(parents=True,exist_ok=True);report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: status={report['status']} step={step} resumed={str(resume).lower()} early_stopped={str(early_stopped).lower()} cpu_toy=true")
    return report,rows
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--log",type=Path,required=True);p.add_argument("--checkpoint",type=Path,required=True);p.add_argument("--report",type=Path,required=True);p.add_argument("--stop-after",type=int);p.add_argument("--resume",action="store_true");a=p.parse_args();run(a.input,a.config,a.log,a.checkpoint,a.report,a.stop_after,a.resume)
if __name__=="__main__":main()
