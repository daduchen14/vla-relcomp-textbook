# Day 1：终端、项目目录与第一段 Python 程序

> 阶段 1 / Day 1 of 70　　建议用时：7—8 小时　　第三方依赖：无

今天不安装 VLA-Arena、不下载模型，也不碰机器人仿真。今天只完成一件更基础、但以后每天都会重复的事：你在正确目录里输入一条命令，Python 接收参数、执行代码、在终端报告结果，并把一份可追溯的文件保存下来。

这看起来比“训练模型”朴素得多，却是整个 VLA-RelComp 项目的最小骨架。以后一次 episode 仍然遵循相同结构：输入是配置、指令与 seed；处理过程是模型推理和环境更新；输出是 success、动作、视频与日志。今天先把这个骨架缩小到一百行以内，确保每一行你都能解释。

## 1. 今天学完后你能做什么

完成本课后，你应该能够：

1. 用自己的话区分终端、shell、命令、程序和 Python 解释器；
2. 看懂 `pwd`、`cd`、`ls`、`python3`、`git status` 各自读取或改变什么；
3. 区分绝对路径、相对路径、仓库根目录、教程目录和个人输出目录；
4. 运行一个带命令行参数的 Python 文件，知道参数怎样进入变量；
5. 顺着 `输入 → 处理 → 输出 → 文件` 解释 `first_run.py`；
6. 从 traceback 或退出码开始定位一个故意制造的错误；
7. 保存自己的 Day 1 输出，而不把它误当成 VLA 模型结果。

## 2. 开始前自检

先不要查答案，在纸上写下你的猜测：

- `cd` 是在移动一个文件，还是在改变 shell 当前所在的目录？
- `python3 a.py --seed 7` 中，谁读取 `a.py`，谁读取 `--seed 7`？
- 如果同名脚本在两个目录里各有一份，输入 `python3 a.py` 会运行哪一份？
- Git 仓库与 GitHub 网页是同一个东西吗？

不知道完全正常。把答案留到本课末尾再改，不要先背术语。

## 3. 一个贯穿全课的场景

想象未来机器人收到一句指令：

```text
Move the red block to the left of the blue bowl.
```

真正的 VLA 程序会读取相机图像和这句话，产生动作，让环境前进一步，反复直到任务成功、失败或达到最大步数。今天没有图像、模型和环境，我们只把这句话与一个 `seed=7` 交给 Python，再保存一条状态为 `prepared` 的教学记录。

这里有一条必须从第一天养成的边界：`prepared` 只表示“教学程序运行并保存了记录”，不表示机器人成功，更不表示模型通过了实验。教材脚本也明确写入：

```text
result_type=synthetic teaching record; not a VLA experiment result
```

## 4. 概念课：终端里究竟发生了什么

### 4.1 终端、shell、命令与程序

把它们想成四层：

- **终端（terminal）**：你看到的文字窗口，负责显示字符和接收键盘输入；
- **shell**：在终端背后等待命令的程序。macOS 常见的是 `zsh`，Linux 常见 `bash`；
- **命令**：你交给 shell 的一行文本，例如 `pwd` 或 `python3 x.py`；
- **程序**：shell 找到并启动的可执行对象，例如 Git、Python 解释器，或由 Python 解释器读取的 `.py` 文件。

当你输入：

```bash
python3 day01/code/first_run.py --seed 7
```

可以按从左到右理解：

1. shell 找到名为 `python3` 的程序；
2. shell 把后面的文本作为参数交给 Python；
3. Python 打开 `first_run.py`，从上到下定义常量和函数；
4. Python 遇到文件末尾的 `if __name__ == "__main__":`，调用 `main()`；
5. `argparse` 从命令行读取 `--seed 7`；
6. 程序生成报告，打印摘要，并写入文件；
7. 程序用退出码 `0` 告诉 shell“成功完成”。

### 4.2 当前目录像一张“命令的出发地图”

shell 总有一个当前工作目录。`pwd` 是 “print working directory”，只负责告诉你现在在哪里；`cd` 是 “change directory”，负责换到另一个目录；`ls` 列出目录内容。

相对路径从当前目录出发：

```text
day01/code/first_run.py
```

绝对路径从文件系统根部出发，在 macOS/Linux 上以 `/` 开头。绝对路径更明确，但每台机器的用户名和克隆位置可能不同；课程命令统一先回到 Git 仓库根目录，再使用仓库内相对路径。

这也是为什么本课第一条定位命令是：

```bash
cd "$(git rev-parse --show-toplevel)"
```

先读懂，不必深挖 shell 语法：`git rev-parse --show-toplevel` 输出当前仓库根目录，`$(...)` 把这段输出交给 `cd`，双引号保证路径中即使有空格也被视为一个参数。

