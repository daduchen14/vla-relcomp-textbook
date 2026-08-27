# Day 3：函数、模块、路径与可测试的数据校验

> 阶段 1 / Day 3 of 70　　建议用时：7—9 小时　　第三方依赖：无

Day 2 已经能把 CSV 读成 Python 数据并生成汇总。但“这次得到正确输出”还不等于程序长期可靠：如果别人把 `level` 写成 `9`、重复使用一个 episode ID，或者从另一个目录启动程序，会发生什么？今天把读取、校验、写出拆成职责明确的函数，用模块组织代码，并第一次用自动化测试证明重要规则确实生效。

今天仍然只处理 `fixture_` 合成教学数据。程序打印的条数和 JSON 都不是 VLA-Arena 或任何模型的实验成绩。

## 1. 学完后你能做什么

完成本课后，你应该能够：

1. 区分“调用函数”和“定义函数”，说明参数、返回值和异常各自传递什么；
2. 解释模块为什么比复制粘贴函数可靠，以及 `import` 时 Python 大致做了什么；
3. 使用 `Path(__file__)` 定位教材资源，不把正确性押在当前工作目录上；
4. 把 CSV 的字符串行转换为字段类型明确的 `Episode`；
5. 区分单行校验、整表校验和跨行唯一性校验；
6. 使用 `unittest` 自动验证正常输入与三种错误输入；
7. 读懂失败测试，先定位“哪条契约被破坏”，而不是盲目改代码。

## 2. 前置检查与今天的产物

先从仓库根目录运行 Day 2：

```bash
cd "$(git rev-parse --show-toplevel)"
python3 day02/code/episode_recorder.py
echo $?
```

退出码应为 `0`。今天会继续读取 `day02/data/mini_episodes.csv`，并新增：

```text
day03/
├── README.md
├── code/
│   ├── __init__.py
│   ├── minimal_schema.py
│   └── episode_schema.py
└── tests/
    └── test_episode_schema.py
```

运行后还会产生 `learner_outputs/day03/validated_manifest.json`。它是个人练习输出，已被 Git 忽略。

开始前先预测：如果 CSV 中 `seed` 是文本 `"7"`，表达式 `"7" + "1"` 得到什么？如果两个 episode 使用相同 ID，逐行类型检查能发现吗？把猜测写在纸上，暂时不要查答案。

## 3. 今天学什么概念

### 3.1 函数是带契约的小机器

函数不是单纯“把代码缩短”。可以把它想成一台写明接口的小机器：参数是入口，返回值是正常出口，异常是拒绝不合法输入的出口。例如：

```python
def parse_non_negative_int(text: str, field: str, row_number: int) -> int:
    ...
```

它承诺接收一段文本、字段名和行号，成功时返回非负整数；失败时报告具体行与字段。类型标注 `str` 和 `int` 是给读者和工具看的说明，不会自动阻止错误数据，因此函数内部仍须校验。

为什么不让一个 `main()` 包办一切？因为当“读文件、转类型、查重复、写 JSON”混在一起时，你很难只测试其中一条规则。拆开以后，`parse_row()` 不需要真的写文件，`build_manifest()` 不需要知道 CSV 怎样打开，测试可以用一行极小输入指出问题。

在 VLA-RelComp 中同样如此：读取 observation、调用 policy、把 action 交给环境、提取状态事件和保存记录应有清楚边界。否则 success 统计错了，你无法判断是模型、环境还是记录器造成的。

### 3.2 参数、返回值与异常不是同一条路

调用：

```python
episode = parse_row(row, row_number=2)
```

数据流是：调用者把 `row` 与 `2` 传入；函数校验并构造对象；正常时返回 `Episode`，名字 `episode` 接住它。如果 CSV 中出现 `level=9`，函数不应该偷偷改成 L0，也不应该返回半成品，而应抛出 `SchemaError`。上层可以捕获并决定如何向终端报告。

