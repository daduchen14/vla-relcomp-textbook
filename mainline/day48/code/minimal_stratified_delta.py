#!/usr/bin/env python3
"""最小例子：按 L1/L2 分层报告配对成功率差。"""

rows = [
    ("L1", True, True), ("L1", False, True),
    ("L1", False, False), ("L1", True, True),
    ("L2", True, False), ("L2", False, True),
    ("L2", False, True), ("L2", True, True),
]

for level in ("L1", "L2"):
    group = [row for row in rows if row[0] == level]
    baseline = sum(row[1] for row in group) / len(group)
    repair = sum(row[2] for row in group) / len(group)
    improved = sum(not row[1] and row[2] for row in group)
    regressed = sum(row[1] and not row[2] for row in group)
    print(f"{level}: delta={repair-baseline:+.3f} "
          f"improved={improved} regressed={regressed}")
