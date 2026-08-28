#!/usr/bin/env python3
"""最小例子：冻结 backbone/head，只让 relation_adapter 接收梯度。"""

import torch
from torch import nn

model = nn.ModuleDict({
    "backbone": nn.Linear(4, 4),
    "relation_adapter": nn.Linear(4, 4, bias=False),
    "action_head": nn.Linear(4, 2),
})
for name, parameter in model.named_parameters():
    parameter.requires_grad = name.startswith("relation_adapter.")

x = torch.tensor([[1.0, 0.0, 0.5, -0.5]])
hidden = model["backbone"] (x).detach()
prediction = model["action_head"] (model["relation_adapter"] (hidden))
target = torch.tensor([[0.2, -0.1]])
loss = torch.nn.functional.mse_loss(prediction, target)
loss.backward()

for name, parameter in model.named_parameters():
    print(f"{name}: trainable={parameter.requires_grad} grad={parameter.grad is not None}")
print(f"loss={loss.item():.6f}")
