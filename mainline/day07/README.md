# Mainline Day 7：用同一 episode 口径比较 OpenVLA 与 SmolVLA

今天把第二个真实模型 adapter 接到 Day 6 的同一实验单位：同 commit、suite、level、task、seed、init state、trial 数和 max steps。你会解释 OpenVLA 如何把 action token 解码成连续 7 维动作，生成计划态比较表；只有合格 GPU 环境实际跑完两边后，才允许比较结果。

## 1. 真实项目产物

- `learner_outputs/mainline/day07/openvla_manifest.json`：锁定 OpenVLA checkpoint 和单 episode 口径；
- `learner_outputs/mainline/day07/comparison.json` 与 `model_comparison.md`：SmolVLA/OpenVLA 同口径计划表；
- 合格 GPU 环境才产生 OpenVLA 的 preflight、log、video、registry；
- `learner_outputs/mainline/day07/fair_pair_answer.json`：对新候选 pair 的独立公平性判断；
- 2 分钟口述：token 如何回到 continuous action，哪些列是控制变量，为什么 planned 表没有性能结论。

## 2. 当前卡点

“两模型都跑 task 0”仍不够公平：seed、init state、step 上限或代码 commit 任一不同，都可能改变 episode。另一方面，“公平”不等于强行让模型内部相同——SmolVLA 的两路图像+state+语言和 OpenVLA 的 agent-view 图像+语言，本来就是被比较的 adapter 差异。

还有一层容易误读：锁定 OpenVLA 的 `prepare_observation` 构造了 `state`，但 `get_vla_action` 只从 dict 取 `full_image`，再把图像和语言交给 processor；不能看见 dict key 就断言 policy 使用它。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day07/code/minimal_token_decode.py
```

应看到 7 个 token ID 和 7 维 `continuous_action`。不理解 NumPy 向量/clip 去 [F07](../../foundation_library/f07_numpy_observations/README.md)，不理解 token ID 去 [F16](../../foundation_library/f16_tokens_embeddings/README.md)，不会逐字段控制实验去复习 [Day 6](../day06/README.md) 的 manifest。

## 4. 即时知识

- **action token**：OpenVLA 让 VLM 生成 7 个离散 token ID；锁定实现用 256 个边界形成 255 个 bin center，将 ID 映射回 `[-1,1]` 的归一化数。
- **反归一化**：checkpoint 的 `unnorm_key=vla_arena_l0_l` 选择训练数据的 `q01/q99`，把归一化值映射回每个动作维度的尺度。
- **gripper 后处理**：最后一维先从 `[0,1]` 归到 `[-1,+1]` 并二值化，OpenVLA 再反号以匹配环境约定。
- **单步与 chunk**：此 OpenVLA 路径每次 environment step 生成一组 7 token→一个 7D action；SmolVLA 一次生成 50 步 chunk 后排队执行。
- **同口径**：控制 episode 外部条件；模型输入、解码与资源需求是应被保留并报告的差异。

## 5. 成熟材料处方

- **中文主材料（12 分钟）**：[《动手学深度学习》词嵌入](https://zh.d2l.ai/chapter_natural-language-processing-pretraining/word2vec.html)。只读开头“独热向量/词嵌入”概念，建立 token ID 是离散符号而非连续机器人动作的边界。
- **OpenVLA 官方项目（英文，15 分钟）**：[OpenVLA README 的模型与推理说明](https://github.com/openvla/openvla#openvla-an-open-source-vision-language-action-model)。只读模型输入/输出和 `predict_action`；不要照其通用示例替换锁定 VLA-Arena adapter。

## 6. 最小实验

[minimal_token_decode.py](code/minimal_token_decode.py) 是完整 25 行 CPU 例子：

```python
#!/usr/bin/env python3
"""最小 action token → 归一化连续动作 → 数据尺度动作。"""

import numpy as np


def decode(token_ids: np.ndarray, vocab_size: int, q01: np.ndarray, q99: np.ndarray) -> np.ndarray:
    """复现锁定 OpenVLA `predict_action` 的核心解码公式。"""
    bins = np.linspace(-1.0, 1.0, 256)
    centers = (bins[:-1] + bins[1:]) / 2.0
    discrete = vocab_size - token_ids
    indices = np.clip(discrete - 1, 0, len(centers) - 1)
    normalized = centers[indices]
    return 0.5 * (normalized + 1.0) * (q99 - q01) + q01


if __name__ == "__main__":
    # fixture 的 vocab/q01/q99 是教学数值，不是 checkpoint 统计。
    ids = np.array([999, 936, 872, 808, 744, 680, 999])
    low = np.array([-0.1] * 6 + [0.0])
    high = np.array([0.1] * 6 + [1.0])
    action = decode(ids, vocab_size=1000, q01=low, q99=high)
    action[-1] = -np.sign(2 * action[-1] - 1)  # evaluator 的 gripper normalize + invert。
    print("token_ids", ids.tolist())
    print("continuous_action", np.round(action, 4).tolist())
