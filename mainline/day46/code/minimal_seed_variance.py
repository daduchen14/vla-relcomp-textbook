#!/usr/bin/env python3
"""最小例子：保留全部预注册 seed，并报告均值与样本标准差。"""

from statistics import mean, stdev

results = [
    {"seed": 1, "score": 0.42},
    {"seed": 2, "score": 0.38},
    {"seed": 3, "score": 0.46},
]

registered = {1, 2, 3}
observed = {row["seed"] for row in results}
if observed != registered:
    raise SystemExit("缺少或多出 seed，禁止选择性报告")

scores = [row["score"] for row in results]
print(f"all_seeds={sorted(observed)}")
print(f"mean={mean(scores):.4f}")
print(f"sample_stdev={stdev(scores):.4f}")
print("best_seed_selection=false")
