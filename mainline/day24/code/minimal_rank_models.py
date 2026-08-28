#!/usr/bin/env python3
"""最小例子：按预注册的多级键排序，而非看完结果改规则。"""

models = [
    {"model": "alpha", "macro": 0.60, "worst": 0.25, "micro": 0.60},
    {"model": "beta", "macro": 0.60, "worst": 0.50, "micro": 0.58},
    {"model": "gamma", "macro": 0.55, "worst": 0.55, "micro": 0.62},
]

ranked = sorted(
    models,
    key=lambda row: (-row["macro"], -row["worst"], -row["micro"], row["model"]),
)

for rank, row in enumerate(ranked, start=1):
    print(rank, row["model"], row["macro"], row["worst"], row["micro"])

print("rule=macro_then_worst_then_micro_then_model_id")
print("boundary=L0_only_never_L1_or_L2")
