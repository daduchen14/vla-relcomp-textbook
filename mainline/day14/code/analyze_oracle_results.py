#!/usr/bin/env python3
"""计算配对 oracle 的恢复、损害和四段转移；不接受不完整 pair。"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

STAGES = ("target_contacted", "target_lifted", "reference_approached", "relation_satisfied")


def bit(value: str, field: str) -> int:
    if value not in {"0", "1"}: raise ValueError(f"{field} 必须是 0/1")
    return int(value)


def analyze(path: Path) -> dict:
    with path.open(encoding="utf-8", newline="") as handle: rows = list(csv.DictReader(handle))
    grouped = defaultdict(dict)
    for row in rows:
        if row["arm"] not in {"control", "oracle"} or row["arm"] in grouped[row["oracle_pair_id"]]:
            raise ValueError("arm 非法或重复")
        if row["valid"] != "1": raise ValueError("本课要求先排除无效 episode，再分析完整 pair")
        values = {stage: bit(row[stage], stage) for stage in STAGES}; success = bit(row["success"], "success")
        if success != values["relation_satisfied"]: raise ValueError("success 必须与锁定 relation_satisfied 一致")
        grouped[row["oracle_pair_id"]][row["arm"]] = {"success": success, **values}
    if not grouped or any(set(arms) != {"control", "oracle"} for arms in grouped.values()):
        raise ValueError("存在不完整 pair")

    def metric(field: str) -> dict:
        cells = {"00": 0, "01": 0, "10": 0, "11": 0}
        for arms in grouped.values(): cells[f"{arms['control'][field]}{arms['oracle'][field]}"] += 1
        failure_n, success_n = cells["00"] + cells["01"], cells["10"] + cells["11"]
        return {"cells_control_oracle": cells, "control_failure_n": failure_n,
                "recovered_n": cells["01"], "recovery_rate": cells["01"] / failure_n if failure_n else None,
                "control_success_n": success_n, "damaged_n": cells["10"],
                "damage_rate": cells["10"] / success_n if success_n else None}
    return {"pair_count": len(grouped), "success": metric("success"),
            "stages": {stage: metric(stage) for stage in STAGES},
            "causal_boundary": "paired association under diagnostic privileged intervention; not proof of internal mechanism",
            "source_kind": "synthetic_fixture_analysis_unless_input_is_verified_model_results"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True); args = parser.parse_args(); result = analyze(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    success = result["success"]
    print(f"PASS: pairs={result['pair_count']} recovery={success['recovered_n']}/{success['control_failure_n']} "
          f"damage={success['damaged_n']}/{success['control_success_n']}")


if __name__ == "__main__": main()
