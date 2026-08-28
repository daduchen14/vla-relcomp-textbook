"""Day 70 参考实现：只在完成 Gate 8 限时提交后查看。"""
import hashlib,json
STAGES=("detect","align","act","verify")
def analyze(payload,minimum_delta):
 episodes=payload["episodes"];repair=[e for e in episodes if e["condition"]=="repair"];pairs={}
 for e in episodes:pairs.setdefault(e["pair_id"],{})[e["condition"]]=e
 funnel={s:{"passed":sum(all(e["stages"][p] for p in STAGES[:i+1]) for e in repair),"n":len(repair)} for i,s in enumerate(STAGES)};counts={"n00":0,"n01":0,"n10":0,"n11":0}
 for v in pairs.values():counts[f"n{int(v['baseline']['success'])}{int(v['repair']['success'])}"]+=1
 failures=sorted((e["episode_id"],next((s for s in STAGES if not e["stages"][s]),"verify")) for e in repair if not e["success"]);base=sum(v["baseline"]["success"] for v in pairs.values())/len(pairs);rep=sum(v["repair"]["success"] for v in pairs.values())/len(pairs);delta=rep-base
 return {"form_id":payload["form_id"],"input_sha256":hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"observation_summary":{k:{"shape":v["shape"],"dtype":v["dtype"]} for k,v in sorted(payload["observation"].items())},"funnel":funnel,"paired_transitions":counts,"first_failure":{"episode_id":failures[0][0],"stage":failures[0][1]},"rates":{"baseline":base,"repair":rep,"delta":delta},"minimum_delta":minimum_delta,"meets_threshold":delta>=minimum_delta,"formal_evidence":False,"boundary":"synthetic capstone; cannot claim VLA-Arena model performance"}
