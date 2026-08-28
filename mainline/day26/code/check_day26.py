#!/usr/bin/env python3
"""验收 A/B hypothesis-to-metric 表与因果边界 memo。"""

from __future__ import annotations
import argparse, csv, json
from pathlib import Path
try: from .build_hypothesis_matrix import build
except ImportError: from build_hypothesis_matrix import build

def read(path):
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))
def check(spec, matrix, report):
    rows, expected = build(spec)
    if read(matrix) != rows or json.loads(report.read_text(encoding="utf-8")) != expected: raise ValueError("matrix/report 不可重建")
    return rows, expected
def main():
    p = argparse.ArgumentParser(description=__doc__)
    for prefix in ("example", "challenge"):
        for name in ("spec", "matrix", "report"): p.add_argument(f"--{prefix}-{name}", type=Path, required=True)
    p.add_argument("--challenge-memo", type=Path, required=True); a=p.parse_args()
    left=check(a.example_spec,a.example_matrix,a.example_report); right=check(a.challenge_spec,a.challenge_matrix,a.challenge_report)
    if left==right: raise ValueError("挑战不得复制 A")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip(); required=("hypothesis","prediction","observable","metric","numerator","denominator","intervention","control","falsifier","alternative","causal","synthetic")
    if len(memo)<220 or not all(token in memo for token in required): raise ValueError("challenge memo 不完整")
    print("PASS: Day 26 falsifiable hypothesis-to-metric design")
if __name__ == "__main__": main()
