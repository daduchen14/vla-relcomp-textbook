# Day 6：Python 环境、包、依赖锁定与异常

> 阶段 1 / Day 6 of 70　　建议用时：7—9 小时　　当前安装成本：0 元

Day 5 已经能回答“哪个 Python 进程在什么系统上运行”。今天继续追问：这个 Python 到底从哪里来？它能看到哪些包？为什么终端明明执行过安装，脚本仍然说找不到模块？我们会创建一个免费的本地虚拟环境，练习模块/发行包/版本的区别，并用异常把“可选依赖缺失”与“必需依赖缺失”分开。

本课不会下载第三方包。所有必需依赖都是 Python 标准库；`fixture_package_not_installed` 是故意不存在的教学名字，不是真实软件，也不需要搜索或安装。

## 1. 学完后你能做什么

1. 区分 Python 解释器、模块、包、发行包和依赖；
2. 使用 `python3 -m venv` 创建、激活、验证和退出隔离环境；
3. 解释为什么应使用 `python -m pip` 而不是盲目信任单独的 `pip`；
4. 区分“直接依赖声明”和“当前环境完整快照”；
5. 读懂 `ModuleNotFoundError`、异常链和 traceback 的定位顺序；
6. 用 `environment_doctor.py` 检查当前解释器及 fixture 依赖清单；
7. 知道什么时候不能擅自升级包或在全局环境中安装。

## 2. 前置检查与目录

从仓库根目录执行：

```bash
cd "$(git rev-parse --show-toplevel)"
python3 foundation_library/f05_linux_processes/code/system_snapshot.py
command -v python3
python3 -c 'import sys; print(sys.executable)'
```

后两条通常指向同一解释器，但 shell alias、环境管理器或激活状态可能让它们不同。今天新增：

```text
foundation_library/f06_environments_dependencies/config/fixture_requirements.json
foundation_library/f06_environments_dependencies/code/minimal_import_check.py
foundation_library/f06_environments_dependencies/code/environment_doctor.py
foundation_library/f06_environments_dependencies/tests/test_environment_doctor.py
```

个人虚拟环境统一放在 `.venv-foundation_library/f06_environments_dependencies/`，根 `.gitignore` 已忽略 `.venv*`。运行报告写入 `learner_outputs/foundation_library/f06_environments_dependencies/`，都不提交。

## 3. 今天学什么概念

### 3.1 解释器不是抽象的“Python”

输入 `python3` 时，shell 按 PATH 找到一个可执行文件。它有具体绝对路径、版本、标准库和第三方包搜索目录。两条终端命令看似都叫 Python，可能实际指向系统 Python、Homebrew Python、Conda 环境或虚拟环境。

在程序中：

```python
import sys
print(sys.executable)
print(sys.version)
print(sys.prefix)
print(sys.base_prefix)
```

`sys.executable` 是当前解释器路径。在普通环境中，prefix 与 base_prefix 通常相同；标准 `venv` 激活后，prefix 指虚拟环境而 base_prefix 指创建它的基础 Python。因此本课用二者是否不同判断虚拟环境，不仅看提示符有没有括号。

### 3.2 模块、package 与 distribution

- **模块 module**：可被 `import` 的代码单元，最简单就是一个 `.py` 文件；
- **导入包 package**：组织多个模块的 Python 命名空间；
- **发行包 distribution**：安装工具管理、带版本元数据的发布物；
- **依赖 dependency**：当前项目运行或开发所需要的外部能力。

它们的名字不必相同。例如发行包常用连字符，导入名可能用下划线；一个发行包可以提供多个导入模块。`importlib.util.find_spec("name")` 回答当前解释器能否定位模块，`importlib.metadata.version("distribution")` 查询已安装发行包版本。不能把二者名字想当然地互换。

`json` 和 `unittest` 属于标准库，随解释器提供，没有需要 pip 管理的独立 distribution 版本。本课清单把它们的 `distribution` 设为 `null`。

### 3.3 import 到底在哪里找

执行 `import x` 时，Python 根据导入系统与 `sys.path` 查找。`sys.path` 通常包含脚本位置、标准库、当前环境的 site-packages 等。常见 `ModuleNotFoundError` 原因包括：

1. 包确实没装；
2. 装到了另一个 Python；
3. 导入名写错；
4. 从错误目录运行本地模块；
5. 本地文件名遮蔽第三方模块，例如自己建了 `json.py`；
6. 安装中断或依赖版本不兼容。

诊断顺序应先记录 `sys.executable` 和失败 import，再用同一个解释器执行 `-m pip --version`/`show`。不要第一反应全局 `pip install`，那会扩大不确定性。

