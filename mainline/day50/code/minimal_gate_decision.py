#!/usr/bin/env python3
"""最小例子：证据完整性优先于漂亮指标。"""

cases = [
    {"name": "complete_and_pass", "formal": True,
     "l0": True, "ood": True, "ablation": True},
    {"name": "recoverable_gap", "formal": True,
     "l0": True, "ood": False, "ablation": True},
    {"name": "synthetic_only", "formal": False,
     "l0": True, "ood": True, "ablation": True},
]

for case in cases:
    if not case["formal"]:
        decision = "停止扩张"
    elif all(case[key] for key in ("l0", "ood", "ablation")):
        decision = "通过"
    else:
        decision = "补做"
    print(f"{case['name']} -> {decision}")
