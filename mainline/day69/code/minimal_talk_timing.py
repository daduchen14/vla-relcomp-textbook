#!/usr/bin/env python3
"""最小例子：逐页预算必须恰好组成 10 分钟。"""

slides = [
    ("问题为什么重要", 60),
    ("调用链如何定义证据", 90),
    ("诊断与修复如何区分", 120),
    ("结果边界是什么", 150),
    ("限制与下一步", 120),
    ("一句话结论", 60),
]

elapsed = 0
for title, seconds in slides:
    start = elapsed
    elapsed += seconds
    print(f"{start:03d}–{elapsed:03d}s | {title}")

assert elapsed == 600
print("total=600s")
