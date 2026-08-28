# Mainline Day 31：批量构造只改变空间关系的匹配 pair

今天把 Day 13 的单个表面改写 pair 扩展为 relation pair set。每对固定对象、资产、相机、seed、模型和推理配置，只改变一个**有效因素**：空间关系。关系变化必须同步反映到 instruction 和实现该关系的 init state；这三列是同一处理的必要编码，不是三个可任意变化的因素。

## 1. 真实项目产物

- `relation_pairs_a.csv`：3 对、6 臂的批量计划表；
- `relation_pairs_report_a.json`：关系 contrast 与审查/运行边界；
- B 新 spec 的 pair set、report 和 `challenge_defense.md`。

## 2. 当前卡点

把 instruction 中 `next to` 改为 `on top of`，却保持原场景不变，会使文本与正确目标不同步，pair 无效。反过来，重置整个场景又会同时改变对象位置、遮挡和控制难度，无法把差异归到关系。

因此 relation treatment 有三项白名单变化：`relation`、`instruction_text`、`init_state_id`；init state 只能改变实现关系所需的几何。资产、相机、对象 multiset、target/reference ID、seed、model/config 都按 hash 或值匹配。机器只能检查声明与清单，不能证明两份状态真的只差关系；goal sync 与 reachability 在真实执行前仍要人工审查/replay。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day31/code/minimal_effective_factor.py
```

应看到三项 changed、两个 fixed，且 `effective_factor=spatial_relation`。若集合推导或断言卡住补 [F03](../../foundation_library/f03_modules_testing/README.md)；若不清楚精确初态与 pair ID，回看 [Day 13](../day13/README.md)。

## 4. 即时知识

- **effective factor**：研究上主动改变的一个因素；这里是空间关系，不等于“只能有一个 CSV 单元格变化”。
- **synchronized fields**：relation、instruction、init geometry 必须一致表达同一处理。
- **fixed fields**：场景资产、相机、对象 multiset、对象 ID、seed、model revision 与 inference config。
- **matched state group**：A/B 的匹配状态身份；仍需实际状态差分证明白名单外相同。
- **pair completeness**：两臂都有效、都实际运行才可进入配对统计。
- **pair asymmetry**：完整真实 pair 中仅一臂成功的比例；计划表不能计算。
- **minimal ≠ causal proof**：更严的匹配减少混淆，但有限执行、状态误差和模型随机性仍存在。

## 5. 成熟材料处方

- **中文主材料（12 分钟）**：[VLA-Arena 场景构建中文说明](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/docs/scene_construction_zh.md)。只读 BDDL/CBDDL 的 init、goal 和状态定义，理解文本关系改变后环境真值必须同步。
- **实验设计补充（英文官方，12 分钟）**：[NIST Randomized Block Designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm)。只读同一 block 内比较 treatments 的动机；本课把 matched state group 当 block，不做公式推导。
- **锁定项目定位（8 分钟）**：[suite task map 第 163–185 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/benchmark/vla_arena_suite_task_map.py#L163-L185) 只登记现有 3×5 个任务；[L0 示例 BDDL 第 141–158 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/bddl_files/extrapolation_preposition_combinations/level_0/pick_the_tomato_next_to_the_cereal_and_place_it_on_the_porcelain_bowl_between_the_cabinet_and_the_cutting_board.bddl#L141-L158) 展示 init 与 goal。新 relation arm 不能靠改文本凭空出现。

## 6. 最小实验

[minimal_effective_factor.py](code/minimal_effective_factor.py) 是完整 18 行代码：

```python
#!/usr/bin/env python3
"""最小例子：一个关系处理会同步改变三列，其余列必须匹配。"""

arm_a = {"relation": "next_to", "instruction": "tomato next to board",
         "init_state": "state-next", "seed": "17", "camera": "front"}
arm_b = {"relation": "on_top_of", "instruction": "tomato on board",
         "init_state": "state-on", "seed": "17", "camera": "front"}

