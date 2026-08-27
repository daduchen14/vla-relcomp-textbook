#!/usr/bin/env python3
"""32 行左右的 observation→policy→action→step→success 最小闭环。"""

import numpy as np


def policy(observation):
    # policy 读 observation 字典；这里用 state 的第一项产生确定性动作。
    direction = 1.0 if observation["state"][0] >= 0 else -1.0
    return np.array([direction, 0, 0, 0, 0, 0, -1], dtype=np.float32)


def env_step(action, step_index):
    # fixture 环境模拟真实 env.step 的四元组返回值。
    next_observation = {
        "agent_image": np.zeros((2, 2, 3), dtype=np.uint8),
        "state": np.array([0.1 + step_index, 0.0, 0.0], dtype=np.float32),
    }
    success = bool(step_index == 2 and action[0] > 0)
    return next_observation, 0.0, success, {"success": success}


observation = {
    "agent_image": np.zeros((2, 2, 3), dtype=np.uint8),
    "state": np.array([0.1, 0.0, 0.0], dtype=np.float32),
}
for step_index in range(5):
    action = np.clip(policy(observation), -1.0, 1.0)
    observation, reward, done, info = env_step(action, step_index)
    success = bool(info.get("success", done))
    print(step_index, action.shape, action.dtype, success)
    if done:
        break
