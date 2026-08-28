#!/usr/bin/env python3
"""最小例子：由 target/reference 位姿形成关系状态。"""

from math import dist

OBJECTS = {
    "tomato_3": {"body_id": 17, "pos": [0.12, -0.05, 0.84]},
    "porcelain_bowl_3": {"body_id": 42, "pos": [0.10, -0.04, 0.78]},
}
TARGET, REFERENCE = "tomato_3", "porcelain_bowl_3"

target_pos = OBJECTS[TARGET]["pos"]
reference_pos = OBJECTS[REFERENCE]["pos"]
snapshot = {
    "target": TARGET,
    "reference": REFERENCE,
    "target_body_id": OBJECTS[TARGET]["body_id"],
    "reference_body_id": OBJECTS[REFERENCE]["body_id"],
    "target_pos": target_pos,
    "reference_pos": reference_pos,
    "target_minus_reference_z": target_pos[2] - reference_pos[2],
    "xy_distance": dist(target_pos[:2], reference_pos[:2]),
    "visibility": "privileged_evaluator_state_not_policy_input",
}

print(snapshot)
