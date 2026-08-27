#!/usr/bin/env python3
"""按锁定源码验收 Day 1 系统地图与 SmolVLA 独立挑战。"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

try:
    from .build_project_map import build_map
except ImportError:
    from build_project_map import build_map


def top_level_symbols(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {node.name for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef))}


def check(upstream: Path, project_map: Path, challenge: Path) -> None:
    expected_map = build_map(upstream)
    actual_map = json.loads(project_map.read_text(encoding="utf-8"))
    if actual_map != expected_map:
        raise ValueError("project_map 必须由当前锁定 checkout 生成，不能手填或改 commit")
    evaluator = upstream / "vla_arena/models/smolvla/evaluator.py"
    config = upstream / "vla_arena/configs/evaluation/smolvla.yaml"
    symbols = top_level_symbols(evaluator)
    required_hooks = ["initialize_model", "run_episode", "run_task", "main"]
    expected_challenge = {
        "model": "smolvla", "evaluator": str(evaluator.relative_to(upstream)),
        "config": str(config.relative_to(upstream)), "config_class": "Args",
        "hooks": required_hooks, "requires_gpu": True,
        "source_kind": "locked_upstream_static_map",
    }
    if not set(required_hooks + ["Args"]).issubset(symbols):
        raise ValueError("锁定 SmolVLA evaluator 的符号契约发生变化")
    if json.loads(challenge.read_text(encoding="utf-8")) != expected_challenge:
        raise ValueError("SmolVLA 挑战必须按真实新文件生成，不能复制 random 节点后改模型名")
    print("PASS: Day 1 locked map and changed-adapter challenge")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--project-map", type=Path, required=True)
    parser.add_argument("--challenge", type=Path, required=True)
    args = parser.parse_args()
    check(args.upstream.resolve(), args.project_map, args.challenge)


if __name__ == "__main__":
    main()
