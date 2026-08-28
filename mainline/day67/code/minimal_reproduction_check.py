#!/usr/bin/env python3
"""最小例子：同一输入必须产生同一摘要与统计。"""

import hashlib
import json

rows = [
    {"condition": "baseline", "success": 1},
    {"condition": "baseline", "success": 0},
    {"condition": "repair", "success": 1},
]
payload = json.dumps(rows, sort_keys=True).encode()
digest = hashlib.sha256(payload).hexdigest()

successes = sum(row["success"] for row in rows)
result = {"rows": len(rows), "successes": successes, "input_sha256": digest}

print(json.dumps(result, sort_keys=True))
