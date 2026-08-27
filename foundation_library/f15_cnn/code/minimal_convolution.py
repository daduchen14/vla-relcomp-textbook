"""Day 15 最小版本：让一个卷积核在合成图像上滑动。"""

import torch
from torch import nn

# 一张 5×5 单通道图像；中间三列是一条竖直亮带。
image = torch.tensor(
    [[0, 0, 1, 1, 1],
     [0, 0, 1, 1, 1],
     [0, 0, 1, 1, 1],
     [0, 0, 1, 1, 1],
     [0, 0, 1, 1, 1]],
    dtype=torch.float32,
).reshape(1, 1, 5, 5)  # CNN 需要 [batch, channel, height, width]。

# 这个 3×3 核比较右侧与左侧像素，能响应竖直边缘。
kernel = torch.tensor(
    [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=torch.float32
)
conv = nn.Conv2d(1, 1, kernel_size=3, bias=False)
with torch.no_grad():
    conv.weight.copy_(kernel.reshape(1, 1, 3, 3))

feature_map = conv(image)
print("input shape:", tuple(image.shape))
print("kernel shape:", tuple(conv.weight.shape))
print("output shape:", tuple(feature_map.shape))
print("feature map:\n", feature_map[0, 0])
