# Day 2：Python 数据结构、CSV/JSON 与第一份实验记录程序

> 阶段 1 / Day 2 of 70　　建议用时：8—9 小时　　第三方依赖：无

昨天的程序只保存一条纯文本。真正的 VLA-RelComp 会运行许多 episode：不同任务、L0/L1/L2、seed、是否成功、执行步数，都必须按同一结构保存。今天把六条**合成教学 episode** 读入 Python，完成类型检查、分组统计，并同时输出逐条 CSV 和汇总 JSON。

今天仍然不加载模型、不运行仿真。你得到的 `50.0%` 是教材人为写入六行数据后算出的结果，不能引用为 SmolVLA、OpenVLA 或 VLA-Arena 的成绩。

## 1. 今天学完后你能做什么

完成本课后，你应该能够：

1. 区分字符串、整数、布尔值、列表和字典，说明它们分别适合表示什么；
2. 解释“一个 episode 是字典，许多 episode 是列表”的含义；
3. 说明 CSV 为什么适合逐行记录，JSON 为什么适合嵌套汇总；
4. 使用 `csv.DictReader` 读取表头，把每行转换为字典；
5. 发现“CSV 中的 `7` 最初仍是字符串”，并显式转换类型；
6. 使用循环按 `level` 分组，计算成功数与成功率；
7. 用输入检查拒绝空 ID、负数和不合法 success，而不是静默猜测；
8. 改一行数据，事先手算，再运行程序验证自己的预测。

## 2. 前置检查

Day 1 标准完成线是本课前置。先运行：

```bash
cd "$(git rev-parse --show-toplevel)"
python3 foundation_library/f01_terminal_python/code/first_run.py --seed 7
echo $?
```

只有退出码为 `0` 才继续。然后在纸上回答：

- 六次 episode 应该写成六个互不相关的变量，还是一个容器？
- 同一条 episode 里，`task_id`、`seed`、`success` 用位置 0/1/2 表示好，还是用字段名表示好？
- CSV 里的字符 `"0"` 与 Python 的整数 `0`、布尔值 `False` 是否完全相同？
- 如果 L0 有 2 次成功、L1 有 1 次、L2 有 0 次，只报“总共成功 3 次”遗漏了什么？

## 3. 今天的数据：六条合成 episode

教材输入文件是 [`data/mini_episodes.csv`](data/mini_episodes.csv)：

```csv
episode_id,level,task_id,seed,relation,success,steps
fixture_001,0,fixture_l0_pick_tomato_on_bowl,7,on,1,74
fixture_002,0,fixture_l0_put_mug_left_plate,11,left,1,82
fixture_003,1,fixture_l1_pick_tomato_on_bowl,7,on,0,120
fixture_004,1,fixture_l1_put_mug_left_plate,11,left,1,96
fixture_005,2,fixture_l2_pick_tomato_on_bowl,7,on,0,120
fixture_006,2,fixture_l2_put_mug_left_plate,11,left,0,120
```

第一行是表头，后面六行每行代表一次 episode。字段含义：

| 字段 | Python 中希望得到的类型 | 本课含义 |
|---|---|---|
| `episode_id` | `str` | 记录的唯一名字；`fixture_` 表明它是合成教学数据 |
| `level` | `int` | 组合泛化层级编号 0/1/2；这里只作分组标签 |
| `task_id` | `str` | 教学任务名，不是官方任务注册表中的正式 ID |
| `seed` | `int` | 随机性编号；本课只记录，不运行随机过程 |
| `relation` | `str` | 空间关系，如 `on`、`left` |
| `success` | `bool` | `1` 转为 `True`，`0` 转为 `False` |
| `steps` | `int` | 教学设定的执行步数 |

为什么反复强调“合成”？因为表格形式很像真结果。没有运行环境、模型和 success 判定，就不能仅凭一行 `success=1` 说模型成功。数据工程不仅是把数字写进文件，也包括维护数字的证据边界。

## 4. 概念课：怎样在 Python 中表示实验

