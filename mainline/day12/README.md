# Mainline Day 12：把逐帧状态变成四段事件证据

今天把 Day 11 的单帧特权状态接进一个可复算的 episode logger：目标接触、目标抬升、向参照物接近、终态关系满足。你会冻结阈值、记录首次触发 step，并保留 probe 与真实 success 不一致的异常，而不是看完结果再调整定义。

## 1. 真实项目产物

- `learner_outputs/mainline/day12/event_contract.json`：四个原始 frame 字段对应的锁定源码来源；
- `learner_outputs/mainline/day12/events_a.json`：A 轨迹的四段布尔量、first step、证据值和冻结阈值；
- `learner_outputs/mainline/day12/events_b.json`：新轨迹上的闪烁、回退与乱序证据；
- `learner_outputs/mainline/day12/challenge_explanation.md`：阈值造成的 false positive/false negative 边界。

这些字段直接对应正式数据字典的 `target_contacted / target_lifted / reference_approached / relation_satisfied`，为后续失败分类和条件成功率提供基础。

## 2. 当前卡点

每帧 `target_gripper_contact=true` 可能只是碰撞抖动；target z 上升一点可能是初始化噪声；距离偶尔变小也不等于稳定搬向 reference。若把瞬时值直接当事件，会出现假阳。反过来，要求太多连续帧或过高阈值又会产生假阴。

更危险的是强迫四事件严格依次成立。锁定 goal predicate 是终态真值，前三个项目 probe 只是诊断定义；一个 probe 漏检时，不能抹掉真实 success。因此 logger 独立保留 relation，并把“relation 早于某个 probe”记入 anomalies 供视频抽查。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day12/code/minimal_event_latch.py
```

应看到 step 1 的单帧 true 没触发，step 4 达到连续两帧后 `contacted=True`，最后 `first_event_step=4`。若不理解函数与测试补 [F03](../../foundation_library/f03_modules_testing/README.md)；若不理解 episode/step 回看 [F08](../../foundation_library/f08_episode_evaluator/README.md)。

## 4. 即时知识

- **raw state**：某一帧直接测到的数值或布尔量；会抖动，也可能漏测。
- **event latch**：条件第一次稳定满足后保持 true，并记录 first step；同一 episode 不反复计数。
- **baseline**：lift 相对第 0 帧 target z；approach 相对首次 lift 帧的 target-reference XY 距离。
- **连续帧规则**：本课 contact 与 approach 都要求 2 帧；降低一帧抖动假阳，但可能漏掉短事件。
- **阈值冻结**：`event_thresholds.json` 的 4 cm lift、5 cm approach drop 和连续帧数必须在正式 pilot 前登记。它们是项目操作性定义，不是 VLA-Arena 内置常数。
- **终态独立性**：relation 直接来自 `info.success`，不依赖前三个 probe 是否触发；异常顺序保留给人工回放。

## 5. 成熟材料处方

- **中文主材料（12 分钟）**：[Google 机器学习速成课程：分类阈值](https://developers.google.com/machine-learning/crash-course/classification/thresholding?hl=zh-cn)。只读“改变阈值会改变假阳/假阴”部分，把同一权衡迁移到事件 probe；不要把分类概率公式硬套进仿真。
- **锁定源码补充（10 分钟）**：[VLA-Arena `check_gripper_contact`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/bddl_base_domain.py#L1535-L1554)。确认它检查 gripper collision geoms 与目标 contact geoms；这只是 raw contact 来源，稳定事件仍由本项目定义。

## 6. 最小实验

[minimal_event_latch.py](code/minimal_event_latch.py) 是完整示例：

```python
#!/usr/bin/env python3
"""最小例子：瞬时布尔量经过连续帧规则变成一次性事件。"""

CONTACT = [False, True, False, True, True, False]
REQUIRED = 2
run_length = 0
first_event_step = None

for step, is_contact in enumerate(CONTACT):
    run_length = run_length + 1 if is_contact else 0
    if first_event_step is None and run_length >= REQUIRED:
        first_event_step = step
    print(
        f"step={step} raw={is_contact} run={run_length} "
        f"contacted={first_event_step is not None}"
    )