required_changes = {"relation", "instruction", "init_state"}
changed = {key for key in arm_a if arm_a[key] != arm_b[key]}
fixed = {key for key in arm_a if arm_a[key] == arm_b[key]}

assert changed == required_changes
assert fixed == {"seed", "camera"}
print(f"changed={sorted(changed)}")
print(f"fixed={sorted(fixed)}")
print("effective_factor=spatial_relation")
print("execution=planned_not_run")
```

## 7. 真实 VLA-Arena 操作

先在免费 fixture 上生成计划：

```bash
.venv-day06/bin/python mainline/day31/code/build_relation_pair_set.py \
  --spec shared/fixtures/day31_relation_pair_spec_a.csv \
  --output learner_outputs/mainline/day31/relation_pairs_a.csv \
  --report learner_outputs/mainline/day31/relation_pairs_report_a.json
```

应看到 `pairs=3 arms=6 execution=planned_not_run`。每对只有 `arm/relation/instruction/init_state` 不同；其中 arm 只是标签，后三列同步编码空间关系。

真实执行前，为每个 relation arm 创建或选择与锁定 suite 兼容的 CBDDL/初态：固定资产、相机和对象 multiset，只移动 treatment 涉及的 target/reference 几何；重新生成 instruction 和正确 init/goal；对状态做白名单差分；逐臂 reset 后人工回放，确认 target 同步且 goal 可达。通过 Gate 1/2 后才能换掉 placeholder model/config 并运行两臂。当前 fixture 是候选设计，不是上游现成任务、真实初态或模型结果。

## 8. 独立挑战

换用 B spec 生成新 pair set/report。写 ≥240 字 defense，必须原样包含 `effective factor`、`relation`、`instruction`、`init_state`、`matched state`、`fixed fields`、`goal sync`、`reachability`、`pair asymmetry`、`planned`、`causal`、`synthetic`。列出允许变化与至少七个固定项，说明为什么同 seed 不足，以及缺臂时如何处理。正文不提供 B pair ID/contrast 汇总。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day31.tests.test_day31_tools
.venv-day06/bin/python mainline/day31/code/check_day31.py \
  --example-spec shared/fixtures/day31_relation_pair_spec_a.csv --example-output learner_outputs/mainline/day31/relation_pairs_a.csv --example-report learner_outputs/mainline/day31/relation_pairs_report_a.json \
  --challenge-spec shared/fixtures/day31_relation_pair_spec_b.csv --challenge-output learner_outputs/mainline/day31/relation_pairs_b.csv --challenge-report learner_outputs/mainline/day31/relation_pairs_report_b.json \
  --challenge-defense learner_outputs/mainline/day31/challenge_defense.md
```

口述 10 分：effective factor/同步字段 2；固定项与 matched state 2；goal sync 2；reachability/pair completeness 2；planned/causal 边界 2。机器通过且 ≥8 进入 Day 32；只改文本、整场景重采、手造 pair ID、缺臂入分母或把计划说成结果均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic spec 批量生成、稳定 pair ID、字段白名单、hash/schema 与严格重建。
- 静态源码事实：锁定 suite 有 3 个 level、每级 5 个登记任务；示例 BDDL 分开定义 init 与 goal。
- 未运行：新 CBDDL、状态白名单 diff、人工 replay、任一模型 pair。
- 可以主张：pair plan 明确了唯一有效因素、必要同步变化、固定项和执行前审查。
- 不能主张：pair 已可达/已运行、真实状态严格匹配、pair asymmetry 或 causal 效应。

自测题（答案在 `shared/answer_keys/day31.md`）：

1. 为什么一个 effective factor 会同步改变三列？
2. 相同 seed 为什么不足以证明 matched state？
3. schema validator 能否批准 goal sync 和 reachability？
4. planned pair set 能否计算 pair asymmetry？
5. 一臂缺失时能否把缺失当失败？
