"""Day 12 工程版本：训练、保存、加载并核验一个 fixture nn.Module。

仅使用 CPU 合成数据；checkpoint 只含本教程 state_dict，不是模型权重成果。
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import Tensor, nn


class ModuleContractError(ValueError):
    """模型输入、超参数或保存加载不满足契约。"""


class FixtureRegressor(nn.Module):
    """用 Linear 封装一元线性回归，演示参数注册。"""

    def __init__(self) -> None:
        super().__init__()
        self.linear = nn.Linear(1, 1, bias=True, dtype=torch.float64)

    def forward(self, features: Tensor) -> Tensor:
        """要求 N×1 输入，输出 N×1。"""
        if features.ndim != 2 or features.shape[1] != 1:
            raise ModuleContractError("features shape 必须是 (N,1)")
        return self.linear(features)


@dataclass(frozen=True)
class EpochRecord:
    """一个 epoch 的 loss 与注册参数快照。"""

    epoch: int
    loss: float
    weight: float
    bias: float


def make_fixture_data() -> tuple[Tensor, Tensor]:
    """构造无噪声 y=2x+1，shape 显式为 N×1。"""
    features = torch.linspace(-2.0, 2.0, 41, dtype=torch.float64).unsqueeze(1)
    targets = 2.0 * features + 1.0
    return features, targets


def initialize_model(seed: int) -> FixtureRegressor:
    """固定初始化 seed，并显式返回 CPU 模型。"""
    torch.manual_seed(seed)
    return FixtureRegressor().to("cpu")


def parameter_manifest(model: nn.Module) -> list[dict[str, object]]:
    """读取已注册参数的名称、shape、dtype、device 与元素数。"""
    return [
        {
            "name": name,
            "shape": list(parameter.shape),
            "dtype": str(parameter.dtype),
            "device": str(parameter.device),
            "requires_grad": parameter.requires_grad,
            "numel": parameter.numel(),
        }
        for name, parameter in model.named_parameters()
    ]


def train_model(
    model: FixtureRegressor,
    features: Tensor,
    targets: Tensor,
    learning_rate: float,
    epochs: int,
) -> list[EpochRecord]:
    """继续手写更新，突出 Module 如何集中暴露 parameters。"""
    if learning_rate <= 0 or not math.isfinite(learning_rate):
        raise ModuleContractError("learning_rate 必须是有限正数")
    if epochs <= 0:
        raise ModuleContractError("epochs 必须为正整数")
    if features.shape != targets.shape:
        raise ModuleContractError("features 与 targets shape 必须相同")

    model.train()
    history: list[EpochRecord] = []
    for epoch in range(epochs):
        predictions = model(features)
        loss = torch.mean((predictions - targets) ** 2)
        if not torch.isfinite(loss):
            raise ModuleContractError(f"epoch {epoch} loss 不是有限数")
        loss.backward()

        weight = model.linear.weight
        bias = model.linear.bias
        if weight.grad is None or bias.grad is None:
            raise ModuleContractError("注册参数没有梯度")
        history.append(
            EpochRecord(
                epoch=epoch,
                loss=float(loss.detach()),
                weight=float(weight.detach().squeeze()),
                bias=float(bias.detach().squeeze()),
            )
        )
        with torch.no_grad():
            for parameter in model.parameters():
                parameter -= learning_rate * parameter.grad
                parameter.grad.zero_()
    return history


def predict(model: FixtureRegressor, features: Tensor) -> Tensor:
    """评估模式加 inference_mode，返回与图无关的 CPU prediction。"""
    model.eval()
    with torch.inference_mode():
        return model(features).detach().cpu()


def save_state_dict(model: nn.Module, path: Path) -> None:
    """只保存 state_dict；不序列化整个 Python model 对象。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), path)


def load_state_dict(path: Path) -> FixtureRegressor:
    """构造同架构模型，再用 weights_only 模式加载可信本地 state_dict。"""
    if not path.is_file():
        raise ModuleContractError(f"checkpoint 不存在：{path}")
    model = FixtureRegressor()
    state = torch.load(path, map_location="cpu", weights_only=True)
    model.load_state_dict(state, strict=True)
    return model


def write_history(path: Path, history: list[EpochRecord]) -> None:
    """保存逐 epoch CSV，不把 checkpoint 二进制当作唯一证据。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(EpochRecord.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(record.__dict__ for record in history)


def default_output_dir() -> Path:
    """输出到 Git 忽略目录。"""
    return Path(__file__).resolve().parents[2] / "learner_outputs/day12"


def build_parser() -> argparse.ArgumentParser:
    """定义 seed、训练参数与输出。"""
    parser = argparse.ArgumentParser(description="训练并往返加载 fixture nn.Module。")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--learning-rate", type=float, default=0.1)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--output-dir", type=Path, default=default_output_dir())
    return parser


def main() -> int:
    """运行训练与 checkpoint round-trip；预测不一致返回 1。"""
    args = build_parser().parse_args()
    try:
        features, targets = make_fixture_data()
        model = initialize_model(args.seed)
        before_manifest = parameter_manifest(model)
        history = train_model(model, features, targets, args.learning_rate, args.epochs)
        predictions_before = predict(model, features)

        checkpoint_path = args.output_dir / "fixture_regressor_state.pt"
        history_path = args.output_dir / "fixture_module_history.csv"
        report_path = args.output_dir / "fixture_module_report.json"
        save_state_dict(model, checkpoint_path)
        reloaded = load_state_dict(checkpoint_path)
        predictions_after = predict(reloaded, features)
        max_prediction_difference = float((predictions_before - predictions_after).abs().max())
        round_trip_match = torch.equal(predictions_before, predictions_after)
        write_history(history_path, history)

        final_loss = float(torch.mean((predictions_after - targets) ** 2))
        report = {
            "run_id": "fixture_day12_module_round_trip",
            "result_type": "synthetic module training; not a VLA experiment result",
            "torch_version": torch.__version__,
            "seed": args.seed,
            "epochs": args.epochs,
            "learning_rate": args.learning_rate,
            "model_training_mode_after_load": reloaded.training,
            "parameters_before_training": before_manifest,
            "state_dict_keys": list(reloaded.state_dict().keys()),
            "final_loss": final_loss,
            "round_trip_match": round_trip_match,
            "max_prediction_difference": max_prediction_difference,
            "checkpoint_path": str(checkpoint_path),
        }
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, RuntimeError, ModuleContractError) as error:
        print(f"module 实验失败：{error}", file=sys.stderr)
        return 2

    print("=== VLA-RelComp Day 12 ===")
    print(f"Parameters: {report['state_dict_keys']}")
    print(f"Final loss: {final_loss:.8f}")
    print(f"Checkpoint round trip: {round_trip_match}")
    print(f"Saved checkpoint: {checkpoint_path.resolve()}")
    print(f"Saved report: {report_path.resolve()}")
    print("Result type: synthetic module training; not a VLA experiment result")
    return 0 if round_trip_match else 1


if __name__ == "__main__":
    raise SystemExit(main())
