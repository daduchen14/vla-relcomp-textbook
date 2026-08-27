#!/usr/bin/env python3
"""从锁定 OpenVLA evaluator 生成单任务静态 pilot manifest。"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
SUITE = "extrapolation_preposition_combinations"
EVALUATOR = "vla_arena/models/openvla/evaluator.py"
UTILS = "vla_arena/models/openvla/experiments/robot/openvla_utils.py"
ROBOT = "vla_arena/models/openvla/experiments/robot/robot_utils.py"
MODEL = "vla_arena/models/openvla/prismatic/extern/hf/modeling_prismatic.py"
CONFIG = "vla_arena/models/openvla/prismatic/extern/hf/configuration_prismatic.py"
YAML = "vla_arena/configs/evaluation/openvla.yaml"
CONTROL_FIELDS = ["suite", "level", "task_id", "seed", "init_state_index", "num_trials", "max_steps"]


def git_text(root: Path, path: str) -> str:
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=root, check=True,
                          text=True, capture_output=True).stdout


def call_names(source: str) -> set[str]:
    return {ast.unparse(node.func) for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Call)}


def locked_contract(root: Path) -> dict:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          text=True, capture_output=True).stdout.strip()
    if head != LOCKED: raise ValueError("upstream 不是锁定 commit")
    evaluator, utils, robot = git_text(root, EVALUATOR), git_text(root, UTILS), git_text(root, ROBOT)
    model, config, yaml = git_text(root, MODEL), git_text(root, CONFIG), git_text(root, YAML)
    required = {
        EVALUATOR: {"get_action", "process_action", "env.step"},
        UTILS: {"processor", "vla.predict_action"},
        MODEL: {"self.generate", "np.clip", "self.get_action_stats"},
    }
    for path, expected in required.items():
        source = {EVALUATOR: evaluator, UTILS: utils, MODEL: model}[path]
        missing = expected - call_names(source)
        if missing: raise ValueError(f"{path} 缺少真实调用：{sorted(missing)}")
    if "assert action.shape == (ACTION_DIM,)" not in robot or "ACTION_DIM = 7" not in robot:
        raise ValueError("OpenVLA 7 维动作断言变化")
    if not re.search(r"n_action_bins:\s*int\s*=\s*256", config):
        raise ValueError("OpenVLA action bins 变化")
    if "VLA-Arena/openvla-7b-finetuned-vla-arena" not in yaml or "unnorm_key: \"vla_arena_l0_l\"" not in yaml:
        raise ValueError("OpenVLA YAML checkpoint/unnorm_key 变化")
    return {"commit": LOCKED, "evaluator": EVALUATOR, "action_decoder": MODEL,
            "checkpoint_loader": UTILS, "action_bins": 256, "action_dim": 7,
            "policy_input": "agentview RGB + language prompt (prepared state is not passed to predict_action)",
            "decode": "generated action token ids → bin centers → q01/q99 unnormalize → 7D continuous action",
            "gripper": "[0,1] → sign in [-1,+1] → invert for OpenVLA",
            "loop": "get_action → process_action → env.step(action.tolist())"}


def build_manifest(root: Path, config_path: Path) -> dict:
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    required = {"form", "model_family", "checkpoint_repo", "checkpoint_revision", "unnorm_key",
                "center_crop", "quantization", *CONTROL_FIELDS}
    if required - set(cfg): raise ValueError(f"缺字段：{sorted(required - set(cfg))}")
    if cfg["model_family"] != "openvla" or cfg["suite"] != SUITE or cfg["level"] != 0:
        raise ValueError("Day 7 只允许目标 suite 的 L0 OpenVLA")
    if not 0 <= cfg["task_id"] < 5 or cfg["num_trials"] != 1 or cfg["max_steps"] != 300:
        raise ValueError("最小 pilot 必须是单个合法 task、1 trial、300 steps")
    if cfg["quantization"] != "none" or not cfg["center_crop"] or cfg["unnorm_key"] != "vla_arena_l0_l":
        raise ValueError("Day 7 首次比较固定 BF16/no quantization、center crop 和 L0 unnorm key")
    if not re.fullmatch(r"[0-9a-f]{40}", cfg["checkpoint_revision"]):
        raise ValueError("checkpoint_revision 必须是 40 位 commit")
    return {"schema_version": 1, "pilot_id": f"openvla-{cfg['form']}-L0-T{cfg['task_id']}-S{cfg['seed']}",
            **cfg, "upstream_commit": LOCKED, "locked_contract": locked_contract(root),
            "expected_evidence": ["preflight.json", "episode_registry.csv", "episode.log", "rollout.mp4"],
            "status": "planned", "real_model_run": False, "source_kind": "locked_source_static_openvla_plan"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True); parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True); args = parser.parse_args()
    payload = build_manifest(args.upstream.resolve(), args.config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: locked OpenVLA plan (real model not run)"); print(f"Saved: {args.output}")


if __name__ == "__main__": main()
