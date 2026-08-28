#!/usr/bin/env python3
"""验收 Day 6 静态 pilot 计划；仅在提供 registry 时验收真实 pilot。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from .build_pilot_manifest import LOCKED, build_manifest
except ImportError:
    from build_pilot_manifest import LOCKED, build_manifest


def check_plan(upstream: Path, config: Path, manifest: Path) -> dict:
    actual, expected = json.loads(manifest.read_text(encoding="utf-8")), build_manifest(upstream, config)
    if actual != expected:
        raise ValueError("manifest 必须由锁定源码与给定 config 重新生成")
    if actual["real_model_run"] or actual["status"] != "planned":
        raise ValueError("静态计划不得冒充真实模型运行")
    return expected


def check_real(registry: Path, config: Path) -> None:
    cfg = json.loads(config.read_text(encoding="utf-8"))
    with registry.open(newline="", encoding="utf-8") as handle: rows = list(csv.DictReader(handle))
    if len(rows) != 1: raise ValueError("最小 pilot 必须恰好一个 episode row")
    row = rows[0]
    expected = {"commit": LOCKED, "checkpoint_repo": cfg["checkpoint_repo"],
                "checkpoint_revision": cfg["checkpoint_revision"], "suite": cfg["suite"],
                "level": "0", "task_id": str(cfg["task_id"]), "seed": str(cfg["seed"]),
                "init_state_index": str(cfg["init_state_index"]), "status": "completed",
                "source_kind": "real_smolvla_vla_arena_episode"}
    if any(row.get(k) != v for k, v in expected.items()):
        raise ValueError("真实 registry 与 config/锁定版本/checkpoint 不一致")
    if row.get("success") not in {"true", "false"} or int(row.get("frame_count", 0)) <= 0:
        raise ValueError("真实 pilot 必须有 boolean success 和非空 frame")
    for field in ("log_path", "video_path"):
        path = Path(row[field])
        if not path.is_file() or path.stat().st_size == 0: raise ValueError(f"缺少非空证据：{field}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--registry", type=Path)
    args = parser.parse_args()
    check_plan(args.upstream.resolve(), args.config, args.manifest)
    if args.registry:
        check_real(args.registry, args.config); print("PASS: Day 6 real SmolVLA pilot evidence")
    else:
        print("PASS: Day 6 locked static plan (real pilot not claimed)")


if __name__ == "__main__":
    main()
