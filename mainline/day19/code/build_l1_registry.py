#!/usr/bin/env python3
"""从 L0 冻结 spec 派生 L1 held-out registry，禁止用测试结果调参。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

try:
    from mainline.day18.code.build_l0_registry import FIELDS, LOCKED, ident
except ModuleNotFoundError:
    # 允许从仓库根直接执行本文件，而不要求预装教材包。
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from mainline.day18.code.build_l0_registry import FIELDS, LOCKED, ident

FROZEN = ("seed_base", "init_state_indices", "protocol_lock_sha256", "model_id", "model_revision")


def derive(table_path: Path, l0_spec_path: Path, l1_spec_path: Path) -> tuple[list[dict], dict]:
    table = json.loads(table_path.read_text(encoding="utf-8")); l0 = json.loads(l0_spec_path.read_text()); l1 = json.loads(l1_spec_path.read_text())
    if table.get("commit") != LOCKED or table.get("suite") != "extrapolation_preposition_combinations":
        raise ValueError("task table 不匹配锁定版本")
    if l0.get("level") != 0 or l1.get("level") != 1: raise ValueError("必须从 L0 派生 L1")
    changed = [key for key in FROZEN if l0.get(key) != l1.get(key)]
    if changed: raise ValueError(f"L1 冻结字段漂移：{changed}")
    if l1.get("heldout_use") != "report_only_never_select_or_tune": raise ValueError("L1 use 违反 held-out 边界")
    forbidden = {"success", "score", "selected_checkpoint", "tuned_threshold", "prompt_after_results"}
    if forbidden.intersection(l1): raise ValueError("L1 spec 混入结果/调参字段")
    tasks = sorted((row for row in table["tasks"] if row["level"] == 1), key=lambda row: row["task_id"])
    if [row["task_id"] for row in tasks] != list(range(5)): raise ValueError("锁定 L1 必须恰有 task 0..4")
    run_identity = {key: l1[key] for key in ("batch_name", "level", "protocol_lock_sha256", "model_id", "model_revision")}
    run_id = ident("run-l1-", run_identity); rows = []
    for task in tasks:
        for trial_id, init_index in enumerate(l1["init_state_indices"]):
            seed = l1["seed_base"] + task["task_id"] * 100 + trial_id
            episode_id = ident("ep-l1-", {"run_id": run_id, "task_id": task["task_id"], "trial_id": trial_id,
                                          "seed": seed, "init_state_index": init_index})
            rows.append({"run_id": run_id, "episode_id": episode_id, "level": 1, "task_id": task["task_id"],
                "trial_id": trial_id, "seed": seed, "init_state_index": init_index, "task_name": task["task_name"],
                "bddl_path": task["bddl_path"], "target_object": task["target_object"],
                "reference_object": task["reference_object"], "relation": task["goal_relation"],
                "model_id": l1["model_id"], "model_revision": l1["model_revision"],
                "protocol_lock_sha256": l1["protocol_lock_sha256"], "status": "PLANNED", "success": "",
                "exception": "", "video_path": f"learner_outputs/evidence/{run_id}/{episode_id}/rollout.mp4",
                "source_kind": l1["source_kind"]})
    guard = {"level": 1, "heldout_use": l1["heldout_use"], "frozen_fields": list(FROZEN), "changed_frozen_fields": [],
             "l0_spec_sha256": hashlib.sha256(l0_spec_path.read_bytes()).hexdigest(),
             "l1_spec_sha256": hashlib.sha256(l1_spec_path.read_bytes()).hexdigest(),
             "episode_count": len(rows), "task_count": 5,
             "boundary": "L1 results cannot select checkpoint, threshold, prompt, or hyperparameters"}
    return rows, guard


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--task-table", type=Path, required=True)
    p.add_argument("--l0-spec", type=Path, required=True); p.add_argument("--l1-spec", type=Path, required=True)
    p.add_argument("--registry", type=Path, required=True); p.add_argument("--guard", type=Path, required=True)
    args = p.parse_args(); rows, guard = derive(args.task_table, args.l0_spec, args.l1_spec); write_csv(args.registry, rows)
    args.guard.parent.mkdir(parents=True, exist_ok=True); args.guard.write_text(json.dumps(guard, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: L1 tasks=5 episodes={len(rows)} frozen_changes=0 heldout=report_only")


if __name__ == "__main__": main()
