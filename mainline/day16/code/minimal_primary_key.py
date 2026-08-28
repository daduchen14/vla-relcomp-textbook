#!/usr/bin/env python3
"""最小例子：稳定主键来自规范化身份，不来自 CSV 行号。"""

import hashlib
import json

identity = {"run_id": "run-demo", "task_id": 2, "seed": 17, "init_state_index": 4}
canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
episode_id = "ep-" + hashlib.sha256(canonical.encode()).hexdigest()[:16]

print(f"identity={canonical}")
print(f"episode_id={episode_id}")
