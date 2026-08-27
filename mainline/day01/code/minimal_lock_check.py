#!/usr/bin/env python3
"""最小版本锁检查：只读 Git 和三个项目入口。"""

import argparse
import subprocess
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
REQUIRED = [
    "README_zh.md",
    "vla_arena/models/random/evaluator.py",
    "vla_arena/vla_arena/benchmark/__init__.py",
]

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--upstream", type=Path, required=True)
args = parser.parse_args()
root = args.upstream.resolve()
# rev-parse 读取当前 checkout；不 import VLA-Arena，也不安装依赖。
head = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=root, check=True,
    text=True, capture_output=True,
).stdout.strip()
if head != LOCKED:
    raise SystemExit(f"FAIL: expected {LOCKED}, got {head}")
missing = [path for path in REQUIRED if not (root / path).is_file()]
if missing:
    raise SystemExit(f"FAIL: missing {missing}")
print(f"PASS: locked commit {head}")
for path in REQUIRED:
    print(f"FOUND: {path}")
