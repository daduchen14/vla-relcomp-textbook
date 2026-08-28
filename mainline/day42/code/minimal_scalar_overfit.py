#!/usr/bin/env python3
"""最小例子：反复训练同一个标量 batch，确认优化闭环。"""

import torch

weight = torch.nn.Parameter(torch.tensor(0.0))
optimizer = torch.optim.SGD([weight], lr=0.2)
target = torch.tensor(3.0)

for step in range(31):
    loss = (weight - target).square()
    if step in {0, 10, 20, 30}:
        print(f"step={step} loss={loss.item():.8f} weight={weight.item():.6f}")
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

print(f"target_reached={abs(weight.item() - target.item()) < 1e-5}")
