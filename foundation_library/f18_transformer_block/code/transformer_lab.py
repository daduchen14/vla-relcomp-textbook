"""Day 18 工程版本：可训练、带 mask 的 pre-norm Transformer block。"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import Tensor, nn

# 直接执行本文件时，Python 只把 foundation_library/f18_transformer_block/code 放入搜索路径；补入仓库根目录，
# 才能复用上一课的 foundation_library.f17_attention 包。以 ``python -m`` 启动时无需重复添加。
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from foundation_library.f17_attention.code.attention_lab import AttentionContractError, SingleHeadSelfAttention


class TransformerContractError(ValueError):
    """block 配置或输入不满足课程契约。"""


class TransformerBlock(nn.Module):
    """pre-norm 单头 block：attention 子层 + FFN 子层，各带残差。"""

    def __init__(
        self, embedding_dim: int, hidden_dim: int, dropout: float = 0.0
    ) -> None:
        super().__init__()
        if embedding_dim <= 0 or hidden_dim <= 0:
            raise TransformerContractError("embedding_dim 与 hidden_dim 必须为正整数")
        if not 0.0 <= dropout < 1.0:
            raise TransformerContractError("dropout 必须在 [0, 1) 范围内")
        self.embedding_dim = embedding_dim
        self.norm1 = nn.LayerNorm(embedding_dim)
        self.attention = SingleHeadSelfAttention(embedding_dim)
        self.norm2 = nn.LayerNorm(embedding_dim)
        self.feed_forward = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, embedding_dim),
        )
        self.dropout = nn.Dropout(dropout)

    def forward(self, vectors: Tensor, valid_mask: Tensor) -> Tensor:
        if vectors.ndim != 3 or vectors.shape[-1] != self.embedding_dim:
            raise TransformerContractError("vectors 必须是 [N, L, embedding_dim]")
        if valid_mask.shape != vectors.shape[:2] or valid_mask.dtype != torch.bool:
            raise TransformerContractError("valid_mask 必须是 [N, L] bool 张量")
        try:
            attended = self.attention(self.norm1(vectors), valid_mask).output
        except AttentionContractError as error:
            raise TransformerContractError(str(error)) from error
        vectors = vectors + self.dropout(attended)
        vectors = vectors + self.dropout(self.feed_forward(self.norm2(vectors)))
        return vectors.masked_fill(~valid_mask.unsqueeze(-1), 0.0)


class FixtureSequenceClassifier(nn.Module):
    """用一个 Transformer block 和 masked mean 完成二分类。"""

    def __init__(self, embedding_dim: int, hidden_dim: int, dropout: float) -> None:
        super().__init__()
        self.block = TransformerBlock(embedding_dim, hidden_dim, dropout)
        self.classifier = nn.Linear(embedding_dim, 2)

    def forward(self, vectors: Tensor, valid_mask: Tensor) -> Tensor:
        encoded = self.block(vectors, valid_mask)
        counts = valid_mask.sum(dim=1, keepdim=True).clamp_min(1)
        pooled = encoded.sum(dim=1) / counts
        return self.classifier(pooled)


@dataclass(frozen=True)
class FixtureBatch:
    vectors: Tensor
    valid_mask: Tensor
    labels: Tensor
    sample_ids: tuple[str, ...]


def make_fixture_batch(sample_count: int, seed: int) -> FixtureBatch:
    """标签取决于所有有效 token 第一维之和，迫使模型汇总序列。"""
    if sample_count < 8:
        raise TransformerContractError("sample_count 至少为 8")
    generator = torch.Generator().manual_seed(seed)
    vectors = torch.randn((sample_count, 5, 8), generator=generator)
    lengths = torch.randint(2, 6, (sample_count,), generator=generator)
    positions = torch.arange(5).unsqueeze(0)
    valid_mask = positions < lengths.unsqueeze(1)
    vectors = vectors.masked_fill(~valid_mask.unsqueeze(-1), 0.0)
    labels = ((vectors[:, :, 0] * valid_mask).sum(dim=1) > 0).to(torch.int64)
    sample_ids = tuple(f"fixture_sequence_{index:03d}" for index in range(sample_count))
    return FixtureBatch(vectors, valid_mask, labels, sample_ids)


def run_experiment(
    sample_count: int,
    epochs: int,
    learning_rate: float,
    hidden_dim: int,
    dropout: float,
    seed: int,
) -> dict[str, object]:
    """在同一 fixture batch 上演示 forward/backward/step 完整闭环。"""
    if epochs <= 0 or learning_rate <= 0:
        raise TransformerContractError("epochs 与 learning_rate 必须为正数")
    batch = make_fixture_batch(sample_count, seed)
    torch.manual_seed(seed)
    model = FixtureSequenceClassifier(8, hidden_dim, dropout)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.CrossEntropyLoss()
    losses: list[float] = []

    model.train()
    for _epoch in range(epochs):
        optimizer.zero_grad()
        logits = model(batch.vectors, batch.valid_mask)
        loss = loss_fn(logits, batch.labels)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.item()))

    model.eval()
    with torch.no_grad():
        encoded = model.block(batch.vectors, batch.valid_mask)
        logits = model(batch.vectors, batch.valid_mask)
        predictions = logits.argmax(dim=-1)
    correct = int((predictions == batch.labels).sum().item())
    pad_l1 = float(encoded[~batch.valid_mask].abs().sum().item())
    return {
        "run_id": "fixture_day18_transformer_block",
        "result_type": "synthetic training result; not a VLA experiment result",
        "seed": seed,
        "sample_count": sample_count,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "hidden_dim": hidden_dim,
        "dropout": dropout,
        "input_shape": list(batch.vectors.shape),
        "encoded_shape": list(encoded.shape),
        "logit_shape": list(logits.shape),
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "first_loss": losses[0],
        "final_loss": losses[-1],
        "correct": correct,
        "total": sample_count,
        "training_accuracy": correct / sample_count,
        "padding_output_l1": pad_l1,
        "sample_ids": list(batch.sample_ids),
    }


def default_output() -> Path:
    return Path(__file__).resolve().parents[3] / "learner_outputs/foundation_library/f18_transformer_block/transformer_report.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="训练 fixture 最小 Transformer 分类器。")
    parser.add_argument("--sample-count", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--learning-rate", type=float, default=0.03)
    parser.add_argument("--hidden-dim", type=int, default=32)
    parser.add_argument("--dropout", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=18)
    parser.add_argument("--output", type=Path, default=default_output())
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = run_experiment(
            args.sample_count,
            args.epochs,
            args.learning_rate,
            args.hidden_dim,
            args.dropout,
            args.seed,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (TransformerContractError, OSError, RuntimeError) as error:
        print(f"Transformer 实验失败：{error}", file=sys.stderr)
        return 2
    print("=== VLA-RelComp Day 18 ===")
    print(f"Shape: {tuple(report['input_shape'])} -> {tuple(report['encoded_shape'])}")
    print(f"Loss: {report['first_loss']:.4f} -> {report['final_loss']:.4f}")
    print(f"Training accuracy: {report['correct']}/{report['total']}")
    print(f"Padding output L1: {report['padding_output_l1']:.1f}")
    print(f"Saved: {args.output.resolve()}")
    print("Result type: synthetic training result; not a VLA experiment result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
