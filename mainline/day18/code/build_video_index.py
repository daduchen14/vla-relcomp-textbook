#!/usr/bin/env python3
"""把 registry 的视频路径变成可核查索引；PLANNED 不创建假视频。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

FIELDS = ("episode_id", "task_id", "trial_id", "seed", "init_state_index", "episode_status",
          "video_path", "video_exists", "video_bytes", "video_sha256")


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def build(registry_path: Path, repo_root: Path) -> tuple[list[dict], dict]:
    registry = read(registry_path); ids = [row["episode_id"] for row in registry]
    if not registry or len(ids) != len(set(ids)): raise ValueError("registry 为空或 episode_id 重复")
    counts = Counter(row["task_id"] for row in registry)
    if set(counts) != {"0", "1", "2", "3", "4"} or len(set(counts.values())) != 1:
        raise ValueError("L0 五任务 planned denominator 不相等")
    rows = []
    for item in registry:
        video = Path(item["video_path"]); path = video if video.is_absolute() else repo_root / video
        exists = path.is_file(); digest = hashlib.sha256(path.read_bytes()).hexdigest() if exists else ""
        size = path.stat().st_size if exists else 0
        if item["status"] == "PLANNED" and exists: raise ValueError("PLANNED 不应已有视频；先核对旧证据串线")
        if item["status"] == "COMPLETED" and (not exists or size == 0 or path.suffix.lower() != ".mp4"):
            raise ValueError("COMPLETED 必须有非空 mp4")
        rows.append({"episode_id": item["episode_id"], "task_id": item["task_id"], "trial_id": item["trial_id"],
            "seed": item["seed"], "init_state_index": item["init_state_index"], "episode_status": item["status"],
            "video_path": item["video_path"], "video_exists": str(exists).lower(), "video_bytes": size,
            "video_sha256": digest})
    report = {"level": 0, "task_count": 5, "episodes_per_task": next(iter(counts.values())),
              "episode_count": len(registry), "completed_videos": sum(row["video_exists"] == "true" for row in rows),
              "planned_missing_videos": sum(row["episode_status"] == "PLANNED" and row["video_exists"] == "false" for row in rows),
              "source_boundary": "missing planned videos are expected; index is not baseline evidence"}
    return rows, report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--registry", type=Path, required=True)
    p.add_argument("--repo-root", type=Path, default=Path.cwd()); p.add_argument("--index", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True); args = p.parse_args(); rows, report = build(args.registry, args.repo_root)
    args.index.parent.mkdir(parents=True, exist_ok=True)
    with args.index.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: L0 video index episodes={report['episode_count']} completed={report['completed_videos']} planned_missing={report['planned_missing_videos']}")


if __name__ == "__main__": main()
