#!/usr/bin/env python3
import argparse,hashlib,json,tempfile
from pathlib import Path
try:from .reproduce_minimal_table import reproduce
except ImportError:from reproduce_minimal_table import reproduce
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for x in ("example","challenge"):p.add_argument(f"--{x}-input",type=Path,required=True);p.add_argument(f"--{x}-expected",type=Path,required=True);p.add_argument(f"--{x}-output-dir",type=Path,required=True)
 p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();inputs=[]
 with tempfile.TemporaryDirectory() as t:
  for x in ("example","challenge"):
   out=getattr(a,f"{x}_output_dir");actual=json.loads((out/"reproduction_log.json").read_text());re=Path(t)/x;expected=reproduce(getattr(a,f"{x}_input"),getattr(a,f"{x}_expected"),re)
   if actual!=expected or any(sha(out/n)!=sha(re/n) for n in ("minimal_table.json","reproduction_log.json")):raise ValueError("reproduction 不可逐字节重建")
   if actual["cache_used"] or actual["gpu_used"] or actual["vla_arena_used"]:raise ValueError("免费复现边界失败")
   inputs.append(actual["input_sha256"])
 if inputs[0]==inputs[1]:raise ValueError("B 必须换输入")
 memo=a.challenge_memo.read_text().strip();req=("fresh clone","locked branch","clean environment","dependency","input hash","script hash","expected output","exit code","cache","CPU","reproduction log","synthetic","cannot claim")
 if len(memo)<280 or not all(x in memo for x in req):raise ValueError("memo 不完整")
 print("PASS: Day 67 A/B minimal tables and reproduction logs are deterministic")
if __name__=="__main__":main()
