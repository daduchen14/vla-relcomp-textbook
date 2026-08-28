#!/usr/bin/env python3
"""最小例子：canonical JSON 让任何计划变动产生新 hash。"""

import hashlib
import json

manifest = {
    "conditions": ["baseline", "repair", "ablation"],
    "levels": ["L0", "L1", "L2"],
    "seeds": [1, 2, 3],
    "max_gpu_hours": 36,
    "authorized": False,
}

canonical = json.dumps(
    manifest,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
print(f"manifest_sha256={hashlib.sha256(canonical).hexdigest()}")
print("frozen_plan_not_authorized=true")
