# Mainline Day 4：Linux/NVIDIA 前检与第一个可重复真实 episode（Gate 1）

Day 1–3 已静态追清版本、任务和 evaluator；今天第一次把“源码存在”与“环境真的跑完一个 episode”分开。教材作者当前不租 GPU，所以只实际运行本地进程实验和诚实 preflight；真实 episode 命令、runner 和证据验收已完整提供，必须在合格 Linux/NVIDIA 环境执行。

## 1. 真实项目产物

跟练 Gate A 应产生：

- `learner_outputs/mainline/day04/preflight.json`；
- `learner_outputs/mainline/day04/episode_registry.csv`，恰好一行；
- 同一 run_id 的 `.log` 与 `.mp4`；
- 若基础设施失败，保留 `infrastructure_error.json`，但不能声称 episode 完成。

今天具体运行教材脚本，不修改 upstream。合格机器上的真实资产是单 episode registry 行及其日志/视频，而不是“环境安装成功”的截图。

## 2. 当前卡点

VLA-Arena 同时依赖 Python 版本、NVIDIA 驱动、EGL headless 渲染、MuJoCo/robosuite 和锁定源码。任何一层失败都会让模型没有机会做决策。若把 import error、黑屏或 CUDA OOM 记成任务失败，后续成功率分母就被污染。

今天需要进程/退出码知识，是为了先判定 runner 是否完整结束；需要 preflight，是为了在昂贵运行前暴露环境错误；需要 registry，是为了把每个 episode 与 commit、task、seed、init state 和证据文件绑定。

## 3. 前置诊断

```bash
python3 mainline/day04/code/minimal_process_probe.py \
  --output learner_outputs/mainline/day04/process_probe.json
python3 -m json.tool learner_outputs/mainline/day04/process_probe.json
```

应同时看到 stdout、stderr 和 `returncode=4`。如果把非零退出码当 success，或看不到 stderr，去 [F05](../../foundation_library/f05_linux_processes/README.md)；Python/依赖路径卡住去 [F06](../../foundation_library/f06_environments_dependencies/README.md)；Git hash 卡住去 [F04](../../foundation_library/f04_git/README.md)。

## 4. 即时知识

- **进程退出码**：0 通常表示命令按契约完成；非 0 需要结合 stderr 分类。
- **headless EGL**：服务器无显示器时让 OpenGL 走 EGL；`MUJOCO_GL=egl` 与 `PYOPENGL_PLATFORM=egl` 必须在 import 前生效。
- **preflight**：只证明运行前条件；不证明 episode、success 或模型能力。
- **基础设施失败**：import/CUDA/渲染/资产错误，不进入任务成功率分母。
- **有效 episode 失败**：环境完成 rollout，但 `success=false`；它必须进入分母。

锁定 random evaluator 的 action 有 7 维；前 6 维控制末端位姿，最后一维控制夹爪。它虽没有研究价值模型能力，却适合验证 evaluator→environment 的真实基础设施闭环。

## 5. 成熟材料处方

