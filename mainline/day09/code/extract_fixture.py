#!/usr/bin/env python3
"""把一个本地教学 BDDL 解析为结构 JSON，不把它冒充 upstream task。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .build_task_structures import structure
except ImportError:
    from build_task_structures import structure


def extract(input_path: Path) -> dict:
    return structure(input_path.read_text(encoding="utf-8"), -1, -1, input_path.stem,
                     str(input_path), "local_teaching_bddl_fixture_not_upstream")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True); args = p.parse_args(); data = extract(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: fixture goal={' '.join(data['goal_predicate'])}; not upstream")


if __name__ == "__main__": main()
