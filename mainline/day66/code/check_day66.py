#!/usr/bin/env python3
import argparse,hashlib,json,tempfile
from pathlib import Path
try:from .build_complete_report import build
except ImportError:from build_complete_report import build
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for x in ("example","challenge"):p.add_argument(f"--{x}-input",type=Path,required=True);p.add_argument(f"--{x}-config",type=Path,required=True);p.add_argument(f"--{x}-output-dir",type=Path,required=True)
 p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();sources=[]
 with tempfile.TemporaryDirectory() as t:
  for x in ("example","challenge"):
   out=getattr(a,f"{x}_output_dir");actual=json.loads((out/"manifest.json").read_text());re=Path(t)/x;expected=build(getattr(a,f"{x}_input"),getattr(a,f"{x}_config"),re)
   if actual!=expected or any(sha(out/n)!=sha(re/n) for n in ("complete_report.md","manifest.json")):raise ValueError("complete report 不可重建")
   if actual["limitation_dimensions"]<5 or actual["ethics_dimensions"]<5 or not actual["negative_results_present"] or actual["formal_report"]:raise ValueError("报告边界失败")
   sources.append(actual["source_sha256"])
 if sources[0]==sources[1]:raise ValueError("B 必须换 dossier")
 memo=a.challenge_memo.read_text().strip();req=("related work","scope","simulator","task suite","checkpoint","physical robot","statistical uncertainty","ethics","safety","misuse","resource","license","privacy","negative result","synthetic","cannot claim")
 if len(memo)<300 or not all(x in memo for x in req):raise ValueError("memo 不完整")
 print("PASS: Day 66 reports preserve related work, limits, ethics, negative results, and scope")
if __name__=="__main__":main()
