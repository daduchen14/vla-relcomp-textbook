"""Day 9 最小版本：把 Day 7 的数组概念迁移到 PyTorch tensor。"""

import torch


# fixture 图像使用 HWC；这里只练 tensor 属性，不代表模型的最终输入布局。
fixture_image = torch.tensor(
    [[[255, 0, 0], [0, 255, 0]], [[0, 0, 255], [255, 255, 255]]],
    dtype=torch.uint8,
)

# 深度学习计算通常使用 float32；当前教程明确放在 CPU。
fixture_state = torch.tensor([0.10, -0.20, 0.30, 1.0], dtype=torch.float32)
fixture_action = torch.tensor(
    [0.01, 0.00, -0.02, 0.0, 0.0, 0.1, 1.0], dtype=torch.float32
)

# uint8 转 float32 后归一化；原 tensor 不被原地修改。
normalized_image = fixture_image.to(torch.float32) / 255.0

print("image", tuple(fixture_image.shape), fixture_image.dtype, fixture_image.device)
print("state", tuple(fixture_state.shape), fixture_state.dtype, fixture_state.device)
print("action", tuple(fixture_action.shape), fixture_action.dtype, fixture_action.device)
print("normalized_range", float(normalized_image.min()), float(normalized_image.max()))
