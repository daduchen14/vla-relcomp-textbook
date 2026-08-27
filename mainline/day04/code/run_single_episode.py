#!/usr/bin/env python3
"""在合格 Linux/NVIDIA 环境调用锁定 random evaluator 跑一个真实 episode。"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from .real_preflight import LOCKED, collect
except ImportError:
    from real_preflight import LOCKED, collect

SUITE = "extrapolation_preposition_combinations"


def write_registry(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader(); writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--gate-config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    upstream, output = args.upstream.resolve(), args.output_dir.resolve()
    gate = json.loads(args.gate_config.read_text(encoding="utf-8"))
    os.environ.setdefault("MUJOCO_GL", "egl")
    os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
    preflight = collect(upstream)
    output.mkdir(parents=True, exist_ok=True)
    (output / "preflight.json").write_text(json.dumps(preflight, ensure_ascii=False, indent=2) + "\n")
    if not preflight["ready_for_real_episode"]:
        raise SystemExit("Preflight blocked real episode: " + ", ".join(preflight["blockers"]))

    # 只有 preflight 通过后才导入真实 VLA-Arena 及其 MuJoCo/torch 依赖。
    sys.path.insert(0, str(upstream))
    from vla_arena.models.random import evaluator
    from vla_arena.vla_arena import benchmark

    cfg = evaluator.EvaluatorConfig(
        task_suite_name=SUITE, task_level=gate["level"], num_steps_wait=10,
        num_trials_per_task=1, seed=gate["seed"], use_wandb=False,
        use_local_log=True, local_log_dir=str(output), save_video_mode="all",
        init_state_selection_mode="first", init_state_offset=gate["init_state_index"],
    )
    run_id = f"gate-{gate['form']}-L{gate['level']}-T{gate['task_id']}-S{gate['seed']}"
    log_path, video_path = output / f"{run_id}.log", output / f"{run_id}.mp4"
    log_file = log_path.open("w", encoding="utf-8")
    env = None
    try:
        suite = benchmark.get_benchmark_dict()[SUITE]()
        task = suite.get_task_by_level_id(gate["level"], gate["task_id"])
        initial_states = suite.get_task_init_states(gate["level"], gate["task_id"])
        initial_state = initial_states[gate["init_state_index"]]
        env, description = evaluator.make_env(task, cfg)
        rng = evaluator.initialize_model(cfg)
        success, frames, cost = evaluator.run_episode(
            cfg, env, description, rng, initial_state=initial_state, log_file=log_file
        )
        evaluator._save_rollout_video(frames, video_path)
        row = {
            "run_id": run_id, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "commit": LOCKED, "suite": SUITE, "level": gate["level"],
            "task_id": gate["task_id"], "task_name": task.name,
            "seed": gate["seed"], "init_state_index": gate["init_state_index"],
            "status": "completed", "success": str(bool(success)).lower(),
            "cost": float(cost), "frame_count": len(frames),
            "log_path": str(log_path), "video_path": str(video_path),
            "source_kind": "real_vla_arena_episode",
        }
        write_registry(output / "episode_registry.csv", row)
        print(f"COMPLETED: success={success} frames={len(frames)} cost={cost}")
        print(f"Saved: {output / 'episode_registry.csv'}")
    except Exception as exc:
        failure = {"status": "infrastructure_error", "type": type(exc).__name__,
                   "message": str(exc), "command": sys.argv, "commit": LOCKED}
        (output / "infrastructure_error.json").write_text(json.dumps(failure, indent=2) + "\n")
        raise
    finally:
        if env is not None and hasattr(env, "close"): env.close()
        log_file.close()


if __name__ == "__main__":
    main()
