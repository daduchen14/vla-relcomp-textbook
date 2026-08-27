#!/usr/bin/env python3
"""最小例子：内容 hash 能发现同名文件被静默修改。"""

import hashlib
from pathlib import Path

path = Path("mainline/day12/config/event_thresholds.json")
payload = path.read_bytes()
digest = hashlib.sha256(payload).hexdigest()

print(f"path={path}")
print(f"bytes={len(payload)}")
print(f"sha256={digest}")
