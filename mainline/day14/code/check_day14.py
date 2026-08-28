#!/usr/bin/env python3
"""验收 oracle A/B 重算与 Gate 3 独立诊断。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from .analyze_oracle_results import analyze
    from .build_oracle_manifest import build
except ImportError:
    from analyze_oracle_results import analyze
    from build_oracle_manifest import build


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def normalized(data: list[dict]) -> list[dict]: return [{key: str(value) for key, value in row.items()} for row in data]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--task-table", type=Path, required=True)
    p.add_argument("--example-spec", type=Path, required=True); p.add_argument("--example-manifest", type=Path, required=True)
    p.add_argument("--example-results", type=Path, required=True); p.add_argument("--example-analysis", type=Path, required=True)
    p.add_argument("--challenge-spec", type=Path, required=True); p.add_argument("--challenge-manifest", type=Path, required=True)
    p.add_argument("--challenge-results", type=Path, required=True); p.add_argument("--challenge-analysis", type=Path, required=True)
    p.add_argument("--gate-case", type=Path, required=True); p.add_argument("--gate-submission", type=Path, required=True)
    p.add_argument("--oral-note", type=Path, required=True); args = p.parse_args()
    expected_a, expected_b = build(args.task_table, args.example_spec), build(args.task_table, args.challenge_spec)
    if rows(args.example_manifest) != normalized(expected_a) or rows(args.challenge_manifest) != normalized(expected_b):
        raise ValueError("oracle manifest 必须分别由 A/B spec 重建")
    analysis_a, analysis_b = analyze(args.example_results), analyze(args.challenge_results)
    if json.loads(args.example_analysis.read_text()) != analysis_a or json.loads(args.challenge_analysis.read_text()) != analysis_b:
        raise ValueError("oracle analysis 必须从对应 paired results 重算")
    if analysis_a == analysis_b: raise ValueError("挑战不得复制 A analysis")
    case = json.loads(args.gate_case.read_text()); sub = json.loads(args.gate_submission.read_text())
    if sub.get("case_id") != case["case_id"] or sub.get("event_readout") != case["events"]:
        raise ValueError("Gate 3 必须先准确读取陌生 case 的四段事件")
    alternatives = sub.get("alternative_explanations", [])
    if len(alternatives) != 2 or any(len(text.strip()) < 30 for text in alternatives) or alternatives[0] == alternatives[1]:
        raise ValueError("必须给出两个不同且具体的替代解释")
    intervention = sub.get("intervention", {}); allowed = {"language_oracle": "instruction_text", "visual_oracle": "visual_hint"}
    if intervention.get("type") not in allowed or intervention.get("changed_field") != allowed[intervention["type"]]:
        raise ValueError("干预类型与唯一 changed field 不匹配")
    if len(set(intervention.get("fixed_fields", []))) < 6 or intervention.get("uses_privileged_info") is not True or intervention.get("diagnostic_only") is not True:
        raise ValueError("必须冻结≥6字段并声明 oracle 的特权/诊断边界")
    prediction = sub.get("prediction", {})
    if prediction.get("first_event_expected_to_change") not in case["events"] or len(prediction.get("falsifier", "")) < 40:
        raise ValueError("必须预先指定首个预期变化事件和可证伪观察")
    note = args.oral_note.read_text(encoding="utf-8").strip()
    if len(note) < 180 or not all(word in note for word in ("recovery", "damage", "alternative", "leakage", "cannot prove")):
        raise ValueError("口述稿须≥180字并解释率、替代解释、泄漏与因果边界")
    print("PASS: Day 14 oracle challenge and Gate 3 diagnostic submission")


if __name__ == "__main__": main()
