# Mainline Day 38：实现一个可回退的关系规范化模块

今天只实现 Day 36 A 卷选中的教学候选：一个纯函数把 L0 结构标签转成固定 `TARGET | START | ACTION | GOAL` 指令。它不改 VLA-Arena evaluator、图像、动作或模型；未知关系和非 L0 输入直接失败。这个窄接口使后续训练样本、回归测试和一键回退都有明确边界。

## 1. 真实项目产物

- [relation_normalizer.py](code/relation_normalizer.py)：单一 repair module；
- `normalized_a.csv`、`normalizer_report_a.json`：A 输入、规范化输出、module version 与输入 hash；
- B 新输入的同类产物与 `challenge_memo.md`。

## 2. 当前卡点

把 normalization 散落在 dataset、trainer 和 evaluator 三处，会出现不同 token 规则且难以回退。默默把未知关系映射为 `other` 又会污染标签。直接修改 upstream evaluator 还混入无关差异。

本课把修复压成 `normalize_relation_instruction(mapping) -> str`：只接受 level 0 的 target/start/goal 标签，固定关系词表与字段顺序，不修改输入。`NextTo`/`Between` 在这里是 Day 9 从任务语言/区域语义得到的 canonical label；它们不冒充锁定 `base_predicates.py` 中不存在的同名 evaluator class。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day38/code/minimal_module_call.py
```

应看到规范化文本与 `input_unchanged=True`。若函数/异常卡住补 [F03](../../foundation_library/f03_modules_testing/README.md)；若 L0 边界不清楚回看 [Day 37](../day37/README.md)。

## 4. 即时知识

- **single repair module**：只改变一个接口/因素，便于归因和消融。
- **canonical relation**：为同一语义选择唯一 token，如 `NextTo→next_to`。
- **pure function**：不修改输入/全局状态，相同输入得到相同输出。
- **fail closed**：缺字段、未知关系、非 L0 输入立即报错，不猜测。
- **module version**：输出记录 `relation-normalizer-v1`，防止规则静默变化。
- **regression test**：固定已知行为与错误路径，后续改动不能悄悄破坏接口。
- **adapter boundary**：未来只在构建训练 instruction 的一个入口调用，不散布到 upstream。

## 5. 成熟材料处方

- **中文主材料（6 分钟）**：[Python `Mapping` 官方中文文档](https://docs.python.org/zh-cn/3/library/collections.abc.html#collections.abc.Mapping)。理解函数为何只要求键值读取，不绑定具体 `dict` 实现。
- **补充材料（8 分钟）**：[Python 异常处理官方中文教程](https://docs.python.org/zh-cn/3/tutorial/errors.html)。只读主动 `raise` 与捕获特定异常；未知关系要携带原 token。
- **锁定项目定位（10 分钟）**：[L0 示例 BDDL 第 141–158 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/bddl_files/extrapolation_preposition_combinations/level_0/pick_the_tomato_next_to_the_cereal_and_place_it_on_the_porcelain_bowl_between_the_cabinet_and_the_cutting_board.bddl#L141-L158) 用区域上的 `On` 编码“next to”等初态语义，而 goal 是真实 `(On target reference)`；规范化模块必须使用 Day 9 的结构任务标签，不能把字符串硬猜成 evaluator predicate。

## 6. 最小实验

[minimal_module_call.py](code/minimal_module_call.py) 是完整 19 行代码：

```python
#!/usr/bin/env python3
"""最小例子：用一个 L0 结构样本调用规范化模块。"""

try:
    from .relation_normalizer import normalize_relation_instruction
except ImportError:
    from relation_normalizer import normalize_relation_instruction

example = {
    "level": "0",
    "target_object_id": "tomato_1",
    "start_relation": "NextTo",
    "start_reference_ids": "cereal_1",
    "goal_relation": "On",
    "goal_reference_ids": "bowl_1",
}
before = dict(example)
print(normalize_relation_instruction(example))
print(f"input_unchanged={example == before}")
```

长文件 [relation_normalizer.py](code/relation_normalizer.py) 依次阅读词表、必填字段、L0 gate、未知关系和返回模板；这是完整实现，不是伪代码。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day38/code/apply_relation_normalizer.py \
  --input shared/fixtures/day38_relation_examples_a.csv \
  --output learner_outputs/mainline/day38/normalized_a.csv \
  --report learner_outputs/mainline/day38/normalizer_report_a.json
```

应看到 `rows=4 module=relation-normalizer-v1 upstream_modified=false model_run=false`。

真实项目若 formal Day 36 选择此修复，adapter 只读取 Day 37 L0 manifest 关联的结构标签，生成新增训练 instruction；保存 raw/normalized pair 与 module version。evaluator 保持锁定版本，control 仍使用原 instruction。若未选中该候选或遇到未知关系，停止而不是扩大词表。当前没有模型 forward、训练、GPU 或 upstream 改动。

## 8. 独立挑战

用 B 输入生成新 output/report。写 ≥240 字 memo，必须原样包含 `single repair module`、`L0`、`TARGET`、`START`、`ACTION`、`GOAL`、`canonical relation`、`pure function`、`input unchanged`、`unknown relation`、`regression test`、`upstream`、`synthetic`、`model run`。解释模块唯一职责、三个失败条件与回退方法。正文不给 B 输出文本。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day38.tests.test_day38_tools
.venv-day06/bin/python mainline/day38/code/check_day38.py \
  --example-input shared/fixtures/day38_relation_examples_a.csv --example-output learner_outputs/mainline/day38/normalized_a.csv --example-report learner_outputs/mainline/day38/normalizer_report_a.json \
  --challenge-input shared/fixtures/day38_relation_examples_b.csv --challenge-output learner_outputs/mainline/day38/normalized_b.csv --challenge-report learner_outputs/mainline/day38/normalizer_report_b.json \
  --challenge-memo learner_outputs/mainline/day38/challenge_memo.md
```

口述 10 分：单一职责 2；L0/词表 2；纯函数/失败关闭 2；版本与回归 2；upstream/synthetic 边界 2。机器通过且 ≥8 进入 Day 39；非 L0 输入、未知关系猜测、原地修改、散改 evaluator 或把字符串转换说成模型修复均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic L0 结构样本、四种 canonical relation、输入不变、非 L0 拒绝与严格重建。
- 静态源码事实：锁定示例通过命名区域表达部分任务语言关系，goal 使用官方 predicate。
- 未运行：真实 L0 dataset adapter、模型 forward/train、GPU 与行为评测。
- 可以主张：单一模块接口、版本、错误路径和批处理器可用。
- 不能主张：模型已学会关系、真实成功率改善或该候选已由 formal evidence 选中。

自测题（答案在 `shared/answer_keys/day38.md`）：

1. single repair module 的唯一职责是什么？
2. canonical relation 解决什么，不解决什么？
3. pure function 为什么有利于回退？
4. unknown relation 为什么必须失败关闭？
5. regression test 通过是否等于 model run 有效？
