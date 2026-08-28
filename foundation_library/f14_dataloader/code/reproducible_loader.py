"""Day 14 工程版本：构造可追踪、可复跑的 fixture DataLoader。

默认 num_workers=0 已在当前 CPU/macOS 实测；脚本不访问真实数据或 VLA 环境。
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import torch
from torch import Tensor
from torch.utils.data import DataLoader, Dataset, get_worker_info, random_split


class DataContractError(ValueError):
    """样本、split 或 batch 违反课程契约。"""


@dataclass(frozen=True)
class FixtureSample:
    """Dataset 内部保存的一条合成样本。"""

    sample_id: str
    feature: float
    target: float


class IndexedFixtureDataset(Dataset[dict[str, Any]]):
    """返回带稳定 ID、索引和 tensor 的 map-style Dataset。"""

    def __init__(self, sample_count: int) -> None:
        if sample_count < 4:
            raise DataContractError("sample_count 至少为 4")
        self.samples = [
            FixtureSample(
                sample_id=f"fixture_sample_{index:03d}",
                feature=float(index),
                target=2.0 * float(index) + 1.0,
            )
            for index in range(sample_count)
        ]

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        sample = self.samples[index]
        return {
            "sample_id": sample.sample_id,
            "source_index": index,
            "feature": torch.tensor([sample.feature], dtype=torch.float32),
            "target": torch.tensor([sample.target], dtype=torch.float32),
        }


def collate_fixture_batch(samples: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """校验 ID 后，显式把各样本 tensor stack 成 batch。"""
    if not samples:
        raise DataContractError("不能 collate 空 batch")
    sample_ids = [sample["sample_id"] for sample in samples]
    if any(not item.startswith("fixture_") for item in sample_ids):
        raise DataContractError("所有 sample_id 必须以 fixture_ 开头")
    if len(set(sample_ids)) != len(sample_ids):
        raise DataContractError("同一 batch 中 sample_id 不能重复")
    return {
        "sample_ids": sample_ids,
        "source_indices": torch.tensor(
            [sample["source_index"] for sample in samples], dtype=torch.int64
        ),
        "features": torch.stack([sample["feature"] for sample in samples]),
        "targets": torch.stack([sample["target"] for sample in samples]),
    }


def seed_worker(worker_id: int) -> None:
    """由 PyTorch worker seed 派生 Python/NumPy seed。"""
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


def make_splits(
    dataset: IndexedFixtureDataset, validation_count: int, seed: int
) -> tuple[Dataset[Any], Dataset[Any]]:
    """固定 generator 划分 train/validation，不按运行时顺序临时猜。"""
    if validation_count <= 0 or validation_count >= len(dataset):
        raise DataContractError("validation_count 必须在 1 与 sample_count-1 之间")
    train_count = len(dataset) - validation_count
    generator = torch.Generator().manual_seed(seed)
    return random_split(dataset, [train_count, validation_count], generator=generator)


def make_loader(
    dataset: Dataset[Any],
    batch_size: int,
    seed: int,
    num_workers: int,
    shuffle: bool,
) -> DataLoader:
    """构造拥有独立 shuffle generator 的 DataLoader。"""
    if batch_size <= 0:
        raise DataContractError("batch_size 必须为正整数")
    if num_workers < 0:
        raise DataContractError("num_workers 不能为负数")
    generator = torch.Generator().manual_seed(seed)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_fixture_batch,
        worker_init_fn=seed_worker if num_workers > 0 else None,
        generator=generator,
        persistent_workers=num_workers > 0,
    )


def collect_loader_manifest(loader: DataLoader, split: str) -> dict[str, object]:
    """遍历一轮并保存 batch 边界、ID、索引与 shape。"""
    batches: list[dict[str, object]] = []
    flattened_ids: list[str] = []
    for batch_index, batch in enumerate(loader):
        sample_ids = list(batch["sample_ids"])
        flattened_ids.extend(sample_ids)
        batches.append(
            {
                "batch_index": batch_index,
                "sample_ids": sample_ids,
                "source_indices": batch["source_indices"].tolist(),
                "feature_shape": list(batch["features"].shape),
                "target_shape": list(batch["targets"].shape),
            }
        )
    if len(flattened_ids) != len(set(flattened_ids)):
        raise DataContractError(f"{split} 一轮中出现重复 sample_id")
    return {"split": split, "sample_order": flattened_ids, "batches": batches}


def default_output() -> Path:
    return Path(__file__).resolve().parents[3] / "learner_outputs/foundation_library/f14_dataloader/loader_manifest.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成可复跑 fixture DataLoader manifest。")
    parser.add_argument("--sample-count", type=int, default=12)
    parser.add_argument("--validation-count", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--output", type=Path, default=default_output())
    return parser


def main() -> int:
    """生成 split/batch 证据；配置或 worker 错误返回 2。"""
    args = build_parser().parse_args()
    try:
        dataset = IndexedFixtureDataset(args.sample_count)
        train_set, validation_set = make_splits(dataset, args.validation_count, args.seed)
        train_loader = make_loader(
            train_set, args.batch_size, args.seed, args.num_workers, shuffle=True
        )
        validation_loader = make_loader(
            validation_set, args.batch_size, args.seed, args.num_workers, shuffle=False
        )
        train_manifest = collect_loader_manifest(train_loader, "train")
        validation_manifest = collect_loader_manifest(validation_loader, "validation")
        overlap = sorted(
            set(train_manifest["sample_order"]) & set(validation_manifest["sample_order"])
        )
        if overlap:
            raise DataContractError(f"train/validation ID 重叠：{overlap}")
        report = {
            "manifest_id": "fixture_day14_loader_manifest",
            "result_type": "synthetic loader order; not a VLA experiment result",
            "torch_version": torch.__version__,
            "seed": args.seed,
            "num_workers": args.num_workers,
            "batch_size": args.batch_size,
            "train": train_manifest,
            "validation": validation_manifest,
            "split_overlap": overlap,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, RuntimeError, DataContractError) as error:
        print(f"DataLoader 实验失败：{error}", file=sys.stderr)
        return 2

    print("=== VLA-RelComp Day 14 ===")
    print(f"Train order: {train_manifest['sample_order']}")
    print(f"Validation order: {validation_manifest['sample_order']}")
    print(f"Workers: {args.num_workers}")
    print(f"Saved: {args.output.resolve()}")
    print("Result type: synthetic loader order; not a VLA experiment result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