### 4.1 标量：一格数据的类型

今天最常见的四个标量类型：

```python
episode_id = "fixture_001"  # str：文字
level = 0                   # int：整数
success = True              # bool：真/假
success_rate = 0.5          # float：小数
```

类型决定可做的操作。整数 `7 + 1` 得到 `8`；字符串 `"7" + "1"` 得到 `"71"`。CSV 是文本文件，`DictReader` 读出的单元格默认都是字符串，所以程序必须把 `level`、`seed`、`steps` 转成整数，把 `success` 严格转成布尔值。

“看起来像数字”不等于“已经是数字”。这是实验脚本里极常见的错误来源。

### 4.2 列表：许多同类对象的有序集合

六条 episode 都有相同结构，适合放进列表：

```python
episodes = [episode_1, episode_2, episode_3]
```

列表有顺序，可以逐条循环，可以追加新记录，可以用 `len(episodes)` 得到数量。程序中的类型提示：

```python
list[dict[str, object]]
```

从外向内读：这是一个列表；列表的每个元素是字典；字典 key 是字符串；value 可能是多种对象。

### 4.3 字典：用字段名找到值

一条 episode 不是“第 0 格是 ID、第 1 格是 level”的无名序列，而是有语义的字段集合：

```python
episode = {
    "episode_id": "fixture_001",
    "level": 0,
    "success": True,
}
```

访问 `episode["success"]` 比访问 `episode[2]` 更清楚。字典 key 像表格列名；value 是当前行在该列的值。

真实 VLA-RelComp episode 会有更多字段：模型 revision、suite、init state、目标物、参照物、四段状态事件、视频路径、异常等。Day 2 只取其中最小的七列，先学会结构，再逐步扩展。

### 4.4 CSV：扁平、逐行、适合表格分析

CSV 的优势：

- 一行一条 episode，很容易追加、筛选和导入电子表格；
- 每列含义由表头固定；
- 人和大量工具都能读取；
- 特别适合后期按 task、level、seed 做表格统计。

CSV 的限制：

- 单元格读入时通常是文本，类型需要另行约定；
- 不擅长表示“一个 level 下面还有多个指标”这类嵌套结构；
- 逗号、引号、换行有正式转义规则，不能可靠地用 `line.split(",")` 处理所有 CSV。

所以本课使用标准库 `csv`，不手写逗号切分。

### 4.5 JSON：键值清楚、适合嵌套汇总

今天的汇总天然有层级：总体指标下面还有 `levels`，`levels` 下面又有 L0、L1、L2，每组再有 episodes、successes、success_rate。JSON 很适合这种结构：

```json
{
  "total_episodes": 6,
  "overall_success_rate": 0.5,
  "levels": {
    "L0": {"episodes": 2, "successes": 2, "success_rate": 1.0}
  }
}
```

把 Python 对象写成 JSON 文本叫**序列化**；从 JSON 文本恢复为 Python 对象叫**反序列化**。本课使用 `json.dump()` 写文件。

JSON 中的对象对应 Python 字典，数组对应列表，`true/false` 对应 `True/False`。JSON 的 key 必须是字符串，所以程序把整数 level 明确写成 `"L0"`、`"L1"`、`"L2"`。

### 4.6 schema：大家对字段的共同约定

schema 可以先理解为“数据应该有哪些列、每列叫什么、允许什么类型和值”。没有 schema 时，以下写法都可能混在一起：

```text
success = 1
success = yes
success = TRUE
success = 成功
```

它们表达相近，却会让程序分支复杂、统计不稳定。本课约定 `success` 只能是 `0` 或 `1`；程序遇到 `yes` 会直接报出行号和字段，而不是猜成 True。

拒绝坏数据不是对学习者苛刻，而是在最便宜的时刻暴露问题。假如错误混入一万条 GPU episode 后才发现，重跑成本会非常高。

### 4.7 循环与累加器

总体成功数的思路是：从 0 开始，逐条看 episode，成功就加 1。程序用生成式写成：

