#!/usr/bin/env python3
"""最小例子：失败运行也进入尝试次数与资源成本。"""

runs = [
    {"status": "completed", "gpu_seconds": 3600},
    {"status": "failed", "gpu_seconds": 1800},
    {"status": "not_run", "gpu_seconds": 0},
]

attempted = [row for row in runs if row["status"] != "not_run"]
completed = [row for row in attempted if row["status"] == "completed"]
failed = [row for row in attempted if row["status"] == "failed"]
gpu_hours = sum(row["gpu_seconds"] for row in attempted) / 3600

print(f"planned={len(runs)}")
print(f"attempted={len(attempted)}")
print(f"completed={len(completed)} failed={len(failed)}")
print(f"failure_rate={len(failed)/len(attempted):.3f}")
print(f"gpu_hours_including_failures={gpu_hours:.3f}")
