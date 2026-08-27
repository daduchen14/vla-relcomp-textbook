#!/usr/bin/env python3
"""验收 Day 8 矩阵、选择报告和 Gate 2 的独立决策。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .build_pilot_matrix import build
    from .select_diagnostic_model import summarize
except ImportError:
    from build_pilot_matrix import build
    from select_diagnostic_model import summarize


def check_gate(report: dict, answer_path: Path) -> None:
    answer = json.loads(answer_path.read_text(encoding="utf-8"))
    if answer.get("selected_model") != report["selected_model"]:
        raise ValueError("Gate 2 必须按 L0 规则独立选择，不能被 L1/L2 高分诱导")
    if sorted(answer.get("excluded_episode_ids", [])) != report["excluded_episode_ids"]:
        raise ValueError("必须列出全部且仅列出无效分母 episode")
    expected_denominators = {model: {level: stats["valid"] for level, stats in data["levels"].items()}
                             for model, data in report["models"].items()}
    if answer.get("valid_denominators") != expected_denominators:
        raise ValueError("有效分母必须按 model/level 从 registry 重算")
    experiment = answer.get("next_minimal_experiment", "")
    required = (report["selected_model"] or "INSUFFICIENT", "task", "seed")
    if len(experiment) < 60 or not all(word.lower() in experiment.lower() for word in required):
        raise ValueError("下一步实验须≥60字，并固定写出候选、task 和 seed")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--matrix-config", type=Path, required=True)
    p.add_argument("--smolvla-manifest", type=Path, required=True); p.add_argument("--openvla-manifest", type=Path, required=True)
    p.add_argument("--matrix", type=Path, required=True); p.add_argument("--registry", type=Path, required=True)
    p.add_argument("--selection-report", type=Path, required=True); p.add_argument("--gate-answer", type=Path, required=True)
    args = p.parse_args(); expected_matrix = build(args.matrix_config, args.smolvla_manifest, args.openvla_manifest)
    if json.loads(args.matrix.read_text()) != expected_matrix: raise ValueError("pilot matrix 与锁定模型/配置不一致")
    expected_report = summarize(args.registry)
    if json.loads(args.selection_report.read_text()) != expected_report: raise ValueError("选择报告不是从 registry 重算")
    check_gate(expected_report, args.gate_answer); print("PASS: Day 8 matrix and Gate 2 independent decision")


if __name__ == "__main__": main()
