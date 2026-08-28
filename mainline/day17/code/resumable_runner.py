#!/usr/bin/env python3
"""用脚本化 executor 演练 checkpoint、retry、原子写与幂等续跑。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

TERMINAL = {"COMPLETED", "INVALID", "FAILED"}
OUTCOMES = {"COMPLETED_SUCCESS", "COMPLETED_FAILURE", "RETRYABLE_ERROR", "INVALID"}


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8"); os.replace(temporary, path)


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle); return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    temporary = path.with_name(path.name + ".tmp"); temporary.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    os.replace(temporary, path)


def load_checkpoint(path: Path, episode_ids: set[str]) -> dict:
    if not path.exists(): return {"schema_version": "day17_checkpoint_v1", "episodes": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "day17_checkpoint_v1" or not set(data.get("episodes", {})).issubset(episode_ids):
        raise ValueError("checkpoint schema 或 episode 集合不匹配")
    return data


def run_batch(input_registry: Path, output_registry: Path, checkpoint_path: Path,
              executor_path: Path, artifact_root: Path, max_work_items: int | None = None) -> dict:
    fields, source_rows = read_csv(input_registry)
    if output_registry.exists(): out_fields, rows = read_csv(output_registry)
    else: out_fields, rows = fields, [dict(row) for row in source_rows]
    if out_fields != fields or {row["episode_id"] for row in rows} != {row["episode_id"] for row in source_rows}:
        raise ValueError("输出 registry 与输入 identity 集合不一致")
    config = json.loads(executor_path.read_text(encoding="utf-8")); max_attempts = int(config["max_attempts"])
    if max_attempts < 1 or not config["executor_kind"].startswith("scripted_fixture"):
        raise ValueError("Day 17 只允许运行脚本化免费 executor")
    checkpoint = load_checkpoint(checkpoint_path, {row["episode_id"] for row in rows}); processed = 0
    for row in rows:
        episode_id = row["episode_id"]; state = checkpoint["episodes"].setdefault(
            episode_id, {"attempts": 0, "status": row["status"], "last_error": "", "result_sha256": ""})
        if state["status"] in TERMINAL: continue
        if max_work_items is not None and processed >= max_work_items: break
        state["attempts"] += 1; processed += 1; task_outcomes = config["outcomes_by_task"].get(row["task_id"])
        if not task_outcomes: raise ValueError(f"task {row['task_id']} 没有 scripted outcome")
        outcome = task_outcomes[min(state["attempts"] - 1, len(task_outcomes) - 1)]
        if outcome not in OUTCOMES: raise ValueError(f"未知 outcome: {outcome}")
        evidence_dir = artifact_root / row["run_id"] / episode_id; evidence_dir.mkdir(parents=True, exist_ok=True)
        row.update({"result_path": str(evidence_dir / "result.json"), "exception_log_path": str(evidence_dir / "exception.txt")})
        if outcome.startswith("COMPLETED"):
            success = outcome == "COMPLETED_SUCCESS"; result = {"episode_id": episode_id, "success": success,
                "attempt": state["attempts"], "source_kind": config["executor_kind"], "real_environment_run": False}
            payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"; atomic_text(Path(row["result_path"]), payload)
            state.update({"status": "COMPLETED", "last_error": "",
                          "result_sha256": hashlib.sha256(payload.encode()).hexdigest()})
            row.update({"status": "COMPLETED", "success": "1" if success else "0",
                        "steps": str(10 + state["attempts"]), "wall_seconds": "0.01", "exception": ""})
        elif outcome == "INVALID":
            atomic_text(Path(row["exception_log_path"]), "synthetic invalid environment fixture\n")
            state.update({"status": "INVALID", "last_error": "synthetic invalid environment fixture"})
            row.update({"status": "INVALID", "success": "", "steps": "", "wall_seconds": "0.01",
                        "exception": state["last_error"]})
        else:
            state.update({"status": "RUNNING", "last_error": "synthetic retryable error"})
            atomic_text(Path(row["exception_log_path"]), state["last_error"] + "\n")
            row.update({"status": "RUNNING", "exception": state["last_error"]})
            if state["attempts"] >= max_attempts:
                state["status"] = row["status"] = "FAILED"
        atomic_text(checkpoint_path, json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n")
        write_csv(output_registry, fields, rows)
    if not output_registry.exists(): write_csv(output_registry, fields, rows)
    summary = {status: sum(state["status"] == status for state in checkpoint["episodes"].values())
               for status in ("COMPLETED", "INVALID", "FAILED", "RUNNING")}
    summary.update({"processed_this_call": processed, "episode_count": len(rows), "executor_kind": config["executor_kind"]})
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--input-registry", type=Path, required=True)
    p.add_argument("--output-registry", type=Path, required=True); p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--executor", type=Path, required=True); p.add_argument("--artifact-root", type=Path, required=True)
    p.add_argument("--max-work-items", type=int); args = p.parse_args(); result = run_batch(
        args.input_registry, args.output_registry, args.checkpoint, args.executor, args.artifact_root, args.max_work_items)
    print("PASS: " + " ".join(f"{key}={value}" for key, value in result.items()))


if __name__ == "__main__": main()
