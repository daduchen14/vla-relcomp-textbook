#!/usr/bin/env python3
"""最小例子：Wilson 区间与 exact McNemar 使用不同信息。"""

import math

n00, n01, n10, n11 = 4, 6, 1, 9
n = n00 + n01 + n10 + n11
z = 1.959963984540054
successes = n01 + n11
p = successes / n
denominator = 1 + z * z / n
center = (p + z * z / (2 * n)) / denominator
margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
margin /= denominator

discordant = n01 + n10
tail = sum(math.comb(discordant, k) for k in range(min(n01, n10) + 1))
exact_p = min(1.0, 2 * tail / (2 ** discordant))

print(f"repair_rate={p:.3f}")
print(f"wilson95=({center-margin:.3f}, {center+margin:.3f})")
print(f"paired_delta={(n01-n10)/n:+.3f}")
print(f"mcnemar_exact_p={exact_p:.4f}")
