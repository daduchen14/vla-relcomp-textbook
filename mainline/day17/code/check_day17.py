#!/usr/bin/env python3
"""验收 A/B 终态、证据 hash、重试次数与零工作幂等续跑。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .resumable_runner import TERMINAL, read_csv, run_batch
except ImportError:
    from resumable_runner import TERMINAL, read_csv, run_batch


def inspect(registry: Path, checkpoint_path: Path) -> dict:
    _, rows = read_csv(registry); checkpoint = json.loads(checkpoint_path.read_text())
    if set(checkpoint["episodes"]) != {row["episode_id"] for row in rows}: raise ValueError("checkpoint episode 不完整")
    for row in rows:
        state = checkpoint["episodes"][row["episode_id"]]
        if state["status"] not in TERMINAL or row["status"] != state["status"]: raise ValueError("存在非终态/状态不一致")
        if state["status"] == "COMPLETED":
            payload = Path(row["result_path"]).read_bytes()
            if hashlib.sha256(payload).hexdigest() != state["result_sha256"]: raise ValueError("result evidence hash 不一致")
            result = json.loads(payload)
            if result["episode_id"] != row["episode_id"] or str(int(result["success"])) != row["success"]:
                raise ValueError("result 与 registry 错配")
        elif row["success"] != "": raise ValueError("INVALID/FAILED 不得伪装 success=0")
    return {"episode_count": len(rows), "attempts": {row["task_id"]: checkpoint["episodes"][row["episode_id"]]["attempts"] for row in rows}}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for prefix in ("example", "challenge"):
        p.add_argument(f"--{prefix}-input", type=Path, required=True); p.add_argument(f"--{prefix}-registry", type=Path, required=True)
        p.add_argument(f"--{prefix}-checkpoint", type=Path, required=True); p.add_argument(f"--{prefix}-executor", type=Path, required=True)
        p.add_argument(f"--{prefix}-artifact-root", type=Path, required=True)
    p.add_argument("--challenge-memo", type=Path, required=True); args = p.parse_args()
    a = inspect(args.example_registry, args.example_checkpoint); b = inspect(args.challenge_registry, args.challenge_checkpoint)
    if a == b: raise ValueError("挑战不得复制 A 状态")
    before = args.challenge_checkpoint.read_bytes(), args.challenge_registry.read_bytes()
    summary = run_batch(args.challenge_input, args.challenge_registry, args.challenge_checkpoint,
                        args.challenge_executor, args.challenge_artifact_root, max_work_items=0)
    after = args.challenge_checkpoint.read_bytes(), args.challenge_registry.read_bytes()
    if before != after or summary["processed_this_call"] != 0: raise ValueError("终态零工作续跑不幂等")
    note = args.challenge_memo.read_text(encoding="utf-8").strip()
    required = ("retry", "checkpoint", "idempotent", "atomic", "INVALID", "FAILED")
    if len(note) < 160 or not all(word in note for word in required): raise ValueError("resume memo 不完整")
    print("PASS: Day 17 terminal evidence, retries and idempotent zero-work resume")


if __name__ == "__main__": main()
