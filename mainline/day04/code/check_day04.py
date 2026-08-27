#!/usr/bin/env python3
"""验收 Day 4 真实 preflight；有 GPU 时再验收单 episode 证据包。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from .real_preflight import LOCKED
except ImportError:
    from real_preflight import LOCKED

SUITE = "extrapolation_preposition_combinations"


def check_preflight(path: Path) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("source_kind") != "real_local_preflight_not_episode":
        raise ValueError("preflight 必须标明不是 episode")
    checks = report.get("checks", {})
    if report.get("ready_for_real_episode") != all(checks.values()):
        raise ValueError("ready 必须由全部真实检查共同决定")
    expected_blockers = [name for name, passed in checks.items() if not passed]
    if report.get("blockers") != expected_blockers or report.get("commit") != LOCKED:
        raise ValueError("preflight blockers 或 commit 不一致")
    return report


def check_episode(registry: Path, gate_config: Path) -> None:
    gate = json.loads(gate_config.read_text(encoding="utf-8"))
    with registry.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1: raise ValueError("Gate 必须恰好提交一个 episode row")
    row = rows[0]
    expected = {"commit": LOCKED, "suite": SUITE, "level": str(gate["level"]),
                "task_id": str(gate["task_id"]), "seed": str(gate["seed"]),
                "init_state_index": str(gate["init_state_index"]), "status": "completed",
                "source_kind": "real_vla_arena_episode"}
    if any(row.get(key) != value for key, value in expected.items()):
        raise ValueError("registry 与 Gate 新输入或锁定版本不一致")
    if row.get("success") not in {"true", "false"} or int(row.get("frame_count", 0)) <= 0:
        raise ValueError("真实 episode 必须记录 boolean success 和非空 frame")
    for field in ("log_path", "video_path"):
        evidence = Path(row[field])
        if not evidence.is_file() or evidence.stat().st_size == 0:
            raise ValueError(f"缺少非空真实证据：{field}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--gate-config", type=Path)
    args = parser.parse_args()
    report = check_preflight(args.preflight)
    if bool(args.registry) != bool(args.gate_config):
        raise ValueError("registry 与 gate-config 必须同时提供")
    if args.registry:
        if not report["ready_for_real_episode"]: raise ValueError("preflight 未通过，不能声称真实 Gate 完成")
        check_episode(args.registry, args.gate_config)
        print("PASS: Gate 1 real episode evidence")
    else:
        print("PASS: truthful local preflight (episode not claimed)")


if __name__ == "__main__":
    main()
