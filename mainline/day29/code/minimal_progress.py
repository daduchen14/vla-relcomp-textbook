#!/usr/bin/env python3
"""最小例子：进入区域与朝区域取得进展是两个事件。"""

distances_m = [0.42, 0.33, 0.25, 0.20]
entry_threshold_m = 0.12
minimum_progress_m = 0.08

decreases = [before - after for before, after in zip(distances_m, distances_m[1:])]
net_progress = distances_m[0] - min(distances_m)
decrease_fraction = sum(delta > 0 for delta in decreases) / len(decreases)
entered = min(distances_m) <= entry_threshold_m
progressed = net_progress >= minimum_progress_m

print(f"net_progress_m={net_progress:.3f}")
print(f"decrease_fraction={decrease_fraction:.3f}")
print(f"entered={entered}")
print(f"progressed={progressed}")
print("status=PROGRESS_NO_ENTRY" if progressed and not entered else "status=OTHER")