异常的价值是“拒绝继续制造看似正常的错误结果”。科研记录尤其不能静默猜测。未知字段可以按协议留空，但已定义为必填或枚举的字段必须失败得清楚。

今天用自定义 `SchemaError(ValueError)`，因为它既表达“值不符合数据契约”，又让命令行能够只捕获预期的数据错误。`raise ... from error` 保留原始整数转换错误作为原因；初学阶段只需知道它没有把底层线索抹掉。

### 3.3 模块让定义只有一个来源

一个 `.py` 文件就是一个最常见的 Python 模块。`episode_schema.py` 集中保存 `Episode`、合法 level、读取函数和命令行入口；测试通过：

```python
from day03.code.episode_schema import SchemaError, load_episodes, run
```

复用这些定义。测试不再复制一份校验逻辑，因此当正式代码改变时，它测试的仍是同一份实现。

`__init__.py` 告诉 Python：这些目录按常规 package 组织。今天只需要会从仓库根目录执行测试，让仓库根目录位于模块搜索路径。暂时不要修改 `sys.path`；到大型工程阶段会使用正式安装方式。

模块底部：

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

表示直接运行文件时才调用 `main()`；被测试导入时只加载定义，不自动读写 CSV。这个边界是“可测试”的关键。

### 3.4 路径：当前目录与脚本位置

相对路径 `day02/data/mini_episodes.csv` 从 shell 的当前目录解释。如果在仓库外运行，路径会失效。`__file__` 则指当前模块文件；本课使用：

```python
repo_root = Path(__file__).resolve().parents[2]
```

路径层级是 `仓库/day03/code/episode_schema.py`：`parents[0]` 是 `code`，`parents[1]` 是 `day03`，`parents[2]` 才是仓库根。然后用 `/` 运算符拼路径。这里的 `/` 不是除法，而是 `Path` 提供的路径组合语法。

这种写法解决“从哪里启动”的问题，但不是宇宙通用方案：如果随意移动文件，固定的 `parents[2]` 仍会错。因此仓库结构也是程序契约的一部分。未来安装成 package 后会学习更正式的资源定位。

### 3.5 schema 是数据契约，不只是表头

Day 2 的 CSV 有七列。schema 不仅回答“有哪些列”，还回答：

- 哪些字段必填；
- 每个字段最终是什么类型；
- 哪些取值合法；
- 字段之间或多行之间有什么约束；
- 违反规则时怎样失败。

今天分三层检查：

1. **整表结构**：必须有七个必需列，且至少有一条数据；
2. **单行规则**：ID 以 `fixture_` 开头，CSV 的 level 属于 0/1/2（读入后规范为 L0/L1/L2），seed/steps 是非负整数，success 只能为 0/1；
3. **跨行规则**：episode ID 不能重复。

“重复 ID”无法靠只看一行发现，必须用 `seen` 集合记住已经出现的值。这一思想以后会保护真实 registry：重复 episode 如果被当成两次独立试验，成功率与置信区间都会失真。

### 3.6 dataclass：让一条记录的字段显式化

字典灵活，但 `row["succes"]` 拼错一个字母只会在运行到那一行时出错。`@dataclass` 根据字段声明生成初始化等常用方法：

```python
@dataclass(frozen=True)
class Episode:
    episode_id: str
    seed: int
    success: bool
```

`frozen=True` 表示构造后不能随手改字段，适合表示“已经校验通过的输入事实”。它不是数据库，也不自动完成校验；校验仍在 `parse_row()` 中。`asdict()` 用于写 JSON 前转回普通字典。

### 3.7 测试不是“跑一下没报错”

手动运行一次只能证明某个输入走通。自动化测试把“应当怎样”保存成可重复执行的例子。本课四个测试分别证明：

- 合法数据会转类型并写出 manifest；
- 非 `fixture_` ID 被拒绝；
- 非法 level 9 被拒绝；
- 重复 episode ID 被拒绝。