### 3.4 虚拟环境隔离了什么

虚拟环境为一个项目提供独立解释器入口和 site-packages，让项目 A 的包版本不必覆盖项目 B。它不是虚拟机：仍共享操作系统、CPU、驱动和基础 Python 的部分能力，也不会自动锁定 CUDA 或系统库。

创建与激活：

```bash
python3 -m venv .venv-day06
source .venv-foundation_library/f06_environments_dependencies/bin/activate
python -c 'import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)'
python -m pip --version
```

Windows PowerShell 的激活命令不同；本项目后期面向 Linux，教程统一使用 POSIX shell。激活主要修改当前 shell 的 PATH；关闭终端后需重新激活。更稳妥的自动化命令可以直接使用 `.venv-foundation_library/f06_environments_dependencies/bin/python`，不依赖激活状态。

退出：

```bash
deactivate
```

删除虚拟环境不会删除源码，但删除仍是有影响操作；学习者可在确认路径精确且无需保留后自行处理。本教材不会自动删除它。

### 3.5 为什么使用 `python -m pip`

单独输入 `pip` 时，shell 也会按 PATH 寻找，可能对应另一个解释器。`python -m pip` 表示让刚刚选定的 Python 运行它环境里的 pip：

```bash
python -c 'import sys; print(sys.executable)'
python -m pip --version
```

两条输出中的环境路径应该协调。今天只运行 `--version`、`list`、`freeze` 等只读命令，不升级 pip、不访问网络、不安装包。

### 3.6 声明依赖与锁定快照

“项目需要什么”和“我的环境恰好装了什么”不是同一问题：

- `requirements.in`、`pyproject.toml` 等可以表达人类选择的直接依赖和范围；
- lock 文件记录解析后的精确版本与可能的哈希，目标是让安装可重复；
- `pip freeze` 罗列当前环境中可见的发行包，包含传递依赖，也可能夹带与项目无关的包。

所以不要在一个用了很久的全局环境中 `pip freeze > requirements.txt` 就宣称获得了最小依赖。后续会在隔离环境、上游锁定版本和实际验证之间建立清晰关系。

今天的 `fixture_requirements.json` 是教学清单：显式写 module、distribution、required 和 reason。它不是 pip 安装文件，不会触发网络；目的是先学会“声明”和“观察”分离。

### 3.7 异常、错误信息与 traceback

异常是程序无法按当前契约继续时传递的结构化对象。例：

```python
try:
    import fixture_package_not_installed
except ModuleNotFoundError as error:
    print(type(error).__name__, error)
```

捕获应尽量具体。`except Exception: pass` 会把真实缺依赖伪装成正常运行。可选依赖缺失可以记录为 unavailable 并继续；必需依赖缺失必须让 `ready=false` 并返回非零。

traceback 从调用链展示异常传播。初学时先看最后一行的异常类型和消息，再从下往上找第一处属于自己项目的文件/行号。修复最早、最具体的原因后重跑，不要同时根据十几行猜十几个问题。

`raise EnvironmentCheckError(...) from error` 会在提供领域友好说明的同时保留原始原因。这样日志既能告诉学习者“清单无法读取”，也能追溯底层 JSON 或文件错误。

## 4. 先运行约 20 行最小版本

```bash
sed -n '1,120p' foundation_library/f06_environments_dependencies/code/minimal_import_check.py
python3 foundation_library/f06_environments_dependencies/code/minimal_import_check.py
echo $?
```

预期结构：

```text
python=/.../python3
required:json=True
optional:fixture_package_not_installed=False
0
```

解释：必需标准库可定位，可选 fixture 模块不可定位；程序仍准备就绪，因此返回 0。`find_spec` 不导入模块代码，适合轻量存在性检查，但它不能证明模块导入后的全部功能正常。

## 5. 工程版逐步操作

完整代码在 [`code/environment_doctor.py`](code/environment_doctor.py)，清单在 [`config/fixture_requirements.json`](config/fixture_requirements.json)。先看清单，再按函数边界阅读：

```bash
sed -n '1,160p' foundation_library/f06_environments_dependencies/config/fixture_requirements.json
sed -n '1,120p' foundation_library/f06_environments_dependencies/code/environment_doctor.py
sed -n '121,260p' foundation_library/f06_environments_dependencies/code/environment_doctor.py
```

调用链是：读取并验证 manifest → 逐项定位 module/读取 distribution 版本 → 用当前解释器读取 pip 身份 → 汇总缺失必需项 → 写 JSON → 用退出码报告 readiness。

先在当前环境运行：

