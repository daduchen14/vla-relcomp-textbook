#!/usr/bin/env python3
"""最小例子：一致率必须保留原始分子与分母。"""

pairs = [(1, 1), (0, 0), (1, 0), (0, 0)]
matches = sum(original == repeat for original, repeat in pairs)
rate = matches / len(pairs)

print(f"matches={matches}")
print(f"pairs={len(pairs)}")
print(f"agreement={rate:.3f}")
