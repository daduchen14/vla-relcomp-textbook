#!/usr/bin/env python3
"""从锁定源码生成对象名→wrapper→MuJoCo state 的静态契约。"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
BASE = "vla_arena/vla_arena/envs/bddl_base_domain.py"
STATES = "vla_arena/vla_arena/envs/object_states/base_object_states.py"
PREDICATES = "vla_arena/vla_arena/envs/predicates/base_predicates.py"


def git_text(root: Path, path: str) -> str:
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=root, check=True,
                          text=True, capture_output=True).stdout


def symbol_source(source: str, cls: str, func: str) -> str:
    tree = ast.parse(source)
    class_node = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == cls)
    func_node = next(node for node in class_node.body if isinstance(node, ast.FunctionDef) and node.name == func)
    return ast.unparse(func_node)


def build(root: Path, task_table: Path) -> dict:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          text=True, capture_output=True).stdout.strip()
    if head != LOCKED:
        raise ValueError("upstream 不是锁定 commit")
    table = json.loads(task_table.read_text(encoding="utf-8"))
    if table.get("commit") != LOCKED or len(table.get("tasks", [])) != 15:
        raise ValueError("Day 9 task table 不匹配锁定版本")
    base, states, predicates = git_text(root, BASE), git_text(root, STATES), git_text(root, PREDICATES)
    checks = {
        "wrapper": (symbol_source(base, "BDDLBaseDomain", "_generate_object_state_wrapper"),
                    ["self.objects_dict.keys()", "ObjectState(self, object_name)",
                     "ObjectState(self, object_name, is_fixture=True)", "SiteObjectState("]),
        "get_geom_state": (symbol_source(states, "ObjectState", "get_geom_state"),
                           ["self.env.obj_body_id[self.object_name]", "body_xpos", "body_xquat",
                            "{'pos': object_pos, 'quat': object_quat}"]),
        "check_ontop": (symbol_source(states, "ObjectState", "check_ontop"),
                        ["this_object_position[2] <= other_object_position[2]",
                         "self.check_contact(other)", "< 0.07"]),
        "On": (symbol_source(predicates, "On", "__call__"), ["arg2.check_ontop(arg1)"]),
    }
    for name, (source, needles) in checks.items():
        for needle in needles:
            if needle not in source:
                raise ValueError(f"锁定 state 契约变化：{name} 缺 {needle}")
    goal_pairs = sorted({(row["target_object"], row["reference_object"]) for row in table["tasks"]})
    return {
        "commit": LOCKED, "suite": table["suite"], "task_count": 15,
        "unique_goal_pair_count": len(goal_pairs),
        "goal_pairs": [{"target": target, "reference": reference} for target, reference in goal_pairs],
        "state_path": ["BDDL goal target/reference names", "env.object_states_dict[name]",
                       "ObjectState.get_geom_state", "env.obj_body_id[name]",
                       "sim.data.body_xpos/body_xquat", "relation snapshot"],
        "quaternion_storage": "MuJoCo body_xquat: wxyz",
        "on_argument_direction": "On(target, reference) -> reference.check_ontop(target)",
        "policy_boundary": "body pose/contact are privileged evaluator diagnostics unless policy observation explicitly contains them",
        "sources": [BASE, STATES, PREDICATES],
        "source_kind": "locked_static_state_contract_not_mujoco_run",
    }


def markdown(data: dict) -> str:
    lines = ["# Object / relation state 路径", ""]
    lines.extend(f"{index}. `{node}`" for index, node in enumerate(data["state_path"], 1))
    lines += ["", "## 方向与边界", "",
              f"- `{data['on_argument_direction']}`",
              "- `body_xquat` 保存顺序：`wxyz`。",
              "- 这些字段默认只进入 evaluator 诊断，不进入 policy 输入。", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--task-table", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args(); data = build(args.upstream.resolve(), args.task_table)
    for output in (args.json_output, args.markdown_output): output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(data), encoding="utf-8")
    print(f"PASS: locked object-state contract; unique goal pairs={data['unique_goal_pair_count']}")


if __name__ == "__main__":
    main()