```bash
python3 foundation_library/f06_environments_dependencies/code/environment_doctor.py --help
python3 foundation_library/f06_environments_dependencies/code/environment_doctor.py
echo $?
sed -n '1,200p' learner_outputs/foundation_library/f06_environments_dependencies/environment_report.json
```

预期 `Missing required: 0`、退出码 0。`fixture_package_not_installed` 的 available 为 false，但 required 也是 false。`inside_virtual_environment` 以实际环境为准。

然后创建隔离环境，不安装任何第三方包：

```bash
python3 -m venv .venv-day06
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f06_environments_dependencies/code/environment_doctor.py \
  --output learner_outputs/foundation_library/f06_environments_dependencies/venv_report.json
.venv-foundation_library/f06_environments_dependencies/bin/python -m pip --version
```

预期 venv 报告中 `inside_virtual_environment=true`，Python executable 位于 `.venv-foundation_library/f06_environments_dependencies/bin/`。清单仍 ready，因为只要求标准库。实际 Python 小版本取决于创建 venv 的基础解释器。

## 6. 自动化测试

```bash
python3 -m unittest -v foundation_library.f06_environments_dependencies.tests.test_environment_doctor
python3 -m py_compile \
  foundation_library/f06_environments_dependencies/code/minimal_import_check.py \
  foundation_library/f06_environments_dependencies/code/environment_doctor.py \
  foundation_library/f06_environments_dependencies/tests/test_environment_doctor.py
```

预期 3 个测试均 `ok`：必需标准库可用；缺失的可选 fixture 包不阻塞 readiness；字符串 `"yes"` 不能冒充布尔值。`py_compile` 无输出并返回 0。

## 7. 动手实验

### 实验 A：比较环境身份

运行系统 Python 与 `.venv-foundation_library/f06_environments_dependencies/bin/python` 两份报告。先预测哪些字段相同、哪些不同，再比较：

```bash
python3 -c 'import json; from pathlib import Path; a=json.loads(Path("learner_outputs/foundation_library/f06_environments_dependencies/environment_report.json").read_text()); b=json.loads(Path("learner_outputs/foundation_library/f06_environments_dependencies/venv_report.json").read_text()); print("system", a["python_executable"], a["inside_virtual_environment"]); print("venv", b["python_executable"], b["inside_virtual_environment"])'
```

解释为什么 OS 没有因为 venv 改变，但解释器前缀和包目录边界改变。

### 实验 B：把可选依赖改成必需

复制清单到个人目录，把不存在包的 `required` 从 false 改为 true。运行前预测报告是否写出、主退出码多少：

```bash
cp foundation_library/f06_environments_dependencies/config/fixture_requirements.json learner_outputs/foundation_library/f06_environments_dependencies/my_requirements.json
python3 foundation_library/f06_environments_dependencies/code/environment_doctor.py \
  --manifest learner_outputs/foundation_library/f06_environments_dependencies/my_requirements.json \
  --output learner_outputs/foundation_library/f06_environments_dependencies/missing_required_report.json
echo $?
```

预期报告仍写出以保存诊断证据，但 `ready=false`、missing list 含 fixture 名，程序返回 2。不要尝试安装这个虚构包。

### 实验 C：制造清单类型错误

在个人清单把 `required` 改成字符串 `"false"`。预测它是否等价于 JSON 布尔 false。预期不等价，检查器指出必须为布尔值并返回 2。这个实验说明配置里的类型与人眼看到的单词不是一回事。

### 实验 D：观察 traceback

运行：

```bash
python3 -c 'import fixture_package_not_installed'
echo $?
```

从最后一行读异常类型与模块名，再找第一处自己的代码 `<string>`。与 doctor 的友好报告比较：一个未捕获异常直接终止；另一个把“可选缺失”作为预期状态保存。

### 实验 E：检查当前环境快照而不提交

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python -m pip list
.venv-foundation_library/f06_environments_dependencies/bin/python -m pip freeze \
  > learner_outputs/foundation_library/f06_environments_dependencies/venv_freeze.txt
