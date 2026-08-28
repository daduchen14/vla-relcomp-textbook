#!/usr/bin/env python3
"""把逐帧仿真诊断状态压缩成四段 episode 事件。"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

EVENT_NAMES = ("target_contacted", "target_lifted", "reference_approached", "relation_satisfied")


def load_thresholds(path: Path) -> dict:
    cfg = json.loads(path.read_text(encoding="utf-8"))
    if cfg.get("schema_version") != "day12_event_thresholds_v1":
        raise ValueError("未知 threshold schema")
    for key in ("contact_consecutive_frames", "approach_consecutive_frames"):
        if not isinstance(cfg.get(key), int) or cfg[key] < 1:
            raise ValueError(f"{key} 必须是正整数")
    for key in ("lift_delta_m", "approach_drop_m"):
        if not isinstance(cfg.get(key), (int, float)) or not math.isfinite(cfg[key]) or cfg[key] <= 0:
            raise ValueError(f"{key} 必须是有限正数")
    return cfg


def _validate_frames(data: dict) -> list[dict]:
    frames = data.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("frames 必须是非空列表")
    expected = ("step", "target_z", "target_gripper_contact", "target_reference_xy_distance", "relation_satisfied")
    previous = -1
    for frame in frames:
        if not all(key in frame for key in expected): raise ValueError(f"frame 缺字段：{expected}")
        if not isinstance(frame["step"], int) or frame["step"] <= previous: raise ValueError("step 必须严格递增")
        previous = frame["step"]
        for key in ("target_z", "target_reference_xy_distance"):
            if not isinstance(frame[key], (int, float)) or not math.isfinite(frame[key]): raise ValueError(f"{key} 非有限数")
        if frame["target_reference_xy_distance"] < 0: raise ValueError("距离不得为负")
        for key in ("target_gripper_contact", "relation_satisfied"):
            if not isinstance(frame[key], bool): raise ValueError(f"{key} 必须是 bool")
    return frames


def _event(step: int, evidence: dict) -> dict:
    return {"occurred": True, "first_step": step, "evidence": evidence}


def summarize(input_path: Path, thresholds_path: Path) -> dict:
    data = json.loads(input_path.read_text(encoding="utf-8")); frames = _validate_frames(data)
    cfg = load_thresholds(thresholds_path); initial_z = float(frames[0]["target_z"])
    events: dict[str, dict] = {name: {"occurred": False, "first_step": None, "evidence": None} for name in EVENT_NAMES}
    contact_run = approach_run = 0; distance_at_lift = None

    for frame in frames:
        step = frame["step"]
        contact_run = contact_run + 1 if frame["target_gripper_contact"] else 0
        if not events["target_contacted"]["occurred"] and contact_run >= cfg["contact_consecutive_frames"]:
            events["target_contacted"] = _event(step, {"consecutive_frames": contact_run})

        lift_delta = float(frame["target_z"]) - initial_z
        if (events["target_contacted"]["occurred"] and not events["target_lifted"]["occurred"]
                and lift_delta >= cfg["lift_delta_m"]):
            distance_at_lift = float(frame["target_reference_xy_distance"])
            events["target_lifted"] = _event(step, {"lift_delta_m": lift_delta,
                                                     "reference_xy_distance_m": distance_at_lift})

        if events["target_lifted"]["occurred"] and not events["reference_approached"]["occurred"]:
            enough_drop = float(frame["target_reference_xy_distance"]) <= distance_at_lift - cfg["approach_drop_m"]
            approach_run = approach_run + 1 if enough_drop else 0
            if approach_run >= cfg["approach_consecutive_frames"]:
                events["reference_approached"] = _event(step, {
                    "distance_at_lift_m": distance_at_lift,
                    "current_distance_m": float(frame["target_reference_xy_distance"]),
                    "drop_m": distance_at_lift - float(frame["target_reference_xy_distance"]),
                    "consecutive_frames": approach_run})

        # 终态真值独立记录：绝不因为前序 probe 漏检而抹掉真实 success。
        if frame["relation_satisfied"] and not events["relation_satisfied"]["occurred"]:
            events["relation_satisfied"] = _event(step, {"predicate": True})

    relation_step = events["relation_satisfied"]["first_step"]
    anomalies = []
    if relation_step is not None:
        for earlier in ("target_contacted", "target_lifted", "reference_approached"):
            earlier_step = events[earlier]["first_step"]
            if earlier_step is None or relation_step < earlier_step: anomalies.append(f"relation_before_{earlier}")
    booleans = {name: event["occurred"] for name, event in events.items()}
    return {
        "episode_id": data["episode_id"], "target_object": data["target_object"],
        "reference_object": data["reference_object"], "relation": data["relation"],
        **booleans, "events": events, "anomalies": anomalies,
        "thresholds": {key: cfg[key] for key in ("schema_version", "contact_consecutive_frames",
                        "lift_delta_m", "approach_drop_m", "approach_consecutive_frames")},
        "frame_count": len(frames), "source_kind": data["source_kind"],
        "real_environment_run": bool(data.get("real_environment_run", False)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True); parser.add_argument("--thresholds", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True); args = parser.parse_args()
    result = summarize(args.input, args.thresholds); args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: " + " ".join(f"{name}={result[name]}" for name in EVENT_NAMES)
          + f"; real environment run={str(result['real_environment_run']).lower()}")


if __name__ == "__main__": main()