一个测试最好只聚焦一条行为。测试使用 `TemporaryDirectory()` 创建会自动清理的临时目录，所以不会把测试垃圾写入仓库。`assertRaisesRegex` 同时检查异常类型和错误信息中的关键词。

测试通过不等于程序无错，只说明这些明确写出的行为目前成立。研究代码要问的不是“有没有测试”而是“测试覆盖了哪项风险”。

## 4. 先运行 30 行最小版本

先打印并阅读：

```bash
sed -n '1,200p' day03/code/minimal_schema.py
python3 day03/code/minimal_schema.py
```

预期输出形如：

```text
{'episode_id': 'fixture_001', 'level': 'L0', 'seed': 7, 'success': True, 'steps': 74}
```

准确 steps 以 fixture CSV 第一行为准。请注意引号：CSV 原始值都是字符串，经过 `parse_row()` 后 `seed` 和 `steps` 没有引号，`success` 是 `True`。最小版让你看清“读一行 → 校验 → 转类型”，但它还没有检查表头、task ID、重复 ID，也没有友好的命令行错误处理。

执行语法检查：

```bash
python3 -m py_compile day03/code/minimal_schema.py
```

没有输出且退出码为 `0`，表示 Python 能解析语法；它不证明业务规则正确。

## 5. 从最小版扩展到工程版

完整代码位于 [`code/episode_schema.py`](code/episode_schema.py)。先分段阅读：

```bash
sed -n '1,100p' day03/code/episode_schema.py
sed -n '101,220p' day03/code/episode_schema.py
```

按调用方向理解：

```text
main
 └─ run
     ├─ load_episodes
     │   └─ parse_row
     │       ├─ require_non_empty
     │       └─ parse_non_negative_int
     ├─ ensure_unique_ids
     └─ build_manifest
```

这不是让你背函数名，而是学会出错时沿调用链缩小范围：文件打不开先看 `load_episodes`；某一字段类型错看 `parse_row`；重复 ID 看 `ensure_unique_ids`；JSON 结构不对看 `build_manifest`。

先查看接口：

```bash
python3 day03/code/episode_schema.py --help
```

再运行默认输入：

```bash
python3 day03/code/episode_schema.py
echo $?
```

预期：

```text
=== VLA-RelComp Day 3 ===
Result type: synthetic teaching data; not a VLA result
Validated episodes: 6
Levels: L0, L1, L2
Saved: .../learner_outputs/day03/validated_manifest.json
0
```

查看产物：

```bash
sed -n '1,100p' learner_outputs/day03/validated_manifest.json
```

确认 `episode_count` 为 6、每个 `success` 是 JSON 的 `true/false` 而非字符串、每条记录都有真实性声明。这个 manifest 在后续可作为“输入已通过当前 schema”的证据，但它仍不是模型结果。

## 6. 第一次运行自动化测试

从仓库根目录执行：

```bash
python3 -m unittest -v day03.tests.test_episode_schema
```

预期看到四个以 `test_` 开头的名字，末尾为：

```text
Ran 4 tests in ...s

OK
```

时间数字随机器变化。`OK` 表示四条已写明的契约通过。若看到 `FAILED` 或 `ERROR`，先找最上方第一个失败测试名，再看 traceback 最靠近本仓库代码的行。给自己 20 分钟定位；超过止损时间，恢复刚才改动并重跑原测试，不要同时改多个函数。

## 7. 动手实验

### 实验 A：修改合法 level

先预测：Day 2 的 CSV 用数字保存 level。把个人 CSV 第一行的 `0` 改成 `2`，校验会失败还是通过？manifest 的 `levels` 会怎样？

```bash
mkdir -p learner_outputs/day03
cp day02/data/mini_episodes.csv learner_outputs/day03/my_episodes.csv
```

