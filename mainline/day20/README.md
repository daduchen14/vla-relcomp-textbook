# Mainline Day 20：冻结 L2 strong-OOD 计划并做行为失败分类

今天从 L0 spec 派生 L2 registry，继续保持 report-only；同时把四段事件压成“首个未满足事件”标签。你会保留 ENV_INVALID、success/probe 冲突和证据边界，不把行为标签冒充模型内部原因。免费运行只使用合成失败 fixture。

## 1. 真实项目产物

- `learner_outputs/mainline/day20/l2_registry_a.csv`、`heldout_guard_a.json`：5×2 L2 计划；
- `failure_labels_a.csv`、`failure_report_a.json`：合成四段结果的行为分类；
- B 新输入对应的 5×3 计划、分类与 `challenge_memo.md`。

## 2. 当前卡点

总体失败只说“没完成”，不能说明行为链断在哪里；但标签太强又会越界。例如没有 approach 可能来自关系 grounding、视角遮挡、轨迹控制或 probe 假阴，不能直接命名为“语言理解失败”。

本课只标首个未满足 observable event，并明确 `behavioral_only=true`。环境无效单列；success 与 probes 冲突单列，交给视频抽查。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day20/code/minimal_first_unmet.py
```

应看到 `first_unmet=reference_approached` 与 `observable_behavior_not_internal_cause`。若生成器/`next` 卡住补 [F03](../../foundation_library/f03_modules_testing/README.md)；四段语义回看 [Day 12](../day12/README.md)。

## 4. 即时知识

- **strong OOD / L2**：更强未见组合层级，仍是 held-out，不用于选择方法。
- **first unmet**：按 contact→lift→approach→relation 顺序找到首个 false。
- **ENV_INVALID**：环境/输入无效，success 可空，不进入模型失败分母。
- **probe gap**：success=true 但某阶段 probe=false，可能是 probe 假阴或非典型成功路径。
- **inconsistent signal**：四段全 true 但 success=false，提示数据/对齐/采集异常。
- **behavioral label**：描述轨迹证据；causal mechanism 需受控干预才能判断。

## 5. 成熟材料处方

- **中文主材料（8 分钟）**：[Python 内置函数 `next`](https://docs.python.org/zh-cn/3/library/functions.html#next)。只读 iterator 与 default；对应“按冻结顺序取第一个 false”，不是机器学习分类器。
- **锁定项目材料（12 分钟）**：[VLA-Arena 场景构建指南 §1.4](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/docs/scene_construction_zh.md#14-状态定义)。重读 goal/state 边界，确认 relation success 是环境谓词，而前三段是本项目 probe。

## 6. 最小实验

[minimal_first_unmet.py](code/minimal_first_unmet.py) 是完整 13 行代码：

```python
#!/usr/bin/env python3
"""最小例子：失败标签是首个未满足事件，不是内部机制诊断。"""

events = {
    "target_contacted": True,
    "target_lifted": True,
    "reference_approached": False,
    "relation_satisfied": False,
}

first_unmet = next(name for name, passed in events.items() if not passed)
print(f"first_unmet={first_unmet}")
print("boundary=observable_behavior_not_internal_cause")
```

完整分类器还处理 success、invalid、probe gap 与 inconsistent signal。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day20/code/build_l2_registry.py \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --l0-spec shared/fixtures/day18_l0_spec_a.json \
  --l2-spec shared/fixtures/day20_l2_spec_a.json \
  --registry learner_outputs/mainline/day20/l2_registry_a.csv \
  --guard learner_outputs/mainline/day20/heldout_guard_a.json
.venv-day06/bin/python mainline/day20/code/classify_failures.py \
  --input shared/fixtures/day20_failures_a.csv \
  --output learner_outputs/mainline/day20/failure_labels_a.csv \
  --report learner_outputs/mainline/day20/failure_report_a.json
```

应看到 `L2 tasks=5 episodes=10 frozen_changes=0` 与 `classified=6 ... behavioral_only=true`。第二条是合成数据代码测试，不是 L2 结果。阅读 [build_l2_registry.py](code/build_l2_registry.py) 先看 frozen guard，再看 [classify_failures.py](code/classify_failures.py) 的 valid/success/stage 分支。

真实运行需用 Day 17 adapter 回填 registry，并把 Day 12 events 按 episode_id join 后再分类。L2 中途结果不得改变 checkpoint、threshold、prompt 或 taxonomy；taxonomy 若有缺陷，只能记录 post hoc 并在新数据边界验证。

若 ENV_INVALID 出现 success，检查 join；若 success/probe 冲突，不要人工改 label；若 frozen drift，停止运行；若某 task 缺行，先补完整分母。

## 8. 独立挑战

使用 Day 18 B spec、`day20_l2_spec_b.json` 与 `day20_failures_b.csv` 生成新的 registry/guard/labels/report。写 ≥180 字 memo，必须出现 `L2`、`strong OOD`、`first unmet`、`ENV_INVALID`、`probe gap`、`behavioral`、`causal`。

解释至少一个冲突标签的后续证据需求；正文不展示 B 的 label counts。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day20.tests.test_day20_tools
.venv-day06/bin/python mainline/day20/code/check_day20.py \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --example-l0-spec shared/fixtures/day18_l0_spec_a.json --example-l2-spec shared/fixtures/day20_l2_spec_a.json \
  --example-registry learner_outputs/mainline/day20/l2_registry_a.csv --example-guard learner_outputs/mainline/day20/heldout_guard_a.json \
  --example-raw shared/fixtures/day20_failures_a.csv --example-labels learner_outputs/mainline/day20/failure_labels_a.csv --example-report learner_outputs/mainline/day20/failure_report_a.json \
  --challenge-l0-spec shared/fixtures/day18_l0_spec_b.json --challenge-l2-spec shared/fixtures/day20_l2_spec_b.json \
  --challenge-registry learner_outputs/mainline/day20/l2_registry_b.csv --challenge-guard learner_outputs/mainline/day20/heldout_guard_b.json \
  --challenge-raw shared/fixtures/day20_failures_b.csv --challenge-labels learner_outputs/mainline/day20/failure_labels_b.csv --challenge-report learner_outputs/mainline/day20/failure_report_b.json \
  --challenge-memo learner_outputs/mainline/day20/challenge_memo.md
```

口述 10 分：L2 held-out 2；taxonomy 2；invalid 2；冲突/probe gap 2；causal 边界 2。机器通过且 ≥8 进入 Day 21；调参、把 invalid 算失败或把行为标签当机制不通过。

## 10. 证据复盘

- 已运行：A/B L2 计划、零 drift guard、六类合成行为标签与冲突测试。
- 未运行：L2 模型、GPU、视频、真实失败比例。
- 可以主张：L2 计划和 failure taxonomy 已冻结且可重算。
- 不能主张：真实 strong-OOD 表现或任何 causal 瓶颈。

自测题（答案在 `shared/answer_keys/day20.md`）：

1. L2 与 L0 必须共享哪些口径？
2. first unmet 标签能/不能说明什么？
3. ENV_INVALID 如何进入分母？
4. 两类 success/probe 冲突如何处理？
5. 当前分类可以支持真实失败占比吗？
