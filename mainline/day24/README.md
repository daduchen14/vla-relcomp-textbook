# Mainline Day 24：公平比较候选模型并冻结主模型

今天只用同口径 L0 结果选择后续主诊断模型。你会先验证每个候选覆盖相同 task、共享 protocol lock、达到最低 `valid_n`，再按预注册的 `macro → worst task → micro → model_id` 排序。L1/L2 继续 held-out，绝不因其结果改变选择。

## 1. 真实项目产物

- `learner_outputs/mainline/day24/model_comparison_a.csv`：候选 eligibility、样本量与三层指标；
- `model_decision_a.json`：选中模型、revision、policy hash 和 held-out 规则；
- B 换候选后的 comparison/decision 与 `challenge_memo.md`。

## 2. 当前卡点

直接选总成功数最高的模型可能不公平：某模型跑了更多 episode、漏了困难任务，或用了不同 init/protocol。看完结果才决定“这次按 macro、下次按 worst task”也会引入研究者自由度。若偷看 L1/L2 决定主模型，held-out 就变成调参集。

因此选择前冻结资格与排序：只收 L0；五个任务齐全；同一 protocol lock；每任务至少达到预注册样本量；eligible 候选的 `valid_n` 向量完全一致。macro 优先保证任务等权，worst task 作第一 tie-break，micro 再打破剩余平局，最终模型名只用于确定性排序。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day24/code/minimal_rank_models.py
```

应看到 beta 排第一：alpha 的 macro 相同，但 worst 较低；gamma 的 micro 最高也不能越过主指标。若 `sorted(key=...)` 不熟，补 [F02](../../foundation_library/f02_csv_json/README.md)；macro/micro 回看 [Day 22](../day22/README.md)。

## 4. 即时知识

- **candidate**：固定 model ID + immutable revision 的候选；不同 checkpoint 不得合并。
- **eligibility**：进入排序前必须满足的 task coverage、样本量、level 与协议条件。
- **balanced comparison**：相同任务格子中，各候选有效重复数一致；任务/seed/init 是 block，模型是比较因素。
- **primary metric**：预先指定的首要排序量；本课为 L0 macro success rate。
- **worst task**：每任务成功率的最小值，防止平均值掩盖完全失效任务。
- **tie-break**：只在上一级完全相同时启用，顺序必须预注册。
- **freeze**：记录选中 model/revision/policy hash；此后不能因 held-out 表现回换。
- **held-out**：L1/L2 只报告泛化，不参与选择、threshold、prompt 或 taxonomy 调整。

## 5. 成熟材料处方

- **中文主材料（8 分钟）**：[Python 排序指南：键函数与多级排序](https://docs.python.org/zh-cn/3/howto/sorting.html)。只读 `key`、升降序和稳定性；对应确定性 tie-break，不代表排序规则可以事后修改。
- **实验设计材料（12 分钟）**：[NIST e-Handbook 5.3.3.2 “Randomized block designs”](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm)。重点读 blocking：在同一 task/seed/init block 内比较模型，控制已知 nuisance factors。本课不是做显著性检验，只借用公平配对原则。
- **锁定项目材料（10 分钟）**：[SmolVLA evaluator 配置第 71–119 行（锁定 commit）](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L71-L119)。逐项确认 policy path、task level、trials、init selection 与 seed 都会改变比较口径；候选间除模型身份外必须冻结。

## 6. 最小实验

[minimal_rank_models.py](code/minimal_rank_models.py) 是完整 19 行代码：

```python
#!/usr/bin/env python3
"""最小例子：按预注册的多级键排序，而非看完结果改规则。"""

models = [
    {"model": "alpha", "macro": 0.60, "worst": 0.25, "micro": 0.60},
    {"model": "beta", "macro": 0.60, "worst": 0.50, "micro": 0.58},
    {"model": "gamma", "macro": 0.55, "worst": 0.55, "micro": 0.62},
]

ranked = sorted(
    models,
    key=lambda row: (-row["macro"], -row["worst"], -row["micro"], row["model"]),
)

