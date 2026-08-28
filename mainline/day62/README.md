# Mainline Day 62：生成最终表格

今天把 tidy episode 表变成论文式表格：每格同时给 successes、denominator、rate 与 95% Wilson interval；caption 和加粗规则由配置冻结。A/B 都是 synthetic，表格是教学版 paper table，不是项目最终结果。

## 1. 真实项目产物

- `table.csv`：未格式化的可复算统计量；
- `table.md`：caption、counts、区间、加粗说明与证据边界；
- `manifest.json`：输入/config/产物 hashes；
- B 新 tidy source 的表格和解释 memo。

## 2. 当前卡点

只放百分比会隐藏分母；只放 `±` 不说明区间方法会产生歧义；手工加粗最好的数字会把排版变成事后结论。论文表也不应成为新的数据源。

本课从 episode rows 重新分组，明确 Wilson 方法和圆整位数。加粗只表示“同 level 观察率最高”，不表示统计显著或方法优越。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day62/code/minimal_table_counts.py
```

应看到 baseline `1/2`、repair `2/2`。若 CSV 分组不熟补 [F02](../../foundation_library/f02_csv_json/README.md)；Wilson 回看 [Day 57](../day57/README.md)，tidy source 回看 [Day 61](../day61/README.md)。

## 4. 即时知识

- **caption**：独立说明表格对象、条件、指标、区间与边界。
- **count/denominator**：比例的分子和分母，必须能由 source rows 重建。
- **effect estimate**：本课为观察成功率，不等于因果效果。
- **Wilson interval**：二项比例的 95% score interval。
- **rounding**：展示层统一三位；原始 CSV 保留机器浮点值。
- **bold rule**：生成前冻结的强调规则；必须说明语义。
- **source of truth**：tidy episode 数据，而不是 Markdown 中的圆整数字。

## 5. 成熟材料处方

- **中文主材料（开放科学促进联合体，8 分钟）**：[中国早期职业研究人员开放科学技术指南](https://open4science.cn/static/ECR_OpenScience_Guide_CN.pdf)。只读数据与代码共享部分，思考表格怎样链接到可复算数据。
- **统计材料（NIST，10 分钟）**：[Binomial Proportion Confidence Interval](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/binomial.htm)。只看 Wilson/score interval，核对小样本不使用裸 Wald。
- **锁定项目定位（8 分钟）**：[task/suite 计数第 479–517 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L479-L517) 产生成功率分子分母；[结果 JSON 第 730–756 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L730-L756) 保存 suite 汇总，但正式论文表仍须由逐 episode release 重建。

## 6. 最小实验

[minimal_table_counts.py](code/minimal_table_counts.py) 是完整 18 行代码：

```python
#!/usr/bin/env python3
"""最小例子：表格同时报告成功数、分母和比例。"""

episodes = [
    {"condition": "baseline", "success": True},
    {"condition": "baseline", "success": False},
    {"condition": "repair", "success": True},
    {"condition": "repair", "success": True},
]

for condition in ("baseline", "repair"):
    selected = [row for row in episodes if row["condition"] == condition]
    successes = sum(row["success"] for row in selected)
    total = len(selected)
    print(
        f"{condition}: successes={successes}, "
        f"n={total}, rate={successes / total:.3f}"
    )
```

长文件 [generate_paper_table.py](code/generate_paper_table.py) 生成 CSV/Markdown/manifest，并拒绝覆盖旧输出。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day62/code/generate_paper_table.py \
  --input shared/fixtures/day62_tidy_a.csv --config mainline/day62/config/table_a.json \
  --output-dir learner_outputs/mainline/day62/table_a
```

A 应生成 4 个 level×condition 行。正式替换时只接受 Day 61 冻结 release 的 `episodes.csv`，先核对 manifest hash，再生成表；不得直接读取 evaluator 的圆整日志，也不得手工删除 failed rows。

## 8. 独立挑战

用 B tidy/config 生成新目录。写 ≥250 字 memo，原样包含 `paper table`、`caption`、`successes`、`denominator`、`Wilson interval`、`effect estimate`、`bold rule`、`descriptive only`、`rounding`、`tidy source`、`synthetic`、`cannot claim`。正文不给 B 分组数值。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day62.tests.test_day62_tools
.venv-day06/bin/python mainline/day62/code/check_day62.py \
  --example-input shared/fixtures/day62_tidy_a.csv --example-config mainline/day62/config/table_a.json --example-output-dir learner_outputs/mainline/day62/table_a \
  --challenge-input shared/fixtures/day62_tidy_b.csv --challenge-config mainline/day62/config/table_b.json --challenge-output-dir learner_outputs/mainline/day62/table_b \
  --challenge-memo learner_outputs/mainline/day62/challenge_memo.md
```

口述 10 分：counts/分母 2；Wilson 2；caption 2；加粗/圆整 2；source/boundary 2。机器通过且 ≥8 才完成 Day 62；只报比例、区间不命名、手工加粗、从展示表反向分析或冒充正式结果均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic tidy rows 的分组、Wilson、Markdown 与逐字节重建。
- 静态源码事实：锁定 evaluator 的 task/suite 计数与 JSON 汇总位置。
- 未运行：正式 episodes、VLA-Arena、GPU 和论文最终数值。
- 可以主张：表格生成器公开分子分母、区间、加粗规则和来源 hashes。
- 不能主张：加粗项显著更优，或表中数值代表真实模型。

自测题（答案在 `shared/answer_keys/day62.md`）：

1. 为什么比例旁必须给 successes/n？
2. Wilson interval 表达什么？
3. caption 至少说明哪些内容？
4. 加粗能否自动解释为显著优越？
5. paper table 能否反过来当分析输入？
