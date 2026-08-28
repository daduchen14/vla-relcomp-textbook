#!/usr/bin/env python3
"""Gate 8 独立模块的输入输出契约与独立期望值计算。"""
from __future__ import annotations
import hashlib,json
STAGES=("detect","align","act","verify")
def expected_analysis(payload,minimum_delta):
 episodes=payload["episodes"];repair=[e for e in episodes if e["condition"]=="repair"];pairs={}
 for e in episodes:pairs.setdefault(e["pair_id"],{})[e["condition"]]=e
 if any(set(v)!={"baseline","repair"} for v in pairs.values()):raise ValueError("pair 不完整")
 funnel={s:{"passed":sum(all(e["stages"][p] for p in STAGES[:i+1]) for e in repair),"n":len(repair)} for i,s in enumerate(STAGES)}
 counts={"n00":0,"n01":0,"n10":0,"n11":0}
 for v in pairs.values():counts[f"n{int(v['baseline']['success'])}{int(v['repair']['success'])}"]+=1
 failures=[]
 for e in repair:
  if not e["success"]:
   stage=next((s for s in STAGES if not e["stages"][s]),"verify");failures.append((e["episode_id"],stage))
 failures.sort();base=sum(v["baseline"]["success"] for v in pairs.values())/len(pairs);rep=sum(v["repair"]["success"] for v in pairs.values())/len(pairs);delta=rep-base
 obs=payload["observation"]
 return {"form_id":payload["form_id"],"input_sha256":hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"observation_summary":{k:{"shape":v["shape"],"dtype":v["dtype"]} for k,v in sorted(obs.items())},"funnel":funnel,"paired_transitions":counts,"first_failure":{"episode_id":failures[0][0],"stage":failures[0][1]},"rates":{"baseline":base,"repair":rep,"delta":delta},"minimum_delta":minimum_delta,"meets_threshold":delta>=minimum_delta,"formal_evidence":False,"boundary":"synthetic capstone; cannot claim VLA-Arena model performance"}
