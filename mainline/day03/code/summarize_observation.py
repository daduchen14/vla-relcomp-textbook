#!/usr/bin/env python3
"""把本地 observation fixture 的 key/shape/dtype/range 写成 JSON 证据。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = ROOT / "shared/fixtures/day03_observation_fixture.json"
DEFAULT_OUTPUT = ROOT / "learner_outputs/mainline/day03/observation_summary.json"
REQUIRED_KEYS = {
    "agentview_image", "robot0_eye_in_hand_image", "robot0_eef_pos",
    "robot0_eef_quat", "robot0_gripper_qpos",
}


def build_summary(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    specs = payload["observation"]
    missing = REQUIRED_KEYS - set(specs)
    if missing:
        raise ValueError(f"observation 缺少真实 evaluator 所需 key：{sorted(missing)}")
    arrays = {}
    for name, spec in specs.items():
        array = np.asarray(spec["values"], dtype=spec["dtype"])
        arrays[name] = {
            "shape": list(array.shape), "dtype": str(array.dtype),
            "min": float(array.min()), "max": float(array.max()),
        }
    return {
        "fixture_id": payload["fixture_id"],
        "source_kind": "local_fixture_not_vla_arena_run",
        "keys": sorted(specs), "arrays": arrays,
        "prepared_contract": {
            "agent_image": "agentview_image reversed on H/W, contiguous",
            "wrist_image": "robot0_eye_in_hand_image reversed on H/W, contiguous",
            "state": "eef_pos(3) + quat_to_axis_angle(3) + gripper_qpos(2)",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    summary = build_summary(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
