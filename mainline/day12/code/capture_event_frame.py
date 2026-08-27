#!/usr/bin/env python3
"""从一次真实 env.step 后采集 Day 12 logger 所需的原始 frame。"""

from __future__ import annotations

from math import hypot
from typing import Any


def capture_frame(env: Any, info: dict, *, target: str, reference: str, step: int) -> dict:
    """读取 target gripper contact、相对位置与 step 写入的 success。"""
    raw_env = env if hasattr(env, "object_states_dict") else getattr(env, "env", env)
    if not hasattr(raw_env, "object_states_dict"):
        raise TypeError("需要 BDDLBaseDomain 或只包一层的 ControlEnv")
    if "success" not in info:
        raise KeyError("锁定 step 应提供 info.success；禁止用 done 猜 relation")
    target_state = raw_env.object_states_dict[target]
    reference_state = raw_env.object_states_dict[reference]
    target_pos = [float(value) for value in target_state.get_geom_state()["pos"]]
    reference_pos = [float(value) for value in reference_state.get_geom_state()["pos"]]
    if len(target_pos) != 3 or len(reference_pos) != 3:
        raise ValueError("object position 必须是三维")
    return {
        "step": int(step), "target_z": target_pos[2],
        "target_gripper_contact": bool(target_state.check_gripper_contact()),
        "target_reference_xy_distance": hypot(target_pos[0] - reference_pos[0],
                                                target_pos[1] - reference_pos[1]),
        "relation_satisfied": bool(info["success"]),
    }
