# Mainline Day 1：锁定版本，并画出 VLA-RelComp 最小系统地图

今天不是学习一整天 Git，而是建立后面 69 天都要引用的版本事实：哪一个仓库、哪一个 commit、目标 suite 从配置流向哪些代码。免费本地操作只读源码，不安装 VLA-Arena 依赖，不运行 MuJoCo 或 GPU。

## 1. 真实项目产物

你会生成：

- `learner_outputs/mainline/day01/project_map.json`：可机器比较的锁定版本、系统节点和边；
- `learner_outputs/mainline/day01/project_map.md`：可阅读的 Mermaid 最小系统图；
- `learner_outputs/mainline/day01/smolvla_adapter_map.json`：独立挑战的新 adapter 地图。

今天只修改 `learner_outputs/mainline/day01/`。不要编辑锁定 VLA-Arena checkout、研究仓库或教材源码。

## 2. 当前卡点

后面说“沿 evaluator 追踪”时，至少有四种容易混淆的东西：网页上的最新 `main`、你本地当前分支、某次 commit 快照、模型配置指向的 suite。只记住仓库名字不能复现研究；必须把每条研究事实钉在不可移动的 commit 上。

今天需要最小系统地图，因为 Day 2 会从 config 追到 15 个任务，Day 3 会从 evaluator 追 observation/action。没有地图时，很容易在同名 README、配置和 Python package 之间迷路。

## 3. 前置诊断

在 10 分钟内完成：

```bash
pwd
git status --short --branch
git rev-parse HEAD
python3 -c 'from pathlib import Path; print(Path("shared/upstream.lock").read_text())'
```

你应能解释：当前目录、教材分支、commit hash 与文件内容是四件不同的事。终端/路径卡住去 [F01](../../foundation_library/f01_terminal_python/README.md)，Git status/commit 卡住去 [F04](../../foundation_library/f04_git/README.md)，环境或命令缺失去 [F06](../../foundation_library/f06_environments_dependencies/README.md)。通过就跳过补习。

## 4. 即时知识

- **repository** 是带 Git 历史的项目目录。
- **working tree** 是你此刻看到的文件；可能有未提交修改。
- **commit** 是不可变快照，用 40 位 hash 标识。
- **branch** 是会移动的名字；`main` 今天和下周可能指向不同 commit。
- **detached HEAD** 表示直接检出一个 commit，适合只读复现，但不要在里面误做教材修改。

本项目锁定 `babe582ebffc82b979b77964a7e56417d02f63a4`。最小数据流是：配置选择 evaluator/suite → registry 建 benchmark → task map/BDDL 给任务 → evaluator 调 environment → environment 把 success 写进 info。

## 5. 成熟材料处方

