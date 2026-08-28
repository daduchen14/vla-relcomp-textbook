#!/usr/bin/env python3
"""最小例子：先检查每个 task 的计划分母是否相同。"""

from collections import Counter

task_ids = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
counts = Counter(task_ids)
expected = 2

for task_id in range(5):
    print(f"task={task_id} planned={counts[task_id]}")
    assert counts[task_id] == expected

print("PASS: five tasks have equal planned denominators")
