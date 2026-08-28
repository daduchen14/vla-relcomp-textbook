#!/usr/bin/env python3
"""最小例子：主张必须同时指向证据和越界边界。"""

claims = [
    {
        "claim": "合成样本中阶段二通过率较低",
        "table": "T-stage",
        "episodes": ["syn-001", "syn-002"],
        "version": "locked-analysis-v1",
        "forbidden": "真实系统普遍在阶段二失败",
    },
    {
        "claim": "合成配对样本未显示改善",
        "table": "T-pair",
        "episodes": ["syn-011", "syn-012"],
        "version": "locked-analysis-v1",
        "forbidden": "修复方法确定无效",
    },
]

for item in claims:
    complete = all(item[key] for key in ("table", "episodes", "version", "forbidden"))
    print(f"claim={item['claim']} evidence_complete={complete}")
    print(f"cannot_claim={item['forbidden']}")
