#!/usr/bin/env python3
"""由 episode 结果计算任务级成功率、Wilson 区间与 macro/micro 汇总。"""

from __future__ import annotations

import argparse
import csv
import json
from math import sqrt
from pathlib import Path

FIELDS = ("task_id", "planned_n", "valid_n", "missing_n", "successes", "success_rate", "wilson_low", "wilson_high")
Z95 = 1.959963984540054


def wilson(successes: int, trials: int, z: float = Z95) -> tuple[float, float]:
    if trials <= 0 or not 0 <= successes <= trials:
        raise ValueError("Wilson 要求 0 <= successes <= trials 且 trials > 0")
    p = successes / trials
    denominator = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denominator
    margin = z * sqrt(p * (1 - p) / trials + z * z / (4 * trials**2)) / denominator
    return center - margin, center + margin


def rounded(value: float) -> str:
    return f"{value:.6f}"


def compute(path: Path) -> tuple[list[dict[str, str | int]], dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        raw = list(csv.DictReader(handle))
    episode_ids = [row.get("episode_id", "") for row in raw]
    if not raw or any(not value for value in episode_ids) or len(episode_ids) != len(set(episode_ids)):
        raise ValueError("episode_id 必须非空且唯一")
    groups: dict[int, list[dict[str, str]]] = {}
    for row in raw:
        try:
            task_id = int(row["task_id"])
        except (KeyError, ValueError) as exc:
            raise ValueError("task_id 必须是非负整数") from exc
        if task_id < 0 or row.get("status") not in {"COMPLETED", "ERROR"}:
            raise ValueError("task_id/status 非法")
        if row["status"] == "COMPLETED" and row.get("success") not in {"0", "1"}:
            raise ValueError("COMPLETED 的 success 必须为 0/1")
        if row["status"] == "ERROR" and row.get("success", "") != "":
            raise ValueError("ERROR 的 success 必须为空")
        groups.setdefault(task_id, []).append(row)

    task_rows: list[dict[str, str | int]] = []
    for task_id, rows in sorted(groups.items()):
        valid = [row for row in rows if row["status"] == "COMPLETED"]
        if not valid:
            raise ValueError(f"task {task_id} 没有有效 episode，不能计算成功率")
        successes = sum(int(row["success"]) for row in valid)
        low, high = wilson(successes, len(valid))
        task_rows.append({"task_id": task_id, "planned_n": len(rows), "valid_n": len(valid),
            "missing_n": len(rows) - len(valid), "successes": successes,
            "success_rate": rounded(successes / len(valid)), "wilson_low": rounded(low), "wilson_high": rounded(high)})

    total_valid = sum(int(row["valid_n"]) for row in task_rows)
    total_successes = sum(int(row["successes"]) for row in task_rows)
    total_planned = sum(int(row["planned_n"]) for row in task_rows)
    micro_low, micro_high = wilson(total_successes, total_valid)
    macro_rate = sum(int(row["successes"]) / int(row["valid_n"]) for row in task_rows) / len(task_rows)
    report = {
        "task_count": len(task_rows), "planned_n": total_planned, "valid_n": total_valid,
        "missing_n": total_planned - total_valid, "successes": total_successes,
        "micro": {"successes": total_successes, "valid_n": total_valid,
                  "success_rate": rounded(total_successes / total_valid),
                  "wilson_low": rounded(micro_low), "wilson_high": rounded(micro_high)},
        "macro": {"task_count": len(task_rows), "success_rate": rounded(macro_rate),
                  "interval": "not_computed_by_naive_binomial_wilson"},
        "boundary": "synthetic episode fixture; ERROR rows reported as missing and excluded from valid denominator",
    }
    return task_rows, report


def write_csv(path: Path, rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--task-stats", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    rows, report = compute(args.input); write_csv(args.task_stats, rows)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: tasks={report['task_count']} valid={report['valid_n']}/{report['planned_n']} micro={report['micro']['success_rate']} macro={report['macro']['success_rate']}")


if __name__ == "__main__":
    main()
