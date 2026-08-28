# Mainline Day 66：完成相关工作、限制、伦理和负结果报告

今天把 Day 64–65 扩成完整报告骨架：related work 说明继承与区别；limitations 按 simulator、task suite、checkpoint、统计不确定性和 physical robot 分层；ethics 覆盖 safety、misuse、resource、license、privacy；negative result 原样保留。仍是 synthetic 教学稿。

## 1. 真实项目产物

- `complete_report.md`：摘要到参考文献共 11 节；
- `manifest.json`：章节、限制/伦理维度、引用与边界；
- B 新 dossier 的完整报告与 memo。

## 2. 当前卡点

Methods+Results 并不等于完整论文。没有 related work 会夸大新颖性；只写一句“仿真有限”会漏掉 checkpoint、任务覆盖与实体机器人外推；只把 ethics 写成人类受试者隐私，又会漏掉机器人安全、误用、许可证和算力资源。

本课用结构契约强制这些内容出现，并让结论沿 scope ladder 停在现有证据层级。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day66/code/minimal_scope_ladder.py
```

应看到 synthetic fixture 不能支持 physical robots，`allowed=False`。若列表索引不熟补 [F03](../../foundation_library/f03_modules_testing/README.md)；方法与结果回看 [Day 64](../day64/README.md)、[Day 65](../day65/README.md)。

## 4. 即时知识

- **related work**：说明已有工作提供什么、本项目继承什么、差异在哪里。
- **scope**：证据直接覆盖的对象与条件集合。
- **external validity**：结论向新任务、模型、环境或实体平台迁移的程度。
- **limitation**：会改变结论解释或适用范围的已知约束。
- **ethics/safety**：不仅是隐私，还包括误用、部署安全、资源和许可证。
- **negative result**：未达预期或仍不确定的结果；不因叙事不方便而删除。
- **scope ladder**：fixture→simulator→held-out→new checkpoint→physical robot，不能越级。

## 5. 成熟材料处方

- **中文主材料（开放科学促进联合体，12 分钟）**：[中国早期职业研究人员开放科学技术指南（PDF）](https://open4science.cn/static/ECR_OpenScience_Guide_CN.pdf)。只读科研数据、代码共享与预注册部分，检查结果可追溯、计划偏离可见且不隐藏不利结果。
- **补充材料（VLA-Arena 论文，12 分钟）**：[VLA-Arena: An Open-Source Framework for Benchmarking VLA Models](https://arxiv.org/abs/2512.22539)。只读摘要、任务层级和评测范围，用来写“继承什么”，不是覆盖锁定源码事实。
- **锁定项目定位（8 分钟）**：[README 第 18–20、95 行起](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/README.md#L18-L20) 描述框架范围；[evaluator 第 280–334 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L280-L334) 才是本报告操作定义的代码证据。

## 6. 最小实验

[minimal_scope_ladder.py](code/minimal_scope_ladder.py) 是完整 20 行代码：

```python
#!/usr/bin/env python3
"""最小例子：结论不能跨越证据的外推层级。"""

scope_ladder = [
    "synthetic fixture",
    "locked simulator episodes",
    "held-out simulator tasks",
    "new VLA checkpoints",
    "physical robots",
]
evidence_scope = "synthetic fixture"
requested_claim = "physical robots"

evidence_level = scope_ladder.index(evidence_scope)
claim_level = scope_ladder.index(requested_claim)
allowed = claim_level <= evidence_level

print(f"evidence_scope={evidence_scope}")
print(f"requested_claim={requested_claim}")
print(f"allowed={allowed}")
```

长文件 [build_complete_report.py](code/build_complete_report.py) 检查章节顺序、五类限制、五类伦理、负结果和参考文献。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day66/code/build_complete_report.py \
  --input shared/fixtures/day66_dossier_a.json --config mainline/day66/config/report_a.json \
  --output-dir learner_outputs/mainline/day66/report_a
```

应报告 `sections=11 limitations=5 ethics=5 formal=false`。正式报告必须把 Day 64/65 教学段替换为 hash-matched 正式 methods/results，并按真实未运行、失败和偏离改写限制；不允许只删除 synthetic 标签。

## 8. 独立挑战

用 B dossier/config 生成新报告。写 ≥300 字 memo，原样包含 `related work`、`scope`、`simulator`、`task suite`、`checkpoint`、`physical robot`、`statistical uncertainty`、`ethics`、`safety`、`misuse`、`resource`、`license`、`privacy`、`negative result`、`synthetic`、`cannot claim`。不复制 A 段落。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day66.tests.test_day66_tools
.venv-day06/bin/python mainline/day66/code/check_day66.py \
  --example-input shared/fixtures/day66_dossier_a.json --example-config mainline/day66/config/report_a.json --example-output-dir learner_outputs/mainline/day66/report_a \
  --challenge-input shared/fixtures/day66_dossier_b.json --challenge-config mainline/day66/config/report_b.json --challenge-output-dir learner_outputs/mainline/day66/report_b \
  --challenge-memo learner_outputs/mainline/day66/challenge_memo.md
```

口述 10 分：related work 2；五类限制 2；五类伦理 2；负结果 2；scope/引用 2。机器通过且 ≥8 才完成 Day 66；泛泛限制、仿真安全当认证、隐去失败/负结果、无许可证/资源边界或冒充正式报告均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic dossier 到 complete report/manifest 的逐字节重建。
- 静态源码事实：锁定 README 的框架范围和 evaluator 执行边界。
- 未运行：正式实验、VLA-Arena/GPU、physical robot 与真实安全评估。
- 可以主张：报告骨架强制相关工作、五类限制/伦理、负结果和引用完整。
- 不能主张：repair 有效、实体安全、跨 checkpoint 泛化或论文已完成实证。

自测题（答案在 `shared/answer_keys/day66.md`）：

1. related work 不能只做什么？
2. 外推限制至少包含哪五类？
3. simulator safety 能否认证部署安全？
4. negative result 为什么必须保留？
5. complete teaching report 是否等于实验完成？
