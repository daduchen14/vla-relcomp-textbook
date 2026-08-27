# Day 5：Linux 文件、进程、环境变量与退出码

> 阶段 1 / Day 5 of 70　　建议用时：7—9 小时　　第三方依赖：无

Day 4 用 Git 回答“代码是什么版本”。但将来同一个 commit 在两台机器上运行，仍可能因为操作系统、Python 路径、环境变量或磁盘空间不同而得到不同现象。今天学习程序运行所依赖的系统外壳：文件与目录、进程、标准输入输出、环境变量和退出码，并写一个不会泄露密钥的系统快照工具。

本课命令兼容 macOS 与常见 Linux shell；课程后半段的 GPU 环境会是 Linux/NVIDIA。今天不安装 Linux、不租服务器、不运行 GPU，也不把本机元数据当作 VLA 结果。

## 1. 学完后你能做什么

1. 用绝对/相对路径、目录、普通文件和权限解释一条命令为什么能或不能访问资源；
2. 区分程序文件与正在运行的进程；
3. 区分 stdout、stderr、退出码以及重定向；
4. 理解环境变量如何由父进程传给子进程，为什么不能把所有变量写进日志；
5. 用 `ps` 查看进程，用 `kill` 发送温和终止信号，并设置止损；
6. 运行 `system_snapshot.py` 保存非敏感系统入口信息；
7. 解释“主脚本成功记录了一个失败探针”为什么主退出码仍可以为 0。

## 2. 前置检查与今天做什么

从仓库根目录开始：

```bash
cd "$(git rev-parse --show-toplevel)"
python3 day04/code/git_evidence.py
python3 --version
pwd
```

今天新增：

```text
day05/code/minimal_process.py
day05/code/system_snapshot.py
day05/tests/test_system_snapshot.py
learner_outputs/day05/system_snapshot.json   # 运行后生成，不提交
```

开始前先预测：脚本文件存在时，它是否一直是进程？把 stdout 重定向到文件后，stderr 会一起进去吗？子进程返回 3 是否必然要求负责记录它的父程序也返回 3？

## 3. 今天学什么概念

### 3.1 文件系统是一棵有名字的树

macOS/Linux 路径从根目录 `/` 开始。`/Users/...` 或 `/home/...` 是绝对路径；`day05/code` 是从当前工作目录解释的相对路径。`.` 代表当前目录，`..` 代表父目录。目录不是“装文件的图标”，而是一组名字到对象的映射。

常用只读命令：

```bash
pwd                         # 当前工作目录
ls -la day05                # 包含隐藏项的长格式列表
find day05 -maxdepth 3 -type f | sort
file day05/code/system_snapshot.py
```

`ls -l` 左侧类似 `-rw-r--r--`：第一位说明对象类型，后面三组分别是 owner、group、others 的读/写/执行权限。Python 源文件只要由 `python3 file.py` 读取，通常不要求文件自己具有执行权限；如果写 shebang 后直接 `./file.py`，才涉及执行位和解释器路径。今天统一显式调用 `python3`。

符号链接可以让一个路径指向另一个对象。`Path.resolve()` 会解析为规范绝对路径，但路径变化或链接策略也可能影响结果。因此实验记录既要保存逻辑资源名，也要保存经过确认的实际版本，不能只凭“我在那个文件夹里”。

### 3.2 程序与进程

磁盘上的 `python3` 是程序；启动后，操作系统创建一个进程。进程有 PID、当前目录、打开的文件、环境变量和退出状态。一个程序可同时对应多个进程，例如两个终端分别运行 Python。

shell 通常是父进程，Python 是它启动的子进程；Python 还可以通过 `subprocess` 启动另一个子进程。环境变量默认从父进程复制给子进程，但子进程修改自己的环境不会倒流改变父 shell。

查看当前 shell 与 Python 进程：

```bash
echo "shell_pid=$$"
ps -p $$ -o pid=,ppid=,stat=,command=
python3 -c 'import os; print("python_pid=", os.getpid(), "parent_pid=", os.getppid())'
```

具体 PID 每次不同。`PPID` 是父进程 ID。不要把教材示例数字当作预期固定输出。

### 3.3 前台、后台与信号

前台进程占用当前终端，通常由你等待；命令末尾加 `&` 可让 shell 把它放到后台：

```bash
python3 -c 'import time; print("fixture_started", flush=True); time.sleep(30)' &
fixture_pid=$!
echo "$fixture_pid"
ps -p "$fixture_pid" -o pid=,stat=,command=
```

