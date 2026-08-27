#!/usr/bin/env python3
"""用 CPU fixture 练习 goal 名称→对象状态→关系快照，不冒充 MuJoCo。"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def _vec(value: object, length: int, field: str) -> list[float]:
    if not isinstance(value, list) or len(value) != length:
        raise ValueError(f"{field} 必须是 {length} 维列表")
    result = [float(item) for item in value]
    if not all(math.isfinite(item) for item in result):
        raise ValueError(f"{field} 出现 NaN/Inf")
    return result


def _task(table: dict, level: int, task_id: int) -> dict:
    rows = [row for row in table["tasks"] if row["level"] == level and row["task_id"] == task_id]
    if len(rows) != 1:
        raise ValueError("task selector 必须命中 Day 9 表中的唯一 task")
    row = rows[0]
    if row["goal_predicate"][0].lower() != "on":
        raise ValueError("Day 11 只处理目标 suite 的 On goal")
    return row


def snapshot(table_path: Path, fixture_path: Path) -> dict:
    table = json.loads(table_path.read_text(encoding="utf-8"))
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    selector = fixture["task_selector"]
    row = _task(table, int(selector["level"]), int(selector["task_id"]))
    target, reference = row["target_object"], row["reference_object"]
    objects = fixture["objects"]
    missing = [name for name in (target, reference) if name not in objects]
    if missing:
        raise ValueError(f"fixture 缺少 goal 对象：{missing}")
    target_data, reference_data = objects[target], objects[reference]
    target_pos = _vec(target_data["pos"], 3, f"{target}.pos")
    reference_pos = _vec(reference_data["pos"], 3, f"{reference}.pos")
    target_quat = _vec(target_data["quat_wxyz"], 4, f"{target}.quat_wxyz")
    reference_quat = _vec(reference_data["quat_wxyz"], 4, f"{reference}.quat_wxyz")
    if target_data["body_id"] == reference_data["body_id"]:
        raise ValueError("target/reference body_id 冲突")
    contact_pairs = {frozenset(pair) for pair in fixture["contacts"]}
    contact = frozenset((target, reference)) in contact_pairs
    dx, dy = target_pos[0] - reference_pos[0], target_pos[1] - reference_pos[1]
    xy_distance = math.hypot(dx, dy)
    return {
        "commit": table["commit"], "suite": table["suite"], "level": row["level"],
        "task_id": row["task_id"], "task_name": row["task_name"], "goal_predicate": row["goal_predicate"],
        "target": target, "reference": reference,
        "target_state": {"body_id": int(target_data["body_id"]), "pos": target_pos, "quat_wxyz": target_quat},
        "reference_state": {"body_id": int(reference_data["body_id"]), "pos": reference_pos, "quat_wxyz": reference_quat},
        "relation_state": {"target_minus_reference_z": target_pos[2] - reference_pos[2],
                           "xy_distance": xy_distance, "contact": contact,
                           "on_by_locked_formula": reference_pos[2] <= target_pos[2]
                           and contact and xy_distance < 0.07},
        "distractor_count": len(objects) - 2,
        "visibility": "privileged_evaluator_state_not_policy_input",
        "source_kind": fixture["source_kind"], "real_environment_run": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-table", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); result = snapshot(args.task_table, args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: L{result['level']}T{result['task_id']} {result['target']}→{result['reference']}; real environment run=false")


if __name__ == "__main__":
    main()
