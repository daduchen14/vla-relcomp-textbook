#!/usr/bin/env python3
"""最小例子：官方谓词需在释放目标后连续成立。"""

predicate = [False, True, True, True]
gripper_contact = [True, True, False, False]
sustained_steps = 2

run = 0
first_stable_step = None
for step, (passed, held) in enumerate(zip(predicate, gripper_contact)):
    valid_terminal = passed and not held
    run = run + 1 if valid_terminal else 0
    if run == sustained_steps:
        first_stable_step = step - sustained_steps + 1
        break

print(f"first_stable_relation_step={first_stable_step}")
print("authority=official_bddl_predicate")
print("proxy_role=diagnostic_only")
