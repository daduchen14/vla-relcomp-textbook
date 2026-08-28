# Mainline Day 32：构造关系固定的对象组合匹配 pair

今天把处理变量从“空间关系”换成“对象组合”：同一 relation 下切换 active target/reference，同时固定场景对象全集、资产、相机、seed、模型和推理配置。输出不仅要有 pair，还要有 relation/slot/对象组合覆盖报告，并诚实保留不同物体带来的视觉与动力学混淆。

## 1. 真实项目产物

- `object_pairs_a.csv`：3 对、6 个对象组合的计划表；
- `object_pairs_report_a.json`：relation、slot 与组合覆盖；
- B 新 spec 的 pair set、report 与 `challenge_defense.md`。

## 2. 当前卡点

若 A 是“tomato next to board”，B 是“apple on plate”，relation 与对象同时变化，无法知道哪一项对应行为翻转。即使 relation 相同，不同对象仍可能有不同尺寸、纹理、遮挡、抓取点和碰撞属性；直接称作“严格相同难度”也不成立。

本课固定 relation，并把 target/reference、instruction 与相应 init state 作为对象组合处理的同步变化。`object_multiset_sha256` 保证两臂声明使用同一对象全集，`matching_stratum` 预登记尺寸/容器形态/可见性等分层。它们降低混淆，不消除物体固有差异。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day32/code/minimal_object_combo.py
```

应看到 object 四个同步字段变化，而 relation/camera 固定。若集合与 CSV 卡住补 [F02](../../foundation_library/f02_csv_json/README.md)；若 effective factor 不清楚，回看 [Day 31](../day31/README.md)。

## 4. 即时知识

- **object combination**：一个 active target 与一个 active reference 的有序配对。
- **relation fixed**：A/B 使用同一关系和同一 relation slot，避免混入关系处理。
- **object multiset**：场景内对象全集；相同不代表 active 对象姿态相同。
- **matching stratum**：按预登记尺寸、形状、可见性、可达性等属性进行近似匹配。
- **coverage**：各 relation、slot 与组合有多少计划 pair；只报告计数，不暗示统计充分。
- **confound**：随对象组合一起变化、也可能影响 outcome 的外观/动力学因素。
- **pair completeness**：只有两臂审查合格且实际执行，才进入 asymmetry 等统计。

## 5. 成熟材料处方

- **中文主材料（6 分钟）**：[Python 集合类型官方中文文档](https://docs.python.org/zh-cn/3/library/stdtypes.html#set-types-set-frozenset)。只读集合去重与差集，理解 coverage 为什么按唯一组合计数。
- **实验设计补充（英文官方，12 分钟）**：[NIST Randomized Block Designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm)。把 matching stratum 看作 block；不要把分层误说成随机化已经完成。
- **锁定项目定位（10 分钟）**：[L0 示例 BDDL 的对象与 `obj_of_interest` 第 124–139 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/bddl_files/extrapolation_preposition_combinations/level_0/pick_the_tomato_next_to_the_cereal_and_place_it_on_the_porcelain_bowl_between_the_cabinet_and_the_cutting_board.bddl#L124-L139) 和 [init/goal 第 141–158 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/bddl_files/extrapolation_preposition_combinations/level_0/pick_the_tomato_next_to_the_cereal_and_place_it_on_the_porcelain_bowl_between_the_cabinet_and_the_cutting_board.bddl#L141-L158) 说明 active 对象必须同时与环境状态和 goal 对齐。

## 6. 最小实验

[minimal_object_combo.py](code/minimal_object_combo.py) 是完整 18 行代码：

```python
#!/usr/bin/env python3
"""最小例子：关系不变，只交换对象组合及其同步字段。"""

arm_a = {"relation": "next_to", "target": "tomato_1", "reference": "board_1",
         "instruction": "tomato next to board", "init": "state-a", "camera": "front"}
arm_b = {"relation": "next_to", "target": "apple_1", "reference": "plate_1",
         "instruction": "apple next to plate", "init": "state-b", "camera": "front"}

changed = {key for key in arm_a if arm_a[key] != arm_b[key]}
required = {"target", "reference", "instruction", "init"}
fixed = {key for key in arm_a if arm_a[key] == arm_b[key]}

assert changed == required
assert fixed == {"relation", "camera"}
print(f"changed={sorted(changed)}")
print(f"fixed={sorted(fixed)}")
print("effective_factor=object_combination")
print("execution=planned_not_run")
```

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day32/code/build_object_pair_set.py \
  --spec shared/fixtures/day32_object_pair_spec_a.csv \
  --output learner_outputs/mainline/day32/object_pairs_a.csv \
  --report learner_outputs/mainline/day32/object_pairs_report_a.json
```

应看到 `pairs=3 combinations=6 execution=planned_not_run`，并覆盖三个 relation。

真实执行前，在同一对象 multiset 的场景内改变 active target/reference assignment，保持 relation/slot、非 active 对象、资产、相机与推理配置；instruction、init 与 goal 必须同步。先以状态 diff 检查白名单，再按 matching stratum 人工检查尺寸、遮挡、可见性和可达性；两臂均 replay 合格才运行。当前 fixture 的 apple/orange 等只是教学候选，不等于锁定 suite 已提供这些合法 task。

## 8. 独立挑战

换用 B spec 生成新 pair set/report。写 ≥240 字 defense，必须原样包含 `object combination`、`target`、`reference`、`relation fixed`、`object multiset`、`matching stratum`、`visibility`、`reachability`、`coverage`、`confound`、`planned`、`synthetic`、`causal`。说明允许变化、至少七个固定项、coverage 的读法与仍未排除的混淆。正文不提供 B 覆盖计数。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day32.tests.test_day32_tools
.venv-day06/bin/python mainline/day32/code/check_day32.py \
  --example-spec shared/fixtures/day32_object_pair_spec_a.csv --example-output learner_outputs/mainline/day32/object_pairs_a.csv --example-report learner_outputs/mainline/day32/object_pairs_report_a.json \
  --challenge-spec shared/fixtures/day32_object_pair_spec_b.csv --challenge-output learner_outputs/mainline/day32/object_pairs_b.csv --challenge-report learner_outputs/mainline/day32/object_pairs_report_b.json \
  --challenge-defense learner_outputs/mainline/day32/challenge_defense.md
```

口述 10 分：对象组合/同步字段 2；relation fixed 2；multiset/stratum 2；coverage 2；confound 与证据边界 2。机器通过且 ≥8 进入 Day 33；同时改关系、场景对象不一致、忽略可达性、把 coverage 当 outcome 或把计划当运行均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic spec、pair ID、字段白名单与 coverage 严格重建。
- 静态源码事实：锁定 BDDL 明确列出对象、obj_of_interest、init 与 goal。
- 未运行：新增 task/CBDDL、对象状态 diff、人工 replay、模型 pair。
- 可以主张：计划表固定 relation，并显式约束/报告对象组合与匹配分层。
- 不能主张：对象难度等价、真实 pair 可达、覆盖充分、pair asymmetry 或 causal 效应。

自测题（答案在 `shared/answer_keys/day32.md`）：

1. 为什么 relation 必须固定？
2. object multiset 相同还不能保证什么？
3. matching stratum 是什么，不是什么？
4. coverage 应怎样报告和解释？
5. 分层后能否说对象差异不再是 confound？
