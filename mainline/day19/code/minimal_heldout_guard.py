#!/usr/bin/env python3
"""最小例子：测试集结果不能回流到选择字段。"""

frozen = {"model_revision": "rev-a", "threshold": 0.04, "prompt": "original"}
l1_run = {"model_revision": "rev-a", "threshold": 0.04, "prompt": "original"}

changed = [key for key in frozen if frozen[key] != l1_run[key]]
forbidden_uses = {"select_checkpoint", "tune_threshold", "rewrite_prompt"}
declared_use = "report_only"

assert changed == []
assert declared_use not in forbidden_uses
print("PASS: L1 uses frozen settings and report_only")