```python
total_successes = sum(bool(item["success"]) for item in episodes)
```

分 level 统计需要多个计数器：

```text
levels = {
  0: {episodes: 2, successes: 2},
  1: {episodes: 2, successes: 1},
  2: {episodes: 2, successes: 0}
}
```

每读一条，先找到它所属的 bucket（桶），再把 episodes 加 1，把 success 的 0/1 加入 successes。最后 `successes / episodes` 得到该组成功率。

### 4.8 平均数为什么可能掩盖问题

六条数据总体是 `3/6 = 50%`，但分组为：

- L0：`2/2 = 100%`
- L1：`1/2 = 50%`
- L2：`0/2 = 0%`

只看总体 50%，看不到难度随 level 变化。真实研究还要按 task、seed、模型和 intervention 分层，并报告不确定性；今天先学会最基本的分组计数，不提前展开统计推断。

## 5. 完整代码导读

完整程序在 [`code/episode_recorder.py`](code/episode_recorder.py)，所有有效语句都有相邻注释。先完整阅读：

```bash
sed -n '1,360p' foundation_library/f02_csv_json/code/episode_recorder.py
```

按数据流分成八步：

| 步骤 | 函数/对象 | 作用 |
|---:|---|---|
| 1 | `FIELDNAMES` | 定义七个必需列 |
| 2 | `build_parser()` | 定义输入 CSV 和输出目录 |
| 3 | `parse_integer()` | 把文本变成非负整数，坏值报行号 |
| 4 | `parse_success()` | 只接受 `0/1` 并转为布尔值 |
| 5 | `load_episodes()` | `DictReader` 逐行读成字典列表 |
| 6 | `summarize()` | 计算总体与分 level 指标 |
| 7 | 两个 `write_...()` | 保存规范逐条 CSV 与汇总 JSON |
| 8 | `main()` | 串起流程、处理错误、给出退出码 |

### 5.1 为什么函数很多

如果全部写进 `main()`，短期少几行，长期却难以回答：是文件没打开、字段缺失、类型转换失败、分组公式错误，还是写文件失败？职责拆开后，每个函数能用一句话描述，而且后面可以单独测试。

### 5.2 为什么不用 pandas

Pandas 很适合后续分析，但 Day 2 先使用 Python 标准库，目的是让你亲眼看到：CSV 读出字符串、字典怎样进入列表、循环怎样累加。等你掌握底层数据流，再用 DataFrame 才不会把错误藏在一行 API 后面。

### 5.3 为什么捕获错误后返回 1

程序只捕获预期的文件/数据错误，打印 `[ERROR] ...`，再返回 `1`。这让人能看懂，也让自动脚本知道失败。它没有写一个宽泛的 `except Exception:` 假装所有问题都一样。

## 6. 逐步操作

### 步骤 1：查看原始 CSV

```bash
cd "$(git rev-parse --show-toplevel)"
sed -n '1,20p' foundation_library/f02_csv_json/data/mini_episodes.csv
```

手工检查：共 1 行表头、6 行数据；所有 episode_id 都以 `fixture_` 开头；success 只有 0/1；level 有 0/1/2。

### 步骤 2：先手算，不要先看程序答案

在纸上填表：

| 分组 | episode 数 | success 数 | success rate |
|---|---:|---:|---:|
| 总体 |  |  |  |
| L0 |  |  |  |
| L1 |  |  |  |
| L2 |  |  |  |

再计算总 steps。正确数字稍后会由程序显示；先预测可以防止“程序有输出，所以一定对”的错觉。

### 步骤 3：查看命令行接口

```bash
python3 foundation_library/f02_csv_json/code/episode_recorder.py --help
```

你应看到：

- `--input-csv`：要读取的数据文件；
- `--output-dir`：两个结果文件保存到哪里；
- 两者都有默认值，因此第一遍可不传参数。

### 步骤 4：运行完整程序

```bash
python3 foundation_library/f02_csv_json/code/episode_recorder.py
echo $?
```

