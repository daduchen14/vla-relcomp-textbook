#!/usr/bin/env python3
"""最小例子：一行一个 episode，一列一个变量。"""

raw = [
    {"episode_id": "e02", "condition": "repair", "outcome": {"success": False, "cost": 2.0}},
    {"episode_id": "e01", "condition": "baseline", "outcome": {"success": True, "cost": 0.0}},
]

tidy = [
    {
        "episode_id": row["episode_id"],
        "condition": row["condition"],
        "success": row["outcome"]["success"],
        "cost": row["outcome"]["cost"],
    }
    for row in raw
]

for row in sorted(tidy, key=lambda item: item["episode_id"]):
    print(row)
