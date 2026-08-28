# Mainline Day 47：配对评测 L0 保持与 catastrophic damage

今天建立 L0 retention 的统计与证据格式：同一 episode/initial state 配对 baseline 和 repair，既报告总体 success-rate delta，也专门统计 baseline 原本成功却被修坏的 catastrophic regressions。本地只运行 synthetic fixture；checkpoint 1–3 和 VLA-Arena 均未运行。

## 1. 真实项目产物

- `l0_pairs_a.csv`：逐 episode baseline/repair success 与 transition；
- `l0_retention_a.json`：成功率差、保持率、regression/recovery ID 和阈值结论；
- B 新 episodes/config 的同类证据与 `challenge_memo.md`。

## 2. 当前卡点

repair 总成功率不下降，并不保证没有损坏旧能力：一个旧成功变失败，可能刚好被另一个旧失败变成功抵消。只比较两批不同 episodes 更危险，因为 initial-state 难度也变了。

本课冻结配对 episode ID。retention 的分母只取 baseline successes；每个 `success→failure` 都进入 regression 清单。总体 delta 和 recovery 另列，不能互相替代。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day47/code/minimal_retention.py
```

应看到 retention 0.667、delta 0 和 regression `ep2`。若布尔统计不熟补 [F02](../../foundation_library/f02_csv_json/README.md)；多 seed 边界回看 [Day 46](../day46/README.md)。

## 4. 即时知识

- **L0 retention**：修复后保留原始分布能力的程度。
- **paired episode**：两模型使用相同 task、episode 与 initial state。
- **retention rate**：`baseline成功且repair成功 / baseline成功`。
- **success-rate delta**：repair 总成功率减 baseline 总成功率。
- **catastrophic regression**：`success→failure`，即修坏已会的 episode。
- **recovery**：`failure→success`；不能抵消 regression 的逐例审查责任。
- **minimum threshold**：看结果前冻结的最低保持率。
- **aggregate + cases**：既报告总体数，也保留所有 paired transitions。

## 5. 成熟材料处方

- **中文主材料（Google ML，8 分钟）**：[分类指标](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall?hl=zh-cn)。只复习混淆类型和“单一总指标会隐藏错误类型”的思想；本课 transition 不是分类器标签。
- **补充材料（statsmodels 官方，8 分钟）**：[McNemar paired test](https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html)。只理解配对二元结果关注不一致对；小 fixture 不做显著性推断。
- **锁定项目定位（10 分钟）**：[SmolVLA evaluator 第 310–334 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L310-L334) 用 done/info/cost 判定单 episode success；[第 381–425 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L381-L425) 按 seed/episode index 选初始状态并运行 episode，是配对时必须锁定的入口。

## 6. 最小实验

[minimal_retention.py](code/minimal_retention.py) 是完整 20 行代码：

```python
#!/usr/bin/env python3
"""最小例子：配对统计原本成功是否被修复模型保留。"""

pairs = [
    ("ep1", True, True),
    ("ep2", True, False),
    ("ep3", False, True),
    ("ep4", True, True),
]

baseline_successes = [row for row in pairs if row[1]]
retained = [row for row in baseline_successes if row[2]]
regressions = [row[0] for row in baseline_successes if not row[2]]
retention = len(retained) / len(baseline_successes)
baseline_rate = sum(row[1] for row in pairs) / len(pairs)
repair_rate = sum(row[2] for row in pairs) / len(pairs)

print(f"retention_rate={retention:.3f}")
print(f"success_delta={repair_rate - baseline_rate:+.3f}")
print(f"catastrophic_regressions={regressions}")
```

长文件 [analyze_l0_retention.py](code/analyze_l0_retention.py) 负责唯一 ID、四类 transition、两种聚合和 evidence boundary。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day47/code/analyze_l0_retention.py \
  --input shared/fixtures/day47_l0_retention_a.json --config mainline/day47/config/retention_config_a.json \
  --paired-table learner_outputs/mainline/day47/l0_pairs_a.csv \
  --report learner_outputs/mainline/day47/l0_retention_a.json
```

A synthetic 结果应为 retention 1.0、delta +0.125、无 regression。真实操作须等 checkpoint 1–3 存在后，以同 evaluator commit、suite、L0、seed、episode index、initial state 和 max steps 分别运行 baseline/repair；逐 episode join 后再运行同一分析。不得先看 test 再调 threshold。当前没有真实模型结果。

## 8. 独立挑战

用 B input/config 生成新 table/report。写 ≥260 字 memo，必须原样包含 `L0 retention`、`paired episode`、`baseline success`、`repair success`、`retention rate`、`success-rate delta`、`catastrophic regression`、`recovery`、`minimum threshold`、`same initial state`、`synthetic fixture`、`checkpoint`、`VLA-Arena`、`cannot claim`。解释为何 B 总 delta 为零仍需记录 damage；正文不给具体 episode ID。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day47.tests.test_day47_tools
.venv-day06/bin/python mainline/day47/code/check_day47.py \
  --example-input shared/fixtures/day47_l0_retention_a.json --example-config mainline/day47/config/retention_config_a.json --example-table learner_outputs/mainline/day47/l0_pairs_a.csv --example-report learner_outputs/mainline/day47/l0_retention_a.json \
  --challenge-input shared/fixtures/day47_l0_retention_b.json --challenge-config mainline/day47/config/retention_config_b.json --challenge-table learner_outputs/mainline/day47/l0_pairs_b.csv --challenge-report learner_outputs/mainline/day47/l0_retention_b.json \
  --challenge-memo learner_outputs/mainline/day47/challenge_memo.md
```

口述 10 分：配对 2；retention 2；delta 2；regression/recovery 2；synthetic/真实边界 2。机器通过且 ≥8 进入 Day 48；未配对、只报总成功率、隐藏 regression、事后改阈值或冒充真实 eval 均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic paired table、retention/delta、regression/recovery 与阈值检查。
- 静态源码事实：锁定 evaluator 的 success 判定和 initial-state/episode 循环。
- 未运行：baseline/repair checkpoints、VLA-Arena、MuJoCo/GPU 和真实 L0。
- 可以主张：统计脚本能揭示总体 delta 掩盖的逐 episode damage。
- 不能主张：repair 保留真实 L0、checkpoint 可评测或 catastrophic damage 已排除。

自测题（答案在 `shared/answer_keys/day47.md`）：

1. retention rate 的分子和分母是什么？
2. 为什么还要报告总体 success-rate delta？
3. catastrophic regression 如何定义，为什么必须列 ID？
4. baseline/repair 为什么必须使用 same initial state？
5. synthetic fixture 通过能否说明真实 L0 保持？
