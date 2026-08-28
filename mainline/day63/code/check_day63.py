#!/usr/bin/env python3
import argparse,hashlib,json,tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
try:from .generate_paper_figures import build
except ImportError:from generate_paper_figures import build
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for x in ("example","challenge"):p.add_argument(f"--{x}-input",type=Path,required=True);p.add_argument(f"--{x}-config",type=Path,required=True);p.add_argument(f"--{x}-output-dir",type=Path,required=True)
 p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();sources=[]
 with tempfile.TemporaryDirectory() as t:
  for x in ("example","challenge"):
   out=getattr(a,f"{x}_output_dir");ET.parse(out/"paper_figures.svg");actual=json.loads((out/"manifest.json").read_text());rebuilt=Path(t)/x;expected=build(getattr(a,f"{x}_input"),getattr(a,f"{x}_config"),rebuilt)
   if actual!=expected or any(sha(out/n)!=sha(rebuilt/n) for n in ("paper_figures.svg","caption.md","manifest.json")):raise ValueError("图不可重建")
   if actual["axis"]!={"min":0.0,"max":1.0} or actual["formal_results"]:raise ValueError("axis/boundary 失败")
   sources.append(actual["source_sha256"])
 if sources[0]==sources[1]:raise ValueError("B 必须换输入")
 memo=a.challenge_memo.read_text().strip();req=("paper figure","stage funnel","paired transitions","intervention","0–1 axis","Wilson interval","denominator","colorblind-safe","direct label","caption","synthetic","cannot claim")
 if len(memo)<260 or not all(x in memo for x in req):raise ValueError("memo 不完整")
 print("PASS: Day 63 SVG figures use honest axes, intervals, labels, and boundaries")
if __name__=="__main__":main()
