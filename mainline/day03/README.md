# Mainline Day 3 样章：沿锁定 evaluator 追踪 observation→policy→action→step→success

本章是 V2 教学方法的代表性样章。它不会启动 MuJoCo、下载模型或使用 GPU；免费本地部分会真实运行，VLA-Arena 部分通过锁定源码做静态追踪。完成本章不等于已经获得真实 episode 成功结果。

## 1. 真实项目产物

今天必须生成两份项目证据：

1. `learner_outputs/mainline/day03/observation_summary.json`：真实 evaluator 所需 raw observation key 的 shape、dtype 和数值范围摘要；数据来自明确标记的本地 fixture。
2. `learner_outputs/mainline/day03/locked_call_chain.md`：从锁定 commit 实际源码生成的调用链图，覆盖 observation→policy→action→step→success。

机器验收还会检查你是否把 fixture 误写成真实 VLA-Arena 运行结果。

## 2. 当前卡点

“observation”可以先理解成机器人每走一步前收到的一只**资料袋**。资料袋不是只有照片：里面可能有外部相机图、腕部相机图、末端位置、旋转姿态和夹爪开合。policy 读取这只资料袋以及任务语言，决定下一条 action；环境执行 action 后，返回下一只资料袋和 `done/info`。

如果只盯着模型名称，很容易漏掉真正的实验契约：图像是否上下翻转、state 拼了哪些字段、action 有几维、`done` 究竟代表成功还是超时。本项目之后的行为诊断都依赖你今天把这条链说清楚。

## 3. 前置诊断

不用查资料，先回答并实际做：

- 对 `(2, 3, 3)` 的图像数组，说出每个轴可能代表什么，并指出 `uint8` 与 `float32` 的差别。
- 从 Python 字典取出 `robot0_eef_pos`；当 key 不存在时，让程序明确失败。
- 看一段 `for`/`while` loop，指出哪一行更新 observation，哪一行决定退出。

第一项卡住去 [F07](../../foundation_library/f07_numpy_observations/README.md)，tensor/device 也卡住再去 [F09](../../foundation_library/f09_tensors/README.md)；字典/函数卡住去 [F03](../../foundation_library/f03_modules_testing/README.md)；episode loop 卡住去 [F08](../../foundation_library/f08_episode_evaluator/README.md)。能完成就全部跳过。

## 4. 即时知识

只补今天需要的四件事：

1. **字典**把名字映射到值。`obs['agentview_image']` 的 key 是接口契约，拼错不会“差不多能用”。
2. **shape** 是每个轴的长度。例如 `(H, W, C)` 表示高、宽、颜色通道；shape 本身不告诉你像素是否归一化。
3. **dtype** 是单个元素的编码。相机常是 `uint8`，模型 state 常是浮点数；转换 dtype 可能改变精度和内存。
4. **episode loop** 重复“读 observation → policy 产 action → `env.step(action)`”。锁定实现中 `done` 可能由成功或 timeout 触发，因此最终成功要看 `info['success']` 的语义。

锁定 random evaluator 的 `prepare_observation` 会把 raw 字典变成 `agent_image`、`wrist_image` 和 `state`。两路图像在高/宽轴反转并转为 contiguous；state 是末端位置 3 维、四元数转 axis-angle 后 3 维、夹爪位置 2 维的拼接，通常是 8 维。这里不展开四元数数学，因为今天只需识别接口与数据流。

## 5. 成熟材料处方

