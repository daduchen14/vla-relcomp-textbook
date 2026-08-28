"""Day 10 工程版本：交叉验证手算、autograd 与有限差分梯度。

只使用 fixture_ 合成数值，不训练模型，不产生 VLA 结果。
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import torch
from torch import Tensor


class GradientCheckError(ValueError):
    """输入或梯度检查不满足教学契约。"""


def quadratic_loss(parameters: Tensor, targets: Tensor) -> Tensor:
    """返回 mean((parameters-targets)^2)，结果必须是标量。"""
    if parameters.shape != targets.shape:
        raise GradientCheckError("parameters 与 targets shape 必须相同")
    if parameters.ndim != 1 or parameters.numel() == 0:
        raise GradientCheckError("本课 parameters 必须是非空一维 tensor")
    if not parameters.is_floating_point() or not targets.is_floating_point():
        raise GradientCheckError("parameters 与 targets 必须是浮点 tensor")
    if not torch.isfinite(parameters).all() or not torch.isfinite(targets).all():
        raise GradientCheckError("输入不能包含 NaN 或 infinity")
    return ((parameters - targets) ** 2).mean()


def manual_gradient(parameters: Tensor, targets: Tensor) -> Tensor:
    """手推均方误差梯度：2*(p-t)/N。"""
    return 2.0 * (parameters - targets) / parameters.numel()


def autograd_gradient(parameters: Tensor, targets: Tensor) -> tuple[Tensor, float]:
    """建立计算图、反向传播，并返回 detached 梯度与 loss。"""
    # clone 防止修改调用者数据；requires_grad_ 让新的叶子 tensor 记录梯度。
    leaf = parameters.detach().clone().requires_grad_(True)
    loss = quadratic_loss(leaf, targets)
    loss.backward()
    if leaf.grad is None:
        raise GradientCheckError("autograd 未生成 leaf.grad")
    return leaf.grad.detach().clone(), float(loss.detach())


def finite_difference_gradient(
    parameters: Tensor, targets: Tensor, epsilon: float
) -> Tensor:
    """逐元素用中心差分近似梯度，作为独立数值检查。"""
    if not math.isfinite(epsilon) or epsilon <= 0:
        raise GradientCheckError("epsilon 必须是有限正数")
    estimates = torch.empty_like(parameters)
    for index in range(parameters.numel()):
        positive = parameters.detach().clone()
        negative = parameters.detach().clone()
        positive[index] += epsilon
        negative[index] -= epsilon
        loss_positive = quadratic_loss(positive, targets)
        loss_negative = quadratic_loss(negative, targets)
        estimates[index] = (loss_positive - loss_negative) / (2.0 * epsilon)
    return estimates


def demonstrate_accumulation(value: float) -> tuple[float, float, float]:
    """连续两次 backward，展示 .grad 默认累积以及 zero_ 清零。"""
    x = torch.tensor(value, dtype=torch.float64, requires_grad=True)
    (x**2).backward()
    first = float(x.grad)
    (x**2).backward()
    accumulated = float(x.grad)
    x.grad.zero_()
    cleared = float(x.grad)
    return first, accumulated, cleared


def build_report(
    parameters: Tensor,
    targets: Tensor,
    epsilon: float,
    tolerance: float,
) -> dict[str, object]:
    """运行三种梯度并输出最大误差与通过状态。"""
    if tolerance <= 0 or not math.isfinite(tolerance):
        raise GradientCheckError("tolerance 必须是有限正数")
    manual = manual_gradient(parameters, targets)
    automatic, loss = autograd_gradient(parameters, targets)
    numerical = finite_difference_gradient(parameters, targets, epsilon)
    manual_error = float((manual - automatic).abs().max())
    numerical_error = float((numerical - automatic).abs().max())
    passed = manual_error <= tolerance and numerical_error <= tolerance
    first, accumulated, cleared = demonstrate_accumulation(float(parameters[0]))
    return {
        "report_id": "fixture_day10_gradient_report",
        "result_type": "synthetic gradient check; not a VLA experiment result",
        "torch_version": torch.__version__,
        "dtype": str(parameters.dtype),
        "parameters": parameters.tolist(),
        "targets": targets.tolist(),
        "loss": loss,
        "manual_gradient": manual.tolist(),
        "autograd_gradient": automatic.tolist(),
        "finite_difference_gradient": numerical.tolist(),
        "manual_max_error": manual_error,
        "finite_difference_max_error": numerical_error,
        "epsilon": epsilon,
        "tolerance": tolerance,
        "passed": passed,
        "accumulation_demo": {
            "first_backward": first,
            "after_second_backward": accumulated,
            "after_zero": cleared,
        },
    }


def default_output() -> Path:
    """输出到 Git 忽略的个人练习目录。"""
    return Path(__file__).resolve().parents[3] / "learner_outputs/foundation_library/f10_autograd/gradient_report.json"


def build_parser() -> argparse.ArgumentParser:
    """定义数值差分步长、容差和输出路径。"""
    parser = argparse.ArgumentParser(description="比较 fixture 手算/autograd/有限差分梯度。")
    parser.add_argument("--epsilon", type=float, default=1e-5)
    parser.add_argument("--tolerance", type=float, default=1e-8)
    parser.add_argument("--output", type=Path, default=default_output())
    return parser


def main() -> int:
    """使用 float64 减少有限差分舍入误差；检查不通过返回 1。"""
    args = build_parser().parse_args()
    parameters = torch.tensor([3.0, -1.0, 0.5], dtype=torch.float64)
    targets = torch.tensor([1.0, 2.0, -0.5], dtype=torch.float64)
    try:
        report = build_report(parameters, targets, args.epsilon, args.tolerance)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, GradientCheckError) as error:
        print(f"梯度检查失败：{error}", file=sys.stderr)
        return 2

    print("=== VLA-RelComp Day 10 ===")
    print(f"Loss: {report['loss']:.6f}")
    print(f"Manual max error: {report['manual_max_error']:.3e}")
    print(f"Finite-difference max error: {report['finite_difference_max_error']:.3e}")
    print(f"Passed: {report['passed']}")
    print(f"Saved: {args.output.resolve()}")
    print("Result type: synthetic gradient check; not a VLA experiment result")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
