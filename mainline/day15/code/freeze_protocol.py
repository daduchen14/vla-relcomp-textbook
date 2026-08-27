#!/usr/bin/env python3
"""冻结代码、模型、任务、口径与关键文件 hash，生成不可含糊的 protocol lock。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
REQUIRED = ("lock_name", "mode", "model_id", "model_revision", "suite", "levels",
            "trials_per_task", "seed_policy", "success_field", "invalid_episode_rule",
            "training_scope", "held_out_scope", "evidence_required", "files_to_hash", "source_kind")


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_spec(spec: dict) -> None:
    missing = [key for key in REQUIRED if key not in spec]
    if missing: raise ValueError(f"lock spec 缺字段：{missing}")
    if spec["suite"] != "extrapolation_preposition_combinations" or spec["levels"] != [0, 1, 2]:
        raise ValueError("suite/levels 偏离正式协议")
    if not isinstance(spec["trials_per_task"], int) or spec["trials_per_task"] < 1:
        raise ValueError("trials_per_task 必须为正整数")
    if spec["success_field"] != "info.success" or "L1_L2_never" not in spec["held_out_scope"]:
        raise ValueError("success 或 L1/L2 保留口径不合格")
    text = json.dumps(spec).casefold()
    if spec["mode"] == "formal" and any(word in text for word in ("placeholder", "synthetic", "fill_after")):
        raise ValueError("formal lock 禁止 placeholder/synthetic")
    if spec["mode"] not in {"formal", "synthetic_demonstration"}: raise ValueError("未知 lock mode")


def file_records(root: Path, names: list[str]) -> list[dict]:
    if len(names) != len(set(names)) or not names: raise ValueError("files_to_hash 为空或重复")
    records = []
    for name in sorted(names):
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts: raise ValueError("只能 hash 仓库内相对路径")
        path = (root / relative).resolve()
        if not path.is_file() or not path.is_relative_to(root.resolve()): raise ValueError(f"锁定文件不存在/越界：{name}")
        records.append({"path": relative.as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)})
    return records


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, text=True, capture_output=True).stdout.strip()


def build(root: Path, upstream: Path, spec_path: Path) -> dict:
    root, upstream = root.resolve(), upstream.resolve(); spec = json.loads(spec_path.read_text(encoding="utf-8")); validate_spec(spec)
    if git(upstream, "rev-parse", "HEAD") != LOCKED: raise ValueError("VLA-Arena 不是锁定 commit")
    dirty = git(root, "status", "--porcelain").splitlines()
    if spec["mode"] == "formal" and dirty: raise ValueError("formal lock 要求教材/项目仓库 clean")
    payload = {"schema_version": "baseline_protocol_lock_v1", "lock_name": spec["lock_name"],
        "mode": spec["mode"], "textbook_commit": git(root, "rev-parse", "HEAD"), "upstream_commit": LOCKED,
        "model": {"id": spec["model_id"], "revision": spec["model_revision"]}, "suite": spec["suite"],
        "levels": spec["levels"], "trials_per_task": spec["trials_per_task"], "seed_policy": spec["seed_policy"],
        "success_field": spec["success_field"], "invalid_episode_rule": spec["invalid_episode_rule"],
        "training_scope": spec["training_scope"], "held_out_scope": spec["held_out_scope"],
        "evidence_required": spec["evidence_required"], "locked_files": file_records(root, spec["files_to_hash"]),
        "spec_sha256": sha(spec_path), "worktree_clean_at_lock": not dirty, "source_kind": spec["source_kind"]}
    payload["lock_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--repo", type=Path, default=Path.cwd())
    p.add_argument("--upstream", type=Path, required=True); p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True); args = p.parse_args(); result = build(args.repo, args.upstream, args.spec)
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: {result['mode']} lock={result['lock_sha256'][:16]} files={len(result['locked_files'])} clean={result['worktree_clean_at_lock']}")


if __name__ == "__main__": main()
