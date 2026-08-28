#!/usr/bin/env python3
"""最小例子：固定 seed、裁剪梯度，并在 step 前拒绝 NaN。"""

import torch

torch.manual_seed(44)
weight = torch.nn.Parameter(torch.randn(()))
optimizer = torch.optim.SGD([weight], lr=0.1)

for step in range(1, 5):
    target = torch.tensor(float("nan") if step == 4 else 2.0)
    optimizer.zero_grad()
    loss = (weight - target).square()
    if not torch.isfinite(loss):
        print(f"caught_nonfinite_before_step={step}")
        break
    loss.backward()
    norm = torch.nn.utils.clip_grad_norm_([weight], max_norm=1.0,
                                           error_if_nonfinite=True)
    optimizer.step()
    print(f"step={step} loss={loss.item():.6f} grad_norm={norm.item():.6f}")
