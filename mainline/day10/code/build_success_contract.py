#!/usr/bin/env python3
"""从锁定源码和 Day 9 表生成 goal→predicate→done→evaluator success 契约。"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
BASE = "vla_arena/vla_arena/envs/bddl_base_domain.py"
PREDICATES = "vla_arena/vla_arena/envs/predicates/base_predicates.py"
REGISTRY = "vla_arena/vla_arena/envs/predicates/__init__.py"
STATES = "vla_arena/vla_arena/envs/object_states/base_object_states.py"
EVAL_COST = "vla_arena/vla_arena/utils/eval_cost.py"
SMOL = "vla_arena/models/smolvla/evaluator.py"
OPEN = "vla_arena/models/openvla/evaluator.py"


def git_text(root: Path, path: str) -> str:
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=root, check=True,
                          text=True, capture_output=True).stdout


def symbol_source(source: str, cls: str | None, func: str) -> str:
    tree = ast.parse(source); nodes = tree.body
    if cls:
        nodes = next(node.body for node in nodes if isinstance(node, ast.ClassDef) and node.name == cls)
    node = next(node for node in nodes if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func)
    return ast.unparse(node)


def build(root: Path, task_table: Path) -> dict:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          text=True, capture_output=True).stdout.strip()
    if head != LOCKED: raise ValueError("upstream 不是锁定 commit")
    table = json.loads(task_table.read_text(encoding="utf-8"))
    if table.get("commit") != LOCKED or len(table.get("tasks", [])) != 15: raise ValueError("Day 9 表不匹配锁定版本")
    if {row["goal_relation"].lower() for row in table["tasks"]} != {"on"}:
        raise ValueError("目标 suite 不再是全 On goal")
    base, predicates = git_text(root, BASE), git_text(root, PREDICATES)
    registry, states = git_text(root, REGISTRY), git_text(root, STATES)
    eval_cost, smol, openvla = git_text(root, EVAL_COST), git_text(root, SMOL), git_text(root, OPEN)
    checks = {
        "_check_success": (symbol_source(base, "BDDLBaseDomain", "_check_success"), ["parsed_problem['goal_state']", "self._eval_predicate(state)"]),
        "step": (symbol_source(base, "BDDLBaseDomain", "step"), ["done = success or timeout_done", "info['success'] = success", "info['timeout']"]),
        "On": (symbol_source(predicates, "On", "__call__"), ["arg2.check_ontop(arg1)"]),
        "ObjectState.check_ontop": (symbol_source(states, "ObjectState", "check_ontop"), ["self.check_contact(other)", "< 0.07", "np.linalg.norm"]),
        "is_success_done": (symbol_source(eval_cost, None, "is_success_done"), ["info.get('success', done)"]),
    }
    for name, (source, needles) in checks.items():
        for needle in needles:
            if needle not in source: raise ValueError(f"锁定成功契约变化：{name} 缺 {needle}")
    if "'on': On()" not in registry or "is_success_done(done, info)" not in smol or "is_success_done(done, info)" not in openvla:
        raise ValueError("predicate registry 或 evaluator 成功调用变化")
    return {"commit": LOCKED, "suite": table["suite"], "task_count": 15,
        "goal_relations": {"on": 15}, "on_formula": {
            "z": "reference_z <= target_z", "contact": True, "xy": "distance < 0.07"},
        "done_formula": "success or timeout_done", "info_contract": {"success": "predicate result", "timeout": "timeout_done and not success"},
        "evaluator_formula": "bool(info.get('success', done))",
        "call_chain": ["BDDL :goal", "parsed_problem.goal_state", "BDDLBaseDomain._check_success",
            "BDDLBaseDomain._eval_predicate", "eval_predicate_fn['on']", "On.__call__",
            "reference ObjectState.check_ontop(target)", "BDDLBaseDomain.step info.success",
            "evaluator.is_success_done"],
        "sources": [BASE, PREDICATES, REGISTRY, STATES, EVAL_COST, SMOL, OPEN],
        "source_kind": "locked_static_success_contract_not_mujoco_run"}


def markdown(data: dict) -> str:
    lines = ["# Success 调用链", ""]
    lines += [f"{index}. `{node}`" for index, node in enumerate(data["call_chain"], 1)]
    lines += ["", "## On 条件", "", "`reference_z <= target_z AND contact AND xy_distance < 0.07`", "",
              "## 结束语义", "", "`done = success OR timeout_done`；evaluator 优先读取 `info.success`。", ""]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--task-table", type=Path, required=True); p.add_argument("--json-output", type=Path, required=True)
    p.add_argument("--markdown-output", type=Path, required=True); args = p.parse_args(); data = build(args.upstream.resolve(), args.task_table)
    for output in (args.json_output, args.markdown_output): output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n"); args.markdown_output.write_text(markdown(data))
    print("PASS: locked goal→On→done/info→evaluator success contract")


if __name__ == "__main__": main()
