#!/usr/bin/env python3
import argparse,hashlib,json,tempfile
from pathlib import Path
try:from .build_defense_package import build
except ImportError:from build_defense_package import build
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for x in ("example","challenge"):p.add_argument(f"--{x}-input",type=Path,required=True);p.add_argument(f"--{x}-config",type=Path,required=True);p.add_argument(f"--{x}-output-dir",type=Path,required=True)
 p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();sources=[]
 with tempfile.TemporaryDirectory() as t:
  for x in ("example","challenge"):
   out=getattr(a,f"{x}_output_dir");actual=json.loads((out/"manifest.json").read_text());re=Path(t)/x;expected=build(getattr(a,f"{x}_input"),getattr(a,f"{x}_config"),re)
   if actual!=expected or any(sha(out/n)!=sha(re/n) for n in ("slides.md","oral_script.md","qa.md","manifest.json")):raise ValueError("答辩包不可重建")
   if actual["total_seconds"]!=600 or actual["qa_count"]<10 or actual["formal_defense"]:raise ValueError("时间/Q&A/边界失败")
   sources.append(actual["source_sha256"])
 if sources[0]==sources[1]:raise ValueError("B 必须换 talk spec")
 memo=a.challenge_memo.read_text().strip();req=("ten-minute story","assertion title","one message","visual evidence","timing budget","oral script","Q&A","short answer","evidence pointer","boundary sentence","synthetic","cannot claim")
 if len(memo)<280 or not all(x in memo for x in req):raise ValueError("memo 不完整")
 print("PASS: Day 69 defense packages are timed, evidence-linked, bounded, and challenge-specific")
if __name__=="__main__":main()
