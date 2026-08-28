# Mainline Day 5：读懂真实 SmolVLA adapter 的输入与连续动作

今天不下载模型，而是回答一个先于模型权重的问题：锁定 SmolVLA evaluator 到底给 policy 什么 key、shape、dtype、device 和语言，policy 的 tensor 怎样回到 `env.step`。CPU fixture 真实执行同一预处理契约；权重加载与 CUDA 保持未运行。

## 1. 真实项目产物

- `learner_outputs/mainline/day05/locked_adapter_contract.json`：从锁定源码 AST 提取的接口卡；
- `learner_outputs/mainline/day05/interface_card_a.json`：A 输入的离线 shape/dtype/device/range；
- `learner_outputs/mainline/day05/interface_card_b.json`：独立挑战的新 shape、旋转和 task；
- 一段口述：图像/state/task 如何进入 policy，continuous action 如何进入 environment。

今天不修改 upstream 或模型配置，只运行教材工具并写 learner_outputs。

## 2. 当前卡点

“VLA 输入是图像和语言”太粗。锁定 adapter 实际使用外部相机、腕部相机、机器人 8 维 state 和 task 字符串；图像还要反转、归一化、换轴、转 dtype、移 device、加 batch。任何一步 shape 错误都可能在模型深处才报错。

输出也不是一句文字：`policy.select_action` 返回 tensor，adapter 把第一个 batch 搬回 CPU、转 NumPy，直接交给 `env.step`。后面比较 SmolVLA/OpenVLA 前，必须先冻结这种接口差异。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day05/code/minimal_nchw.py
```

应依次看到 raw `(2,2,3,3) uint8`、model `(2,3,2,3) torch.float32 cpu`、action `(1,7)`。NumPy shape/dtype 卡住去 [F07](../../foundation_library/f07_numpy_observations/README.md)，tensor/device 卡住去 [F09](../../foundation_library/f09_tensors/README.md)，不理解 module eval 去 [F12](../../foundation_library/f12_module_state_dict/README.md)。只补失败项。

## 4. 即时知识

- **HWC→CHW**：相机常给高×宽×通道，PyTorch 视觉模型常要通道×高×宽。
- **batch 轴**：单张图也变成 `[1,C,H,W]`；state 变 `[1,8]`。
- **dtype/range**：uint8 `[0,255]` 经 `/255.0` 和 `.float()` 成 float32 `[0,1]`。
- **device**：tensor 和 policy 必须在兼容设备；锁定配置默认 `cuda`。
- **eval 与 inference_mode**：`policy.eval()` 改模块行为，`torch.inference_mode()` 关闭梯度记录；真实推理两者都用。
- **continuous action**：adapter 把 tensor 转成 NumPy 第 0 个 batch，交给环境；本课 fixture 只验证 `[1,7]→[7]` 接口。

## 5. 成熟材料处方

- **主材料（中文，25 分钟）**：[《动手学深度学习》5.6 GPU](https://zh.d2l.ai/chapter_deep-learning-computation/use-gpu.html)。只读设备查询、tensor 与模型搬移，重点理解“数据和模型要在同一 device”。
- **补充材料（英文官方，10 分钟）**：[PyTorch `inference_mode`](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html)。阅读地图：只看作用、上下文管理器示例，以及它不自动调用 `model.eval()` 的提示。

## 6. 最小实验

[minimal_nchw.py](code/minimal_nchw.py) 是完整 22 行示例：

```python
#!/usr/bin/env python3
"""最小 HWC uint8 → NCHW float32 转换。"""

import numpy as np
import torch

# 两张 2×3 RGB 图像组成 NumPy batch；真实 adapter 是逐张图像再加 batch 轴。
images_hwc = np.arange(2 * 2 * 3 * 3, dtype=np.uint8).reshape(2, 2, 3, 3)
print("raw", images_hwc.shape, images_hwc.dtype)

# /255 把像素缩放到 [0,1]；from_numpy 保留共享内存和数值。
images = torch.from_numpy(images_hwc / 255.0)
print("scaled", images.shape, images.dtype, float(images.min()), float(images.max()))

