# Mainline Day 44：检查数值稳定性并冻结训练 recipe

今天把 Day 43 的短 pilot 收敛为不可静默改动的 recipe：固定 toy 底座，改变三个训练 seed，实际检查有限 loss、梯度 norm 与结果离散度；再注入 NaN，要求在 backward/optimizer step 前中止。通过后输出带 SHA-256 的 frozen recipe，但仍不授权正式训练。

## 1. 真实项目产物

- `stability_report_a.json`：三 seed 的 loss、pre-clip grad norm、离散度与 NaN 注入结果；
- `frozen_recipe_a.json`：方法、底座 seed、训练 seed、超参数、input/config hash 和 recipe hash；
- B 新 input/config 的同类证据与 `challenge_memo.md`。

## 2. 当前卡点

一次 pilot 成功不代表稳定：换 mini-batch 顺序可能发散，NaN 也可能经过 optimizer 污染参数。反之，把预训练底座也随 seed 重置，会把模型差异误算成训练随机性。

本课固定 `model_init_seed` 模拟同一预训练底座，只让每个训练 seed 改变 mini-batch 抽样；三次 final loss 的相对 spread 必须 ≤0.25。NaN target 必须在 backward 前被 finite guard 捕获，并用 adapter hash 证明没有 step。recipe 的任何字段变化都生成新 hash。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day44/code/minimal_finite_guard.py
```

应先打印 3 个有限 loss/grad norm，再出现 `caught_nonfinite_before_step=4`。若 seed 与 batch 顺序不清楚补 [F14](../../foundation_library/f14_dataloader/README.md)；训练恢复回看 [Day 43](../day43/README.md)。

## 4. 即时知识

- **numerical stability**：loss/gradient/parameter 在规定范围内保持 finite，且不同 seed 行为可解释。
- **训练 seed**：控制 batch 顺序等随机过程；不等于更换预训练底座。
- **finite guard**：在有害操作前检查 NaN/Inf，并立即中止。
- **pre-clip norm**：裁剪前的梯度总范数；用于发现尖峰。
- **gradient clipping**：把过大梯度缩到阈值内，不负责掩盖 non-finite。
- **anomaly injection**：主动加入已知坏输入，验证防护确实会触发。
- **spread**：本课用 `(max final−min final)/mean final` 比较 seed 离散度。
- **frozen recipe**：带身份 hash 的确定配置；改动必须新建 recipe id 并重跑审计。

## 5. 成熟材料处方

- **中文主材料（PyTorch 中文文档，10 分钟）**：[随机性说明](https://docs.pytorch.ac.cn/docs/stable/notes/randomness.html)。只读 seed、确定性与“跨版本/平台不保证完全一致”；把结论写进边界。
- **补充材料（PyTorch 官方，8 分钟）**：[clip_grad_norm_](https://docs.pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html)。重点看返回总 norm 与 `error_if_nonfinite`，不要把 clipping 当 NaN 修复器。
- **锁定项目定位（10 分钟）**：[SmolVLA train 第 82–104 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/scripts/train.py#L82-L104) 展示 autocast、backward、unscale、clip、step 的真实顺序；[第 134–140 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/scripts/train.py#L134-L140) 设置 seed，但同时开启 cuDNN benchmark/TF32，真实复现报告必须记录这些开关。

## 6. 最小实验

[minimal_finite_guard.py](code/minimal_finite_guard.py) 是完整 21 行代码：

```python
#!/usr/bin/env python3
"""最小例子：固定 seed、裁剪梯度，并在 step 前拒绝 NaN。"""

import torch

torch.manual_seed(44)
weight = torch.nn.Parameter(torch.randn(()))
optimizer = torch.optim.SGD([weight], lr=0.1)

