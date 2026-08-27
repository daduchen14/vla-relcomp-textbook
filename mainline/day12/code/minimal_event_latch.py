#!/usr/bin/env python3
"""最小例子：瞬时布尔量经过连续帧规则变成一次性事件。"""

CONTACT = [False, True, False, True, True, False]
REQUIRED = 2
run_length = 0
first_event_step = None

for step, is_contact in enumerate(CONTACT):
    run_length = run_length + 1 if is_contact else 0
    if first_event_step is None and run_length >= REQUIRED:
        first_event_step = step
    print(
        f"step={step} raw={is_contact} run={run_length} "
        f"contacted={first_event_step is not None}"
    )

print(f"first_event_step={first_event_step}")
