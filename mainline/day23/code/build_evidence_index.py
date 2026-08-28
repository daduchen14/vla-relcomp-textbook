#!/usr/bin/env python3
"""把 video、exception、stage events 一对一 left join 到 episode registry。"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

FIELDS = ("episode_id", "task_id", "status", "success", "video_path", "video_status",
          "stage_contact", "stage_lift", "stage_approach", "stage_relation",
          "exception_type", "exception_message", "evidence_state", "review_priority")


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def unique_index(rows: list[dict[str, str]], name: str, allowed_ids: set[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        episode_id = row.get("episode_id", "")
        if not episode_id or episode_id in result: raise ValueError(f"{name} episode_id 必须非空且唯一")
        if episode_id not in allowed_ids: raise ValueError(f"{name} 存在 orphan episode_id：{episode_id}")
        result[episode_id] = row
    return result


def build(registry_path: Path, videos_path: Path, stages_path: Path, exceptions_path: Path) -> tuple[list[dict[str, str]], dict]:
    registry = read(registry_path)
    ids = [row.get("episode_id", "") for row in registry]
    if not registry or any(not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError("registry episode_id 必须非空且唯一")
    allowed = set(ids)
    videos = unique_index(read(videos_path), "video", allowed)
    stages = unique_index(read(stages_path), "stage", allowed)
    exceptions = unique_index(read(exceptions_path), "exception", allowed)

    output: list[dict[str, str]] = []
    for episode in registry:
        episode_id = episode["episode_id"]
        status, success = episode.get("status", ""), episode.get("success", "")
        if status not in {"COMPLETED", "ERROR"} or (status == "COMPLETED" and success not in {"0", "1"}):
            raise ValueError("registry status/success 非法")
        if status == "ERROR" and success != "": raise ValueError("ERROR success 必须为空")
        video = videos.get(episode_id, {})
        stage = stages.get(episode_id, {})
        exception = exceptions.get(episode_id, {})
        video_status = video.get("video_status", "NOT_INDEXED")
        video_path = video.get("video_path", "")
        if video_status not in {"PRESENT", "MISSING", "NOT_INDEXED"}: raise ValueError("video_status 非法")
        if (video_status == "PRESENT") != bool(video_path): raise ValueError("video PRESENT/path 不一致")
        stage_values = [stage.get(name, "") for name in ("contact", "lift", "approach", "relation")]
        if stage and any(value not in {"0", "1"} for value in stage_values): raise ValueError("stage 必须四列齐全且为 0/1")
        if status == "ERROR":
            if not exception.get("exception_type"): raise ValueError("ERROR episode 必须有 exception")
            evidence_state, priority = "RUN_ERROR", "P0"
        elif video_status != "PRESENT" or not stage:
            evidence_state, priority = "INCOMPLETE_EVIDENCE", "P1"
        elif (success == "1") != (stage["relation"] == "1"):
            evidence_state, priority = "SIGNAL_CONFLICT", "P1"
        elif success == "0":
            evidence_state, priority = "COMPLETE_FAILURE", "P2"
        else:
            evidence_state, priority = "COMPLETE_SUCCESS", "P3"
        output.append({"episode_id": episode_id, "task_id": episode.get("task_id", ""), "status": status,
            "success": success, "video_path": video_path, "video_status": video_status,
            "stage_contact": stage_values[0], "stage_lift": stage_values[1],
            "stage_approach": stage_values[2], "stage_relation": stage_values[3],
            "exception_type": exception.get("exception_type", ""),
            "exception_message": exception.get("exception_message", ""),
            "evidence_state": evidence_state, "review_priority": priority})
    states = Counter(row["evidence_state"] for row in output)
    priorities = Counter(row["review_priority"] for row in output)
    report = {"registry_rows": len(registry), "output_rows": len(output), "cardinality_preserved": len(registry) == len(output),
              "evidence_state_counts": dict(sorted(states.items())), "review_priority_counts": dict(sorted(priorities.items())),
              "boundary": "synthetic evidence paths and probes; evidence_state is triage, not a causal diagnosis"}
    return output, report


def write(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("registry", "videos", "stages", "exceptions", "output", "report"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args(); rows, report = build(args.registry, args.videos, args.stages, args.exceptions)
    write(args.output, rows); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: evidence_rows={report['output_rows']} cardinality_preserved=true states={report['evidence_state_counts']}")


if __name__ == "__main__": main()
