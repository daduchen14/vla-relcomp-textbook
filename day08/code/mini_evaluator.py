"""Day 8 工程版本：运行可重复的 fixture CPU episode 并保存证据。

这是教学用一维环境，不是 VLA-Arena、机器人或模型评测。
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol


class EpisodeContractError(ValueError):
    """episode 配置或策略动作违反契约。"""


@dataclass(frozen=True)
class Observation:
    """策略在一个 step 开始时可见的信息。"""

    position: float
    target: float


@dataclass(frozen=True)
class StepRecord:
    """一次环境转移的完整教学记录。"""

    episode_id: str
    step_index: int
    position_before: float
    target: float
    action: float
    position_after: float
    distance_after: float
    terminated: bool
    truncated: bool
    success: bool


class Policy(Protocol):
    """任何策略只要实现 act(observation) 就能被 evaluator 调用。"""

    def act(self, observation: Observation) -> float:
        """根据 observation 返回一个标量动作。"""


class FixtureLineWorld:
    """一维确定性环境：智能体沿数轴靠近目标。"""

    def __init__(self, target: float, tolerance: float, max_action: float) -> None:
        if tolerance <= 0 or max_action <= 0:
            raise EpisodeContractError("tolerance 和 max_action 必须为正数")
        self.target = float(target)
        self.tolerance = float(tolerance)
        self.max_action = float(max_action)
        self.position = 0.0

    def reset(self, start: float) -> Observation:
        """显式重置 episode 状态并返回第一份 observation。"""
        if not math.isfinite(start):
            raise EpisodeContractError("start 必须是有限数")
        self.position = float(start)
        return self.observe()

    def observe(self) -> Observation:
        """只返回策略获准看到的位置与目标。"""
        return Observation(position=self.position, target=self.target)

    def is_success(self) -> bool:
        """success 只由环境 predicate 判定，不由策略自报。"""
        return abs(self.target - self.position) <= self.tolerance

    def step(self, action: float) -> tuple[Observation, bool]:
        """校验动作、更新状态并返回新 observation 与 success。"""
        if not math.isfinite(action):
            raise EpisodeContractError("action 必须是有限数")
        clipped = max(-self.max_action, min(self.max_action, float(action)))
        self.position += clipped
        return self.observe(), self.is_success()


class ProportionalFixturePolicy:
    """把目标误差乘 gain 的确定性教学策略。"""

    def __init__(self, gain: float) -> None:
        if not math.isfinite(gain):
            raise EpisodeContractError("gain 必须是有限数")
        self.gain = float(gain)

    def act(self, observation: Observation) -> float:
        return self.gain * (observation.target - observation.position)


def run_episode(
    episode_id: str,
    environment: FixtureLineWorld,
    policy: Policy,
    start: float,
    max_steps: int,
) -> tuple[list[StepRecord], bool, str]:
    """运行一个 episode，明确区分 success 终止与步数截断。"""
    if not episode_id.startswith("fixture_"):
        raise EpisodeContractError("episode_id 必须以 fixture_ 开头")
    if max_steps <= 0:
        raise EpisodeContractError("max_steps 必须为正整数")

    observation = environment.reset(start)
    records: list[StepRecord] = []

    # reset 后若已满足目标，episode 可零动作成功；这里记录 termination reason，不伪造 step。
    if environment.is_success():
        return records, True, "success_at_reset"

    for step_index in range(max_steps):
        position_before = observation.position
        action = policy.act(observation)
        observation, success = environment.step(action)
        is_last_allowed_step = step_index + 1 == max_steps
        truncated = is_last_allowed_step and not success
        records.append(
            StepRecord(
                episode_id=episode_id,
                step_index=step_index,
                position_before=position_before,
                target=observation.target,
                action=float(action),
                position_after=observation.position,
                distance_after=abs(observation.target - observation.position),
                terminated=success,
                truncated=truncated,
                success=success,
            )
        )
        if success:
            return records, True, "success"

    return records, False, "max_steps"


def write_artifacts(
    output_dir: Path,
    episode_id: str,
    records: list[StepRecord],
    success: bool,
    termination_reason: str,
) -> tuple[Path, Path]:
    """写逐 step CSV 与 episode JSON 摘要。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    steps_path = output_dir / "fixture_steps.csv"
    summary_path = output_dir / "fixture_episode_summary.json"

    fieldnames = list(StepRecord.__dataclass_fields__)
    with steps_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(asdict(record) for record in records)

    summary = {
        "episode_id": episode_id,
        "result_type": "synthetic CPU episode; not a VLA experiment result",
        "success": success,
        "step_count": len(records),
        "termination_reason": termination_reason,
        # reset 即成功时没有 step record；未知的精确初态距离用 null，而不是猜成 0。
        "final_distance": records[-1].distance_after if records else None,
        "steps_path": str(steps_path),
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return steps_path, summary_path


def default_output_dir() -> Path:
    """默认输出到 Git 忽略的个人练习目录。"""
    return Path(__file__).resolve().parents[2] / "learner_outputs/day08"


def build_parser() -> argparse.ArgumentParser:
    """定义可做控制变量实验的参数。"""
    parser = argparse.ArgumentParser(description="运行 fixture 一维 CPU episode。")
    parser.add_argument("--episode-id", default="fixture_day08_episode_001")
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--target", type=float, default=1.0)
    parser.add_argument("--tolerance", type=float, default=0.05)
    parser.add_argument("--max-action", type=float, default=0.25)
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--max-steps", type=int, default=6)
    parser.add_argument("--output-dir", type=Path, default=default_output_dir())
    return parser


def main() -> int:
    """运行 evaluator；基础设施错误返回 2，合法 episode 失败仍返回 0。"""
    args = build_parser().parse_args()
    try:
        environment = FixtureLineWorld(args.target, args.tolerance, args.max_action)
        policy = ProportionalFixturePolicy(args.gain)
        records, success, reason = run_episode(
            args.episode_id, environment, policy, args.start, args.max_steps
        )
        steps_path, summary_path = write_artifacts(
            args.output_dir, args.episode_id, records, success, reason
        )
    except (OSError, EpisodeContractError) as error:
        print(f"evaluator 失败：{error}", file=sys.stderr)
        return 2

    print("=== VLA-RelComp Day 8 ===")
    print(f"Episode: {args.episode_id}")
    print(f"Success: {success}")
    print(f"Steps: {len(records)}")
    print(f"Termination: {reason}")
    print(f"Saved steps: {steps_path.resolve()}")
    print(f"Saved summary: {summary_path.resolve()}")
    print("Result type: synthetic CPU episode; not a VLA experiment result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
