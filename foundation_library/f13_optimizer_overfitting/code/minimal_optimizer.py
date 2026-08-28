"""Day 13 最小版本：DataLoader + SGD optimizer 完成 mini-batch 训练。"""

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


torch.manual_seed(7)
features = torch.linspace(-2.0, 2.0, 20).unsqueeze(1)
targets = 2.0 * features + 1.0

# Dataset 对齐保存每个 x/y；DataLoader 每次提供 5 个样本。
loader = DataLoader(TensorDataset(features, targets), batch_size=5, shuffle=True)
model = nn.Linear(1, 1)
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
loss_function = nn.MSELoss()

for epoch in range(20):
    for batch_features, batch_targets in loader:
        optimizer.zero_grad()
        predictions = model(batch_features)
        loss = loss_function(predictions, batch_targets)
        loss.backward()
        optimizer.step()

weight = float(model.weight.detach().squeeze())
bias = float(model.bias.detach().squeeze())
print(f"batches_per_epoch={len(loader)}")
print(f"weight={weight:.4f}, bias={bias:.4f}")
print("synthetic mini-batch training; not a VLA experiment result")
