# Day 8：episode、step、success 与实验目录闭环

> 阶段 1 / Day 8 of 70　　建议用时：8—9 小时　　运行环境：免费 CPU

今天把前七天的零件连成第一个完整闭环：环境给 observation，策略产生 action，环境更新 state，一次 step 被记录；重复直到 success 或达到最大步数，最后保存逐步 CSV 和 episode JSON。这个一维小世界很简单，但它和未来 VLA evaluator 具有相同的控制骨架。

所有 ID 以 `fixture_` 开头。这里没有图像模型、仿真器或机器人，`success=True` 只代表合成点到达一维目标，绝不是 VLA-Arena 成绩。

## 1. 学完后你能做什么

1. 区分 environment state、observation、action、step 与 episode；
2. 解释 reset、step、terminated、truncated 和 success 的关系；
3. 明白 success 必须由环境 predicate 判定，不能由 policy 自报；
4. 区分合法 episode failure 与 evaluator/infrastructure error；
5. 运行确定性 CPU evaluator 并保存逐 step/逐 episode 证据；
6. 修改 gain、max action、max steps 前先预测终止方式；
7. 说明这个最小闭环怎样迁移到 VLA-Arena。

## 2. 前置检查与今天产物

从仓库根目录开始：

```bash
cd "$(git rev-parse --show-toplevel)"
python3 foundation_library/f07_numpy_observations/code/sensor_pipeline.py
python3 -m unittest -v foundation_library.f07_numpy_observations.tests.test_sensor_pipeline
```

今天的教材代码：

```text
foundation_library/f08_episode_evaluator/code/minimal_episode.py
foundation_library/f08_episode_evaluator/code/mini_evaluator.py
foundation_library/f08_episode_evaluator/tests/test_mini_evaluator.py
```

运行产物：

```text
learner_outputs/foundation_library/f08_episode_evaluator/fixture_steps.csv
learner_outputs/foundation_library/f08_episode_evaluator/fixture_episode_summary.json
```

开始前预测：episode 达到 max_steps 是 success、failure 还是程序错误？策略输出 NaN 又属于哪一类？如果 reset 时已经在目标内，应不应该伪造一个 action step？

## 3. 今天学什么概念

### 3.1 environment state 与 observation

**state** 是环境完整内部状态；**observation** 是当前允许策略看到的信息。今天环境内部只有 position、target 和契约参数，observation 暴露 position/target，因此二者看似接近。真实仿真器 state 可能包含物体精确位姿、接触、速度等，而模型只看到相机图像、机器人 proprioception 和语言。

不能因为仿真器知道目标物坐标，就默认 policy 可以使用。VLA-RelComp 的视觉 oracle 可以临时使用真值做诊断，但必须明确标注特权信息；最终修复不能偷偷读取测试真值。

### 3.2 action 与环境转移

policy 的职责是从 observation 产生 action；environment 的 `step(action)` 校验动作、更新 state、产生下一 observation 并计算终止信息。今天动作是数轴上的标量位移请求，环境把它裁剪到 `[-max_action,max_action]`。

策略返回 10 不代表实际移动 10。日志若只保存原始 action 而不保存 state before/after，会看不到裁剪效果。完整工程因此记录 position_before、action、position_after 和 distance_after。

真实 7 维动作还涉及归一化、坐标系和夹爪约定；Day 7 的向量只是接口准备，今天用标量让控制流可手算。

### 3.3 step 是一次交互，不是代码行

一个 step 的逻辑顺序：

```text
observation_t → policy → action_t → environment.step
→ state_(t+1) → observation_(t+1) → predicate/record
```

`step_index=0` 是第一次交互。运行 4 次 step 后，step index 最后是 3，但 `step_count=4`。日志应明确用哪个口径，避免 off-by-one。

### 3.4 episode 是有边界的一段轨迹

episode 从 `reset` 开始，在某个终止条件结束。它不是“固定恰好 120 行”：success 可以提前结束，也可以因为最大步数、安全条件或异常而停止。

本课三种 termination reason：

- `success_at_reset`：初态已满足 predicate，没有虚构 action；
- `success`：某次 step 后满足 predicate；
- `max_steps`：用完预算仍未成功，属于合法任务失败。

真实 evaluator 还需记录异常、人工中止、环境崩溃等。不能把这些统统算模型 failure，否则会污染成功率。

### 3.5 terminated、truncated 与 success

今天：

- `terminated=True` 表示任务 predicate 已满足；
- `truncated=True` 表示未成功但达到外部步数上限；
- `success` 是明确 predicate 的布尔结果。

在其他强化学习环境中 terminated 也可能代表失败终态，不一定等于 success。因此接口中应独立保留 success，不能永久写死 `success = terminated`。本课只有成功任务终态，所以二者在 step record 中暂时相同。

### 3.6 predicate 是可执行定义

本课 success：

```python
abs(target - position) <= tolerance
```

