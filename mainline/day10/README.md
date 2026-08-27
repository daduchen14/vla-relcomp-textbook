# Mainline Day 10：追到真实 success predicate，而不是把 done 当成功

今天沿锁定源码把 Day 9 的 `:goal` 追到运行时几何判定，再追到 evaluator 的 success 记录。你会得到一张 goal→predicate→`info.success` 调用链图，并用 CPU 数值 fixture 验证 `On` 的严格阈值与 timeout 边界；没有合格 MuJoCo 环境时不伪造真实 probe。

## 1. 真实项目产物

- `learner_outputs/mainline/day10/success_contract.json`：锁定文件、公式和 15 个 task 的 predicate 统计；
- `learner_outputs/mainline/day10/success_chain.md`：从 BDDL goal 到 evaluator 的九节点路径；
- `learner_outputs/mainline/day10/predicate_a.json`：A 数值 fixture 的 On/done/info/evaluator success；
- `learner_outputs/mainline/day10/predicate_b.json` 与 `challenge_reflection.md`：独立处理严格边界、timeout 与同时成功。

## 2. 当前卡点

机器人 episode 停止可能因为目标完成，也可能因为 horizon 到期。锁定环境明确写 `done = success or timeout_done`；若只统计 done，所有 timeout 都会被误报成功。evaluator 因此调用 `is_success_done(done, info)`，优先读取环境写入的 `info['success']`。

“On”也不是看到 target 比 reference 高就算成功。目标 suite 最终调用 `reference.check_ontop(target)`，对象实现同时检查高度、物理接触和 XY 距离。缺任一项都是 false。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day10/code/minimal_done_success.py
```

应看到 `goal` 成功、`timeout` done=true 但 success=false、`running` 两者都 false，以及缺 `info.success` 时的 legacy fallback。若布尔条件/字典卡住补 [F02](../../foundation_library/f02_csv_json/README.md)，episode 结束语义卡住补 [F08](../../foundation_library/f08_episode_evaluator/README.md)。

## 4. 即时知识

- **predicate**：把当前仿真状态映射成布尔值的函数；本套件 goal 全是二元 `On`。
- **conjunction**：`_check_success` 遍历 `goal_state` 并做 AND；虽然当前文件各只有一个 goal，代码支持多个条件共同成立。
- **On 条件**：`reference_z <= target_z`、contact=true、XY Euclidean distance `<0.07`。
- **done**：环境本轮返回的 episode 结束信号，可能由 success 或内部 timeout 触发。
- **timeout**：时间上限到达且没有 success；锁定环境写 `info.timeout = timeout_done and not success`。
- **evaluator success**：`bool(info.get('success', done))`；正常 VLA-Arena 环境有 success key，因此不会把 timeout done 当成功。

## 5. 成熟材料处方

- **中文主材料（12 分钟）**：[VLA-Arena 锁定《场景构建指南》§1.4 状态定义](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/docs/scene_construction_zh.md#14-状态定义)。只读 init/goal 示例，确认 goal 是逻辑条件，不是 reward 文案。
- **概念补充（英文官方，10 分钟）**：[Gymnasium Handling Time Limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)。只读 termination/truncation 区分；VLA-Arena 锁定 API 仍返回四元组 `done/info`，不要把文档的五元组接口硬套到源码。

## 6. 最小实验

[minimal_done_success.py](code/minimal_done_success.py) 是完整 20 行示例：

```python
#!/usr/bin/env python3
"""最小例子：episode 结束（done）不等于任务成功。"""


def evaluator_success(done: bool, info: dict) -> bool:
    """复现锁定 `is_success_done`: 优先读取 info.success。"""
    return bool(info.get("success", done))


CASES = [
    ("goal", True, {"success": True, "timeout": False}),
    ("timeout", True, {"success": False, "timeout": True}),
    ("running", False, {"success": False, "timeout": False}),
    ("legacy_no_success_key", True, {"timeout": False}),
]


