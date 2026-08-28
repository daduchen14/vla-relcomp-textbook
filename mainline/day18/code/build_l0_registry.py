#!/usr/bin/env python3
"""由锁定 Day 9 task table 生成五任务等分母 L0 执行 registry。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
FIELDS = ("run_id", "episode_id", "level", "task_id", "trial_id", "seed", "init_state_index",
          "task_name", "bddl_path", "target_object", "reference_object", "relation", "model_id",
          "model_revision", "protocol_lock_sha256", "status", "success", "exception", "video_path", "source_kind")


def ident(prefix: str, payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return prefix + hashlib.sha256(raw).hexdigest()[:16]


def build(table_path: Path, spec_path: Path) -> list[dict]:
    table = json.loads(table_path.read_text(encoding="utf-8")); spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if table.get("commit") != LOCKED or table.get("suite") != "extrapolation_preposition_combinations":
        raise ValueError("task table 不匹配锁定 suite/commit")
    if spec.get("level") != 0: raise ValueError("Day 18 只允许 L0")
    init_indices = spec.get("init_state_indices", [])
    if not init_indices or len(init_indices) != len(set(init_indices)) or any(not isinstance(value, int) or value < 0 for value in init_indices):
        raise ValueError("init_state_indices 必须是非空、不重复、非负整数")
    tasks = sorted((row for row in table["tasks"] if row["level"] == 0), key=lambda row: row["task_id"])
    if [row["task_id"] for row in tasks] != list(range(5)): raise ValueError("锁定 L0 必须恰有 task 0..4")
    run_identity = {key: spec[key] for key in ("batch_name", "level", "protocol_lock_sha256", "model_id", "model_revision")}
    run_id = ident("run-l0-", run_identity); rows = []
    for task in tasks:
        for trial_id, init_index in enumerate(init_indices):
            seed = int(spec["seed_base"]) + task["task_id"] * 100 + trial_id
            ep_identity = {"run_id": run_id, "task_id": task["task_id"], "trial_id": trial_id,
                           "seed": seed, "init_state_index": init_index}
            episode_id = ident("ep-l0-", ep_identity)
            rows.append({"run_id": run_id, "episode_id": episode_id, "level": 0, "task_id": task["task_id"],
                "trial_id": trial_id, "seed": seed, "init_state_index": init_index, "task_name": task["task_name"],
                "bddl_path": task["bddl_path"], "target_object": task["target_object"],
                "reference_object": task["reference_object"], "relation": task["goal_relation"],
                "model_id": spec["model_id"], "model_revision": spec["model_revision"],
                "protocol_lock_sha256": spec["protocol_lock_sha256"], "status": "PLANNED", "success": "",
                "exception": "", "video_path": f"learner_outputs/evidence/{run_id}/{episode_id}/rollout.mp4",
                "source_kind": spec["source_kind"]})
    return rows


def write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--task-table", type=Path, required=True)
    p.add_argument("--spec", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(); rows = build(args.task_table, args.spec); write(args.output, rows)
    print(f"PASS: L0 tasks=5 trials/task={len(rows)//5} episodes={len(rows)} status=PLANNED")


if __name__ == "__main__": main()
