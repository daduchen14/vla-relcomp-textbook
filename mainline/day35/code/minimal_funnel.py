#!/usr/bin/env python3
"""最小例子：阶段转化率以前一阶段为分母。"""

counts = {
    "episodes": 10,
    "contact": 8,
    "lift": 6,
    "approach": 3,
    "relation": 2,
}
transitions = (
    ("episodes", "contact"),
    ("contact", "lift"),
    ("lift", "approach"),
    ("approach", "relation"),
)
for before, after in transitions:
    rate = counts[after] / counts[before] if counts[before] else None
    print(f"{before}->{after}: {counts[after]}/{counts[before]}={rate:.3f}")
