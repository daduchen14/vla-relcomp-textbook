#!/usr/bin/env python3
import argparse,json,sys,tempfile
from pathlib import Path
try:from shared.scripts.course_demo import run
except ModuleNotFoundError:
 sys.path.insert(0,str(Path(__file__).resolve().parents[3]));from shared.scripts.course_demo import run
def main():
 p=argparse.ArgumentParser()
 for x in ("example","challenge"):p.add_argument(f"--{x}-spec",type=Path,required=True);p.add_argument(f"--{x}-report",type=Path,required=True)
 p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();ids=[]
 with tempfile.TemporaryDirectory() as t:
  for x in ("example","challenge"):
   actual=json.loads(getattr(a,f"{x}_report").read_text());expected=run(getattr(a,f"{x}_spec"),Path(t)/f"{x}.json")
   if actual!=expected or not actual["all_passed"] or actual["gpu_used"] or any(not s["fallback"] for s in actual["steps"]):raise ValueError("public demo 失败")
   ids.append(actual["demo_id"])
 if ids[0]==ids[1]:raise ValueError("B 必须使用新 demo")
 memo=a.challenge_memo.read_text().strip();req=("public entry","five-minute demo","learner path","reviewer path","one command","expected output","failure fallback","evidence legend","Day 0","COURSE_MAP","synthetic","cannot claim")
 if len(memo)<270 or not all(x in memo for x in req):raise ValueError("memo 不完整")
 print("PASS: Day 68 public entry and A/B demos are executable and fail helpfully")
if __name__=="__main__":main()
