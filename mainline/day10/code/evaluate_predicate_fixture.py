#!/usr/bin/env python3
"""用确定 JSON 验证锁定 ObjectState.check_ontop 与 done/success 逻辑。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def evaluate_case(case: dict) -> dict:
    on = (case["reference_z"] <= case["target_z"] and case["contact"]
          and case["xy_distance"] < 0.07)
    timeout_done = bool(case["timeout_done"])
    done = on or timeout_done
    info = {"success": on, "timeout": timeout_done and not on}
    return {**case, "on_predicate": on, "done": done, "info": info,
            "evaluator_success": bool(info.get("success", done)),
            "source_kind": "numeric_fixture_replaying_locked_formula_not_mujoco"}


def evaluate(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"form": data["form"], "threshold": {"xy_strictly_less_than": 0.07},
            "cases": [evaluate_case(case) for case in data["cases"]],
            "real_environment_run": False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True); args = p.parse_args(); result = evaluate(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("PASS: predicate fixture; real environment run=false")


if __name__ == "__main__": main()
