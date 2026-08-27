#!/usr/bin/env python3
"""按锁定 blob 验收 Day 2 主追踪与变更配置挑战。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .trace_config import build_artifacts, parse_simple_yaml
except ImportError:
    from trace_config import build_artifacts, parse_simple_yaml

CHALLENGE_VALUES = {
    "model_name": "random",
    "task_suite_name": "extrapolation_preposition_combinations",
    "task_level": 2,
    "num_steps_wait": 10,
    "num_trials_per_task": 2,
    "use_local_log": True,
    "use_wandb": False,
    "seed": 19,
    "result_json_path": "learner_outputs/mainline/day02/challenge_results.json",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check(upstream: Path, config: Path, trace_path: Path, manifest_path: Path,
          challenge_config: Path, challenge_trace_path: Path) -> None:
    trace, manifest = build_artifacts(upstream, config)
    if read_json(trace_path) != trace or read_json(manifest_path) != manifest:
        raise ValueError("主追踪必须由锁定 blob 和当前 YAML 重新生成")
    if parse_simple_yaml(challenge_config) != CHALLENGE_VALUES:
        raise ValueError("独立挑战配置没有同时满足 level/trials/seed/本地证据约束")
    challenge_trace, _ = build_artifacts(upstream, challenge_config)
    if read_json(challenge_trace_path) != challenge_trace:
        raise ValueError("挑战 trace 与新配置的真实解析结果不一致，不能复制主示例后改 ID")
    if trace["config"] == challenge_trace["config"]:
        raise ValueError("独立挑战必须改变真实配置输入")
    print("PASS: Day 2 locked CLI trace, 15-task manifest, and changed-config challenge")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--challenge-config", type=Path, required=True)
    parser.add_argument("--challenge-trace", type=Path, required=True)
    args = parser.parse_args()
    check(args.upstream.resolve(), args.config.resolve(), args.trace, args.manifest,
          args.challenge_config.resolve(), args.challenge_trace)


if __name__ == "__main__":
    main()
