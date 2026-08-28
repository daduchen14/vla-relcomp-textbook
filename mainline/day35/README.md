# Mainline Day 35 / Gate 5：汇总四段转化、pair 与 oracle 证据

今天把阶段 4 的证据压成一张 diagnosis table：baseline 四段漏斗、relation pair asymmetry、language oracle 与 visual oracle 的 recovery/damage。Gate 5 要求先预测，再对新 B 卷选择候选瓶颈或 `INSUFFICIENT_EVIDENCE`；规则允许不进入修复，不为讲故事牺牲证据边界。

## 1. 真实项目产物

- `diagnosis_table_a.csv`、`diagnosis_report_a.json`：A 的漏斗、pair 和 oracle 汇总；
- B 新证据的同类产物；
- `gate5_submission.json` 与 `gate5_oral.md`：事前预测、有限结论、替代解释和 falsifier。

## 2. 当前卡点

总体 success 低不能区分抓取前、搬运中还是终态失败；最大漏斗下降也不能自动指出内部原因。pair asymmetry 可能来自匹配不严，oracle recovery 可能伴随 damage。把三张表各挑一个好看的数字，会得到互相冲突的故事。

本课先冻结统一分母：每段转化以前一阶段为分母；pair 只纳入完整两臂；oracle 同时报 recovery、damage 与净差。预登记的描述性规则只有在 pair/失败分母足够且两 oracle 净差达到阈值时才给“候选”；否则必须写证据不足。即便给候选，synthetic rehearsal 也不产生研究结论。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day35/code/minimal_funnel.py
```

应看到 `lift->approach: 3/6=0.500`，不是 `3/10`。若计数/分母卡住补 [F02](../../foundation_library/f02_csv_json/README.md)；pair 与两类 oracle 分别回看 [Day 31](../day31/README.md)、[Day 33](../day33/README.md)、[Day 34](../day34/README.md)。

## 4. 即时知识

- **conversion funnel**：episodes→contact→lift→approach→relation 的条件转化链。
- **largest conversion drop**：`1-rate` 最大的一段；是行为断点，不是机制诊断。
- **pair asymmetry**：完整 relation pair 中 success 只在一臂成立的比例。
- **oracle net effect**：本课描述量为 recovery rate − damage rate；不能取代原始计数。
- **candidate**：达到预登记证据规则的优先后续假设，仍不是 causal 定论。
- **insufficient evidence**：证据分母、差异或一致性不足；是合法结果。
- **falsifier**：若出现将削弱当前解释的新结果，必须在下一实验前写清。

## 5. 成熟材料处方

- **中文主材料（8 分钟）**：[Python `collections.Counter` 官方中文文档](https://docs.python.org/zh-cn/3/library/collections.html#collections.Counter)。理解四格原始计数为何先于比例。
- **配对补充（英文官方，8 分钟）**：[statsmodels McNemar 文档](https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html)。只认出配对 2×2 表与 exact 选项；本日小样本只准备计数，不安装包、不报告 p 值。
- **锁定项目定位（8 分钟）**：[SmolVLA evaluator 第 279–334 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L279-L334) 展示 observation→action→`env.step`→success 的实际循环；真实 diagnosis 的分母必须来自保留完整状态的 episode registry，而不是视频印象。

## 6. 最小实验

[minimal_funnel.py](code/minimal_funnel.py) 是完整 19 行代码：

```python
#!/usr/bin/env python3
"""最小例子：阶段转化率以前一阶段为分母。"""

counts = {
    "episodes": 10,
    "contact": 8,
    "lift": 6,
    "approach": 3,
    "relation": 2,
}
transitions = (
    ("episodes", "contact"),
    ("contact", "lift"),
    ("lift", "approach"),
    ("approach", "relation"),
)
for before, after in transitions:
    rate = counts[after] / counts[before] if counts[before] else None
    print(f"{before}->{after}: {counts[after]}/{counts[before]}={rate:.3f}")
```

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day35/code/build_diagnosis_table.py \
  --input shared/fixtures/day35_diagnosis_evidence_a.csv \
  --table learner_outputs/mainline/day35/diagnosis_table_a.csv \
  --report learner_outputs/mainline/day35/diagnosis_report_a.json
```

A 应得到 `LANGUAGE_RELATION_CANDIDATE` 与 `synthetic=true`。这只是让候选分支可练习，不是项目诊断。

真实运行时，从同一个 formal registry join Day 27–30 事件、Day 31 完整 relation pairs、Day 33/34 匹配 oracle；保留 invalid/interrupted 分母表。先冻结规则再读取结果，输出 task/level/seed 分层与原始四格。若任一来源版本、pair 完整性或 probe 视频抽查不合格，结论降为证据不足；不得为了 Day 36 强选 repair。当前未运行真实模型、MuJoCo 或 GPU。

## 8. 独立挑战

1. **运行前**复制 [Gate 5 模板](config/gate5_submission_template.json)，先填 `prediction_before_analysis` 和时间顺序。
2. 用 B input 生成新 table/report，再完成结论、四项 evidence metric、两个 alternative 和一个 falsifier。
3. 写 ≥260 字 oral note，必须原样包含 `conversion funnel`、`pair asymmetry`、`language oracle`、`visual oracle`、`recovery`、`damage`、`alternative`、`falsifier`、`insufficient evidence`、`synthetic`、`causal`。

正文不给 B label；答案在 `shared/answer_keys/day35_gate5_solution.json` 与 `day35_gate5_oral.md`，提交后再看。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day35.tests.test_day35_tools
.venv-day06/bin/python mainline/day35/code/check_day35.py \
  --example-input shared/fixtures/day35_diagnosis_evidence_a.csv --example-table learner_outputs/mainline/day35/diagnosis_table_a.csv --example-report learner_outputs/mainline/day35/diagnosis_report_a.json \
  --challenge-input shared/fixtures/day35_diagnosis_evidence_b.csv --challenge-table learner_outputs/mainline/day35/diagnosis_table_b.csv --challenge-report learner_outputs/mainline/day35/diagnosis_report_b.json \
  --gate-submission learner_outputs/mainline/day35/gate5_submission.json --oral-note learner_outputs/mainline/day35/gate5_oral.md
```

Gate 5 口述 10 分：funnel 分母 2；pair 完整性/asymmetry 2；两 oracle recovery/damage 2；alternative/falsifier 2；证据不足/causal 边界 2。机器通过且 ≥8 才算学习者通过；教材已编写不等于 Gate 已通过。事后伪造预测、缺臂入分母、只报净效应、强选 repair 或把 synthetic 模式当研究结论均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic evidence 的漏斗、pair/oracle 四格、预登记 pattern rule 与 Gate 结构验收。
- 静态源码事实：锁定 evaluator 的真实 action/step/success 数据流。
- 未运行：formal registry join、真实 pair/oracle、McNemar、模型/GPU 与学习者 Gate。
- 可以主张：diagnosis table 和“候选/证据不足”规则在新输入上可重建。
- 不能主张：语言或视觉是真实瓶颈、Gate 已通过，或应启动某项修复。

自测题（答案在 `shared/answer_keys/day35.md`）：

1. conversion rate 为什么不总以 episode 总数为分母？
2. 哪些 pair 可进入 asymmetry 分母？
3. oracle net effect 如何计算，为什么还要展示原始计数？
4. 最大漏斗下降与 oracle 恢复能否直接形成 causal 结论？
5. 哪些情况下必须选择 insufficient evidence？
