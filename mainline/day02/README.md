# Mainline Day 2：从 CLI/YAML 追到 PrepositionCombinations 的 15 个任务

Day 1 画了系统地图；今天把其中一条边落实为可复查的数据：命令行如何找到 YAML，YAML 如何选择 random evaluator 和 registry，registry 如何落到 L0/L1/L2 各五个任务。全程读取锁定 Git blob，不 import torch/MuJoCo。

## 1. 真实项目产物

今天生成：

- `learner_outputs/mainline/day02/config_trace.md/json`：CLI→配置→evaluator→registry 的七节点追踪；
- `learner_outputs/mainline/day02/config_suite_manifest.json`：15 个任务的 level、level_id、BDDL 与 init 路径；
- `learner_outputs/mainline/day02/challenge_config.yaml` 与 `challenge_trace.json`：独立配置挑战。

你只新建/修改 learner_outputs 中的挑战配置；教材配置 [random_preposition_manifest.yaml](config/random_preposition_manifest.yaml) 和 upstream 都只读。

## 2. 当前卡点

一条看似简单的命令 `vla-arena eval --model random --config ...` 横跨 TOML entry point、argparse 子命令、配置路径解析、动态 import、YAML dataclass、benchmark registry 和 task map。只看最终 YAML 会漏掉“谁读取它”；只看 evaluator 会漏掉“模型名怎样选择模块”。

本地锁定 checkout 还可能是 sparse checkout：CLI 文件存在于 commit，但未展开在工作树。今天需要知道 Git blob 才是锁定版本事实，`ls` 看不到不等于 commit 不包含。

## 3. 前置诊断

用 10 分钟回答：

```bash
python3 mainline/day02/code/minimal_yaml_trace.py \
  mainline/day02/config/random_preposition_manifest.yaml
python3 -c 'd={"model":"random","level":0}; print(d["model"], type(d["level"]).__name__)'
```

应看到 `task_level=0 type=int`、`use_local_log=True type=bool`，不是全都字符串。字典/模块卡住去 [F03](../../foundation_library/f03_modules_testing/README.md)，CSV/JSON 表达卡住去 [F02](../../foundation_library/f02_csv_json/README.md)，Git blob/版本卡住去 [F04](../../foundation_library/f04_git/README.md)。通过就跳过。

## 4. 即时知识

- **CLI entry point**：TOML 把 shell 命令映射到 Python 模块函数。
- **YAML mapping**：`key: value` 进入 Python 字典；boolean、整数和字符串类型必须保留。
- **动态 import**：模型名拼成模块路径，random 与 SmolVLA 因而走不同 evaluator。
- **registry**：稳定字符串 `extrapolation_preposition_combinations` 映射到动态创建的 benchmark class。
- **manifest**：只读列举将要运行的任务；不是运行结果，也不含 success。

`task_level: 0` 表示一次 evaluator 选择 L0，不表示 suite 只有 L0。本项目 manifest 必须保留全部 15 条，以便后续冻结 L0 训练、L1/L2 保留测试边界。

## 5. 成熟材料处方

