# Mainline Day 37：构建严格 L0-only 数据清单并做泄漏测试

今天把混合 level registry 变成只含 L0 的 repair dataset manifest。L0 可预先分为 train/validation；L1/L2 必须保持 `heldout_test`、`eligible_for_training=0`，不能用于样本选择、早停或调参。每行保存 BDDL、原 episode 与最终数据行的三层 hash，机器同时拒绝重复内容和 split-group 穿越。

## 1. 真实项目产物

- `l0_dataset_a.csv`：严格 L0-only 的 train/validation 数据清单；
- `l0_dataset_report_a.json`：输入/输出、held-out 排除、重复、split 与 provenance 结果；
- B 新 registry 的同类产物与 `challenge_memo.md`。

## 2. 当前卡点

文件夹叫 `L0` 不代表里面没有 L1/L2；按文件名随机切分还可能让同一 episode 的近重复片段同时进入 train 与 validation。只记录最终图片/动作路径，日后又无法追到是哪份 BDDL 和原始 episode。

本课把 level、task_id、eligibility 与 split 当成独立校验项。L1/L2 行允许出现在输入 registry，便于统计 held-out 边界，但绝不进入输出。`split_group_id` 把同源片段绑在一个 split；episode content hash 重复直接失败，而不是静默去重。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day37/code/minimal_l0_filter.py
```

应看到 selected 为 `a,c`、heldout 为 `b,d`、`training_levels=[0]`。若列表推导卡住补 [F01](../../foundation_library/f01_terminal_python/README.md)；若 hash 与路径不清楚回看 [Day 15](../day15/README.md)。

## 4. 即时知识

- **L0-only**：repair 的 train/validation 输出 level 集合严格等于 `{0}`。
- **heldout_test**：L1/L2 只在最终评测时首次使用；不能参与任何选择。
- **data lineage**：从 BDDL→原 episode→最终 dataset row 的内容身份链。
- **content hash**：按字节识别完全重复内容；不判断语义近重复或数据质量。
- **split group**：必须整体进入同一 split 的同源样本集合。
- **validation**：只可用预登记 L0 validation 做训练内选择；测试仍独立。
- **leakage**：测试信息直接或间接影响训练数据、prompt、阈值、checkpoint 或停止规则。

## 5. 成熟材料处方

- **中文主材料（8 分钟）**：[Python `hashlib` 官方中文文档](https://docs.python.org/zh-cn/3/library/hashlib.html)。只读 `sha256()`/`hexdigest()`，理解 hash 是内容身份，不是科学质量证明。
- **数据集补充（英文官方，8 分钟）**：[Hugging Face Datasets：DatasetDict](https://huggingface.co/docs/datasets/package_reference/main_classes#datasets.DatasetDict)。只读 split 名到 Dataset 的映射；本课先生成 manifest，不下载数据或创建 Hub 仓库。
- **锁定项目定位（8 分钟）**：[suite task map 第 163–185 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/benchmark/vla_arena_suite_task_map.py#L163-L185) 固定 L0/L1/L2 各 5 个任务；[SmolVLA train config 第 1–4 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/configs/train/smolvla.yaml#L1-L4) 指向 L0 数据 repo，但本项目仍须逐行验证来源，不能只信 repo 名。

## 6. 最小实验

[minimal_l0_filter.py](code/minimal_l0_filter.py) 是完整 17 行代码：

```python
#!/usr/bin/env python3
"""最小例子：训练只选择 L0，L1/L2 只计数不输出。"""

registry = [
    {"sample": "a", "level": 0, "split": "train"},
    {"sample": "b", "level": 1, "split": "heldout_test"},
    {"sample": "c", "level": 0, "split": "validation"},
    {"sample": "d", "level": 2, "split": "heldout_test"},
]
selected = [row for row in registry if row["level"] == 0]
excluded = [row for row in registry if row["level"] in {1, 2}]

assert all(row["split"] in {"train", "validation"} for row in selected)
assert all(row["split"] == "heldout_test" for row in excluded)
print(f"selected={[row['sample'] for row in selected]}")
print(f"heldout={[row['sample'] for row in excluded]}")
print("training_levels=[0]")
```

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day37/code/build_l0_dataset.py \
  --registry shared/fixtures/day37_registry_a.csv \
  --output learner_outputs/mainline/day37/l0_dataset_a.csv \
  --report learner_outputs/mainline/day37/l0_dataset_report_a.json
```

应看到 `rows=6 levels=[0] l1_l2_in_output=0 synthetic=true`。

真实数据阶段从合格 episode registry 导出每个 L0 trajectory/window 的 source hash、task/BDDL 和 split group；先按整组分割，再生成最终 row hash。L1/L2 registry 只保留 held-out 索引，不读取其结果挑样本。若发现 level/task 不一致、重复 episode/content、group 跨 split 或 eligibility 错误，先修 registry provenance，不手改输出 CSV。当前 fixture 不是 demonstration，未运行训练/GPU。

## 8. 独立挑战

用 B registry 生成新 manifest/report。写 ≥240 字 memo，必须原样包含 `L0-only`、`L1/L2`、`heldout_test`、`data lineage`、`source_bddl_sha256`、`source_episode_sha256`、`dataset_row_sha256`、`split group`、`duplicate content`、`leakage`、`validation`、`synthetic`、`training`。解释三层 hash、允许 split 与至少三条泄漏路径。正文不给 B 行数。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day37.tests.test_day37_tools
.venv-day06/bin/python mainline/day37/code/check_day37.py \
  --example-registry shared/fixtures/day37_registry_a.csv --example-output learner_outputs/mainline/day37/l0_dataset_a.csv --example-report learner_outputs/mainline/day37/l0_dataset_report_a.json \
  --challenge-registry shared/fixtures/day37_registry_b.csv --challenge-output learner_outputs/mainline/day37/l0_dataset_b.csv --challenge-report learner_outputs/mainline/day37/l0_dataset_report_b.json \
  --challenge-memo learner_outputs/mainline/day37/challenge_memo.md
```

口述 10 分：L0/held-out 边界 2；三层 lineage 2；split group 2；重复与 leakage 2；synthetic/training 边界 2。机器通过且 ≥8 进入 Day 38；L1/L2 调参、逐帧随机切分、静默去重、缺 provenance 或把 registry 当真实数据均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic registry 筛选、L0-only、held-out、hash、重复与 split-group 校验。
- 静态源码事实：锁定 suite 的 3×5 task map 与 SmolVLA 配置中的 L0 数据入口。
- 未运行：真实 demonstration 导出、近重复检测、训练/GPU。
- 可以主张：builder 不让合法输入中的 L1/L2 进入输出，并保留三层 lineage。
- 不能主张：真实 L0 数据已收集、内容高质量、语义近重复已消除或训练已开始。

自测题（答案在 `shared/answer_keys/day37.md`）：

1. L0-only 与 heldout_test 分别要求什么？
2. validation 能使用哪些 level？
3. 三层 data lineage 各是什么？
4. split group 与 duplicate content 分别防什么？
5. synthetic registry 通过能否说明 training data 已就绪？
