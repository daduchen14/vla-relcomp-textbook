#!/usr/bin/env python3
"""最小例子：计算有效 batch、checkpoint 数和粗略显存上限。"""

micro_batch = 2
gradient_accumulation = 8
world_size = 1
global_batch = micro_batch * gradient_accumulation * world_size

frozen_parameters = 450_000_000
trainable_parameters = 1_000_000
frozen_bytes = frozen_parameters * 2
trainable_bytes = trainable_parameters * (2 + 4 + 8)
activation_bytes = 4 * 1024**3
safety_factor = 1.25
estimated_gib = (
    (frozen_bytes + trainable_bytes + activation_bytes)
    * safety_factor / 1024**3
)

max_steps = 200
save_every = 50
print(f"global_batch={global_batch}")
print(f"planned_checkpoints={max_steps // save_every}")
print(f"estimated_peak_gib={estimated_gib:.3f}")
print("estimate_only_not_profiled=true")
