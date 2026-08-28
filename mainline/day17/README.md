# Mainline Day 17：构建可恢复、可重试且幂等的批量 runner

今天让 Day 16 registry 真正具有“跑到一半还能继续”的执行语义。你会模拟中断、可重试错误、无效环境与真实失败，得到 checkpoint、更新后的 episode registry 和逐 episode 证据 hash。免费脚本化 executor 不加载 VLA 模型，只验证批处理骨架。

## 1. 真实项目产物

- `learner_outputs/mainline/day17/episodes_a.csv`：续跑后的终态 registry；
- `learner_outputs/mainline/day17/checkpoint_a.json`：attempt/status/error/result hash；
- `learner_outputs/mainline/day17/evidence_a/`：按 run/episode 隔离的 result/exception；
- B 输入对应的独立终态资产与 `challenge_memo.md`。

这个 runner 是 Day 18–20 分 level 运行的控制层；真实 executor 只替换单 episode 调用，不改变 registry/checkpoint 约定。

## 2. 当前卡点

长批次会因进程退出、显存错误或环境异常中断。如果重启后从第 0 条再跑，会覆盖证据、重复计数并浪费 GPU；如果任何异常都无限 retry，会把确定性输入错误伪装成暂时故障。

本课把 episode 状态分成非终态 `PLANNED/RUNNING` 与终态 `COMPLETED/INVALID/FAILED`。终态永远跳过；retry 有上限；每个 work item 后原子写 checkpoint 与 registry。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day17/code/minimal_idempotence.py
```

应看到已有 `ep-a` 被 SKIP、`ep-b/ep-c` 各 RUN 一次，重复的 `ep-a` 不再执行。若集合/循环卡住补 [F03](../../foundation_library/f03_modules_testing/README.md)，若进程与退出状态卡住补 [F05](../../foundation_library/f05_linux_processes/README.md)。

## 4. 即时知识

- **checkpoint**：最近一次可靠进度；不是日志摘要，而是续跑决策输入。
- **retry**：只重试暂时性错误，并记录 attempts/max_attempts。
- **INVALID**：环境、任务或输入无效，不计模型失败；**FAILED**：达到重试上限仍无法完成。
- **idempotent**：终态 episode 再提交不会重复执行或改变证据。
- **atomic replace**：先写同目录临时文件，再一次替换目标，避免半写文件被当完整 checkpoint。
- **result hash**：checkpoint 保存 result bytes 的 sha256，防止 registry 指向被替换的证据。

## 5. 成熟材料处方

- **中文主材料（10 分钟）**：[Python `os.replace`](https://docs.python.org/zh-cn/3/library/os.html#os.replace)。只读替换目标的语义；理解本课为什么不用直接覆盖 checkpoint。
- **工程补充（英文官方，15 分钟）**：[AWS Builders' Library：Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。只读 retry 与 idempotency token 的关系；把本课 episode_id 类比为稳定请求身份。

## 6. 最小实验

[minimal_idempotence.py](code/minimal_idempotence.py) 是完整 16 行代码：

```python
#!/usr/bin/env python3
"""最小例子：终态 ID 再出现时跳过，而不是重复执行。"""

planned = ["ep-a", "ep-b", "ep-a", "ep-c"]
terminal = {"ep-a"}
executed = []

for episode_id in planned:
    if episode_id in terminal:
        print(f"SKIP {episode_id}")
        continue
    executed.append(episode_id)
    terminal.add(episode_id)
    print(f"RUN  {episode_id}")

print(f"executed={executed}")
```

真实代码还必须持久化 terminal 集合；否则重启后内存丢失，幂等性也随之丢失。

## 7. 真实 VLA-Arena 操作

先使用 Day 16 A registry 模拟“处理两次后中断”，再 resume：

```bash
.venv-day06/bin/python mainline/day17/code/resumable_runner.py \
  --input-registry learner_outputs/mainline/day16/episodes_a.csv \
  --output-registry learner_outputs/mainline/day17/episodes_a.csv \
  --checkpoint learner_outputs/mainline/day17/checkpoint_a.json \
  --executor shared/fixtures/day17_executor_a.json \
  --artifact-root learner_outputs/mainline/day17/evidence_a \
  --max-work-items 2
