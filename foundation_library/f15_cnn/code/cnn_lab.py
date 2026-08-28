"""Day 15 工程版本：在 CPU 上训练并评测一个最小图像分类 CNN。

数据由程序合成，只用于理解图像张量、卷积与分类，绝不是 VLA 结果。
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch import Tensor, nn
from torch.utils.data import DataLoader, Dataset


class ConfigurationError(ValueError):
    """命令行配置不满足本课约束。"""


@dataclass(frozen=True)
class FixtureImage:
    """一张可追踪的合成图像及其类别。"""

    sample_id: str
    pixels: Tensor
    label: int


class StripeDataset(Dataset[tuple[Tensor, Tensor, str]]):
    """生成横条纹（0）或竖条纹（1）的 8×8 灰度图像。"""

    def __init__(self, sample_count: int, seed: int) -> None:
        if sample_count < 4 or sample_count % 2 != 0:
            raise ConfigurationError("sample_count 必须是至少为 4 的偶数")
        generator = torch.Generator().manual_seed(seed)
        samples: list[FixtureImage] = []
        for index in range(sample_count):
            label = index % 2
            image = torch.zeros((1, 8, 8), dtype=torch.float32)
            offset = int(torch.randint(1, 5, (1,), generator=generator).item())
            if label == 0:
                image[:, offset : offset + 2, :] = 1.0  # 横向亮带。
            else:
                image[:, :, offset : offset + 2] = 1.0  # 竖向亮带。
            noise = 0.08 * torch.randn((1, 8, 8), generator=generator)
            image = (image + noise).clamp(0.0, 1.0)
            samples.append(FixtureImage(f"fixture_stripe_{index:03d}", image, label))
        self.samples = samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> tuple[Tensor, Tensor, str]:
        sample = self.samples[index]
        return sample.pixels, torch.tensor(sample.label), sample.sample_id


class TinyStripeCNN(nn.Module):
    """卷积提局部特征，池化压缩，再由线性层输出两个类别分数。"""

    def __init__(self, channels: int = 4) -> None:
        super().__init__()
        if channels <= 0:
            raise ConfigurationError("channels 必须为正整数")
        self.features = nn.Sequential(
            nn.Conv2d(1, channels, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
        )
        self.classifier = nn.Linear(channels * 4 * 4, 2)

    def forward(self, images: Tensor) -> Tensor:
        if images.ndim != 4 or tuple(images.shape[1:]) != (1, 8, 8):
            raise ValueError("images 必须具有 [batch, 1, 8, 8] 形状")
        features = self.features(images)
        return self.classifier(torch.flatten(features, start_dim=1))


def set_seed(seed: int) -> None:
    """同时固定本课会用到的三个随机数源。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def accuracy(model: nn.Module, loader: DataLoader) -> tuple[int, int, list[dict[str, object]]]:
    """在不构建梯度图的情况下统计逐样本预测。"""
    model.eval()
    correct = 0
    total = 0
    rows: list[dict[str, object]] = []
    with torch.no_grad():
        for images, labels, sample_ids in loader:
            predictions = model(images).argmax(dim=1)
            correct += int((predictions == labels).sum().item())
            total += int(labels.numel())
            rows.extend(
                {"sample_id": sid, "label": int(label), "prediction": int(prediction)}
                for sid, label, prediction in zip(sample_ids, labels, predictions)
            )
    return correct, total, rows


def run_experiment(
    sample_count: int, epochs: int, learning_rate: float, channels: int, seed: int
) -> dict[str, object]:
    """训练同一 fixture 数据集，并返回可保存的最小证据。"""
    if epochs <= 0 or learning_rate <= 0:
        raise ConfigurationError("epochs 和 learning_rate 必须为正数")
    set_seed(seed)
    dataset = StripeDataset(sample_count, seed)
    loader_generator = torch.Generator().manual_seed(seed)
    loader = DataLoader(dataset, batch_size=8, shuffle=True, generator=loader_generator)
    evaluation_loader = DataLoader(dataset, batch_size=8, shuffle=False)
    model = TinyStripeCNN(channels)
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    loss_fn = nn.CrossEntropyLoss()
    losses: list[float] = []

    model.train()
    for _epoch in range(epochs):
        loss_sum = 0.0
        for images, labels, _sample_ids in loader:
            optimizer.zero_grad()
            loss = loss_fn(model(images), labels)
            loss.backward()
            optimizer.step()
            loss_sum += float(loss.item()) * len(labels)
        losses.append(loss_sum / len(dataset))

    correct, total, predictions = accuracy(model, evaluation_loader)
    return {
        "run_id": "fixture_day15_cnn",
        "result_type": "synthetic teaching result; not a VLA experiment result",
        "seed": seed,
        "sample_count": sample_count,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "channels": channels,
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "first_loss": losses[0],
        "final_loss": losses[-1],
        "correct": correct,
        "total": total,
        "accuracy": correct / total,
        "predictions": predictions,
    }


def default_output() -> Path:
    return Path(__file__).resolve().parents[3] / "learner_outputs/foundation_library/f15_cnn/cnn_report.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="训练横/竖条纹 fixture 分类 CNN。")
    parser.add_argument("--sample-count", type=int, default=40)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--learning-rate", type=float, default=0.2)
    parser.add_argument("--channels", type=int, default=4)
    parser.add_argument("--seed", type=int, default=15)
    parser.add_argument("--output", type=Path, default=default_output())
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = run_experiment(
            args.sample_count, args.epochs, args.learning_rate, args.channels, args.seed
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (ConfigurationError, OSError, RuntimeError, ValueError) as error:
        print(f"CNN 实验失败：{error}", file=sys.stderr)
        return 2
    print("=== VLA-RelComp Day 15 ===")
    print(f"Loss: {report['first_loss']:.4f} -> {report['final_loss']:.4f}")
    print(f"Accuracy: {report['correct']}/{report['total']} = {report['accuracy']:.1%}")
    print(f"Parameters: {report['parameter_count']}")
    print(f"Saved: {args.output.resolve()}")
    print("Result type: synthetic teaching result; not a VLA experiment result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
