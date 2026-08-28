#!/usr/bin/env python3
"""从冻结批次 spec 生成 run/episode registry、稳定主键和证据命名。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
RUN_FIELDS = ("run_id", "batch_name", "protocol_lock_sha256", "upstream_commit", "code_commit",
              "model_id", "model_revision", "inference_config_sha256", "suite", "level",
              "status", "planned_episode_count", "source_kind")
EPISODE_FIELDS = ("episode_id", "run_id", "task_id", "seed", "init_state_index", "status",
                  "success", "steps", "wall_seconds", "exception", "result_path", "event_log_path",
                  "video_path", "exception_log_path")


def stable_id(prefix: str, identity: dict) -> str:
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return prefix + hashlib.sha256(canonical.encode()).hexdigest()[:16]


def validate_spec(spec: dict) -> None:
    required = ("batch_name", "protocol_lock_sha256", "upstream_commit", "code_commit", "model_id",
                "model_revision", "inference_config_sha256", "suite", "level", "episodes", "source_kind")
    missing = [key for key in required if key not in spec]
    if missing: raise ValueError(f"registry spec 缺字段：{missing}")
    if spec["upstream_commit"] != LOCKED or spec["suite"] != "extrapolation_preposition_combinations":
        raise ValueError("upstream/suite 偏离锁定协议")
    for key in ("protocol_lock_sha256", "inference_config_sha256"):
        value = spec[key]
        if len(value) != 64 or any(char not in "0123456789abcdef" for char in value): raise ValueError(f"{key} 非 sha256")
    episodes = spec["episodes"]
    identities = [(row["task_id"], row["seed"], row["init_state_index"]) for row in episodes]
    if not episodes or len(identities) != len(set(identities)): raise ValueError("episode identity 为空或重复")
    if spec["level"] not in (0, 1, 2) or any(not 0 <= row["task_id"] < 5 for row in episodes):
        raise ValueError("level/task_id 越界")


def schema() -> dict:
    return {"schema_version": "run_episode_registry_v1",
            "primary_keys": {"runs": ["run_id"], "episodes": ["episode_id"]},
            "foreign_keys": {"episodes.run_id": "runs.run_id"},
            "planned_missing_policy": {"allowed_blank": ["success", "steps", "wall_seconds", "exception"],
                "meaning": "not_observed_yet; never encode as success=0"},
            "status_enum": ["PLANNED", "RUNNING", "COMPLETED", "INVALID", "FAILED"],
            "completed_required": ["success", "steps", "wall_seconds"],
            "evidence_root": "learner_outputs/evidence"}


def build(spec_path: Path) -> tuple[list[dict], list[dict], dict]:
    spec = json.loads(spec_path.read_text(encoding="utf-8")); validate_spec(spec)
    run_identity = {key: spec[key] for key in ("batch_name", "protocol_lock_sha256", "model_id",
                    "model_revision", "inference_config_sha256", "suite", "level")}
    run_id = stable_id("run-", run_identity)
    run = {"run_id": run_id, "batch_name": spec["batch_name"], "protocol_lock_sha256": spec["protocol_lock_sha256"],
           "upstream_commit": spec["upstream_commit"], "code_commit": spec["code_commit"], "model_id": spec["model_id"],
           "model_revision": spec["model_revision"], "inference_config_sha256": spec["inference_config_sha256"],
           "suite": spec["suite"], "level": spec["level"], "status": "PLANNED",
           "planned_episode_count": len(spec["episodes"]), "source_kind": spec["source_kind"]}
    episodes = []
    for item in spec["episodes"]:
        identity = {"run_id": run_id, "task_id": item["task_id"], "seed": item["seed"],
                    "init_state_index": item["init_state_index"]}
        episode_id = stable_id("ep-", identity); base = f"learner_outputs/evidence/{run_id}/{episode_id}"
        episodes.append({"episode_id": episode_id, "run_id": run_id, "task_id": item["task_id"],
            "seed": item["seed"], "init_state_index": item["init_state_index"], "status": "PLANNED",
            "success": "", "steps": "", "wall_seconds": "", "exception": "",
            "result_path": f"{base}/result.json", "event_log_path": f"{base}/events.json",
            "video_path": f"{base}/rollout.mp4", "exception_log_path": f"{base}/exception.txt"})
    return [run], episodes, schema()


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--runs", type=Path, required=True); p.add_argument("--episodes", type=Path, required=True)
    p.add_argument("--schema", type=Path, required=True); args = p.parse_args(); runs, episodes, contract = build(args.spec)
    write_csv(args.runs, RUN_FIELDS, runs); write_csv(args.episodes, EPISODE_FIELDS, episodes)
    args.schema.parent.mkdir(parents=True, exist_ok=True); args.schema.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: run={runs[0]['run_id']} planned episodes={len(episodes)}; result fields blank")


if __name__ == "__main__": main()
