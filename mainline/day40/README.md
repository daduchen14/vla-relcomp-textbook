# Mainline Day 40：定义双项 loss 与可训练/冻结参数边界

今天把 Day 39 的同动作 instruction pairs 转成训练接口：`action loss` 让两臂预测同一动作 target，`pair consistency` 约束两臂预测接近；只有 `relation_adapter.weight` 可训练，backbone 与 action head 冻结。免费 CPU toy model 实际执行 forward/backward 并检查梯度，但不做 optimizer step，也不冒充 SmolVLA。

## 1. 真实项目产物

- `trainability_report_a.json`：loss 分项/权重、每个参数的 numel、requires_grad、梯度与冻结统计；
- [build_trainability_report.py](code/build_trainability_report.py)：CPU 参数边界 rehearsal；
- B 新 tensor/config 的 report 与 `challenge_memo.md`。

## 2. 当前卡点

只写“冻结 backbone”无法证明 optimizer 前的参数标志和 backward 结果正确；把所有参数交给 optimizer 又会把“最小修复”变成全模型微调。只用 consistency loss 可能让两臂输出同一个错误动作；只用 action loss 则没有直接利用配对结构。

本课冻结两个 loss weight，并报告每个参数。adapter 必须 `requires_grad=True` 且梯度非零；冻结参数必须 `requires_grad=False`、`grad=None`。今天故意不调用 optimizer step：先证明计算图和边界，再在 Day 41 配置实际轻量训练。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day40/code/minimal_gradient_boundary.py
```

应看到只有 `relation_adapter.weight` 为 `trainable=True grad=True`，其余均 false。若 autograd 卡住补 [F10](../../foundation_library/f10_autograd/README.md)；参数注册/冻结补 [F12](../../foundation_library/f12_module_state_dict/README.md)。

## 4. 即时知识

- **action loss**：control/normalized 各自与同一动作 target 的 MSE 平均。
- **pair consistency**：两臂预测之间的 MSE；不能替代动作监督。
- **loss weight**：两项 loss 的冻结相对系数；不得事后按测试结果调。
- **parameter group**：按模块职责分出的 trainable/frozen 参数集合。
- **requires_grad**：是否为该 tensor 记录梯度；不等于已经被 optimizer 更新。
- **gradient boundary**：backward 后 adapter 有梯度、冻结参数无梯度。
- **optimizer step**：真正更新参数的动作；本日不执行。

## 5. 成熟材料处方

- **主材料（PyTorch 官方，12 分钟）**：[Autograd 基础教程](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)。只读 `requires_grad`、`backward()` 与禁用梯度部分；结合 F10 中文笔记。
- **补充材料（PyTorch 官方，6 分钟）**：[Module.requires_grad_](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.requires_grad_)。理解模块级冻结只是设置参数标志，仍需逐名报告确认。
- **锁定项目定位（10 分钟）**：[SmolVLA trainer 第 71–120 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/trainer.py#L71-L120) 的真实顺序是 policy forward→backward→unscale/clip→optimizer step→zero grad；[第 164–178 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/trainer.py#L164-L178) 创建 optimizer 并统计 `requires_grad` 参数。本日只演练前半段。

## 6. 最小实验

[minimal_gradient_boundary.py](code/minimal_gradient_boundary.py) 是完整 24 行代码：

```python
#!/usr/bin/env python3
"""最小例子：冻结 backbone/head，只让 relation_adapter 接收梯度。"""

import torch
from torch import nn

model = nn.ModuleDict({
    "backbone": nn.Linear(4, 4),
    "relation_adapter": nn.Linear(4, 4, bias=False),
    "action_head": nn.Linear(4, 2),
})
for name, parameter in model.named_parameters():
    parameter.requires_grad = name.startswith("relation_adapter.")

x = torch.tensor([[1.0, 0.0, 0.5, -0.5]])
hidden = model["backbone"] (x).detach()
prediction = model["action_head"] (model["relation_adapter"] (hidden))
target = torch.tensor([[0.2, -0.1]])
loss = torch.nn.functional.mse_loss(prediction, target)
loss.backward()

for name, parameter in model.named_parameters():
    print(f"{name}: trainable={parameter.requires_grad} grad={parameter.grad is not None}")
print(f"loss={loss.item():.6f}")
```

长文件 [build_trainability_report.py](code/build_trainability_report.py) 依次阅读 toy module、参数分类、双臂 loss、backward 与参数报告。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day40/code/build_trainability_report.py \
  --input shared/fixtures/day40_trainability_a.json \
  --config mainline/day40/config/trainability_config_a.json \
  --report learner_outputs/mainline/day40/trainability_report_a.json
```

应看到 `trainable=['relation_adapter.weight'] frozen_grad_count=0 optimizer_step=false runtime=cpu_toy`。

真实接入时先对锁定 policy 打印 `named_parameters()`，按 Day 36 唯一修复映射 trainable prefixes；在 optimizer 创建前保存完整 parameter report，并用一个 L0 batch 只做 forward/backward。检查 loss 有限、adapter 梯度非零、冻结参数无梯度，再销毁进程。若名字不匹配或有未分类参数，停止；不能通过放开全模型“解决”。当前没有 SmolVLA 权重/forward、CUDA 或训练 step。

## 8. 独立挑战

用 B input/config 生成新 report。写 ≥240 字 memo，必须原样包含 `action loss`、`pair consistency`、`loss weight`、`relation_adapter`、`backbone`、`action_head`、`requires_grad`、`parameter group`、`gradient`、`frozen`、`optimizer step`、`CPU toy`、`SmolVLA`、`training evidence`。解释两项 loss、三组模块、预期梯度和不能主张的内容。正文不给 B loss 数值。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day40.tests.test_day40_tools
.venv-day06/bin/python mainline/day40/code/check_day40.py \
  --example-input shared/fixtures/day40_trainability_a.json --example-config mainline/day40/config/trainability_config_a.json --example-report learner_outputs/mainline/day40/trainability_report_a.json \
  --challenge-input shared/fixtures/day40_trainability_b.json --challenge-config mainline/day40/config/trainability_config_b.json --challenge-report learner_outputs/mainline/day40/trainability_report_b.json \
  --challenge-memo learner_outputs/mainline/day40/challenge_memo.md
```

口述 10 分：双项 loss 2；权重/监督边界 2；parameter groups 2；梯度检查 2；toy/真实训练边界 2。机器通过且 ≥8 进入 Day 41；只用 consistency、全参数可训练、冻结参数有梯度、执行 optimizer 或把 toy 当 SmolVLA 均不通过。

## 10. 证据复盘

- 已运行：A/B 免费 CPU toy forward/backward、双项 loss、逐参数 requires_grad 与梯度重建。
- 静态源码事实：锁定 trainer 的 forward/backward/clip/step 顺序和 learnable 参数统计。
- 未运行：真实 policy 参数映射、SmolVLA forward、optimizer、CUDA/GPU。
- 可以主张：toy 计算图只让 adapter 接收梯度，冻结边界和 loss 公式可复算。
- 不能主张：真实参数名已经匹配、loss 会下降、训练稳定或修复有效。

自测题（答案在 `shared/answer_keys/day40.md`）：

1. action loss 与 pair consistency 各解决什么？
2. loss weight 为什么要预先冻结？
3. 哪个参数组可训练，哪些冻结？
4. adapter 有 gradient 能证明什么、不能证明什么？
5. 本日是否执行 optimizer step，是否属于 training evidence？
