#!/usr/bin/env python3
import argparse,hashlib,json,tempfile
from pathlib import Path
try:from .generate_paper_table import build
except ImportError:from generate_paper_table import build
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for x in ("example","challenge"):p.add_argument(f"--{x}-input",type=Path,required=True);p.add_argument(f"--{x}-config",type=Path,required=True);p.add_argument(f"--{x}-output-dir",type=Path,required=True)
 p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();sources=[]
 with tempfile.TemporaryDirectory() as t:
  for x in ("example","challenge"):
   out=getattr(a,f"{x}_output_dir");actual=json.loads((out/"manifest.json").read_text());re=Path(t)/x;expected=build(getattr(a,f"{x}_input"),getattr(a,f"{x}_config"),re)
   if actual!=expected or any(sha(out/n)!=sha(re/n) for n in ("table.csv","table.md","manifest.json")):raise ValueError("表格不可重建")
   if not actual["counts_reported"] or actual["formal_results"]:raise ValueError("表格边界失败")
   sources.append(actual["source_sha256"])
 if sources[0]==sources[1]:raise ValueError("B 必须换输入")
 memo=a.challenge_memo.read_text().strip();req=("paper table","caption","successes","denominator","Wilson interval","effect estimate","bold rule","descriptive only","rounding","tidy source","synthetic","cannot claim")
 if len(memo)<250 or not all(x in memo for x in req):raise ValueError("memo 不完整")
 print("PASS: Day 62 paper tables expose counts, intervals, rules, and evidence boundary")
if __name__=="__main__":main()
