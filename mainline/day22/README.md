# Mainline Day 22：计算任务级成功率与 Wilson 区间

今天把 episode 结果汇总成能进入 baseline 表的统计量：每个任务同时给出 `successes/valid_n`、成功率和 95% Wilson 区间，再分别计算 macro 与 micro 成功率。错误 episode 不会被偷偷当作失败或删掉，而是进入 `missing_n`。

## 1. 真实项目产物

- `learner_outputs/mainline/day22/task_stats_a.csv`：五个任务的计数、点估计与 Wilson 区间；
- `baseline_report_a.json`：macro/micro、总分母和缺失计数；
- B 换输入后的 stats/report 与 `challenge_memo.md`。

## 2. 当前卡点

只写 “success rate = 60%” 有三重歧义：是 3/5 还是 300/500？五个任务是否等权？ERROR 是失败还是缺失？样本小时，普通 Wald 区间 `p ± 1.96√(p(1-p)/n)` 在 0% 或 100% 处还会错误地缩成零宽。

本课固定：`COMPLETED + success∈{0,1}` 才进入有效二项分母；`ERROR` 进入 planned/missing 但不进入 valid；任务级与汇总都保留整数计数。每任务用 Wilson；micro 的总成功/总有效 episode 也用 Wilson。macro 是任务成功率的等权平均，不把它硬塞进一个“总二项试验”做朴素 Wilson。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day22/code/minimal_wilson.py
```

应看到 `count=3/5`、`rate=0.600` 与非零宽区间。若 `sqrt`、乘方或浮点格式化不熟，补 [F01](../../foundation_library/f01_terminal_python/README.md)；若 episode registry 与缺失规则不熟，回看 [Day 16](../day16/README.md)。

## 4. 即时知识

- **二项计数**：每个有效 episode 恰为 success=1 或 failure=0；分子 `x`，分母 `n`。
- **点估计**：`p̂=x/n`，描述观察样本，不等于未知真实成功概率。
- **95% Wilson 区间**：由 score test 反演得到；小样本与边界比例通常比对称 Wald 更合理。
- **micro**：先合并所有有效 episode，再算 `Σx/Σn`；样本多的任务权重更高。
- **macro**：先算各任务 `x_t/n_t`，再做等权平均；每个任务权重相同。
- **missing**：ERROR/未取得结果不是自动失败。必须另报 missing rate，并调查是否与难度相关。
- **置信区间解释**：95% 修饰长期重复抽样方法的覆盖率，不是“真实成功率有 95% 概率落在本次区间”。

## 5. 成熟材料处方

- **中文主材料（8 分钟）**：[Python `math` 官方中文文档](https://docs.python.org/zh-cn/3/library/math.html#math.sqrt)。只读 `sqrt` 与浮点返回值；对应 Wilson margin 的平方根，不需要统计库。
- **统计主材料（15 分钟）**：[NIST e-Handbook 7.2.4.1 “Confidence intervals”](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm)。读 Wilson 方法、公式来源和小样本提醒；注意页面后半还介绍 exact interval，本课实现的是前述 Wilson，不混称 exact。
- **锁定项目材料（10 分钟）**：[SmolVLA evaluator 第 439–470 行（锁定 commit）](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L439-L470)。识别 `task_episodes/task_successes` 与 `total_episodes/total_successes`，分别对应任务级与 pooled/micro 计数；教材脚本额外补上区间和缺失口径。

## 6. 最小实验

[minimal_wilson.py](code/minimal_wilson.py) 是完整 16 行代码：

```python
#!/usr/bin/env python3
"""最小例子：二项成功率的 95% Wilson 区间。"""

from math import sqrt

successes, trials = 3, 5
z = 1.959963984540054
p = successes / trials
denominator = 1 + z * z / trials
center = (p + z * z / (2 * trials)) / denominator
margin = z * sqrt(p * (1 - p) / trials + z * z / (4 * trials**2)) / denominator

print(f"count={successes}/{trials}")
print(f"rate={p:.3f}")
print(f"wilson95=[{center - margin:.3f}, {center + margin:.3f}]")
print("boundary=interval_describes_sampling_uncertainty_not_model_cause")
```

把 `successes` 改成 0 或 5：点估计到边界，但 Wilson 上界或下界仍保留不确定性。不要只抄三位小数；正式表保留六位和原始计数。

## 7. 真实 VLA-Arena 操作

先在 Day 17/18 registry 副本中回填真实 `status/success`，导出本课四列输入；免费练习运行合成 A：

```bash
.venv-day06/bin/python mainline/day22/code/compute_baseline_stats.py \
  --input shared/fixtures/day22_episode_results_a.csv \
  --task-stats learner_outputs/mainline/day22/task_stats_a.csv \
  --report learner_outputs/mainline/day22/baseline_report_a.json
```

应看到 `tasks=5 valid=10/11 micro=0.400000 macro=0.500000`。不同是因为各任务有效分母不等：micro 给 episode 等权，macro 给任务等权。

接真实 registry 时，先验证 episode_id 唯一、每个计划 episode 恰有一个终态；`PLANNED/RUNNING` 说明批次尚未封口，不应提前出 formal 表；`ERROR` 要保留 exception/evidence join，并在报告中显示 missing。若缺失与任务难度相关，complete-case 成功率可能有偏，本课区间不修正这种偏差。

## 8. 独立挑战

用 `day22_episode_results_b.csv` 生成 B stats/report，不给出正文答案。写 ≥170 字 memo，必须原样包含 `Wilson`、`successes`、`valid_n`、`macro`、`micro`、`missing`、`synthetic`。

解释 B 中任务权重如何令 macro/micro 不同、为什么 ERROR 不自动记 0，以及 Wilson 区间能覆盖哪类不确定性、不能修复哪类选择/缺失偏差。不得复制 A 数字或参考答案段落。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day22.tests.test_day22_tools
.venv-day06/bin/python mainline/day22/code/check_day22.py \
  --example-raw shared/fixtures/day22_episode_results_a.csv \
  --example-stats learner_outputs/mainline/day22/task_stats_a.csv \
  --example-report learner_outputs/mainline/day22/baseline_report_a.json \
  --challenge-raw shared/fixtures/day22_episode_results_b.csv \
  --challenge-stats learner_outputs/mainline/day22/task_stats_b.csv \
  --challenge-report learner_outputs/mainline/day22/baseline_report_b.json \
  --challenge-memo learner_outputs/mainline/day22/challenge_memo.md
```

口述 10 分：分子/分母 2；Wilson 解释 2；macro/micro 2；ERROR/missing 2；synthetic/real 与偏差边界 2。机器通过且 ≥8 进入 Day 23；只报百分比、用 Wald 零宽区间、静默删 ERROR 或把 macro 当 pooled binomial 均不通过。

## 10. 证据复盘

- 已运行：A/B 合成 episode 的任务级计数、Wilson、macro/micro 与非法输入测试。
- 未运行：真实 L0/L1/L2 成功统计、真实 missing pattern、GPU。
- 可以主张：统计脚本的口径和计算可由原始 episode 精确重建。
- 不能主张：任何真实模型成功率、总体分布或失败机制。

自测题（答案在 `shared/answer_keys/day22.md`）：

1. 为什么 0/5 的 Wilson 区间不应是 `[0,0]`？
2. macro 与 micro 各给谁等权？
3. ERROR 为什么不自动写 success=0？
4. 95% 置信区间不表示什么？
5. Wilson 能否修复非随机缺失造成的偏差？
