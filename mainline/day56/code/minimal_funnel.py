#!/usr/bin/env python3
"""最小例子：同时计算阶段到达率与相邻转化率。"""

episodes = [
    [1, 1, 1, 1],
    [1, 1, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
]
stages = ["contact", "lift", "approach", "satisfied"]

reached = [sum(row[index] for row in episodes)
           for index in range(len(stages))]
reach_rates = [count / len(episodes) for count in reached]
conversions = [
    reached[index] / reached[index - 1]
    for index in range(1, len(stages))
]

print(dict(zip(stages, reach_rates)))
print(dict(zip(stages[1:], conversions)))
print("denominator=previous_stage_reached")
