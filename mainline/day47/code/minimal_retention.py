#!/usr/bin/env python3
"""最小例子：配对统计原本成功是否被修复模型保留。"""

pairs = [
    ("ep1", True, True),
    ("ep2", True, False),
    ("ep3", False, True),
    ("ep4", True, True),
]

baseline_successes = [row for row in pairs if row[1]]
retained = [row for row in baseline_successes if row[2]]
regressions = [row[0] for row in baseline_successes if not row[2]]
retention = len(retained) / len(baseline_successes)
baseline_rate = sum(row[1] for row in pairs) / len(pairs)
repair_rate = sum(row[2] for row in pairs) / len(pairs)

print(f"retention_rate={retention:.3f}")
print(f"success_delta={repair_rate - baseline_rate:+.3f}")
print(f"catastrophic_regressions={regressions}")
