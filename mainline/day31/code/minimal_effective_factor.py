#!/usr/bin/env python3
"""最小例子：一个关系处理会同步改变三列，其余列必须匹配。"""

arm_a = {"relation": "next_to", "instruction": "tomato next to board",
         "init_state": "state-next", "seed": "17", "camera": "front"}
arm_b = {"relation": "on_top_of", "instruction": "tomato on board",
         "init_state": "state-on", "seed": "17", "camera": "front"}

required_changes = {"relation", "instruction", "init_state"}
changed = {key for key in arm_a if arm_a[key] != arm_b[key]}
fixed = {key for key in arm_a if arm_a[key] == arm_b[key]}

assert changed == required_changes
assert fixed == {"seed", "camera"}
print(f"changed={sorted(changed)}")
print(f"fixed={sorted(fixed)}")
print("effective_factor=spatial_relation")
print("execution=planned_not_run")
