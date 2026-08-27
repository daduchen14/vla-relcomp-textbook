"""Day 9 工程版本：构造、变换、校验并记录 fixture tensors。

所有 tensor 都是合成教学数据；脚本默认 CPU，不产生 VLA 或 GPU 结果。
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import Tensor


class TensorContractError(ValueError):
    """tensor 的 shape、dtype、device 或数值违反教学契约。"""


@dataclass(frozen=True)
class FixtureTensorBatch:
    """一个 batch 的合成图像、状态与动作。"""

    batch_id: str
    images: Tensor
    states: Tensor
    actions: Tensor


def select_device(requested: str) -> torch.device:
    """显式选择设备；不可用时失败，不静默换设备。"""
    if requested == "cpu":
        return torch.device("cpu")
    if requested == "mps":
        if not torch.backends.mps.is_available():
            raise TensorContractError("请求了 mps，但当前 PyTorch 报告不可用")
        return torch.device("mps")
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise TensorContractError("请求了 cuda，但当前 PyTorch 报告不可用")
        return torch.device("cuda")
    raise TensorContractError("device 只能是 cpu、mps 或 cuda")


def build_fixture_batch(batch_size: int, device: torch.device) -> FixtureTensorBatch:
    """生成规律可预测的 N×H×W×C 图像及对应状态/动作。"""
    if batch_size <= 0:
        raise TensorContractError("batch_size 必须为正整数")

    # arange 产生 0..71；reshape 为 2×3×4×3 的两张 HWC fixture 图像。
    base_images = torch.arange(72, dtype=torch.uint8).reshape(2, 3, 4, 3)
    # repeat 按所需 batch 数复制模板，再截取精确 batch_size。
    repeats = (batch_size + 1) // 2
    images = base_images.repeat(repeats, 1, 1, 1)[:batch_size].to(device)

    base_state = torch.tensor([0.10, -0.20, 0.30, 1.0], dtype=torch.float32)
    states = base_state.repeat(batch_size, 1).to(device)

    base_action = torch.tensor(
        [0.01, 0.00, -0.02, 0.0, 0.0, 0.1, 1.0], dtype=torch.float32
    )
    actions = base_action.repeat(batch_size, 1).to(device)
    return FixtureTensorBatch("fixture_day09_batch", images, states, actions)


def validate_batch(batch: FixtureTensorBatch) -> None:
    """检查 batch 轴一致、字段 dtype 正确且浮点值有限。"""
    if not batch.batch_id.startswith("fixture_"):
        raise TensorContractError("batch_id 必须以 fixture_ 开头")
    if batch.images.ndim != 4 or batch.images.shape[-1] != 3:
        raise TensorContractError("images shape 必须是 (N,H,W,3)")
    if batch.images.dtype != torch.uint8:
        raise TensorContractError("原始 images dtype 必须是 torch.uint8")
    batch_size = batch.images.shape[0]
    if batch.states.shape != (batch_size, 4):
        raise TensorContractError("states shape 必须是 (N,4)")
    if batch.actions.shape != (batch_size, 7):
        raise TensorContractError("actions shape 必须是 (N,7)")
    if batch.states.dtype != torch.float32 or batch.actions.dtype != torch.float32:
        raise TensorContractError("states/actions dtype 必须是 torch.float32")
    devices = {batch.images.device, batch.states.device, batch.actions.device}
    if len(devices) != 1:
        raise TensorContractError("同一 batch 的 tensors 必须位于同一 device")
    if not torch.isfinite(batch.states).all() or not torch.isfinite(batch.actions).all():
        raise TensorContractError("states/actions 不能包含 NaN 或 infinity")


def prepare_images(images_hwc: Tensor) -> Tensor:
    """把 N×H×W×C uint8 转成连续 N×C×H×W float32 [0,1]。"""
    # permute 只重排轴，常返回非连续 view；contiguous 明确整理布局。
    images_chw = images_hwc.permute(0, 3, 1, 2).contiguous()
    return images_chw.to(dtype=torch.float32) / 255.0


def summarize_tensor(name: str, tensor: Tensor) -> dict[str, object]:
    """生成可写 JSON 的小型 tensor 元数据。"""
    summary: dict[str, object] = {
        "name": name,
        "shape": list(tensor.shape),
        "dtype": str(tensor.dtype),
        "device": str(tensor.device),
        "requires_grad": tensor.requires_grad,
        "is_contiguous": tensor.is_contiguous(),
        "numel": tensor.numel(),
        "element_size_bytes": tensor.element_size(),
        "storage_bytes": tensor.numel() * tensor.element_size(),
    }
    if tensor.numel() > 0:
        summary["min"] = float(tensor.min().detach().cpu())
        summary["max"] = float(tensor.max().detach().cpu())
    return summary


def build_report(batch: FixtureTensorBatch, model_images: Tensor) -> dict[str, object]:
    """汇总版本、设备与字段元数据，不保存大 tensor。"""
    return {
        "report_id": "fixture_day09_tensor_report",
        "result_type": "synthetic tensor metadata; not a VLA experiment result",
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available(),
        "batch_id": batch.batch_id,
        "tensors": [
            summarize_tensor("images_hwc", batch.images),
            summarize_tensor("images_nchw", model_images),
            summarize_tensor("states", batch.states),
            summarize_tensor("actions", batch.actions),
        ],
    }


def default_output() -> Path:
    """输出报告进入 Git 忽略的个人目录。"""
    return Path(__file__).resolve().parents[2] / "learner_outputs/day09/tensor_report.json"


def build_parser() -> argparse.ArgumentParser:
    """定义 batch、device 与输出参数。"""
    parser = argparse.ArgumentParser(description="运行 fixture PyTorch tensor 实验。")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--device", choices=("cpu", "mps", "cuda"), default="cpu")
    parser.add_argument("--output", type=Path, default=default_output())
    return parser


def main() -> int:
    """运行 CPU 默认实验；契约/设备错误返回 2。"""
    args = build_parser().parse_args()
    try:
        device = select_device(args.device)
        batch = build_fixture_batch(args.batch_size, device)
        validate_batch(batch)
        model_images = prepare_images(batch.images)
        report = build_report(batch, model_images)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, TensorContractError) as error:
        print(f"tensor 实验失败：{error}", file=sys.stderr)
        return 2

    print("=== VLA-RelComp Day 9 ===")
    print(f"PyTorch: {torch.__version__}")
    print(f"Device: {device}")
    print(f"Images HWC: {tuple(batch.images.shape)} {batch.images.dtype}")
    print(f"Images NCHW: {tuple(model_images.shape)} {model_images.dtype}")
    print(f"Saved: {args.output.resolve()}")
    print("Result type: synthetic tensor metadata; not a VLA experiment result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
