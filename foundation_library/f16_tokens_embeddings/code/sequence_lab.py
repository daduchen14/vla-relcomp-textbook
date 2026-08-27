"""Day 16 工程版本：将 fixture 指令编码为带位置的批量序列。"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import torch
from torch import Tensor, nn


class SequenceContractError(ValueError):
    """词表、长度或张量 shape 不满足教学契约。"""


@dataclass(frozen=True)
class EncodedBatch:
    """注意力层将需要的 ID、有效位 mask 与稳定样本 ID。"""

    token_ids: Tensor
    valid_mask: Tensor
    sample_ids: tuple[str, ...]


class CharacterVocabulary:
    """从训练文本建立确定性的字符级词表。"""

    PAD = "<PAD>"
    UNK = "<UNK>"

    def __init__(self, training_texts: Sequence[str]) -> None:
        characters = sorted({char for text in training_texts for char in text})
        self.token_to_id = {self.PAD: 0, self.UNK: 1}
        self.token_to_id.update({char: index + 2 for index, char in enumerate(characters)})
        self.id_to_token = {index: token for token, index in self.token_to_id.items()}

    def __len__(self) -> int:
        return len(self.token_to_id)

    def encode(self, text: str, max_length: int) -> tuple[list[int], list[bool]]:
        if max_length <= 0:
            raise SequenceContractError("max_length 必须为正整数")
        if len(text) > max_length:
            raise SequenceContractError(
                f"文本长度 {len(text)} 超过 max_length={max_length}；本课不静默截断"
            )
        ids = [self.token_to_id.get(char, self.token_to_id[self.UNK]) for char in text]
        valid = [True] * len(ids)
        pad_count = max_length - len(ids)
        return ids + [self.token_to_id[self.PAD]] * pad_count, valid + [False] * pad_count

    def decode(self, ids: Sequence[int], skip_pad: bool = True) -> str:
        tokens: list[str] = []
        for index in ids:
            token = self.id_to_token.get(int(index), self.UNK)
            if skip_pad and token == self.PAD:
                continue
            tokens.append(token)
        return "".join(tokens)


def encode_batch(
    vocabulary: CharacterVocabulary, texts: Sequence[str], max_length: int
) -> EncodedBatch:
    """把不同长度文本补齐为矩形 tensor，同时保留有效位置。"""
    if not texts:
        raise SequenceContractError("texts 不能为空")
    encoded = [vocabulary.encode(text, max_length) for text in texts]
    token_ids = torch.tensor([item[0] for item in encoded], dtype=torch.int64)
    valid_mask = torch.tensor([item[1] for item in encoded], dtype=torch.bool)
    sample_ids = tuple(f"fixture_instruction_{index:03d}" for index in range(len(texts)))
    return EncodedBatch(token_ids, valid_mask, sample_ids)


def sinusoidal_positions(max_length: int, embedding_dim: int) -> Tensor:
    """按 Transformer 论文公式生成无需训练的正弦/余弦位置表。"""
    if max_length <= 0 or embedding_dim <= 0 or embedding_dim % 2 != 0:
        raise SequenceContractError("max_length 必须为正，embedding_dim 必须为正偶数")
    positions = torch.arange(max_length, dtype=torch.float32).unsqueeze(1)
    frequencies = torch.exp(
        torch.arange(0, embedding_dim, 2, dtype=torch.float32)
        * (-math.log(10000.0) / embedding_dim)
    )
    table = torch.zeros((max_length, embedding_dim), dtype=torch.float32)
    table[:, 0::2] = torch.sin(positions * frequencies)
    table[:, 1::2] = torch.cos(positions * frequencies)
    return table


class SequenceEncoder(nn.Module):
    """token 查表后加固定位置编码，并把 PAD 输出清零。"""

    def __init__(self, vocabulary_size: int, embedding_dim: int, max_length: int) -> None:
        super().__init__()
        if vocabulary_size < 2:
            raise SequenceContractError("词表至少应包含 PAD 和 UNK")
        self.max_length = max_length
        self.token_embedding = nn.Embedding(vocabulary_size, embedding_dim, padding_idx=0)
        self.register_buffer(
            "position_table", sinusoidal_positions(max_length, embedding_dim), persistent=True
        )

    def forward(self, token_ids: Tensor, valid_mask: Tensor) -> Tensor:
        if token_ids.ndim != 2 or token_ids.shape != valid_mask.shape:
            raise SequenceContractError("token_ids 与 valid_mask 必须是相同 shape 的二维张量")
        if token_ids.shape[1] > self.max_length:
            raise SequenceContractError("序列长度超过位置表容量")
        positions = self.position_table[: token_ids.shape[1]].unsqueeze(0)
        vectors = self.token_embedding(token_ids) + positions
        return vectors.masked_fill(~valid_mask.unsqueeze(-1), 0.0)


def run_experiment(max_length: int, embedding_dim: int, seed: int) -> dict[str, object]:
    """对三条 fixture 指令执行完整编码并返回 JSON 可序列化摘要。"""
    training_texts = ["拿起红杯", "把红杯放在蓝碗左边", "拿起蓝碗"]
    evaluation_texts = ["拿起红杯", "红杯左边", "拿起绿杯"]
    vocabulary = CharacterVocabulary(training_texts)
    batch = encode_batch(vocabulary, evaluation_texts, max_length)
    torch.manual_seed(seed)
    encoder = SequenceEncoder(len(vocabulary), embedding_dim, max_length)
    vectors = encoder(batch.token_ids, batch.valid_mask)
    unknown_id = vocabulary.token_to_id[vocabulary.UNK]
    return {
        "run_id": "fixture_day16_sequence_encoding",
        "result_type": "synthetic teaching representation; not a VLA result",
        "seed": seed,
        "vocabulary": vocabulary.token_to_id,
        "texts": [
            {
                "sample_id": sample_id,
                "text": text,
                "token_ids": ids.tolist(),
                "valid_mask": mask.tolist(),
                "unknown_count": int((ids == unknown_id).sum().item()),
            }
            for sample_id, text, ids, mask in zip(
                batch.sample_ids, evaluation_texts, batch.token_ids, batch.valid_mask
            )
        ],
        "token_id_shape": list(batch.token_ids.shape),
        "embedding_shape": list(vectors.shape),
        "padding_vector_l1": float(vectors[~batch.valid_mask].abs().sum().item()),
        "first_vector": vectors[0, 0].tolist(),
    }


def default_output() -> Path:
    return Path(__file__).resolve().parents[3] / "learner_outputs/foundation_library/f16_tokens_embeddings/sequence_report.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="编码 fixture 指令的 token、mask 与位置。")
    parser.add_argument("--max-length", type=int, default=12)
    parser.add_argument("--embedding-dim", type=int, default=8)
    parser.add_argument("--seed", type=int, default=16)
    parser.add_argument("--output", type=Path, default=default_output())
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = run_experiment(args.max_length, args.embedding_dim, args.seed)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, RuntimeError, SequenceContractError) as error:
        print(f"序列编码失败：{error}", file=sys.stderr)
        return 2
    print("=== VLA-RelComp Day 16 ===")
    print(f"Vocabulary size: {len(report['vocabulary'])}")
    print(f"Token IDs shape: {tuple(report['token_id_shape'])}")
    print(f"Embedding shape: {tuple(report['embedding_shape'])}")
    print(f"Padding vector L1: {report['padding_vector_l1']:.1f}")
    print(f"Saved: {args.output.resolve()}")
    print("Result type: synthetic teaching representation; not a VLA result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
