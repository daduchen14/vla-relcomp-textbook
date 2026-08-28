# Mainline Day 13：构造第一组只改一个因素的匹配 pair

今天先做最保守的一组反事实：同一锁定 task、同一 goal 和同一精确初态，只改变指令的表面表达。你会得到两行 pair manifest、稳定 `pair_id` 和结构校验报告；不运行模型，也不把这组语言改写夸大成“关系组合反事实”。批量关系最小对在 Day 31 再做。

## 1. 真实项目产物

- `learner_outputs/mainline/day13/pair_a.csv`：同一 L0T0 的原指令 A 与语义拟等价改写 B；
- `learner_outputs/mainline/day13/validation_a.json`：唯一变化字段、固定字段数和人工语义审查状态；
- `learner_outputs/mainline/day13/pair_b.csv`：换成 L1T1 与新 seed/init 的独立挑战；
- `learner_outputs/mainline/day13/challenge_defense.md`：为什么它是匹配 pair、机器又不能证明什么。

产物是**计划清单而非模型结果**。两臂都写 `real_environment_run=false`，在 Gate 1/2 未满足时不伪造成功率。

## 2. 当前卡点

如果 A 用 seed 7、B 用 seed 8，动作差异可能来自初态；如果改指令时顺便换 target 或 goal，就无法把行为翻转归因于语言表述。最隐蔽的错误是“seed 相同所以状态一定相同”：两个 reset 的随机调用顺序仍可能不同，必须加载同一个 `init_state_index`。

另一方面，结构完全相同也不自动证明两句英文语义等价。validator 能检查字段，不能替人判断“drawer top layer”和“cabinet top”是否被偷换。因此 manifest 先标 `pending_human_review`，真实执行前必须对照 BDDL 手工审阅。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day13/code/minimal_matched_pair.py
```

应看到 `fixed=['seed', 'init_state', 'goal'] changed=['instruction']`。若 assertion、函数或测试卡住补 [F03](../../foundation_library/f03_modules_testing/README.md)；若 CSV/JSON 卡住补 [F02](../../foundation_library/f02_csv_json/README.md)。

## 4. 即时知识

- **实验单位**：本课是同一个 task × seed × init state；A/B 必须能由 `pair_id` 找回。
- **处理变量**：主动改变、希望解释效果的字段；本课只有 `instruction_text`。
- **控制变量**：task/BDDL/goal、对象、模型 revision、推理配置、seed/init 等必须相同。
- **精确初态**：seed 生成随机序列，`init_state_index` 指向实际加载的状态；匹配实验两者都固定。
- **配对**：比较同一实验单位的 A/B，而不是把两堆不相干 episode 当独立样本。
- **语义等价边界**：字符串不同是机器事实；“含义未变”是需要人工对照 goal/初态的设计判断。

## 5. 成熟材料处方

- **中文主材料（10 分钟）**：[Python 官方 `csv` 文档](https://docs.python.org/zh-cn/3/library/csv.html)。只读 `DictReader/DictWriter` 与 `newline=''`，对应本日 manifest 的可逆读写。
- **实验设计补充（英文官方，15 分钟）**：[NIST/SEMATECH e-Handbook §5.3.3.2 Randomized block designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm)。只读“同一 block 内比较 treatments”的动机；把本课的 task×init 看作 block，把 A/B instruction 看作两种 treatment，不扩展到公式推导。

## 6. 最小实验

[minimal_matched_pair.py](code/minimal_matched_pair.py) 是完整 14 行例子：

```python
#!/usr/bin/env python3
"""最小例子：先比较固定列，再确认唯一处理变量。"""

A = {"seed": 7, "init_state": 2, "goal": "On(tomato_3,bowl_3)",
     "instruction": "Put the selected tomato on the bowl."}
B = {"seed": 7, "init_state": 2, "goal": "On(tomato_3,bowl_3)",
     "instruction": "Place the chosen tomato atop the bowl."}

fixed_fields = ("seed", "init_state", "goal")
changed_fields = [key for key in A if A[key] != B[key]]

