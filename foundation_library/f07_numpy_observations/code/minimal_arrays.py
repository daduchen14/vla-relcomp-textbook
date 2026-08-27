"""Day 7 最小版本：用 NumPy 表示合成图像、机器人状态和动作。"""

import numpy as np


# 两行三列 RGB 图像；最后一维的 3 依次表示红、绿、蓝通道。
fixture_image = np.array(
    [
        [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        [[255, 255, 255], [128, 128, 128], [0, 0, 0]],
    ],
    dtype=np.uint8,
)

# 合成机器人状态使用 float32；数值只用于教学，不对应真实机械臂。
fixture_state = np.array([0.10, -0.20, 0.30, 0.0], dtype=np.float32)

# 七维合成动作：前三维平移，后三维旋转，最后一维夹爪。
fixture_action = np.array([0.01, 0.00, -0.02, 0.0, 0.0, 0.1, 1.0], dtype=np.float32)

print("image", fixture_image.shape, fixture_image.dtype)
print("state", fixture_state.shape, fixture_state.dtype)
print("action", fixture_action.shape, fixture_action.dtype)
print("red_pixel", fixture_image[0, 0].tolist())