.venv-day06/bin/python mainline/day17/code/resumable_runner.py \
  --input-registry learner_outputs/mainline/day16/episodes_a.csv \
  --output-registry learner_outputs/mainline/day17/episodes_a.csv \
  --checkpoint learner_outputs/mainline/day17/checkpoint_a.json \
  --executor shared/fixtures/day17_executor_a.json \
  --artifact-root learner_outputs/mainline/day17/evidence_a
```

第一次应处理 2 个 work items；第二次终结两个 COMPLETED 与一个 INVALID。再运行一次应 `processed_this_call=0`。长脚本 [resumable_runner.py](code/resumable_runner.py) 按 `atomic_text/read/write → checkpoint → run_batch` 阅读。

真实 VLA-Arena 适配点是锁定 SmolVLA [`run_task` 的 episode loop](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L350-L435)：它选择 initial state 后调用 `run_episode`；外层 [`main` task loop](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L634-L700) 遍历 task。未来 adapter 必须按 registry 指定单个 task/init，并把真实 success/video/events 返回 runner；当前没有运行这些路径。

若 resume 重做终态，先检查 episode_id/checkpoint 是否共用；若 hash 不一致停止覆盖并保留两份证据；若持续 retry，检查 max_attempts 与错误分类；INVALID 不得自动改 FAILED。

## 8. 独立挑战

使用 Day 16 B registry 与 `day17_executor_b.json`。先限制一个 work item 模拟中断，再自行决定需要几次 resume，直到再次调用显示零工作。生成 B registry/checkpoint/evidence。

写 ≥160 字 `challenge_memo.md`，必须出现 `retry`、`checkpoint`、`idempotent`、`atomic`、`INVALID`、`FAILED`，解释 B 的 attempts、终态区别和证据 hash。正文不提供 B 每个 task 的最终 attempts。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day17.tests.test_day17_tools
.venv-day06/bin/python mainline/day17/code/check_day17.py \
  --example-input learner_outputs/mainline/day16/episodes_a.csv \
  --example-registry learner_outputs/mainline/day17/episodes_a.csv \
  --example-checkpoint learner_outputs/mainline/day17/checkpoint_a.json \
  --example-executor shared/fixtures/day17_executor_a.json \
  --example-artifact-root learner_outputs/mainline/day17/evidence_a \
  --challenge-input learner_outputs/mainline/day16/episodes_b.csv \
  --challenge-registry learner_outputs/mainline/day17/episodes_b.csv \
  --challenge-checkpoint learner_outputs/mainline/day17/checkpoint_b.json \
  --challenge-executor shared/fixtures/day17_executor_b.json \
  --challenge-artifact-root learner_outputs/mainline/day17/evidence_b \
  --challenge-memo learner_outputs/mainline/day17/challenge_memo.md
```

口述 10 分：状态机 2；retry 上限/分类 2；checkpoint 2；atomic/idempotent 2；证据 hash 2。机器通过且 ≥8 进入 Day 18；无限重试、覆盖不一致结果、异常补失败或 fixture 冒充模型均不通过。

## 10. 证据复盘

- 已运行：脚本化中断/续跑、一次 retry、上限、未知 checkpoint、证据 hash 与零工作幂等测试。
- 未运行：VLA-Arena、GPU、checkpoint 模型或真实 episode。
- 可以主张：批处理控制层能安全恢复合成 work items，并区分终态。
- 不能主张：模型失败可重试、真实 evaluator 已适配，或 fixture success 是基线结果。

自测题（答案在 `shared/answer_keys/day17.md`）：

1. checkpoint 至少要保存哪些字段？
2. RETRYABLE、INVALID、FAILED 如何区分？
3. 什么叫终态续跑 idempotent？
4. atomic replace 解决什么、又不解决什么？
5. result hash 为什么要进入 checkpoint？
