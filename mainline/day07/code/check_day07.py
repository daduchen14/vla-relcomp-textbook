#!/usr/bin/env python3
"""验收 OpenVLA 计划、同口径比较、独立公平性判断，以及可选真实 registry。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from .build_fair_comparison import build
    from .build_openvla_manifest import LOCKED, build_manifest
except ImportError:
    from build_fair_comparison import build
    from build_openvla_manifest import LOCKED, build_manifest


def check_challenge(candidates_path: Path, answer_path: Path) -> None:
    candidates, answer = json.loads(candidates_path.read_text()), json.loads(answer_path.read_text())
    fair = []
    for pair in candidates["pairs"]:
        differences = [key for key in pair["smolvla"] if pair["smolvla"][key] != pair["openvla"][key]]
        if not differences: fair.append(pair["pair_id"])
    if fair != ["pair_alpha"] or answer.get("selected_pair") != fair[0]:
        raise ValueError("必须从新输入逐字段找出唯一同口径 pair")
    reasons = answer.get("rejected_reasons", {})
    if "seed" not in reasons.get("pair_beta", "").lower() or "task" not in reasons.get("pair_gamma", "").lower():
        raise ValueError("拒绝理由必须分别指出 seed 和 task_id 混杂")


def check_real(registry: Path, config: Path) -> None:
    cfg = json.loads(config.read_text())
    with registry.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1: raise ValueError("OpenVLA pilot 必须恰好一个 row")
    row = rows[0]; expected = {"commit": LOCKED, "checkpoint_repo": cfg["checkpoint_repo"],
        "checkpoint_revision": cfg["checkpoint_revision"], "suite": cfg["suite"], "level": "0",
        "task_id": str(cfg["task_id"]), "seed": str(cfg["seed"]), "init_state_index": str(cfg["init_state_index"]),
        "status": "completed", "source_kind": "real_openvla_vla_arena_episode"}
    if any(row.get(k) != v for k, v in expected.items()): raise ValueError("registry 与锁定 OpenVLA 口径不一致")
    if row.get("success") not in {"true", "false"} or int(row.get("frame_count", 0)) <= 0:
        raise ValueError("真实 pilot 必须有 boolean success 和 frame")
    for field in ("log_path", "video_path"):
        path = Path(row[field])
        if not path.is_file() or path.stat().st_size == 0: raise ValueError(f"缺少证据：{field}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--config", type=Path, required=True); p.add_argument("--openvla-manifest", type=Path, required=True)
    p.add_argument("--smolvla-manifest", type=Path, required=True); p.add_argument("--comparison-json", type=Path, required=True)
    p.add_argument("--candidates", type=Path); p.add_argument("--challenge-answer", type=Path); p.add_argument("--registry", type=Path)
    args = p.parse_args(); expected = build_manifest(args.upstream.resolve(), args.config)
    if json.loads(args.openvla_manifest.read_text()) != expected: raise ValueError("OpenVLA manifest 不是从锁定源码/config 生成")
    if json.loads(args.comparison_json.read_text()) != build(args.smolvla_manifest, args.openvla_manifest):
        raise ValueError("比较表控制字段或内容不一致")
    if bool(args.candidates) != bool(args.challenge_answer): raise ValueError("挑战输入/答案必须同时提供")
    if args.candidates: check_challenge(args.candidates, args.challenge_answer)
    if args.registry: check_real(args.registry, args.config)
    print("PASS: Day 7 fair comparison" + (" and real pilot" if args.registry else " (plans only)"))


if __name__ == "__main__": main()