`$!` 是最近后台进程 PID。完成观察后发送默认 `TERM`：

```bash
kill "$fixture_pid"
wait "$fixture_pid"
echo $?
```

`TERM` 请求程序有机会清理；不要一开始用 `kill -9`。真实训练卡住时也先保存日志、确认 PID 和子进程，再逐级终止。今天的练习最多等待 2 分钟；找不到 PID 时不要用模糊的批量 kill。

### 3.4 stdout、stderr 与退出码是三条通道

正常结果写 stdout，诊断/错误写 stderr，退出码是一个整数状态。三者相互独立：程序可以在 stderr 写警告后仍返回 0，也可以 stdout 有部分结果后返回非零。

shell 重定向示例：

```bash
python3 day05/code/minimal_process.py \
  > learner_outputs/day05/stdout.txt \
  2> learner_outputs/day05/stderr.txt
echo $?
```

`>` 重定向文件描述符 1（stdout），`2>` 重定向文件描述符 2（stderr）。`>>` 是追加，`>` 会覆盖目标，所以正式实验使用唯一 run 目录，避免覆盖旧证据。

退出码通常 0 表示命令按自身契约完成，非零表示某种失败；具体非零含义由程序定义。`echo $?` 必须紧跟目标命令，否则看到的是中间另一条命令的退出码。

### 3.5 父进程怎样处理子进程失败

`subprocess.run(..., check=False)` 会返回 `CompletedProcess`，让父程序读取 `returncode`；`check=True` 遇到非零会抛 `CalledProcessError`。没有哪一种永远正确：

- 若子命令是主任务不可缺的步骤，通常用 `check=True` 立即失败；
- 若目的就是观察不同退出码，应用 `check=False` 并明确记录。

本课快照工具的 probe 是被研究的对象。即使 probe 按要求返回 3，只要父程序完整记录了 3，快照任务本身仍成功并返回 0。这类似评测器成功记录“episode 失败”：模型任务失败不等于记录基础设施失败。二者必须使用不同字段。

### 3.6 环境变量：进程启动时的外部配置

查看一个明确变量：

```bash
printf 'SHELL=%s\n' "${SHELL:-unset}"
printf 'LANG=%s\n' "${LANG:-unset}"
```

临时只对一条命令设置变量：

```bash
FIXTURE_MODE=careful python3 -c 'import os; print(os.environ["FIXTURE_MODE"])'
```

`export NAME=value` 会让当前 shell 后续启动的子进程继承该变量；关闭终端后是否保留取决于 shell 配置文件。API token 常通过环境变量传递，但这不意味着可以打印 `env` 或把 `dict(os.environ)` 写入日志。

今天工程脚本只允许读取 `LANG`、`SHELL`、`TERM`、`VIRTUAL_ENV` 四个键。白名单比“排除我想到的几个 secret 名”安全，因为密钥名称无法穷举。真正项目还应在输出进入 Git 前检查敏感信息。

### 3.7 系统快照能证明什么

本课记录 OS、release、CPU 架构、Python 版本与解释器路径、仓库根、当前目录、磁盘剩余字节、白名单环境变量和一个探针。它能帮助回答“入口环境是否明显不同”，不能完整复现 CUDA、驱动、Python 包、模型权重或仿真器。Day 6 会继续记录 Python 环境与依赖；GPU 章节再加入 `nvidia-smi` 等信息，并明确实际运行状态。

## 4. 先运行 25 行最小版本

```bash
mkdir -p learner_outputs/day05
sed -n '1,160p' day05/code/minimal_process.py
python3 day05/code/minimal_process.py
echo $?
```

预期：

```text
stdout=fixture_stdout
stderr=fixture_stderr
returncode=0
0
```

前三行由父 Python 打印，最后的 0 是父程序退出码。打开源码，把 `run_child(exit_code=0)` 复制到个人副本后改为 3。预测：内部 `returncode` 变 3，但脚本末尾没有 `SystemExit(3)`，所以 shell 看到的仍是 0。这正是“观察对象状态”和“观察程序状态”的区别。

## 5. 工程版完整导读与操作

完整代码在 [`code/system_snapshot.py`](code/system_snapshot.py)。按以下顺序打印：

```bash
sed -n '1,110p' day05/code/system_snapshot.py
sed -n '111,240p' day05/code/system_snapshot.py
```

