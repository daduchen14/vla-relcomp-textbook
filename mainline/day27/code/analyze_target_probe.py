#!/usr/bin/env python3
"""从逐步距离与 gripper contact object 生成 target probe 和阈值敏感性表。"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

SUMMARY_FIELDS = ("episode_id", "target_object_id", "step_count", "min_target_distance_m", "first_near_step",
                  "first_target_contact_step", "first_contact_objects", "near_detected", "target_contact_detected",
                  "wrong_object_first", "distance_without_contact", "probe_status")
SENSITIVITY_FIELDS = ("episode_id", "threshold_m", "sustained_steps", "near_detected", "first_near_step")


def split_contacts(value: str) -> set[str]:
    return {item for item in value.split("|") if item}


def first_sustained(distances: list[float], threshold: float, length: int) -> int | None:
    run = 0
    for step, distance in enumerate(distances):
        run = run + 1 if distance <= threshold else 0
        if run == length:
            return step - length + 1
    return None


def analyze(trace_path: Path, config_path: Path) -> tuple[list[dict[str, str | int]], list[dict[str, str | int]], dict]:
    with trace_path.open(encoding="utf-8", newline="") as handle:
        raw = list(csv.DictReader(handle))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    primary = float(config["primary_threshold_m"]); length = int(config["sustained_near_steps"])
    thresholds = [float(value) for value in config["sensitivity_thresholds_m"]]
    source_kind = config.get("source_kind", "")
    if primary <= 0 or length <= 0 or thresholds != sorted(set(thresholds)) or primary not in thresholds:
        raise ValueError("threshold config 必须为正、唯一、有序，且包含 primary")
    if not source_kind.startswith("synthetic_target_"):
        raise ValueError("免费 fixture 必须明确 synthetic source boundary")
    # registry 主键是 episode_id；逐步 trace 在每组内再按 step 恢复时间顺序。
    groups: dict[str, list[dict[str, str]]] = {}
    for row in raw:
        episode_id = row.get("episode_id", "")
        if not episode_id: raise ValueError("episode_id 不能为空")
        groups.setdefault(episode_id, []).append(row)
    if not groups: raise ValueError("trace 不能为空")

    summaries: list[dict[str, str | int]] = []; sensitivity: list[dict[str, str | int]] = []
    for episode_id, rows in sorted(groups.items()):
        rows.sort(key=lambda row: int(row["step"]))
        steps = [int(row["step"]) for row in rows]
        if steps != list(range(len(rows))): raise ValueError(f"{episode_id} step 必须从 0 连续")
        targets = {row["target_object_id"] for row in rows}
        if len(targets) != 1 or "" in targets: raise ValueError("每个 episode 必须固定一个 target_object_id")
        target = next(iter(targets)); distances = [float(row["target_distance_m"]) for row in rows]
        if any(not math.isfinite(value) or value < 0 for value in distances): raise ValueError("distance 必须有限且非负")
        contacts = [split_contacts(row.get("contact_object_ids", "")) for row in rows]
        first_any = next((step for step, values in enumerate(contacts) if values), None)
        first_target = next((step for step, values in enumerate(contacts) if target in values), None)
        first_objects = "|".join(sorted(contacts[first_any])) if first_any is not None else ""
        wrong_first = first_any is not None and target not in contacts[first_any]
        # 近距依赖人为阈值和持续窗口；接触依赖 contact object，二者绝不互相代替。
        first_near = first_sustained(distances, primary, length); near = first_near is not None; contacted = first_target is not None
        if contacted: status = "WRONG_OBJECT_FIRST_THEN_TARGET" if wrong_first else "TARGET_CONTACT"
        elif wrong_first: status = "WRONG_OBJECT_ONLY"
        elif near: status = "NEAR_NO_CONTACT"
        else: status = "NO_TARGET_EVIDENCE"
        summaries.append({"episode_id": episode_id, "target_object_id": target, "step_count": len(rows),
            "min_target_distance_m": f"{min(distances):.6f}", "first_near_step": "" if first_near is None else first_near,
            "first_target_contact_step": "" if first_target is None else first_target, "first_contact_objects": first_objects,
            "near_detected": str(near).lower(), "target_contact_detected": str(contacted).lower(),
            "wrong_object_first": str(wrong_first).lower(), "distance_without_contact": str(near and not contacted).lower(),
            "probe_status": status})
        for threshold in thresholds:
            # 同一原始距离轨迹重算全部阈值，禁止手工编辑敏感性标签。
            detected_step = first_sustained(distances, threshold, length)
            sensitivity.append({"episode_id": episode_id, "threshold_m": f"{threshold:.6f}", "sustained_steps": length,
                "near_detected": str(detected_step is not None).lower(), "first_near_step": "" if detected_step is None else detected_step})
    counts = Counter(row["probe_status"] for row in summaries)
    report = {"episode_count": len(summaries), "primary_threshold_m": primary, "sustained_near_steps": length,
              "probe_status_counts": dict(sorted(counts.items())), "sensitivity_row_count": len(sensitivity),
              "source_kind": source_kind,
              "boundary": "synthetic distance/contact trace; near is not contact and probe status is not a causal diagnosis"}
    return summaries, sensitivity, report


def write(path: Path, rows: list[dict], fields: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True); parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--sensitivity", type=Path, required=True); parser.add_argument("--report", type=Path, required=True); args = parser.parse_args()
    summaries, sensitivity, report = analyze(args.trace, args.config); write(args.summary, summaries, SUMMARY_FIELDS); write(args.sensitivity, sensitivity, SENSITIVITY_FIELDS)
    args.report.parent.mkdir(parents=True, exist_ok=True); args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: episodes={len(summaries)} sensitivity_rows={len(sensitivity)} near_is_not_contact=true")


if __name__ == "__main__": main()
