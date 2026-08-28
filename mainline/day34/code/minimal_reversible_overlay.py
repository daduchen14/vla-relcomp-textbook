#!/usr/bin/env python3
"""最小例子：提示层只存在于 oracle observation 副本。"""

base_observation = {
    "pixels": "raw_agentview_rgb",
    "task": "pick tomato and place on bowl",
}
oracle_observation = base_observation.copy()
oracle_observation["overlay"] = "TARGET_BOX=tomato_1 | REFERENCE_BOX=bowl_1"

assert "overlay" not in base_observation
print(f"during_oracle={oracle_observation['overlay']}")
del oracle_observation["overlay"]
assert oracle_observation == base_observation
print("cleanup_verified=true")
print("source=simulator_ground_truth")
print("use=diagnostic_only")