数据流为：命令行参数 → Git 定位根目录 → 平台/磁盘/白名单环境读取 → 可控 probe 子进程 → dataclass → JSON。脚本用参数列表调用子进程，不启用 shell，从而避免额外的字符串解释层。

查看接口并运行：

```bash
python3 day05/code/system_snapshot.py --help
python3 day05/code/system_snapshot.py --probe-exit-code 0
echo $?
sed -n '1,160p' learner_outputs/day05/system_snapshot.json
```

预期终端显示 OS、Python、probe return code 0 和输出路径。macOS 可能显示 `Darwin arm64`，Linux 可能显示 `Linux x86_64`；以本机实测为准。JSON 的 `safe_environment` 中不存在的键为 `null`，不表示空字符串。

再运行一个“被成功记录的失败探针”：

```bash
python3 day05/code/system_snapshot.py --probe-exit-code 3
echo $?
```

终端应显示 `Probe return code: 3`，随后 shell 的主程序退出码仍是 0。打开 JSON，stdout/stderr/returncode 应分开保存。

## 6. 自动化测试

```bash
python3 -m unittest -v day05.tests.test_system_snapshot
python3 -m py_compile \
  day05/code/minimal_process.py \
  day05/code/system_snapshot.py \
  day05/tests/test_system_snapshot.py
```

预期两个测试均 `ok`，末尾 `OK`；`py_compile` 成功时没有输出。第一个测试实际启动退出码为 3 的免费本地子进程；第二个在隔离环境字典中放入 `SECRET_TOKEN`，证明白名单结果不含该键。它只证明当前函数行为，不能证明所有日志工具都不会泄密。

## 7. 动手实验

### 实验 A：先预测三条通道

复制最小脚本到 `learner_outputs/day05/my_process.py`，把子进程 exit code 改成 2。先写下父脚本 stdout、stderr 和 shell `$?` 的预测，再分别重定向运行。查看两个文件，解释为什么子进程 stderr 最终由父程序作为普通文字打印到了父 stdout。

### 实验 B：白名单变量

运行：

```bash
FIXTURE_MODE=careful python3 day05/code/system_snapshot.py
rg 'FIXTURE_MODE' learner_outputs/day05/system_snapshot.json || true
```

先预测。预期找不到，因为 `FIXTURE_MODE` 不在白名单。这不是脚本没收到变量，而是它主动不保存。不要把变量加入白名单，除非能说明它为何安全且与复现有关。

### 实验 C：从子目录启动

```bash
cd day05/code
python3 system_snapshot.py --probe-exit-code 1
cd "$(git rev-parse --show-toplevel)"
```

预测仓库根和默认输出是否仍正确。预期脚本用 Git 和 `__file__` 定位，仍写入根下 `learner_outputs/day05`；JSON 的 current directory 则诚实记录 `day05/code`。

### 实验 D：观察后台进程生命周期

按 §3.3 启动 30 秒 fixture sleep，记录 PID，用 `ps` 确认存在，再用默认 `kill` 和 `wait` 结束。预测 `wait` 的非零退出码。写下“收到信号退出”与“程序内部报错”的区别；二者都可能非零，但证据不同。

### 实验 E：磁盘单位转换

JSON 的 `free_bytes` 是字节。先预测除以 `1024**3` 后约有多少 GiB，再运行：

```bash
python3 -c 'import json; from pathlib import Path; d=json.loads(Path("learner_outputs/day05/system_snapshot.json").read_text()); print(round(d["free_bytes"] / 1024**3, 2), "GiB")'
```

结果只是采集时刻的可用空间，会变化。它能提醒下载前检查容量，不能作为永久硬件规格。

## 8. 常见错误与止损

| 现象 | 先检查与处理 | 止损时间 |
|---|---|---:|
| `command not found` | `command -v python3`，检查拼写与 PATH | 15 分钟 |
| `Permission denied` | 是读取、写入还是直接执行；不要盲目 `chmod 777` | 20 分钟 |
| 重定向后终端“没输出” | 查看目标 stdout/stderr 文件 | 10 分钟 |
| `$?` 与预期不符 | 是否紧跟目标命令，中间是否跑了 `echo/ls` | 10 分钟 |
| 后台进程仍存在 | 核对精确 PID，先 TERM 并 wait | 2 分钟 |
| JSON 出现疑似密钥 | 停止提交/推送，删除产物并撤销密钥 | 立即停止 |
| 非 Git 目录快照失败 | 回到仓库根或传正确 `--start` | 10 分钟 |

