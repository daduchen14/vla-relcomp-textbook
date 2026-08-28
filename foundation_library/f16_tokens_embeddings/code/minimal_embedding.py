"""Day 16 最小版本：字符 token、ID、embedding 与位置向量。"""

import torch
from torch import nn

# 为演示手写一个极小词表；0 留给补齐位置。
vocabulary = {"<PAD>": 0, "拿": 1, "起": 2, "杯": 3, "子": 4}
text = "拿起杯子"
token_ids = torch.tensor([[vocabulary[char] for char in text]])

# 每个离散 ID 查表得到一个 4 维可学习向量。
torch.manual_seed(16)
token_embedding = nn.Embedding(num_embeddings=len(vocabulary), embedding_dim=4)
token_vectors = token_embedding(token_ids)

# 相同 token 在不同位置需要不同表示，因此再查一次位置表。
position_ids = torch.arange(token_ids.shape[1]).unsqueeze(0)
position_embedding = nn.Embedding(num_embeddings=8, embedding_dim=4)
sequence_vectors = token_vectors + position_embedding(position_ids)

print("text:", text)
print("token ids:", token_ids.tolist())
print("token shape:", tuple(token_ids.shape))
print("embedding shape:", tuple(sequence_vectors.shape))
print("first vector:", sequence_vectors[0, 0].tolist())
