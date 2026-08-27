#!/usr/bin/env python3
"""只读检查 Linux/NVIDIA/headless/版本条件，绝不伪造 ready。"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"


def evaluate(snapshot: dict) -> dict:
    checks = {
        "linux": snapshot["os"] == "Linux",
        "python_3_11": snapshot["python"].startswith("3.11."),
        "locked_commit": snapshot["commit"] == LOCKED,
        "nvidia_smi": snapshot["nvidia_smi_returncode"] == 0,
        "mujoco_egl": snapshot["MUJOCO_GL"] == "egl",
        "pyopengl_egl": snapshot["PYOPENGL_PLATFORM"] == "egl",
    }
    return {**snapshot, "checks": checks,
            "ready_for_real_episode": all(checks.values()),
            "blockers": [name for name, passed in checks.items() if not passed],
            "source_kind": "real_local_preflight_not_episode"}


def collect(upstream: Path) -> dict:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=upstream, check=True,
                            text=True, capture_output=True).stdout.strip()
    executable = shutil.which("nvidia-smi")
    if executable:
        probe = subprocess.run([executable, "--query-gpu=name,memory.total,driver_version",
                                "--format=csv,noheader"], text=True, capture_output=True)
        nvidia_code, nvidia_output = probe.returncode, probe.stdout.strip()
    else:
        nvidia_code, nvidia_output = 127, "nvidia-smi not found"
    return evaluate({"os": platform.system(), "machine": platform.machine(),
                     "python": platform.python_version(), "python_executable": sys.executable,
                     "commit": commit, "nvidia_smi_returncode": nvidia_code,
                     "nvidia_smi_output": nvidia_output,
                     "MUJOCO_GL": os.environ.get("MUJOCO_GL"),
                     "PYOPENGL_PLATFORM": os.environ.get("PYOPENGL_PLATFORM")})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("learner_outputs/mainline/day04/preflight.json"))
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    report = collect(args.upstream.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("READY" if report["ready_for_real_episode"] else "NOT READY: " + ", ".join(report["blockers"]))
    print(f"Saved: {args.output}")
    if args.require_ready and not report["ready_for_real_episode"]: raise SystemExit(2)


if __name__ == "__main__":
    main()
