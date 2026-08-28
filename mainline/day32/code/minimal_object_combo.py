#!/usr/bin/env python3
"""最小例子：关系不变，只交换对象组合及其同步字段。"""

arm_a = {"relation": "next_to", "target": "tomato_1", "reference": "board_1",
         "instruction": "tomato next to board", "init": "state-a", "camera": "front"}
arm_b = {"relation": "next_to", "target": "apple_1", "reference": "plate_1",
         "instruction": "apple next to plate", "init": "state-b", "camera": "front"}

changed = {key for key in arm_a if arm_a[key] != arm_b[key]}
required = {"target", "reference", "instruction", "init"}
fixed = {key for key in arm_a if arm_a[key] == arm_b[key]}

assert changed == required
assert fixed == {"relation", "camera"}
print(f"changed={sorted(changed)}")
print(f"fixed={sorted(fixed)}")
print("effective_factor=object_combination")
print("execution=planned_not_run")