- **主材料（中文，20 分钟）**：[Pro Git 2.1 获取 Git 仓库](https://git-scm.com/book/zh/v2/Git-基础-获取-Git-仓库)。只读“在现有目录中初始化仓库”和“克隆现有仓库”，重点理解 clone 得到的是完整 Git 仓库。
- **补充材料（中文，15 分钟）**：[VLA-Arena 锁定版中文 README：快速开始](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/README_zh.md#快速开始)。只读项目定位、clone 与评测入口；其中命令仍要以本课锁定源码核对。

## 6. 最小实验

先读完 31 行的 [完整注释代码](code/minimal_lock_check.py)。它不 import VLA-Arena，只问 Git 和文件系统：

```python
#!/usr/bin/env python3
"""最小版本锁检查：只读 Git 和三个项目入口。"""

import argparse
import subprocess
from pathlib import Path

LOCKED = "babe582ebffc82b979b77964a7e56417d02f63a4"
REQUIRED = [
    "README_zh.md",
    "vla_arena/models/random/evaluator.py",
    "vla_arena/vla_arena/benchmark/__init__.py",
]

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--upstream", type=Path, required=True)
args = parser.parse_args()
root = args.upstream.resolve()
# rev-parse 读取当前 checkout；不 import VLA-Arena，也不安装依赖。
head = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=root, check=True,
    text=True, capture_output=True,
).stdout.strip()
if head != LOCKED:
    raise SystemExit(f"FAIL: expected {LOCKED}, got {head}")
missing = [path for path in REQUIRED if not (root / path).is_file()]
if missing:
    raise SystemExit(f"FAIL: missing {missing}")
print(f"PASS: locked commit {head}")
for path in REQUIRED:
    print(f"FOUND: {path}")
```

从仓库根运行，把路径换成自己的只读 checkout：

```bash
VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
python3 mainline/day01/code/minimal_lock_check.py --upstream "$VLA_ARENA_LOCKED"
```

应看到锁定 hash 和三个 `FOUND`。若 hash 不同，先停下，不要用“文件看起来差不多”继续。

## 7. 真实 VLA-Arena 操作

若还没有 checkout，免费执行 clone 与 detached checkout；已有锁定 checkout 就从第三条开始：

```bash
mkdir -p learner_outputs/mainline/day01/source
git clone https://github.com/PKU-Alignment/VLA-Arena.git \
  learner_outputs/mainline/day01/source/VLA-Arena
git -C learner_outputs/mainline/day01/source/VLA-Arena \
  switch --detach babe582ebffc82b979b77964a7e56417d02f63a4
VLA_ARENA_LOCKED=learner_outputs/mainline/day01/source/VLA-Arena
git -C "$VLA_ARENA_LOCKED" rev-parse HEAD
python3 mainline/day01/code/build_project_map.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --output-dir learner_outputs/mainline/day01
sed -n '1,160p' learner_outputs/mainline/day01/project_map.md
```

`build_project_map.py` 是较长工程代码，完整文件按四段阅读：常量定义真实节点；`git_head/build_map` 验证版本与源码契约；`markdown` 生成图；`main` 只处理 CLI 和落盘。

逐项核对锁定事实：

- [suite 列表与 problem folder 映射](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/benchmark/__init__.py#L335-L385)
- [benchmark class 的动态注册](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/benchmark/__init__.py#L631-L660)
- [PrepositionCombinations 的 L0/L1/L2 任务映射](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/benchmark/vla_arena_suite_task_map.py#L163-L185)
- [random evaluator 从 suite 名实例化 benchmark](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/random/evaluator.py#L349-L395)

应看到 `PASS: babe... / extrapolation_preposition_combinations`。常见错误优先检查 checkout 路径、HEAD 是否精确匹配、是否误把展示名 `PrepositionCombinations` 写入配置。

## 8. 独立挑战

换一个真实输入：不要再看 random adapter，独立阅读锁定版：

- `vla_arena/models/smolvla/evaluator.py`
- `vla_arena/configs/evaluation/smolvla.yaml`

生成 `learner_outputs/mainline/day01/smolvla_adapter_map.json`，包含模型名、两条相对路径、配置 dataclass 名、四个顶层 hook、是否需要 GPU，以及证据类型。不给字段值和搜索命令；先预测，再用源码核对。复制 random 地图后只改模型名不能通过机器验收。

## 9. 机器验收与口述 rubric

```bash
python3 -m unittest -v mainline.day01.tests.test_day01_tools
python3 mainline/day01/code/check_day01.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --project-map learner_outputs/mainline/day01/project_map.json \
  --challenge learner_outputs/mainline/day01/smolvla_adapter_map.json
```

机器通过表示：地图由锁定 checkout 重新计算；suite 与七个节点匹配；挑战中的 SmolVLA 路径和顶层符号匹配真实源码。

口述 10 分：commit 与 branch 2 分；七节点职责 3 分；从 config 到 success 的边 2 分；registry 名与展示名 1 分；静态事实/未运行边界 2 分。8 分以上且机器通过进入 Day 2；5–7 分补 F01/F04；更低则停止扩张，重新完成版本锁实验。

## 10. 证据复盘

今天得到的是**真实锁定源码地图**，不是模型实验结果：

- 已实际验证：Git HEAD、关键文件存在、suite 字符串、静态节点与边。
- 未实际验证：依赖安装、MuJoCo 渲染、SmolVLA 权重、任何 GPU episode。
- 不能推出：某模型成功率、RelComp 失败机制或修复方向。

在 `learner_outputs/mainline/day01/evidence_reflection.md` 记录运行命令、实际 checkout 路径、hash、一个定位错误及边界。

自测题（答案在 `shared/answer_keys/day01.md`）：

1. 为什么 `main` 分支名不能代替 40 位 commit？
2. config、evaluator、registry、task map/BDDL、environment 各负责什么？
3. registry 名为什么不能凭 README 展示名称猜？
4. 静态地图通过后，仍有哪些真实运行事实未知？
