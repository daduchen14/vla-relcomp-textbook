#!/usr/bin/env python3
"""合格 Linux/NVIDIA 环境中下载锁定 checkpoint 并跑一个真实 SmolVLA episode。"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from mainline.day04.code.real_preflight import LOCKED, collect  # noqa: E402
from mainline.day06.code.build_pilot_manifest import build_manifest  # noqa: E402


def write_registry(path: Path, row: dict) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row)); writer.writeheader(); writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--pilot-config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    upstream, output = args.upstream.resolve(), args.output_dir.resolve()
    cfg_data = json.loads(args.pilot_config.read_text(encoding="utf-8"))
    # 先以锁定源码验证单任务、checkpoint SHA 和运行口径，再接触 GPU / 网络。
    build_manifest(upstream, args.pilot_config)
    os.environ.setdefault("MUJOCO_GL", "egl"); os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
    output.mkdir(parents=True, exist_ok=True)
    preflight = collect(upstream)
    (output / "preflight.json").write_text(json.dumps(preflight, ensure_ascii=False, indent=2) + "\n")
    if not preflight["ready_for_real_episode"]:
        raise SystemExit("Preflight blocked real pilot: " + ", ".join(preflight["blockers"]))

    sys.path.insert(0, str(upstream))
    from huggingface_hub import snapshot_download
    from vla_arena.models.smolvla import evaluator
    from vla_arena.vla_arena import benchmark

    checkpoint = snapshot_download(repo_id=cfg_data["checkpoint_repo"],
                                   revision=cfg_data["checkpoint_revision"])
    cfg = evaluator.Args(policy_path=checkpoint, device="cuda", task_suite_name=cfg_data["suite"],
                         task_level=0, num_steps_wait=10, num_trials_per_task=1,
                         init_state_selection_mode="first", init_state_offset=cfg_data["init_state_index"],
                         use_local_log=True, local_log_dir=str(output), use_wandb=False,
                         seed=cfg_data["seed"], video_out_path=str(output), save_video_mode="all",
                         use_replacements=False)
    log_path, video_path = output / "episode.log", output / "rollout.mp4"
    env, log_file = None, log_path.open("w", encoding="utf-8")
    try:
        suite = benchmark.get_benchmark_dict()[cfg_data["suite"]]()
        task = suite.get_task_by_level_id(0, cfg_data["task_id"])
        initial_state = suite.get_task_init_states(0, cfg_data["task_id"])[cfg_data["init_state_index"]]
        env, description = evaluator._get_vla_arena_env(task, evaluator.VLA_ARENA_ENV_RESOLUTION,
                                                        cfg_data["seed"])
        if isinstance(task.language, list): description = task.language[0]
        policy = evaluator.initialize_model(cfg)
        success, frames, cost = evaluator.run_episode(cfg, env, description, policy, {}, cfg_data["suite"],
                                                      cfg_data["max_steps"], initial_state, log_file)
        if not frames:
            raise RuntimeError("episode 没有产生 frame，不能登记为 completed pilot")
        generated = evaluator.save_rollout_video(frames, 1, success, description, output, log_file)
        Path(generated).replace(video_path)
        row = {"run_id": f"smolvla-L0-T{cfg_data['task_id']}-S{cfg_data['seed']}",
               "timestamp_utc": datetime.now(timezone.utc).isoformat(), "commit": LOCKED,
               "checkpoint_repo": cfg_data["checkpoint_repo"],
               "checkpoint_revision": cfg_data["checkpoint_revision"], "suite": cfg_data["suite"],
               "level": 0, "task_id": cfg_data["task_id"], "task_name": task.name,
               "seed": cfg_data["seed"], "init_state_index": cfg_data["init_state_index"],
               "status": "completed", "success": str(bool(success)).lower(), "cost": float(cost),
               "frame_count": len(frames), "log_path": str(log_path.resolve()),
               "video_path": str(video_path.resolve()), "source_kind": "real_smolvla_vla_arena_episode"}
        write_registry(output / "episode_registry.csv", row)
        print(f"COMPLETED: success={success} frames={len(frames)} cost={cost}")
    except Exception as exc:
        failure = {"status": "infrastructure_error", "type": type(exc).__name__, "message": str(exc),
                   "commit": LOCKED, "checkpoint_revision": cfg_data.get("checkpoint_revision")}
        (output / "infrastructure_error.json").write_text(json.dumps(failure, indent=2) + "\n")
        raise
    finally:
        if env is not None and hasattr(env, "close"): env.close()
        log_file.close()


if __name__ == "__main__":
    main()
