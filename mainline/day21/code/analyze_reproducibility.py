#!/usr/bin/env python3
"""统计配对重跑的 success 与四段事件一致性，保留原始分子/分母。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

STAGES = ("contact", "lift", "approach", "relation")
DETAIL_FIELDS = ("pair_id", "success_match", "matching_stage_count", "stage_count", "exact_match", "mismatch_fields")


def read_bit(row: dict[str, str], name: str) -> int:
    value = row.get(name)
    if value not in {"0", "1"}:
        raise ValueError(f"{name} 必须为 0/1，实际为 {value!r}")
    return int(value)


def ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6)


def analyze(path: Path) -> tuple[list[dict[str, str | int]], dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        raw = list(csv.DictReader(handle))
    pair_ids = [row.get("pair_id", "") for row in raw]
    if not raw or any(not value for value in pair_ids) or len(pair_ids) != len(set(pair_ids)):
        raise ValueError("pair_id 必须非空且唯一")

    details: list[dict[str, str | int]] = []
    stage_matches = {stage: 0 for stage in STAGES}
    success_match_n = 0
    exact_match_n = 0
    mismatch_pair_ids: list[str] = []
    for row in raw:
        mismatches: list[str] = []
        success_match = read_bit(row, "original_success") == read_bit(row, "repeat_success")
        success_match_n += int(success_match)
        if not success_match:
            mismatches.append("success")
        matching_stage_count = 0
        for stage in STAGES:
            matched = read_bit(row, f"original_{stage}") == read_bit(row, f"repeat_{stage}")
            stage_matches[stage] += int(matched)
            matching_stage_count += int(matched)
            if not matched:
                mismatches.append(stage)
        exact_match = success_match and matching_stage_count == len(STAGES)
        exact_match_n += int(exact_match)
        if not exact_match:
            mismatch_pair_ids.append(row["pair_id"])
        details.append({
            "pair_id": row["pair_id"],
            "success_match": int(success_match),
            "matching_stage_count": matching_stage_count,
            "stage_count": len(STAGES),
            "exact_match": int(exact_match),
            "mismatch_fields": "|".join(mismatches),
        })

    denominator = len(raw)
    report = {
        "pair_count": denominator,
        "success_match": {"numerator": success_match_n, "denominator": denominator, "rate": ratio(success_match_n, denominator)},
        "exact_match": {"numerator": exact_match_n, "denominator": denominator, "rate": ratio(exact_match_n, denominator)},
        "stage_match": {
            stage: {"numerator": count, "denominator": denominator, "rate": ratio(count, denominator)}
            for stage, count in stage_matches.items()
        },
        "mismatch_pair_ids": mismatch_pair_ids,
        "boundary": "paired synthetic fixture check; not a VLA-Arena/model reproducibility result",
    }
    return details, report


def write_csv(path: Path, rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DETAIL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--details", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    details, report = analyze(args.input)
    write_csv(args.details, details)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: pairs={report['pair_count']} success_match={report['success_match']['numerator']}/{report['success_match']['denominator']} exact_match={report['exact_match']['numerator']}/{report['exact_match']['denominator']}")


if __name__ == "__main__":
    main()
