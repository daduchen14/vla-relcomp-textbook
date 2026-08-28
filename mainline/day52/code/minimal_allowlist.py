#!/usr/bin/env python3
"""最小例子：clean-room 只复制显式允许的输入角色。"""

inventory = [
    ("upstream", "src@locked"),
    ("base_model", "smolvla-base"),
    ("raw_dataset", "l0-l2"),
    ("repair_checkpoint", "repair-seed1"),
    ("old_eval_cache", "results.json"),
]
allowed_roles = {"upstream", "base_model", "raw_dataset"}

accepted = [item for role, item in inventory if role in allowed_roles]
rejected = [
    {"role": role, "item": item}
    for role, item in inventory
    if role not in allowed_roles
]

print(f"accepted={accepted}")
print(f"rejected={rejected}")
print(f"clean={str(len(rejected) == 2).lower()}")
