# Day 0（不计天数）：A/B 卷可执行诊断与跳过机制

Day 0 不是“先学基础”的第 0 课，而是一次 100–160 分钟的项目入口诊断。你会收到真实文件、一个隔离 Git 仓库和两套不同输入；评分器按产物内容决定 F01–F09 是否需要补习。F10–F18 在主线真正用到模型或训练时延迟诊断，不阻止入口通过者直接开工。

## 1. 诊断产物

完成一套卷后，目录中必须有：

```text
learner_outputs/mainline/day00_diagnostic/form_A/
├── FORM.json
├── inputs/
├── git_sandbox/
├── artifacts/
│   ├── task1_process.json
│   ├── normalized_episodes.json
│   ├── rejected_rows.json
│   ├── task4_observation.json
│   └── task5_episode.json
└── diagnostic_result.json
```

`diagnostic_result.json` 是今天的真实课程资产。它记录每项是否通过、推荐 F 模块和仍待主线触发的延迟诊断；它不是 VLA 实验结果。

## 2. 为什么现在诊断

Day 1 就要读锁定仓库，Day 2 要追配置，Day 3 要读 observation 和 episode loop。只有具体缺口会阻止这些任务；把所有人统一送回 18 天基础课既慢，也看不出谁真正卡在哪里。

## 3. 诊断规则

- 第一次随机选 A 或 B；补习后用另一卷复测，避免记住输入。
- 允许查 Python/Git 命令帮助，不允许看 `shared/answer_keys/`。
- 每项限时 20–40 分钟。限时内不能独立完成就保留失败，不靠抄答案刷绿。
- 所有命令从教材仓库根目录运行；只修改 `learner_outputs/mainline/day00_diagnostic/`。

## 4. 准备一套真实输入卷

下面以 A 卷为例；复测时把两处 `A` 改为 `B`：

```bash
.venv-day06/bin/python mainline/day00_diagnostic/code/prepare_form.py --form A
find learner_outputs/mainline/day00_diagnostic/form_A -maxdepth 3 -type f | sort
git -C learner_outputs/mainline/day00_diagnostic/form_A/git_sandbox status --short
```

应看到 CSV、observation、trace、一个 `settings.txt` 已修改且一个 `scratch.txt` 未跟踪。准备器若提示目录已存在，说明你已经有证据；不要覆盖，改做另一卷或明确另选 `--output`。

## 5. 五项任务与路由

### 任务 1：进程、stdout 与退出码

在 `shared/fixtures/day00/form_a.json` 中找到 `command` 数组并实际运行它。把观察到的卷号、去掉末尾换行的 stdout 和整数退出码写入 `artifacts/task1_process.json`。失败路由 F01/F05/F06。

优先检查：是否从根目录运行、是否把打印文本误当返回值、shell 是否吞掉非零退出码。

### 任务 2：CSV→JSON 与坏行

读取 `inputs/episodes.csv`。只接受 success 严格等于小写 `true` 或 `false` 的行；把有效行的 success 转成 JSON boolean，按原顺序写入 `normalized_episodes.json`。坏行写入 `rejected_rows.json`，至少含 CSV 行号和 episode_id。失败路由 F02/F03。

优先检查：表头算第 1 行；JSON 的 `true` 不是字符串；坏行不得静默进入有效输出。

### 任务 3：隔离 Git 仓库

进入 `git_sandbox`，只提交目标 `settings.txt`，提交信息必须以 `diagnostic:` 开头；`scratch.txt` 不应保留、暂存或进入提交。完成后仓库必须干净。失败路由 F04。

优先检查：`git status --short`、`git diff`、`git diff --cached`、`git ls-files`。不要对教材仓库做练习提交。

### 任务 4：NumPy shape/dtype/range

读取 `inputs/observation.json` 中每个数组的 values 和 dtype，用 NumPy 恢复数组。写出卷号，以及每个 key 的 shape（整数列表）、dtype、min、max 到 `task4_observation.json`。失败路由 F07/F09。

优先检查：外层/内层列表对应哪个轴；dtype 是否由输入指定；min/max 是数字而不是字符串。

### 任务 5：episode loop 语义

读取 `inputs/trace.json`，写出卷号、实际 step 数、终止类型、success boolean，并按顺序给出 `observation → policy → action → env.step → success` 到 `task5_episode.json`。失败路由 F08。

优先检查：timeout 与 success 不同；不能因为最后 `done=true` 就默认成功。

## 6. 机器验收与补习路线

```bash
.venv-day06/bin/python mainline/day00_diagnostic/code/grade_form.py \
  --form A \
  --workspace learner_outputs/mainline/day00_diagnostic/form_A
echo $?
.venv-day06/bin/python -m json.tool \
  learner_outputs/mainline/day00_diagnostic/form_A/diagnostic_result.json
```

- 退出码 `0` 且显示 `PASS: direct to mainline`：直接进入 Day 1。
- 退出码 `2`：只完成 `recommended_foundations` 中的模块快速路径，再用 B 卷复测。
- 评分器坏掉、缺 NumPy 或 Git 命令不可用：这是基础设施问题，先检查 F05/F06，不把它算成学习失败。

机器检查比较真实内容与 Git 历史，不只检查文件存在；A 卷产物不能通过 B 卷。

## 7. 延迟诊断 F10–F18

| 主线触发点 | 快问 | 失败路由 |
|---|---|---|
| 首次解释梯度 | 能说明 loss→backward→gradient 吗 | F10 |
| 首次短训练 | 能说明 loss→backward→update 吗 | F11 |
| 首次加载模型 | 能列出 Module/state_dict/checkpoint 区别吗 | F12 |
| 首次选 checkpoint | 能用 validation 而非 test 做选择吗 | F13 |
| 首次构造 L0 数据 | 能解释 Dataset、batch、shuffle 吗 | F14 |
| 首次追视觉编码 | 能追踪 H/W/C 到 feature map 吗 | F15 |
| 首次追语言输入 | 能区分 token、id、embedding 吗 | F16 |
| 首次追模型融合 | 能解释 query/key/value 的 shape 吗 | F17 |
| 首次追模型结构 | 能定位 attention、MLP、residual 吗 | F18 |

延迟项只有在对应主线日失败时才补，不要求 Day 0 提前全绿。

## 8. Day 0 自身测试

作者和维护者运行：

```bash
.venv-day06/bin/python -m unittest -v \
  mainline.day00_diagnostic.tests.test_diagnostic_router
.venv-day06/bin/python mainline/day00_diagnostic/code/diagnostic_router.py --check
```

测试会分别完成 A/B 卷，并验证复制 A 卷产物不能通过 B 卷。参考作答器和判分原则位于 `shared/answer_keys/`；首次诊断前不要打开。