它比“看起来到了”精确：目标、位置、容差共同决定。改变 tolerance 会改变 success 判定，却不必改变轨迹。这说明评测指标也是实验定义的一部分，必须预先固定。

VLA-Arena 中 success 来自 CBDDL goal predicate。视频适合人工理解，但正式 success 不能由作者看完视频临时决定。

### 3.7 policy 与 evaluator 解耦

`Policy` Protocol 只要求 `act(observation)`。比例策略、零动作策略和未来模型 adapter 都可接入同一 evaluator。这样对比策略时环境、记录与 predicate 不变。

今天的比例策略：

```text
action = gain × (target - position)
```

环境再按 max_action 裁剪。gain=1 时从 0 到 1，每步最多 0.25，需要 4 步；gain=0 时永远不动，达到 max_steps 后 failure；负 gain 会远离目标但仍是合法有限动作。

### 3.8 合法失败与基础设施错误

一个 episode 在环境正常、动作合法、记录完整的情况下未达到 goal，是合法 failure，主 evaluator 可以返回 0，摘要 success=false。NaN 动作、无效配置、文件无法写出则是基础设施错误，程序返回 2，不应产生可计入模型分母的 episode。

这个区别贯穿项目：模型做错任务与模型根本没加载、渲染崩溃、磁盘写满不能混为一谈。

## 4. 先运行约 30 行最小闭环

```bash
sed -n '1,160p' foundation_library/f08_episode_evaluator/code/minimal_episode.py
python3 foundation_library/f08_episode_evaluator/code/minimal_episode.py
```

预期每行依次出现 step index、旧 position、action、新 position、success；最后：

```text
episode_success=True; steps=4
synthetic CPU episode; not a VLA experiment result
```

手算轨迹：0 → 0.25 → 0.5 → 0.75 → 1.0。`MAX_STEPS=6` 是最多允许六步，不表示一定执行六步；success 后立即 break。

## 5. 完整 evaluator 导读与运行

完整代码在 [`code/mini_evaluator.py`](code/mini_evaluator.py)。按环境 → policy → episode loop → artifacts → CLI 阅读：

```bash
sed -n '1,140p' foundation_library/f08_episode_evaluator/code/mini_evaluator.py
sed -n '141,320p' foundation_library/f08_episode_evaluator/code/mini_evaluator.py
python3 foundation_library/f08_episode_evaluator/code/mini_evaluator.py --help
```

默认运行：

```bash
python3 foundation_library/f08_episode_evaluator/code/mini_evaluator.py
echo $?
sed -n '1,20p' learner_outputs/foundation_library/f08_episode_evaluator/fixture_steps.csv
sed -n '1,120p' learner_outputs/foundation_library/f08_episode_evaluator/fixture_episode_summary.json
```

预期 success true、4 steps、termination success、主退出码 0。CSV 有四条转移，最后一条 terminated 为 True；JSON 指向 CSV 并显著声明 synthetic。

运行合法失败：

```bash
python3 foundation_library/f08_episode_evaluator/code/mini_evaluator.py \
  --episode-id fixture_day08_zero_gain \
  --gain 0 --max-steps 3
echo $?
```

预期 success false、3 steps、termination max_steps，但主退出码仍 0，因为 evaluator 完整完成了一次合法评测。

## 6. 自动化测试

```bash
python3 -m unittest -v foundation_library.f08_episode_evaluator.tests.test_mini_evaluator
python3 -m py_compile \
  foundation_library/f08_episode_evaluator/code/minimal_episode.py \
  foundation_library/f08_episode_evaluator/code/mini_evaluator.py \
  foundation_library/f08_episode_evaluator/tests/test_mini_evaluator.py
```

四项测试覆盖：四步成功；零 gain 截断失败；reset 已成功且不伪造 step；NaN action 被判为基础设施错误。预期末尾 `OK`，语法检查无输出。

## 7. 动手实验

### 实验 A：改变 max action

先预测 `max-action=0.4` 从 0 到 1 需要几步，再运行：

```bash
python3 foundation_library/f08_episode_evaluator/code/mini_evaluator.py \
  --episode-id fixture_day08_fast \
  --max-action 0.4
```

预期 3 步：0→0.4→0.8→1.0。只改变环境动作上限，不代表模型变聪明。

### 实验 B：区分 gain 与裁剪

预测 gain=10、max-action=0.25 的第一步实际 position_after。运行并查看 CSV。策略请求 10，但环境裁剪后移动 0.25；当前 CSV action 记录 policy 原始请求，因此需用 before/after 识别实际转移。写下以后是否应增设 applied_action 字段——答案是应当，Day 23 真实 schema 会补。

### 实验 C：改变 tolerance

固定 start=0、target=1、max-action=0.3、max-steps=3，分别 tolerance 0.05 与 0.11。先手算终点 0.9，再预测两次 success。第二次会因距离 0.1≤0.11 成功。这说明 predicate 变化可改变标签，必须预先登记。

