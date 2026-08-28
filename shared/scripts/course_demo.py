#!/usr/bin/env python3
"""一键运行课程公开入口的免费 smoke demo，并给出逐步失败回退。"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def command(step,tmp):
 if step=="route_check":return [sys.executable,"mainline/day00_diagnostic/code/diagnostic_router.py","--check"]
 if step=="structure_check":return [sys.executable,"shared/scripts/validate_v2.py"]
 suffix="a" if step=="minimal_table_a" else "b"
 return [sys.executable,"mainline/day67/code/reproduce_minimal_table.py","--input",f"shared/fixtures/day67_repro_{suffix}.csv","--expected",f"shared/fixtures/day67_expected_{suffix}.json","--output-dir",str(tmp/f"table_{suffix}")]
def run(spec_path,output_path):
 if output_path.exists():raise FileExistsError("demo report 已存在")
 spec=json.loads(spec_path.read_text());allowed={"route_check","structure_check","minimal_table_a","minimal_table_b"}
 if not spec["steps"] or any(s not in allowed for s in spec["steps"]):raise ValueError("demo step 不合法")
 results=[]
 with tempfile.TemporaryDirectory() as name:
  tmp=Path(name)
  for step in spec["steps"]:
   p=subprocess.run(command(step,tmp),cwd=ROOT,text=True,capture_output=True)
   results.append({"step":step,"status":"PASS" if p.returncode==0 else "FAIL","exit_code":p.returncode,"output":(p.stdout+p.stderr).strip(),"fallback":spec["fallbacks"][step]})
 report={"demo_id":spec["demo_id"],"spec_sha256":sha(spec_path),"steps":results,"all_passed":all(r["status"]=="PASS" for r in results),"gpu_used":False,"boundary":"free local teaching smoke; not VLA-Arena execution"};output_path.parent.mkdir(parents=True,exist_ok=True);output_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n");return report
def main():
 p=argparse.ArgumentParser();p.add_argument("--spec",type=Path,default=ROOT/"shared/fixtures/day68_demo_a.json");p.add_argument("--output",type=Path,default=ROOT/"learner_outputs/mainline/day68/demo_report.json");a=p.parse_args();r=run(a.spec,a.output);print(f"{'PASS' if r['all_passed'] else 'FAIL'}: demo={r['demo_id']} steps={len(r['steps'])} gpu=false");raise SystemExit(0 if r["all_passed"] else 1)
if __name__=="__main__":main()
