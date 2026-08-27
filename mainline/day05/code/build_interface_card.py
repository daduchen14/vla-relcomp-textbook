#!/usr/bin/env python3
"""用 CPU fixture 复现锁定 SmolVLA adapter 的输入张量契约。"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch

REQUIRED = {"agentview_image", "robot0_eye_in_hand_image", "robot0_eef_pos",
            "robot0_eef_quat", "robot0_gripper_qpos"}


def quat_to_axis_angle(quat: np.ndarray) -> np.ndarray:
    quat = quat.copy(); quat[3] = np.clip(quat[3], -1.0, 1.0)
    denominator = math.sqrt(max(0.0, 1.0 - float(quat[3]) ** 2))
    if math.isclose(denominator, 0.0): return np.zeros(3, dtype=np.float64)
    return quat[:3] * 2.0 * math.acos(float(quat[3])) / denominator


def tensor_meta(tensor: torch.Tensor) -> dict:
    return {"shape": list(tensor.shape), "dtype": str(tensor.dtype),
            "device": str(tensor.device), "min": float(tensor.min()), "max": float(tensor.max())}


def build_card(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8")); specs = payload["raw"]
    if set(specs) != REQUIRED: raise ValueError("raw observation key 与锁定 adapter 不一致")
    arrays = {name: np.asarray(item["values"], dtype=item["dtype"]) for name, item in specs.items()}
    agent = np.ascontiguousarray(arrays["agentview_image"][::-1, ::-1])
    wrist = np.ascontiguousarray(arrays["robot0_eye_in_hand_image"][::-1, ::-1])
    state = np.concatenate((arrays["robot0_eef_pos"], quat_to_axis_angle(arrays["robot0_eef_quat"]),
                            arrays["robot0_gripper_qpos"]))
    observation = {
        "observation.images.image": torch.from_numpy(agent / 255.0).permute(2, 0, 1).float().unsqueeze(0),
        "observation.images.wrist_image": torch.from_numpy(wrist / 255.0).permute(2, 0, 1).float().unsqueeze(0),
        "observation.state": torch.from_numpy(state).float().unsqueeze(0),
    }
    with torch.inference_mode():
        fixture_action = torch.linspace(-1.0, 1.0, 7, dtype=torch.float32).unsqueeze(0)
    return {"form_id": payload["form_id"], "task": payload["task"],
            "inputs": {name: tensor_meta(value) for name, value in observation.items()},
            "action": tensor_meta(fixture_action), "inference_mode": True,
            "source_kind": "cpu_fixture_matches_locked_adapter_contract",
            "real_model_loaded": False, "requires_gpu_for_real_model": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); card = build_card(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: {card['form_id']} state={card['inputs']['observation.state']['shape']} action={card['action']['shape']}")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
