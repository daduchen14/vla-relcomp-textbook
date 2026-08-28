# Mainline Day 43：短训练 pilot、早停与中断恢复

今天实际运行免费 CPU pilot：先训练到指定 step 后人为中断，再从 checkpoint 继续；同时另跑未中断基线，要求两条路径的日志、停止点和模型 hash 完全一致。实验使用 synthetic tensor 与 tiny adapter，不是 SmolVLA/GPU/formal training 结果。

## 1. 真实项目产物

- `pilot_log_a.csv`：逐次验证的 train/validation loss、最佳值、耐心计数和事件；
- `latest_a.pt` 与 `pilot_report_a.json`：恢复所需状态、停止原因和证据边界；
- B 新输入/config 的同类证据与 `challenge_memo.md`。

## 2. 当前卡点

Day 42 证明固定 batch 能被记住，却没有回答数据流动后日志是否足够、验证指标何时停止、进程中断会不会改变结果。只看到 checkpoint 文件存在也不等于可恢复：若遗漏 optimizer state、step 或 early-stopping state，续跑会偷偷变成另一条轨迹。

本课把 A/B 的 `max_steps`、`eval_every`、`save_every`、`patience`、`min_delta` 与人为中断点预先冻结。resume 必须校验 input/config SHA-256；最终再与未中断基线比较完整日志和 adapter hash。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day43/code/minimal_resume.py
```

应看到 `resumed_from=3 final_step=6`。若不理解 optimizer state，补 [F13](../../foundation_library/f13_optimizer_overfitting/README.md)；若小 batch 本身不能下降，先回 [Day 42](../day42/README.md)。

## 4. 即时知识

- **training pilot**：有严格步数/资源上限的短训练，用来验证流程，不是正式实验。
- **training log**：按固定频率记录 step、train loss、validation loss 与事件。
- **validation loss**：不参与当前 optimizer step 的留出数据损失，用于监控而非训练。
- **early stopping**：验证指标连续不再满足改善条件时提前结束。
- **min_delta**：一次改善至少要超过的幅度；小抖动不重置耐心。
- **patience**：可容忍的连续无改善检查次数，不是训练 step 数。
- **checkpoint**：模型、optimizer、step、早停状态和身份 hash 的一致快照。
- **resume equivalence**：中断恢复路径与未中断路径得到相同日志、停止点和模型 hash。

## 5. 成熟材料处方

- **中文主材料（PyTorch 中文文档，12 分钟）**：[保存和加载通用 checkpoint](https://docs.pytorch.ac.cn/tutorials/beginner/saving_loading_models.html#saving-loading-a-general-checkpoint-for-inference-and-or-resuming-training)。只读模型、optimizer、epoch/step 与 loss 为什么要共同保存。
- **补充材料（Lightning 官方，8 分钟）**：[Early Stopping](https://lightning.ai/docs/pytorch/stable/common/early_stopping.html)。只看 `monitor`、`min_delta`、`patience` 的语义；本课自己实现最小逻辑，不引入 Lightning。
- **锁定项目定位（10 分钟）**：[SmolVLA train 第 163–173 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/scripts/train.py#L163-L173) 创建 optimizer 并在 `cfg.resume` 时加载训练状态；[第 260–285 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/scripts/train.py#L260-L285) 在更新后增加 step、判断日志/保存频率并保存 policy、optimizer、scheduler。

## 6. 最小实验

[minimal_resume.py](code/minimal_resume.py) 是完整 25 行代码：

```python
#!/usr/bin/env python3
"""最小例子：保存 step、参数和 optimizer，再从下一步继续。"""

from pathlib import Path
import torch

checkpoint = Path("learner_outputs/mainline/day43/minimal.pt")
checkpoint.parent.mkdir(parents=True, exist_ok=True)
weight = torch.nn.Parameter(torch.tensor(0.0))
optimizer = torch.optim.SGD([weight], lr=0.2)

for step in range(1, 4):
    optimizer.zero_grad()
    (weight - 3).square().backward()
    optimizer.step()
torch.save({"step": step, "weight": weight.detach(),
            "optimizer": optimizer.state_dict()}, checkpoint)

saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
weight = torch.nn.Parameter(saved["weight"])
optimizer = torch.optim.SGD([weight], lr=0.2)
optimizer.load_state_dict(saved["optimizer"])
for step in range(saved["step"] + 1, 7):
    optimizer.zero_grad(); (weight - 3).square().backward(); optimizer.step()
