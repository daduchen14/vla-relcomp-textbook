# Mainline Day 19：用冻结口径建立 L1 held-out registry

今天从 Day 18 的 L0 spec 派生 L1 计划：model revision、protocol lock、seed 与 init 全部不变，只把 level 切到 1，并把用途锁为 `report_only_never_select_or_tune`。当前只生成 registry/guard，不运行模型、不查看 L1 结果。

## 1. 真实项目产物

- `learner_outputs/mainline/day19/l1_registry_a.csv`：与 L0 A 同口径的 5×2 L1 计划；
- `heldout_guard_a.json`：冻结字段、两份 spec hash 与反泄漏声明；
- B 新输入的 5×3 registry/guard 和 `challenge_memo.md`。

## 2. 当前卡点

如果看到 L1 低分后换 checkpoint、调阈值或润色 prompt，再回报同一个 L1，测试集已经参与方法选择。即使没有训练梯度，这也是数据泄漏。

本课让 L1 spec 继承 L0 的五个冻结字段，并拒绝 `score/selected_checkpoint/tuned_threshold/prompt_after_results` 等结果反馈字段。计划先写，结果后填。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day19/code/minimal_heldout_guard.py
```

应看到 `L1 uses frozen settings and report_only`。若集合与字段比较卡住补 [F02](../../foundation_library/f02_csv_json/README.md)；若不理解 OOD/held-out 回看 [Day 8](../day08/README.md)。

## 4. 即时知识

- **held-out**：不参与当前模型/方法选择的数据，只按预登记方式报告。
- **selection leakage**：测试结果影响 checkpoint、prompt、threshold、停止时点或超参数。
- **frozen-field drift**：L0→L1 除 level 外的运行口径变化，使比较失去意义。
- **report_only**：允许计算预登记结果，不允许把结果反馈给当前方法。
- **spec hash**：证明运行前使用的是哪份计划；不证明执行真的发生。

## 5. 成熟材料处方

- **中文主材料（15 分钟）**：[《动手学深度学习》欠拟合和过拟合](https://zh.d2l.ai/chapter_multilayer-perceptrons/underfit-overfit.html)。只读训练误差、验证误差与模型选择部分，区分 validation 与最终 test。
- **锁定源码（10 分钟）**：[SmolVLA evaluator task/level loop](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L634-L700)。确认 level/task 是运行输入；冻结 guard 属于本项目额外保护，不是 upstream 自动完成。

## 6. 最小实验

[minimal_heldout_guard.py](code/minimal_heldout_guard.py) 是完整 13 行代码：

```python
#!/usr/bin/env python3
"""最小例子：测试集结果不能回流到选择字段。"""

frozen = {"model_revision": "rev-a", "threshold": 0.04, "prompt": "original"}
l1_run = {"model_revision": "rev-a", "threshold": 0.04, "prompt": "original"}

changed = [key for key in frozen if frozen[key] != l1_run[key]]
forbidden_uses = {"select_checkpoint", "tune_threshold", "rewrite_prompt"}
declared_use = "report_only"

assert changed == []
assert declared_use not in forbidden_uses
print("PASS: L1 uses frozen settings and report_only")
```

真实脚本还对照 L0/L1 spec、锁定 task table 并拒绝结果字段。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day19/code/build_l1_registry.py \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --l0-spec shared/fixtures/day18_l0_spec_a.json \
  --l1-spec shared/fixtures/day19_l1_spec_a.json \
  --registry learner_outputs/mainline/day19/l1_registry_a.csv \
  --guard learner_outputs/mainline/day19/heldout_guard_a.json
```

应看到 `tasks=5 episodes=10 frozen_changes=0 heldout=report_only`；success 仍为空。阅读 [build_l1_registry.py](code/build_l1_registry.py) 的顺序是 `FROZEN → derive → task 展开 → guard`。

真实运行只能在 Day 15 formal lock、Day 17 adapter 和 Day 18 L0 结果完整后开始；沿 registry 逐 episode 运行，但不得根据中途 L1 结果换设置。若必须修改方法，记录 post hoc，新建后续开发集与新的最终测试边界。

若报 drift，比较两份 spec 而非放宽 guard；若 heldout use 不合法，恢复 report_only；若 registry 出现预填 success，删除猜测并追查来源；若缺 task，不能用宏平均掩盖。

## 8. 独立挑战

用 Day 18 B spec 与 `day19_l1_spec_b.json` 生成新的 5×3 L1 registry/guard。写 ≥170 字 `challenge_memo.md`，必须出现 `L1`、`held-out`、`checkpoint`、`threshold`、`prompt`、`report_only`、`leakage`，解释哪些分析允许、哪些反馈禁止。

机器会重算两份 spec hash、冻结字段与所有 episode ID；复制 A 后改 level 无法通过。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day19.tests.test_day19_tools
.venv-day06/bin/python mainline/day19/code/check_day19.py \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --example-l0-spec shared/fixtures/day18_l0_spec_a.json \
  --example-l1-spec shared/fixtures/day19_l1_spec_a.json \
  --example-registry learner_outputs/mainline/day19/l1_registry_a.csv \
  --example-guard learner_outputs/mainline/day19/heldout_guard_a.json \
  --challenge-l0-spec shared/fixtures/day18_l0_spec_b.json \
  --challenge-l1-spec shared/fixtures/day19_l1_spec_b.json \
  --challenge-registry learner_outputs/mainline/day19/l1_registry_b.csv \
  --challenge-guard learner_outputs/mainline/day19/heldout_guard_b.json \
  --challenge-memo learner_outputs/mainline/day19/challenge_memo.md
```

口述 10 分：held-out 定义 2；冻结字段 2；selection leakage 2；允许分析 2；post-hoc 处理 2。机器通过且 ≥8 进入 Day 20；看 L1 调参、漂移口径或计划冒充结果不通过。

## 10. 证据复盘

- 已运行：A/B L1 计划、冻结字段/hash、结果字段/selection use/drift 拒绝测试。
- 未运行：任何 L1 episode、模型、GPU、视频或 OOD 统计。
- 可以主张：L1 计划与对应 L0 口径一致且用途受 guard 约束。
- 不能主张：L1 泛化表现、相对 L0 下降或某 checkpoint 更好。

自测题（答案在 `shared/answer_keys/day19.md`）：

1. L1 held-out 的允许用途是什么？
2. 哪些字段必须从 L0 原样继承？
3. 看一眼结果再改 prompt 为什么也是 leakage？
4. report_only 是否意味着不能分析？
5. 当前 L1 registry 能支持什么结论？
