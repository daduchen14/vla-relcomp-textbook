"""Day 17 最小版本：直接用矩阵乘法实现缩放点积注意力。"""

import math

import torch

# 三个 token，每个 token 用二维向量表示；此处令 Q=K=V 便于手算。
tokens = torch.tensor(
    [[1.0, 0.0],   # token 0 更像第一个方向
     [0.0, 1.0],   # token 1 更像第二个方向
     [1.0, 1.0]]   # token 2 同时包含两个方向
)
queries = tokens
keys = tokens
values = tokens

# QK^T 得到“每个查询对每个键”的分数，除以 sqrt(d) 防止数值过大。
scores = queries @ keys.T / math.sqrt(keys.shape[-1])
weights = torch.softmax(scores, dim=-1)

# 每个输出是所有 value 的加权和，而不是只复制自己。
outputs = weights @ values

print("scores shape:", tuple(scores.shape))
print("weights:\n", weights)
print("row sums:", weights.sum(dim=-1))
print("outputs shape:", tuple(outputs.shape))
print("outputs:\n", outputs)
