#!/usr/bin/env python3
"""最小例子：把可部署结果与特权 oracle 诊断分栏。"""

records = {
    "baseline": [0, 1, 0, 1],
    "repair": [1, 1, 0, 1],
    "language_oracle": [1, 1, 1, 1],
}

deployable = {
    name: sum(values) / len(values)
    for name, values in records.items()
    if name in {"baseline", "repair"}
}
diagnostic = {
    name: sum(values) / len(values)
    for name, values in records.items()
    if name.endswith("oracle")
}

print(f"deployable={deployable}")
print(f"diagnostic_only={diagnostic}")
print("oracle_in_primary_result=false")
