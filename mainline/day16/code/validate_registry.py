#!/usr/bin/env python3
"""验证主外键、稳定 ID、状态相关缺失值和证据命名。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path, PurePosixPath

try: from .build_registry import EPISODE_FIELDS, RUN_FIELDS, schema, stable_id
except ImportError: from build_registry import EPISODE_FIELDS, RUN_FIELDS, schema, stable_id


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def validate(runs_path: Path, episodes_path: Path, schema_path: Path) -> dict:
    runs, episodes = read(runs_path), read(episodes_path)
    if json.loads(schema_path.read_text()) != schema(): raise ValueError("schema contract 被修改")
    if not runs or set(runs[0]) != set(RUN_FIELDS) or not episodes or set(episodes[0]) != set(EPISODE_FIELDS):
        raise ValueError("registry 字段不完整")
    run_ids = [row["run_id"] for row in runs]; episode_ids = [row["episode_id"] for row in episodes]
    if len(run_ids) != len(set(run_ids)) or len(episode_ids) != len(set(episode_ids)): raise ValueError("主键重复")
    for row in runs:
        identity = {key: int(row[key]) if key == "level" else row[key] for key in
                    ("batch_name", "protocol_lock_sha256", "model_id", "model_revision",
                     "inference_config_sha256", "suite", "level")}
        if row["run_id"] != stable_id("run-", identity): raise ValueError("run_id 与冻结身份不一致")
    run_set = set(run_ids)
    for row in episodes:
        if row["run_id"] not in run_set: raise ValueError("episode.run_id 外键悬空")
        identity = {key: int(row[key]) if key != "run_id" else row[key]
                    for key in ("run_id", "task_id", "seed", "init_state_index")}
        if row["episode_id"] != stable_id("ep-", identity): raise ValueError("episode_id 与身份不一致")
        if row["status"] == "PLANNED" and any(row[key] != "" for key in ("success", "steps", "wall_seconds", "exception")):
            raise ValueError("PLANNED 结果字段必须为空，不得把缺失写 0")
        if row["status"] == "COMPLETED" and any(row[key] == "" for key in ("success", "steps", "wall_seconds")):
            raise ValueError("COMPLETED 缺结果")
        for key in ("result_path", "event_log_path", "video_path", "exception_log_path"):
            path = PurePosixPath(row[key]); expected = ("learner_outputs", "evidence", row["run_id"], row["episode_id"])
            if path.parts[:4] != expected or ".." in path.parts: raise ValueError(f"{key} 命名越界/错配")
    counts = {run_id: sum(row["run_id"] == run_id for row in episodes) for run_id in run_ids}
    if any(int(row["planned_episode_count"]) != counts[row["run_id"]] for row in runs): raise ValueError("run episode count 不一致")
    return {"run_count": len(runs), "episode_count": len(episodes), "planned_count": sum(row["status"] == "PLANNED" for row in episodes),
            "primary_keys_unique": True, "foreign_keys_valid": True, "missing_policy_valid": True}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--runs", type=Path, required=True)
    p.add_argument("--episodes", type=Path, required=True); p.add_argument("--schema", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True); args = p.parse_args(); result = validate(args.runs, args.episodes, args.schema)
    args.report.parent.mkdir(parents=True, exist_ok=True); args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: runs={result['run_count']} episodes={result['episode_count']} planned={result['planned_count']}")


if __name__ == "__main__": main()
