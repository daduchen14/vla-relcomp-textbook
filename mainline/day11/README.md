# Mainline Day 11：把 goal 对象名接到真实仿真状态

今天把 Day 9 的 `On(target, reference)` 和 Day 10 的 success 公式接到锁定环境的对象状态。你会生成 object/relation state snapshot，知道每个坐标和 ID 从哪来，也会划清“policy 看见的 observation”和“evaluator 才能读取的仿真真值”之间的边界。

## 1. 真实项目产物

- `learner_outputs/mainline/day11/state_contract.json`：锁定对象 wrapper、位姿数组和 On 参数方向契约；
- `learner_outputs/mainline/day11/state_path.md`：对象名到 MuJoCo 状态的六节点路径；
- `learner_outputs/mainline/day11/snapshot_a.json`：L0T0 target/reference 与关系状态快照；
- `learner_outputs/mainline/day11/snapshot_b.json`、`challenge_explanation.md`：换成 L2T3 后独立生成的快照和特权边界说明。

这些资产为 Day 12 的四段事件日志提供逐帧输入。本日只采状态，不提前实现事件判定。

## 2. 当前卡点

BDDL 给的是 `tomato_3` 这类**语义对象名**，MuJoCo 的 `body_xpos` 却按整数 `body_id` 索引。锁定环境用 `object_states_dict[name]` 包住这层映射，再由 `ObjectState.get_geom_state()` 通过 `obj_body_id[name]` 读取 `body_xpos/body_xquat`。若按字典顺序猜 target、把 `obj_of_interest` 当 goal，或把 body ID 当永久身份，日志会悄悄记错对象。

另一个风险是信息泄漏：模型可能只看到图像、机器人本体状态和指令，但 evaluator 能直接读目标真值坐标与 contact。真值可以做失败诊断，不能未经协议授权就拼进 policy observation。

## 3. 前置诊断

从教材仓库根目录运行：

```bash
.venv-day06/bin/python mainline/day11/code/minimal_state_snapshot.py
```

应看到 target/reference 名称、不同 body ID、两个三维位置、相对高度、XY 距离，以及 `privileged_evaluator_state_not_policy_input`。若看不懂列表切片和字典补 [F02](../../foundation_library/f02_csv_json/README.md)；若仍混淆 observation 与诊断真值，回看 [Day 3](../day03/README.md) 第 4 节。

## 4. 即时知识

- **语义对象名**：BDDL 中稳定表达角色的名字；target/reference 必须从 goal 参数读取。
- **body ID**：当前已编译 MuJoCo model 中数组行的索引。它只在这个环境实例中有意义，不代替对象名。
- **position**：`[x, y, z]` 三维世界坐标，单位是米。相对高度用 `target_z-reference_z`，平面距离只取 XY。
- **quaternion**：四元数表达旋转。`ObjectState.get_geom_state()` 直接读 `body_xquat`，本课字段明确命名为 `quat_wxyz`；而锁定 observation sensor 会转换成 `xyzw`，两者不可按位置硬拼。
- **参数方向**：锁定 `On.__call__(arg1, arg2)` 调 `arg2.check_ontop(arg1)`，即 `On(target, reference) → reference.check_ontop(target)`。
- **privileged state**：仿真器内部真值，可供 evaluator 诊断；若 policy 的公开 observation 没有它，就不能用它决策。

## 5. 成熟材料处方