除绝对路径外，预期输出为：

```text
Loaded 6 synthetic teaching episodes.
Overall success: 3/6 = 50.0%
L0: 2/2 = 100.0%
L1: 1/2 = 50.0%
L2: 0/2 = 0.0%
Saved normalized CSV: .../learner_outputs/foundation_library/f02_csv_json/normalized_episodes.csv
Saved summary JSON: .../learner_outputs/foundation_library/f02_csv_json/summary.json
```

退出码应为 `0`。把输出与你的手算比较。若不一致，先重新数原始行，不要先改程序迎合答案。

### 步骤 5：检查规范 CSV

```bash
sed -n '1,20p' \
  learner_outputs/foundation_library/f02_csv_json/normalized_episodes.csv
```

它应与输入表达相同的七列和六条记录。规范化的价值不是“数字变神奇”，而是所有值已经经过程序的 schema 与类型检查，然后用标准 CSV writer 重新输出。

### 步骤 6：用 Python 自带工具检查 JSON

```bash
python3 -m json.tool \
  learner_outputs/foundation_library/f02_csv_json/summary.json
```

重点找到：

```json
"dataset_kind": "synthetic teaching fixture; not a VLA result"
"total_episodes": 6
"total_successes": 3
"overall_success_rate": 0.5
"total_steps": 612
```

`python3 -m json.tool` 能成功格式化，说明文件是合法 JSON；这并不能单独证明统计逻辑正确，所以仍要和手算对照。

### 步骤 7：把最小字段映射到真实项目协议

本课七列在冻结实验协议的完整 episode registry 中都有对应位置：

| Day 2 字段 | 完整 registry 中的意义 | 后续会补什么 |
|---|---|---|
| episode_id | 全局 episode 标识 | run_id、timestamp |
| level/task_id | suite 内难度与任务 | suite、init_state_index |
| seed | 随机性复现入口 | code/model/data revision |
| relation | CBDDL 登记的空间关系 | target/reference object |
| success | 最终 goal predicate 结果 | 四段状态事件 |
| steps | 轨迹长度 | wall time、显存、证据路径、异常 |

今天只理解数据形状，不填写不存在的真实字段。字段允许暂时没有，不允许凭猜测补齐。

## 7. 动手实验：先预测，再改变一项

所有实验都先复制输入，不改教材原件：

```bash
mkdir -p learner_outputs/foundation_library/f02_csv_json
cp foundation_library/f02_csv_json/data/mini_episodes.csv \
  learner_outputs/foundation_library/f02_csv_json/my_episodes.csv
```

### 实验 A：新增一个失败 episode

用编辑器在 `my_episodes.csv` 末尾新增：

```csv
fixture_007,1,fixture_l1_move_can_right_box,19,right,0,110
```

运行到独立输出目录：

```bash
python3 foundation_library/f02_csv_json/code/episode_recorder.py \
  --input-csv learner_outputs/foundation_library/f02_csv_json/my_episodes.csv \
  --output-dir learner_outputs/foundation_library/f02_csv_json/experiment_a
```

运行前先预测。正确预期是：

- 总体：`3/7 = 42.9%`；
- L1：`1/3 = 33.3%`；
- L0、L2 不变；
- `total_steps` 从 612 变成 722。

如果只看成功次数，仍是 3；如果看成功率，因为分母增加，结果下降。这是计数与比率的区别。

### 实验 B：只改变一行 success

重新从教材 CSV 复制一份，命名为 `flip_success.csv`。把 `fixture_006` 的 success 从 `0` 改为 `1`，其他格保持不变。运行到 `experiment_b/`。

运行前预测：总体应为 `4/6 = 66.7%`，L2 应为 `1/2 = 50.0%`，总 steps 仍为 612。若总 steps 变化，说明你不小心改了第二个因素。

这只是数据处理练习。你不能把手工把 0 改成 1 描述成“模型修复成功”；真实 success 必须由冻结的环境判定和原始证据支持。

### 实验 C：让坏数据被明确拒绝

