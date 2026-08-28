#!/usr/bin/env python3
"""最小例子：训练只选择 L0，L1/L2 只计数不输出。"""

registry = [
    {"sample": "a", "level": 0, "split": "train"},
    {"sample": "b", "level": 1, "split": "heldout_test"},
    {"sample": "c", "level": 0, "split": "validation"},
    {"sample": "d", "level": 2, "split": "heldout_test"},
]
selected = [row for row in registry if row["level"] == 0]
excluded = [row for row in registry if row["level"] in {1, 2}]

assert all(row["split"] in {"train", "validation"} for row in selected)
assert all(row["split"] == "heldout_test" for row in excluded)
print(f"selected={[row['sample'] for row in selected]}")
print(f"heldout={[row['sample'] for row in excluded]}")
print("training_levels=[0]")
