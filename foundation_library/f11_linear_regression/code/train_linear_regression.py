"""Day 11 工程版本：生成 fixture 数据并从零训练线性回归。

使用 PyTorch tensor/autograd，但不使用 nn.Module 或 optimizer；Day 12–13 再引入。
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
from torch import Tensor


class TrainingContractError(ValueError):
    """数据或训练超参数违反本课契约。"""


@dataclass(frozen=True)
class EpochRecord:
    """一个 epoch 结束后的可追溯训练状态。"""

    epoch: int
    loss: float
    weight: float
    bias: float
    weight_gradient: float
    bias_gradient: float


def make_fixture_data(noise_scale: float, seed: int) -> tuple[Tensor, Tensor]:
    """生成 y=2x+1 加可控高斯噪声的一维数据。"""
    if not math.isfinite(noise_scale) or noise_scale < 0:
        raise TrainingContractError("noise_scale 必须是有限非负数")
    generator = torch.Generator(device="cpu").manual_seed(seed)
    features = torch.linspace(-2.0, 2.0, steps=41, dtype=torch.float64)
    noise = torch.randn(features.shape, generator=generator, dtype=torch.float64)
    targets = 2.0 * features + 1.0 + noise_scale * noise
    return features, targets


def mean_squared_error(predictions: Tensor, targets: Tensor) -> Tensor:
    """计算标量 MSE，先拒绝 shape 不一致。"""
    if predictions.shape != targets.shape:
        raise TrainingContractError("predictions 与 targets shape 必须相同")
    return ((predictions - targets) ** 2).mean()


def validate_training_inputs(
    features: Tensor,
    targets: Tensor,
    learning_rate: float,
    epochs: int,
) -> None:
    """在进入循环前校验 shape、数值和超参数。"""
    if features.ndim != 1 or features.shape != targets.shape or features.numel() < 2:
        raise TrainingContractError("features/targets 必须是同 shape 且至少两项的一维 tensor")
    if not torch.isfinite(features).all() or not torch.isfinite(targets).all():
        raise TrainingContractError("训练数据不能包含 NaN 或 infinity")
    if not math.isfinite(learning_rate) or learning_rate <= 0:
        raise TrainingContractError("learning_rate 必须是有限正数")
    if epochs <= 0:
        raise TrainingContractError("epochs 必须为正整数")


def train(
    features: Tensor,
    targets: Tensor,
    learning_rate: float,
    epochs: int,
) -> tuple[Tensor, Tensor, list[EpochRecord]]:
    """手写全批量梯度下降并返回参数与每轮记录。"""
    validate_training_inputs(features, targets, learning_rate, epochs)
    weight = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
    bias = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
    history: list[EpochRecord] = []

    for epoch in range(epochs):
        predictions = weight * features + bias
        loss = mean_squared_error(predictions, targets)
        if not torch.isfinite(loss):
            raise TrainingContractError(f"epoch {epoch} loss 不是有限数")
        loss.backward()
        if weight.grad is None or bias.grad is None:
            raise TrainingContractError("autograd 未产生参数梯度")

        # 先记录本轮前向/梯度，再做原地参数更新。
        history.append(
            EpochRecord(
                epoch=epoch,
                loss=float(loss.detach()),
                weight=float(weight.detach()),
                bias=float(bias.detach()),
                weight_gradient=float(weight.grad.detach()),
                bias_gradient=float(bias.grad.detach()),
            )
        )
        with torch.no_grad():
            weight -= learning_rate * weight.grad
            bias -= learning_rate * bias.grad
        weight.grad.zero_()
        bias.grad.zero_()

    return weight.detach(), bias.detach(), history


def closed_form_solution(features: Tensor, targets: Tensor) -> tuple[float, float]:
    """用一元线性回归闭式解提供独立结果核对。"""
    centered_x = features - features.mean()
    centered_y = targets - targets.mean()
    denominator = (centered_x**2).sum()
    if float(denominator) == 0.0:
        raise TrainingContractError("features 没有变化，无法求唯一斜率")
    weight = (centered_x * centered_y).sum() / denominator
    bias = targets.mean() - weight * features.mean()
    return float(weight), float(bias)


def write_artifacts(
    output_dir: Path,
    history: list[EpochRecord],
    report: dict[str, object],
) -> tuple[Path, Path]:
    """保存逐 epoch CSV 和训练摘要 JSON。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    history_path = output_dir / "fixture_training_history.csv"
    report_path = output_dir / "fixture_training_report.json"
    with history_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(EpochRecord.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(asdict(record) for record in history)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return history_path, report_path


def default_output_dir() -> Path:
    """默认写入被 Git 忽略的学习者输出目录。"""
    return Path(__file__).resolve().parents[3] / "learner_outputs/foundation_library/f11_linear_regression"


def build_parser() -> argparse.ArgumentParser:
    """定义可做控制变量实验的训练参数。"""
    parser = argparse.ArgumentParser(description="从零训练 fixture 一元线性回归。")
    parser.add_argument("--learning-rate", type=float, default=0.1)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--noise-scale", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output-dir", type=Path, default=default_output_dir())
    return parser


def main() -> int:
    """运行训练；正常完成但不收敛返回 1，契约错误返回 2。"""
    args = build_parser().parse_args()
    try:
        features, targets = make_fixture_data(args.noise_scale, args.seed)
        weight, bias, history = train(
            features, targets, args.learning_rate, args.epochs
        )
        closed_weight, closed_bias = closed_form_solution(features, targets)
        final_predictions = weight * features + bias
        final_loss = float(mean_squared_error(final_predictions, targets))
        converged = final_loss < history[0].loss and math.isfinite(final_loss)
        report = {
            "run_id": "fixture_day11_linear_regression",
            "result_type": "synthetic regression training; not a VLA experiment result",
            "seed": args.seed,
            "noise_scale": args.noise_scale,
            "learning_rate": args.learning_rate,
            "epochs": args.epochs,
            "sample_count": features.numel(),
            "initial_loss": history[0].loss,
            "final_loss": final_loss,
            "learned_weight": float(weight),
            "learned_bias": float(bias),
            "closed_form_weight": closed_weight,
            "closed_form_bias": closed_bias,
            "converged": converged,
        }
        history_path, report_path = write_artifacts(args.output_dir, history, report)
    except (OSError, TrainingContractError) as error:
        print(f"训练失败：{error}", file=sys.stderr)
        return 2

    print("=== VLA-RelComp Day 11 ===")
    print(f"Initial loss: {report['initial_loss']:.6f}")
    print(f"Final loss: {report['final_loss']:.6f}")
    print(f"Learned: w={report['learned_weight']:.4f}, b={report['learned_bias']:.4f}")
    print(f"Closed form: w={closed_weight:.4f}, b={closed_bias:.4f}")
    print(f"Saved history: {history_path.resolve()}")
    print(f"Saved report: {report_path.resolve()}")
    print("Result type: synthetic regression training; not a VLA experiment result")
    return 0 if converged else 1


if __name__ == "__main__":
    raise SystemExit(main())
