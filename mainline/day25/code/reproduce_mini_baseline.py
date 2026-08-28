#!/usr/bin/env python3
"""从单一 spec 与空输出目录复现 synthetic mini baseline package。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

try:
    from mainline.day18.code.build_l0_registry import LOCKED, ident
    from mainline.day22.code.compute_baseline_stats import compute, write_csv as write_stats
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from mainline.day18.code.build_l0_registry import LOCKED, ident
    from mainline.day22.code.compute_baseline_stats import compute, write_csv as write_stats

MANIFEST_FIELDS = ("episode_id", "task_id", "trial_id", "seed", "init_state_index", "model_id",
                   "model_revision", "protocol_lock_sha256", "status", "success", "source_kind")
ARTIFACTS = ("manifest.csv", "registry.csv", "task_stats.csv", "baseline_report.json")


def write_rows(path: Path, rows: list[dict[str, str | int]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS); writer.writeheader(); writer.writerows(rows)


def reproduce(spec_path: Path, output_dir: Path) -> dict:
    if output_dir.exists() and any(output_dir.iterdir()): raise ValueError("输出目录必须为空，禁止复用旧 manifest/结果")
    output_dir.mkdir(parents=True, exist_ok=True)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    required = ("package_name", "locked_commit", "model_id", "model_revision", "protocol_lock_sha256",
                "task_ids", "trials_per_task", "seed_base", "init_state_indices", "synthetic_outcomes", "source_kind")
    if any(name not in spec for name in required): raise ValueError("mini baseline spec 缺字段")
    if spec["locked_commit"] != LOCKED or spec["source_kind"] not in {"synthetic_gate4_fixture", "synthetic_gate4_challenge"}:
        raise ValueError("锁定 commit/source boundary 不匹配")
    tasks = spec["task_ids"]; trials = int(spec["trials_per_task"]); inits = spec["init_state_indices"]
    if not tasks or tasks != sorted(set(tasks)) or trials <= 0 or len(inits) != trials or len(set(inits)) != trials:
        raise ValueError("task/trial/init spec 非法")
    outcomes = spec["synthetic_outcomes"]
    if set(outcomes) != {str(task) for task in tasks} or any(len(outcomes[str(task)]) != trials for task in tasks):
        raise ValueError("synthetic outcomes 必须覆盖 task×trial")

    manifest: list[dict[str, str | int]] = []
    for task_id in tasks:
        for trial_id in range(trials):
            success = outcomes[str(task_id)][trial_id]
            if success not in (0, 1): raise ValueError("synthetic outcome 必须为 0/1")
            seed = int(spec["seed_base"]) + task_id * 100 + trial_id
            episode_id = ident("mini-ep-", {"package": spec["package_name"], "task": task_id,
                "trial": trial_id, "seed": seed, "init": inits[trial_id]})
            manifest.append({"episode_id": episode_id, "task_id": task_id, "trial_id": trial_id, "seed": seed,
                "init_state_index": inits[trial_id], "model_id": spec["model_id"], "model_revision": spec["model_revision"],
                "protocol_lock_sha256": spec["protocol_lock_sha256"], "status": "PLANNED", "success": "",
                "source_kind": spec["source_kind"]})
    write_rows(output_dir / "manifest.csv", manifest)
    registry = [{**row, "status": "COMPLETED", "success": outcomes[str(row["task_id"])][int(row["trial_id"])]} for row in manifest]
    write_rows(output_dir / "registry.csv", registry)
    stats, report = compute(output_dir / "registry.csv"); write_stats(output_dir / "task_stats.csv", stats)
    (output_dir / "baseline_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    hashes = {name: hashlib.sha256((output_dir / name).read_bytes()).hexdigest() for name in ARTIFACTS}
    receipt = {"package_name": spec["package_name"], "locked_commit": spec["locked_commit"],
               "spec_sha256": hashlib.sha256(spec_path.read_bytes()).hexdigest(), "artifact_sha256": hashes,
               "episode_count": len(registry), "task_count": len(tasks), "adapter": "deterministic_synthetic_adapter",
               "gpu_used": False, "boundary": "pipeline reproduction fixture; not a VLA-Arena/model baseline"}
    (output_dir / "reproduction_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True); args = parser.parse_args()
    receipt = reproduce(args.spec, args.output_dir)
    print(f"PASS: package={receipt['package_name']} tasks={receipt['task_count']} episodes={receipt['episode_count']} gpu_used=false")


if __name__ == "__main__": main()