用编辑器只改第一条数据的 level，然后运行：

```bash
python3 day03/code/episode_schema.py \
  --input learner_outputs/day03/my_episodes.csv \
  --output learner_outputs/day03/my_manifest.json
```

预期通过，因为输入值 2 合法，并在内存中规范为 L2；`levels` 仍包含三种值，因为其他行仍含 0（规范为 L0）。含义是“schema 保证格式合法”，不保证你的实验设计合理。数据契约不能替代研究协议。

### 实验 B：制造非法 level 9

把刚才那一格改成 `9`。运行前预测退出码和是否生成新 JSON，再运行相同命令并执行：

```bash
echo $?
```

预期 stderr 指出具体 CSV 行及 `level='9'`，退出码为 `2`。程序在写出前失败，因此不会用半合法数据覆盖 manifest。若旧 JSON 已存在，它可能仍保留上次内容，所以证据不能只看“文件存在”，还要记录本次命令与退出码。

### 实验 C：让一个测试故意失败

不要改教材原件，先复制：

```bash
cp day03/tests/test_episode_schema.py \
  learner_outputs/day03/my_test_episode_schema.py
```

把 `self.assertEqual(manifest["episode_count"], 1)` 中的 `1` 改成 `2`。预测失败信息会显示哪个 expected/actual，再运行：

```bash
python3 -m unittest -v learner_outputs/day03/my_test_episode_schema.py
```

预期只有合法数据测试失败，并显示 `1 != 2`；其他三个仍通过。这说明测试能把错误限制到某条期望。完成后改回 `1`，重跑并恢复 `OK`。

### 实验 D：增加一条真正的新规则

在个人测试副本中添加一个测试：把 `steps` 改成 `-1`，断言抛出包含“不能为负数”的 `SchemaError`。先运行确认现有工程代码已经满足它。然后口述：为什么 steps 不能为负，但可以为 0？零步可能代表初始化后立即终止或基础设施异常，是否应计入模型失败要由后续实验协议决定；schema 只负责保留合法数值，不擅自归因。

## 8. 常见错误与止损

| 现象 | 先检查 | 常见原因 | 止损时间 |
|---|---|---|---:|
| `ModuleNotFoundError: day03` | `pwd` 与仓库根 | 在 `day03/tests` 内启动测试 | 10 分钟 |
| `FileNotFoundError` | `--input` 实际路径 | 相对路径从当前目录解释 | 15 分钟 |
| `IndexError` 出现在 `parents[2]` | 脚本是否被移动 | 复制到了不同目录层级 | 15 分钟 |
| 测试发现 0 个用例 | 文件名、类与方法名 | 方法未以 `test_` 开头 | 15 分钟 |
| 修改错误数据却仍看到旧 JSON | 退出码与文件时间 | 失败时旧输出不会自动删除 | 10 分钟 |
| 一次出现许多失败 | 最早失败与刚才唯一改动 | 同时改了 fixture 和代码 | 20 分钟 |

不要通过删除校验、把异常改成 `pass` 或把错误值自动换成默认值来“修好”测试。若 30 分钟仍无法恢复，重新复制教材测试到个人目录，从一次只改一行开始。

## 9. 与 VLA-RelComp 的连接

今天的 `Episode` 只有七个字段。真实项目将逐步加入 model revision、suite、init state、原始/变体指令、intervention、目标物、参照物、relation、四段事件、墙钟、显存和证据路径。今天先练习的三类约束会直接迁移：

- 字段类型错误会破坏统计或排序；
- 不合法枚举会把同一 level 拆成多个组；
- 重复 episode 会让样本数和置信区间虚高。

更重要的是，校验器只说明“数据符合契约”，不能说明“模型真的运行”“任务定义正确”或“success 可信”。证据链需要版本、日志、视频、环境状态和上游 success predicate 共同支持。程序边界越清楚，后面越容易定位失败来自哪一层。

