#!/usr/bin/env python3
"""最小例子：二项成功率的 95% Wilson 区间。"""

from math import sqrt

successes, trials = 3, 5
z = 1.959963984540054
p = successes / trials
denominator = 1 + z * z / trials
center = (p + z * z / (2 * trials)) / denominator
margin = z * sqrt(p * (1 - p) / trials + z * z / (4 * trials**2)) / denominator

print(f"count={successes}/{trials}")
print(f"rate={p:.3f}")
print(f"wilson95=[{center - margin:.3f}, {center + margin:.3f}]")
print("boundary=interval_describes_sampling_uncertainty_not_model_cause")