重新复制一份，命名为 `bad_success.csv`。把任意一行 success 改成 `yes`，然后运行：

```bash
python3 foundation_library/f02_csv_json/code/episode_recorder.py \
  --input-csv learner_outputs/foundation_library/f02_csv_json/bad_success.csv \
  --output-dir learner_outputs/foundation_library/f02_csv_json/experiment_c
echo $?
```

预期：终端出现包含行号、`success`、`0 or 1` 和 `yes` 的 `[ERROR]`；退出码为 `1`。程序不会把 `yes` 猜成成功。

### 实验 D：独立代码修改

把 `episode_recorder.py` 复制为个人副本 `my_episode_recorder.py`。在 `summarize()` 返回字典中新增：

```python
"failed_episode_ids": [
    str(item["episode_id"])
    for item in episodes
    if not bool(item["success"])
],
```

每行的含义：创建一个新 key；列表推导逐条访问 episodes；保留 success 为 False 的记录；把 ID 统一转成字符串。运行后，默认数据应得到 `fixture_003`、`fixture_005`、`fixture_006` 三个 ID。

这段修改只写入你的个人副本。你必须能把列表推导改写成普通 `for` 循环口述出来；不能只复制后看到 JSON 多一列就算完成。

## 8. 常见错误与止损

| 现象 | 根因候选 | 诊断顺序 | 最长排错时间 |
|---|---|---|---:|
| `CSV is missing required fields` | 表头拼错或少列 | 打印第一行，与 `FIELDNAMES` 逐字比较 | 15 分钟 |
| `must be an integer` | 数字列混入文字/小数 | 看错误行号与字段，不要全表乱改 | 10 分钟 |
| `must be 0 or 1` | success 用了 yes/True/空值 | 回到 schema，只保留 0/1 | 10 分钟 |
| `teaching episode_id must start...` | 个人行没有 fixture_ | 补前缀；不要冒充真实 ID | 5 分钟 |
| JSON 中 `0.5` 不是 `50` | 比率用 0—1 表示 | 显示时用百分号，文件保留数值 0.5 | 5 分钟 |
| 修改一行却多个指标变化 | 同时改了多个字段 | 与教材原 CSV 逐行比较 | 15 分钟 |
| 输出目录里留有旧文件 | 上次成功、本次失败 | 先看退出码和本次终端信息 | 10 分钟 |

不要通过删除输入检查“让程序先跑起来”。如果超过止损时间，保存输入文件副本、完整命令、错误行号、退出码和你预期的 schema。

## 9. 当日交付物与完成线

在 `learner_outputs/foundation_library/f02_csv_json/` 中应有：

- 默认运行产生的 `normalized_episodes.csv` 与 `summary.json`；
- `my_episodes.csv` 及 `experiment_a/` 输出；
- `flip_success.csv` 及 `experiment_b/` 输出；
- `bad_success.csv` 和错误信息笔记；
- `my_episode_recorder.py` 以及含 `failed_episode_ids` 的 JSON；
- `day02_notes.md`：写清列表、字典、CSV、JSON、schema 各自解决什么问题。

最低完成线：默认程序成功，能解释总体 50% 与 L0/L1/L2 三个比例怎样算出。

标准完成线：完成 A—D，能独立说明 CSV 单元格为什么要转换类型，能解释为什么总体指标不能替代分组指标。

提前完成：给个人脚本增加 `--level 1` 可选过滤参数；输出必须同时记录过滤条件。不要安装 pandas，不要开始深度学习。

## 10. 自测题（3—5 题要求：本课共 5 题）

### 题 1

为什么“许多 episode”适合用列表，而“一条 episode 的多个字段”适合用字典？

**答案：** 列表表示同类对象的有序集合，方便追加和逐条循环；字典用有含义的 key 映射 value，能以 `episode["success"]` 访问字段，比依赖位置更清楚。

### 题 2

CSV 文件里看到 `seed=7`，`DictReader` 读出后为什么仍要调用 `int()`？

