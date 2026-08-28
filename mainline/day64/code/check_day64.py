#!/usr/bin/env python3
"""验收 A/B methods draft 可重建、操作定义完整且没有结果泄漏。"""
import argparse,hashlib,json,tempfile
from pathlib import Path
try:from .build_methods_draft import build
except ImportError:from build_methods_draft import build
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for x in ("example","challenge"):p.add_argument(f"--{x}-input",type=Path,required=True);p.add_argument(f"--{x}-config",type=Path,required=True);p.add_argument(f"--{x}-output-dir",type=Path,required=True)
 p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();sources=[]
 with tempfile.TemporaryDirectory() as t:
  for x in ("example","challenge"):
   out=getattr(a,f"{x}_output_dir");actual=json.loads((out/"manifest.json").read_text());re=Path(t)/x;expected=build(getattr(a,f"{x}_input"),getattr(a,f"{x}_config"),re)
   if actual!=expected or any(sha(out/n)!=sha(re/n) for n in ("methods_draft.md","manifest.json")):raise ValueError("methods draft 不可重建")
   if actual["result_claims_in_methods"] or actual["formal_methods"] or len(actual["sections"])!=9:raise ValueError("methods 结构/边界失败")
   sources.append(actual["source_sha256"])
 if sources[0]==sources[1]:raise ValueError("B 必须换 protocol")
 memo=a.challenge_memo.read_text().strip();req=("research question","operational definition","system boundary","task suite","condition","episode protocol","initial state","pair key","frozen seed","analysis plan","provenance","synthetic","cannot claim")
 if len(memo)<280 or not all(x in memo for x in req):raise ValueError("memo 不完整")
 print("PASS: Day 64 methods drafts are complete, versioned, result-free, and bounded")
if __name__=="__main__":main()
