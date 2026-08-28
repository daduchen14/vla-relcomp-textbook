# Mainline Day 18：按任务建立 L0 baseline registry 与视频索引

今天把锁定 suite 的 5 个 L0 task 展开成等分母执行计划，并为每个 task×seed×init 登记唯一 episode 和视频路径。没有合格 GPU 环境时，只生成 PLANNED registry 与“视频尚不存在”的诚实索引；真实 baseline 成功率不能由教材 fixture 代替。

## 1. 真实项目产物

- `learner_outputs/mainline/day18/l0_registry_a.csv`：5 tasks×2 trials 的 L0 计划；
- `l0_video_index_a.csv`、`l0_coverage_a.json`：逐 episode 视频状态与 task 覆盖；
- B 新输入生成 5×3 的 registry/index/report 与 `challenge_memo.md`。

这些资产给 Day 19/20 提供同构口径，也给 Day 22 的任务级分母提供来源。

## 2. 当前卡点

“跑了 10 个 L0 episode”不说明五个 task 是否都覆盖；若某个 task 0 次、另一个 4 次，宏平均不可比较。视频路径也不能只靠目录扫描推断：旧文件、空文件或重名文件都可能串到错误 episode。

本课从 Day 9 锁定 task table 展开每 task 相同 trials，seed/init 写进稳定 ID；视频索引从 registry 出发，而不是从磁盘文件反向猜身份。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day18/code/minimal_task_counts.py
```

应看到 task 0–4 各 `planned=2` 和 PASS。若 Counter/循环卡住补 [F03](../../foundation_library/f03_modules_testing/README.md)；若仍混淆 episode 与 task 回看 [F08](../../foundation_library/f08_episode_evaluator/README.md)。

## 4. 即时知识

- **task denominator**：某 task 纳入统计的有效 episode 数；运行前先保证 planned 分母对称。
- **trial**：同一 task 的一次 seed×init 执行，不等于不同 task。
- **L0**：训练组合层级；此处先验证主模型是否有足够成功样本，不用 L1/L2 选 checkpoint。
- **planned evidence path**：未来写入地址，不代表文件已存在。
- **video index**：episode_id、task、seed/init、状态、path、exists、bytes、sha256 的可连接表。
- **环境异常**：应转 INVALID 并保留异常证据，不能按模型失败写 0。

## 5. 成熟材料处方

- **中文主材料（8 分钟）**：[Python `collections.Counter`](https://docs.python.org/zh-cn/3/library/collections.html#collections.Counter)。只读计数器创建与缺失键返回 0，对应 task 分母检查。
- **锁定源码（15 分钟）**：[SmolVLA evaluator `run_task`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L340-L435)。只读 task 获取、initial state 选择、trial loop 与 `run_episode` 调用，逐项对应 registry 字段。

## 6. 最小实验

[minimal_task_counts.py](code/minimal_task_counts.py) 是完整 14 行代码：

```python
#!/usr/bin/env python3
"""最小例子：先检查每个 task 的计划分母是否相同。"""

from collections import Counter

task_ids = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
counts = Counter(task_ids)
expected = 2

for task_id in range(5):
    print(f"task={task_id} planned={counts[task_id]}")
    assert counts[task_id] == expected

print("PASS: five tasks have equal planned denominators")
```

真实生成器还验证锁定 commit、suite、task 0..4、init 不重复，并重算 ID。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day18/code/build_l0_registry.py \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --spec shared/fixtures/day18_l0_spec_a.json \
  --output learner_outputs/mainline/day18/l0_registry_a.csv
.venv-day06/bin/python mainline/day18/code/build_video_index.py \
  --registry learner_outputs/mainline/day18/l0_registry_a.csv --repo-root . \
  --index learner_outputs/mainline/day18/l0_video_index_a.csv \
  --report learner_outputs/mainline/day18/l0_coverage_a.json
```

应看到 `tasks=5 trials/task=2 episodes=10 status=PLANNED`，随后 `completed=0 planned_missing=10`。这正是当前预期，不要创建空 mp4 让数字变大。长代码 [build_l0_registry.py](code/build_l0_registry.py) 从锁定 task 表生成身份；[build_video_index.py](code/build_video_index.py) 要求 COMPLETED 对应非空 `.mp4`。

真实 Gate 1/2 就绪后，先以 Day 15 formal lock 替换 synthetic model/hash，再让 Day 17 adapter逐行运行。锁定 evaluator 在 task loop 中选择 `initial_state_idx` 并调用 `run_episode`；adapter 必须把真实 success、异常和保存视频路径回写同一 episode，之后重新生成 index。

若覆盖不等，检查是否漏 task/trial；若 PLANNED 已存在视频，先隔离旧 evidence；若 COMPLETED 报视频缺失，不能降级为警告；若模型没跑却出现 success，停止并重建 registry。

## 8. 独立挑战

使用 `day18_l0_spec_b.json` 生成 5×3 的 B registry、index 与 coverage。写 ≥160 字 `challenge_memo.md`，必须出现 `L0`、`task`、`seed`、`init_state`、`PLANNED`、`video`、`denominator`，说明计划与结果、missing video 与失败的区别。

机器会从新 seed base、init 列表、model revision 重算所有 ID，复制 A 改 batch 名无法通过。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day18.tests.test_day18_tools
.venv-day06/bin/python mainline/day18/code/check_day18.py \
  --task-table learner_outputs/mainline/day09/task_structures.json --repo-root . \
  --example-spec shared/fixtures/day18_l0_spec_a.json \
  --example-registry learner_outputs/mainline/day18/l0_registry_a.csv \
  --example-index learner_outputs/mainline/day18/l0_video_index_a.csv \
  --example-report learner_outputs/mainline/day18/l0_coverage_a.json \
  --challenge-spec shared/fixtures/day18_l0_spec_b.json \
  --challenge-registry learner_outputs/mainline/day18/l0_registry_b.csv \
  --challenge-index learner_outputs/mainline/day18/l0_video_index_b.csv \
  --challenge-report learner_outputs/mainline/day18/l0_coverage_b.json \
  --challenge-memo learner_outputs/mainline/day18/challenge_memo.md
```

口述 10 分：五 task 覆盖 2；seed/init 2；planned/result 2；video 身份/hash 2；异常分母 2。机器通过且 ≥8 进入 Day 19；空视频、假 success、漏 task 或 synthetic 冒充 baseline 不通过。

## 10. 证据复盘

- 已运行：A/B L0 计划、等分母、稳定 ID、planned video index、缺视频/重复 init 拒绝测试。
- 未运行：VLA-Arena、模型、GPU、真实视频与 L0 baseline。
- 可以主张：L0 执行矩阵和证据命名已完整计划。
- 不能主张：L0 成功率、模型可诊断性、视频存在或任何 episode 已完成。

自测题（答案在 `shared/answer_keys/day18.md`）：

1. 为什么五个 task 必须分别检查 denominator？
2. seed 与 init_state_index 各控制什么？
3. PLANNED video path 是否是 evidence？
4. COMPLETED/INVALID 对视频和 success 的要求有何不同？
5. 当前 Day 18 资产能支持哪些主张？
