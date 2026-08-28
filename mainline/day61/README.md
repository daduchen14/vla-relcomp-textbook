# Mainline Day 61：清理数据、脚本和可追溯索引

今天把嵌套 episode 记录整理为发布候选数据：原始输入只读，一行一个 episode，一列一个变量；每个派生产物都有 schema、SHA-256 和 provenance index。所有输入仍是 synthetic，目标是验证发布工程，不是发布 VLA-Arena 结果。

## 1. 真实项目产物

- `episodes.csv`：稳定排序的 tidy episode 表；
- `provenance_index.json`：每行到原始记录与源摘要的映射；
- `manifest.json`：schema、行数、产物 hashes、只读与证据边界；
- B 新输入的独立 release candidate 与说明 memo。

## 2. 当前卡点

分析期间的嵌套 JSON 适合程序写入，却不适合人工复核和论文脚本。若“清洗”直接覆盖 raw，错误无法回滚；若只交 CSV 而不交来源索引，表格数字又无法回到 episode。

因此 raw immutable，tidy/manifest/index 都是 derived artifacts。输出目录已存在时脚本直接拒绝，迫使每个 release 使用新版本目录。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day61/code/minimal_tidy_rows.py
```

应按 `e01`、`e02` 输出扁平字典。若 CSV/JSON 不熟补 [F02](../../foundation_library/f02_csv_json/README.md)；results lock 回看 [Day 60](../day60/README.md)。

## 4. 即时知识

- **tidy data**：一行一个观察、一列一个变量、一张表一个观察单位。
- **primary key**：在表内唯一标识一行；这里是 `episode_id`。
- **raw immutable**：原始输入不被清洗脚本改写。
- **derived artifact**：从 raw 可重复生成的 CSV、索引或表格。
- **schema**：字段、类型、主键和观察单位的明确契约。
- **provenance index**：派生行到源记录、版本和 hash 的反向索引。
- **release candidate**：准备审阅但尚未宣布为正式结果的冻结包。

## 5. 成熟材料处方

- **中文主材料（开放科学促进联合体，12 分钟）**：[中国早期职业研究人员开放科学技术指南](https://open4science.cn/static/ECR_OpenScience_Guide_CN.pdf)。只读数据/代码共享与 FAIR 相关部分，记录“能找到、能理解、能复核”分别需要什么元数据。
- **补充材料（Journal of Statistical Software，10 分钟）**：[Tidy Data 论文 PDF](https://vita.had.co.nz/papers/tidy-data.pdf)。重点看 variable、observation、observational unit 三个定义与宽/长表转换。
- **锁定项目定位（8 分钟）**：[episode 计数与日志第 391–499 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L391-L499) 说明原始 episode 发生在哪里；[汇总 JSON 第 724–757 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L724-L757) 只保存 suite 级汇总，所以正式发布还需外层逐 episode ledger。

## 6. 最小实验

[minimal_tidy_rows.py](code/minimal_tidy_rows.py) 是完整 20 行代码：

```python
#!/usr/bin/env python3
"""最小例子：一行一个 episode，一列一个变量。"""

raw = [
    {"episode_id": "e02", "condition": "repair", "outcome": {"success": False, "cost": 2.0}},
    {"episode_id": "e01", "condition": "baseline", "outcome": {"success": True, "cost": 0.0}},
]

tidy = [
    {
        "episode_id": row["episode_id"],
        "condition": row["condition"],
        "success": row["outcome"]["success"],
        "cost": row["outcome"]["cost"],
    }
    for row in raw
]

for row in sorted(tidy, key=lambda item: item["episode_id"]):
    print(row)
```

长文件 [build_release_candidate.py](code/build_release_candidate.py) 执行 schema/主键检查、稳定排序、hash 与不可覆盖策略。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day61/code/build_release_candidate.py \
  --input shared/fixtures/day61_episodes_a.json --config mainline/day61/config/release_a.json \
  --output-dir learner_outputs/mainline/day61/release_a
```

应生成 4 行并报告 `source_unchanged=true`。正式运行时输入应来自锁定 evaluator 的逐 episode ledger，不得从 suite 总成功率反推 episode；输出使用新的版本目录，旧 raw 与旧 release 均不覆盖。

## 8. 独立挑战

对 B 输入/config 创建 `release_b`，不要复用 A 目录。写 ≥260 字 memo，原样包含 `release candidate`、`raw immutable`、`tidy data`、`one row per episode`、`primary key`、`schema`、`provenance index`、`SHA-256`、`derived artifact`、`no overwrite`、`synthetic`、`cannot claim`；说明如何从任意 CSV 行回到源记录。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day61.tests.test_day61_tools
.venv-day06/bin/python mainline/day61/code/check_day61.py \
  --example-input shared/fixtures/day61_episodes_a.json --example-config mainline/day61/config/release_a.json --example-output-dir learner_outputs/mainline/day61/release_a \
  --challenge-input shared/fixtures/day61_episodes_b.json --challenge-config mainline/day61/config/release_b.json --challenge-output-dir learner_outputs/mainline/day61/release_b \
  --challenge-memo learner_outputs/mainline/day61/challenge_memo.md
```

口述 10 分：tidy/schema 2；raw 只读 2；主键 2；provenance 2；synthetic 边界 2。机器通过且 ≥8 才完成 Day 61；覆盖目录、重复 ID、丢失败行、无 hash/index 或冒充正式数据均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic nested records 到 release candidate 的逐字节重建。
- 静态源码事实：锁定 evaluator 的 episode loop、计数和 suite 汇总 JSON。
- 未运行：VLA-Arena、GPU、正式逐 episode ledger 与公开发布。
- 可以主张：同一输入/config 能重建相同 CSV/index/manifest，且脚本拒绝覆盖。
- 不能主张：这些行是真实模型 episode 或足以支持论文结论。

自测题（答案在 `shared/answer_keys/day61.md`）：

1. 一行一个 episode 属于哪条 tidy 约定？
2. 为什么清洗不能覆盖 raw？
3. 本课的 primary key 是什么？
4. provenance index 解决什么问题？
5. synthetic release candidate 能否当真实结果发布？
