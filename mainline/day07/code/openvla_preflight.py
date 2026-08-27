#!/usr/bin/env python3
"""在 Day 4 基础检查上增加 OpenVLA 7B 显存门槛。"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from mainline.day04.code.real_preflight import collect as collect_base

MIN_MEMORY_MIB = 24_000


def evaluate(base: dict, memory_mib: int) -> dict:
    checks = {"day04_episode_ready": base["ready_for_real_episode"],
              "gpu_memory_at_least_24000_mib": memory_mib >= MIN_MEMORY_MIB}
    return {"base_preflight": base, "gpu_memory_mib": memory_mib,
            "checks": checks, "ready_for_openvla_pilot": all(checks.values()),
            "blockers": [name for name, passed in checks.items() if not passed],
            "source_kind": "real_openvla_preflight_not_episode"}


def collect(upstream: Path) -> dict:
    base, memory_mib = collect_base(upstream), 0
    if shutil.which("nvidia-smi"):
        probe = subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                               text=True, capture_output=True)
        if probe.returncode == 0:
            memory_mib = max(int(line.strip()) for line in probe.stdout.splitlines() if line.strip())
    return evaluate(base, memory_mib)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True); args = parser.parse_args()
    report = collect(args.upstream.resolve()); args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("READY" if report["ready_for_openvla_pilot"] else "NOT READY: " + ", ".join(report["blockers"]))


if __name__ == "__main__": main()
