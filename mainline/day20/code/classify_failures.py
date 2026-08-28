#!/usr/bin/env python3
"""按首个未满足四段事件分类；标签只描述行为证据。"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

STAGES = ("target_contacted", "target_lifted", "reference_approached", "relation_satisfied")
LABELS = {"target_contacted": "TARGET_CONTACT_FAILURE", "target_lifted": "LIFT_FAILURE",
          "reference_approached": "REFERENCE_APPROACH_FAILURE", "relation_satisfied": "TERMINAL_RELATION_FAILURE"}


def classify(path: Path) -> tuple[list[dict], dict]:
    with path.open(encoding="utf-8", newline="") as handle: source = list(csv.DictReader(handle))
    if not source or len({row["episode_id"] for row in source}) != len(source): raise ValueError("结果为空或 episode_id 重复")
    rows = []
    for row in source:
        if row["valid"] not in {"0", "1"}: raise ValueError("valid 必须 0/1")
        if row["valid"] == "0": label, first = "ENV_INVALID", ""
        else:
            if row["success"] not in {"0", "1"} or any(row[key] not in {"0", "1"} for key in STAGES):
                raise ValueError("有效 episode 的 success/events 必须为 0/1")
            success = row["success"] == "1"; events = {key: row[key] == "1" for key in STAGES}
            if success: label, first = ("SUCCESS", "") if all(events.values()) else ("SUCCESS_WITH_PROBE_GAP", next(key for key in STAGES if not events[key]))
            elif all(events.values()): label, first = "INCONSISTENT_SUCCESS_SIGNAL", ""
            else: first = next(key for key in STAGES if not events[key]); label = LABELS[first]
        rows.append({"episode_id": row["episode_id"], "failure_label": label, "first_unmet_event": first,
                     "behavioral_only": "true", "internal_cause_claimed": "false"})
    counts = Counter(row["failure_label"] for row in rows)
    report = {"episode_count": len(rows), "label_counts": dict(sorted(counts.items())),
              "taxonomy_version": "first_unmet_stage_v1",
              "boundary": "labels locate observable chain break; they do not identify language, vision, or control mechanism"}
    return rows, report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True); p.add_argument("--report", type=Path, required=True)
    args = p.parse_args(); rows, report = classify(args.input); args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: classified={len(rows)} labels={len(report['label_counts'])} behavioral_only=true")


if __name__ == "__main__": main()
