#!/usr/bin/env python3
"""把 Day 6/7 锁定模型计划展开为 2×3×5×5=150 个 planned episodes。"""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"


def read_manifest(path: Path, source_kind: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("source_kind") != source_kind or data.get("upstream_commit") != LOCKED:
        raise ValueError(f"模型 manifest 不是锁定静态计划：{path}")
    if data.get("real_model_run") is not False: raise ValueError("输入 manifest 不得冒充真实结果")
    return data


def build(matrix_path: Path, smol_path: Path, open_path: Path) -> dict:
    cfg = json.loads(matrix_path.read_text(encoding="utf-8"))
    smol = read_manifest(smol_path, "locked_source_static_pilot_plan")
    openvla = read_manifest(open_path, "locked_source_static_openvla_plan")
    if cfg["levels"] != [0, 1, 2] or cfg["task_ids"] != [0, 1, 2, 3, 4]:
        raise ValueError("pilot 必须覆盖 L0/L1/L2 各 5 个 task")
    if len(cfg["seeds"]) != 5 or len(set(cfg["seeds"])) != 5 or len(cfg["init_state_indices"]) != 5:
        raise ValueError("每个 level/task 必须有 5 个不同 seed/init")
    models = [("SmolVLA", smol), ("OpenVLA", openvla)]; episodes = []
    for (model, manifest), (level, task_id, pair_index) in product(
        models, product(cfg["levels"], cfg["task_ids"], range(5))
    ):
        seed, init_index = cfg["seeds"][pair_index], cfg["init_state_indices"][pair_index]
        episodes.append({"episode_id": f"{model.lower()}-L{level}-T{task_id}-S{seed}-I{init_index}",
            "model": model, "checkpoint_repo": manifest["checkpoint_repo"],
            "checkpoint_revision": manifest["checkpoint_revision"], "upstream_commit": LOCKED,
            "suite": cfg["suite"], "level": level, "task_id": task_id, "seed": seed,
            "init_state_index": init_index, "max_steps": cfg["max_steps"],
            "instruction_replacement": cfg["instruction_replacement"], "status": "planned",
            "real_model_run": False, "source_kind": "locked_static_matrix_plan"})
    if len(episodes) != 150 or len({row["episode_id"] for row in episodes}) != 150:
        raise ValueError("矩阵必须包含 150 个唯一 episode")
    return {"schema_version": 1, "upstream_commit": LOCKED, "models": [m for m, _ in models],
            "episodes_per_model": 75, "total_episodes": 150, "selection_uses_levels": [0],
            "l1_l2_role": "preregistered research-cut pilot only; never checkpoint/model selection",
            "status": "planned", "real_model_runs": 0, "episodes": episodes}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--matrix-config", type=Path, required=True)
    p.add_argument("--smolvla-manifest", type=Path, required=True); p.add_argument("--openvla-manifest", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True); args = p.parse_args()
    data = build(args.matrix_config, args.smolvla_manifest, args.openvla_manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("PASS: 150 planned episodes; real model runs=0"); print(f"Saved: {args.output}")


if __name__ == "__main__": main()
