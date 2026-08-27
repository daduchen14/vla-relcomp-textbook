#!/usr/bin/env python3
"""从锁定 SmolVLA 源码和单任务配置生成不冒充运行结果的 pilot manifest。"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
EVALUATOR = "vla_arena/models/smolvla/evaluator.py"
SMOL_CONFIG = "vla_arena/models/smolvla/src/lerobot/policies/smolvla/configuration_smolvla.py"
YAML = "vla_arena/configs/evaluation/smolvla.yaml"
SUITE = "extrapolation_preposition_combinations"
REQUIRED = {"form", "checkpoint_repo", "checkpoint_revision", "suite", "level", "task_id",
            "seed", "init_state_index", "num_trials", "max_steps", "device"}


def git_text(root: Path, path: str) -> str:
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=root, check=True,
                          text=True, capture_output=True).stdout


def locked_contract(root: Path) -> dict:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          text=True, capture_output=True).stdout.strip()
    if head != LOCKED:
        raise ValueError(f"upstream 必须位于锁定 commit {LOCKED}")
    evaluator, config, yaml = git_text(root, EVALUATOR), git_text(root, SMOL_CONFIG), git_text(root, YAML)
    calls = {ast.unparse(n.func) for n in ast.walk(ast.parse(evaluator)) if isinstance(n, ast.Call)}
    for call in ("SmolVLAPolicy.from_pretrained", "policy.to", "policy.eval",
                 "policy.select_action", "env.step"):
        if call not in calls:
            raise ValueError(f"锁定 evaluator 缺少调用：{call}")
    values = {}
    klass = next(n for n in ast.parse(config).body if isinstance(n, ast.ClassDef) and n.name == "SmolVLAConfig")
    for node in klass.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id in {"n_obs_steps", "chunk_size", "n_action_steps", "vlm_model_name"}:
                values[node.target.id] = ast.literal_eval(node.value)
    if values != {"n_obs_steps": 1, "chunk_size": 50, "n_action_steps": 50,
                  "vlm_model_name": "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"}:
        raise ValueError(f"SmolVLA 默认契约变化：{values}")
    if not re.search(r"policy_path:\s*[\"']?VLA-Arena/smolvla-vla-arena[\"']?", yaml):
        raise ValueError("锁定 YAML 默认 checkpoint 发生变化")
    return {"commit": LOCKED, "evaluator": EVALUATOR, "model_config": SMOL_CONFIG,
            "evaluation_config": YAML, **values}


def build_manifest(root: Path, config_path: Path) -> dict:
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    missing = REQUIRED - set(cfg)
    if missing:
        raise ValueError(f"pilot config 缺字段：{sorted(missing)}")
    if cfg["suite"] != SUITE or cfg["level"] != 0 or not 0 <= cfg["task_id"] < 5:
        raise ValueError("Day 6 只允许目标 suite 的一个 L0 task")
    if cfg["num_trials"] != 1 or cfg["max_steps"] != 300 or cfg["device"] != "cuda":
        raise ValueError("最小 pilot 必须是 1 trial、300 max_steps、cuda")
    if not re.fullmatch(r"[0-9a-f]{40}", cfg["checkpoint_revision"]):
        raise ValueError("checkpoint_revision 必须是 40 位不可变 commit")
    contract = locked_contract(root)
    return {"schema_version": 1, "pilot_id": f"smolvla-{cfg['form']}-L0-T{cfg['task_id']}-S{cfg['seed']}",
            **cfg, "upstream_commit": LOCKED, "locked_contract": contract,
            "expected_evidence": ["preflight.json", "episode_registry.csv", "episode.log", "rollout.mp4"],
            "status": "planned", "real_model_run": False,
            "source_kind": "locked_source_static_pilot_plan"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_manifest(args.upstream.resolve(), args.config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: locked SmolVLA pilot plan (real model not run)")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
