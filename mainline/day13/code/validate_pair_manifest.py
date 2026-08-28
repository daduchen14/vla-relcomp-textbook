#!/usr/bin/env python3
"""验证一个 instruction-surface pair 只改变指令文本。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from .build_pair_manifest import FIELDS, FIXED, pair_id
except ImportError:
    from build_pair_manifest import FIELDS, FIXED, pair_id


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def validate(path: Path, table_path: Path) -> dict:
    rows = read_rows(path)
    if len(rows) != 2 or set(rows[0]) != set(FIELDS): raise ValueError("manifest 必须恰有两行和冻结字段")
    by_arm = {row["arm"]: row for row in rows}
    if set(by_arm) != {"A", "B"}: raise ValueError("必须各有一个 A/B arm")
    a, b = by_arm["A"], by_arm["B"]
    if a["pair_id"] != b["pair_id"]: raise ValueError("两臂 pair_id 不一致")
    if any(a[key] != b[key] for key in FIXED): raise ValueError("除 instruction/run order 外存在未声明变化")
    if a["instruction_text"].casefold() == b["instruction_text"].casefold(): raise ValueError("instruction 没有变化")
    if {a["run_order"], b["run_order"]} != {"1", "2"}: raise ValueError("run_order 必须恰为 1/2")
    if a["changed_factor"] != "instruction_surface" or a["real_environment_run"] != "false":
        raise ValueError("factor/source 状态不合法")
    if a["pair_id"] != pair_id(a, b): raise ValueError("pair_id 与匹配键/指令不一致")
    table = json.loads(table_path.read_text(encoding="utf-8"))
    candidates = [row for row in table["tasks"] if str(row["level"]) == a["level"]
                  and str(row["task_id"]) == a["task_id"]]
    if len(candidates) != 1: raise ValueError("manifest task 不在 Day 9 表")
    task = candidates[0]
    exact = {"suite": table["suite"], "task_name": task["task_name"], "bddl_path": task["bddl_path"],
             "target_object": task["target_object"], "reference_object": task["reference_object"],
             "relation": task["goal_relation"], "goal_predicate_json": json.dumps(task["goal_predicate"],
             ensure_ascii=False, separators=(",", ":")), "instruction_text": task["language"]}
    if any(a[key] != value for key, value in exact.items()): raise ValueError("A arm 未精确锚定锁定 task table")
    return {"pair_id": a["pair_id"], "changed_fields": ["instruction_text"],
            "fixed_field_count": len(FIXED), "semantic_equivalence_review": a["semantic_equivalence_review"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--task-table", type=Path, required=True); parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(); result = validate(args.manifest, args.task_table); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {result['pair_id']} only changed instruction_text; semantic review pending")


if __name__ == "__main__": main()
