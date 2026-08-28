#!/usr/bin/env python3
import argparse,hashlib,json,tempfile
from pathlib import Path
try:from .build_results_draft import build
except ImportError:from build_results_draft import build
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for x in ("example","challenge"):p.add_argument(f"--{x}-input",type=Path,required=True);p.add_argument(f"--{x}-config",type=Path,required=True);p.add_argument(f"--{x}-output-dir",type=Path,required=True)
 p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();sources=[]
 with tempfile.TemporaryDirectory() as t:
  for x in ("example","challenge"):
   out=getattr(a,f"{x}_output_dir");actual=json.loads((out/"manifest.json").read_text());re=Path(t)/x;expected=build(getattr(a,f"{x}_input"),getattr(a,f"{x}_config"),re)
   if actual!=expected or any(sha(out/n)!=sha(re/n) for n in ("results_draft.md","manifest.json")):raise ValueError("results draft 不可重建")
   if not actual["negative_results_preserved"] or not actual["all_claims_have_boundaries"] or actual["formal_results"]:raise ValueError("结果边界失败")
   sources.append(actual["source_sha256"])
 if sources[0]==sources[1]:raise ValueError("B 必须换结果输入")
 memo=a.challenge_memo.read_text().strip();req=("evidence order","denominator","effect estimate","confidence interval","diagnosis","repair","retention","oracle","resource","negative result","limited language","synthetic","cannot claim")
 if len(memo)<280 or not all(x in memo for x in req):raise ValueError("memo 不完整")
 print("PASS: Day 65 results drafts preserve evidence order, negative results, and claim limits")
if __name__=="__main__":main()
