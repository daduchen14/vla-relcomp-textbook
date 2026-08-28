#!/usr/bin/env python3
"""按冻结 L0 公平口径检查候选资格、排序并输出主模型选择记录。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

FIELDS = ("model_id", "model_revision", "task_count", "total_valid_n", "total_successes",
          "micro_success_rate", "macro_success_rate", "worst_task_rate", "eligible", "exclusion_reason")
RANKING = ["macro_success_rate", "worst_task_rate", "micro_success_rate", "model_id_lexical"]


def rate(value: float) -> str: return f"{value:.6f}"


def select(stats_path: Path, policy_path: Path) -> tuple[list[dict[str, str | int]], dict]:
    with stats_path.open(encoding="utf-8", newline="") as handle: raw = list(csv.DictReader(handle))
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if policy.get("allowed_level") != 0 or policy.get("ranking") != RANKING:
        raise ValueError("只允许预注册的 L0 ranking")
    if policy.get("heldout_use") != "L1_L2_report_only_never_select": raise ValueError("held-out 规则未冻结")
    if "selected_model_id" in policy: raise ValueError("policy 不得预填选择结果")
    expected_tasks = [int(value) for value in policy["expected_task_ids"]]
    minimum = int(policy["min_valid_per_task"])
    if expected_tasks != sorted(set(expected_tasks)) or minimum <= 0: raise ValueError("task/minimum policy 非法")

    grouped: dict[str, list[dict[str, str]]] = {}
    seen: set[tuple[str, int]] = set()
    protocols: set[str] = set()
    for row in raw:
        model_id = row.get("model_id", "")
        try: task_id, level, successes, valid_n = (int(row[name]) for name in ("task_id", "level", "successes", "valid_n"))
        except (KeyError, ValueError) as exc: raise ValueError("候选统计整数列非法") from exc
        if not model_id or level != 0: raise ValueError("候选选择只能包含 L0")
        if (model_id, task_id) in seen: raise ValueError("model/task 必须唯一")
        if not 0 <= successes <= valid_n: raise ValueError("successes/valid_n 非法")
        seen.add((model_id, task_id)); protocols.add(row.get("protocol_lock_sha256", "")); grouped.setdefault(model_id, []).append(row)
    if len(protocols) != 1 or "" in protocols: raise ValueError("候选必须共享同一 protocol lock")

    rows: list[dict[str, str | int]] = []
    vectors: dict[str, tuple[int, ...]] = {}
    metrics: dict[str, tuple[float, float, float]] = {}
    for model_id, items in sorted(grouped.items()):
        items.sort(key=lambda item: int(item["task_id"]))
        if [int(item["task_id"]) for item in items] != expected_tasks: raise ValueError("候选 task set 不完整")
        revisions = {item.get("model_revision", "") for item in items}
        if len(revisions) != 1 or "" in revisions: raise ValueError("model revision 必须固定")
        valid = tuple(int(item["valid_n"]) for item in items); vectors[model_id] = valid
        successes = [int(item["successes"]) for item in items]
        task_rates = [x / n for x, n in zip(successes, valid)]
        micro = sum(successes) / sum(valid); macro = sum(task_rates) / len(task_rates); worst = min(task_rates)
        metrics[model_id] = (macro, worst, micro)
        eligible = all(n >= minimum for n in valid)
        rows.append({"model_id": model_id, "model_revision": next(iter(revisions)), "task_count": len(items),
            "total_valid_n": sum(valid), "total_successes": sum(successes), "micro_success_rate": rate(micro),
            "macro_success_rate": rate(macro), "worst_task_rate": rate(worst),
            "eligible": str(eligible).lower(), "exclusion_reason": "" if eligible else "min_valid_per_task"})

    eligible_ids = [row["model_id"] for row in rows if row["eligible"] == "true"]
    if len(eligible_ids) < 2: raise ValueError("至少需要两个 eligible 候选")
    eligible_vectors = {vectors[model_id] for model_id in eligible_ids}
    if len(eligible_vectors) != 1: raise ValueError("eligible 候选 valid_n 向量必须一致")
    selected = sorted(eligible_ids, key=lambda model_id: (-metrics[model_id][0], -metrics[model_id][1], -metrics[model_id][2], model_id))[0]
    revision = next(row["model_revision"] for row in rows if row["model_id"] == selected)
    decision = {"decision_name": policy["decision_name"], "selection_scope": "L0_only", "selected_model_id": selected,
                "selected_model_revision": revision, "eligible_model_ids": eligible_ids, "ranking": RANKING,
                "min_valid_per_task": minimum, "protocol_lock_sha256": next(iter(protocols)),
                "policy_sha256": hashlib.sha256(policy_path.read_bytes()).hexdigest(),
                "heldout_use": policy["heldout_use"], "source_kind": policy["source_kind"],
                "boundary": "synthetic L0 comparison fixture; freeze record is not a real model-selection result"}
    return rows, decision


def write(path: Path, rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--stats", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True); parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--decision", type=Path, required=True); args = parser.parse_args()
    rows, decision = select(args.stats, args.policy); write(args.comparison, rows)
    args.decision.parent.mkdir(parents=True, exist_ok=True); args.decision.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: eligible={len(decision['eligible_model_ids'])} selected={decision['selected_model_id']} scope=L0_only heldout=report_only")


if __name__ == "__main__": main()
