"""Day 12 最小版本：用 nn.Module 封装 y=wx+b。"""

import torch
from torch import nn


class TinyRegressor(nn.Module):
    """输入一项、输出一项的最小线性模型。"""

    def __init__(self) -> None:
        super().__init__()
        # 赋给 self 的 nn.Linear 会自动注册其中 weight 和 bias。
        self.linear = nn.Linear(in_features=1, out_features=1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """定义一次前向：把 N×1 features 映射为 N×1 predictions。"""
        return self.linear(features)


torch.manual_seed(7)
model = TinyRegressor()
fixture_features = torch.tensor([[-1.0], [0.0], [1.0]])
fixture_predictions = model(fixture_features)

print(model)
print("input_shape", tuple(fixture_features.shape))
print("output_shape", tuple(fixture_predictions.shape))
for name, parameter in model.named_parameters():
    print(name, tuple(parameter.shape), parameter.requires_grad)
print("synthetic forward pass; not a VLA experiment result")
