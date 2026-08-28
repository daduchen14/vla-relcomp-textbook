#!/usr/bin/env python3
"""最小例子：成本匹配时用 repair−ablation 隔离单一组件。"""

repair = {"score": 0.62, "gpu_hours": 5.0,
          "normalization": True, "adapter": True}
ablation = {"score": 0.51, "gpu_hours": 4.9,
            "normalization": False, "adapter": True}

changed = [
    key for key in ("normalization", "adapter")
    if repair[key] != ablation[key]
]
cost_gap = abs(repair["gpu_hours"] - ablation["gpu_hours"])
cost_gap /= repair["gpu_hours"]

print(f"changed_factors={changed}")
print(f"component_effect={repair['score']-ablation['score']:+.3f}")
print(f"relative_cost_gap={cost_gap:.3f}")
print(f"single_variable={str(changed == ['normalization']).lower()}")
