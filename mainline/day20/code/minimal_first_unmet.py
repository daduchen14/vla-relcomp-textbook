#!/usr/bin/env python3
"""最小例子：失败标签是首个未满足事件，不是内部机制诊断。"""

events = {
    "target_contacted": True,
    "target_lifted": True,
    "reference_approached": False,
    "relation_satisfied": False,
}

first_unmet = next(name for name, passed in events.items() if not passed)
print(f"first_unmet={first_unmet}")
print("boundary=observable_behavior_not_internal_cause")
