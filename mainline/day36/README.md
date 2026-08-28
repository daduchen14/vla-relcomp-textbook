# Mainline Day 36：用冻结决策矩阵选择唯一修复或停止

今天把 Day 35 的诊断变成可审查的 repair decision。矩阵同时考虑证据对齐、预期收益、实现成本、泄漏风险、L0 损伤风险与可证伪性；evidence gate 未过、最高分并列或不达阈值时必须 `STOP_NO_REPAIR`。选择修复不等于获准训练，本课所有输出均为 synthetic rehearsal 且 `authorized_for_training=false`。

## 1. 真实项目产物

- `repair_decision_a.csv`：四个候选的冻结分数、排名与唯一选择；
- `repair_decision_report_a.json`：gate、阈值、决策和训练授权边界；
- B 新矩阵的同类产物与 `challenge_memo.md`。

## 2. 当前卡点

看到 language oracle 恢复就直接做关系模块，会忽略 damage、信息泄漏和 L0 退化风险；同时做语言、视觉与控制三种修复，又无法知道哪个因素有效。更常见的问题是先看分数再改权重，让偏好的候选“获胜”。

本课先冻结权重与最低分，再运行矩阵。evidence gate 在排序前生效；候选必须唯一最高且过阈值。`STOP_NO_REPAIR` 不是失败，而是证据不足、并列或风险过高时的正式负结果。即便选出候选，付费/GPU 训练还需要后续独立配置与权限。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day36/code/minimal_decision_score.py
```

应看到语言候选分数高于视觉候选，并打印 `gate_required_before_selection=true`。若字典/循环卡住补 [F03](../../foundation_library/f03_modules_testing/README.md)；若不知道 evidence gate 来源，回看 [Day 35](../day35/README.md)。

## 4. 即时知识

- **decision matrix**：用冻结权重把多项收益/风险转成可复算排序。
- **evidence gate**：诊断质量的先决条件；未过则不进入候选排序结论。
- **unique repair**：只允许一个非 stop 候选，避免多因素改动。
- **implementation cost**：代码、数据、算力与排错负担；高成本扣分。
- **leakage risk**：修复是否可能把 L1/L2 或仿真真值泄漏进训练/部署。
- **L0 damage**：修复破坏已学能力的风险，必须在决策时而非事后考虑。
- **falsifiability**：能否用小实验明确推翻修复假设；越清晰越优先。

## 5. 成熟材料处方

- **中文主材料（5 分钟）**：[Python `max()` 官方中文文档](https://docs.python.org/zh-cn/3/library/functions.html#max)。理解排序只执行规则，不替你证明权重合理；并列必须显式处理。
- **实验规划补充（英文官方，10 分钟）**：[NIST Process Modeling：Objectives](https://www.itl.nist.gov/div898/handbook/pri/section2/pri211.htm)。只读先明确目标与响应量的部分，把“提高 L1/L2 且不伤 L0”写在训练前。
- **锁定项目定位（8 分钟）**：[SmolVLA 训练配置第 1–22 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/configs/train/smolvla.yaml#L1-L22) 明确 dataset、CUDA、batch、steps 与 checkpoint 等真实开销；Day 36 只决策，不运行该配置。

## 6. 最小实验

[minimal_decision_score.py](code/minimal_decision_score.py) 是完整 19 行代码：

```python
#!/usr/bin/env python3
"""最小例子：收益加分，成本/泄漏/损伤风险扣分。"""

candidates = {
    "LANGUAGE_RELATION_NORMALIZATION": {
        "alignment": 3, "benefit": 3, "falsifiability": 3,
        "cost": 1, "leakage": 1, "damage": 1,
    },
    "VISUAL_OBJECT_AUXILIARY": {
        "alignment": 1, "benefit": 2, "falsifiability": 2,
        "cost": 2, "leakage": 3, "damage": 2,
    },
}
for name, item in candidates.items():
    score = (3 * item["alignment"] + 2 * item["benefit"]
             + item["falsifiability"] - item["cost"]
             - 2 * item["leakage"] - 2 * item["damage"])
    print(f"{name}={score}")
print("gate_required_before_selection=true")
```

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day36/code/make_repair_decision.py \
  --spec shared/fixtures/day36_repair_candidates_a.csv \
  --config mainline/day36/config/repair_decision_weights.json \
  --output learner_outputs/mainline/day36/repair_decision_a.csv \
  --report learner_outputs/mainline/day36/repair_decision_report_a.json
```

A 应选择 `LANGUAGE_RELATION_NORMALIZATION`，同时打印 `authorized_for_training=false synthetic=true`。

真实项目必须用通过 Gate 5 的 formal diagnosis 填评分，冻结并提交矩阵后再看排名；评审每个 0–3 分的原始证据。若 gate 失败、并列或阈值不足，写 stop conclusion 并保留 falsifier；若唯一候选通过，只把它交给 Day 37 设计实验，不自动改训练数据、启动命令或租 GPU。

## 8. 独立挑战

用 B spec 生成新 decision/report。写 ≥240 字 memo，必须原样包含 `decision matrix`、`evidence gate`、`unique repair`、`STOP_NO_REPAIR`、`benefit`、`implementation cost`、`leakage risk`、`L0 damage`、`falsifiability`、`negative result`、`authorized_for_training`、`synthetic`、`causal`。解释为什么最高分也可能不被选择，以及 stop 后下一步是什么。正文不给 B 决策。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day36.tests.test_day36_tools
.venv-day06/bin/python mainline/day36/code/check_day36.py \
  --config mainline/day36/config/repair_decision_weights.json \
  --example-spec shared/fixtures/day36_repair_candidates_a.csv --example-output learner_outputs/mainline/day36/repair_decision_a.csv --example-report learner_outputs/mainline/day36/repair_decision_report_a.json \
  --challenge-spec shared/fixtures/day36_repair_candidates_b.csv --challenge-output learner_outputs/mainline/day36/repair_decision_b.csv --challenge-report learner_outputs/mainline/day36/repair_decision_report_b.json \
  --challenge-memo learner_outputs/mainline/day36/challenge_memo.md
```

口述 10 分：gate/冻结权重 2；收益与成本 2；leakage/L0 damage 2；唯一修复/stop 2；训练授权/causal 边界 2。机器通过且 ≥8 进入 Day 37；事后调权重、同时选多个、gate 失败仍修复、把选择当训练许可或把 synthetic 当研究结果均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic matrix、冻结权重、唯一选择、stop 路径与严格重建。
- 静态源码事实：锁定 SmolVLA 真实训练配置要求 CUDA、数据、batch/steps 与 checkpoint。
- 未运行：formal diagnosis 评分、训练配置、数据、模型/GPU。
- 可以主张：决策工具能唯一选择候选或在 gate 失败时停止。
- 不能主张：真实项目已选修复、分数客观真理、训练已获授权或修复会有效。

自测题（答案在 `shared/answer_keys/day36.md`）：

1. decision matrix 解决什么问题？
2. evidence gate 与候选分数谁先起作用？
3. 什么条件才叫 unique repair？
4. 为什么 negative result 是有效结论？
5. 选出候选是否等于 authorized_for_training？
