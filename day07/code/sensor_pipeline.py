"""Day 7 工程版本：构造、校验、变换并保存 fixture 观测与动作。

所有数组均为合成教学数据，不来自机器人、仿真器或 VLA 模型。
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


class ArrayContractError(ValueError):
    """数组的 shape、dtype 或数值范围违反教学契约。"""


@dataclass(frozen=True)
class FixtureObservation:
    """一帧合成 RGB 图像与一维机器人状态。"""

    observation_id: str
    image: NDArray[np.uint8]
    state: NDArray[np.float32]


def build_fixture_observation(height: int, width: int) -> FixtureObservation:
    """生成有确定规律的 RGB 图像和四维状态，便于预测与测试。"""
    if height <= 0 or width <= 0:
        raise ArrayContractError("height 和 width 必须为正整数")

    # zeros 一次分配连续的 H×W×3 uint8 数组。
    image = np.zeros((height, width, 3), dtype=np.uint8)
    # 红通道沿列从 0 逐渐变亮；广播把一行复制到所有行。
    image[:, :, 0] = np.linspace(0, 255, width, dtype=np.uint8)
    # 绿通道沿行从 0 逐渐变亮；[:, None] 把形状变为 H×1 以便广播。
    image[:, :, 1] = np.linspace(0, 255, height, dtype=np.uint8)[:, None]
    # 蓝通道使用常数，便于观察通道顺序。
    image[:, :, 2] = 64

    # 数值是 fixture；四个位置可类比 x、y、z 与夹爪状态。
    state = np.array([0.10, -0.20, 0.30, 1.0], dtype=np.float32)
    return FixtureObservation("fixture_day07_observation", image, state)


def build_fixture_action(scale: float) -> NDArray[np.float32]:
    """构造七维 delta action；scale 只缩放前六个运动分量。"""
    if not np.isfinite(scale) or scale < 0:
        raise ArrayContractError("action scale 必须是有限非负数")
    motion = np.array([0.01, 0.00, -0.02, 0.0, 0.0, 0.1], dtype=np.float32)
    gripper = np.array([1.0], dtype=np.float32)
    return np.concatenate((motion * np.float32(scale), gripper))


def validate_observation(observation: FixtureObservation) -> None:
    """拒绝错误 ID、shape、dtype 与像素范围。"""
    if not observation.observation_id.startswith("fixture_"):
        raise ArrayContractError("observation_id 必须以 fixture_ 开头")
    if observation.image.ndim != 3 or observation.image.shape[2] != 3:
        raise ArrayContractError("image shape 必须是 (height, width, 3)")
    if observation.image.dtype != np.uint8:
        raise ArrayContractError("原始 RGB image dtype 必须是 uint8")
    if observation.state.shape != (4,):
        raise ArrayContractError("本课 state shape 必须是 (4,)")
    if observation.state.dtype != np.float32:
        raise ArrayContractError("state dtype 必须是 float32")
    if not np.all(np.isfinite(observation.state)):
        raise ArrayContractError("state 不能包含 NaN 或 infinity")


def validate_action(action: NDArray[np.float32]) -> None:
    """检查七维动作，不对其物理语义作超出教学范围的推断。"""
    if action.shape != (7,):
        raise ArrayContractError("action shape 必须是 (7,)")
    if action.dtype != np.float32:
        raise ArrayContractError("action dtype 必须是 float32")
    if not np.all(np.isfinite(action)):
        raise ArrayContractError("action 不能包含 NaN 或 infinity")


def normalize_image(image: NDArray[np.uint8]) -> NDArray[np.float32]:
    """把 [0,255] 的 uint8 图像转换成 [0,1] 的 float32 图像。"""
    # astype 先创建浮点副本，避免 uint8 除法/写回造成精度或溢出问题。
    normalized = image.astype(np.float32) / np.float32(255.0)
    return normalized


def build_summary(
    observation: FixtureObservation,
    action: NDArray[np.float32],
    normalized_image: NDArray[np.float32],
) -> dict[str, object]:
    """只保存小型统计与 shape；完整数组另存为压缩 NPZ。"""
    return {
        "artifact_id": "fixture_day07_array_summary",
        "result_type": "synthetic arrays; not a VLA experiment result",
        "image_shape": list(observation.image.shape),
        "image_dtype": str(observation.image.dtype),
        "normalized_dtype": str(normalized_image.dtype),
        "normalized_min": float(normalized_image.min()),
        "normalized_max": float(normalized_image.max()),
        "state_shape": list(observation.state.shape),
        "action_shape": list(action.shape),
        "action_values": action.tolist(),
    }


def save_artifacts(
    output_dir: Path,
    observation: FixtureObservation,
    action: NDArray[np.float32],
    normalized_image: NDArray[np.float32],
) -> tuple[Path, Path]:
    """保存精确数组 NPZ 与人类可读 JSON 摘要。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    array_path = output_dir / "fixture_arrays.npz"
    summary_path = output_dir / "array_summary.json"
    np.savez_compressed(
        array_path,
        image=observation.image,
        normalized_image=normalized_image,
        state=observation.state,
        action=action,
    )
    summary = build_summary(observation, action, normalized_image)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return array_path, summary_path


def default_output_dir() -> Path:
    """输出进入被 Git 忽略的个人目录。"""
    root = Path(__file__).resolve().parents[2]
    return root / "learner_outputs/day07"


def build_parser() -> argparse.ArgumentParser:
    """定义可修改的图像尺寸、动作尺度和输出目录。"""
    parser = argparse.ArgumentParser(description="生成并校验 fixture 图像、状态和动作数组。")
    parser.add_argument("--height", type=int, default=4, help="fixture 图像高度")
    parser.add_argument("--width", type=int, default=6, help="fixture 图像宽度")
    parser.add_argument("--action-scale", type=float, default=1.0, help="运动动作缩放")
    parser.add_argument("--output-dir", type=Path, default=default_output_dir())
    return parser


def main() -> int:
    """运行完整数组管线；契约错误返回 2。"""
    args = build_parser().parse_args()
    try:
        observation = build_fixture_observation(args.height, args.width)
        action = build_fixture_action(args.action_scale)
        validate_observation(observation)
        validate_action(action)
        normalized = normalize_image(observation.image)
        array_path, summary_path = save_artifacts(
            args.output_dir, observation, action, normalized
        )
    except (OSError, ArrayContractError) as error:
        print(f"数组管线失败：{error}", file=sys.stderr)
        return 2

    print("=== VLA-RelComp Day 7 ===")
    print(f"Image: shape={observation.image.shape}, dtype={observation.image.dtype}")
    print(f"State: shape={observation.state.shape}, dtype={observation.state.dtype}")
    print(f"Action: shape={action.shape}, dtype={action.dtype}")
    print(f"Saved arrays: {array_path.resolve()}")
    print(f"Saved summary: {summary_path.resolve()}")
    print("Result type: synthetic arrays; not a VLA experiment result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