Day 4 会把今天的代码和规则放入 Git 的版本模型中，学习如何用 commit 与 diff 回答“哪次改动改变了什么”。

## 10. 检查点与答案

### 题 1

为什么类型标注 `seed: int` 不能代替 `int(text)` 和错误检查？

**答案：** Python 的普通类型标注主要服务读者、编辑器和静态工具，运行时不会自动把 CSV 字符串变成整数，也不会自动拒绝负数。程序仍须显式转换并验证业务约束。

### 题 2

为什么重复 episode ID 不能只在 `parse_row()` 中判断？

**答案：** `parse_row()` 一次只看到当前行，不知道之前出现过哪些 ID。跨行唯一性需要在整组 episode 上维护 `seen` 集合或类似索引。

### 题 3

直接运行模块和在测试中导入模块时，`if __name__ == "__main__"` 有什么作用？

**答案：** 直接运行时 `__name__` 为 `__main__`，会执行命令行入口；导入时它是模块名，只加载类和函数，不自动读写文件，因此测试可以安全复用定义。

### 题 4

四个测试都通过，能否宣称数据校验器没有 bug？

**答案：** 不能。只能说四个测试明确覆盖的行为在当前环境通过。缺列、空文件、非法整数等其他路径虽由实现处理，但若要把它们作为稳定承诺，还应增加对应测试。

### 题 5

为什么一次失败运行后看到旧 JSON 不能证明本次成功？

**答案：** 程序在写出前失败时不会删除上次成功生成的文件。必须结合本次命令、退出码、终端日志和文件时间判断，不能只看路径存在。

## 11. 完成标准

**最低完成线：** 最小版和工程版均退出 `0`；能指出 CSV 字符串在哪里转为 `int/bool`；四个原始测试全部通过。

**标准完成线：** 完成实验 A—D；能口述函数调用链；解释 schema、测试与研究真实性的边界；保存 `validated_manifest.json` 和个人实验笔记。

**当天产物：** 教材源码中的两个校验器和测试；个人目录中的 manifest、错误实验 CSV、测试副本与笔记。只有源码/测试属于教材，个人输出不提交。

## 12. 精确外部材料

| 材料 | 今天精确阅读范围 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [Python 3.12 教程 §4.9 Defining Functions](https://docs.python.org/3.12/tutorial/controlflow.html#defining-functions) | 从函数定义读到 §4.9.3 Special parameters 之前，约 25 分钟 | 参数、默认值、返回值和 docstring | `/`、`*` 的复杂参数规则以后再学 |
| [Python 3.12 教程 §6 Modules](https://docs.python.org/3.12/tutorial/modules.html#modules) | §6 开头至 §6.1.1，重点看 `__name__`，约 25 分钟 | 模块、导入和直接运行的区别 | compiled modules 与 `dir()` 细节 |
| [Python 3.12 `pathlib` §Basic use](https://docs.python.org/3.12/library/pathlib.html#basic-use) | 只运行 Basic use 中构造路径、`/` 拼接、遍历的例子，约 20 分钟 | 不用手拼斜杠地操作路径 | 全部类层级和 URI 方法 |
| [Python 3.12 `dataclasses`](https://docs.python.org/3.12/library/dataclasses.html#module-contents) | 读介绍、`@dataclass` 参数中的 `frozen`，并查 `asdict()`，约 20 分钟 | 知道本课自动生成了什么 | ordering、slots、继承 |
| [Python 3.12 `unittest` §Basic example](https://docs.python.org/3.12/library/unittest.html#basic-example) | Basic example 与 Command-Line Interface 的 `-v` 示例，约 30 分钟 | 会组织并运行一个 TestCase | mock、异步测试、测试发现高级参数 |

阅读顺序是函数 → 模块 → pathlib → dataclass → unittest。每看完一项，都回到今天代码找到对应的一处真实用法；不要连续读完整章再开始敲代码。