- **中文主材料（12 分钟）**：[VLA-Arena 锁定《场景构建指南》§1.4 状态定义](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/docs/scene_construction_zh.md#14-状态定义)。只读对象状态如何支撑 predicate，并把 BDDL 名称与环境状态 wrapper 对上。
- **官方补充（英文，15 分钟）**：[MuJoCo Computation—State and control](https://mujoco.readthedocs.io/en/stable/computation/index.html#state-and-control)。只读 state 的定义与数组化表示；不要把通用 MuJoCo 文档当作 VLA-Arena 的字段契约，字段仍以锁定源码为准。

## 6. 最小实验

[minimal_state_snapshot.py](code/minimal_state_snapshot.py) 是完整 26 行例子：

```python
#!/usr/bin/env python3
"""最小例子：由 target/reference 位姿形成关系状态。"""

from math import dist

OBJECTS = {
    "tomato_3": {"body_id": 17, "pos": [0.12, -0.05, 0.84]},
    "porcelain_bowl_3": {"body_id": 42, "pos": [0.10, -0.04, 0.78]},
}
TARGET, REFERENCE = "tomato_3", "porcelain_bowl_3"

target_pos = OBJECTS[TARGET]["pos"]
reference_pos = OBJECTS[REFERENCE]["pos"]
snapshot = {
    "target": TARGET,
    "reference": REFERENCE,
    "target_body_id": OBJECTS[TARGET]["body_id"],
    "reference_body_id": OBJECTS[REFERENCE]["body_id"],
    "target_pos": target_pos,
    "reference_pos": reference_pos,
    "target_minus_reference_z": target_pos[2] - reference_pos[2],
    "xy_distance": dist(target_pos[:2], reference_pos[:2]),
    "visibility": "privileged_evaluator_state_not_policy_input",
}

print(snapshot)
```

这里的 ID/坐标是教学数值，不是一次 MuJoCo rollout。它只练习名称映射、shape 与相对量。

## 7. 真实 VLA-Arena 操作

先从锁定源码和 Day 9 结构表建立契约，再跑 A fixture：

```bash
export VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
.venv-day06/bin/python mainline/day11/code/build_state_contract.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --json-output learner_outputs/mainline/day11/state_contract.json \
  --markdown-output learner_outputs/mainline/day11/state_path.md
.venv-day06/bin/python mainline/day11/code/snapshot_fixture.py \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --input shared/fixtures/day11_state_a.json \
  --output learner_outputs/mainline/day11/snapshot_a.json
```

应分别看到 `PASS: locked object-state contract` 和 `PASS: L0T0 tomato_3→porcelain_bowl_3; real environment run=false`。脚本精确检查 [`_generate_object_state_wrapper`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/bddl_base_domain.py#L343-L389)、[`ObjectState.get_geom_state/check_ontop`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/object_states/base_object_states.py#L48-L134) 和 [`On.__call__`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/predicates/base_predicates.py#L79-L81)。锁定 object observable 在 [`bddl_base_domain.py#L705-L720`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/bddl_base_domain.py#L705-L720) 把四元数转为 `xyzw`，这正是必须标字段顺序的原因。

Gate 1 环境可用后，在 evaluator 的 episode loop 内导入 [capture_vla_state.py](code/capture_vla_state.py)，并在 `env.step(action)` 后调用：

```python
snapshot = capture_state(
    env, target=task_row["target_object"],
    reference=task_row["reference_object"], step=t,
)
```

适配器能识别 `OffScreenRenderEnv/ControlEnv` 的一层 `.env`，真实读取相同 wrapper、body ID、位姿与 contact。把 JSONL 写盘属于 Day 12；本日只用单步调用确认字段。当前没有合格环境，因此没有声称运行这段 MuJoCo 路径。

若报 `object_states_dict 缺少 goal 对象`，先核对 level/task_id 与 Day 9 表，不要退回 `obj_of_interest` 猜测；若四元数含义异常，先核对 `wxyz/xyzw`；若 body ID 相同，说明采集或 fixture 映射错误。

## 8. 独立挑战

换用 `shared/fixtures/day11_state_b.json`，生成 `learner_outputs/mainline/day11/snapshot_b.json`。它选择新的 L2T3，字典中还放了 distractors；不得靠首项或 A 的对象名硬编码。

再写至少 120 字 `challenge_explanation.md`，必须出现 `target`、`reference`、`body_id`、`wxyz`、`privileged`、`policy`，解释 B 的对象身份、相对高度为何使 On 为 false，以及为何这些真值不能回灌模型。正文不提供 B 的完整输出。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day11.tests.test_day11_tools
.venv-day06/bin/python mainline/day11/code/check_day11.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --contract-json learner_outputs/mainline/day11/state_contract.json \
  --path-md learner_outputs/mainline/day11/state_path.md \
  --example-input shared/fixtures/day11_state_a.json \
  --example-output learner_outputs/mainline/day11/snapshot_a.json \
  --challenge-input shared/fixtures/day11_state_b.json \
  --challenge-output learner_outputs/mainline/day11/snapshot_b.json \
  --challenge-explanation learner_outputs/mainline/day11/challenge_explanation.md
```

机器会按 B 的 task selector、名称和数值重算，复制 A 后改标签不能通过。口述 10 分：goal→对象映射 3；pose/body ID/四元数 3；relation 方向 2；privileged-policy 边界 2。机器通过且 ≥8 进入 Day 12；5–7 补 F02/Day 3。混淆 target/reference、`wxyz/xyzw` 或把真值输入 policy，必须重做。

## 10. 证据复盘

- 已运行：锁定 commit 的 wrapper/位姿/On AST 契约、A/B CPU snapshot、fake ControlEnv 采集测试。
- 未运行：真实 MuJoCo body pose/contact 采样；fixture 中的 body ID、位姿、接触均为人工输入。
- 可以主张：15 个 task 的 goal 名称能唯一映射为 target/reference；锁定状态访问路径和参数方向已验证。
- 不能主张：某个真实 rollout 具有 fixture 坐标、policy 能看到这些字段，或 body ID 可跨环境比较。

自测题（答案在 `shared/answer_keys/day11.md`）：

1. target/reference 应从哪里读取，为什么不能用 `obj_of_interest` 代替？
2. body ID 与 BDDL 对象名分别承担什么角色？
3. `get_geom_state` 与 object observation 中的四元数顺序有何不同？
4. `On(target, reference)` 为什么调用 reference 的方法？
5. 什么是 privileged state，为什么不能默认加入 policy 输入？
