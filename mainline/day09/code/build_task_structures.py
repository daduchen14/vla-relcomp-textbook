#!/usr/bin/env python3
"""只读解析锁定 PrepositionCombinations 的 15 个 BDDL task。"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from collections import deque
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
SUITE = "extrapolation_preposition_combinations"
TASK_MAP = "vla_arena/vla_arena/benchmark/vla_arena_suite_task_map.py"


def git_text(root: Path, path: str) -> str:
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=root, check=True,
                          text=True, capture_output=True).stdout


def parse_one(tokens: deque[str]):
    token = tokens.popleft()
    if token != "(": return token
    result = []
    while tokens and tokens[0] != ")": result.append(parse_one(tokens))
    if not tokens: raise ValueError("BDDL 缺少右括号")
    tokens.popleft(); return result


def parse_sexpr(text: str):
    clean = "\n".join(line.split(";", 1)[0] for line in text.splitlines())
    tokens = deque(clean.replace("(", " ( ").replace(")", " ) ").split())
    tree = parse_one(tokens)
    if tokens: raise ValueError("BDDL 有多个顶层表达式")
    return tree


def section(tree: list, name: str) -> list:
    matches = [item for item in tree if isinstance(item, list) and item and item[0] == name]
    if len(matches) != 1: raise ValueError(f"{name} section 数量不是 1")
    return matches[0]


def typed_items(node: list) -> dict[str, str]:
    mapping, pending, index = {}, [], 1
    while index < len(node):
        token = node[index]
        if token == "-":
            item_type = node[index + 1]
            for item in pending: mapping[item] = item_type
            pending, index = [], index + 2
        else: pending.append(token); index += 1
    if pending: raise ValueError(f"未带类型的对象：{pending}")
    return mapping


def task_map(source: str) -> dict:
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and
                any(isinstance(t, ast.Name) and t.id == "vla_arena_task_map" for t in n.targets))
    return ast.literal_eval(node.value)[SUITE]


def structure(bddl: str, level: int, task_id: int, name: str, path: str,
              source_kind: str = "locked_bddl_static_structure_not_episode") -> dict:
    tree = parse_sexpr(bddl); objects = typed_items(section(tree, ":objects"))
    fixtures = typed_items(section(tree, ":fixtures")); interest = section(tree, ":obj_of_interest")[1:]
    init = section(tree, ":init")[1:]; goal_node = section(tree, ":goal")[1]
    goals = goal_node[1:] if goal_node[0].lower() == "and" else [goal_node]
    if len(goals) != 1 or len(goals[0]) != 3: raise ValueError("本课只接受单个二元 goal predicate")
    relation, target, reference = goals[0]
    placement = lambda obj: next((pred for pred in init if len(pred) >= 3 and pred[1] == obj), None)
    return {"level": level, "task_id": task_id, "task_name": name, "bddl_path": path,
            "language": " ".join(section(tree, ":language")[1:]), "object_types": objects,
            "fixture_types": fixtures, "object_count": len(objects), "obj_of_interest": interest,
            "init_predicate_count": len(init), "target_initial_predicate": placement(target),
            "reference_initial_predicate": placement(reference), "goal_predicate": goals[0],
            "goal_relation": relation, "target_object": target, "reference_object": reference,
            "goal_args_covered_by_obj_of_interest": {target, reference}.issubset(set(interest)),
            "source_kind": source_kind}


def build(root: Path) -> dict:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          text=True, capture_output=True).stdout.strip()
    if head != LOCKED: raise ValueError("upstream 不是锁定 commit")
    mapping, rows = task_map(git_text(root, TASK_MAP)), []
    for level in (0, 1, 2):
        if len(mapping[level]) != 5: raise ValueError(f"L{level} 不是 5 tasks")
        for task_id, name in enumerate(mapping[level]):
            path = f"vla_arena/vla_arena/bddl_files/{SUITE}/level_{level}/{name}.bddl"
            rows.append(structure(git_text(root, path), level, task_id, name, path))
    return {"commit": LOCKED, "suite": SUITE, "task_count": 15,
            "metadata_warning_count": sum(not row["goal_args_covered_by_obj_of_interest"] for row in rows),
            "tasks": rows, "source_kind": "locked_bddl_static_table_not_simulation"}


def markdown(data: dict) -> str:
    lines = ["# PrepositionCombinations 任务结构表", "",
        "| Level | ID | goal | target 初态 | reference 初态 | interest 覆盖 goal |", "|---:|---:|---|---|---|---|"]
    for row in data["tasks"]:
        goal = " ".join(row["goal_predicate"]); target = " ".join(row["target_initial_predicate"] or ["UNKNOWN"])
        reference = " ".join(row["reference_initial_predicate"] or ["UNKNOWN"])
        lines.append(f"| L{row['level']} | {row['task_id']} | `{goal}` | `{target}` | `{reference}` | {row['goal_args_covered_by_obj_of_interest']} |")
    lines += ["", f"> 静态提示：{data['metadata_warning_count']} 个 task 的 obj_of_interest 未覆盖全部 goal 参数；保留原数据，不自动修正。", ""]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--json-output", type=Path, required=True); p.add_argument("--markdown-output", type=Path, required=True)
    args = p.parse_args(); data = build(args.upstream.resolve())
    for output in (args.json_output, args.markdown_output): output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    args.markdown_output.write_text(markdown(data), encoding="utf-8")
    print(f"PASS: 15 locked BDDL tasks; metadata warnings={data['metadata_warning_count']}")


if __name__ == "__main__": main()
