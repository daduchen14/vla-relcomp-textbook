#!/usr/bin/env python3
"""最小例子：给产物内容计算 SHA-256 receipt。"""

import hashlib

artifacts = {
    "manifest.csv": b"episode_id,status\ne1,PLANNED\n",
    "registry.csv": b"episode_id,status,success\ne1,COMPLETED,1\n",
}

for name, payload in artifacts.items():
    digest = hashlib.sha256(payload).hexdigest()
    print(name, digest)

print(f"artifact_count={len(artifacts)}")
print("boundary=hash_checks_bytes_not_scientific_truth")
