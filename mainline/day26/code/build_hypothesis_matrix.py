#!/usr/bin/env python3
"""把研究假设编译为可观察、可干预、可证伪的预注册 metric 表。"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

STAGES = {"contact", "lift", "approach", "relation"}
REQUIRED_CONTROLS = {"task_id", "seed", "init_state_index", "model_revision", "protocol_lock_sha256"}
FIELDS = ("hypothesis_id", "claim", "primary_event", "observable_metric", "numerator", "denominator",
          "intervention", "baseline_arm", "intervention_arm", "directional_prediction", "falsifier",
          "alternative_explanations", "control_variables", "causal_status", "source_kind")


def build(path: Path) -> tuple[list[dict[str, str]], dict]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    forbidden = {"observed_result", "p_value", "conclusion", "supported"}
    if forbidden.intersection(spec): raise ValueError("预注册 spec 不得包含结果/结论")
    hypotheses = spec.get("hypotheses", [])
    if not hypotheses: raise ValueError("hypotheses 不能为空")
    ids: set[str] = set(); rows: list[dict[str, str]] = []
    for item in hypotheses:
        if forbidden.intersection(item): raise ValueError("hypothesis 不得预填结果/结论")
        required = {"hypothesis_id", "claim", "primary_event", "observable_metric", "numerator", "denominator",
                    "intervention", "baseline_arm", "intervention_arm", "directional_prediction", "falsifier",
                    "alternative_explanations", "control_variables"}
        if not required.issubset(item): raise ValueError("hypothesis 缺少必需字段")
        hypothesis_id = item["hypothesis_id"]
        if not hypothesis_id or hypothesis_id in ids: raise ValueError("hypothesis_id 必须唯一")
        ids.add(hypothesis_id)
        if item["primary_event"] not in STAGES: raise ValueError("primary_event 非四段事件")
        alternatives = item["alternative_explanations"]
        if len(alternatives) < 2 or len(set(alternatives)) != len(alternatives): raise ValueError("至少两个不同 alternative explanations")
        controls = set(item["control_variables"])
        if not REQUIRED_CONTROLS.issubset(controls): raise ValueError("control variables 不完整")
        if not all(str(item[name]).strip() for name in ("numerator", "denominator", "directional_prediction", "falsifier")):
            raise ValueError("metric/prediction/falsifier 不得为空")
        rows.append({"hypothesis_id": hypothesis_id, "claim": item["claim"], "primary_event": item["primary_event"],
            "observable_metric": item["observable_metric"], "numerator": item["numerator"], "denominator": item["denominator"],
            "intervention": item["intervention"], "baseline_arm": item["baseline_arm"], "intervention_arm": item["intervention_arm"],
            "directional_prediction": item["directional_prediction"], "falsifier": item["falsifier"],
            "alternative_explanations": " | ".join(alternatives), "control_variables": " | ".join(item["control_variables"]),
            "causal_status": "pre_registered_untested", "source_kind": spec["source_kind"]})
    events = Counter(row["primary_event"] for row in rows); interventions = Counter(row["intervention"] for row in rows)
    report = {"hypothesis_count": len(rows), "all_falsifiable": True, "primary_event_counts": dict(sorted(events.items())),
              "intervention_counts": dict(sorted(interventions.items())), "causal_status": "pre_registered_untested",
              "boundary": "synthetic hypothesis design fixture; no intervention result or causal conclusion"}
    return rows, report


def write(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True); parser.add_argument("--report", type=Path, required=True); args = parser.parse_args()
    rows, report = build(args.spec); write(args.matrix, rows); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: hypotheses={len(rows)} falsifiable=true causal_status=pre_registered_untested")


if __name__ == "__main__": main()
