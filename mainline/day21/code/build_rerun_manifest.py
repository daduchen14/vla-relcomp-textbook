#!/usr/bin/env python3
"""从已冻结的 episode registry 预注册 original/repeat 配对重跑。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from mainline.day18.code.build_l0_registry import ident
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from mainline.day18.code.build_l0_registry import ident

FIELDS = (
    "rerun_pair_id", "execution_id", "replicate", "selection_name", "selection_rule",
    "source_episode_id", "run_id", "level", "task_id", "trial_id", "seed",
    "init_state_index", "task_name", "bddl_path", "model_id", "model_revision",
    "protocol_lock_sha256", "status", "success", "source_kind",
)
FROZEN = (
    "source_episode_id", "run_id", "level", "task_id", "trial_id", "seed",
    "init_state_index", "task_name", "bddl_path", "model_id", "model_revision",
    "protocol_lock_sha256",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build(registry_path: Path, selection_path: Path) -> list[dict[str, str]]:
    registry = read_csv(registry_path)
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    required = {"selection_name", "selection_rule", "selectors", "source_kind"}
    if not required.issubset(selection):
        raise ValueError("selection 缺少必需字段")
    if selection["selection_rule"] != "pre_registered_boundary_tasks_not_result_cherry_pick":
        raise ValueError("必须预注册选择规则，禁止按结果挑选")
    selectors = selection["selectors"]
    keys = [(item.get("task_id"), item.get("trial_id")) for item in selectors]
    if not keys or len(keys) != len(set(keys)):
        raise ValueError("selectors 必须非空且 task_id/trial_id 唯一")

    rows: list[dict[str, str]] = []
    for task_id, trial_id in keys:
        matches = [row for row in registry if row.get("task_id") == str(task_id) and row.get("trial_id") == str(trial_id)]
        if len(matches) != 1:
            raise ValueError(f"selector 必须唯一匹配 source episode：task={task_id}, trial={trial_id}")
        source = matches[0]
        missing = [name for name in FROZEN[1:] if not source.get(name)]
        if missing:
            raise ValueError(f"source registry 冻结字段缺失：{missing}")
        pair_id = ident("rerun-pair-", {"episode_id": source["episode_id"], "selection": selection["selection_name"]})
        for replicate in ("original", "repeat"):
            execution_id = ident("rerun-exec-", {"pair_id": pair_id, "replicate": replicate})
            row = {
                "rerun_pair_id": pair_id,
                "execution_id": execution_id,
                "replicate": replicate,
                "selection_name": selection["selection_name"],
                "selection_rule": selection["selection_rule"],
                "source_episode_id": source["episode_id"],
                **{name: source[name] for name in FROZEN[1:]},
                "status": "PLANNED",
                "success": "",
                "source_kind": selection["source_kind"],
            }
            rows.append(row)
    return rows


def write(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = build(args.registry, args.selection)
    write(args.output, rows)
    print(f"PASS: rerun_pairs={len(rows) // 2} executions={len(rows)} frozen_fields={len(FROZEN)}")


if __name__ == "__main__":
    main()
