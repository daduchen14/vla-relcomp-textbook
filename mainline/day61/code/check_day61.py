#!/usr/bin/env python3
"""验收 A/B release candidate 可重建、不可覆盖且有来源索引。"""
import argparse,csv,hashlib,json,tempfile
from pathlib import Path
try:from .build_release_candidate import build
except ImportError:from build_release_candidate import build
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for x in ("example","challenge"):p.add_argument(f"--{x}-input",type=Path,required=True);p.add_argument(f"--{x}-config",type=Path,required=True);p.add_argument(f"--{x}-output-dir",type=Path,required=True)
    p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();seen=[]
    with tempfile.TemporaryDirectory() as tmp:
        for x in ("example","challenge"):
            out=getattr(a,f"{x}_output_dir");actual=json.loads((out/"manifest.json").read_text(encoding="utf-8"));rebuilt=Path(tmp)/x;expected=build(getattr(a,f"{x}_input"),getattr(a,f"{x}_config"),rebuilt)
            if actual!=expected or any(sha(out/name)!=sha(rebuilt/name) for name in ("episodes.csv","provenance_index.json","manifest.json")):raise ValueError("release candidate 无法逐字节重建")
            rows=list(csv.DictReader((out/"episodes.csv").open(encoding="utf-8")));index=json.loads((out/"provenance_index.json").read_text(encoding="utf-8"))
            if len(rows)!=len(index["rows"]) or not actual["source_unchanged"] or actual["formal_results"]:raise ValueError("schema/provenance/boundary 失败")
            seen.append(actual["source_sha256"])
    if seen[0]==seen[1]:raise ValueError("B 必须换输入")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("release candidate","raw immutable","tidy data","one row per episode","primary key","schema","provenance index","SHA-256","derived artifact","no overwrite","synthetic","cannot claim")
    if len(memo)<260 or not all(t in memo for t in required):raise ValueError("memo 不完整")
    print("PASS: Day 61 release candidates are tidy, traceable, immutable, and reproducible")
if __name__=="__main__":main()
