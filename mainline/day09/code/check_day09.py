#!/usr/bin/env python3
"""验收锁定 15-task 结构表和新 BDDL fixture 的语义解析。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .build_task_structures import build, markdown
    from .extract_fixture import extract
except ImportError:
    from build_task_structures import build, markdown
    from extract_fixture import extract


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--table-json", type=Path, required=True); p.add_argument("--table-md", type=Path, required=True)
    p.add_argument("--challenge-input", type=Path, required=True); p.add_argument("--challenge-output", type=Path, required=True)
    p.add_argument("--challenge-reflection", type=Path, required=True); args = p.parse_args()
    expected = build(args.upstream.resolve())
    if json.loads(args.table_json.read_text()) != expected or args.table_md.read_text() != markdown(expected):
        raise ValueError("5×3 表必须从锁定 BDDL blob 重新生成")
    challenge = extract(args.challenge_input)
    if json.loads(args.challenge_output.read_text()) != challenge:
        raise ValueError("挑战结构必须由新 BDDL 内容解析，不能复制真实表的一行")
    note = args.challenge_reflection.read_text(encoding="utf-8")
    required = ("obj_of_interest", "goal", challenge["goal_relation"], challenge["target_object"], challenge["obj_of_interest"][0])
    if len(note.strip()) < 100 or not all(word in note for word in required):
        raise ValueError("挑战反思须≥100字，并精确比较 interest、goal、关系和两个不同对象")
    print("PASS: Day 9 locked table and changed-input BDDL challenge")


if __name__ == "__main__": main()