# permute 只换轴语义：N,H,W,C → N,C,H,W；模型通常读取 channel-first。
images_nchw = images.permute(0, 3, 1, 2).to(torch.float32)
print("model", tuple(images_nchw.shape), images_nchw.dtype, images_nchw.device)

# inference_mode 表示只推理；fixture action 不是 SmolVLA 权重输出。
with torch.inference_mode():
    fixture_action = torch.linspace(-1.0, 1.0, 7).unsqueeze(0)
print("action", tuple(fixture_action.shape), fixture_action.dtype)
```

`fixture_action` 由 `linspace` 人工构造，绝不是 SmolVLA 输出；它只让你看到 continuous action 的 batch 契约。

## 7. 真实 VLA-Arena 操作

```bash
VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
.venv-day06/bin/python mainline/day05/code/trace_adapter.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --output learner_outputs/mainline/day05/locked_adapter_contract.json
.venv-day06/bin/python mainline/day05/code/build_interface_card.py \
  --input shared/fixtures/day05_interface_a.json \
  --output learner_outputs/mainline/day05/interface_card_a.json
.venv-day06/bin/python -m json.tool learner_outputs/mainline/day05/interface_card_a.json
```

应看到 image `[1,3,2,3]`、wrist `[1,3,2,2]`、state `[1,8]`、action `[1,7]`，全部 CPU float32；同时 `real_model_loaded=false`。

锁定证据：

- [`Args` 的 policy_path/device/suite](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L63-L99)
- [`initialize_model`: from_pretrained→device→eval](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L173-L178)
- [两路图像、state、task、inference_mode 与 select_action](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L262-L305)
- [锁定 SmolVLA YAML 默认 CUDA](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/configs/evaluation/smolvla.yaml#L1-L28)

工程文件 [build_interface_card.py](code/build_interface_card.py) 完整实现四元数→axis-angle、两路 tensor 和接口卡；[trace_adapter.py](code/trace_adapter.py) 只读锁定 blob，不 import SmolVLA 依赖。

## 8. 独立挑战

换用 `shared/fixtures/day05_interface_b.json`，生成 `learner_outputs/mainline/day05/interface_card_b.json`。先手写预测：两路 image、state、action 的 shape/dtype/device，以及 B 的非单位四元数是否改变 state 数值。

不给运行命令；用 `--help` 和示例自行迁移。B 同时改变图像尺寸、raw state dtype、旋转和 task，验收器会重新计算完整数值范围与 axis-angle；复制 A 后只改 form_id 不能通过。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day05.tests.test_day05_tools
.venv-day06/bin/python mainline/day05/code/check_day05.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --contract learner_outputs/mainline/day05/locked_adapter_contract.json \
  --example-input shared/fixtures/day05_interface_a.json \
  --example-card learner_outputs/mainline/day05/interface_card_a.json \
  --challenge-input shared/fixtures/day05_interface_b.json \
  --challenge-card learner_outputs/mainline/day05/interface_card_b.json
```

口述 10 分：两路图像转换 3；8 维 state 2；task 语言 1；eval/inference/device 2；action 与未加载模型边界 2。机器通过且 ≥8 进入 Day 6；5–7 分按弱项补 F07/F09/F12。

## 10. 证据复盘

- 已运行：CPU NumPy/PyTorch 预处理、真实锁定 adapter AST 提取、A/B 内容验收。
- 未运行：`SmolVLAPolicy.from_pretrained`、模型权重、CUDA、真实 `select_action` 和 episode。
- 能主张：接口 key、预处理顺序和静态调用契约对应锁定 commit。
- 不能主张：fixture action 是模型动作、SmolVLA 可加载或在目标 suite 有任何成功率。

自测题（答案在 `shared/answer_keys/day05.md`）：

1. 两路 uint8 HWC 图像如何变成 policy tensor？
2. 为什么 raw state 有 3+4+2 项，prepared state 却是 8 维？
3. `policy.eval()` 和 `torch.inference_mode()` 有何不同？
4. action tensor 怎样进入 `env.step`？
5. CPU fixture 通过后仍有哪些事实未知？
