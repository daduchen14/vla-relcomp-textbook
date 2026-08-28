#!/usr/bin/env python3
"""从 L0 冻结 spec 派生 L2 strong-OOD registry 与 held-out guard。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

try: from mainline.day18.code.build_l0_registry import FIELDS, LOCKED, ident
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3])); from mainline.day18.code.build_l0_registry import FIELDS, LOCKED, ident

FROZEN = ("seed_base", "init_state_indices", "protocol_lock_sha256", "model_id", "model_revision")


def derive(table_path: Path, l0_path: Path, l2_path: Path) -> tuple[list[dict], dict]:
    table = json.loads(table_path.read_text()); l0 = json.loads(l0_path.read_text()); l2 = json.loads(l2_path.read_text())
    if table.get("commit") != LOCKED or l0.get("level") != 0 or l2.get("level") != 2: raise ValueError("必须由锁定表/L0 派生 L2")
    changed = [key for key in FROZEN if l0.get(key) != l2.get(key)]
    if changed: raise ValueError(f"L2 冻结字段漂移：{changed}")
    if l2.get("heldout_use") != "report_only_never_select_or_tune" or l2.get("taxonomy_version") != "first_unmet_stage_v1":
        raise ValueError("held-out use 或 taxonomy 未冻结")
    if {"success", "score", "selected_checkpoint", "tuned_threshold", "prompt_after_results"}.intersection(l2):
        raise ValueError("L2 spec 混入结果/选择字段")
    tasks = sorted((row for row in table["tasks"] if row["level"] == 2), key=lambda row: row["task_id"])
    if [row["task_id"] for row in tasks] != list(range(5)): raise ValueError("锁定 L2 必须恰有 task 0..4")
    run_id = ident("run-l2-", {key: l2[key] for key in ("batch_name", "level", "protocol_lock_sha256", "model_id", "model_revision")})
    rows = []
    for task in tasks:
        for trial_id, init_index in enumerate(l2["init_state_indices"]):
            seed = l2["seed_base"] + task["task_id"] * 100 + trial_id
            episode_id = ident("ep-l2-", {"run_id": run_id, "task_id": task["task_id"], "trial_id": trial_id,
                                          "seed": seed, "init_state_index": init_index})
            rows.append({"run_id": run_id, "episode_id": episode_id, "level": 2, "task_id": task["task_id"],
                "trial_id": trial_id, "seed": seed, "init_state_index": init_index, "task_name": task["task_name"],
                "bddl_path": task["bddl_path"], "target_object": task["target_object"],
                "reference_object": task["reference_object"], "relation": task["goal_relation"],
                "model_id": l2["model_id"], "model_revision": l2["model_revision"],
                "protocol_lock_sha256": l2["protocol_lock_sha256"], "status": "PLANNED", "success": "",
                "exception": "", "video_path": f"learner_outputs/evidence/{run_id}/{episode_id}/rollout.mp4",
                "source_kind": l2["source_kind"]})
    guard = {"level": 2, "strong_ood": True, "heldout_use": l2["heldout_use"], "taxonomy_version": l2["taxonomy_version"],
             "frozen_fields": list(FROZEN), "changed_frozen_fields": [], "l0_spec_sha256": hashlib.sha256(l0_path.read_bytes()).hexdigest(),
             "l2_spec_sha256": hashlib.sha256(l2_path.read_bytes()).hexdigest(), "task_count": 5, "episode_count": len(rows),
             "boundary": "L2 results are report-only and failure labels are behavioral, not internal causes"}
    return rows, guard


def write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--task-table", type=Path, required=True)
    p.add_argument("--l0-spec", type=Path, required=True); p.add_argument("--l2-spec", type=Path, required=True)
    p.add_argument("--registry", type=Path, required=True); p.add_argument("--guard", type=Path, required=True)
    args = p.parse_args(); rows, guard = derive(args.task_table, args.l0_spec, args.l2_spec); write(args.registry, rows)
    args.guard.parent.mkdir(parents=True, exist_ok=True); args.guard.write_text(json.dumps(guard, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: L2 tasks=5 episodes={len(rows)} frozen_changes=0 strong_ood=true")


if __name__ == "__main__": main()