print(f"first_event_step={first_event_step}")
```

关键不是“看到过 true”，而是把规则、连续计数和首次 step 一起留下。

## 7. 真实 VLA-Arena 操作

先验证字段来源并在 CPU fixture 上跑完整 logger：

```bash
export VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
.venv-day06/bin/python mainline/day12/code/build_event_contract.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --output learner_outputs/mainline/day12/event_contract.json
.venv-day06/bin/python mainline/day12/code/event_logger.py \
  --input shared/fixtures/day12_frames_a.json \
  --thresholds mainline/day12/config/event_thresholds.json \
  --output learner_outputs/mainline/day12/events_a.json
```

应看到 contract PASS；A 应为四事件全 true、`real environment run=false`，first steps 是 2/4/7/8。长文件 [event_logger.py](code/event_logger.py) 完整实现并注释了三类 latch；阅读顺序是 `load_thresholds → _validate_frames → summarize`，不要跳过输入校验。

字段契约精确追到 [`ObjectState.get_geom_state/check_gripper_contact`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/object_states/base_object_states.py#L63-L75)、[`ObjectState.check_gripper_contact`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/object_states/base_object_states.py#L212-L214) 和 [`BDDLBaseDomain.step`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/bddl_base_domain.py#L1188-L1210)。relation 必须读取 step 写入的 `info.success`，不能用 done。

Gate 1 环境可用后，在 evaluator 的 `obs, _, done, info = env.step(action)` 后调用 [capture_event_frame.py](code/capture_event_frame.py)：

```python
frames.append(capture_frame(
    env, info, target=task_row["target_object"],
    reference=task_row["reference_object"], step=t,
))
```

episode 结束后，把 metadata 与 `frames` 写成和 A fixture 相同的 JSON，再用同一 `event_logger.py` 处理。保存原始 frames，不能只保存四个最终布尔量，否则无法复核阈值。当前未运行 MuJoCo；fixture 是合成时序，不是模型结果。

若 contact 永不出现，先验证 target 名和 gripper collision geoms；若 lift 一开始就 true，检查第 0 帧是否真在 reset 后采集；若 relation 与 done 冲突，检查 `info.success` 与 timeout；若大量 anomalies，先回放视频，不要直接调阈值。

## 8. 独立挑战

换用 `shared/fixtures/day12_frames_b.json` 生成 `events_b.json`。B 包含单帧 contact 闪烁、提前抬高、approach 条件中途回退，以及 relation 先于 approach；正文不提供完整 first-step 答案。

写至少 140 字 `challenge_explanation.md`，必须出现 `false positive`、`false negative`、`contact`、`lift`、`approach`、`relation`。解释哪些帧被过滤、为何 relation 不应被抹掉，以及提高连续帧数会怎样改变两类错误。复制 A 输出或手改 first step 会被重算拒绝。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day12.tests.test_day12_tools
.venv-day06/bin/python mainline/day12/code/check_day12.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --thresholds mainline/day12/config/event_thresholds.json \
  --contract learner_outputs/mainline/day12/event_contract.json \
  --example-input shared/fixtures/day12_frames_a.json \
  --example-output learner_outputs/mainline/day12/events_a.json \
  --challenge-input shared/fixtures/day12_frames_b.json \
  --challenge-output learner_outputs/mainline/day12/events_b.json \
  --challenge-explanation learner_outputs/mainline/day12/challenge_explanation.md
```

口述 10 分：四事件操作定义 4；baseline/连续帧 2；假阳假阴 2；relation 独立与人工抽查 2。机器通过且 ≥8 进入 Day 13；5–7 补 F03/F08。看 L1/L2 输出后调阈值、删异常或用 done 代 success，必须重做。

## 10. 证据复盘

- 已运行：锁定字段来源 AST 契约、A/B 时序重算、闪烁/回退/乱序测试、fake env frame 采集。
- 未运行：真实 gripper collision、MuJoCo 位姿时序、模型 episode；当前阈值尚未经过真实视频人工抽查。
- 可以主张：logger 的输入、阈值、首次触发与异常可复算；relation 不会被前序 probe 漏检覆盖。
- 不能主张：4 cm/5 cm 是唯一正确阈值、连续两帧消除了噪声，或四事件能证明模型内部表征。

自测题（答案在 `shared/answer_keys/day12.md`）：

1. raw state 与 event 有什么区别？
2. A 的 lift/approach baseline 分别来自哪一帧？
3. 连续帧规则如何同时影响 false positive 和 false negative？
4. 为什么 relation 不应以前三事件为前提？
5. 发现 relation 早于 approach 时应该删除、调阈值还是保留并回放？
