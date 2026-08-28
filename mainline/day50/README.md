# Mainline Day 50：Gate 6——继续、补做或停止扩张

今天从 Day 46–49 的原始输入重建多 seed、L0 retention、L1/L2 与消融结论，再执行 Gate 6。A/B 的 synthetic 数值虽然满足演练阈值，但正式 checkpoints、GPU runs 和 evaluator records 均不存在，因此唯一合格结论是“停止扩张”；学习者 Gate 状态仍为 `REHEARSAL_ONLY_NOT_PASSED`。

## 1. 真实项目产物

- `gate6_report_a.json`：全部 source hashes、允许/禁止材料、重建指标、criteria 与三态结论；
- 明确的 `next_action` 和 evidence boundary；
- B 陌生原始输入的报告与 `challenge_memo.md`。

## 2. 当前卡点

漂亮的 fixture 数值最容易诱发越界结论。Gate 不能只问“指标过线吗”，还要先问“这些指标来自正式 checkpoint 和锁定 evaluator 吗”。直接读汇总表也可能掩盖 cherry-picking 或阈值变化。

本课从原始 config/fixtures 现场调用 Day 46–49 分析器。formal evidence 不完整时，不论 synthetic 指标多好都不能通过；报告必须同时给出“通过 / 补做 / 停止扩张”语义和下一步。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day50/code/minimal_gate_decision.py
```

应依次看到通过、补做、停止扩张。若条件分支不熟补 [F03](../../foundation_library/f03_modules_testing/README.md)；四类证据回看 [Day 46](../day46/README.md) 至 [Day 49](../day49/README.md)。

## 4. 即时知识

- **Gate**：在扩大实验或结论前执行的硬验收，不是进度庆祝。
- **evidence eligibility**：先判断来源是否为正式、锁定、可重建证据。
- **raw rebuild**：从原始 ledger/config 重新计算，不信任手填摘要。
- **通过**：证据资格和全部冻结条件都满足。
- **补做**：已有 formal 证据基础，但存在按既定协议可补的缺项。
- **停止扩张**：证据资格不足或关键条件不允许继续扩大主张。
- **negative result**：允许接受“不改善”，不能靠新增实验无限追逐正结果。
- **learner status**：教材/演练文件存在不等于学习者通过 Gate。

## 5. 成熟材料处方

- **中文主材料（Open for Science，10 分钟）**：[早期职业研究人员开放科学指南（中文 PDF）](https://open4science.cn/static/ECR_OpenScience_Guide_CN.pdf)。重点看提前冻结问题、方法和分析如何减少结果后决策。
- **补充材料（OSF 官方，10 分钟）**：[Welcome to Registrations](https://help.osf.io/article/330-welcome-to-registrations)。只读 registration 如何形成不可变、带时间戳的研究计划，以及 embargo 的含义。
- **锁定项目定位（8 分钟）**：[SmolVLA evaluator Args 第 79–139 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L79-L139) 固定 level、trials、initial-state、seed 与 replacement；[success 判定第 310–334 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L310-L334) 是正式原始记录必须追溯的终点。

## 6. 最小实验

[minimal_gate_decision.py](code/minimal_gate_decision.py) 是完整 20 行代码：

```python
#!/usr/bin/env python3
"""最小例子：证据完整性优先于漂亮指标。"""

cases = [
    {"name": "complete_and_pass", "formal": True,
     "l0": True, "ood": True, "ablation": True},
    {"name": "recoverable_gap", "formal": True,
     "l0": True, "ood": False, "ablation": True},
    {"name": "synthetic_only", "formal": False,
     "l0": True, "ood": True, "ablation": True},
]

for case in cases:
    if not case["formal"]:
        decision = "停止扩张"
    elif all(case[key] for key in ("l0", "ood", "ablation")):
        decision = "通过"
    else:
        decision = "补做"
    print(f"{case['name']} -> {decision}")
