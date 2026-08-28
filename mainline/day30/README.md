# Mainline Day 30：用官方谓词检测稳定终态空间关系

今天完成四段行为探针的最后一段：目标最终是否与任务指定参照物形成 `On` 或 `In`。核心规则是：锁定项目的 BDDL predicate 是权威信号，几何 proxy 只诊断冲突；若课程配置要求释放，谓词还要在夹爪不再接触目标后连续成立 k 步。

## 1. 真实项目产物

- `relation_summary_a.csv`：逐 episode 的关系、对象 ID、首次谓词/稳定 step、冲突和状态；
- `relation_report_a.json`；
- B 新输入的同类产物与 `challenge_memo.md`。

## 2. 当前卡点

“目标离碗很近”不等于“目标在碗上”。`On` 和 `In` 是带顺序的二元关系：`On(target, reference)` 不能写反。单帧真值又可能来自弹跳或临界接触；夹爪未释放时还可能只是机械臂暂时托住目标。因此，本课把“关系身份、官方谓词、释放条件、连续窗口”分别记录，避免让自制距离阈值覆盖项目成功定义。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day30/code/minimal_stable_relation.py
```

应看到首次稳定 step 为 2、权威信号为官方 BDDL predicate。若不会处理布尔序列，补 [F07](../../foundation_library/f07_numpy_observations/README.md)；目标/参照 ID 回看 [Day 9](../day09/README.md)，连续窗口回看 [Day 27](../day27/README.md)。

## 4. 即时知识

- **predicate（谓词）**：输入对象后返回真/假的关系函数；本课只允许 `On`、`In`。
- **argument order**：第一个参数是 target，第二个是 reference；顺序属于任务语义。
- **official predicate**：锁定 VLA-Arena 的实现和 BDDL goal 共同确定的权威真值。
- **terminal relation**：课程操作定义为 official predicate 在释放条件下连续 k 步为真。
- **geometric proxy**：自制几何近似，只报告 `OFFICIAL_ONLY`/`PROXY_ONLY` 冲突，不投票改写官方值。
- **transient**：谓词曾真但未达到连续窗口；与从未成关系不同。
- **observable ≠ causal**：终态失败是行为观测，不能单独断言语言、视觉或控制模块是原因。

## 5. 成熟材料处方

- **中文主材料（10 分钟）**：[VLA-Arena 场景构建中文说明：状态定义](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/docs/scene_construction_zh.md#14-%E7%8A%B6%E6%80%81%E5%AE%9A%E4%B9%89)。只读状态通过 predicate 定义、BDDL 中 goal 引用状态的部分。
- **补充材料（5 分钟）**：[Python `zip()` 官方中文文档](https://docs.python.org/zh-cn/3/library/functions.html#zip)。理解谓词与夹爪接触序列必须按同一 step 配对。
- **锁定项目定位（10 分钟）**：[predicate 实现第 64–98 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/predicates/base_predicates.py#L64-L98) 中，`In(arg1,arg2)` 调用参照物的 contact/contain，`On(arg1,arg2)` 调用参照物的 `check_ontop(arg1)`；[目标 BDDL 第 136–158 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/bddl_files/extrapolation_preposition_combinations/level_0/pick_the_tomato_next_to_the_cereal_and_place_it_on_the_porcelain_bowl_between_the_cabinet_and_the_cutting_board.bddl#L136-L158) 明确对象与 `(On tomato_1 porcelain_bowl_3)` goal。

## 6. 最小实验

[minimal_stable_relation.py](code/minimal_stable_relation.py) 是完整 19 行代码：

```python
#!/usr/bin/env python3
"""最小例子：官方谓词需在释放目标后连续成立。"""

predicate = [False, True, True, True]
gripper_contact = [True, True, False, False]
sustained_steps = 2

run = 0
first_stable_step = None
for step, (passed, held) in enumerate(zip(predicate, gripper_contact)):
    valid_terminal = passed and not held
    run = run + 1 if valid_terminal else 0
    if run == sustained_steps:
        first_stable_step = step - sustained_steps + 1
        break

print(f"first_stable_relation_step={first_stable_step}")
print("authority=official_bddl_predicate")
print("proxy_role=diagnostic_only")
```

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day30/code/analyze_relation_probe.py \
  --trace shared/fixtures/day30_relation_trace_a.csv --config shared/fixtures/day30_relation_config_a.json \
  --output learner_outputs/mainline/day30/relation_summary_a.csv \
  --report learner_outputs/mainline/day30/relation_report_a.json
```

应看到 5 个 synthetic episode，分别覆盖稳定关系、谓词为真但未释放、瞬时关系、仅 proxy 为真和从未成关系。

真实采集时，按 BDDL goal 固定 `relation/target/reference`，每个 env step 调用同一锁定 predicate，并同步记录夹爪—目标接触。保留官方值与独立 proxy 的原始列；不得先平滑再保存，也不得用 proxy 替代 evaluator。真实 MuJoCo、视频和模型/GPU 尚未运行。

## 8. 独立挑战

换用 B trace/config 生成新 summary/report。写 ≥220 字 memo，必须原样包含 `official predicate`、`On`、`In`、`target`、`reference`、`sustained`、`gripper release`、`geometric proxy`、`signal conflict`、`terminal relation`、`causal`、`synthetic`。不给 B 的状态与冲突答案；先预测，再运行。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day30.tests.test_day30_tools
.venv-day06/bin/python mainline/day30/code/check_day30.py \
  --example-trace shared/fixtures/day30_relation_trace_a.csv --example-config shared/fixtures/day30_relation_config_a.json --example-output learner_outputs/mainline/day30/relation_summary_a.csv --example-report learner_outputs/mainline/day30/relation_report_a.json \
  --challenge-trace shared/fixtures/day30_relation_trace_b.csv --challenge-config shared/fixtures/day30_relation_config_b.json --challenge-output learner_outputs/mainline/day30/relation_summary_b.csv --challenge-report learner_outputs/mainline/day30/relation_report_b.json \
  --challenge-memo learner_outputs/mainline/day30/challenge_memo.md
```

口述 10 分：关系参数顺序 2；官方 predicate 权威性 2；release/sustained 2；proxy/conflict 2；synthetic/causal 边界 2。机器通过且 ≥8 进入 Day 31；写反对象、单帧作稳定、proxy 覆盖官方值或伪造真实结果均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic predicate trace、稳定窗口、释放条件、严格重建与冲突保留。
- 静态源码事实：锁定 `In`/`On` 实现及目标 suite 的具体 BDDL goal。
- 未运行：真实 evaluator trace、MuJoCo、视频、模型/GPU。
- 可以主张：detector 在合成输入上按官方谓词区分五种终态状态并暴露 proxy 冲突。
- 不能主张：真实模型成功率、谓词质量，或某模块导致关系失败。

自测题（答案在 `shared/answer_keys/day30.md`）：

1. `On(target, reference)` 的参数能否互换？
2. 为什么不能用单帧 predicate=true 判稳定成功？
3. 为什么默认要求 gripper release？
4. geometric proxy 与 official predicate 冲突时谁覆盖谁？
5. signal conflict 能否直接证明模型的 causal 错误？
