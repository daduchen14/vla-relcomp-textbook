# Mainline Day 64：写问题、方法和实验设置

今天把冻结 protocol 变成可审阅的 methods draft。研究问题必须落到任务、条件、episode、initial state、seed、配对键、测量和分析；observation、action、success、failure 都给出代码级操作定义。当前是 synthetic 教学稿，不夹带任何结果。

## 1. 真实项目产物

- `methods_draft.md`：九节问题/方法/实验设置；
- `manifest.json`：protocol、draft、锁定 commit 和“无结果泄漏”证据；
- B 新 protocol 的独立 methods draft 与 memo。

## 2. 当前卡点

“评测模型泛化”不是可复现方法：读者不知道 observation 是什么、success 怎样判断、哪些初始状态被配对、何时停止。反过来在看到结果后补写 seed 或排除规则，也会让 Methods 合法化事后选择。

本课从结构化 protocol 单向生成正文。`result_claims` 必须为空；方法稿只描述计划和边界，不提前暗示 repair 有效。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day64/code/minimal_operational_definition.py
```

应看到 observation/action/success 均为 `operational=True`。若字典与字符串检查不熟补 [F03](../../foundation_library/f03_modules_testing/README.md)；真实调用链回看 [Day 3](../day03/README.md)，冻结协议回看 [Day 51](../day51/README.md)。

## 4. 即时知识

- **research question**：能由冻结比较、测量和分析回答的问题。
- **operational definition**：概念在代码、记录和阈值中如何被判定。
- **system boundary**：哪些组件与输入属于研究对象，哪些在范围外。
- **experimental unit**：独立产生一个结果的单位；这里首先是 episode/pair，不是日志行。
- **condition**：baseline、deployable repair 与 diagnostic oracle 必须分栏。
- **stopping rule**：看结果前规定运行何时结束。
- **methods/results separation**：方法描述怎么得到证据，结果描述证据显示什么。

## 5. 成熟材料处方

- **中文主材料（开放科学促进联合体，12 分钟）**：[中国早期职业研究人员开放科学技术指南](https://open4science.cn/static/ECR_OpenScience_Guide_CN.pdf)。只读预注册、研究材料和代码共享部分，把计划、偏离和最终报告分开。
- **补充材料（APA，10 分钟）**：[Journal Article Reporting Standards—Quantitative Research](https://apastyle.apa.org/jars/quantitative)。只看 quantitative design/reporting 表，检查参与单位、测量、条件、排除、分析和数据可得性；机器人任务按等价字段迁移。
- **锁定项目定位（10 分钟）**：[Args 第 79–139 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L79-L139) 固定 suite/level/trials/state/seed/replacement；[observation→step→success 第 280–334 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L280-L334) 提供四个操作定义的真实代码锚点。

## 6. 最小实验

[minimal_operational_definition.py](code/minimal_operational_definition.py) 是完整 18 行代码：

```python
#!/usr/bin/env python3
"""最小例子：把抽象问题改写为可执行的操作定义。"""

definitions = {
    "observation": "进入 policy.select_action 的图像、状态与任务字典",
    "action": "policy 输出并传给 env.step 的数值向量",
    "success": "episode done 且 is_success_done 为真，并满足 safety cost 条件",
}

required_terms = {
    "observation": ("policy.select_action", "字典"),
    "action": ("env.step", "向量"),
    "success": ("is_success_done", "cost"),
}

for name, definition in definitions.items():
    complete = all(term in definition for term in required_terms[name])
    print(f"{name}: operational={complete}")
```

长文件 [build_methods_draft.py](code/build_methods_draft.py) 校验 protocol、禁止结果泄漏并生成九节正文和 manifest。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day64/code/build_methods_draft.py \
  --input shared/fixtures/day64_protocol_a.json --config mainline/day64/config/methods_a.json \
  --output-dir learner_outputs/mainline/day64/methods_a
```

应报告 `sections=9 result_claims=false formal=false`。未来正式稿要把 synthetic spec 替换为 Day 51 冻结 manifest 与 Day 52–60 实际执行记录；若实际偏离 seed/state/stopping rule，单列 deviation，不能静默改写原方法。

## 8. 独立挑战

用 B protocol/config 生成新稿；不要复制 A 句子。写 ≥280 字 memo，原样包含 `research question`、`operational definition`、`system boundary`、`task suite`、`condition`、`episode protocol`、`initial state`、`pair key`、`frozen seed`、`analysis plan`、`provenance`、`synthetic`、`cannot claim`，说明它怎样阻止结果后决策。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day64.tests.test_day64_tools
.venv-day06/bin/python mainline/day64/code/check_day64.py \
  --example-input shared/fixtures/day64_protocol_a.json --example-config mainline/day64/config/methods_a.json --example-output-dir learner_outputs/mainline/day64/methods_a \
  --challenge-input shared/fixtures/day64_protocol_b.json --challenge-config mainline/day64/config/methods_b.json --challenge-output-dir learner_outputs/mainline/day64/methods_b \
  --challenge-memo learner_outputs/mainline/day64/challenge_memo.md
```

口述 10 分：问题/边界 2；操作定义 2；任务/条件 2；episode/配对/seed 2；分析/provenance 2。机器通过且 ≥8 才完成 Day 64；夹带结果、漏停止规则、混淆 oracle、版本漂移或 synthetic 冒充正式方法均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic protocol 到 methods/manifest 的逐字节重建。
- 静态源码事实：锁定 evaluator 的 Args 与 observation→action→success 路径。
- 未运行：正式实验、VLA-Arena、GPU、checkpoint 与 protocol deviations。
- 可以主张：draft 覆盖九节、四个操作定义且没有 result claims。
- 不能主张：研究已按此执行、repair 有效或 Gate 7 已通过。

自测题（答案在 `shared/answer_keys/day64.md`）：

1. research question 与宽泛目标有何区别？
2. 什么是 operational definition？
3. 哪些设置必须在看结果前冻结？
4. oracle 为什么不能混入 deployable condition？
5. synthetic methods draft 能否证明真实执行？