- **主材料（中文，20 分钟）**：[VLA-Arena 锁定版中文 README“配置文件说明”](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/README_zh.md#配置文件说明)。只读 eval 命令、model/config 对应关系；随后必须用本章源码追踪核对。
- **补充材料（中文，15 分钟）**：[Python 中文教程 5.5 字典](https://docs.python.org/zh-cn/3/tutorial/datastructures.html#dictionaries)。练 key 访问、遍历和嵌套字典；不扩展到完整 Python 基础课。

## 6. 最小实验

完整 [minimal_yaml_trace.py](code/minimal_yaml_trace.py) 用 32 行展示今天所需的最小 YAML 类型知识：

```python
#!/usr/bin/env python3
"""最小 YAML 标量解析：展示 key、值和 Python 类型。"""

import argparse
from pathlib import Path


def scalar(text):
    # 本课配置只用字符串、整数和 boolean；不冒充完整 YAML 解析器。
    value = text.split("#", 1)[0].strip().strip('"').strip("'")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        return value


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("config", type=Path)
args = parser.parse_args()
config = {}
for line_number, line in enumerate(args.config.read_text().splitlines(), start=1):
    clean = line.strip()
    if not clean or clean.startswith("#"):
        continue
    if ":" not in clean:
        raise SystemExit(f"line {line_number}: missing ':'")
    key, raw = clean.split(":", 1)
    config[key.strip()] = scalar(raw)
for key, value in config.items():
    print(f"{key}={value!r} type={type(value).__name__}")
```

这不是通用 YAML parser：不支持嵌套、数组、多行字符串或锚点。工程工具也刻意只接受课程配置的简单标量；未来真实 evaluator 使用自己的 YAML/draccus 解析路径。

## 7. 真实 VLA-Arena 操作

沿用 Day 1 的锁定 checkout：

```bash
VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
git -C "$VLA_ARENA_LOCKED" rev-parse HEAD
git -C "$VLA_ARENA_LOCKED" show HEAD:vla_arena/cli/main.py | sed -n '15,60p'
python3 mainline/day02/code/trace_config.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --config mainline/day02/config/random_preposition_manifest.yaml \
  --output-dir learner_outputs/mainline/day02
sed -n '1,120p' learner_outputs/mainline/day02/config_trace.md
python3 -m json.tool learner_outputs/mainline/day02/config_suite_manifest.json | sed -n '1,120p'
```

应看到 `PASS: extrapolation_preposition_combinations / 15 tasks`。工程脚本按四段读：简单 YAML 类型；`git show` 读取锁定 blob；AST 提取 task map；逐任务验证 BDDL/init blob。

锁定证据：

- [TOML console entry point](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/pyproject.toml#L43-L51)
- [CLI main 的 eval 子命令](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/cli/main.py#L21-L50)
- [`eval_main` 配置解析与动态 evaluator import](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/cli/eval.py#L21-L51)
- [`resolve_config_path`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/config_paths.py#L27-L98)
- [random `_parse_cfg` 与 `main`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/random/evaluator.py#L331-L395)
- [目标 task map 15 条](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/benchmark/vla_arena_suite_task_map.py#L163-L185)

若提示 blob 不存在，优先检查 commit；若配置 suite 不匹配，检查是否用了展示名；若类型不对，检查 YAML 是否给数字加了引号。

## 8. 独立挑战

在 `learner_outputs/mainline/day02/challenge_config.yaml` 独立写一份新配置，满足：random、目标 registry、L2、每任务 2 次、等待 10 步、seed 19、只启用本地日志、关闭 W&B，并把未来结果指向 `learner_outputs/mainline/day02/challenge_results.json`。

使用今天的工程工具生成 stem 为 `challenge` 的 trace。不给完整 YAML 或逐步命令；先预测哪些 CLI 节点不变、哪些 `EvaluatorConfig` 值改变。不要运行 evaluator。

## 9. 机器验收与口述 rubric

```bash
python3 -m unittest -v mainline.day02.tests.test_day02_tools
python3 mainline/day02/code/check_day02.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --config mainline/day02/config/random_preposition_manifest.yaml \
  --trace learner_outputs/mainline/day02/config_trace.json \
  --manifest learner_outputs/mainline/day02/config_suite_manifest.json \
  --challenge-config learner_outputs/mainline/day02/challenge_config.yaml \
  --challenge-trace learner_outputs/mainline/day02/challenge_trace.json
```

机器会重新读取锁定 blob、重新提取 15 条任务、重新解析主配置和挑战配置；复制主 trace 后只改 ID 或文件名不能通过。

口述 10 分：CLI 七节点 3 分；YAML 类型/覆盖 2 分；registry→15 tasks 2 分；L0 训练与 L1/L2 保留边界 1 分；稀疏 checkout 与未运行边界 2 分。8 分以上且机器通过进入 Day 3；5–7 分按弱项补 F02/F03/F04。

## 10. 证据复盘

- 已验证：锁定 blob 中 CLI chain、配置字段、registry 名、15 个 task name 及对应 BDDL/init 路径。
- 未运行：CLI package、MuJoCo、random episode、任何模型或 GPU。
- 不能推出：任务可成功初始化、模型成功率或关系理解能力。

在 `learner_outputs/mainline/day02/evidence_reflection.md` 写出一项“配置改变但代码节点不变”的例子、一项“稀疏 checkout 误判”以及当前证据边界。

自测题（答案在 `shared/answer_keys/day02.md`）：

1. shell 的 `vla-arena` 最先进入哪个 Python 函数？
2. `--model random` 怎样决定 evaluator 模块？
3. YAML 怎样变成 `EvaluatorConfig`？
4. `task_level=0` 为什么不等于 manifest 只有 5 条？
5. 工作树没有 CLI 文件时，为什么仍能从锁定 commit 读取？
