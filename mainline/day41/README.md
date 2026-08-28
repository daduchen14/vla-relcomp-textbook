# Mainline Day 41：冻结有界的 adapter-only 训练配置

今天把 Day 40 的 trainable boundary 写成有上限的训练计划：micro batch、gradient accumulation、mixed precision、max steps、checkpoint/resume 与粗略显存预算。正式教学选择 `adapter_only`，因为 Day 36 只允许一个 repair；LoRA 作为成熟替代方法被解释但明确关闭，避免叠加第二项修复。脚本只做 CPU 算术，不分配 CUDA。

## 1. 真实项目产物

- `bounded_train_config_a.json`：adapter-only、batch/schedule/checkpoint/level/memory 边界；
- `bounded_train_report_a.json`：global batch、checkpoint 数、规划峰值与 headroom；
- B 新配置的 report 与 `challenge_memo.md`。

## 2. 当前卡点

只写 `batch_size=16` 无法知道是单步 16 还是 micro 2×累积 8；只报“8GB 能跑”又混淆权重、梯度、optimizer state 与激活。没有 max steps、save frequency 和 keep-last，短实验也可能无限消耗磁盘/预算。

本课冻结 global batch 的构成，要求规划显存至少 20% 余量，并标记 `ASSUMPTION_ONLY_NOT_PROFILED`。参数量与 activation 都是教学假设，不是 SmolVLA 实测。配置通过仍写 `authorized_for_training=false`、`command_run=false`，训练许可与配置正确性分离。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day41/code/minimal_batch_memory.py
```

应看到 global batch 16、4 个计划 checkpoint、约 6.064 GiB 估算，并明确 `not_profiled`。若 batch/累积不清楚补 [F13](../../foundation_library/f13_optimizer_overfitting/README.md)；参数边界回看 [Day 40](../day40/README.md)。

## 4. 即时知识

- **micro batch**：一次 forward/backward 放入设备的样本数，直接影响激活显存。
- **gradient accumulation**：累积多次梯度后再 step，放大全局 batch 而不等价于增加单步显存。
- **global batch**：micro × accumulation × world size。
- **mixed precision**：bf16/fp16 降低部分存储/计算成本；数值与算子支持需实测。
- **LoRA**：训练低秩增量矩阵的 PEFT；本项目当前未选中，因此关闭。
- **checkpoint/resume**：周期保存模型/optimizer/scheduler 状态，并能从最近完整点恢复。
- **headroom**：budget−estimate；预留给框架缓存、峰值算子与估算误差。

## 5. 成熟材料处方

- **主材料（PyTorch 官方，12 分钟）**：[Automatic Mixed Precision examples](https://docs.pytorch.org/docs/stable/notes/amp_examples.html)。只读 autocast、GradScaler、gradient accumulation 和 clipping 顺序；结合 F13 中文笔记。
- **补充材料（Hugging Face 官方，8 分钟）**：[PEFT LoRA developer guide](https://huggingface.co/docs/peft/developer_guides/lora)。只理解低秩 adapter 与 target modules；本日不安装 PEFT、不启用 LoRA。
- **锁定项目定位（8 分钟）**：[SmolVLA train config 第 1–22 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/configs/train/smolvla.yaml#L1-L22) 的真实默认是 CUDA、batch 64、100000 steps、每 5000 step 保存；本课有界配置是独立教学计划，不声称修改了锁定文件。

## 6. 最小实验

[minimal_batch_memory.py](code/minimal_batch_memory.py) 是完整 25 行代码：

```python
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
```

长文件 [validate_bounded_train_config.py](code/validate_bounded_train_config.py) 依次阅读方法/LoRA、batch、schedule、level、memory 估算与权限报告。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day41/code/validate_bounded_train_config.py \
  --config mainline/day41/config/bounded_train_config_a.json \
  --report learner_outputs/mainline/day41/bounded_train_report_a.json
```

应看到 `method=adapter_only global_batch=16 estimated_peak_gib=6.064 authorized=false command_run=false`。

未来在合格 Linux/NVIDIA 主机上，先用真实 policy parameter report 替换规划参数量，用单 batch dry-run 记录 `torch.cuda.max_memory_allocated()`；若余量不足，先降 micro batch/activation，再保持 global batch 口径。确认 checkpoint 同时保存 adapter、optimizer、scheduler、step/config hash，并做一次 resume rehearsal。只有另行授权后才把有界值映射到 trainer；当前不执行锁定 train command。

## 8. 独立挑战

用 B config 生成新 report。写 ≥240 字 memo，必须原样包含 `adapter-only`、`LoRA`、`single repair`、`micro batch`、`gradient accumulation`、`global batch`、`mixed precision`、`memory estimate`、`headroom`、`checkpoint`、`resume`、`max steps`、`authorized`、`CUDA`、`not profiled`。解释 B 算术、为什么关闭 LoRA，以及实际 profile 的验收证据。正文不给 B 峰值。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day41.tests.test_day41_tools
.venv-day06/bin/python mainline/day41/code/check_day41.py \
  --example-config mainline/day41/config/bounded_train_config_a.json --example-report learner_outputs/mainline/day41/bounded_train_report_a.json \
  --challenge-config mainline/day41/config/bounded_train_config_b.json --challenge-report learner_outputs/mainline/day41/bounded_train_report_b.json \
  --challenge-memo learner_outputs/mainline/day41/challenge_memo.md
```

口述 10 分：batch 算术 2；precision/显存组成 2；单一 repair/LoRA 2；checkpoint/resume 2；估算/授权边界 2。机器通过且 ≥8 进入 Day 42；叠加 LoRA、余量不足、无 max steps、只存模型不存状态或把估算当 profile 均不通过。

## 10. 证据复盘

- 已运行：A/B 免费配置算术、global batch、显存假设、20% headroom、checkpoint/resume 与 level 边界。
- 静态源码事实：锁定 SmolVLA 默认训练配置的 dataset/device/batch/steps/checkpoint。
- 未运行：真实参数统计、CUDA memory profile、checkpoint 写入/resume、训练/GPU。
- 可以主张：教学配置有明确方法、上限、恢复点、余量和权限边界。
- 不能主张：8GB 实机一定可跑、bf16 稳定、checkpoint 可恢复或训练已获授权。

自测题（答案在 `shared/answer_keys/day41.md`）：

1. global batch 如何计算，什么主要影响激活显存？
2. mixed precision 能省什么，仍需检查什么？
3. 为什么本日关闭 LoRA？
4. memory estimate 为什么不能替代 profile？
5. checkpoint/resume/max steps 与 authorized 各控制什么？
