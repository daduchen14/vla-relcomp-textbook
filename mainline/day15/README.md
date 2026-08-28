# Mainline Day 15：把 baseline 口径冻结成可重算 lock

今天把“我记得当时用的是这个版本”变成机器可核对的 protocol lock：代码 commit、上游 commit、模型 revision、suite/levels、seed/init、success、无效 episode 规则、L1/L2 保留边界和关键文件 sha256。真实模型尚未选定，因此本日实际运行的是合成锁定演示；formal 模式会拒绝 placeholder 和 dirty worktree。

## 1. 真实项目产物

- `learner_outputs/mainline/day15/protocol_lock_a.json`：当前仓库与 A spec 的完整可重算快照；
- `learner_outputs/mainline/day15/protocol_lock_b.json`、`challenge_memo.md`：换模型、试次数和证据文件后的独立锁；
- [freeze_protocol.py](code/freeze_protocol.py)：未来 Gate 1/2 完成后生成正式 baseline lock 的同一工具。

## 2. 当前卡点

只写“SmolVLA、5 seeds、成功率”无法复现：模型名不等于 revision，seed 不等于精确 init state，`done` 不等于 `info.success`，同名配置也可能被改写。反过来，把当前 placeholder 写进 JSON 并命名 final 也不是冻结。lock 必须区分内容身份与证据状态。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day15/code/minimal_file_hash.py
```

应看到 Day 12 阈值文件的 path、bytes 和 64 位 sha256。若路径/字节卡住补 [F01](../../foundation_library/f01_terminal_python/README.md)；若 Git commit 卡住补 [F04](../../foundation_library/f04_git/README.md)。

## 4. 即时知识

- **commit/revision**：代码与模型的不可变版本标识；branch、tag、模型别名可能移动。
- **sha256**：内容指纹；内容变一字节通常就变 hash，但 hash 不判断内容是否科学合理。
- **protocol lock**：把运行前已经决定的口径与内容身份打包，并对整个 payload 再计算 lock hash。
- **formal/synthetic**：formal 要求无 placeholder、clean worktree 和真实 revision；synthetic 只演练工具。
- **held-out boundary**：L1/L2 不参与 checkpoint、阈值、prompt 或超参数选择。

## 5. 成熟材料处方

- **Git 官方材料（12 分钟）**：[git-rev-parse](https://git-scm.com/docs/git-rev-parse)。只读 `--verify`/对象名解析，理解为什么记录 `HEAD` 的完整 commit，而不是分支名。
- **模型版本补充（英文官方，10 分钟）**：[Hugging Face Hub：Download a specific file version](https://huggingface.co/docs/huggingface_hub/guides/download#download-a-specific-file-version)。只读 `revision` 可取 commit hash 的部分；不下载权重。

## 6. 最小实验

[minimal_file_hash.py](code/minimal_file_hash.py) 是完整 13 行示例：

```python
#!/usr/bin/env python3
"""最小例子：内容 hash 能发现同名文件被静默修改。"""

import hashlib
from pathlib import Path

path = Path("mainline/day12/config/event_thresholds.json")
payload = path.read_bytes()
digest = hashlib.sha256(payload).hexdigest()

print(f"path={path}")
print(f"bytes={len(payload)}")
print(f"sha256={digest}")
```

它不修改文件；长脚本还限制路径不能越出仓库，避免错误地冻结任意机器文件。

## 7. 真实 VLA-Arena 操作

```bash
export VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
.venv-day06/bin/python mainline/day15/code/freeze_protocol.py \
  --repo . --upstream "$VLA_ARENA_LOCKED" \
  --spec shared/fixtures/day15_lock_spec_a.json \
  --output learner_outputs/mainline/day15/protocol_lock_a.json
```

应看到 `synthetic_demonstration`、4 files 和 `clean=False/True`（取决于学习者是否有未提交产物）。输出精确验证 upstream 为 `babe582...`，记录教材 HEAD，并给每个关键文件 path/bytes/sha256。`source_kind=synthetic...not_baseline`，不能交给 Day 16 registry 当正式锁。

真实 Gate 1/2 完成后：复制 A spec 到 learner output，设 `mode=formal`，填实际 model ID 与不可变 revision，把正式任务表、阈值、evaluator 配置和 manifest 加入 hash 清单；先提交并保持 worktree clean，再重跑。脚本发现 `placeholder/synthetic/fill_after`、dirty worktree、`done` success 或 L1/L2 选择泄漏会拒绝。

## 8. 独立挑战

用 `day15_lock_spec_b.json` 生成 B lock。写 ≥160 字 `challenge_memo.md`，必须出现 `commit`、`revision`、`sha256`、`seed`、`init_state`、`L1/L2`、`formal`，解释 B 为何不同、hash 能/不能证明什么，以及当前为何不能升级为正式基线锁。正文不给 B lock hash。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day15.tests.test_day15_tools
.venv-day06/bin/python mainline/day15/code/check_day15.py \
  --repo . --upstream "$VLA_ARENA_LOCKED" \
  --example-spec shared/fixtures/day15_lock_spec_a.json \
  --example-lock learner_outputs/mainline/day15/protocol_lock_a.json \
  --challenge-spec shared/fixtures/day15_lock_spec_b.json \
  --challenge-lock learner_outputs/mainline/day15/protocol_lock_b.json \
  --challenge-memo learner_outputs/mainline/day15/challenge_memo.md
```

口述 10 分：代码/模型身份 2；文件 hash 2；seed/init 2；success/异常口径 2；formal 与 held-out 边界 2。机器通过且 ≥8 进入 Day 16；formal lock 未生成不阻止学习教材，但阻止真实 baseline 开跑。

## 10. 证据复盘

- 已运行：两套合成 spec 重算、upstream commit 检查、文件 hash、越界/重复/placeholder/`done` 拒绝测试。
- 未运行：真实模型 revision 冻结、clean formal lock、baseline episode。
- 可以主张：冻结 schema 和内容校验工具可用；A/B 是不同可复算演示。
- 不能主张：baseline 已冻结、模型已选定、当前 dirty=False，或 L0/L1/L2 可以开跑。

自测题（答案在 `shared/answer_keys/day15.md`）：

1. 为什么分支名和模型名不足以冻结版本？
2. sha256 能证明什么、不能证明什么？
3. seed 为什么不能替代 init state？
4. L1/L2 哪些用途会破坏 held-out？
5. 当前 A/B 为什么不能叫 formal baseline lock？