### 实验 D：reset success

运行 start=0.98、target=1、tolerance=0.05。预测 step_count。预期 0、reason `success_at_reset`。解释为什么不应为凑 CSV 行而调用一次 action。

### 实验 E：基础设施错误

```bash
python3 foundation_library/f08_episode_evaluator/code/mini_evaluator.py \
  --episode-id fixture_day08_bad \
  --tolerance 0
echo $?
```

预期返回 2 并报告契约错误。这条运行不能加入 episode 成功率分母。

## 8. 常见错误与止损

| 现象 | 先检查与处理 | 止损时间 |
|---|---|---:|
| step 数比 index 大 1 | index 从 0 开始；用记录条数作 count | 10 分钟 |
| failure 时程序却返回 0 | 区分合法 episode failure 与 evaluator error | 10 分钟 |
| action 很大但移动很小 | 环境进行了 clip；对照 before/after | 15 分钟 |
| success 随 tolerance 改变 | predicate 本身变了，不是策略结果变化 | 15 分钟 |
| 旧 CSV 被覆盖 | 每次实验使用唯一 output dir/run ID | 10 分钟 |
| NaN 进入记录 | 在环境边界先做 finite 校验 | 15 分钟 |
| 循环不结束 | 明确 max_steps 并检查每次递增 | 20 分钟 |

不要通过手工改 summary 的 success“修复”结果；任何修改必须来自可执行 predicate 并重新运行。

## 9. 与 VLA-RelComp 的连接

未来闭环只是把部件替换：一维 observation 换成图像/state/instruction；比例策略换成 SmolVLA/OpenVLA adapter；LineWorld 换成 VLA-Arena/MuJoCo；一维目标 predicate 换成 CBDDL goal。循环骨架仍是 reset→observe→act→step→record→terminate。

VLA-RelComp 还会在每个 step 提取目标接触、抬升、参照接近和终态关系四段事件。今天的 distance_after 是最简单状态探针：它能描述轨迹是否接近目标，但不能说明策略内部理解了目标。

阶段 1 至此建立了可重复程序、结构化记录、校验测试、Git 恢复、系统与 Python 环境、数组接口和 evaluator 闭环。Day 9 开始把 NumPy 数组迁移到 PyTorch tensor。

## 10. 检查点与答案

### 题 1

state 与 observation 为什么不能总当同一个对象？

**答案：** state 是环境完整内部信息，observation 是允许策略看到的投影。仿真真值若未经声明进入 policy，会造成特权信息泄漏。

### 题 2

max_steps 用尽且未成功是什么状态？

**答案：** 是合法 episode failure，truncated=true、success=false；只要 evaluator 正常记录，外层程序可以成功返回 0。

### 题 3

谁应该判定 success？

**答案：** 预先定义的环境/任务 predicate。policy 只产生 action，不能自报完成；人工视频判断只能作核对或标注协议的一部分。

### 题 4

为什么 NaN action 不应算普通模型失败？

**答案：** 它违反动作接口并可能来自模型数值、适配器或基础设施异常，应单独记录和归因；直接计入任务失败会混淆行为能力与运行故障。

### 题 5

只记录最终 success 会丢失什么？

**答案：** 丢失动作、状态转移、何时偏离、是否接近目标、裁剪和终止原因，无法做行为级诊断。

## 11. 完成标准

**最低完成线：** 最小/完整 evaluator 均运行；成功与合法失败两条路径可解释；4 项测试通过。

**标准完成线：** 完成 A—E；能手算轨迹并区分 terminated/truncated/success/error；保存独立输出目录和个人闭环图。

**当天产物：** 教材中的最小 episode、完整 evaluator 与测试；个人目录中的逐步 CSV、episode JSON、五项对照结果和闭环口述笔记。

## 12. 精确外部材料

| 材料 | 精确范围 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [Gymnasium Basic Usage](https://gymnasium.farama.org/introduction/basic_usage/) | Initialization、Observations、Actions、Episode Termination，35 分钟 | 对照 reset/step/terminated/truncated | wrappers 与 vector env |
| [Gymnasium Env API](https://gymnasium.farama.org/api/env/) | `Env.reset` 与 `Env.step` 返回值定义，25 分钟 | 理解通用环境接口 | 自定义注册系统 |
| [Python 3.12 `typing.Protocol`](https://docs.python.org/3.12/library/typing.html#typing.Protocol) | 读 Protocol 说明与第一个例子，15 分钟 | 理解为何不同 policy 可接同一 evaluator | 泛型 protocol |
| [Python 3.12 `csv.DictWriter`](https://docs.python.org/3.12/library/csv.html#csv.DictWriter) | 构造参数、`writeheader`、`writerows`，15 分钟 | 保存逐 step 字段 | dialect 高级配置 |

Gymnasium 只是接口参考，本课没有安装或运行它；VLA-Arena 的真实接口将在锁定上游版本后按源码核验。
