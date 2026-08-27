# Mainline Day 6：把 SmolVLA 单任务 pilot 做成可审计证据

今天第一次把真实模型放进 episode 计划，但不把“配置写好了”说成“模型跑过了”。你会沿锁定 SmolVLA 源码确认 VLM 条件与 action chunk，生成一个固定 checkpoint、task、seed、init state 的单 episode manifest；有合格 Linux/NVIDIA 环境时再执行真实 runner。本机免费部分只做源码检查和 CPU 队列实验。

## 1. 真实项目产物

- `learner_outputs/mainline/day06/pilot_a_manifest.json`：由锁定源码和 A 配置生成的运行前 manifest；
- 合格 GPU 环境才产生 `preflight.json`、`episode.log`、`rollout.mp4`、`episode_registry.csv`；
- `learner_outputs/mainline/day06/pilot_b_manifest.json`：改变 task、seed、init state 的独立挑战；
- 2 分钟口述：VLM 条件是什么、action chunk 如何逐步执行、静态计划为何不是 pilot 结果。

这一天不修改 VLA-Arena、模型或 main。A/B manifest 中 `real_model_run=false` 是刻意保留的证据边界；真实运行后也不能手改它冒充结果，而要提交 runner 生成的独立 registry。

## 2. 当前卡点

直接运行锁定 YAML 会遍历 suite 的五个 task、每个默认 10 次，不是“最小 pilot”。只写 `policy_path` 也没有固定模型内容：Hub 仓库名可保持不变而文件更新。因此最小可信 pilot 必须同时固定两类版本和一组运行输入：

- 代码：VLA-Arena commit `babe582ebffc82b979b77964a7e56417d02f63a4`；
- 模型：repo `VLA-Arena/smolvla-vla-arena` + 40 位 revision `ef87aa3f97a4feaed69c93b9ed2014bba07acf8a`；
- 运行：suite、level、task、seed、init state、1 trial、300 max steps；
- 证据：preflight、log、video、registry，且基础设施失败不进入成功率分母。

模型 revision 来自 Hugging Face 模型仓库在本教材编写时公开的 SHA；runner 用该 SHA 下载 snapshot，不跟随未来的 `main`。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day06/code/minimal_action_queue.py
```

你应看到 7 个 step、`model_calls=3`；前三个动作来自同一 chunk。说不清 `[batch,time,action_dim]` 去 [F09 tensor](../../foundation_library/f09_tensors/README.md)，不会读 JSON 去 [F02 JSON](../../foundation_library/f02_csv_json/README.md)，不理解 loop/queue 去 [F08 episode loop](../../foundation_library/f08_episode_evaluator/README.md)。只补失败项。

## 4. 即时知识

- **VLM 条件**：SmolVLA 不是只看语言。两路 RGB、8 维机器人 state 和自然语言共同形成条件，action expert 据此生成动作块。
- **action chunk**：一次模型调用生成一段未来动作。锁定默认 `chunk_size=50`、`n_action_steps=50`；`select_action` 每个环境 step 只从队列弹出一项，队列空了才重新推理。
- **episode reset**：锁定 evaluator 在每个 episode 开头调用 `policy.reset()`，避免残留 chunk 串到下一局。
- **checkpoint provenance**：代码 commit 和模型 revision 都要固定；只固定其中一个仍不能复现。
- **pilot 分母**：真实 episode 即使失败也是有效观察；下载失败、OOM、MuJoCo 启动失败是基础设施错误，不算模型失败。

## 5. 成熟材料处方

- **中文主材料（8 分钟）**：[Python 中文官方文档：`collections.deque`](https://docs.python.org/zh-cn/3/library/collections.html#collections.deque)。只读 `append`、`extend`、`popleft`：它们正好对应“把 chunk 放入队列、每步弹出一个 action”。
- **项目主材料（英文官方，15 分钟）**：[Hugging Face SmolVLA 文档](https://huggingface.co/docs/lerobot/smolvla)。只读开头架构图说明：多相机、sensorimotor state、语言如何条件化 action expert；本日不做训练。
- **checkpoint 材料（项目模型卡，10 分钟）**：[VLA-Arena SmolVLA 模型卡](https://huggingface.co/VLA-Arena/smolvla-vla-arena)。只核对 2 路 256×256 RGB、8 维 state、7-DoF action、50 步 horizon；模型卡描述不是本地运行证据。
- **精确源码（10 分钟）**：[锁定配置的 chunk 参数](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/policies/smolvla/configuration_smolvla.py#L28-L43) 与 [`select_action` 队列](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/policies/smolvla/modeling_smolvla.py#L479-L507)。

## 6. 最小实验

[minimal_action_queue.py](code/minimal_action_queue.py) 是完整 29 行 CPU 示例：

```python
#!/usr/bin/env python3
"""用小数组演示 action chunk 何时推理、何时从队列取动作。"""

from collections import deque

import numpy as np


