# Mainline Day 70：最终 Capstone 与 Gate 8

今天不看答案，从 fresh clone 在隔离 workspace 复写 `analyze` 核心模块：总结 observation、重建四段 funnel 与配对四格、定位失败 episode、计算 repair delta，并现场把 minimum delta 从 0.10 改到 0.30 解释影响。机器 rehearsal 可本地验收；学习者的限时 live oral 不能由 Agent 代做。

## 1. 真实项目产物

- `core_module.py`：学习者独立复写的核心分析模块；
- A/B `exam.json`、oral memo 和 `gate8_report.json`；
- fresh-clone commit/命令/exit code 与关键表证据；
- Gate 8 三态结论，当前教材状态固定为 `NOT_PASSED`。

## 2. 当前卡点

一路照教程完成不等于拥有代码：可能只会复制已见输入，也可能把机器测试通过误当成能口述证据边界。最终 Gate 必须同时测迁移、定位、参数解释和现场表达。

本课的 B 卷改变 observation keys/shapes/dtype、episode 顺序和失败位置；checker 从内容重算，不接受改 ID 的 A 输出。答案区在提交前明确禁止查看。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day70/code/minimal_parameter_transfer.py
```

应看到同一 delta 在阈值 0.10 时通过、0.30 时不通过。若函数/测试不熟补 [F03](../../foundation_library/f03_modules_testing/README.md)；fresh clone 回看 [Day 67](../day67/README.md)，口述回看 [Day 69](../day69/README.md)。

## 4. 即时知识

- **transfer**：同一实现面对未见输入仍按契约工作。
- **code ownership**：能脱离逐步答案重建、解释和修改核心模块。
- **failure localization**：从 raw stage states 稳定定位首个失败 episode/阶段。
- **parameter sensitivity**：改变阈值，说明哪些派生判断变化、哪些 raw evidence 不变。
- **live oral**：现场沿 observation→funnel→pair→repair→boundary 口述。
- **Gate 8**：机器、fresh clone、限时、禁答案、口述与现场改参的联合验收。
- **three outcomes**：通过 / 补做 / 停止扩张；证据缺失不能强行通过。

## 5. 成熟材料处方

- **中文主材料（Python 官方，10 分钟）**：[unittest—单元测试框架](https://docs.python.org/zh-cn/3/library/unittest.html)。只读 test case、assertions 和命令行，理解 checker 是契约证据而非答案。
- **补充材料（Psychological Bulletin / PubMed，10 分钟）**：[The effect of testing versus restudy on retention: a meta-analytic review](https://pubmed.ncbi.nlm.nih.gov/25150680/)。只读摘要，理解“不看答案重建”为什么比单纯重读更能检验可提取知识。
- **锁定项目定位（10 分钟）**：[observation/action 第 280–305 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L280-L305) 与 [success 第 310–334 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L310-L334) 是 live oral 必须准确说出的真实链。

## 6. 最小实验

[minimal_parameter_transfer.py](code/minimal_parameter_transfer.py) 是完整 22 行代码：

```python
#!/usr/bin/env python3
"""最小例子：同一函数迁移到新输入，并解释阈值影响。"""

def compare(baseline, repair, minimum_delta):
    baseline_rate = sum(baseline) / len(baseline)
    repair_rate = sum(repair) / len(repair)
    delta = repair_rate - baseline_rate
    return {
        "delta": delta,
        "minimum_delta": minimum_delta,
        "meets_threshold": delta >= minimum_delta,
    }


new_input = {
    "baseline": [False, True, False, False],
    "repair": [True, True, False, False],
}

for threshold in (0.10, 0.30):
    result = compare(**new_input, minimum_delta=threshold)
    print(result)
```

长文件 [prepare_capstone.py](code/prepare_capstone.py) 只生成 starter；[check_day70.py](code/check_day70.py) 对 A/B、两阈值和口述 memo 重算语义。参考实现只在 `shared/answer_keys/day70_reference.py`。

## 7. 真实 VLA-Arena 操作

先在 fresh clone 根目录准备两卷，提交前不要打开 `shared/answer_keys/day70*`：

```bash
python3 mainline/day70/code/prepare_capstone.py --form A --output learner_outputs/mainline/day70/form_A
python3 mainline/day70/code/prepare_capstone.py --form B --output learner_outputs/mainline/day70/form_B
```

独立实现两个 workspace 的 `core_module.py`，填写 B oral memo，再运行第 9 节 checker。预期机器只说 rehearsal PASS、learner/live gate NOT_PASSED。正式 Gate 还需用锁定 upstream source 口述真实链；本课不启动 simulator/GPU。

## 8. 独立挑战

限时 90 分钟：fresh clone 后只看课程正文与锁定源码，不看答案区；先完成 A，再在 B 新输入上修复泛化问题。现场再把阈值 0.10 改为 0.30。B memo ≥420 字，原样包含 `fresh clone`、`without answer key`、`observation`、`four-stage funnel`、`paired transitions`、`failure episode`、`minimal repair`、`parameter change`、`threshold`、`evidence boundary`、`synthetic`、`cannot claim`、`live oral`。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day70.tests.test_day70_tools
.venv-day06/bin/python mainline/day70/code/check_day70.py \
  --example-workspace learner_outputs/mainline/day70/form_A \
  --challenge-workspace learner_outputs/mainline/day70/form_B \
  --report learner_outputs/mainline/day70/gate8_report.json
```

口述 10 分：真实调用链 2；observation/funnel 2；pair/failure 2；repair/改参 2；证据边界 2。机器通过、fresh clone 90 分钟内完成、未看答案、现场改参正确且口述 ≥8，才可由人类考官记录 Gate 8“通过”。代码错但可修为“补做”；答案依赖、无法迁移、越界主张或 formal evidence 缺失为“停止扩张”。Agent smoke test 永不把 `gate8_passed` 改成 true。

## 10. 证据复盘

- 已运行：A/B synthetic contract、参考实现、两阈值与 checker smoke。
- 静态源码事实：锁定 evaluator 的 observation→action→step→success 链。
- 未运行：学习者 fresh-clone 限时、live oral、VLA-Arena/MuJoCo/GPU/formal episodes。
- 可以主张：Gate 8 教材、陌生输入、机器契约、答案区和三态 rubric 完整。
- 不能主张：学习者通过 Gate 8、拥有代码、模型有效或课程学习已完成。

自测题（答案在 `shared/answer_keys/day70.md`）：

1. transfer 与复制示例有何区别？
2. funnel 的后续阶段 passed 怎样计算？
3. n01/n10 分别是什么？
4. 改 threshold 后哪些值不应变化？
5. 为什么机器 rehearsal PASS 仍不是 Gate 8 通过？