**答案：** CSV 是文本格式，`DictReader` 默认把单元格读成字符串。字符串 `"7"` 与整数 `7` 的运算语义不同，必须按 schema 显式转换并检查。

### 题 3

CSV 和 JSON 在本课分别保存什么？为什么不只用一种？

**答案：** CSV 保存逐条、扁平、列固定的 episode；JSON 保存总体下面再分 L0/L1/L2 的嵌套汇总。两者分别适合表格记录和层级对象，没有一种在所有结构上都最清楚。

### 题 4

默认数据总体成功率是多少？如果只看总体，会漏掉什么？

**答案：** 总体 `3/6=50%`。它会漏掉 L0 为 100%、L1 为 50%、L2 为 0% 的层级差异，因此不能定位结果随难度的变化。

### 题 5

把 CSV 中 `success=0` 手工改为 `1` 后，能否说模型性能提升？为什么？

**答案：** 不能。手工改值只改变教学输入，没有运行模型、环境和 success predicate，也没有原始日志/视频证据。它只能证明统计程序对输入变化作出了预期响应。

## 11. 精确外部材料

| 材料 | 精确范围 | 用时 | 看完必须会什么 | 今天跳过 |
|---|---|---:|---|---|
| [Python 3.12 教程 §3.1.3 Lists](https://docs.python.org/3.12/tutorial/introduction.html#lists) | 阅读列表创建、索引、切片、拼接、`append` 与嵌套列表示例 | 25—35 分钟 | 创建列表、取元素、追加一条 episode | 高级切片技巧 |
| [Python 3.12 教程 §5.5 Dictionaries](https://docs.python.org/3.12/tutorial/datastructures.html#dictionaries) | 完整阅读 §5.5 | 20—30 分钟 | 创建字典、按 key 取值、判断 key 是否存在 | 集合与元组专题 |
| [Python 3.12 教程 §5.6 Looping Techniques](https://docs.python.org/3.12/tutorial/datastructures.html#looping-techniques) | 阅读 `items()`、`enumerate()`、`zip()` 和 `sorted()` 示例 | 25—35 分钟 | 解释本课为什么用 `for level, counts in sorted(levels.items())` | 列表比较规则 |
| [Python 3.12 `csv` 文档：Module Contents、DictReader、DictWriter](https://docs.python.org/3.12/library/csv.html#module-contents) | 从 Module Contents 读 `reader()`，再定位 `DictReader`、`DictWriter.writeheader()`、`writerow()` | 35—45 分钟 | 说明 `newline=""`、表头到字典、标准 writer 的意义 | dialect 自定义与 QUOTE_* 常量 |
| [Python 3.12 `json` 文档：Basic Usage](https://docs.python.org/3.12/library/json.html#basic-usage) | 看 Python-to-JSON 转换表与 `dump/load`；动手读 `indent`、`ensure_ascii` 参数 | 25—35 分钟 | 把字典写成缩进 JSON，并解释序列化/反序列化 | 自定义 JSONEncoder、命令行全部选项 |

材料完成标准：不看代码，画出 `CSV 文本 → DictReader 字符串字典 → 类型化 episode 字典 → episodes 列表 → summary 字典 → JSON` 的箭头图。

## 12. 连接到 VLA-RelComp

今天建立的不是最终 registry，而是最终数据管线的缩影：

```text
一行 episode CSV
  -> 字段存在性检查
  -> 字符串转 int/bool
  -> 一条字典
  -> 多条组成列表
  -> 按 level 分组
  -> 逐条 CSV + 汇总 JSON
```

真实项目会把七列扩展到完整证据：

```text
run / code / model revision
suite / level / task / seed / init
instruction / target / relation / reference
四段行为事件 / success / steps / wall time
video / log / result / exception / notes
```

但“字段越多”不等于“研究越可信”。可信来自三个条件：字段定义清楚，值来自真实可追溯过程，统计时保留 task/level/seed 等关键分层。Day 2 先把这三件事的编程基础扎牢。
