#!/usr/bin/env python3
"""按真实内容评分 Day 0 A/B 卷，并生成基础补习路由。"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path

import numpy as np

ROUTES = {
    "task1": ["F01", "F05", "F06"], "task2": ["F02", "F03"],
    "task3": ["F04"], "task4": ["F07", "F09"], "task5": ["F08"],
}
CHAIN = ["observation", "policy", "action", "env.step", "success"]
ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "shared/fixtures/day00"


def load_form(form: str) -> dict:
    return json.loads((FIXTURES / f"form_{form.lower()}.json").read_text(encoding="utf-8"))


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def expected(form: str) -> dict:
    spec = load_form(form)
    probe = subprocess.run(spec["command"], text=True, capture_output=True)
    valid, rejected = [], []
    for row_number, row in enumerate(spec["records"], start=2):
        if row["success"] not in {"true", "false"}:
            rejected.append({"row_number": row_number, "episode_id": row["episode_id"]})
        else:
            valid.append({**row, "success": row["success"] == "true"})
    arrays = {}
    for name, item in spec["observation"].items():
        array = np.asarray(item["values"], dtype=item["dtype"])
        arrays[name] = {"shape": list(array.shape), "dtype": str(array.dtype),
                        "min": float(array.min()), "max": float(array.max())}
    final = spec["trace"][-1]
    terminal = "success" if final["info"]["success"] else "timeout" if final["info"]["timeout"] else "done"
    return {
        "task1": {"form_id": form, "stdout": probe.stdout.strip(), "returncode": probe.returncode},
        "task2_valid": valid, "task2_rejected": rejected,
        "task4": {"form_id": form, "arrays": arrays},
        "task5": {"form_id": form, "steps_executed": len(spec["trace"]),
                  "terminal_kind": terminal, "success": bool(final["info"]["success"]), "chain": CHAIN},
    }


def git_passed(workspace: Path, form: str) -> bool:
    repo, spec = workspace / "git_sandbox", load_form(form)
    try:
        status = subprocess.run(["git", "status", "--porcelain"], cwd=repo, check=True,
                                text=True, capture_output=True).stdout
        message = subprocess.run(["git", "log", "-1", "--format=%s"], cwd=repo, check=True,
                                 text=True, capture_output=True).stdout.strip()
        tracked = subprocess.run(["git", "ls-files"], cwd=repo, check=True,
                                 text=True, capture_output=True).stdout.splitlines()
        return (not status and message.startswith("diagnostic:") and tracked == ["settings.txt"]
                and (repo / "settings.txt").read_text() == spec["git"]["target_text"])
    except (OSError, subprocess.SubprocessError):
        return False


def grade(workspace: Path, form: str) -> dict:
    exp, artifacts = expected(form), workspace / "artifacts"
    checks = {}
    try: checks["task1"] = read_json(artifacts / "task1_process.json") == exp["task1"]
    except Exception: checks["task1"] = False
    try:
        valid = read_json(artifacts / "normalized_episodes.json")
        rejected = read_json(artifacts / "rejected_rows.json")
        rejected_core = [{"row_number": r["row_number"], "episode_id": r["episode_id"]} for r in rejected]
        checks["task2"] = valid == exp["task2_valid"] and rejected_core == exp["task2_rejected"]
    except Exception: checks["task2"] = False
    checks["task3"] = git_passed(workspace, form)
    try: checks["task4"] = read_json(artifacts / "task4_observation.json") == exp["task4"]
    except Exception: checks["task4"] = False
    try: checks["task5"] = read_json(artifacts / "task5_episode.json") == exp["task5"]
    except Exception: checks["task5"] = False
    gaps = sorted({route for task, passed in checks.items() if not passed for route in ROUTES[task]})
    return {"form_id": form, "tasks": checks, "recommended_foundations": gaps,
            "entry_ready": all(checks.values()), "deferred_diagnostics": [f"F{i:02d}" for i in range(10, 19)]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--form", choices=["A", "B"], required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    result = grade(args.workspace.resolve(), args.form)
    output = args.workspace / "diagnostic_result.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved: {output}")
    print("PASS: direct to mainline" if result["entry_ready"] else "REVIEW: " + ", ".join(result["recommended_foundations"]))
    raise SystemExit(0 if result["entry_ready"] else 2)


if __name__ == "__main__":
    main()
