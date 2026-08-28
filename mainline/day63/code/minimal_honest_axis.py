#!/usr/bin/env python3
"""最小例子：比例图固定 0–1 轴，并保留区间。"""

points = [
    {"label": "baseline", "rate": 0.45, "low": 0.25, "high": 0.67},
    {"label": "repair", "rate": 0.60, "low": 0.39, "high": 0.78},
]

y_min, y_max = 0.0, 1.0
for point in points:
    if not (y_min <= point["low"] <= point["rate"] <= point["high"] <= y_max):
        raise ValueError("点估计或区间超出冻结比例轴")
    height = (point["rate"] - y_min) / (y_max - y_min)
    print(
        f"{point['label']}: normalized_height={height:.2f}, "
        f"interval=[{point['low']:.2f}, {point['high']:.2f}]"
    )
