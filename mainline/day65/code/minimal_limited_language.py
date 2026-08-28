#!/usr/bin/env python3
"""最小例子：把点估计、区间和解释边界放在同一句。"""

result = {
    "scope": "synthetic paired sample",
    "estimate": 0.15,
    "interval": (-0.08, 0.36),
    "formal": False,
}

sentence = (
    f"在 {result['scope']} 中，paired delta 为 "
    f"{result['estimate']:+.2f}，95% 区间为 "
    f"[{result['interval'][0]:+.2f}, {result['interval'][1]:+.2f}]。"
)
boundary = "该教学估计不能推出真实模型改善或因果效果。"

print(sentence)
print(boundary)