git status --short -- learner_outputs .venv-day06
```

预测 Git 状态。两者都应被忽略；freeze 只是观察快照，不是本项目正式锁文件。说明为什么不能把它直接当作后续 VLA 完整依赖。

## 8. 常见错误与止损

| 现象 | 先检查与处理 | 止损时间 |
|---|---|---:|
| 激活后仍用错 Python | `command -v python` 与 `sys.executable` | 15 分钟 |
| `No module named pip` | 用该解释器检查 venv 创建是否完整，不要混用全局 pip | 20 分钟 |
| `ModuleNotFoundError` | 记录解释器、导入名、`python -m pip --version` | 20 分钟 |
| 本地 `json.py` 导致异常 | 检查当前目录同名文件和 `module.__file__` | 15 分钟 |
| 创建 venv 很慢/失败 | 检查磁盘、Python 安装和完整 stderr | 20 分钟 |
| 想升级所有包解决冲突 | 停止；先锁定哪个解释器、哪个包和版本约束 | 立即停止 |
| 输出含 token | 不提交，撤销 token，清理产物 | 立即停止 |

当前课程不需要管理员权限，不要使用 `sudo pip`。单项排错超过止损时间，保存命令、解释器路径和完整错误，回到最小标准库清单继续。

## 9. 与 VLA-RelComp 的连接

VLA-Arena、仿真器、SmolVLA 和 OpenVLA 可能需要不同且互相冲突的依赖。后续不会把所有包塞入一个环境，而会依据上游版本分别锁定，并记录解释器、依赖文件、代码 commit、模型 revision 和系统/GPU 信息。

一次 import 成功不等于模型可推理；一个 package 版本正确也不等于 CUDA ABI 匹配。今天建立的是第一层诊断：先证明“正在使用哪个 Python、声明哪些依赖、当前能否定位”。下一层才是实际 API smoke test，最后才是 GPU/仿真运行。

Day 7 将在隔离环境中安装本课程第一次第三方数值依赖 NumPy（如当前环境尚无则会走免费安装；任何网络或权限问题按止损路线处理），并把 Python 列表、图像和机器人状态转换为形状明确的数组。

## 10. 检查点与答案

### 题 1

为什么发行包名和 import 名不能默认相同？

**答案：** 它们属于不同层：发行包是安装元数据单位，模块/包是 Python 导入命名空间。一个发行包可提供多个模块，命名规则也可能不同，必须查官方元数据。

### 题 2

虚拟环境是否隔离操作系统和 GPU 驱动？

**答案：** 不隔离。它主要隔离 Python 解释器入口和 site-packages；仍共享操作系统、硬件、驱动及部分基础运行库。

### 题 3

为什么推荐 `python -m pip`？

**答案：** 它明确用当前选定的 Python 执行 pip，降低 shell 中 `pip` 指向另一解释器而“装了却导不进来”的风险。

### 题 4

缺失可选依赖与缺失必需依赖应怎样不同处理？

**答案：** 可选依赖可记录 unavailable 并继续不需要它的路径；必需依赖缺失使 readiness 为 false、返回非零，不能假装成功。

### 题 5

`pip freeze` 为什么不自动等于高质量锁文件？

**答案：** 它反映当前环境全部发行包，可能包含无关包，也不表达哪些是直接依赖、适用平台和选择理由。应在干净环境和明确声明基础上生成、验证正式锁定。

## 11. 完成标准

**最低完成线：** 最小检查器、工程检查器和 3 个测试通过；成功创建 venv，并指出两种解释器路径。

**标准完成线：** 完成 A—E；能解释 module/distribution、声明/快照、可选/必需异常的区别；保存两份环境报告、个人错误清单和 freeze 观察文件。

**当天产物：** 教材中的 fixture 依赖清单、两个检查器与测试；个人目录中的系统/venv 报告、修改清单、freeze 与 traceback 笔记。

## 12. 精确外部材料

| 材料 | 精确范围 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [Python 3.12 教程 §12 Virtual Environments and Packages](https://docs.python.org/3.12/tutorial/venv.html) | §12.1–12.3，45 分钟 | 创建 venv、使用 pip、理解 freeze | 第三方工具选择 |
| [Python 3.12 `venv` §Creating virtual environments](https://docs.python.org/3.12/library/venv.html#creating-virtual-environments) | 读创建命令、激活表格与 `EnvBuilder` 之前内容，25 分钟 | 知道激活的本质与平台差异 | 编程式 EnvBuilder |
| [Python Packaging User Guide: Installing Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/) | 读 Creating Virtual Environments 与 Use pip，30 分钟 | 用当前环境的 Python/pip | 用户级/系统级复杂安装 |
| [Python 3.12 教程 §8.3 Handling Exceptions](https://docs.python.org/3.12/tutorial/errors.html#handling-exceptions) | §8.3 与 §8.5，30 分钟 | 精确捕获、读取异常链 | 自定义清理协议留到训练日志日 |
| [Python 3.12 `importlib.metadata`](https://docs.python.org/3.12/library/importlib.metadata.html#distribution-versions) | 读 Distribution versions 与 Import Package Distributions，20 分钟 | 区分 import package 与 distribution | entry points 和 files API |

阅读时每遇到一个命令，都先确认提示符中的环境以及 `sys.executable`；不要在教材仓库之外随手升级任何包。
