#!/usr/bin/env python3
"""用冻结矩阵选择唯一修复或 STOP；本脚本只接受 synthetic rehearsal。"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
INPUT=("candidate_id","evidence_alignment","expected_benefit","implementation_cost","leakage_risk","l0_damage_risk","falsifiability","evidence_gate_passed","source_kind");OUTPUT=("rank","candidate_id","score","evidence_gate_passed","selected","decision_reason","authorized_for_training","source_kind")
ALLOWED={"STOP_NO_REPAIR","LANGUAGE_RELATION_NORMALIZATION","VISUAL_OBJECT_AUXILIARY","CONTROL_EXECUTION_REPAIR"}
def integer(row,key):
    value=int(row[key])
    if value not in range(4):raise ValueError(f"{key} 必须为 0..3")
    return value
def analyze(spec_path:Path,config_path:Path):
    with spec_path.open(encoding="utf-8",newline="") as handle:reader=csv.DictReader(handle);raw=list(reader);fields=tuple(reader.fieldnames or ())
    cfg=json.loads(config_path.read_text(encoding="utf-8"));weights=cfg["weights"];threshold=int(cfg["minimum_non_stop_score"])
    if fields!=INPUT or not raw or set(row["candidate_id"] for row in raw)!=ALLOWED or len(raw)!=len(ALLOWED):raise ValueError("candidate schema/set 非法")
    gates={row["evidence_gate_passed"] for row in raw};sources={row["source_kind"] for row in raw}
    if len(gates)!=1 or not gates<={"0","1"} or len(sources)!=1 or not next(iter(sources)).startswith("synthetic_repair_decision_") or cfg.get("source_kind")!="synthetic_repair_decision_config":raise ValueError("gate/source boundary 非法")
    scored=[]
    for row in raw:
        values={key:integer(row,key) for key in ("evidence_alignment","expected_benefit","implementation_cost","leakage_risk","l0_damage_risk","falsifiability")}
        score=sum(int(weights[key])*value for key,value in values.items());scored.append((score,row))
    gate=next(iter(gates))=="1";non_stop=sorted((item for item in scored if item[1]["candidate_id"]!="STOP_NO_REPAIR"),key=lambda item:(-item[0],item[1]["candidate_id"]));top_score=non_stop[0][0];tied=sum(score==top_score for score,_ in non_stop)>1
    selected="STOP_NO_REPAIR" if not gate or top_score<threshold or tied else non_stop[0][1]["candidate_id"]
    ranked=sorted(scored,key=lambda item:(-item[0],item[1]["candidate_id"]));output=[]
    for rank,(score,row) in enumerate(ranked,1):
        chosen=row["candidate_id"]==selected;reason=("evidence gate failed" if chosen and not gate else "no unique candidate cleared frozen threshold" if chosen and selected=="STOP_NO_REPAIR" else "unique highest non-stop candidate cleared frozen threshold" if chosen else "not selected")
        output.append({"rank":rank,"candidate_id":row["candidate_id"],"score":score,"evidence_gate_passed":str(gate).lower(),"selected":str(chosen).lower(),"decision_reason":reason,"authorized_for_training":"false","source_kind":row["source_kind"]})
    report={"selected_decision":selected,"evidence_gate_passed":gate,"minimum_non_stop_score":threshold,"top_non_stop_score":top_score,"top_non_stop_tied":tied,"selected_count":1,"authorized_for_training":False,"matrix_weights":weights,"decision_status":"SYNTHETIC_REHEARSAL_NOT_PROJECT_AUTHORIZATION","boundary":"a repair choice and permission to spend/run training are separate; no GPU/model run"}
    return output,report
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=OUTPUT);writer.writeheader();writer.writerows(rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--spec",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();rows,report=analyze(a.spec,a.config);write(a.output,rows);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(f"PASS: selected={report['selected_decision']} authorized_for_training=false synthetic=true")
if __name__=="__main__":main()