- **主材料（中文，25 分钟）**：[VLA-Arena 锁定版中文 README“安装/执行评估”](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/README_zh.md#快速开始)。只读前置条件、评测命令和配置说明；真实命令以本章 runner 为准。
- **补充材料（中文，20 分钟）**：[Python `subprocess.run` 中文文档](https://docs.python.org/zh-cn/3/library/subprocess.html#subprocess.run)。只读 `check`、`capture_output`、`text` 和 `returncode`。

## 6. 最小实验

完整 [minimal_process_probe.py](code/minimal_process_probe.py) 用 28 行把三个进程通道分开：

```python
#!/usr/bin/env python3
"""最小进程探针：把 stdout、stderr、退出码分开保存。"""

import argparse
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
# 故意让子进程同时写 stdout/stderr；退出码 4 是数据，不是 Python 异常。
command = [
    "python3", "-c",
    "import sys; print('renderer=fixture'); print('gpu=not-used', file=sys.stderr); sys.exit(4)",
]
result = subprocess.run(command, text=True, capture_output=True)
report = {
    "command": command,
    "stdout": result.stdout.strip(),
    "stderr": result.stderr.strip(),
    "returncode": result.returncode,
    "source_kind": "local_process_fixture",
}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(f"returncode={result.returncode}")
print(f"Saved: {args.output}")
```

这里的 `gpu=not-used` 是 fixture 文本，不是 GPU 探测结果；真实 GPU 只认下一节 `nvidia-smi` 输出。

## 7. 真实 VLA-Arena 操作

### 当前免费机器先做诚实前检

```bash
VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
python3 mainline/day04/code/real_preflight.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --output learner_outputs/mainline/day04/preflight.json
python3 mainline/day04/code/check_day04.py \
  --preflight learner_outputs/mainline/day04/preflight.json
```

macOS/非 3.11/无 NVIDIA 时应显示 `NOT READY`，同时 checker 显示 `PASS: truthful local preflight (episode not claimed)`。这不是 Gate 通过，只证明报告没有撒谎。

### 未来合格 Linux/NVIDIA 机器跑 Gate A

```bash
export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl
python3.11 mainline/day04/code/real_preflight.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --output learner_outputs/mainline/day04/preflight.json \
  --require-ready
python3.11 mainline/day04/code/run_single_episode.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --gate-config mainline/day04/config/gate_a.json \
  --output-dir learner_outputs/mainline/day04
python3.11 mainline/day04/code/check_day04.py \
  --preflight learner_outputs/mainline/day04/preflight.json \
  --registry learner_outputs/mainline/day04/episode_registry.csv \
  --gate-config mainline/day04/config/gate_a.json
```

长代码 [run_single_episode.py](code/run_single_episode.py) 按五段读：preflight；延迟 import；真实 suite/task/init state；调用 `make_env/run_episode`；落 registry/log/video 或 infrastructure error。

锁定证据：[`load_initial_states/make_env`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/random/evaluator.py#L126-L150)、[`run_episode`](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/random/evaluator.py#L187-L233)、[`run_task` 的 init/episode/video](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/random/evaluator.py#L244-L318)、[`Benchmark` 的 level/task/init 接口](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/benchmark/__init__.py#L425-L535)。

## 8. 独立挑战

完成 [Gate 1](../gates/gate01/README.md)：关闭旧终端，从 fresh terminal 使用未跟练的 Gate B（task 1、seed 19）独立完成 preflight、一个真实 episode、registry/log/video 和三分钟口述。不给简化 runner，不允许把 Gate A 文件改名后提交。

当前没有合格机器时，保留本机 `NOT READY` 报告并继续**教材编写**；但学习者课程进度中的 Gate 1 必须保持未通过，不能用作者 smoke test替代。

## 9. 机器验收与口述 rubric

免费作者测试：

```bash
python3 -m unittest -v mainline.day04.tests.test_day04_tools
python3 -m compileall -q mainline/day04
```

真实 Gate 机器命令见 Gate 1。checker 会核对 commit、suite、level/task/seed/init、新输入、单行 status、boolean success、frame_count 和非空 log/video，不只检查路径存在。

口述 10 分：进程/退出码 2；preflight 与 episode 区别 2；observation/action/success 3；基础设施失败与有效失败 2；证据版本反查 1。机器通过且 ≥8 才是学习者 Gate 通过。

## 10. 证据复盘

- 当前作者实际运行：本地进程 fixture、平台/NVIDIA/EGL/commit preflight、Python 单元测试。
- 当前作者未运行：MuJoCo、random real episode、GPU、真实视频与 registry。
- 未来真实 episode 即使 `success=false`，只要 status completed、frame/log/video 完整，就是有效基础设施证据。
- 不能推出：random policy 代表模型能力，或单个 episode 能估计成功率。

自测题（答案在 `shared/answer_keys/day04.md`）：

1. 为什么 `preflight ready` 仍不等于 episode 完成？
2. `success=false` 与 infrastructure error 谁进入分母？
3. EGL 环境变量为什么必须在 MuJoCo import 前设置？
4. registry 为什么必须同时保存 task、seed、init state、commit 与视频路径？
