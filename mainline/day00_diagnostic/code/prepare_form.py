#!/usr/bin/env python3
"""在 learner_outputs 中准备 Day 0 A/B 卷和隔离 Git 练习仓库。"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "shared/fixtures/day00"


def load_form(form: str) -> dict:
    return json.loads((FIXTURES / f"form_{form.lower()}.json").read_text(encoding="utf-8"))


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def prepare(form: str, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(f"{output} 已存在；请保留证据并改用另一输出目录")
    spec = load_form(form)
    inputs = output / "inputs"
    artifacts = output / "artifacts"
    inputs.mkdir(parents=True)
    artifacts.mkdir()
    (output / "FORM.json").write_text(json.dumps({"form_id": form}, indent=2) + "\n")
    with (inputs / "episodes.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["episode_id", "level", "success"])
        writer.writeheader(); writer.writerows(spec["records"])
    for name in ("observation", "trace"):
        (inputs / f"{name}.json").write_text(
            json.dumps(spec[name], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    repo = output / "git_sandbox"
    repo.mkdir()
    run_git(repo, "init", "-q"); run_git(repo, "config", "user.name", "Day0 Learner")
    run_git(repo, "config", "user.email", "day0@example.invalid")
    (repo / "settings.txt").write_text(spec["git"]["base_text"], encoding="utf-8")
    run_git(repo, "add", "--", "settings.txt"); run_git(repo, "commit", "-qm", "baseline")
    (repo / "settings.txt").write_text(spec["git"]["target_text"], encoding="utf-8")
    (repo / "scratch.txt").write_text("这行不应进入最终提交。\n", encoding="utf-8")
    print(f"Prepared form {form}: {output}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--form", choices=["A", "B"], required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / f"learner_outputs/mainline/day00_diagnostic/form_{args.form}"
    prepare(args.form, output.resolve())


if __name__ == "__main__":
    main()
