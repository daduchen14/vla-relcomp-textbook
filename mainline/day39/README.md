# Mainline Day 39：构造平衡、对比、规范化的 L0 训练 pairs

今天把 Day 37 的 L0 manifest 与 Day 38 的规范化文本组织成训练 pair：每个样本保留原指令 `control` 和规范化指令 `normalized` 两臂，共享同一个 action target。四种 relation 按冻结 seed 确定性采样到相同数量，选择过程不读取模型 outcome；输出仍只是 synthetic manifest，不加载图像/动作，不运行训练。

## 1. 真实项目产物

- `training_pairs_a.csv`：平衡 relation coverage 的完整 control/normalized pairs；
- `training_pairs_report_a.json`：采样数、平衡差、pair 完整性、level 与 outcome-free 边界；
- B 新 registry/config 的同类产物与 `challenge_memo.md`。

## 2. 当前卡点

直接把所有规范化文本追加到训练集，会让原本样本多的关系占据更多梯度；只保留 normalized 又无法做“模块是否必要”的最小消融。若两臂对应不同动作、episode 或对象，它们也不再是 instruction contrast。

本课先按 relation 分组，再用 `sampling_seed + sample_id` 的 hash 排序，每组取相同冻结数量。每个选中样本展开两臂；两臂只改变 instruction，`action_target_sha256`、source episode、对象与 split 均固定。缺臂、raw=normalized、非 L0、重复 episode 或关系不足都会失败。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day39/code/minimal_balanced_pairs.py
```

应看到每种 relation 取 2 个、6 个 pair/12 个 arm。若列表推导卡住补 [F01](../../foundation_library/f01_terminal_python/README.md)；L0 与 normalizer 分别回看 [Day 37](../day37/README.md)、[Day 38](../day38/README.md)。

## 4. 即时知识

- **balanced sampling**：每个 relation 选中相同数量，避免类别频次主导训练。
- **relation coverage**：NextTo/On/In/Between 的原始和选中计数；不等于对象难度平衡。
- **contrast pair**：同一 source/action 的两种 instruction treatment。
- **pair label**：`same_action_instruction_contrast` 明确两臂应预测同一动作目标。
- **sample weight**：样本进 loss 的相对权重；本课冻结为 1.0。
- **outcome-free selection**：采样不读取模型成功、loss 或测试表现，防止结果驱动挑样本。
- **pair completeness**：control 与 normalized 两臂都在才进入训练 manifest。

## 5. 成熟材料处方

- **中文主材料（6 分钟）**：[Python `sorted()` 官方中文文档](https://docs.python.org/zh-cn/3/library/functions.html#sorted)。理解 key 决定确定性顺序，原输入不被原地修改。
- **实验设计补充（英文官方，10 分钟）**：[NIST Randomized Block Designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm)。把 relation 看作预登记 strata；本课的 hash 排序用于可复算抽样，不声称完成随机试验。
- **锁定项目定位（8 分钟）**：[SmolVLA 训练配置第 1–18 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/configs/train/smolvla.yaml#L1-L18) 定义真实 dataset、batch、steps 与 checkpoint；Day 39 只生成教学 manifest，不改或执行该配置。

## 6. 最小实验

[minimal_balanced_pairs.py](code/minimal_balanced_pairs.py) 是完整 22 行代码：

```python
#!/usr/bin/env python3
"""最小例子：每种关系取相同数量，再展开 control/normalized 两臂。"""

samples = {
    "NextTo": ["n1", "n2", "n3"],
    "On": ["o1", "o2"],
    "In": ["i1", "i2", "i3"],
}
target_per_relation = min(len(rows) for rows in samples.values())
selected = {
    relation: rows[:target_per_relation]
    for relation, rows in samples.items()
}
pairs = [
    (sample_id, arm)
    for rows in selected.values()
    for sample_id in rows
    for arm in ("control", "normalized")
]
print(f"target_per_relation={target_per_relation}")
print(f"pair_count={len(pairs) // 2} arm_count={len(pairs)}")
print(f"balanced_counts={{{', '.join(f'{k}:{len(v)}' for k, v in selected.items())}}}")
```

长文件 [build_training_pairs.py](code/build_training_pairs.py) 依次阅读 schema/边界、关系分组、seeded hash 排序、两臂展开和报告；完整代码可直接运行。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day39/code/build_training_pairs.py \
  --input shared/fixtures/day39_training_registry_a.csv \
  --config mainline/day39/config/training_pair_config_a.json \
  --output learner_outputs/mainline/day39/training_pairs_a.csv \
  --report learner_outputs/mainline/day39/training_pairs_report_a.json
```

应看到 `pairs=8 arms=16 balance_gap=0 levels=[0] synthetic=true`。

真实阶段 join Day 37 L0 rows、Day 38 normalized text 和实际 action-label content hash；先冻结 relation target 与 seed，再生成 manifest。两臂指向同一图像/状态/动作数据，只替换 instruction。若某 relation 数量不足，缩小所有组或补 L0 数据，不能从 L1/L2 借样本。当前不读取真实 tensor、动作文件，不调用 trainer/GPU。

## 8. 独立挑战

用 B registry/config 生成新 pairs/report。写 ≥240 字 memo，必须原样包含 `balanced sampling`、`relation coverage`、`contrast pair`、`control`、`normalized`、`same action target`、`pair label`、`sample weight`、`sampling seed`、`outcome-free`、`L0-only`、`incomplete pair`、`synthetic`、`training`。解释允许变化、固定项、采样规则与缺臂处理。正文不给 B 选中 ID。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day39.tests.test_day39_tools
.venv-day06/bin/python mainline/day39/code/check_day39.py \
  --example-input shared/fixtures/day39_training_registry_a.csv --example-config mainline/day39/config/training_pair_config_a.json --example-output learner_outputs/mainline/day39/training_pairs_a.csv --example-report learner_outputs/mainline/day39/training_pairs_report_a.json \
  --challenge-input shared/fixtures/day39_training_registry_b.csv --challenge-config mainline/day39/config/training_pair_config_b.json --challenge-output learner_outputs/mainline/day39/training_pairs_b.csv --challenge-report learner_outputs/mainline/day39/training_pairs_report_b.json \
  --challenge-memo learner_outputs/mainline/day39/challenge_memo.md
```

口述 10 分：平衡/coverage 2；contrast 唯一变化 2；action/label 固定 2；seed/outcome-free 2；L0/synthetic 边界 2。机器通过且 ≥8 进入 Day 40；按结果挑样本、借 L1/L2、缺臂、动作 label 不同或把 manifest 当训练结果均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic registry 的确定性平衡、完整 pair、同 action hash 与严格重建。
- 静态源码事实：锁定训练配置的真实数据、batch/steps 与 checkpoint 入口。
- 未运行：真实图像/动作读取、dataloader、loss、模型/GPU。
- 可以主张：manifest 在四关系上计数平衡，两臂共享监督 target 且选择不看 outcome。
- 不能主张：对象难度完全平衡、样本高质量、loss 会改善或训练已开始。

自测题（答案在 `shared/answer_keys/day39.md`）：

1. balanced sampling 解决什么，不解决什么？
2. contrast pair 的两臂必须共享什么？
3. pair label 与 sample weight 各起什么作用？
4. 为什么 sampling 必须 outcome-free？
5. incomplete pair 应怎样处理？
