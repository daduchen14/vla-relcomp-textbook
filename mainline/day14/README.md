# Mainline Day 14 / Gate 3：用最小 oracle 做可证伪诊断

今天把一个锁定任务的自然语言改写成结构化 `目标—起始关系—动作—终止关系—参照物`，与原指令做同 seed/init 配对。你会规划 language oracle、计算 recovery 与 damage、比较四段事件，并对陌生失败给出两个替代解释和一个单因素干预。当前只运行合成结果的免费分析，不伪造模型恢复。

## 1. 真实项目产物

- `learner_outputs/mainline/day14/oracle_manifest_a.csv`：3 个 control/language-oracle 配对计划；
- `learner_outputs/mainline/day14/synthetic_analysis_a.json`：合成 A 结果的成功与四段转移统计；
- `learner_outputs/mainline/day14/oracle_manifest_b.csv`、`synthetic_analysis_b.json`：换 task/试次后的独立挑战；
- `learner_outputs/mainline/day14/gate3_submission.json`、`gate3_oral.md`：陌生失败的事件读数、两个替代解释、干预与证伪预测。

Gate 3 通过表示你能设计诊断，不表示真实 oracle pilot 已运行或学习者已完成前 14 天。

## 2. 当前卡点

失败 episode 中 `contact/lift=true`、`approach/relation=false` 只能说明行为断在后半段，不能区分“没用对关系/reference”与“理解对但控制失败”。oracle 的作用是只给一个环节更明确的信息，看后续事件是否恢复。

但 oracle 使用 BDDL 真值，是刻意的信息泄漏。恢复只支持“这类额外信息能改变行为”，不能证明模型内部机制，也不能直接当部署方法。还必须报告 damage：干预可能修好原失败，却破坏原成功。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day14/code/minimal_recovery.py
```

应看到 `recovery=2/3=0.667` 与 `damage=1/2=0.500`。若分母仍混淆，补 [F02](../../foundation_library/f02_csv_json/README.md) 并手画 control/oracle 的 00/01/10/11 四格表。

## 4. 即时知识

- **oracle**：临时提供某个环节的正确/更明确答案，用恢复差定位瓶颈；不是最终作弊方案。
- **language oracle**：把 BDDL 真值组织成固定结构，只改变送给 policy 的 instruction text。
- **recovery**：control=0 的 pair 中 oracle=1 的比例；分母是 control failures。
- **damage**：control=1 的 pair 中 oracle=0 的比例；分母是 control successes。
- **阶段恢复**：对 contact/lift/approach/relation 各自构造相同四格表，观察首个系统性变化。
- **因果边界**：匹配干预缩小替代解释，但一次小 pilot 仍受随机执行、文本长度/token 分布等影响。
- **泄漏边界**：BDDL target/reference 真值只允许 `diagnostic_oracle_only_not_final_method`。

## 5. 成熟材料处方

- **中文主材料（12 分钟）**：[VLA-Arena 锁定《场景构建指南》§1.4 状态定义](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/docs/scene_construction_zh.md#14-状态定义)。只读 init/goal 如何提供 oracle 的结构字段；牢记这些字段不是 policy 默认可见输入。
- **因果补充（英文官方，15 分钟）**：[PyWhy DoWhy v0.13：Estimating Causal Effects](https://www.pywhy.org/dowhy/v0.13/user_guide/causal_tasks/estimating_causal_effects/index.html)。只读 treatment/outcome/estimand 的区分；本课 treatment 是 oracle arm，outcome 是 success/阶段事件，不需要安装 DoWhy。

## 6. 最小实验

[minimal_recovery.py](code/minimal_recovery.py) 是完整 14 行例子：

```python
#!/usr/bin/env python3
"""最小例子：恢复率只以原本失败的配对为分母。"""

PAIRS = [(0, 1), (0, 0), (1, 1), (1, 0), (0, 1)]
failed = [pair for pair in PAIRS if pair[0] == 0]
succeeded = [pair for pair in PAIRS if pair[0] == 1]

recovered = sum(control == 0 and oracle == 1 for control, oracle in PAIRS)
damaged = sum(control == 1 and oracle == 0 for control, oracle in PAIRS)
recovery_rate = recovered / len(failed) if failed else None
damage_rate = damaged / len(succeeded) if succeeded else None

print(f"recovery={recovered}/{len(failed)}={recovery_rate:.3f}")
print(f"damage={damaged}/{len(succeeded)}={damage_rate:.3f}")
```

分母为零时返回 `None`，不能写 0%；那代表当前样本无法估计该指标。

## 7. 真实 VLA-Arena 操作

先生成计划并用合成 fixture 验证分析器：

```bash
.venv-day06/bin/python mainline/day14/code/build_oracle_manifest.py \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --spec shared/fixtures/day14_oracle_spec_a.json \
  --output learner_outputs/mainline/day14/oracle_manifest_a.csv
