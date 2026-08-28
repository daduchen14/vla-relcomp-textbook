# Mainline Day 67：fresh clone 复现最小表格

今天从 fresh clone、locked branch 和干净输出目录重建一张最小表。脚本只用 Python 标准库，记录输入、expected、脚本与输出 hashes，明确 cache/GPU/VLA-Arena 均未使用。它证明免费教学路径可复现，不是模型实验复现。

## 1. 真实项目产物

- `minimal_table.json`：从 CSV 重建的 condition counts/rates；
- `reproduction_log.json`：环境、四类 hash、缓存/算力与边界；
- fresh-clone 命令日志和 B 新输入复现 memo。

## 2. 当前卡点

在作者长期使用的工作树里“能跑”可能依赖未提交文件、全局包、旧输出或缓存。只写依赖列表也不能证明文档命令从零可执行。

本课把复现对象缩到一张 CPU 表，先证明 clone→command→expected output 闭环；真实 GPU 复现仍需另行提供环境与授权证据。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day67/code/minimal_reproduction_check.py
```

应输出 rows=3、successes=2 和稳定 SHA-256。若 Git clone 不熟补 [F04](../../foundation_library/f04_git/README.md)；环境/依赖回看 [F06](../../foundation_library/f06_environments_dependencies/README.md)。

## 4. 即时知识

- **fresh clone**：从提交对象新建、不继承当前未提交状态的工作目录。
- **locked branch/commit**：复现时明确选择的 Git 状态。
- **clean environment**：不借用未声明全局包和隐式变量。
- **expected output**：运行前冻结的语义结果，不能由本次结果覆盖。
- **cache control**：禁用或记录缓存来源与 hash。
- **reproduction log**：命令、环境、输入、脚本、输出、exit code 与边界的证据。
- **minimal reproduction**：先重建最小关键表，再逐层扩大到完整实验。

## 5. 成熟材料处方

- **中文主材料（Pro Git，10 分钟）**：[Git 基础—获取 Git 仓库](https://git-scm.com/book/zh/v2/Git-基础-获取-Git-仓库)。只读 clone 与已存在目录两段，理解 fresh clone 的对象边界。
- **补充材料（Python 官方中文，8 分钟）**：[venv—创建虚拟环境](https://docs.python.org/zh-cn/3/library/venv.html)。只看环境创建、激活非必需和不可移植性说明。
- **锁定项目定位（8 分钟）**：[pyproject 第 5–40 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/pyproject.toml#L5-L40) 固定 Python 3.11 与核心依赖；这解释为何完整 VLA-Arena 复现不能由本课标准库 smoke test 替代。

## 6. 最小实验

[minimal_reproduction_check.py](code/minimal_reproduction_check.py) 是完整 18 行代码：

```python
#!/usr/bin/env python3
"""最小例子：同一输入必须产生同一摘要与统计。"""

import hashlib
import json

rows = [
    {"condition": "baseline", "success": 1},
    {"condition": "baseline", "success": 0},
    {"condition": "repair", "success": 1},
]
payload = json.dumps(rows, sort_keys=True).encode()
digest = hashlib.sha256(payload).hexdigest()

successes = sum(row["success"] for row in rows)
result = {"rows": len(rows), "successes": successes, "input_sha256": digest}

print(json.dumps(result, sort_keys=True))
```

长文件 [reproduce_minimal_table.py](code/reproduce_minimal_table.py) 读取冻结输入/expected，拒绝覆盖并写 reproduction log。

## 7. 真实 VLA-Arena 操作

从教材仓库根目录先做本地 free rehearsal：

```bash
.venv-day06/bin/python mainline/day67/code/reproduce_minimal_table.py \
  --input shared/fixtures/day67_repro_a.csv --expected shared/fixtures/day67_expected_a.json \
  --output-dir learner_outputs/mainline/day67/repro_a
```

应看到 `PASS: rows=4 cache=false gpu=false`。fresh clone 时在新临时目录 clone `content/day01-02`，用系统 `python3` 运行同一命令并保存 shell exit code、`git rev-parse HEAD`、`git status --short`。未来完整 VLA-Arena 需 Python 3.11、锁定依赖、模型权重、MuJoCo/NVIDIA 与授权 GPU；本课不运行也不伪造。

## 8. 独立挑战

在新的输出目录用 B input/expected 复现。写 ≥280 字 memo，原样包含 `fresh clone`、`locked branch`、`clean environment`、`dependency`、`input hash`、`script hash`、`expected output`、`exit code`、`cache`、`CPU`、`reproduction log`、`synthetic`、`cannot claim`；正文不给 B 统计值。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day67.tests.test_day67_tools
.venv-day06/bin/python mainline/day67/code/check_day67.py \
  --example-input shared/fixtures/day67_repro_a.csv --example-expected shared/fixtures/day67_expected_a.json --example-output-dir learner_outputs/mainline/day67/repro_a \
  --challenge-input shared/fixtures/day67_repro_b.csv --challenge-expected shared/fixtures/day67_expected_b.json --challenge-output-dir learner_outputs/mainline/day67/repro_b \
  --challenge-memo learner_outputs/mainline/day67/challenge_memo.md
```

口述 10 分：clone/commit 2；环境/依赖 2；四类 hash 2；expected/exit 2；cache/边界 2。机器通过且 ≥8 才完成 Day 67；当前目录冒充 fresh clone、覆盖 expected、使用隐式 cache 或把 CPU table 当 GPU 复现均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic CSV 的标准库 CPU 重建、hash 与逐字节复验。
- 静态源码事实：锁定 upstream pyproject 要求 Python 3.11 和完整依赖。
- 未运行：VLA-Arena、MuJoCo、模型权重、NVIDIA/GPU 与 formal episodes。
- 可以主张：最小表可从提交内输入在 clean output 重建。
- 不能主张：模型结果、完整 upstream 环境或 GPU 实验已复现。

自测题（答案在 `shared/answer_keys/day67.md`）：

1. fresh clone 排除哪些隐性状态？
2. reproduction log 至少记录什么？
3. expected output 能否自动更新？
4. cache 为什么必须显式处理？
5. CPU table 复现等于 VLA-Arena 复现吗？