```

长文件 [run_gate6.py](code/run_gate6.py) 重点阅读四个分析器重建、formal evidence 优先级、三态决策和 status 分离。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day50/code/run_gate6.py \
  --split shared/fixtures/day45_split_a.json --base-plan mainline/day45/config/seed1_plan_a.json --repeat-plan mainline/day46/config/repeat_plan_a.json \
  --stability shared/fixtures/day44_stability_a.json --candidate mainline/day44/config/candidate_recipe_a.json \
  --l0-input shared/fixtures/day47_l0_retention_a.json --l0-config mainline/day47/config/retention_config_a.json \
  --ood-input shared/fixtures/day48_ood_a.json --ood-config mainline/day48/config/ood_analysis_a.json \
  --ablation-input shared/fixtures/day49_ablation_a.json --ablation-config mainline/day49/config/ablation_config_a.json \
  --report learner_outputs/mainline/day50/gate6_report_a.json
```

应输出“停止扩张 / FORMAL_EVIDENCE_MISSING / learner_passed=false”。未来只有把各 synthetic/planned source 换成授权运行产生的 checkpoint manifests、逐 episode evaluator records 和实际 resource ledgers，且 hashes/thresholds 不变，才可重跑 Gate。当前结论不是项目失败，而是禁止越过证据缺口。

## 8. 独立挑战

使用 B 的 Day 44–49 全套陌生输入重建 Gate。写 ≥280 字 memo，必须原样包含 `Gate 6`、`raw inputs`、`rebuild`、`L0 retention`、`L1/L2`、`multi-seed`、`ablation`、`cost matched`、`formal evidence`、`synthetic`、`通过`、`补做`、`停止扩张`、`learner status`、`next action`。不得复制 A hashes/metrics。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day50.tests.test_day50_tools
.venv-day06/bin/python mainline/day50/code/check_day50.py \
  --example-split shared/fixtures/day45_split_a.json --example-base-plan mainline/day45/config/seed1_plan_a.json --example-repeat-plan mainline/day46/config/repeat_plan_a.json --example-stability shared/fixtures/day44_stability_a.json --example-candidate mainline/day44/config/candidate_recipe_a.json \
  --example-l0-input shared/fixtures/day47_l0_retention_a.json --example-l0-config mainline/day47/config/retention_config_a.json --example-ood-input shared/fixtures/day48_ood_a.json --example-ood-config mainline/day48/config/ood_analysis_a.json --example-ablation-input shared/fixtures/day49_ablation_a.json --example-ablation-config mainline/day49/config/ablation_config_a.json --example-report learner_outputs/mainline/day50/gate6_report_a.json \
  --challenge-split shared/fixtures/day45_split_b.json --challenge-base-plan mainline/day45/config/seed1_plan_b.json --challenge-repeat-plan mainline/day46/config/repeat_plan_b.json --challenge-stability shared/fixtures/day44_stability_b.json --challenge-candidate mainline/day44/config/candidate_recipe_b.json \
  --challenge-l0-input shared/fixtures/day47_l0_retention_b.json --challenge-l0-config mainline/day47/config/retention_config_b.json --challenge-ood-input shared/fixtures/day48_ood_b.json --challenge-ood-config mainline/day48/config/ood_analysis_b.json --challenge-ablation-input shared/fixtures/day49_ablation_b.json --challenge-ablation-config mainline/day49/config/ablation_config_b.json --challenge-report learner_outputs/mainline/day50/gate6_report_b.json \
  --challenge-memo learner_outputs/mainline/day50/challenge_memo.md
```

口述 10 分：raw rebuild 2；四类 criteria 2；证据资格 2；三态语义 2；learner/project 边界 2。机器通过且 ≥8 才完成 Day 50 教学；真实 Gate 6 仍须 formal evidence。复制摘要、挑 seed、事后阈值、把 synthetic 当正式或记录 Gate passed 均不通过。

## 10. 证据复盘

- 已运行：A/B 原始 synthetic/planned inputs 的多模块重建、hash 与三态 Gate 演练。
- 静态源码事实：锁定 evaluator 的评测配置与 success 终点。
- 未运行：formal checkpoints、GPU、VLA-Arena L0/L1/L2 和真实消融。
- 可以主张：Gate 会在数值达标但证据不合格时强制停止扩张。
- 不能主张：Gate 6 已通过、repair 有效果、阶段 6 实验可以启动。

自测题（答案在 `shared/answer_keys/day50.md`）：

1. 为什么 synthetic 指标全达标仍必须停止扩张？
2. “补做”和“停止扩张”如何区分？
3. 为什么 Gate 必须从 raw inputs rebuild？
4. Gate 6 通过需要哪些类别的正式证据？
5. Day 50 教材完成是否等于 learner Gate 6 通过？
