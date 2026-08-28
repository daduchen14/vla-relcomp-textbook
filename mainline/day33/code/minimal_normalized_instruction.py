#!/usr/bin/env python3
"""最小例子：把关系真值写成固定字段顺序。"""

facts = {
    "target": "tomato_1",
    "start": "next_to(cereal_1)",
    "action": "pick_and_place",
    "goal": "On(porcelain_bowl_3)",
}
order = ("target", "start", "action", "goal")
normalized = " | ".join(f"{key.upper()}={facts[key]}" for key in order)

print(normalized)
print(f"field_count={len(order)}")
print("privilege=bddl_truth")
print("use=diagnostic_only")
