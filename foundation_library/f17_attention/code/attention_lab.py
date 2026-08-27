"""Day 17 工程版本：带 padding mask 的单头 self-attention。"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import Tensor, nn


class AttentionContractError(ValueError):
    """输入 shape、mask 或维度不满足注意力契约。"""


@dataclass(frozen=True)
class AttentionResult:
    """同时返回上下文化向量与可检查的注意力权重。"""

    output: Tensor
    weights: Tensor


class SingleHeadSelfAttention(nn.Module):
    """教学用单头 self-attention：Q、K、V 都来自同一序列。"""

    def __init__(self, embedding_dim: int) -> None:
        super().__init__()
        if embedding_dim <= 0:
            raise AttentionContractError("embedding_dim 必须为正整数")
        self.embedding_dim = embedding_dim
        self.query = nn.Linear(embedding_dim, embedding_dim, bias=False)
        self.key = nn.Linear(embedding_dim, embedding_dim, bias=False)
        self.value = nn.Linear(embedding_dim, embedding_dim, bias=False)
        self.output = nn.Linear(embedding_dim, embedding_dim, bias=False)

    def forward(self, vectors: Tensor, valid_mask: Tensor) -> AttentionResult:
        if vectors.ndim != 3:
            raise AttentionContractError("vectors 必须是 [batch, sequence, embedding]")
        if vectors.shape[-1] != self.embedding_dim:
            raise AttentionContractError("vectors 最后一维与 embedding_dim 不一致")
        if valid_mask.shape != vectors.shape[:2] or valid_mask.dtype != torch.bool:
            raise AttentionContractError("valid_mask 必须是与前两维一致的 bool 张量")
        if not bool(valid_mask.any(dim=1).all()):
            raise AttentionContractError("每条序列至少需要一个有效 token")

        queries = self.query(vectors)
        keys = self.key(vectors)
        values = self.value(vectors)
        scores = queries @ keys.transpose(-2, -1) / math.sqrt(self.embedding_dim)

        # 键位置为 PAD 时设为 -inf，使 softmax 后权重严格为 0。
        scores = scores.masked_fill(~valid_mask.unsqueeze(1), float("-inf"))
        weights = torch.softmax(scores, dim=-1)
        attended = weights @ values
        output = self.output(attended)

        # PAD 查询本身也不应向下一层输出内容或展示误导性权重。
        query_mask = valid_mask.unsqueeze(-1)
        output = output.masked_fill(~query_mask, 0.0)
        weights = weights.masked_fill(~valid_mask.unsqueeze(-1), 0.0)
        return AttentionResult(output, weights)


def make_fixture_batch() -> tuple[Tensor, Tensor, tuple[str, ...], tuple[str, ...]]:
    """构造两条长度不同的合成序列，模拟 Day 16 的编码器输出。"""
    torch.manual_seed(17)
    vectors = torch.randn((2, 4, 8), dtype=torch.float32)
    valid_mask = torch.tensor(
        [[True, True, True, True], [True, True, True, False]], dtype=torch.bool
    )
    sample_ids = ("fixture_instruction_000", "fixture_instruction_001")
    token_labels = ("目标", "动作", "关系", "参照")
    return vectors, valid_mask, sample_ids, token_labels


def run_experiment(seed: int, temperature: float) -> dict[str, object]:
    """运行前向传播；temperature 仅用于受控观察权重尖锐程度。"""
    if temperature <= 0:
        raise AttentionContractError("temperature 必须为正数")
    vectors, valid_mask, sample_ids, token_labels = make_fixture_batch()
    torch.manual_seed(seed)
    attention = SingleHeadSelfAttention(vectors.shape[-1])

    # 缩放 query 权重等价于改变本实验 scores 的温度，只用于教学观察。
    with torch.no_grad():
        attention.query.weight.div_(temperature)
    result = attention(vectors, valid_mask)
    valid_query_rows = result.weights[valid_mask]
    row_sum_error = float((valid_query_rows.sum(dim=-1) - 1.0).abs().max().item())
    masked_key_max = float(result.weights[..., -1][1].abs().max().item())
    return {
        "run_id": "fixture_day17_single_head_attention",
        "result_type": "synthetic attention trace; not a VLA result or explanation",
        "seed": seed,
        "temperature": temperature,
        "sample_ids": list(sample_ids),
        "token_labels": list(token_labels),
        "input_shape": list(vectors.shape),
        "mask": valid_mask.tolist(),
        "score_shape": [vectors.shape[0], vectors.shape[1], vectors.shape[1]],
        "output_shape": list(result.output.shape),
        "valid_row_sum_max_error": row_sum_error,
        "second_sequence_masked_key_max": masked_key_max,
        "first_sequence_weights": result.weights[0].tolist(),
        "second_sequence_weights": result.weights[1].tolist(),
    }


def default_output() -> Path:
    return Path(__file__).resolve().parents[3] / "learner_outputs/foundation_library/f17_attention/attention_report.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="运行带 mask 的 fixture 单头 self-attention。")
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--output", type=Path, default=default_output())
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = run_experiment(args.seed, args.temperature)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (AttentionContractError, OSError, RuntimeError) as error:
        print(f"注意力实验失败：{error}", file=sys.stderr)
        return 2
    print("=== VLA-RelComp Day 17 ===")
    print(f"Input shape: {tuple(report['input_shape'])}")
    print(f"Score shape: {tuple(report['score_shape'])}")
    print(f"Output shape: {tuple(report['output_shape'])}")
    print(f"Valid row-sum max error: {report['valid_row_sum_max_error']:.2e}")
    print(f"Masked key max weight: {report['second_sequence_masked_key_max']:.1f}")
    print(f"Saved: {args.output.resolve()}")
    print("Result type: synthetic attention trace; not a VLA result or explanation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