if __name__ == "__main__":
    for name, done, info in CASES:
        success = evaluator_success(done, info)
        print(f"{name}: done={done} success={success} info={info}")
```

legacy case 只是解释 fallback，不是 VLA-Arena 正常路径；真实 `BDDLBaseDomain.step` 总会写 success key。

## 7. 真实 VLA-Arena 操作

先复用 Day 9 的锁定结构表，构建静态 success 契约：

```bash
export VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
.venv-day06/bin/python mainline/day10/code/build_success_contract.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --json-output learner_outputs/mainline/day10/success_contract.json \
  --markdown-output learner_outputs/mainline/day10/success_chain.md
.venv-day06/bin/python mainline/day10/code/evaluate_predicate_fixture.py \
  --input shared/fixtures/day10_predicate_a.json \
  --output learner_outputs/mainline/day10/predicate_a.json
```

静态检查精确覆盖：[`_check_success` 与 `step`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/bddl_base_domain.py#L1137-L1210)、[`On.__call__`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/predicates/base_predicates.py#L69-L91)、[`ObjectState.check_ontop`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/object_states/base_object_states.py#L97-L130)、[`is_success_done`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/utils/eval_cost.py#L27-L28)。SmolVLA/OpenVLA evaluator 都必须出现真实调用。

A 应展示 success、timeout failure 和缺 contact 三种分支，且 `real_environment_run=false`。CPU fixture 直接复现源码布尔式，但 contact/position 是人工数值；只有 Gate 1 环境真实跑通后，才能从 episode 的 `info`、视频和终态状态验证 MuJoCo 路径。

## 8. 独立挑战

换用 `shared/fixtures/day10_predicate_b.json`，生成 `learner_outputs/mainline/day10/predicate_b.json`。B 同时包含精确 XY 边界、target 高度反例，以及 success 与 timeout horizon 同时发生的输入；不给逐 case 结果。

写至少 100 字 `challenge_reflection.md`，必须出现 `0.07`、`<`、`done`、`success`、`timeout`，逐项解释为什么不能只看距离或 done。复制 A 输出后改 form 会被按 B 数值重算拒绝。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day10.tests.test_day10_tools
.venv-day06/bin/python mainline/day10/code/check_day10.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --task-table learner_outputs/mainline/day09/task_structures.json \
  --contract-json learner_outputs/mainline/day10/success_contract.json \
  --chain-md learner_outputs/mainline/day10/success_chain.md \
  --example-input shared/fixtures/day10_predicate_a.json \
  --example-output learner_outputs/mainline/day10/predicate_a.json \
  --challenge-input shared/fixtures/day10_predicate_b.json \
  --challenge-output learner_outputs/mainline/day10/predicate_b.json \
  --challenge-reflection learner_outputs/mainline/day10/challenge_reflection.md
```

口述 10 分：BDDL→predicate path 3；On 三条件 3；done/timeout/success 3；fixture/MuJoCo 边界 1。机器通过且 ≥8 进入 Day 11；5–7 补 F02/F08。若把 timeout 算成功、把 `<` 说成 `<=` 或把数值 fixture 冒充 MuJoCo，停止扩张并重做。

## 10. 证据复盘

- 已运行：七个锁定源码文件的 AST/text 契约检查、A/B 数值 formula、done/info 分支与单元测试。
- 未运行：MuJoCo contact、body position、真实 `env.step` success；学习者 Gate 1 仍未完成。
- 可以主张：锁定 15 goal 都走 On；源码公式、0.07 严格阈值与 done/info 语义已定位。
- 不能主张：人工 contact 等于真实碰撞、真实 task 会在某帧 success，或 status metadata 问题已影响运行结果。

自测题（答案在 `shared/answer_keys/day10.md`）：

1. 为什么 done=true 不足以证明成功？
2. `is_success_done` 在何时退回 done？
3. 锁定 On predicate 的三个条件是什么？
4. XY 距离恰好 0.07 或没有 contact 会怎样？
5. CPU predicate fixture 通过后仍不能证明什么？
