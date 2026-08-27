#!/usr/bin/env python3
"""从已创建的真实 VLA-Arena env 采集 evaluator 侧状态；本文件不创建环境。"""

from __future__ import annotations

from typing import Any


def _vector(values: Any, length: int, field: str) -> list[float]:
    """把 MuJoCo/NumPy 向量复制为可 JSON 序列化的有限浮点列表。"""
    result = [float(value) for value in values]
    if len(result) != length:
        raise ValueError(f"{field} 应有 {length} 项，实际 {len(result)}")
    if not all(value == value and abs(value) != float("inf") for value in result):
        raise ValueError(f"{field} 出现 NaN/Inf")
    return result


def capture_state(env: Any, *, target: str, reference: str, step: int) -> dict:
    """读取与锁定 On predicate 相同的对象 wrapper，并标注特权边界。"""
    # evaluator 拿到的是 ControlEnv/OffScreenRenderEnv；内部 `.env` 才是 BDDLBaseDomain。
    raw_env = env if hasattr(env, "object_states_dict") else getattr(env, "env", env)
    if target == reference:
        raise ValueError("target 与 reference 不得相同")
    if not hasattr(raw_env, "object_states_dict") or not hasattr(raw_env, "obj_body_id"):
        raise TypeError("需要 BDDLBaseDomain 或只包一层的 ControlEnv")
    missing = [name for name in (target, reference) if name not in raw_env.object_states_dict]
    if missing:
        raise KeyError(f"object_states_dict 缺少 goal 对象：{missing}")

    target_state = raw_env.object_states_dict[target]
    reference_state = raw_env.object_states_dict[reference]
    target_geom = target_state.get_geom_state()
    reference_geom = reference_state.get_geom_state()
    target_pos = _vector(target_geom["pos"], 3, "target.pos")
    reference_pos = _vector(reference_geom["pos"], 3, "reference.pos")
    target_quat = _vector(target_geom["quat"], 4, "target.quat_wxyz")
    reference_quat = _vector(reference_geom["quat"], 4, "reference.quat_wxyz")
    contact = bool(reference_state.check_contact(target_state))
    dx, dy = target_pos[0] - reference_pos[0], target_pos[1] - reference_pos[1]

    return {
        "step": int(step), "target": target, "reference": reference,
        "target_body_id": int(raw_env.obj_body_id[target]),
        "reference_body_id": int(raw_env.obj_body_id[reference]),
        "target_pos": target_pos, "reference_pos": reference_pos,
        "target_quat_wxyz": target_quat, "reference_quat_wxyz": reference_quat,
        "target_minus_reference_z": target_pos[2] - reference_pos[2],
        "xy_distance": (dx * dx + dy * dy) ** 0.5, "contact": contact,
        "on_by_locked_formula": reference_pos[2] <= target_pos[2] and contact
        and (dx * dx + dy * dy) ** 0.5 < 0.07,
        "visibility": "privileged_evaluator_state_not_policy_input",
        "real_environment_run": True,
    }