### 4.3 仓库、分支与工作目录不是一回事

- **工作目录**：你此刻能直接打开和编辑的文件；
- **Git 仓库**：工作目录加上 Git 保存的版本历史与状态；
- **分支**：指向某条版本历史末端的名称；
- **GitHub**：可以保存远端 Git 仓库、协作和展示的网络服务，不是 Git 本身。

本课程把 70 天教材放在独立教材仓库的教学分支。Day 1 只需要会读取分支名和工作区状态，不做提交、合并或推送。

`git status --short --branch` 的第一行可能形如：

```text
## content/day01-02
```

`##` 后面是当前分支名。以后你看到 `main` 时也不要自行改它；学习练习全部写入课程指定的个人输出目录。

### 4.4 Python 解释器与 Python 脚本

Python 代码不能仅靠文件扩展名自己运行。`python3` 是解释器：它读入源代码，把语法转换成可执行操作。

两种常见使用方式：

```bash
# 交互模式：适合快速算一行；输入 exit() 离开。
python3

# 脚本模式：适合保存、重复和追踪一个完整程序。
python3 path/to/program.py
```

科研项目主要使用脚本，因为“昨天手敲过什么”不是可靠证据；能保存、复跑、比较的代码才是。

### 4.5 变量、函数和主入口

今天只掌握三个最小概念：

- **变量**给一个值起名字，例如 `DEFAULT_SEED = 7`；
- **函数**把一段有明确职责的步骤装起来，例如 `build_report(...)`；
- **主入口**决定“直接运行文件”时从哪里开始，即 `if __name__ == "__main__":`。

函数像研究流程里的工位：一个函数解析参数，一个函数定位路径，一个函数构造报告，`main()` 负责安排顺序。拆函数不是为了显得高级，而是让出错时能回答“哪一步坏了”。

### 4.6 标准输出、标准错误与退出码

一个命令至少有三类结果：

- **标准输出 stdout**：正常信息，`print(...)` 默认写到这里；
- **标准错误 stderr**：错误信息，本课用 `file=sys.stderr` 写入；
- **退出码**：整数状态，通常 `0` 表示成功，非零表示失败。

终端运行完后可立即查看上一条命令的退出码：

```bash
echo $?
```

以后长时间实验首先看退出码和最早的错误信息，而不是只看最后一屏。

## 5. 认识今天的目录

从仓库根目录运行：

```bash
find . -maxdepth 3 -type f -not -path './.git/*' | sort
```

今天重点是：

```text

├── README.md
├── day01/
│   ├── README.md
│   └── code/
│       └── first_run.py
└── learner_outputs/
    └── .gitignore
```

`code/` 是教材提供、应该阅读的源代码；`learner_outputs/` 是你运行和修改的个人区域。两者分开，避免把生成结果和源代码混在一起。

## 6. 完整代码导读

完整程序在 [`code/first_run.py`](code/first_run.py)。文件中的每个有效语句都已有相邻注释。先完整打印它：

```bash
sed -n '1,240p' day01/code/first_run.py
```

不要一开始逐字背。先按执行顺序分成六块：

| 代码块 | 输入 | 输出 | 为什么这样写 |
|---|---|---|---|
| `import` | 标准库名称 | 可使用的模块 | 复用可靠工具，不手写参数解析与路径处理 |
| 常量 | 课程默认值 | 默认 instruction/seed | 默认值集中，之后容易修改 |
| `build_parser()` | 参数规则 | parser | 让 `--help`、类型检查和错误提示自动一致 |
| `locate_paths()` | `__file__` | 源文件与输出目录 | 输出位置不依赖你从哪个目录打开编辑器 |
| `build_report()` | instruction、seed、环境 | 多行字符串 | 把“内容生成”与“文件写入”分开 |
| `main()` | 命令行 | 终端文字、文件、退出码 | 明确控制程序的执行顺序 |

现在跟着一条数据走：终端里的 `--seed 42` 被 `argparse` 转成整数，存入 `args.seed`，传入 `build_report()`，通过 f-string 变成 `seed=42`，最后由 `write_text()` 写进 `first_run.txt`。

这就是最小的数据流追踪。以后 `success` 从仿真环境返回时，你也要能说出它经过哪些函数、以什么类型进入哪一列。

## 7. 逐步操作

### 步骤 1：回到仓库根目录并确认工具

```bash
cd "$(git rev-parse --show-toplevel)"
pwd
git branch --show-current
python3 --version
```

预期：

- `pwd` 末尾是当前仓库目录；
- 分支不是 `main`；
- Python 输出 `Python 3.x.y`。本课代码要求 Python 3.9 或更高；
- 这四条命令不会修改教材或实验数据。

### 步骤 2：先看帮助，不带参数运行

```bash
python3 day01/code/first_run.py --help
```