assert all(A[key] == B[key] for key in fixed_fields)
assert changed_fields == ["instruction"]
print(f"PASS: fixed={list(fixed_fields)} changed={changed_fields}")
```

`changed_fields` 只是教学缩影；真实 validator 还验证 task table、hash、pair ID 与两行 schema。

## 7. 真实 VLA-Arena 操作

先复用 Day 9 锁定 task table 生成并校验 A：

```bash
.venv-day06/bin/python mainline/day13/code/build_pair_manifest.py \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --spec shared/fixtures/day13_pair_spec_a.json \
  --output learner_outputs/mainline/day13/pair_a.csv
.venv-day06/bin/python mainline/day13/code/validate_pair_manifest.py \
  --manifest learner_outputs/mainline/day13/pair_a.csv \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --report learner_outputs/mainline/day13/validation_a.json
```

应看到同一 `pair-...` 的 two matched arms，然后 `only changed instruction_text; semantic review pending`。打开 CSV，A 的 language/goal/target/reference 必须与锁定表一致；B 只有 instruction 不同。`inference_config_sha256` 和 model revision 目前是明确 placeholder，真实 pilot 前必须由 Gate 2 选定值替换并重新生成，不能把 placeholder 行送入 evaluator。

长文件 [build_pair_manifest.py](code/build_pair_manifest.py) 的阅读顺序是 `_task → pair_id → build → write_csv`；[validate_pair_manifest.py](code/validate_pair_manifest.py) 会把 CSV 读回后重新比对锁定任务，不只检查文件存在。

未来真实运行时，对同一 pair 的两臂加载完全相同的 initial state，只把当前行的 `instruction_text` 传给 evaluator。锁定 SmolVLA 的 [`run_episode`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L225-L305) 已把 `task_description` 放入 policy observation；同一函数也通过 `env.set_init_state(initial_state)` 恢复指定状态。不要改 BDDL goal 来实现本日 surface pair。

若 pair ID 校验失败，先检查是否手改 CSV；若 fixed-field 报错，逐列比较 init/model/config；若 A 不锚定 task table，重跑 Day 9；若语义拿不准，保持 pending 并找人逐词对照，不要用模型输出反推“哪种改写更合理”。

## 8. 独立挑战

换用 `shared/fixtures/day13_pair_spec_b.json` 生成 `pair_b.csv`；它选择 L1T1、新 seed/init、不同指令与不同 config hash，不能复制 A 后改 `pair_id`。

写至少 140 字 `challenge_defense.md`，必须出现 `pair_id`、`seed`、`init_state`、`instruction`、`semantic`、`human review`。列出唯一处理变量和至少六个固定字段，解释 seed 为什么不能替代精确初态，以及机器为何无法批准语义等价。正文不展示 B 的 pair ID 或 run order。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python mainline/day13/code/check_day13.py \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --example-spec shared/fixtures/day13_pair_spec_a.json \
  --example-manifest learner_outputs/mainline/day13/pair_a.csv \
  --challenge-spec shared/fixtures/day13_pair_spec_b.json \
  --challenge-manifest learner_outputs/mainline/day13/pair_b.csv \
  --challenge-defense learner_outputs/mainline/day13/challenge_defense.md
.venv-day06/bin/python -m unittest -v mainline.day13.tests.test_day13_tools
```

口述 10 分：实验单位/pair ID 2；唯一变化 2；seed/init 2；模型与配置冻结 2；语义人工审查边界 2。机器通过且 ≥8 进入 Day 14；5–7 补 F02/F03。不同初态、隐藏换 goal、用输出挑 paraphrase 或把 planned rows 当结果，必须重做。

## 10. 证据复盘

- 已运行：A/B spec 的锁定 task 映射、CSV 往返、pair ID 重算、固定字段篡改与复制攻击测试。
- 未运行：任一 A/B 模型 episode；model/revision/config 仍是显式 placeholder；语义等价仍待人工审阅。
- 可以主张：计划表中机器可见的唯一差异是 instruction text，且精确 task/seed/init 匹配。
- 不能主张：改写已由人批准、两臂真实初态已复现、输出差异来自语言，或这已经是空间关系反事实。

自测题（答案在 `shared/answer_keys/day13.md`）：

1. pair ID 的作用是什么，为什么要可重算？
2. 为什么相同 seed 仍不足以保证配对？
3. 本日允许变化与必须固定的字段分别是什么？
4. validator 为什么不能证明 paraphrase 语义等价？
5. pair 只完成一臂时能否计算配对差，应该怎样处理？
