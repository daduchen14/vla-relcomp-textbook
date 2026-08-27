#!/usr/bin/env python3
"""从锁定源码生成四段 frame 各字段的来源契约。"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
BASE = "vla_arena/vla_arena/envs/bddl_base_domain.py"
STATES = "vla_arena/vla_arena/envs/object_states/base_object_states.py"


def git_text(root: Path, path: str) -> str:
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=root, check=True,
                          text=True, capture_output=True).stdout


def method(source: str, cls: str, name: str) -> str:
    tree = ast.parse(source); cls_node = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == cls)
    node = next(node for node in cls_node.body if isinstance(node, ast.FunctionDef) and node.name == name)
    return ast.unparse(node)


def build(root: Path) -> dict:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          text=True, capture_output=True).stdout.strip()
    if head != LOCKED: raise ValueError("upstream 不是锁定 commit")
    base, states = git_text(root, BASE), git_text(root, STATES)
    checks = {
        "ObjectState.get_geom_state": (method(states, "ObjectState", "get_geom_state"),
                                       ["body_xpos", "obj_body_id", "'pos': object_pos"]),
        "ObjectState.check_gripper_contact": (method(states, "ObjectState", "check_gripper_contact"),
                                              ["self.env.check_gripper_contact(object_1)"]),
        "BDDLBaseDomain.check_gripper_contact": (method(base, "BDDLBaseDomain", "check_gripper_contact"),
                                                 ["self._get_gripper_collision_geoms()", "self._check_contact"]),
        "BDDLBaseDomain.step": (method(base, "BDDLBaseDomain", "step"),
                                ["info['success'] = success", "done = success or timeout_done"]),
    }
    for name, (source, needles) in checks.items():
        for needle in needles:
            if needle not in source: raise ValueError(f"锁定 event probe 契约变化：{name} 缺 {needle}")
    return {
        "commit": LOCKED,
        "frame_fields": {
            "target_z": "target ObjectState.get_geom_state()['pos'][2]",
            "target_gripper_contact": "target ObjectState.check_gripper_contact()",
            "target_reference_xy_distance": "Euclidean XY distance from target/reference get_geom_state positions",
            "relation_satisfied": "info['success'] written by BDDLBaseDomain.step",
        },
        "semantic_boundary": "contact/lift/approach thresholds are project operational definitions; relation is locked goal predicate",
        "sources": [BASE, STATES], "source_kind": "locked_static_event_probe_contract_not_mujoco_run",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True); args = parser.parse_args(); result = build(args.upstream.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: locked frame-field source contract")


if __name__ == "__main__": main()
