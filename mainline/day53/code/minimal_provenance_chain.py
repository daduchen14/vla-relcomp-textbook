#!/usr/bin/env python3
"""最小例子：逐环验证 repair checkpoint 的来源链。"""

expected = {
    "checkpoint_sha256": "ckpt-123",
    "parent_base_sha256": "base-456",
    "recipe_sha256": "recipe-789",
    "split_sha256": "split-abc",
    "seed": 1,
}
observed = dict(expected)

checks = {
    key: observed.get(key) == value
    for key, value in expected.items()
}
checks["completed"] = True
checks["step_positive"] = 1000 > 0

print(f"checks={checks}")
print(f"provenance_valid={str(all(checks.values())).lower()}")
