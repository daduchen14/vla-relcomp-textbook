#!/usr/bin/env python3
"""静态核对锁定 VLA-Arena 源码，并生成真实 evaluator 调用链图。"""

from __future__ import annotations

import argparse
import ast
import subprocess
from pathlib import Path

LOCKED_COMMIT = "babe582ebffc82b979b77964a7e56417d02f63a4"
EVALUATOR = Path("vla_arena/models/random/evaluator.py")
DOMAIN = Path("vla_arena/vla_arena/envs/bddl_base_domain.py")
SUCCESS = Path("vla_arena/vla_arena/utils/eval_cost.py")
CONFIG = Path("vla_arena/configs/evaluation/random.yaml")


def function_calls(source: str, function_name: str) -> set[str]:
    tree = ast.parse(source)
    node = next((item for item in ast.walk(tree)
                 if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and item.name == function_name), None)
    if node is None:
        raise ValueError(f"找不到函数：{function_name}")
    return {ast.unparse(call.func) for call in ast.walk(node) if isinstance(call, ast.Call)}


def require_calls(source: str, function_name: str, required: set[str]) -> None:
    calls = function_calls(source, function_name)
    missing = required - calls
    if missing:
        raise ValueError(f"{function_name} 缺少预期调用：{sorted(missing)}")


def verify_upstream(upstream: Path) -> None:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=upstream, check=True,
        text=True, capture_output=True,
    ).stdout.strip()
    if commit != LOCKED_COMMIT:
        raise ValueError(f"upstream commit 不匹配：{commit}")
    evaluator = (upstream / EVALUATOR).read_text(encoding="utf-8")
    domain = (upstream / DOMAIN).read_text(encoding="utf-8")
    success = (upstream / SUCCESS).read_text(encoding="utf-8")
    config = (upstream / CONFIG).read_text(encoding="utf-8")
    require_calls(evaluator, "run_episode", {
        "prepare_observation", "get_action", "process_action", "env.step", "is_success_done",
    })
    require_calls(domain, "step", {"super().step", "self._check_success", "self._check_cost"})
    require_calls(domain, "_check_success", {"self._eval_predicate"})
    if "info.get('success', done)" not in success or "task_suite_name:" not in config:
        raise ValueError("success helper 或 random 配置契约发生变化")


def diagram() -> str:
    return f"""# Locked evaluator call chain\n\n- commit: `{LOCKED_COMMIT}`\n- evidence: static source trace; VLA-Arena episode not executed\n\n```mermaid\nflowchart TD\n  O[raw obs dict] --> P[prepare_observation]\n  P --> G[get_action / policy]\n  G --> A[process_action / 7-D action]\n  A --> E[env.step runtime dispatch]\n  E --> B[BDDLBaseDomain.step]\n  B --> S[_check_success / goal predicates]\n  S --> I[info success + done]\n  I --> D[is_success_done]\n```\n\nExact paths: `{EVALUATOR}`, `{DOMAIN}`, `{SUCCESS}`, `{CONFIG}`.\n"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("learner_outputs/mainline/day03/locked_call_chain.md"))
    args = parser.parse_args()
    verify_upstream(args.upstream.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(diagram(), encoding="utf-8")
    print(f"PASS: locked source verified; saved {args.output}")


if __name__ == "__main__":
    main()
