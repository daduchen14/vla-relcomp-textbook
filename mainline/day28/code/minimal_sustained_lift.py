#!/usr/bin/env python3
"""最小例子：抬升要求高度与离开支撑面连续同时成立。"""

heights_m = [0.000, 0.010, 0.031, 0.042, 0.018]
support_contacts = [True, True, False, False, True]
threshold_m = 0.025
sustained_steps = 2

run = 0
first_lift_step = None
for step, (height, supported) in enumerate(zip(heights_m, support_contacts)):
    passed = height >= threshold_m and not supported
    run = run + 1 if passed else 0
    if run == sustained_steps:
        first_lift_step = step - sustained_steps + 1
        break

print(f"first_lift_step={first_lift_step}")
print("grasp_status=requires_separate_bilateral_contact_signal")
