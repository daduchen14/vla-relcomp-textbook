#!/usr/bin/env python3
"""单一修复模块：把 L0 结构标签转成固定关系指令。"""
from __future__ import annotations
from collections.abc import Mapping

MODULE_VERSION = "relation-normalizer-v1"
RELATIONS = {"NextTo": "next_to", "On": "on", "In": "in", "Between": "between"}

def normalize_relation_instruction(example: Mapping[str, str]) -> str:
    """返回规范化指令；不修改输入，也不读取图像、动作或测试集真值。"""
    required = ("level", "target_object_id", "start_relation", "start_reference_ids", "goal_relation", "goal_reference_ids")
    missing = [key for key in required if not example.get(key)]
    if missing:
        raise ValueError(f"缺少字段: {missing}")
    if str(example["level"]) != "0":
        raise ValueError("repair module 只接受 L0 标签")
    try:
        start = RELATIONS[example["start_relation"]]
        goal = RELATIONS[example["goal_relation"]]
    except KeyError as exc:
        raise ValueError(f"未知关系: {exc.args[0]}") from exc
    return (
        f"TARGET={example['target_object_id']} | "
        f"START={start}({example['start_reference_ids']}) | "
        f"ACTION=pick_and_place | GOAL={goal}({example['goal_reference_ids']})"
    )
