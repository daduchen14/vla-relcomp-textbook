#!/usr/bin/env python3
"""最小例子：按 pair/condition 检查两条 arm 都齐全。"""

rows = [
    ("p1", "baseline", "control", True),
    ("p1", "baseline", "counterfactual", False),
    ("p1", "repair", "control", True),
    ("p1", "repair", "counterfactual", True),
]
required_arms = {"control", "counterfactual"}

groups = {}
for pair_id, condition, arm, success in rows:
    groups.setdefault((pair_id, condition), {})[arm] = success

complete = all(set(arms) == required_arms for arms in groups.values())
scores = {
    condition: all(arms.values())
    for (_, condition), arms in groups.items()
}
print(f"complete={str(complete).lower()}")
print(f"paired_success={scores}")
print("missing_policy=fail_closed")
