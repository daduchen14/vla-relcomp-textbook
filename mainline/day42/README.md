# Mainline Day 42：用同一个小 batch 做 overfit 闭环检查

今天实际运行免费 CPU optimizer：反复训练同一个 synthetic batch，要求 loss 降到冻结 target，adapter 参数 hash 改变，而 backbone/action head hash 保持不变。one-batch overfit 用来发现数据、loss、梯度、optimizer 或容量错误；它故意不测泛化，也不是 SmolVLA/GPU 结果。

## 1. 真实项目产物

- `overfit_trajectory_a.csv`：step 与 loss 的实际 CPU 轨迹；
- `overfit_report_a.json`：初末 loss、下降倍数、target、optimizer steps 与冻结 hash；
- B 新 batch/config 的同类证据与 `challenge_memo.md`。

## 2. 当前卡点

单次 backward 有梯度，只证明图连通；不能证明 optimizer 参数组、zero-grad、step 和 loss target 能形成闭环。反过来，一开始就跑大数据，loss 不降时很难区分数据噪声和代码错误。

本课固定同一 batch，容量足够且不做 augmentation/shuffle。adapter-only optimizer 反复 step，记录 trajectory；成功标准同时要求 target reached、至少 50× loss reduction、adapter changed、frozen hashes unchanged。任何一项失败都先排查，不扩数据或上 GPU。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day42/code/minimal_scalar_overfit.py
```

应看到 loss 从 9 降到接近 0、weight 接近 3、`target_reached=True`。若 optimizer/zero-grad 卡住补 [F13](../../foundation_library/f13_optimizer_overfitting/README.md)；梯度边界回看 [Day 40](../day40/README.md)。

## 4. 即时知识

- **one batch**：固定的一小组输入/target，所有 step 重复使用。
- **overfit smoke**：验证实现能记住小 batch；不是良好泛化的目标。
- **initial/final loss**：必须来自同一公式与同一 batch，才能计算 reduction factor。
- **target loss**：运行前冻结的停止阈值；不能按最终曲线事后移动。
- **optimizer step**：真正改变 adapter 参数；需配合 zero_grad/backward。
- **frozen hash**：冻结模块前后字节身份；比只看 `requires_grad` 更强。
- **capacity**：若所有接口正确仍无法记忆，允许模块可能表达能力不足。

## 5. 成熟材料处方

- **主材料（PyTorch 官方，8 分钟）**：[Zeroing out gradients](https://docs.pytorch.org/tutorials/recipes/recipes/zeroing_out_gradients.html)。只读梯度默认累积及每步 `zero_grad()` 的原因；结合 F13 中文内容。
- **补充材料（PyTorch 官方，8 分钟）**：[Saving and loading a general checkpoint](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html#saving-loading-a-general-checkpoint-for-inference-and-or-resuming-training)。只看 model/optimizer/step/loss 状态；本日尚不写 checkpoint。
- **锁定项目定位（10 分钟）**：[SmolVLA trainer 第 71–120 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/trainer.py#L71-L120) 展示真实 forward→backward→clip→step→zero-grad 顺序；[第 209–218 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/trainer.py#L209-L218) 构造 dataloader。未来 VLA smoke 必须固定同一取出的 batch，而不是让 iterator 前进。

## 6. 最小实验

[minimal_scalar_overfit.py](code/minimal_scalar_overfit.py) 是完整 18 行代码：

```python
#!/usr/bin/env python3
"""最小例子：反复训练同一个标量 batch，确认优化闭环。"""

import torch

weight = torch.nn.Parameter(torch.tensor(0.0))
optimizer = torch.optim.SGD([weight], lr=0.2)
target = torch.tensor(3.0)

for step in range(31):
    loss = (weight - target).square()
    if step in {0, 10, 20, 30}:
        print(f"step={step} loss={loss.item():.8f} weight={weight.item():.6f}")
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

print(f"target_reached={abs(weight.item() - target.item()) < 1e-5}")
```

长文件 [run_one_batch_overfit.py](code/run_one_batch_overfit.py) 依次阅读模型/冻结 hash、同一 batch、双项 loss、optimizer loop 与边界报告。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day42/code/run_one_batch_overfit.py \
  --input shared/fixtures/day42_one_batch_a.json \
  --config mainline/day42/config/overfit_config_a.json \
  --trajectory learner_outputs/mainline/day42/overfit_trajectory_a.csv \
  --report learner_outputs/mainline/day42/overfit_report_a.json
```

应看到 initial 约 `0.0769`、final ≤`0.001`、target reached、adapter changed、frozen unchanged、`cpu_toy=true`。精确 final/step 由机器重建。

未来真实 smoke 在授权环境加载一个 Day 39 L0 batch 后立刻缓存，固定随机增强，重复同一 tensor；只优化 Day 40 参数组，记录分项 loss、grad norm、CUDA peak memory 与所有冻结 hash。target 未达时依次查 batch/label join、loss、梯度、lr、precision、capacity；通过后丢弃 toy checkpoint，不能当候选模型。当前没有 SmolVLA 或 GPU。

## 8. 独立挑战

用 B batch/config 生成新 trajectory/report。写 ≥240 字 memo，必须原样包含 `one batch`、`overfit`、`initial loss`、`final loss`、`reduction factor`、`target loss`、`optimizer step`、`adapter changed`、`frozen hash`、`data pipeline`、`loss implementation`、`capacity`、`CPU toy`、`SmolVLA`、`generalization`。解释 B 是否通过和失败时的排查顺序。正文不给 B 数值。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day42.tests.test_day42_tools
.venv-day06/bin/python mainline/day42/code/check_day42.py \
  --example-input shared/fixtures/day42_one_batch_a.json --example-config mainline/day42/config/overfit_config_a.json --example-trajectory learner_outputs/mainline/day42/overfit_trajectory_a.csv --example-report learner_outputs/mainline/day42/overfit_report_a.json \
  --challenge-input shared/fixtures/day42_one_batch_b.json --challenge-config mainline/day42/config/overfit_config_b.json --challenge-trajectory learner_outputs/mainline/day42/overfit_trajectory_b.csv --challenge-report learner_outputs/mainline/day42/overfit_report_b.json \
  --challenge-memo learner_outputs/mainline/day42/challenge_memo.md
```

口述 10 分：overfit 目的 2；loss/target 2；optimizer loop 2；adapter/frozen hash 2；toy/generalization 边界 2。机器通过且 ≥8 进入 Day 43；换 batch、事后调 target、冻结参数变化、只截图曲线或把 toy 当 VLA 证据均不通过。

## 10. 证据复盘

- 已运行：A/B 免费 CPU toy optimizer、真实 loss 轨迹、target、adapter/frozen hash 与严格重建。
- 静态源码事实：锁定 trainer 的 optimizer loop 与 dataloader 入口。
- 未运行：真实 batch/tensor、SmolVLA、CUDA memory、checkpoint/GPU。
- 可以主张：toy adapter 在同一 synthetic batch 上达到冻结 target，且只改变允许参数。
- 不能主张：真实 data pipeline 正确、模型会 overfit、泛化改善或训练稳定。

自测题（答案在 `shared/answer_keys/day42.md`）：

1. one-batch overfit 验证什么，不验证什么？
2. 哪四个 loss 数值/条件必须报告？
3. adapter changed 与 frozen hash 各证明什么？
4. 无法 overfit 时优先检查什么？
5. CPU toy 通过能否作为 SmolVLA/generalization 证据？
