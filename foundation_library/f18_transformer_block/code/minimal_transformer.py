"""Day 18 最小版本：把注意力、残差、归一化和前馈层组装起来。"""

import torch
from torch import nn


class TinyTransformerBlock(nn.Module):
    def __init__(self, embedding_dim: int) -> None:
        super().__init__()
        self.norm1 = nn.LayerNorm(embedding_dim)
        self.attention = nn.MultiheadAttention(
            embedding_dim, num_heads=1, batch_first=True
        )
        self.norm2 = nn.LayerNorm(embedding_dim)
        self.feed_forward = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim * 2),
            nn.GELU(),
            nn.Linear(embedding_dim * 2, embedding_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pre-norm：先归一化，再把注意力结果通过残差加回原输入。
        normalized = self.norm1(x)
        attended, _weights = self.attention(normalized, normalized, normalized)
        x = x + attended
        # 每个 token 独立通过同一个前馈网络，再做第二次残差相加。
        x = x + self.feed_forward(self.norm2(x))
        return x


torch.manual_seed(18)
inputs = torch.randn(2, 4, 8)
block = TinyTransformerBlock(embedding_dim=8)
outputs = block(inputs)
print("input shape:", tuple(inputs.shape))
print("output shape:", tuple(outputs.shape))
print("parameters:", sum(parameter.numel() for parameter in block.parameters()))
print("first output token:", outputs[0, 0].tolist())
