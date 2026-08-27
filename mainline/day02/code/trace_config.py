#!/usr/bin/env python3
"""沿锁定 CLI/YAML/evaluator/registry 生成 15-task 只读 manifest。"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import tomllib
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
SUITE = "extrapolation_preposition_combinations"
TASK_MAP_PATH = "vla_arena/vla_arena/benchmark/vla_arena_suite_task_map.py"
CLI_CHAIN = [
    {"path": "pyproject.toml", "symbol": "project.scripts.vla-arena"},
    {"path": "vla_arena/cli/main.py", "symbol": "main"},
    {"path": "vla_arena/cli/eval.py", "symbol": "eval_main"},
    {"path": "vla_arena/config_paths.py", "symbol": "resolve_config_path"},
    {"path": "vla_arena/models/random/evaluator.py", "symbol": "_parse_cfg"},
    {"path": "vla_arena/models/random/evaluator.py", "symbol": "main"},
    {"path": "vla_arena/vla_arena/benchmark/__init__.py", "symbol": "get_benchmark_dict"},
]


def parse_scalar(text: str):
    value = text.split("#", 1)[0].strip().strip('"').strip("'")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try: return int(value)
    except ValueError: return value


def parse_simple_yaml(path: Path) -> dict:
    result = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        clean = line.strip()
        if not clean or clean.startswith("#"): continue
        if ":" not in clean: raise ValueError(f"YAML line {number} 缺少冒号")
        key, value = clean.split(":", 1)
        result[key.strip()] = parse_scalar(value)
    return result


def git_head(root: Path) -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          text=True, capture_output=True).stdout.strip()


def git_blob(root: Path, path: str) -> str:
    # 对稀疏 checkout 也有效：读取 commit blob，而非假设文件已展开。
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=root, check=True,
                          text=True, capture_output=True).stdout


def git_object_exists(root: Path, path: str) -> None:
    # init state 是二进制 pickle；这里只验证 blob 存在，避免错误按 UTF-8 解码。
    subprocess.run(["git", "cat-file", "-e", f"HEAD:{path}"], cwd=root,
                   check=True, capture_output=True)


def extract_task_map(source: str) -> dict:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "vla_arena_task_map" for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError("找不到 vla_arena_task_map")


def build_artifacts(root: Path, config_path: Path) -> tuple[dict, dict]:
    if git_head(root) != LOCKED: raise ValueError("upstream 不是锁定 commit")
    config = parse_simple_yaml(config_path)
    if config.get("task_suite_name") != SUITE: raise ValueError("配置没有选择目标 registry 名")
    pyproject = tomllib.loads(git_blob(root, "pyproject.toml"))
    if pyproject["project"]["scripts"]["vla-arena"] != "vla_arena.cli.main:main":
        raise ValueError("CLI entry point 发生变化")
    sources = {item["path"]: git_blob(root, item["path"]) for item in CLI_CHAIN}
    required = ["eval_main", "resolve_config_path", "_parse_cfg", "get_benchmark_dict"]
    if any(word not in "\n".join(sources.values()) for word in required):
        raise ValueError("CLI→evaluator 调用链契约不完整")
    task_map = extract_task_map(git_blob(root, TASK_MAP_PATH))[SUITE]
    tasks = []
    for level in (0, 1, 2):
        if len(task_map[level]) != 5: raise ValueError(f"L{level} 不是五个任务")
        for level_id, name in enumerate(task_map[level]):
            bddl = f"vla_arena/vla_arena/bddl_files/{SUITE}/level_{level}/{name}.bddl"
            init = f"vla_arena/vla_arena/init_files/{SUITE}/level_{level}/{name}.pruned_init"
            git_object_exists(root, bddl); git_object_exists(root, init)
            tasks.append({"level": level, "level_id": level_id, "task_name": name,
                          "bddl_path": bddl, "init_path": init})
    trace = {"source_kind": "locked_upstream_static_trace", "commit": LOCKED,
             "config_path": str(config_path), "config": config, "cli_chain": CLI_CHAIN,
             "active_level": config["task_level"], "suite_registry_name": SUITE}
    manifest = {"source_kind": "locked_upstream_static_manifest", "commit": LOCKED,
                "suite_registry_name": SUITE, "task_count": len(tasks), "tasks": tasks}
    return trace, manifest


def write_artifacts(trace: dict, manifest: dict, output: Path, stem: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{stem}_trace.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n")
    (output / f"{stem}_suite_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    lines = ["# CLI to suite trace", "", f"- commit: `{trace['commit']}`",
             f"- config: `{trace['config_path']}`", f"- suite: `{trace['suite_registry_name']}`", ""]
    lines += [f"{i}. `{item['path']}::{item['symbol']}`" for i, item in enumerate(trace["cli_chain"], 1)]
    lines += ["", f"Manifest: {manifest['task_count']} tasks (5 per level).", ""]
    (output / f"{stem}_trace.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("learner_outputs/mainline/day02"))
    parser.add_argument("--stem", default="config")
    args = parser.parse_args()
    trace, manifest = build_artifacts(args.upstream.resolve(), args.config.resolve())
    write_artifacts(trace, manifest, args.output_dir, args.stem)
    print(f"PASS: {trace['suite_registry_name']} / {manifest['task_count']} tasks")
    print(f"Saved: {args.output_dir / f'{args.stem}_trace.md'}")


if __name__ == "__main__":
    main()
