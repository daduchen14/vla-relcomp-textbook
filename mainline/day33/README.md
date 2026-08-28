# Mainline Day 33：运行语言规范化 oracle 的配对分析

今天把自然指令临时改写为固定的 `TARGET | START | ACTION | GOAL` 结构，并对 control/oracle 的 success 与四段事件分别计算 recovery、damage 和首个变化阶段。oracle 使用 BDDL 真值，只用于诊断；当前免费运行分析 synthetic 配对结果，不冒充真实模型干预。

## 1. 真实项目产物

- `language_oracle_pairs_a.csv`：每对 success transition 与 first changed stage；
- `language_oracle_report_a.json`：success/四阶段的 00/01/10/11、recovery 与 damage；
- B 新输入的同类产物与 `challenge_memo.md`。

## 2. 当前卡点

总体 success 从 0 变 1，只说明结构化文本与行为变化同时出现；不知道最早从 contact、lift、approach 还是 relation 开始，也不知道原成功是否被破坏。只报恢复率会隐藏 damage；把两组非匹配 episode 比平均值又会混入初态。

因此每个 pair 固定 task/seed/init/对象/goal，只改变送给 policy 的 instruction。分析器严格校验 oracle 字段顺序与内容，并为每个阶段构造配对四格。恢复仍可能来自文本长度、token 分布或执行随机性，不能直接证明内部语言关系模块。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day33/code/minimal_normalized_instruction.py
```

应看到四个字段、`privilege=bddl_truth` 和 `use=diagnostic_only`。若字符串拼接卡住补 [F01](../../foundation_library/f01_terminal_python/README.md)；若 recovery/damage 分母不清楚回看 [Day 14](../day14/README.md)。

## 4. 即时知识

- **normalized instruction**：固定字段名、顺序和关系表达，降低表面措辞差异。
- **BDDL truth**：target/start/goal 的仿真真值；默认不属于公开 policy observation。
- **paired outcome**：同一 task/seed/init 的 control 与 oracle 两臂结果。
- **recovery**：control=0 中 oracle=1；分母为 control failures。
- **damage**：control=1 中 oracle=0；分母为 control successes。
- **stage effect**：对四段事件各自计算同样四格，而非只看最终 success。
- **first changed stage**：同一 pair 中最早真值不同的观测阶段；`NONE` 也必须保留。

## 5. 成熟材料处方

- **中文主材料（6 分钟）**：[Python `str.join` 官方中文文档](https://docs.python.org/zh-cn/3/library/stdtypes.html#str.join)。理解为什么字段顺序由显式 tuple 决定，不能依赖自由文本。
- **因果补充（英文官方，12 分钟）**：[PyWhy DoWhy：Estimating Causal Effects](https://www.pywhy.org/dowhy/v0.13/user_guide/causal_tasks/estimating_causal_effects/index.html)。只读 treatment、outcome、estimand 的区别；本课的 treatment 是 oracle instruction，四段事件是 outcomes。
- **锁定项目定位（10 分钟）**：[SmolVLA `run_episode` 第 225–305 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L225-L305) 把 `task_description` 放入 policy observation，并用 `env.set_init_state(initial_state)` 固定初态；真实 oracle 只能改前者。

## 6. 最小实验

[minimal_normalized_instruction.py](code/minimal_normalized_instruction.py) 是完整 16 行代码：

```python
#!/usr/bin/env python3
"""最小例子：把关系真值写成固定字段顺序。"""

facts = {
    "target": "tomato_1",
    "start": "next_to(cereal_1)",
    "action": "pick_and_place",
    "goal": "On(porcelain_bowl_3)",
}
order = ("target", "start", "action", "goal")
normalized = " | ".join(f"{key.upper()}={facts[key]}" for key in order)

print(normalized)
print(f"field_count={len(order)}")
print("privilege=bddl_truth")
print("use=diagnostic_only")
```

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day33/code/analyze_language_oracle.py \
  --input shared/fixtures/day33_language_oracle_results_a.csv \
  --output learner_outputs/mainline/day33/language_oracle_pairs_a.csv \
  --report learner_outputs/mainline/day33/language_oracle_report_a.json
```

应看到 5 对 synthetic 结果，success recovery `2/3`、damage `1/2`。这些数字只验证统计器。

真实运行时，从 Day 9 task table 生成唯一 normalized text；同一 pair 加载完全相同 initial state，control 使用原 instruction，oracle 只替换 `task_description`，两臂接 Day 27–30 的四段 probe。保存完整/中断/无效 episode 与原始日志，禁止只保留恢复案例。L1/L2 的 BDDL truth 只能用于预登记 diagnostic pilot，不得进入最终修复输入。

## 8. 独立挑战

用 B input 生成新 pair summary/report。写 ≥240 字 memo，必须原样包含 `normalized instruction`、`TARGET`、`START`、`ACTION`、`GOAL`、`BDDL truth`、`recovery`、`damage`、`stage effect`、`paired`、`leakage`、`synthetic`、`causal`。解释 B 的分母、首个变化阶段如何解读，以及至少两个替代解释。正文不给 B 数值答案。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day33.tests.test_day33_tools
.venv-day06/bin/python mainline/day33/code/check_day33.py \
  --example-input shared/fixtures/day33_language_oracle_results_a.csv --example-output learner_outputs/mainline/day33/language_oracle_pairs_a.csv --example-report learner_outputs/mainline/day33/language_oracle_report_a.json \
  --challenge-input shared/fixtures/day33_language_oracle_results_b.csv --challenge-output learner_outputs/mainline/day33/language_oracle_pairs_b.csv --challenge-report learner_outputs/mainline/day33/language_oracle_report_b.json \
  --challenge-memo learner_outputs/mainline/day33/challenge_memo.md
```

口述 10 分：结构化字段/特权来源 2；配对固定项 2；recovery/damage 2；stage effect 2；leakage/causal 边界 2。机器通过且 ≥8 进入 Day 34；缺臂入分母、只报恢复、修改 init、把 oracle 当最终方法或把 synthetic 数字当研究结果均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic oracle 配对、文本 schema、四格/阶段效果与严格重建。
- 静态源码事实：锁定 evaluator 的 policy observation 包含 task description，并可设置 initial state。
- 未运行：真实 control/oracle policy episode、模型/GPU、视频。
- 可以主张：分析器正确分离 recovery/damage，并定位每对最早观测变化阶段。
- 不能主张：真实 oracle 有效、语言是主要瓶颈、内部机制或可部署修复。

自测题（答案在 `shared/answer_keys/day33.md`）：

1. normalized instruction 暴露了什么，为什么是 privileged？
2. recovery 与 damage 的分母分别是什么？
3. stage effect 能说明什么、不能说明什么？
4. oracle 恢复还有哪些非语义解释？
5. 能否把 L1/L2 BDDL truth 直接用于最终修复？
