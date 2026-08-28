#!/usr/bin/env python3
"""最小例子：连续近距事件不同于单帧越阈值。"""

distances = [0.14, 0.07, 0.09, 0.06, 0.05]
threshold = 0.08
sustained_steps = 2

run = 0
first_near_step = None
for step, distance in enumerate(distances):
    run = run + 1 if distance <= threshold else 0
    if run == sustained_steps:
        first_near_step = step - sustained_steps + 1
        break

print(f"threshold_m={threshold}")
print(f"first_near_step={first_near_step}")
print("contact_detected=unknown_without_contact_geoms")
