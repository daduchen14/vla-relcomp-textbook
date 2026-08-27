#!/usr/bin/env python3
"""由锁定 task table 构造 control/language-oracle 配对计划。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

FIELDS = ("oracle_pair_id", "pilot_name", "arm", "intervention", "suite", "level", "task_id",
          "task_name", "bddl_path", "seed", "init_state_index", "model_id", "model_revision",
          "inference_config_sha256", "target_object", "reference_object", "relation",
          "instruction_text", "privileged_info_used", "allowed_use", "source_kind", "real_environment_run")


def structured_instruction(row: dict) -> str:
    start = " ".join(row["target_initial_predicate"] or ["UNKNOWN"])
    return (f"目标={row['target_object']}；起始关系={start}；动作=pick-and-place；"
            f"终止关系={row['goal_relation']}；参照物={row['reference_object']}")


def build(table_path: Path, spec_path: Path) -> list[dict]:
    table = json.loads(table_path.read_text(encoding="utf-8")); spec = json.loads(spec_path.read_text(encoding="utf-8"))
    selector = spec["task_selector"]
    matches = [row for row in table["tasks"] if row["level"] == selector["level"] and row["task_id"] == selector["task_id"]]
    if len(matches) != 1: raise ValueError("task selector 必须唯一命中")
    task = matches[0]; config_hash = spec["inference_config_sha256"]
    if len(config_hash) != 64 or any(ch not in "0123456789abcdef" for ch in config_hash):
        raise ValueError("inference config hash 非法")
    trials = spec.get("trials", [])
    if not trials or len({(row["seed"], row["init_state_index"]) for row in trials}) != len(trials):
        raise ValueError("trials 必须非空且 seed/init 不重复")
    rows = []
    for trial in trials:
        key = {"pilot": spec["pilot_name"], "suite": table["suite"], "level": task["level"],
               "task_id": task["task_id"], "seed": trial["seed"], "init": trial["init_state_index"],
               "model": spec["model_id"], "revision": spec["model_revision"], "config": config_hash}
        identifier = "oracle-" + hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:16]
        base = {"oracle_pair_id": identifier, "pilot_name": spec["pilot_name"], "suite": table["suite"],
                "level": task["level"], "task_id": task["task_id"], "task_name": task["task_name"],
                "bddl_path": task["bddl_path"], "seed": trial["seed"],
                "init_state_index": trial["init_state_index"], "model_id": spec["model_id"],
                "model_revision": spec["model_revision"], "inference_config_sha256": config_hash,
                "target_object": task["target_object"], "reference_object": task["reference_object"],
                "relation": task["goal_relation"], "privileged_info_used": "bddl_goal_and_init",
                "allowed_use": "diagnostic_oracle_only_not_final_method", "source_kind": spec["source_kind"],
                "real_environment_run": "false"}
        rows += [{**base, "arm": "control", "intervention": "none", "instruction_text": task["language"]},
                 {**base, "arm": "oracle", "intervention": "language_oracle",
                  "instruction_text": structured_instruction(task)}]
    return [{key: row[key] for key in FIELDS} for row in rows]


def write_csv(rows: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--task-table", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); rows = build(args.task_table, args.spec); write_csv(rows, args.output)
    print(f"PASS: {len(rows)//2} control/oracle pairs planned; privileged diagnostic only; real run=false")


if __name__ == "__main__": main()