.venv-day06/bin/python mainline/day14/code/analyze_oracle_results.py \
  --input shared/fixtures/day14_oracle_results_a.csv \
  --output learner_outputs/mainline/day14/synthetic_analysis_a.json
```

应看到 `3 control/oracle pairs planned ... real run=false`，以及合成分析 `pairs=5 recovery=2/3 damage=1/2`。计划与演示结果的 pair 数不同是刻意的：fixture 只测试统计代码，绝不是 manifest 的模型输出，禁止 join 后冒充 pilot。

[build_oracle_manifest.py](code/build_oracle_manifest.py) 从 Day 9 的 `target_initial_predicate/goal` 生成结构化文本；[analyze_oracle_results.py](code/analyze_oracle_results.py) 拒绝缺臂、非 0/1 和 success/relation 冲突。真实运行时，锁定 SmolVLA [`run_episode`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L225-L305) 的 `task_description` 是唯一改变字段；同一 pair 必须加载相同 initial state，并接 Day 12 logger。

真实 Gate 1/2 就绪后，先把 placeholder model/revision/config 换成冻结值，再执行极小 L0 pilot；L1/L2 只能用预登记的小验证，不能据结果挑 oracle 文本。若 pair 不完整不分析；若 recovery 高且 damage 高同时报告；若阶段变化不稳定，增加预登记重复而不是挑好看的 episode。

## 8. 独立挑战

1. 用 `day14_oracle_spec_b.json` 生成 B manifest，用 `day14_oracle_results_b.csv` 生成 B analysis。
2. 复制 `mainline/day14/config/gate3_submission_template.json` 到 learner output，再读取 `day14_gate3_case.json` 独立填写。必须准确抄四事件，给两个各 ≥30 字的替代解释，只选 language 或 visual oracle 中一个，固定至少 6 个字段，并写一个 ≥40 字 falsifier。
3. 写 ≥180 字 `gate3_oral.md`，必须出现 `recovery`、`damage`、`alternative`、`leakage`、`cannot prove`，用两分钟口述证据边界。正文不提供 case 的选择答案。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day14.tests.test_day14_tools
.venv-day06/bin/python mainline/day14/code/check_day14.py \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --example-spec shared/fixtures/day14_oracle_spec_a.json \
  --example-manifest learner_outputs/mainline/day14/oracle_manifest_a.csv \
  --example-results shared/fixtures/day14_oracle_results_a.csv \
  --example-analysis learner_outputs/mainline/day14/synthetic_analysis_a.json \
  --challenge-spec shared/fixtures/day14_oracle_spec_b.json \
  --challenge-manifest learner_outputs/mainline/day14/oracle_manifest_b.csv \
  --challenge-results shared/fixtures/day14_oracle_results_b.csv \
  --challenge-analysis learner_outputs/mainline/day14/synthetic_analysis_b.json \
  --gate-case shared/fixtures/day14_gate3_case.json \
  --gate-submission learner_outputs/mainline/day14/gate3_submission.json \
  --oral-note learner_outputs/mainline/day14/gate3_oral.md
```

Gate 3 口述 10 分：四段证据 2；两个替代解释 2；单因素干预/固定项 2；预测与 falsifier 2；leakage/因果边界 2。机器通过且 ≥8 才算学习者通过 Gate 3；教材状态仍只表示“已编写”。用 oracle 真值训练最终方法、只报 recovery、把恢复说成内部机制证明或看结果改干预，均不通过。

## 10. 证据复盘

- 已运行：A/B 计划生成、两个陌生合成结果的四格重算、缺臂/冲突拒绝、Gate 3 结构验收。
- 未运行：任何 checkpoint 的 oracle episode；placeholder 未冻结；合成 recovery/damage 不是研究结论。
- 可以主张：language oracle 改变字段、特权来源、配对统计和 Gate 判断规则已编码。
- 不能主张：oracle 真实恢复模型、语言是主要瓶颈、结构化文本可部署，或 Gate 3 学习者已通过。

自测题（答案在 `shared/answer_keys/day14.md`）：

1. recovery 与 damage 的分母分别是什么？
2. language oracle 使用了哪些 privileged information？
3. oracle 恢复成功为什么不能证明模型内部理解？
4. control/oracle pair 必须固定哪些字段？
5. Gate case 的四段模式支持哪些行为描述，又留下哪两个替代解释？
