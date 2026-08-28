#!/usr/bin/env python3
"""按预注册 L0 规则汇总 pilot registry，拒绝无效分母和测试集选模。"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

LEVELS, TASKS = (0, 1, 2), range(5)


def read_bool(value: str) -> bool | None:
    if value.lower() == "true": return True
    if value.lower() == "false": return False
    return None


def summarize(path: Path) -> dict:
    with path.open(newline="", encoding="utf-8") as handle: rows = list(csv.DictReader(handle))
    episode_ids = [row["episode_id"] for row in rows]
    if len(episode_ids) != len(set(episode_ids)): raise ValueError("registry 含重复 episode_id")
    grouped, excluded = defaultdict(list), []
    for row in rows:
        success = read_bool(row.get("success", "")); evidence = read_bool(row.get("evidence_complete", ""))
        if row.get("status") != "completed" or evidence is not True or success is None:
            excluded.append(row["episode_id"]); continue
        row["level"], row["task_id"], row["success"] = int(row["level"]), int(row["task_id"]), success
        grouped[(row["model"], row["level"])].append(row)
    models = sorted({row["model"] for row in rows}); summaries, eligible = {}, []
    for model in models:
        per_level = {}
        for level in LEVELS:
            valid = grouped[(model, level)]; successes = sum(row["success"] for row in valid)
            per_level[str(level)] = {"valid": len(valid), "successes": successes,
                "success_rate": successes / len(valid) if valid else None}
        l0 = grouped[(model, 0)]; coverage = len({row["task_id"] for row in l0 if row["success"]})
        cells_complete = all(sum(row["task_id"] == task for row in l0) == 5 for task in TASKS)
        pilot_complete = all(per_level[str(level)]["valid"] == 25 for level in LEVELS)
        l0_eligible = cells_complete and sum(row["success"] for row in l0) >= 10 and coverage == 5
        eligible_for_selection = pilot_complete and l0_eligible
        summaries[model] = {"levels": per_level, "l0_successful_task_coverage": coverage,
                            "l0_cells_complete": cells_complete, "pilot_complete_75": pilot_complete,
                            "eligible_from_l0_only": eligible_for_selection}
        if eligible_for_selection: eligible.append(model)
    if len(eligible) == 1: decision, reason = eligible[0], "唯一候选满足预注册 L0 分母、成功数和 task coverage"
    elif not eligible: decision, reason = None, "没有候选满足 L0 诊断能力；证据不足以选择"
    else:
        scores = {model: summaries[model]["levels"]["0"]["successes"] for model in eligible}
        best = max(scores.values()); winners = [m for m, score in scores.items() if score == best]
        decision = winners[0] if len(winners) == 1 else None
        reason = "仅按 L0 成功数择优" if decision else "多个候选 L0 并列；证据不足以选择"
    return {"rule": {"valid_per_level": 25, "full_pilot_completeness_required": True,
                     "min_l0_successes": 10, "successful_task_coverage": 5,
                     "selection_levels": [0], "l1_l2_performance_used_for_selection": False},
            "models": summaries, "excluded_episode_ids": sorted(excluded),
            "selected_model": decision, "decision_reason": reason,
            "registry_source_kinds": sorted({row.get("source_kind", "") for row in rows}),
            "source_kind": "registry_summary_not_new_model_run"}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--registry", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True); args = p.parse_args(); report = summarize(args.registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"decision={report['selected_model'] or 'INSUFFICIENT'} excluded={len(report['excluded_episode_ids'])}")


if __name__ == "__main__": main()