```

fixture 只执行真实解码公式；token 与统计是人工值，不是 OpenVLA 预测或 checkpoint 内容。

## 7. 真实 VLA-Arena 操作

先生成两个计划态 manifest 和比较表：

```bash
export VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
.venv-day06/bin/python mainline/day06/code/build_pilot_manifest.py \
  --upstream "$VLA_ARENA_LOCKED" --config mainline/day06/config/pilot_a.json \
  --output learner_outputs/mainline/day06/pilot_a_manifest.json
.venv-day06/bin/python mainline/day07/code/build_openvla_manifest.py \
  --upstream "$VLA_ARENA_LOCKED" --config mainline/day07/config/openvla_a.json \
  --output learner_outputs/mainline/day07/openvla_manifest.json
.venv-day06/bin/python mainline/day07/code/build_fair_comparison.py \
  --smolvla-manifest learner_outputs/mainline/day06/pilot_a_manifest.json \
  --openvla-manifest learner_outputs/mainline/day07/openvla_manifest.json \
  --json-output learner_outputs/mainline/day07/comparison.json \
  --markdown-output learner_outputs/mainline/day07/model_comparison.md
```

表中两行都应是 `not_run`，success 为 `—`。静态工具精确检查锁定 [`GenerateConfig/initialize_model`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/openvla/evaluator.py#L62-L181)、[`run_episode`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/openvla/evaluator.py#L267-L363) 和 YAML，不加载 7B 模型。

同时核对 [VLA-Arena OpenVLA checkpoint 仓库](https://huggingface.co/VLA-Arena/openvla-7b-finetuned-vla-arena)、[`get_vla_action`: prompt→processor→predict_action](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/openvla/experiments/robot/openvla_utils.py#L168-L219)、[`predict_action`: generate→bin→q01/q99](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/openvla/prismatic/extern/hf/modeling_prismatic.py#L610-L654) 和 [gripper 后处理](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/openvla/evaluator.py#L252-L264)。这些是锁定项目证据，不是额外泛读材料。

只有 Day 4 基础 preflight 通过、最大 GPU 显存 ≥24000 MiB 且你已批准资源时，才运行 [完整 runner](code/run_openvla_single_pilot.py)：

```bash
python3.11 mainline/day07/code/run_openvla_single_pilot.py \
  --upstream "$VLA_ARENA_LOCKED" --pilot-config mainline/day07/config/openvla_a.json \
  --output-dir learner_outputs/mainline/day07/real_openvla_a
```

runner 在下载前检查版本、Linux/Python/NVIDIA/EGL/显存，按 revision 下载 snapshot，再运行同一 task/seed/init。当前教材制作没有执行此命令，也没有 OpenVLA 成败结果。

## 8. 独立挑战

打开 `shared/fixtures/day07_comparison_candidates.json`，逐字段选出唯一只改变模型族/checkpoint 的 pair。自行创建：

```json
{"selected_pair": "你的选择", "rejected_reasons": {"另一个 pair": "具体混杂字段"}}
```

保存为 `learner_outputs/mainline/day07/fair_pair_answer.json`。不给逐项提示；候选使用新 task/seed，不能从 A 比较表复制答案。验收器会重新计算每个 pair 的字段差异，并要求拒绝理由指出具体变量。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day07.tests.test_day07_tools
.venv-day06/bin/python mainline/day07/code/check_day07.py \
  --upstream "$VLA_ARENA_LOCKED" --config mainline/day07/config/openvla_a.json \
  --openvla-manifest learner_outputs/mainline/day07/openvla_manifest.json \
  --smolvla-manifest learner_outputs/mainline/day06/pilot_a_manifest.json \
  --comparison-json learner_outputs/mainline/day07/comparison.json \
  --candidates shared/fixtures/day07_comparison_candidates.json \
  --challenge-answer learner_outputs/mainline/day07/fair_pair_answer.json
```

真实 OpenVLA 完成后可追加 `--registry learner_outputs/mainline/day07/real_openvla_a/episode_registry.csv`。口述 10 分：token→continuous 3；unnorm/gripper 2；真实输入差异 2；控制变量 2；计划/结果边界 1。机器通过且 ≥8 进入 Day 8；5–7 补 F07/F16 或重做 pair。没有两边真实 registry 时禁止填写模型优劣。

## 10. 证据复盘

- 已运行：锁定 OpenVLA 源码/YAML 静态检查、CPU token 解码、控制变量比较与新 pair 验收。
- 未运行：7B checkpoint 下载、BF16 GPU 推理、OpenVLA episode；比较表只有计划和接口。
- 可以主张：两个计划使用相同 episode 口径；锁定 adapter 的输入和 action 解码路径不同。
- 不能主张：OpenVLA 更强/更弱、显存门槛保证不 OOM、单 episode 能代表模型总体能力。

自测题（答案在 `shared/answer_keys/day07.md`）：

1. action token 如何变成 7 维连续动作？
2. 锁定 OpenVLA policy 实际使用 observation 中哪些部分？
3. 公平比较必须固定哪些外部变量，哪些模型差异应保留？
4. 两个 planned manifest 能否支持“OpenVLA 胜过 SmolVLA”？
5. `unnorm_key` 错了为何不能只靠 shape 检查发现？
