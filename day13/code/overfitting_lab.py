"""Day 13 工程版本：用 train/validation 曲线观察 fixture 过拟合。

CPU 合成回归实验；结果只说明本构造，不是 VLA 模型成绩。
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import torch
from torch import Tensor, nn
from torch.utils.data import DataLoader, TensorDataset


class TrainingLoopError(ValueError):
    """数据划分或训练配置违反契约。"""


class FixtureMLP(nn.Module):
    """容量可调的一维 MLP。"""

    def __init__(self, hidden_size: int) -> None:
        super().__init__()
        if hidden_size <= 0:
            raise TrainingLoopError("hidden_size 必须为正整数")
        self.network = nn.Sequential(
            nn.Linear(1, hidden_size),
            nn.Tanh(),
            nn.Linear(hidden_size, hidden_size),
            nn.Tanh(),
            nn.Linear(hidden_size, 1),
        )

    def forward(self, features: Tensor) -> Tensor:
        return self.network(features)


@dataclass(frozen=True)
class EpochRecord:
    """每个 epoch 的 train/validation 指标和更新次数。"""

    epoch: int
    train_loss: float
    validation_loss: float
    optimizer_steps: int


def make_fixture_splits(seed: int) -> tuple[TensorDataset, TensorDataset]:
    """训练集稀疏且带噪声；验证集密集、无噪声，二者 ID 逻辑隔离。"""
    generator = torch.Generator().manual_seed(seed)
    train_x = torch.linspace(-3.0, 3.0, 16, dtype=torch.float32).unsqueeze(1)
    noise = 0.35 * torch.randn(train_x.shape, generator=generator)
    train_y = torch.sin(train_x) + noise

    validation_x = torch.linspace(-3.0, 3.0, 121, dtype=torch.float32).unsqueeze(1)
    validation_y = torch.sin(validation_x)
    return TensorDataset(train_x, train_y), TensorDataset(validation_x, validation_y)


def make_loader(dataset: TensorDataset, batch_size: int, seed: int) -> DataLoader:
    """用独立 generator 固定 shuffle 顺序。"""
    if batch_size <= 0:
        raise TrainingLoopError("batch_size 必须为正整数")
    generator = torch.Generator().manual_seed(seed)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True, generator=generator)


def evaluate(model: nn.Module, dataset: TensorDataset, loss_function: nn.Module) -> float:
    """评估不建梯度图，使用整个小型数据集。"""
    model.eval()
    features, targets = dataset.tensors
    with torch.inference_mode():
        loss = loss_function(model(features), targets)
    return float(loss)


def train(
    model: nn.Module,
    train_loader: DataLoader,
    validation_dataset: TensorDataset,
    learning_rate: float,
    epochs: int,
) -> list[EpochRecord]:
    """用 Adam 训练，并在每个 epoch 后独立评估。"""
    if not math.isfinite(learning_rate) or learning_rate <= 0:
        raise TrainingLoopError("learning_rate 必须是有限正数")
    if epochs <= 0:
        raise TrainingLoopError("epochs 必须为正整数")
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_function = nn.MSELoss()
    history: list[EpochRecord] = []
    total_steps = 0

    for epoch in range(epochs):
        model.train()
        weighted_loss_sum = 0.0
        sample_count = 0
        for features, targets in train_loader:
            optimizer.zero_grad()
            loss = loss_function(model(features), targets)
            if not torch.isfinite(loss):
                raise TrainingLoopError(f"epoch {epoch} 出现非有限 loss")
            loss.backward()
            optimizer.step()
            batch_count = features.shape[0]
            weighted_loss_sum += float(loss.detach()) * batch_count
            sample_count += batch_count
            total_steps += 1
        train_loss = weighted_loss_sum / sample_count
        validation_loss = evaluate(model, validation_dataset, loss_function)
        history.append(EpochRecord(epoch, train_loss, validation_loss, total_steps))
    return history


def summarize(history: list[EpochRecord]) -> dict[str, object]:
    """以 validation 最低点定义 best epoch，不用最后一轮冒充最佳。"""
    best = min(history, key=lambda record: record.validation_loss)
    last = history[-1]
    return {
        "run_id": "fixture_day13_overfitting_lab",
        "result_type": "synthetic train/validation metrics; not a VLA experiment result",
        "best_epoch": best.epoch,
        "best_validation_loss": best.validation_loss,
        "last_epoch": last.epoch,
        "last_train_loss": last.train_loss,
        "last_validation_loss": last.validation_loss,
        "validation_degradation_after_best": last.validation_loss - best.validation_loss,
        "overfitting_signal": last.validation_loss > best.validation_loss * 1.05,
        "optimizer_steps": last.optimizer_steps,
    }


def write_artifacts(output_dir: Path, history: list[EpochRecord], report: dict[str, object]) -> None:
    """保存完整曲线 CSV 与摘要 JSON。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "fixture_learning_curves.csv").open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=list(EpochRecord.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(asdict(record) for record in history)
    (output_dir / "fixture_overfitting_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def default_output_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "learner_outputs/day13"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="运行 fixture mini-batch/过拟合实验。")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=0.01)
    parser.add_argument("--epochs", type=int, default=400)
    parser.add_argument("--output-dir", type=Path, default=default_output_dir())
    return parser


def main() -> int:
    """运行训练并保存曲线；没有过拟合信号也属于合法结果。"""
    args = build_parser().parse_args()
    try:
        torch.manual_seed(args.seed)
        train_dataset, validation_dataset = make_fixture_splits(args.seed)
        loader = make_loader(train_dataset, args.batch_size, args.seed)
        model = FixtureMLP(args.hidden_size)
        history = train(model, loader, validation_dataset, args.learning_rate, args.epochs)
        report = summarize(history)
        report.update(
            {
                "seed": args.seed,
                "hidden_size": args.hidden_size,
                "batch_size": args.batch_size,
                "learning_rate": args.learning_rate,
                "epochs": args.epochs,
                "train_samples": len(train_dataset),
                "validation_samples": len(validation_dataset),
            }
        )
        write_artifacts(args.output_dir, history, report)
    except (OSError, TrainingLoopError) as error:
        print(f"训练循环失败：{error}", file=sys.stderr)
        return 2


    print("=== VLA-RelComp Day 13 ===")
    print(f"Best epoch: {report['best_epoch']}")
    print(f"Best validation loss: {report['best_validation_loss']:.6f}")
    print(f"Last train loss: {report['last_train_loss']:.6f}")
    print(f"Last validation loss: {report['last_validation_loss']:.6f}")
    print(f"Overfitting signal: {report['overfitting_signal']}")
    print(f"Saved: {args.output_dir.resolve()}")
    print("Result type: synthetic train/validation metrics; not a VLA experiment result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