你应看到 `--instruction`、`--seed` 和它们的说明。`--help` 是命令行程序给使用者的最短契约：程序收什么、参数叫什么。

### 步骤 3：使用默认值完成第一次运行

```bash
python3 day01/code/first_run.py
```

预期输出的路径前缀会因机器而不同，其余结构应为：

```text
=== VLA-RelComp Day 1 ===
Python: 3.x.y
Instruction: Move the red block to the left of the blue bowl.
Seed: 7
Status: prepared (teaching record, not a VLA result)
Saved: .../learner_outputs/day01/first_run.txt
```

立刻查看退出码：

```bash
echo $?
```

预期为 `0`。

### 步骤 4：查看程序保存的证据

```bash
sed -n '1,80p' learner_outputs/day01/first_run.txt
```

逐行解释：

- `course` 与 `day` 说明这条记录属于哪里；
- `python_version` 记录运行环境的一小部分；
- `instruction` 和 `seed` 是本次输入；
- `status=prepared` 是程序真实做到的事情；
- `result_type` 阻止我们把合成教学记录冒充实验结果；
- `source_script` 指回生成它的代码。

### 步骤 5：用参数改变输入

```bash
python3 day01/code/first_run.py \
  --instruction "Place the tomato on the plate." \
  --seed 42
```

再次查看文件：

```bash
sed -n '1,80p' learner_outputs/day01/first_run.txt
```

预期 `instruction` 与 `seed` 已改变，代码文件本身没有改变。一次只改变输入而保留程序，是以后做对照实验的雏形。

### 步骤 6：确认个人输出没有混进教材修改

```bash
git status --short -- learner_outputs
```

预期没有输出，因为个人输出目录中的 `.gitignore` 忽略了运行产物。这里的目的只是学习“源代码”和“生成文件”的边界，不要求你提交任何内容。

## 8. 动手实验：你必须亲自改变什么

### 实验 A：只改变命令行参数

设计两次运行：instruction 保持相同，seed 分别使用 `7` 和 `8`。每次运行后，把 `first_run.txt` 中的 `seed=` 行抄到笔记里。

你应该观察到：记录变化了，但今天的程序没有真正使用随机数，因此终端不会出现机器人行为差异。结论只能是“程序成功记录了不同 seed”，不能说“两个 seed 的实验结果相同”。

### 实验 B：复制后修改自己的代码

不要改教材原件。先复制到个人目录：

```bash
cp day01/code/first_run.py \
  learner_outputs/day01/my_first_run.py
```

用编辑器打开 `my_first_run.py`，完成两处修改：

1. 把 `DEFAULT_SEED = 7` 改成 `DEFAULT_SEED = 2026`；
2. 把默认 instruction 改成你自己的空间关系指令，但必须包含目标物、关系和参照物。

然后运行：

```bash
python3 learner_outputs/day01/my_first_run.py
```

注意：复制后的 `source_script=` 会指向你的个人副本；因为本课指定的复制位置仍然恰好位于教程根目录下三级，`Saved:` 仍落在 `learner_outputs/day01/`。这说明 `__file__` 记录“当前文件在哪里”，而路径计算还取决于目录层级。把现象写入 `day01_notes.md`，不要急着重构；Day 3 之后再系统学习模块与路径设计。

### 实验 C：故意给 seed 一个错误类型

```bash
python3 day01/code/first_run.py --seed seven
echo $?
```

预期看到类似：

```text
error: argument --seed: invalid int value: 'seven'
```

退出码预期为 `2`。错误发生在 `argparse` 的类型转换阶段，所以 `main()` 还没进入写文件步骤。请用一句话回答：“为什么旧的 `first_run.txt` 可能仍然存在，但不能把它当成本次失败运行的新结果？”

## 9. 常见问题与止损

| 现象 | 先检查什么 | 处理方法 | 最长排错时间 |
|---|---|---|---:|
| `not a git repository` | 当前目录 | 先进入本仓库，再执行根目录定位命令 | 10 分钟 |
| `python3: command not found` | `which python3` | 记录完整输出；本日不自行混装多个 Python | 20 分钟 |
| `can't open file` | `pwd` 与相对路径 | 回仓库根目录，复制教程中的完整相对路径 | 10 分钟 |
| `Permission denied` 写文件 | `Saved:` 的父目录 | 查看目录是否属于当前用户；不要用 `sudo` 跑教材 | 20 分钟 |
| `invalid int value` | `--seed` 后面的值 | 改成十进制整数，如 `7` 或 `42` | 5 分钟 |
| 看见旧输出误以为本次成功 | 退出码和终端错误 | 先确认 `echo $?`，失败运行不生成新证据 | 5 分钟 |

超过止损时间后，保存：当前目录、完整命令、完整错误、退出码、最后一次成功步骤。不要只说“运行不了”。

