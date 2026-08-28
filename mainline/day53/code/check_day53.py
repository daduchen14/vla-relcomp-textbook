#!/usr/bin/env python3
"""验收 A/B repair provenance、protocol freeze 与 NOT_RUN 边界。"""
from __future__ import annotations
import argparse,json
from pathlib import Path
try:from .build_clean_repair_packet import analyze
except ImportError:from build_clean_repair_packet import analyze
def check(metadata,config,packet_path):
    expected=analyze(metadata,config)
    if json.loads(packet_path.read_text(encoding="utf-8"))!=expected:raise ValueError("repair packet 不可重建")
    if not expected["provenance_valid"] or not expected["protocol_frozen"] or expected["command_run"] or expected["vla_arena_run"] or expected["repair_records"] is not None:raise ValueError("provenance/run boundary 失败")
    return expected
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--example-metadata",type=Path,required=True);p.add_argument("--example-config",type=Path,required=True);p.add_argument("--example-packet",type=Path,required=True);p.add_argument("--challenge-metadata",type=Path,required=True);p.add_argument("--challenge-config",type=Path,required=True);p.add_argument("--challenge-packet",type=Path,required=True);p.add_argument("--challenge-memo",type=Path,required=True);a=p.parse_args();left=check(a.example_metadata,a.example_config,a.example_packet);right=check(a.challenge_metadata,a.challenge_config,a.challenge_packet)
    if left["cleanroom_id"]==right["cleanroom_id"]:raise ValueError("挑战必须换 checkpoint/protocol")
    memo=a.challenge_memo.read_text(encoding="utf-8").strip();required=("checkpoint provenance","checkpoint hash","parent base","recipe hash","split hash","seed","step","optimizer","scheduler","evaluation protocol","same evaluator","clean-room","repair","NOT_RUN","cannot claim")
    if len(memo)<270 or not all(token in memo for token in required):raise ValueError("challenge memo 不完整")
    print("PASS: Day 53 repair packets bind checkpoint provenance")
if __name__=="__main__":main()
