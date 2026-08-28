#!/usr/bin/env python3
"""最小例子：同一函数迁移到新输入，并解释阈值影响。"""

def compare(baseline, repair, minimum_delta):
    baseline_rate = sum(baseline) / len(baseline)
    repair_rate = sum(repair) / len(repair)
    delta = repair_rate - baseline_rate
    return {
        "delta": delta,
        "minimum_delta": minimum_delta,
        "meets_threshold": delta >= minimum_delta,
    }


new_input = {
    "baseline": [False, True, False, False],
    "repair": [True, True, False, False],
}

for threshold in (0.10, 0.30):
    result = compare(**new_input, minimum_delta=threshold)
    print(result)
