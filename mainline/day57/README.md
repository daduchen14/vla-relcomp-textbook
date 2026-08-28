# Mainline Day 57：Wilson 区间、恢复/损伤率与 exact McNemar

今天从 baseline→repair 的配对四格 `n00/n01/n10/n11` 同时计算成功率 Wilson 区间、paired delta、recovery/damage Wilson 区间和 two-sided exact McNemar。报告强制分开 effect size、confidence interval 与 hypothesis test，禁止把“不显著”写成“没有效果”。

## 1. 真实项目产物

- `paired_statistics_a.json`：四格定义/counts、五组效应/区间与 exact test；
- p 值解释边界和 synthetic evidence 标记；
- B 新 counts/config 的报告与 `challenge_memo.md`。

## 2. 当前卡点

裸成功率没有不确定性；baseline/repair 独立区间又忽略同 episode 配对。recovery 与 damage 若都除以总数，会回答错误问题；McNemar p 值若被当作 effect size，也会造成“显著=大”“不显著=零”的错误。

本课先固定 transition 方向：`n01` 是恢复，`n10` 是损伤。Wilson 描述单个比例的不确定性；McNemar 只看 discordant pairs 的方向不对称；paired delta 单独报告。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day57/code/minimal_wilson_mcnemar.py
```

应看到 repair 0.75、95% Wilson 约 `(0.531,0.888)`、delta +0.25、p 0.125。若组合数学不熟补 [F02](../../foundation_library/f02_csv_json/README.md) 并逐项跟算；四格方向回看 [Day 47](../day47/README.md)。

## 4. 即时知识

- **Wilson interval**：二项比例的 score interval，适合有限样本。
- **paired table**：同一 episode 的 baseline/repair 两个二元结果。
- **n01 recovery**：baseline fail、repair success。
- **n10 damage**：baseline success、repair fail。
- **effect size**：本课主效应是 `(n01−n10)/n`。
- **discordant pairs**：只有 n01+n10 能区分两条件。
- **exact McNemar**：在 discordant 总数上做双侧二项 exact test。
- **p-value boundary**：不是 null 为真的概率，也不是效果大小。

## 5. 成熟材料处方

- **主材料（NIST，10 分钟）**：[Binomial Proportion Confidence Interval](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/binomial.htm)。只看 Wilson/score interval 与 Wald 的差别。
- **补充材料（statsmodels 官方，10 分钟）**：[mcnemar](https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html)。核对 exact、correction 和四格输入；本课自己实现双侧 exact 便于审计。
- **锁定项目定位（8 分钟）**：[evaluator 第 322–334 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L322-L334) 返回单 episode success；[第 391–454 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L391-L454) 生成 episode 分母。正式 counts 必须由同 episode join 重建。

## 6. 最小实验

[minimal_wilson_mcnemar.py](code/minimal_wilson_mcnemar.py) 是完整 23 行代码：

```python
#!/usr/bin/env python3
"""最小例子：Wilson 区间与 exact McNemar 使用不同信息。"""

import math

n00, n01, n10, n11 = 4, 6, 1, 9
n = n00 + n01 + n10 + n11
z = 1.959963984540054
successes = n01 + n11
p = successes / n
denominator = 1 + z * z / n
center = (p + z * z / (2 * n)) / denominator
margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
margin /= denominator

discordant = n01 + n10
tail = sum(math.comb(discordant, k) for k in range(min(n01, n10) + 1))
exact_p = min(1.0, 2 * tail / (2 ** discordant))

print(f"repair_rate={p:.3f}")
print(f"wilson95=({center-margin:.3f}, {center+margin:.3f})")
print(f"paired_delta={(n01-n10)/n:+.3f}")
print(f"mcnemar_exact_p={exact_p:.4f}")
```

长文件 [compute_paired_statistics.py](code/compute_paired_statistics.py) 依次读 Wilson、exact binomial tail、分母与 boundary。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day57/code/compute_paired_statistics.py \
  --input shared/fixtures/day57_counts_a.json --config mainline/day57/config/statistics_a.json \
  --report learner_outputs/mainline/day57/paired_statistics_a.json
```

A synthetic delta +0.25、p=0.125；正确措辞是“点估计为正、区间较宽、exact test 未在 alpha .05 拒绝等边际”，不是“无效果”。未来正式操作必须从 Day 52–56 raw episode records 重建 counts，验证总数/方向后再运行；不得手填四格。

## 8. 独立挑战

用 B counts/config 生成新 report。写 ≥280 字 memo，必须原样包含 `Wilson interval`、`paired table`、`n01 recovery`、`n10 damage`、`baseline failures`、`baseline successes`、`effect size`、`confidence interval`、`exact McNemar`、`discordant pairs`、`two-sided p-value`、`alpha`、`not significant`、`not no effect`、`synthetic counts`。正文不给 B 数值。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day57.tests.test_day57_tools
.venv-day06/bin/python mainline/day57/code/check_day57.py \
  --example-input shared/fixtures/day57_counts_a.json --example-config mainline/day57/config/statistics_a.json --example-report learner_outputs/mainline/day57/paired_statistics_a.json \
  --challenge-input shared/fixtures/day57_counts_b.json --challenge-config mainline/day57/config/statistics_b.json --challenge-report learner_outputs/mainline/day57/paired_statistics_b.json \
  --challenge-memo learner_outputs/mainline/day57/challenge_memo.md
```

口述 10 分：四格 2；Wilson 2；recovery/damage 2；McNemar 2；解释边界 2。机器通过且 ≥8 进入 Day 58；错方向、错分母、Wald 替代、p 值冒充效应或 synthetic 冒充正式推断均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic counts 的 Wilson、effect、recovery/damage 和 exact McNemar。
- 静态源码事实：锁定 evaluator 的 episode success 与分母来源。
- 未运行：raw final episodes、VLA-Arena/GPU 和正式推断。
- 可以主张：统计脚本数学可重建，且分开效应、区间与检验。
- 不能主张：真实 repair 显著、有固定效果，或 A 的 p>0.05 证明无效。

自测题（答案在 `shared/answer_keys/day57.md`）：

1. Wilson interval 为什么比简单 Wald 更合适？
2. n01/n10 分别代表什么？
3. exact McNemar 使用哪些格？
4. p>alpha 能否写“没有效果”？
5. 为什么正式统计必须从 raw episodes 重建 counts？
