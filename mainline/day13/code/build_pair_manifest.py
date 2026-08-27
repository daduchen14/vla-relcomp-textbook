#!/usr/bin/env python3
"""从 Day 9 task table 和 pair spec 生成两行匹配反事实 manifest。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path

FIELDS = ("pair_id", "pair_name", "arm", "run_order", "changed_factor", "suite", "level",
          "task_id", "task_name", "bddl_path", "seed", "init_state_index", "model_id",
          "model_revision", "inference_config_sha256", "target_object", "reference_object",
          "relation", "goal_predicate_json", "instruction_text", "semantic_equivalence_review",
          "source_kind", "real_environment_run")
FIXED = ("pair_name", "changed_factor", "suite", "level", "task_id", "task_name", "bddl_path",
         "seed", "init_state_index", "model_id", "model_revision", "inference_config_sha256",
         "target_object", "reference_object", "relation", "goal_predicate_json",
         "semantic_equivalence_review", "source_kind", "real_environment_run")


def _task(table: dict, selector: dict) -> dict:
    rows = [row for row in table["tasks"] if row["level"] == selector["level"]
            and row["task_id"] == selector["task_id"]]
    if len(rows) != 1: raise ValueError("task selector 必须唯一命中 Day 9 表")
    return rows[0]


def pair_id(a: dict, b: dict) -> str:
    # CSV 读回后所有值都是字符串；先归一化，保证 ID 可跨写入/读取重算。
    payload = {key: str(a[key]) for key in FIXED}
    payload.update({"instruction_a": str(a["instruction_text"]),
                    "instruction_b": str(b["instruction_text"])})
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"pair-{digest[:16]}"


def build(table_path: Path, spec_path: Path) -> list[dict]:
    table = json.loads(table_path.read_text(encoding="utf-8")); spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("factor") != "instruction_surface": raise ValueError("Day 13 只允许 instruction_surface")
    row = _task(table, spec["task_selector"]); instruction_a = row["language"].strip()
    instruction_b = spec["instruction_b"].strip()
    if not instruction_a or not instruction_b or instruction_a.casefold() == instruction_b.casefold():
        raise ValueError("A/B instruction 必须非空且表述不同")
    config_hash = spec["inference_config_sha256"]
    if len(config_hash) != 64 or any(ch not in "0123456789abcdef" for ch in config_hash):
        raise ValueError("inference_config_sha256 必须是 64 位小写十六进制")
    base = {"pair_name": spec["pair_name"], "changed_factor": spec["factor"],
            "suite": table["suite"], "level": row["level"], "task_id": row["task_id"],
            "task_name": row["task_name"], "bddl_path": row["bddl_path"], "seed": spec["seed"],
            "init_state_index": spec["init_state_index"], "model_id": spec["model_id"],
            "model_revision": spec["model_revision"], "inference_config_sha256": config_hash,
            "target_object": row["target_object"], "reference_object": row["reference_object"],
            "relation": row["goal_relation"],
            "goal_predicate_json": json.dumps(row["goal_predicate"], ensure_ascii=False, separators=(",", ":")),
            "semantic_equivalence_review": "pending_human_review", "source_kind": spec["source_kind"],
            "real_environment_run": "false"}
    arms = [{**base, "arm": "A", "instruction_text": instruction_a},
            {**base, "arm": "B", "instruction_text": instruction_b}]
    order = ["A", "B"]; random.Random(spec["order_seed"]).shuffle(order)
    order_map = {arm: index + 1 for index, arm in enumerate(order)}
    for arm in arms: arm["run_order"] = order_map[arm["arm"]]
    identifier = pair_id(arms[0], arms[1])
    for arm in arms: arm["pair_id"] = identifier
    return [{key: arm[key] for key in FIELDS} for arm in arms]


def write_csv(rows: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--task-table", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); rows = build(args.task_table, args.spec); write_csv(rows, args.output)
    print(f"PASS: {rows[0]['pair_id']} two matched arms; run order="
          + ",".join(f"{row['arm']}:{row['run_order']}" for row in rows)
          + "; real environment run=false")


if __name__ == "__main__": main()