print(f"resumed_from={saved['step']} final_step={step} weight={weight.item():.6f}")
```

长文件 [run_cpu_training_pilot.py](code/run_cpu_training_pilot.py) 依次阅读冻结边界、checkpoint schema、验证/早停、interrupt 与 resume；[check_day43.py](code/check_day43.py) 会重建未中断基线。

## 7. 真实 VLA-Arena 操作

先人为中断 A，再用同一 checkpoint 恢复：

```bash
.venv-day06/bin/python mainline/day43/code/run_cpu_training_pilot.py \
  --input shared/fixtures/day43_pilot_a.json --config mainline/day43/config/pilot_config_a.json \
  --log learner_outputs/mainline/day43/pilot_log_a.csv --checkpoint learner_outputs/mainline/day43/latest_a.pt \
  --report learner_outputs/mainline/day43/interrupted_a.json --stop-after 18

.venv-day06/bin/python mainline/day43/code/run_cpu_training_pilot.py \
  --input shared/fixtures/day43_pilot_a.json --config mainline/day43/config/pilot_config_a.json \
  --log learner_outputs/mainline/day43/pilot_log_a.csv --checkpoint learner_outputs/mainline/day43/latest_a.pt \
  --report learner_outputs/mainline/day43/pilot_report_a.json --resume
```

A 应从 18 恢复并在 45 早停。机器会另跑未中断基线，而不是要求你手工相信该数字。

未来真实操作是在另行授权的 Linux/NVIDIA 环境把同样字段映射到锁定 trainer：限制 steps，保留本地日志，确认 checkpoint 包含 policy/optimizer/scheduler/config，杀掉一次进程再用 `cfg.resume` 恢复，并比较未中断对照。当前不运行 SmolVLA、VLA-Arena 环境或 GPU。

## 8. 独立挑战

换用 B input/config，在第 25 step 中断后恢复，生成 B log/checkpoint/report。写 ≥260 字 memo，必须原样包含 `pilot`、`training log`、`validation loss`、`early stopping`、`patience`、`min_delta`、`checkpoint`、`optimizer state`、`resume`、`uninterrupted baseline`、`model hash`、`CPU toy`、`SmolVLA`、`GPU`、`formal training`。解释如何判断恢复等价及为什么不能把 toy 证据外推。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day43.tests.test_day43_tools
.venv-day06/bin/python mainline/day43/code/check_day43.py \
  --example-input shared/fixtures/day43_pilot_a.json --example-config mainline/day43/config/pilot_config_a.json --example-log learner_outputs/mainline/day43/pilot_log_a.csv --example-checkpoint learner_outputs/mainline/day43/latest_a.pt --example-report learner_outputs/mainline/day43/pilot_report_a.json \
  --challenge-input shared/fixtures/day43_pilot_b.json --challenge-config mainline/day43/config/pilot_config_b.json --challenge-log learner_outputs/mainline/day43/pilot_log_b.csv --challenge-checkpoint learner_outputs/mainline/day43/latest_b.pt --challenge-report learner_outputs/mainline/day43/pilot_report_b.json \
  --challenge-memo learner_outputs/mainline/day43/challenge_memo.md
```

口述 10 分：pilot/日志 2；validation/早停 2；checkpoint 完整性 2；resume 等价性 2；toy/正式边界 2。机器通过且 ≥8 进入 Day 44；未换 B、改动中断后的配置、只保存权重、没有未中断对照或声称正式训练成功均不通过。

## 10. 证据复盘

- 已运行：A/B 免费 CPU toy pilot、人为中断、checkpoint 恢复、early stopping 与未中断等价重建。
- 静态源码事实：锁定 SmolVLA 的 optimizer/scheduler 创建、resume load、step/log/save 条件和 checkpoint 调用。
- 未运行：真实 training pairs tensor、SmolVLA、VLA-Arena env、CUDA/GPU 或 formal training。
- 可以主张：教学 pilot 在相同 input/config 下恢复后与未中断基线逐项一致。
- 不能主张：锁定 trainer 的真实 checkpoint 已验证、模型稳定、验证指标改善或正式训练可启动。

自测题（答案在 `shared/answer_keys/day43.md`）：

1. training pilot 要回答什么、不回答什么？
2. 为什么 resume 不能只保存模型权重？
3. patience 与 `min_delta` 各控制什么？
4. 怎样证明 resume 不是从头训练或悄悄换了一条轨迹？
5. CPU toy 通过后可以和不可以主张什么？