for rank, row in enumerate(ranked, start=1):
    print(rank, row["model"], row["macro"], row["worst"], row["micro"])

print("rule=macro_then_worst_then_micro_then_model_id")
print("boundary=L0_only_never_L1_or_L2")
```

试着把 gamma 的 micro 改成 1.0，它仍不会越过更高 macro。若你认为应优先 worst 或成本，应在正式运行前改 policy 并重新锁定，而不是看完表再改。

## 7. 真实 VLA-Arena 操作

免费合成 A：

```bash
.venv-day06/bin/python mainline/day24/code/select_primary_model.py \
  --stats shared/fixtures/day24_candidate_stats_a.csv \
  --policy shared/fixtures/day24_selection_policy_a.json \
  --comparison learner_outputs/mainline/day24/model_comparison_a.csv \
  --decision learner_outputs/mainline/day24/model_decision_a.json
```

应看到 `eligible=2 selected=synthetic/model-beta scope=L0_only`。这是教学 fixture，不是 SmolVLA/OpenVLA 的实际优劣。

真实操作先用 Day 8 的候选集合和 Day 15 lock 生成相同 L0 manifest；候选必须跑相同 task×seed×init block。用 Day 22 输出构造 candidate stats，ERROR 补跑或使候选不 eligible，不能让某模型靠更小分母进入比较。正式最低样本量必须在 GPU 运行前写入 protocol；fixture 的 4 只是免费验收数字。

选中后把真实 model ID、immutable revision、policy SHA 和选择时间写入正式 decision，再冻结 Day 17 adapter。L1/L2 只在 freeze 后运行并原样报告；若 held-out 很差，结论是泛化差，不是回头挑另一个模型。除非启动新的、明确标记的研究周期，否则不能改选择。

## 8. 独立挑战

用 `day24_candidate_stats_b.csv` 与 B policy 生成 comparison/decision，不给出正文选择。写 ≥200 字 memo，必须原样包含 `L0`、`eligible`、`valid_n`、`macro`、`worst_task`、`tie-break`、`L1`、`L2`、`held-out`、`synthetic`、`freeze`。

说明为何 delta 被排除、eligible 候选是否公平、排序各层何时生效，以及选定后为什么不能用 L1/L2 回换。不得复制 A 模型名或参考答案段落。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day24.tests.test_day24_tools
.venv-day06/bin/python mainline/day24/code/check_day24.py \
  --example-stats shared/fixtures/day24_candidate_stats_a.csv --example-policy shared/fixtures/day24_selection_policy_a.json \
  --example-comparison learner_outputs/mainline/day24/model_comparison_a.csv --example-decision learner_outputs/mainline/day24/model_decision_a.json \
  --challenge-stats shared/fixtures/day24_candidate_stats_b.csv --challenge-policy shared/fixtures/day24_selection_policy_b.json \
  --challenge-comparison learner_outputs/mainline/day24/model_comparison_b.csv --challenge-decision learner_outputs/mainline/day24/model_decision_b.json \
  --challenge-memo learner_outputs/mainline/day24/challenge_memo.md
```

口述 10 分：L0/fair blocks 2；eligibility/valid_n 2；macro/worst/micro 2；tie-break/freeze 2；L1/L2 held-out 与 synthetic 边界 2。机器通过且 ≥8 进入 Day 25；分母不等、偷看 held-out、事后换指标或把 fixture 当真实选择均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic 候选资格、公平分母、预注册排序、L1 拒绝与 policy 防预填测试。
- 未运行：真实候选 GPU L0 比较、真实主模型 freeze、L1/L2。
- 可以主张：选择器能按冻结 policy 精确重建 eligibility 与 decision。
- 不能主张：beta/任何真实 VLA 模型更好，或真实 L0 样本已充分。

自测题（答案在 `shared/answer_keys/day24.md`）：

1. 为何 eligible 候选必须共享 valid_n 向量？
2. primary metric 与 tie-break 有何区别？
3. 为什么用 macro 作主指标？
4. L1/L2 表现能否用于回换模型？
5. freeze record 至少应保存什么？
