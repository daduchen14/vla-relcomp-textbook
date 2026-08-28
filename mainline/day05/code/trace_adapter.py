#!/usr/bin/env python3
"""静态提取锁定 SmolVLA evaluator 的模型接口契约。"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
EVALUATOR = "vla_arena/models/smolvla/evaluator.py"
INPUT_KEYS = ["observation.images.image", "observation.images.wrist_image", "observation.state", "task"]


def git_text(root: Path, path: str) -> str:
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=root, check=True,
                          text=True, capture_output=True).stdout


def build_contract(root: Path) -> dict:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          text=True, capture_output=True).stdout.strip()
    if head != LOCKED: raise ValueError("upstream 不是锁定 commit")
    source = git_text(root, EVALUATOR); tree = ast.parse(source)
    symbols = {node.name: node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef))}
    if not {"Args", "initialize_model", "run_episode", "main"}.issubset(symbols):
        raise ValueError("SmolVLA 顶层接口发生变化")
    episode = symbols["run_episode"]
    strings = {node.value for node in ast.walk(episode) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    calls = {ast.unparse(node.func) for node in ast.walk(episode) if isinstance(node, ast.Call)}
    if not set(INPUT_KEYS).issubset(strings): raise ValueError("observation 输入 key 发生变化")
    if not {"torch.inference_mode", "policy.select_action", "env.step"}.issubset(calls):
        raise ValueError("inference/action/step 调用契约发生变化")
    return {"commit": LOCKED, "evaluator": EVALUATOR, "config_class": "Args",
            "initialize_model": "SmolVLAPolicy.from_pretrained → to(device) → eval",
            "input_keys": INPUT_KEYS, "image_contract": "uint8 HWC → /255 → CHW float32 → device → batch",
            "state_contract": "eef_pos(3) + quat_to_axis_angle(3) + gripper_qpos(2) → float32 → batch",
            "inference_context": "torch.inference_mode", "policy_call": "policy.select_action(observation)",
            "action_to_env": "action_tensor.cpu().numpy()[0] → env.step(action)",
            "source_kind": "locked_upstream_static_contract", "real_model_loaded": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); contract = build_contract(args.upstream.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n")
    print("PASS: locked SmolVLA input/output contract")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
