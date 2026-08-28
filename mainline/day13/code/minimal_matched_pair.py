#!/usr/bin/env python3
"""最小例子：先比较固定列，再确认唯一处理变量。"""

A = {"seed": 7, "init_state": 2, "goal": "On(tomato_3,bowl_3)",
     "instruction": "Put the selected tomato on the bowl."}
B = {"seed": 7, "init_state": 2, "goal": "On(tomato_3,bowl_3)",
     "instruction": "Place the chosen tomato atop the bowl."}

fixed_fields = ("seed", "init_state", "goal")
changed_fields = [key for key in A if A[key] != B[key]]

assert all(A[key] == B[key] for key in fixed_fields)
assert changed_fields == ["instruction"]
print(f"PASS: fixed={list(fixed_fields)} changed={changed_fields}")
