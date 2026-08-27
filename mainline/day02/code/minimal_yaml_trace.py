#!/usr/bin/env python3
"""最小 YAML 标量解析：展示 key、值和 Python 类型。"""

import argparse
from pathlib import Path


def scalar(text):
    # 本课配置只用字符串、整数和 boolean；不冒充完整 YAML 解析器。
    value = text.split("#", 1)[0].strip().strip('"').strip("'")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        return value


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("config", type=Path)
args = parser.parse_args()
config = {}
for line_number, line in enumerate(args.config.read_text().splitlines(), start=1):
    clean = line.strip()
    if not clean or clean.startswith("#"):
        continue
    if ":" not in clean:
        raise SystemExit(f"line {line_number}: missing ':'")
    key, raw = clean.split(":", 1)
    config[key.strip()] = scalar(raw)
for key, value in config.items():
    print(f"{key}={value!r} type={type(value).__name__}")