- **主材料（中文，35 分钟）**：[《动手学深度学习》2.1 数据操作](https://zh.d2l.ai/chapter_preliminaries/ndarray.html)。只读“入门、运算符、广播机制、索引和切片”，把每个例子的 shape 与 dtype 说出来；无需做完整章习题。
- **补充材料（中文，15 分钟）**：[Python 3 中文教程 5.5 字典](https://docs.python.org/zh-cn/3/tutorial/datastructures.html#dictionaries)。只练 key 访问、成员判断和遍历；今天不学习高级容器。

项目源码不是额外泛读材料；下一节按给定文件和函数定位即可。

## 6. 最小实验

[完整注释代码](code/minimal_episode_trace.py) 只有一个本地 fixture policy 和环境，不冒充 VLA-Arena。逐行读完再运行：

```python
#!/usr/bin/env python3
"""32 行左右的 observation→policy→action→step→success 最小闭环。"""

import numpy as np


def policy(observation):
    # policy 读 observation 字典；这里用 state 的第一项产生确定性动作。
    direction = 1.0 if observation["state"][0] >= 0 else -1.0
    return np.array([direction, 0, 0, 0, 0, 0, -1], dtype=np.float32)


def env_step(action, step_index):
    # fixture 环境模拟真实 env.step 的四元组返回值。
    next_observation = {
        "agent_image": np.zeros((2, 2, 3), dtype=np.uint8),
        "state": np.array([0.1 + step_index, 0.0, 0.0], dtype=np.float32),
    }
    success = bool(step_index == 2 and action[0] > 0)
    return next_observation, 0.0, success, {"success": success}


observation = {
    "agent_image": np.zeros((2, 2, 3), dtype=np.uint8),
    "state": np.array([0.1, 0.0, 0.0], dtype=np.float32),
}
for step_index in range(5):
    action = np.clip(policy(observation), -1.0, 1.0)
    observation, reward, done, info = env_step(action, step_index)
    success = bool(info.get("success", done))
    print(step_index, action.shape, action.dtype, success)
    if done:
        break
```

```bash
.venv-day06/bin/python mainline/day03/code/minimal_episode_trace.py
.venv-day06/bin/python mainline/day03/code/summarize_observation.py
.venv-day06/bin/python -m json.tool learner_outputs/mainline/day03/observation_summary.json
```

预期最小 loop 在 step 2 停止；摘要明确写 `source_kind=local_fixture_not_vla_arena_run`。

## 7. 真实 VLA-Arena 操作

先定位一个只读的 VLA-Arena checkout，把下方占位路径换成你机器上的实际路径：

```bash
VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
git -C "$VLA_ARENA_LOCKED" rev-parse HEAD
python3 mainline/day03/code/trace_locked_evaluator.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --output learner_outputs/mainline/day03/locked_call_chain.md
sed -n '1,120p' learner_outputs/mainline/day03/locked_call_chain.md
```

第一条命令必须输出 `babe582ebffc82b979b77964a7e56417d02f63a4`；工具会再次核对，不匹配就失败。它使用 AST 读取源码，不 import VLA-Arena，因此不需要 MuJoCo。

按以下锁定证据逐边核对你的图：

- [`EvaluatorConfig` 与 `get_action`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/random/evaluator.py#L40-L89)：random policy 返回 7 维动作。
- [`prepare_observation`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/random/evaluator.py#L153-L168)：raw key、图像处理和 state 拼接。
- [`run_episode`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/random/evaluator.py#L187-L233)：等待步、policy、action、`env.step` 与 success 判定。
- [`BDDLBaseDomain._get_observations`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/bddl_base_domain.py#L946-L999)：环境如何汇集 NumPy observation 字典。
- [`_check_success` 与 `step`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/bddl_base_domain.py#L1137-L1207)：goal predicates 如何成为 `success/done/info`。
- [`is_success_done`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/utils/eval_cost.py#L16-L28)：优先读 `info['success']`。
- [`random.yaml`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/configs/evaluation/random.yaml#L1-L19)：官方默认指向 safety suite；教材侧 [追踪配置](config/random_preposition_trace.yaml) 只在教材仓库把 suite 改为 `extrapolation_preposition_combinations`，没有覆盖 upstream。

重要边界：今天没有运行 `random evaluator` 的真实 episode，也没有生成真实 frame/success。静态追踪证明的是“锁定源码的数据流和接口仍匹配”，不是“仿真可运行”或“模型有效”。

## 8. 独立挑战

不要看 `shared/answer_keys/day03.md`。对新输入 `shared/fixtures/day03_observation_challenge.json` 独立完成：

- 生成 `learner_outputs/mainline/day03/challenge_summary.json`；
- 在调用链图下新增一段 120–200 字说明：新输入改变了哪些 shape/dtype，哪些调用链节点不变；
- 口述为什么 raw 四元数是 4 维，而准备后的 axis-angle 是 3 维，并指出你没有实际验证哪一部分。

可以使用今天的工具和两份成熟材料，但不给逐步命令。不得修改示例 fixture 来“适配”答案。

## 9. 验收 rubric

机器验收：

```bash
.venv-day06/bin/python -m unittest -v mainline.day03.tests.test_day03_tools
.venv-day06/bin/python mainline/day03/code/check_deliverables.py \
  --summary learner_outputs/mainline/day03/observation_summary.json \
  --call-chain learner_outputs/mainline/day03/locked_call_chain.md \
  --challenge learner_outputs/mainline/day03/challenge_summary.json
```

口述评分共 10 分：

- 2 分：用生活化语言解释 observation，并说出它不只包含图像；
- 2 分：把关键 raw key 的 shape、dtype 与语义对应，不把 shape 当数值范围；
- 3 分：不看图按 observation→policy→action→step→success 复述，指出 `env.step` 是运行时分派；
- 2 分：区分 `done`、timeout 与 `info['success']`；
- 1 分：明确 fixture、静态源码事实和真实 episode 结果的边界。

`8–10` 分且机器通过：进入下一主线日；`5–7` 分：按弱项补 F03/F07/F08/F09 后重测；`0–4` 分：停止扩张，先完成对应补习快速路径。代码排版不是主要分数。

## 10. 证据复盘

完成后在 `learner_outputs/mainline/day03/evidence_reflection.md` 写四栏：

| 证据类型 | 今天能写什么 | 不能写什么 |
|---|---|---|
| 本地 fixture 已运行 | 工具能总结 key/shape/dtype，最小 loop 能退出 | 不能称为 VLA-Arena observation 或成功率 |
| 锁定源码静态核对 | 指定 commit 存在这些函数、调用和配置字段 | 不能证明依赖、MuJoCo 或 GPU 可运行 |
| 真实 VLA-Arena | 今天未运行 | 不能填造 frame、日志、耗时或 success |
| 研究推断 | 数据流已具备后续插桩位置 | 不能由 random policy 调用链推出 RelComp 失败机制 |

### 自测题（先答，答案在共享答案区）

1. 为什么 observation 不能简单翻译成“相机图片”？
2. `(256, 256, 3)` 和 `uint8` 各回答什么问题？
3. `done=True` 为什么不能自动等同任务成功？
4. 从 evaluator 的 `env.step` 连到 `BDDLBaseDomain.step`，这条边与普通函数直接调用有何不同？

答案只在 [shared/answer_keys/day03.md](../../shared/answer_keys/day03.md)；完成独立挑战前不要打开。
