#!/usr/bin/env python3
"""最小 HWC uint8 → NCHW float32 转换。"""

import numpy as np
import torch

# 两张 2×3 RGB 图像组成 NumPy batch；真实 adapter 是逐张图像再加 batch 轴。
images_hwc = np.arange(2 * 2 * 3 * 3, dtype=np.uint8).reshape(2, 2, 3, 3)
print("raw", images_hwc.shape, images_hwc.dtype)

# /255 把像素缩放到 [0,1]；from_numpy 保留共享内存和数值。
images = torch.from_numpy(images_hwc / 255.0)
print("scaled", images.shape, images.dtype, float(images.min()), float(images.max()))

# permute 只换轴语义：N,H,W,C → N,C,H,W；模型通常读取 channel-first。
images_nchw = images.permute(0, 3, 1, 2).to(torch.float32)
print("model", tuple(images_nchw.shape), images_nchw.dtype, images_nchw.device)

# inference_mode 表示只推理；fixture action 不是 SmolVLA 权重输出。
with torch.inference_mode():
    fixture_action = torch.linspace(-1.0, 1.0, 7).unsqueeze(0)
print("action", tuple(fixture_action.shape), fixture_action.dtype)
