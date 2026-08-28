#!/usr/bin/env python3
"""最小例子：按预注册 strata 和 salted hash 选案例。"""

import hashlib

episodes = [
    ("ep01", "recovery"), ("ep02", "recovery"),
    ("ep03", "damage"), ("ep04", "damage"),
]
salt = "casebook-v1"
quota = {"recovery": 1, "damage": 1}

selected = []
for stratum, count in quota.items():
    candidates = [episode for episode, label in episodes if label == stratum]
    ranked = sorted(
        candidates,
        key=lambda item: hashlib.sha256(f"{salt}|{item}".encode()).hexdigest(),
    )
    selected.extend((stratum, item) for item in ranked[:count])

print(f"selected={selected}")
print("manual_override=false")
