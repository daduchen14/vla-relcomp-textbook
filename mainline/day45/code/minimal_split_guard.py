#!/usr/bin/env python3
"""最小例子：训练启动前证明 train/val/test 三者互斥。"""

splits = {
    "train": {"ep01", "ep02", "ep03"},
    "validation": {"ep04"},
    "test": {"ep05", "ep06"},
}

pairs = (("train", "validation"),
         ("train", "test"),
         ("validation", "test"))
overlaps = {
    f"{left}_{right}": sorted(splits[left] & splits[right])
    for left, right in pairs
}
training_reads = splits["train"] | splits["validation"]
test_isolated = not overlaps["train_test"] and not overlaps["validation_test"]

print(f"overlaps={overlaps}")
print(f"training_reads={sorted(training_reads)}")
print(f"test_isolated={str(test_isolated).lower()}")
