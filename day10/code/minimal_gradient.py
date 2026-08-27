"""Day 10 最小版本：手算并用 autograd 验证一个标量导数。"""

import torch


# x 是需要求导的叶子 tensor；float32 足够完成本课最小例子。
x = torch.tensor(3.0, dtype=torch.float32, requires_grad=True)

# y = (x - 1)^2；手算 dy/dx = 2(x - 1)，x=3 时应为 4。
y = (x - 1.0) ** 2
y.backward()

manual_gradient = 2.0 * (float(x.detach()) - 1.0)
autograd_gradient = float(x.grad)

print(f"x={float(x.detach())}")
print(f"y={float(y.detach())}")
print(f"manual_gradient={manual_gradient}")
print(f"autograd_gradient={autograd_gradient}")
print(f"match={abs(manual_gradient - autograd_gradient) < 1e-6}")
print("synthetic scalar example; not a VLA experiment result")
