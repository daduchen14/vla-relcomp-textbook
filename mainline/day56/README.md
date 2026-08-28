# Mainline Day 56：冻结四段事件漏斗与 conversion rate

今天把任务拆成 `target_contacted → target_lifted → reference_approached → relation_satisfied` 四段。每个 condition 同时报全体 episode 的 reach rate、以上一阶段为分母的 adjacent conversion、drop-off 和 repair−baseline stage delta。后段为真而前段为假会 fail closed。

## 1. 真实项目产物

- `stage_funnel_a.json`：baseline/repair 四段 counts、reach、conversion、drop-off 与 delta；
- monotonicity 与唯一 episode key 证据；
- B 新 events/config 的报告与 `challenge_memo.md`。

## 2. 当前卡点

最终 success 下降只告诉“没完成”，不能区分没接触、没举起、没靠近还是没满足关系。若 conversion 仍除以全部 episodes，它会与 reach rate 混淆；若事件顺序自相矛盾，后续机制解释无效。

本课明确两个分母，并要求四段单调。baseline/repair 各自保持固定 episode count；missing/duplicate 在进入统计前被拒绝。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day56/code/minimal_funnel.py
```

应看到四个 reach、三个 conversion 和 `previous_stage_reached`。若比例不熟回看 [Day 28](../day28/README.md)；事件定义回看 [Day 10](../day10/README.md)。

## 4. 即时知识

- **four-stage funnel**：按必要先后顺序排列的行为事件链。
- **reach rate**：到达某阶段 / 全部注册 episodes。
- **conversion rate**：到达当前阶段 / 到达上一阶段。
- **previous-stage denominator**：条件概率的显式分母。
- **drop-off**：上一阶段到达数−当前阶段到达数。
- **monotonicity**：后段真要求所有前段真。
- **stage delta**：repair reach−baseline reach，同阶段比较。
- **bottleneck candidate**：最大 drop-off/delta 只是候选解释，不是因果证明。

## 5. 成熟材料处方

- **中文主材料（Google Analytics，8 分钟）**：[漏斗探索](https://support.google.com/analytics/answer/9327974?hl=zh-Hans)。只理解开放/封闭漏斗与阶段流失；本课使用严格封闭、单调漏斗。
- **补充材料（Python 官方，6 分钟）**：[statistics](https://docs.python.org/zh-cn/3/library/statistics.html)。只复习比例汇总前必须保留原始 counts；本日不做推断统计。
- **锁定项目定位（10 分钟）**：[evaluator 第 262–328 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L262-L328) 是 action→step→done/success loop；四段事件需要从同一 episode trace/环境状态派生，不能仅从最终 `success` 猜测。[第 439–454 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L439-L454) 累计 episode/success 分母。

## 6. 最小实验

[minimal_funnel.py](code/minimal_funnel.py) 是完整 22 行代码：

```python
#!/usr/bin/env python3
"""最小例子：同时计算阶段到达率与相邻转化率。"""

episodes = [
    [1, 1, 1, 1],
    [1, 1, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
]
stages = ["contact", "lift", "approach", "satisfied"]

reached = [sum(row[index] for row in episodes)
           for index in range(len(stages))]
reach_rates = [count / len(episodes) for count in reached]
conversions = [
    reached[index] / reached[index - 1]
    for index in range(1, len(stages))
]

print(dict(zip(stages, reach_rates)))
print(dict(zip(stages[1:], conversions)))
print("denominator=previous_stage_reached")
```

长文件 [analyze_stage_funnel.py](code/analyze_stage_funnel.py) 依次检查 condition 分母、episode keys、单调性，再生成 reach/conversion/delta。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day56/code/analyze_stage_funnel.py \
  --input shared/fixtures/day56_stages_a.json --config mainline/day56/config/stage_funnel_a.json \
  --report learner_outputs/mainline/day56/stage_funnel_a.json
```

A synthetic final-stage delta 约 +0.333。未来真实操作需由同一锁定 evaluator 的 episode trace 生成四个布尔事件和 evidence timestamps，baseline/repair 使用相同 registry；异常/缺失保留并 fail closed。还要抽查视频确认事件语义，不能只信自动 detector。当前未运行。

## 8. 独立挑战

用 B events/config 生成新 report。写 ≥270 字 memo，必须原样包含 `four-stage funnel`、`target contacted`、`target lifted`、`reference approached`、`relation satisfied`、`reach rate`、`conversion rate`、`previous-stage denominator`、`drop-off`、`monotonicity`、`baseline`、`repair`、`stage delta`、`synthetic events`、`cannot claim`。正文不给 B 数值。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day56.tests.test_day56_tools
.venv-day06/bin/python mainline/day56/code/check_day56.py \
  --example-input shared/fixtures/day56_stages_a.json --example-config mainline/day56/config/stage_funnel_a.json --example-report learner_outputs/mainline/day56/stage_funnel_a.json \
  --challenge-input shared/fixtures/day56_stages_b.json --challenge-config mainline/day56/config/stage_funnel_b.json --challenge-report learner_outputs/mainline/day56/stage_funnel_b.json \
  --challenge-memo learner_outputs/mainline/day56/challenge_memo.md
```

口述 10 分：四段定义 2；reach 分母 2；conversion/drop-off 2；monotonicity 2；synthetic 边界 2。机器通过且 ≥8 进入 Day 57；错分母、非单调、条件分母不同、只报 rate 不报 count 或冒充 final metrics 均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic 四段 counts、reach、adjacent conversion、drop-off 与 deltas。
- 静态源码事实：锁定 evaluator 的 episode loop 与 total episode/success 累计。
- 未运行：真实 event detectors、videos、VLA-Arena/MuJoCo/GPU。
- 可以主张：脚本区分总体 reach 与条件 conversion，并拒绝非单调 traces。
- 不能主张：真实 repair 在最后阶段改善、最大 drop-off 是因果瓶颈。

自测题（答案在 `shared/answer_keys/day56.md`）：

1. stage reach rate 的分母是什么？
2. adjacent conversion rate 的分母是什么？
3. 为什么必须检查阶段 monotonicity？
4. drop-off count 如何计算？
5. synthetic funnel 能否定位真实模型瓶颈？
