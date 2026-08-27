#!/usr/bin/env python3
"""Day 0 A/B 卷参考作答器；首次诊断前不要运行。"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from mainline.day00_diagnostic.code.grade_form import expected, load_form


def solve(workspace: Path, form: str) -> None:
    exp, artifacts = expected(form), workspace / "artifacts"
    artifacts.mkdir(exist_ok=True)
    outputs = {
        "task1_process.json": exp["task1"],
        "normalized_episodes.json": exp["task2_valid"],
        "rejected_rows.json": exp["task2_rejected"],
        "task4_observation.json": exp["task4"],
        "task5_episode.json": exp["task5"],
    }
    for name, payload in outputs.items():
        (artifacts / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    repo, spec = workspace / "git_sandbox", load_form(form)
    (repo / "settings.txt").write_text(spec["git"]["target_text"])
    scratch = repo / "scratch.txt"
    if scratch.exists():
        scratch.unlink()
    subprocess.run(["git", "add", "--", "settings.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", f"diagnostic: solve form {form}"], cwd=repo, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--form", choices=["A", "B"], required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    solve(args.workspace.resolve(), args.form)


if __name__ == "__main__":
    main()