不要用管理员权限掩盖路径问题，不要把 shell 初始化文件整份上传排错，也不要运行来源不明的安装脚本。

## 9. 与 VLA-RelComp 的连接

未来 evaluator 本身是父进程，模型服务、仿真器或编码器可能是子进程。一次 episode 的 `success=false`、模型子进程 OOM、渲染器崩溃、外层调度命令失败是四类不同事件，不能都写成“实验失败”。至少要保存：哪个进程、stdout/stderr、退出码、异常字段和是否生成有效结果。

环境变量会携带缓存目录、离线模式、设备选择或认证信息。记录配置时采用白名单与脱敏；密钥只用于授权访问，永远不是可复现产物。磁盘空间检查则会在以后下载模型前成为免费预检，但未经授权不会触发下载。

Day 6 将在今天的系统层上加入虚拟环境、Python 包和依赖版本，并练习把“系统找不到程序”和“Python 找不到包”分开诊断。

## 10. 检查点与答案

### 题 1

源文件和进程有什么区别？

**答案：** 源文件是磁盘上的持久数据；进程是操作系统运行程序时创建的实例，具有 PID、环境、打开文件和退出状态。同一程序可同时有多个进程。

### 题 2

为什么 stderr 有内容不必然等于退出码非零？

**答案：** stderr 是文字通道，程序可用它写警告；退出码是独立状态。必须同时读取，不能靠“是否出现红字”判断成功。

### 题 3

为何快照脚本不保存所有环境变量？

**答案：** 环境中可能含 token、密钥和个人路径。完整保存会泄密；应只记录与复现有关且确认安全的白名单键。

### 题 4

probe 返回 3，而 `system_snapshot.py` 返回 0 是否矛盾？

**答案：** 不矛盾。probe 是被观察子任务，它按要求返回 3；父程序成功捕获并保存三条通道，所以快照任务完成。真实项目也要区分 episode 失败与记录器失败。

### 题 5

为什么终止进程前要确认精确 PID？

**答案：** 模糊匹配可能杀死无关程序或其他实验。先用 `ps` 核对 PID/命令，再发送温和信号并等待清理，证据更明确且风险更低。

## 11. 完成标准

**最低完成线：** 运行最小脚本、默认快照与两个测试；能区分 stdout、stderr、退出码和进程。

**标准完成线：** 完成 A—E；能解释白名单环境策略、父子进程状态和路径；保存 JSON、重定向文件和个人笔记。

**当天产物：** 教材中的最小进程脚本、系统快照工具和测试；个人目录中的系统 JSON、两条流文件、进程观察与磁盘换算笔记。

## 12. 精确外部材料

| 材料 | 今天阅读范围 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [GNU Coreutils manual §2 Common options](https://www.gnu.org/software/coreutils/manual/html_node/Common-options.html) | 读 `--help`、`--version`、`--`，20 分钟 | 安全查看命令契约与终止选项解析 | locale 与 block size 细节 |
| [GNU Bash manual §3.6 Redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html) | 读开头、Redirecting Output、Redirecting Error，30 分钟 | 看懂 `>`、`2>` 与文件描述符 | here document 与自定义 FD |
| [GNU Bash manual §3.7.4 Environment](https://www.gnu.org/software/bash/manual/html_node/Environment.html) | 全节，15 分钟 | 父 shell 如何准备子进程环境 | shell startup 文件细节 |
| [Python 3.12 `subprocess` §Using the subprocess Module](https://docs.python.org/3.12/library/subprocess.html#using-the-subprocess-module) | 读 `run()` 参数中的 args/check/capture_output/text，30 分钟 | 解释本课子进程调用 | `Popen` 管道高级用法 |
| [Python 3.12 `os.environ`](https://docs.python.org/3.12/library/os.html#os.environ) | 读 `os.environ` 条目及 `getenv()`，15 分钟 | 知道 Python 如何读取环境 | bytes 环境与平台差异 |
| [Linux man-pages `signal(7)`](https://man7.org/linux/man-pages/man7/signal.7.html) | 读 Description 与 Standard signals 中 SIGTERM/SIGKILL，25 分钟 | 区分请求终止与强制终止 | 实时信号、内核 ABI |

`signal(7)` 描述 Linux；macOS 名称和基本概念相近，但细节以本机 `man 7 signal` 为准。今天只操作自己启动的 fixture 进程。
