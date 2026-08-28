#!/usr/bin/env python3
"""最小例子：先写阈值和 falsifier，再看 synthetic observation。"""

hypothesis = {
    "prediction": "paired_recovery_rate >= 0.30",
    "threshold": 0.30,
    "falsifier": "paired_recovery_rate < 0.30",
}
synthetic_recoveries = [1, 0, 0, 0, 0]

numerator = sum(synthetic_recoveries)
denominator = len(synthetic_recoveries)
observed = numerator / denominator
supported_by_test = observed >= hypothesis["threshold"]

print(f"metric={numerator}/{denominator}={observed:.3f}")
print(f"prediction={hypothesis['prediction']}")
print(f"falsifier={hypothesis['falsifier']}")
print(f"supported_by_this_synthetic_test={supported_by_test}")
print("boundary=one_test_does_not_establish_a_unique_causal_mechanism")