def rollout(num_steps: int = 7, chunk_size: int = 3) -> tuple[list[list[float]], int]:
    """每当队列为空就生成新 chunk；返回逐步动作和“推理”次数。"""
    queue: deque[np.ndarray] = deque()
    actions, model_calls = [], 0
    for step in range(num_steps):
        if not queue:
            # fixture 用确定数组代替模型；真实 SmolVLA chunk 形如 [batch, time, action_dim]。
            chunk = np.arange(chunk_size * 2, dtype=np.float32).reshape(chunk_size, 2)
            chunk += model_calls * 10
            queue.extend(chunk)
            model_calls += 1
        action = queue.popleft()
        actions.append(action.tolist())
        print(f"step={step} action={action.tolist()} remaining={len(queue)}")
    return actions, model_calls


if __name__ == "__main__":
    _, calls = rollout()
    print(f"model_calls={calls}")
```

它验证队列控制流，不包含图像、语言、SmolVLA 权重或环境，输出绝不能称为模型动作。

## 7. 真实 VLA-Arena 操作

先在任意本机做免费静态操作：

```bash
export VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
.venv-day06/bin/python mainline/day06/code/build_pilot_manifest.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --config mainline/day06/config/pilot_a.json \
  --output learner_outputs/mainline/day06/pilot_a_manifest.json
.venv-day06/bin/python -m json.tool learner_outputs/mainline/day06/pilot_a_manifest.json
```

应看到 `chunk_size: 50`、`n_action_steps: 50`、`status: planned`、`real_model_run: false`。工具通过 `git show HEAD:<path>` 读取锁定 blob，并检查真实的 `from_pretrained→to(device)→eval`、`select_action→env.step`，但不 import 模型。

只有 Day 4 preflight 在 Linux/Python 3.11/NVIDIA/EGL 全通过且你已批准 GPU 资源时，才运行：

```bash
python3.11 mainline/day06/code/run_smolvla_single_pilot.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --pilot-config mainline/day06/config/pilot_a.json \
  --output-dir learner_outputs/mainline/day06/real_pilot_a
```

runner 先验证锁定源码和 config，再按精确 revision 下载 snapshot，调用真实 [`initialize_model`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L173-L178)、[`_get_vla_arena_env`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L539-L566) 和 [`run_episode`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L222-L334)。[完整 runner](code/run_smolvla_single_pilot.py) 分为 preflight、锁定下载、单 task/init、episode、证据登记五段；失败另写 `infrastructure_error.json`，不写 completed registry。

## 8. 独立挑战

不看答案，使用 [pilot_b.json](config/pilot_b.json) 生成 `learner_outputs/mainline/day06/pilot_b_manifest.json`。先预测哪些字段必须保持，哪些字段应变化；再说明为何同 checkpoint 下换 task、seed、init state 比只换 `form` 更能检验你是否掌握了运行单位。

不给完整命令。参考 A、程序 `--help` 自行迁移。验收器会从 B config 和真实锁定 blob 重建内容，复制 A 后只改 `form` 不能通过。独立挑战只要求静态 manifest，不授权或要求第二次 GPU 运行。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day06.tests.test_day06_tools
.venv-day06/bin/python mainline/day06/code/check_day06.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --config mainline/day06/config/pilot_b.json \
  --manifest learner_outputs/mainline/day06/pilot_b_manifest.json
```

若真实 A pilot 已执行，再追加：

```bash
.venv-day06/bin/python mainline/day06/code/check_day06.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --config mainline/day06/config/pilot_a.json \
  --manifest learner_outputs/mainline/day06/pilot_a_manifest.json \
  --registry learner_outputs/mainline/day06/real_pilot_a/episode_registry.csv
```

口述 10 分：VLM 三类条件 2；chunk/queue/reset 3；双版本锁定 2；有效 episode 与基础设施错误边界 2；A→B 控制变量 1。机器通过且口述 ≥8 可进入 Day 7；5–7 按弱项补 F02/F08/F09。没有 GPU 时只记录“静态部分通过、真实 pilot 待执行”，不得写成功或失败率。

## 10. 证据复盘

- 已在教材作者环境运行：锁定源码 AST/YAML 检查、CPU action queue、A/B 语义验收和语法测试。
- 未运行：checkpoint 下载、CUDA、SmolVLA forward、MuJoCo episode；因此仓库没有任何 SmolVLA 成败结果。
- 可以主张：锁定源码默认 VLM backbone、50 步 chunk/queue 契约、pilot 参数与 checkpoint SHA 已冻结。
- 不能主张：模型能在当前机器加载、单 task 成功、50 步一定全部执行，或该 pilot 可代表 L0/L1/L2 总体表现。

自测题（答案在 `shared/answer_keys/day06.md`）：

1. 为什么 checkpoint repo 名和 VLA-Arena commit 不能互相替代？
2. `chunk_size=50`、`n_action_steps=50` 时，前 51 个 `select_action` 调用如何触发模型推理？
3. 为什么每个 episode 开头必须 `policy.reset()`？
4. 哪些证据把 `status=planned` 的 manifest 升格为真实 pilot？
5. 模型加载失败是否应算一次任务失败？为什么？
