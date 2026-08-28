#!/usr/bin/env python3
"""最小例子：收益加分，成本/泄漏/损伤风险扣分。"""

candidates = {
    "LANGUAGE_RELATION_NORMALIZATION": {
        "alignment": 3, "benefit": 3, "falsifiability": 3,
        "cost": 1, "leakage": 1, "damage": 1,
    },
    "VISUAL_OBJECT_AUXILIARY": {
        "alignment": 1, "benefit": 2, "falsifiability": 2,
        "cost": 2, "leakage": 3, "damage": 2,
    },
}
for name, item in candidates.items():
    score = (3 * item["alignment"] + 2 * item["benefit"]
             + item["falsifiability"] - item["cost"]
             - 2 * item["leakage"] - 2 * item["damage"])
    print(f"{name}={score}")
print("gate_required_before_selection=true")
