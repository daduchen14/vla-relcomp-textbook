#!/usr/bin/env python3
"""最小例子：表格同时报告成功数、分母和比例。"""

episodes = [
    {"condition": "baseline", "success": True},
    {"condition": "baseline", "success": False},
    {"condition": "repair", "success": True},
    {"condition": "repair", "success": True},
]

for condition in ("baseline", "repair"):
    selected = [row for row in episodes if row["condition"] == condition]
    successes = sum(row["success"] for row in selected)
    total = len(selected)
    print(
        f"{condition}: successes={successes}, "
        f"n={total}, rate={successes / total:.3f}"
    )
