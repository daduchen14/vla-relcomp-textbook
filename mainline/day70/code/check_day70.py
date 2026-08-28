#!/usr/bin/env python3
"""Gate 8：验收 A/B 独立核心模块，生成未代替现场口述的 Gate report。"""
import argparse,importlib.util,json
from pathlib import Path
try:from .capstone_contract import expected_analysis
except ImportError:from capstone_contract import expected_analysis
def load_module(path):
 spec=importlib.util.spec_from_file_location("learner_core",path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def check_workspace(workspace,form):
 payload=json.loads((workspace/"exam.json").read_text());source=(workspace/"core_module.py").read_text()
 if payload["form_id"]!=form or "NotImplementedError" in source or len(source)<450:raise ValueError(f"Form {form} 未独立完成 core_module")
 module=load_module(workspace/"core_module.py");reports=[]
 for threshold in (0.10,0.30):
  actual=module.analyze(json.loads(json.dumps(payload)),threshold);expected=expected_analysis(payload,threshold)
  if actual!=expected:raise ValueError(f"Form {form} threshold={threshold} 结果不符")
  reports.append(actual)
 if reports[0]["meets_threshold"]==reports[1]["meets_threshold"]:raise ValueError("现场参数变化没有改变阈值判断")
 return reports
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--example-workspace",type=Path,required=True);p.add_argument("--challenge-workspace",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();ra=check_workspace(a.example_workspace,"A");rb=check_workspace(a.challenge_workspace,"B")
 if ra[0]["input_sha256"]==rb[0]["input_sha256"]:raise ValueError("B 必须是新输入")
 memo=(a.challenge_workspace/"oral_memo.md").read_text().strip();req=("fresh clone","without answer key","observation","four-stage funnel","paired transitions","failure episode","minimal repair","parameter change","threshold","evidence boundary","synthetic","cannot claim","live oral")
 if len(memo)<420 or not all(x in memo for x in req):raise ValueError("Gate 8 oral memo 不完整")
 report={"gate":"Gate 8","machine_rehearsal":"PASS","forms":["A","B"],"new_input_verified":True,"parameter_change_verified":True,"formal_evidence":False,"live_oral_observed":False,"learner_gate_status":"AWAITING_FRESH_CLONE_TIMED_LIVE_ORAL_NOT_PASSED","gate8_passed":False,"outcome":"停止扩张","reason":"LIVE_ORAL_AND_FORMAL_EVIDENCE_MISSING","allowed_materials":["course README","locked upstream source","own notes before timed attempt"],"forbidden_materials":["shared/answer_keys/day70* during attempt","copied reference module","Agent-authored oral response"],"next_action":"learner repeats Form B from fresh clone under time limit and completes live oral without answer key"};a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n");print("PASS: Gate 8 machine rehearsal; learner/live gate remains NOT_PASSED")
if __name__=="__main__":main()
