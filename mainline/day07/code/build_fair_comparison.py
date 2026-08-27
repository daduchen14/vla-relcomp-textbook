#!/usr/bin/env python3
"""验证 SmolVLA/OpenVLA 控制变量，并生成计划态同口径比较表。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .build_openvla_manifest import CONTROL_FIELDS, LOCKED
except ImportError:
    from build_openvla_manifest import CONTROL_FIELDS, LOCKED


def build(smol_path: Path, open_path: Path) -> dict:
    smol, openvla = json.loads(smol_path.read_text()), json.loads(open_path.read_text())
    if smol.get("source_kind") != "locked_source_static_pilot_plan" or openvla.get("source_kind") != "locked_source_static_openvla_plan":
        raise ValueError("两行必须来自 Day 6/7 锁定静态 manifest")
    if smol.get("upstream_commit") != LOCKED or openvla.get("upstream_commit") != LOCKED:
        raise ValueError("两模型必须使用同一 VLA-Arena commit")
    mismatches = [field for field in CONTROL_FIELDS if smol.get(field) != openvla.get(field)]
    if mismatches: raise ValueError(f"比较口径不一致：{mismatches}")
    return {"comparison_status": "planned_no_model_results", "controlled_fields": CONTROL_FIELDS,
            "controls": {field: smol[field] for field in CONTROL_FIELDS},
            "rows": [
                {"model": "SmolVLA", "checkpoint_revision": smol["checkpoint_revision"],
                 "policy_input": "2 RGB + 8D state + language", "action_path": "50-step chunk queue → one 7D action/step",
                 "episode_status": "not_run", "success": None},
                {"model": "OpenVLA", "checkpoint_revision": openvla["checkpoint_revision"],
                 "policy_input": "agentview RGB + language", "action_path": "7 action tokens → unnormalize → one 7D action/step",
                 "episode_status": "not_run", "success": None}],
            "claim_boundary": "本表只比较锁定计划与接口，不能比较模型性能。"}


def markdown(data: dict) -> str:
    lines = ["# Day 7 同口径模型比较（计划态）", "", "| 模型 | policy 输入 | 动作路径 | episode 状态 | success |", "|---|---|---|---|---|"]
    for row in data["rows"]:
        lines.append(f"| {row['model']} | {row['policy_input']} | {row['action_path']} | {row['episode_status']} | — |")
    lines += ["", f"控制字段：`{', '.join(data['controlled_fields'])}`。", "", f"> 结论边界：{data['claim_boundary']}"]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smolvla-manifest", type=Path, required=True); parser.add_argument("--openvla-manifest", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True); parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args(); data = build(args.smolvla_manifest, args.openvla_manifest)
    for path in (args.json_output, args.markdown_output): path.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    args.markdown_output.write_text(markdown(data), encoding="utf-8")
    print("PASS: fair plan-level comparison; no performance result claimed")


if __name__ == "__main__": main()
