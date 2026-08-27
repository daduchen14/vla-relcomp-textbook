#!/usr/bin/env python3
"""从锁定 checkout 生成 VLA-RelComp 最小系统地图。"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
SUITE = "extrapolation_preposition_combinations"
FILES = {
    "config": "vla_arena/configs/evaluation/random.yaml",
    "evaluator": "vla_arena/models/random/evaluator.py",
    "registry": "vla_arena/vla_arena/benchmark/__init__.py",
    "task_map": "vla_arena/vla_arena/benchmark/vla_arena_suite_task_map.py",
    "tasks": "vla_arena/vla_arena/bddl_files/extrapolation_preposition_combinations",
    "environment": "vla_arena/vla_arena/envs/bddl_base_domain.py",
    "success": "vla_arena/vla_arena/utils/eval_cost.py",
}
ROLES = {
    "config": "选择模型、suite、level 与运行参数",
    "evaluator": "加载配置并驱动 task/episode loop",
    "registry": "把 registry 名称注册为 benchmark class",
    "task_map": "列出 L0/L1/L2 每级五个任务",
    "tasks": "保存声明式 CBDDL/BDDL 任务文件",
    "environment": "执行 action 并计算 observation/done/info",
    "success": "从 info 中解释 episode 是否成功",
}
EDGES = [
    ["config", "evaluator", "配置输入"], ["evaluator", "registry", "按 suite 名查找"],
    ["registry", "task_map", "按 level 构造 Task"], ["task_map", "tasks", "映射 BDDL 文件"],
    ["evaluator", "environment", "env.step(action)"], ["environment", "success", "info['success']"],
]


def git_head(root: Path) -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          text=True, capture_output=True).stdout.strip()


def build_map(root: Path) -> dict:
    head = git_head(root)
    if head != LOCKED:
        raise ValueError(f"锁定版本不匹配：{head}")
    missing = [path for path in FILES.values() if not (root / path).exists()]
    if missing:
        raise FileNotFoundError(f"缺少系统地图节点：{missing}")
    registry = (root / FILES["registry"]).read_text(encoding="utf-8")
    task_map = (root / FILES["task_map"]).read_text(encoding="utf-8")
    evaluator = (root / FILES["evaluator"]).read_text(encoding="utf-8")
    for label, source in ((SUITE, registry), (SUITE, task_map), ("run_episode", evaluator)):
        if label not in source:
            raise ValueError(f"锁定源码缺少契约：{label}")
    return {
        "source_kind": "locked_upstream_static_map",
        "repository": "https://github.com/PKU-Alignment/VLA-Arena.git",
        "commit": head, "suite_registry_name": SUITE,
        "nodes": [{"id": key, "path": path, "role": ROLES[key]} for key, path in FILES.items()],
        "edges": [{"from": start, "to": end, "meaning": meaning} for start, end, meaning in EDGES],
        "not_executed": ["MuJoCo", "VLA model", "GPU episode"],
    }


def markdown(payload: dict) -> str:
    lines = ["# VLA-RelComp minimal system map", "", f"- commit: `{payload['commit']}`",
             f"- suite: `{payload['suite_registry_name']}`", "", "```mermaid", "flowchart LR"]
    for node in payload["nodes"]:
        lines.append(f"  {node['id']}[{node['id']}: {node['path']}]")
    for edge in payload["edges"]:
        lines.append(f"  {edge['from']} -->|{edge['meaning']}| {edge['to']}")
    lines += ["```", "", "此图来自锁定源码静态检查；没有运行 MuJoCo、模型或 GPU episode。", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("learner_outputs/mainline/day01"))
    args = parser.parse_args()
    payload = build_map(args.upstream.resolve())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "project_map.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    (args.output_dir / "project_map.md").write_text(markdown(payload), encoding="utf-8")
    print(f"PASS: {payload['commit']} / {payload['suite_registry_name']}")
    print(f"Saved: {args.output_dir / 'project_map.md'}")


if __name__ == "__main__":
    main()
