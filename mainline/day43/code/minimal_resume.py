#!/usr/bin/env python3
"""最小例子：保存 step、参数和 optimizer，再从下一步继续。"""

from pathlib import Path
import torch

checkpoint = Path("learner_outputs/mainline/day43/minimal.pt")
checkpoint.parent.mkdir(parents=True, exist_ok=True)
weight = torch.nn.Parameter(torch.tensor(0.0))
optimizer = torch.optim.SGD([weight], lr=0.2)

for step in range(1, 4):
    optimizer.zero_grad()
    (weight - 3).square().backward()
    optimizer.step()
torch.save({"step": step, "weight": weight.detach(),
            "optimizer": optimizer.state_dict()}, checkpoint)

saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
weight = torch.nn.Parameter(saved["weight"])
optimizer = torch.optim.SGD([weight], lr=0.2)
optimizer.load_state_dict(saved["optimizer"])
for step in range(saved["step"] + 1, 7):
    optimizer.zero_grad(); (weight - 3).square().backward(); optimizer.step()
print(f"resumed_from={saved['step']} final_step={step} weight={weight.item():.6f}")
