# Mainline Day 26：把研究假设变成可证伪的指标表

今天不运行新模型，而是把“关系没理解”“视觉没看对”“控制不稳定”改写成实验前可检查的行：observable event、metric 的 numerator/denominator、单因素 intervention、directional prediction、falsifier、controls 和至少两个 alternative explanations。

## 1. 真实项目产物

- `hypothesis_matrix_a.csv` 与 `hypothesis_report_a.json`；
- B 新假设的 matrix/report 与 `challenge_memo.md`；
- 所有行固定为 `pre_registered_untested`，不混入观察结果。

## 2. 当前卡点

宽泛机制故事可以解释任何结果，因而无法被数据推翻。只写“看 contact rate”也不够：分母不明确、没有对照 intervention、失败后还能换解释。相反，单次 oracle 恢复也未必唯一指向一个机制，可能是 probe 缺陷或 intervention 同时改变多个因素。

本课先写 prediction 和 falsifier，再运行。每个假设只选一个主要四段事件，明确 paired recovery 的分子/分母，固定 task/seed/init/model/protocol，并列出替代解释。表是实验设计，不是因果结论。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day26/code/minimal_falsifier.py
```

应看到 synthetic `1/5=0.200` 未达到 0.30。若布尔/`sum` 不熟补 [F02](../../foundation_library/f02_csv_json/README.md)；四段事件回看 [Day 12](../day12/README.md)，配对反事实回看 [Day 13](../day13/README.md)。

## 4. 即时知识

- **hypothesis**：对可观察模式与 intervention 响应的预先陈述。
- **observable**：日志/状态可重复测量的 contact、lift、approach、relation，不是“理解程度”。
- **metric**：必须写 numerator 与 denominator；本课用有效 pair 的 recovery rate。
- **intervention**：有意改变一个因素的实验臂；baseline 与 intervention 其余条件保持一致。
- **prediction**：若假设在本设计下成立，指标应朝哪个方向、越过什么阈值。
- **falsifier**：什么观察会与 prediction 冲突；不是证明反命题为真。
- **alternative explanation**：同样观察模式的其他可能原因，至少两个。
- **causal status**：设计前只能是 untested；一次支持也不能宣称唯一机制。

## 5. 成熟材料处方

- **中文主材料（6 分钟）**：[Python `all()` / `any()` 官方中文文档](https://docs.python.org/zh-cn/3/library/functions.html#all)。理解“所有 controls 齐全”的程序检查；它不替代实验判断。
- **实验设计材料（12 分钟）**：[NIST 5.1.1 “What is experimental design?”](https://www.itl.nist.gov/div898/handbook/pri/section1/pri11.htm)。重点读事先确定 objective、factor、response，以及主动改变 factor 观察 response。
- **因果边界材料（8 分钟）**：[NIST 3.1.3.6 “Experiments and Experimental Design”](https://www.itl.nist.gov/div898/handbook/ppc/section1/ppc136.htm)。只读 correlation 与 causality 区分。
- **锁定项目材料（10 分钟）**：[SmolVLA evaluator 的真实 `run_episode` 成功判定链](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L270-L349)。success 是环境终态；contact/lift/approach 是项目 probe，不能混称 evaluator 原生机制标签。

## 6. 最小实验

[minimal_falsifier.py](code/minimal_falsifier.py) 是完整 20 行代码。它先冻结 `prediction/falsifier`，再读取 synthetic observation；输出 false 只表示这次测试未支持该阈值预测。

```python
#!/usr/bin/env python3
"""最小例子：先写阈值和 falsifier，再看 synthetic observation。"""

hypothesis = {
    "prediction": "paired_recovery_rate >= 0.30",
    "threshold": 0.30,
    "falsifier": "paired_recovery_rate < 0.30",
}
synthetic_recoveries = [1, 0, 0, 0, 0]

numerator = sum(synthetic_recoveries)
denominator = len(synthetic_recoveries)
observed = numerator / denominator
supported_by_test = observed >= hypothesis["threshold"]

print(f"metric={numerator}/{denominator}={observed:.3f}")
print(f"prediction={hypothesis['prediction']}")
print(f"falsifier={hypothesis['falsifier']}")
print(f"supported_by_this_synthetic_test={supported_by_test}")
print("boundary=one_test_does_not_establish_a_unique_causal_mechanism")
```

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day26/code/build_hypothesis_matrix.py \
  --spec shared/fixtures/day26_hypotheses_a.json \
  --matrix learner_outputs/mainline/day26/hypothesis_matrix_a.csv \
  --report learner_outputs/mainline/day26/hypothesis_report_a.json
```

应看到 `hypotheses=3 ... pre_registered_untested`。A/B 都是 synthetic 设计文本，没有干预结果。

真实操作先从 Day 23 evidence index 选择预注册失败 strata，但不能把既有结果写回 spec；用 Day 13 pair manifest 固定 controls，Day 14 oracle 只改变声明的因素。运行前封存 matrix，运行后另建 results 表，通过 hypothesis_id 连接。probe 无效、两臂异常或 intervention 泄漏必须单列，不静默进入 denominator。

## 8. 独立挑战

用 B spec 生成新 matrix/report，不给正文输出。写 ≥220 字 memo，必须原样包含 `hypothesis`、`prediction`、`observable`、`metric`、`numerator`、`denominator`、`intervention`、`control`、`falsifier`、`alternative`、`causal`、`synthetic`。

任选一行说明支持模式、推翻模式和两个替代解释；不得写成已经观察到的结果。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day26.tests.test_day26_tools
.venv-day06/bin/python mainline/day26/code/check_day26.py \
  --example-spec shared/fixtures/day26_hypotheses_a.json --example-matrix learner_outputs/mainline/day26/hypothesis_matrix_a.csv --example-report learner_outputs/mainline/day26/hypothesis_report_a.json \
  --challenge-spec shared/fixtures/day26_hypotheses_b.json --challenge-matrix learner_outputs/mainline/day26/hypothesis_matrix_b.csv --challenge-report learner_outputs/mainline/day26/hypothesis_report_b.json \
  --challenge-memo learner_outputs/mainline/day26/challenge_memo.md
```

口述 10 分：observable/metric 2；numerator/denominator 2；intervention/control 2；prediction/falsifier 2；alternative/causal/synthetic 边界 2。机器通过且 ≥8 进入 Day 27；预填结果、无 falsifier 或把 recovery 当唯一机制均不通过。

## 10. 证据复盘

- 已运行：A/B hypothesis schema、结果字段禁入、control 与 alternative tests。
- 未运行：真实 intervention、GPU、recovery rate 或 causal analysis。
- 可以主张：假设已转成可执行、可证伪的预注册表。
- 不能主张：任何瓶颈已被证实或推翻。

自测题（答案在 `shared/answer_keys/day26.md`）：

1. observable 与机制词有何区别？
2. 为什么 metric 必须保留分子/分母？
3. falsifier 能证明替代解释吗？
4. 为什么至少写两个 alternative？
5. 结果应写入 hypothesis spec 吗？