for step in range(1, 5):
    target = torch.tensor(float("nan") if step == 4 else 2.0)
    optimizer.zero_grad()
    loss = (weight - target).square()
    if not torch.isfinite(loss):
        print(f"caught_nonfinite_before_step={step}")
        break
    loss.backward()
    norm = torch.nn.utils.clip_grad_norm_([weight], max_norm=1.0,
                                           error_if_nonfinite=True)
    optimizer.step()
    print(f"step={step} loss={loss.item():.6f} grad_norm={norm.item():.6f}")
```

长文件 [audit_and_freeze_recipe.py](code/audit_and_freeze_recipe.py) 依次阅读固定底座/随机 batch、finite guard、pre-clip norm、NaN 注入和 canonical recipe hash。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day44/code/audit_and_freeze_recipe.py \
  --input shared/fixtures/day44_stability_a.json \
  --config mainline/day44/config/candidate_recipe_a.json \
  --report learner_outputs/mainline/day44/stability_report_a.json \
  --frozen-recipe learner_outputs/mainline/day44/frozen_recipe_a.json
```

A 应得到 3 个 finite seed runs、spread 约 0.142、NaN 在 step 前被捕获，并输出 recipe hash。精确值由机器重建。

未来真实操作要在获授权 Linux/NVIDIA 环境固定 Day 41/43 配置与 pretrained checkpoint，分别运行预注册 seed；记录 loss、unscaled pre-clip norm、GradScaler skipped steps、CUDA 错误和环境 fingerprint。用单独 dry-run 注入/模拟 non-finite，绝不污染候选 checkpoint。通过真实阈值后才能冻结 formal recipe；当前 recipe 仅供 CPU 教学。

## 8. 独立挑战

用 B input/config 生成新 report/frozen recipe。写 ≥260 字 memo，必须原样包含 `numerical stability`、`seed`、`finite loss`、`gradient clipping`、`pre-clip norm`、`NaN`、`abort before step`、`anomaly injection`、`spread`、`frozen recipe`、`recipe hash`、`silent change`、`CPU toy`、`SmolVLA`、`formal training`。正文不给 B 数值或 hash。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day44.tests.test_day44_tools
.venv-day06/bin/python mainline/day44/code/check_day44.py \
  --example-input shared/fixtures/day44_stability_a.json --example-config mainline/day44/config/candidate_recipe_a.json --example-report learner_outputs/mainline/day44/stability_report_a.json --example-recipe learner_outputs/mainline/day44/frozen_recipe_a.json \
  --challenge-input shared/fixtures/day44_stability_b.json --challenge-config mainline/day44/config/candidate_recipe_b.json --challenge-report learner_outputs/mainline/day44/stability_report_b.json --challenge-recipe learner_outputs/mainline/day44/frozen_recipe_b.json \
  --challenge-memo learner_outputs/mainline/day44/challenge_memo.md
```

口述 10 分：seed/固定底座 2；finite/gradient 2；异常注入 2；spread 2；冻结/证据边界 2。机器通过且 ≥8 进入 Day 45；更换底座冒充 seed、NaN 后仍 step、只报 clipped norm、静默改 config 或声称 formal training 已授权均不通过。

## 10. 证据复盘

- 已运行：A/B 各三 seed CPU toy、finite loss、pre-clip norm、spread、NaN 注入与 recipe hash。
- 静态源码事实：锁定 trainer 的 AMP/backward/unscale/clip/step 顺序和 seed/CUDA 开关。
- 未运行：SmolVLA、真实 batch、CUDA/GradScaler、正式多 seed training。
- 可以主张：教学 recipe 在固定 toy 底座上满足预设离散度，异常 guard 有效且内容已 hash。
- 不能主张：真实模型数值稳定、跨 GPU 完全确定、formal recipe 已冻结或训练已获授权。

自测题（答案在 `shared/answer_keys/day44.md`）：

1. 为什么固定 model init、只改变训练 seed？
2. 梯度裁剪应记录裁剪前还是裁剪后的 norm，为什么？
3. NaN anomaly injection 怎样才算安全通过？
4. recipe hash 防止什么问题？
5. 为什么 frozen recipe 仍写 `authorized_for_formal_training=false`？