## 10. 当日交付物与完成线

在 `learner_outputs/day01/` 中保存：

- 程序生成的 `first_run.txt`；
- 你复制并修改的 `my_first_run.py`；
- 自己创建的 `day01_notes.md`，写出 input、process、output、artifact 四项；
- 对实验 C 的一句话解释。

最低完成线：默认程序成功运行，能指出 instruction、seed 和输出文件。

标准完成线：完成 A/B/C 三个实验，能离开教程口述“shell 怎样启动 Python 脚本”，并能解释为什么 `prepared` 不是 `success`。

提前完成：在自己的副本中新增 `--learner-name` 参数，并让它进入报告。不要安装新库，不要开始 Day 2。

## 11. 自测题（先答，再展开答案）

### 题 1

`pwd`、`cd` 和 `ls` 的职责分别是什么？哪一个会改变 shell 状态？

**答案：** `pwd` 打印当前工作目录，`ls` 列出目录内容，`cd` 改变当前工作目录；三者中 `cd` 会改变 shell 的当前目录状态。

### 题 2

在 `python3 first_run.py --seed 7` 中，`python3`、`first_run.py`、`--seed 7` 分别扮演什么角色？

**答案：** `python3` 是解释器程序，`first_run.py` 是解释器要执行的源文件，`--seed 7` 是交给脚本的命令行参数；本课由 `argparse` 把文本 `7` 转成整数。

### 题 3

为什么课程先回到仓库根目录，再使用相对路径运行脚本？

**答案：** 相对路径以当前目录为出发点。统一出发点可让命令的含义稳定，也避免把某台机器的绝对用户名和克隆位置写死在教材里。

### 题 4

程序终端打印 `Status: prepared`，能否据此声称 VLA 完成了任务？

**答案：** 不能。该程序没有加载图像、模型或环境，`prepared` 只表示合成教学记录被构造并保存；源代码和报告都明确说明它不是 VLA 实验结果。

### 题 5

错误运行后为什么要同时看错误文字和退出码？

**答案：** 错误文字说明失败发生在哪里及原因，退出码让 shell 或自动化工具判断成功/失败。旧输出文件可能仍在，只有同时确认本次进程状态，才不会把旧文件误当成本次新结果。

## 12. 精确外部材料

正文已经覆盖今天的主干。外部材料只用于加深，不要求通读整本书。

| 材料 | 精确范围 | 用时 | 看完必须会什么 | 今天跳过 |
|---|---|---:|---|---|
| [Python 3.12 教程 §2.1 Invoking the Interpreter](https://docs.python.org/3.12/tutorial/interpreter.html#invoking-the-interpreter) | 从 §2.1 开头读到 §2.1.2 Interactive Mode 结束；重点看“脚本文件”和 argument passing | 25—35 分钟 | 解释交互模式、脚本模式、参数列表的区别 | §2.2 编码细节只知道默认 UTF-8 即可 |
| [Python 3.12 教程 §3.1.2 Text 与 §3.2 First Steps](https://docs.python.org/3.12/tutorial/introduction.html#first-steps-towards-programming) | 先看 §3.1.2 的字符串，再看 §3.2 的赋值与 `while` 示例；不要求抄 Fibonacci | 30—40 分钟 | 看懂字符串、变量、缩进、`print()` | 列表切片与复杂运算留到 Day 2 |
| [Pro Git §1.1 About Version Control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control) | 读开头定义与 Local Version Control Systems 之前的第一部分 | 15—20 分钟 | 说明“保存版本历史”为什么比复制 `final_v2_new.py` 可靠 | 集中式/分布式历史细节 |
| [Pro Git §1.3 What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F) | 只读 Snapshots, Not Differences 与 Nearly Every Operation Is Local | 20—25 分钟 | 用“快照”和“本地操作”解释 Git 的基本心智模型 | Git 完整内部对象模型 |

材料完成标准不是“网页看过了”，而是合上网页后能回答：Python 解释器如何接收脚本和参数？Git 保存的核心对象更像文件差异列表还是项目快照？

## 13. 连接到 VLA-RelComp

Day 1 没有训练任何 AI，但已经建立未来研究的四个固定位置：

```text
instruction / seed          -> 输入
Python 函数                 -> 处理
终端摘要 / 退出码           -> 即时状态
first_run.txt               -> 可保存证据
```

到 Day 37 以后，这四项会扩展为：

```text
配置 / 图像 / instruction / seed
  -> VLA policy + 仿真环境
  -> action / success / exception
  -> CSV / JSON / 日志 / 视频
```

复杂度会大幅增加，基本纪律不变：先知道从哪个目录运行、输入是什么、程序真实做了什么、产物写到哪里，以及它允许你下什么结论。
