# Mainline Day 25：从空 manifest 复现缩小版基线包（Gate 4）

今天把 Day 15–24 串成一个入口：输入只有锁定 spec 和一个 empty 输出目录，脚本生成 planned manifest，经 deterministic synthetic adapter 得到 registry，再生成 task stats、baseline report 与 SHA-256 receipt。A 是逐步示例；B 要独立完成。免费通过只是 Gate 4 rehearsal，真实 Gate 4 仍需在合格环境用 Day 17 adapter 演示中断恢复。

## 1. 真实项目产物

每个 `package_*` 目录必须且只能有：

- `manifest.csv`：从 spec 新生成的 PLANNED episode；
- `registry.csv`：adapter 回填后的 COMPLETED/success；
- `task_stats.csv`、`baseline_report.json`：Day 22 同口径缩小表；
- `reproduction_receipt.json`：spec、四项产物的 SHA-256 与 GPU 边界。

B 还需 `gate4_memo.md`，由 learner 放在 package 外，避免污染精确文件集合。

## 2. 当前卡点

“我以前跑出来过”不是复现。旧 manifest、手工编辑 registry、缓存统计或未记录的命令都可能让结果看似一致。目录清空后若无法从 spec 重建，就缺少真正的生成链；反过来，字节 hash 相同也只证明约定产物相同，不能证明指标科学正确。

本课要求输出目录起初 empty；脚本发现任何旧文件即停止，不自动覆盖或删除。spec 固定 commit、model revision、protocol lock、task/trial、seed/init 和 synthetic outcomes。receipt 记录内容 hash，不写时间戳或绝对路径，因此同输入可在新目录逐字节重建。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day25/code/minimal_receipt.py
```

应看到两个 64 位 hex digest、`artifact_count=2`。若 bytes/hash 不熟，补 [F01](../../foundation_library/f01_terminal_python/README.md)；manifest/runner 回看 [Day 17](../day17/README.md)，统计回看 [Day 22](../day22/README.md)。

## 4. 即时知识

- **single source spec**：生成链唯一人工输入；manifest 不是预先手填。
- **clean-room output**：目标目录 empty，避免读取或覆盖历史产物。
- **deterministic adapter**：相同 spec 给相同教学 outcome；它替代昂贵模型，只测试管线。
- **artifact set**：声明哪些文件属于需要复现的正式输出；多/少一个都失败。
- **SHA-256 receipt**：对原始 bytes 计算摘要，用于发现内容漂移；不是数字签名，也不证明来源可信。
- **end-to-end**：spec→manifest→registry→task_stats/report→receipt，每一步可追溯。
- **Gate rehearsal**：CPU fixture 验证编排；真实 Gate 还要替换 adapter、保存日志/视频并演示 resume。
- **claim boundary**：管线可复现与模型结果可复现是两件事。

## 5. 成熟材料处方

- **中文主材料（8 分钟）**：[Python `hashlib` 官方中文文档](https://docs.python.org/zh-cn/3/library/hashlib.html)。只读 `sha256(data).hexdigest()` 和文件 bytes；不要把 digest 当加密签名。
- **工程材料（10 分钟）**：[Reproducible Builds 的 Definitions](https://reproducible-builds.org/docs/definition/)。读“相同源、环境、步骤→指定产物逐字节相同”及 hash 比较；本课借用 artifact reproduction 思路，不声称满足完整跨环境构建规范。
- **锁定项目材料（12 分钟）**：[SmolVLA evaluator 主流程第 586–649 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L586-L649) 与 [结果写出第 724–756 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L724-L756)。确认 config→seed/model/suite→task loop→episode/success payload 的真实链；formal package 要在这条链外加 registry 与 receipt，不能只保留最终 JSON。

## 6. 最小实验

[minimal_receipt.py](code/minimal_receipt.py) 是完整 16 行代码：

```python
#!/usr/bin/env python3
"""最小例子：给产物内容计算 SHA-256 receipt。"""

import hashlib

artifacts = {
    "manifest.csv": b"episode_id,status\ne1,PLANNED\n",
    "registry.csv": b"episode_id,status,success\ne1,COMPLETED,1\n",
}

for name, payload in artifacts.items():
    digest = hashlib.sha256(payload).hexdigest()
    print(name, digest)

print(f"artifact_count={len(artifacts)}")
print("boundary=hash_checks_bytes_not_scientific_truth")
```

把 registry 的 success 从 1 改 0，digest 会整体改变。hash 能发现 bytes 不同，却不知道修改是正确修复还是篡改，所以还需要锁定来源与人工复盘。

## 7. 真实 VLA-Arena 操作

为 A 选择一个尚不存在或确实 empty 的目录：

```bash
.venv-day06/bin/python mainline/day25/code/reproduce_mini_baseline.py \
  --spec shared/fixtures/day25_mini_spec_a.json \
  --output-dir learner_outputs/mainline/day25/package_a
```

应看到 `tasks=2 episodes=4 gpu_used=false`。不要再次对同目录运行；脚本应报“输出目录必须为空”。若要验证重建，指定另一个新目录，再比较 receipt/hash。

真实 Gate 4 操作不运行本课 synthetic outcomes：从 Day 15 formal lock 与 Day 24 real decision 生成新的两任务 spec，接 Day 17 real evaluator adapter，先从 empty 目录生成 manifest；处理中主动终止一次，再用 Day 17 checkpoint/resume 恢复，保证 completed episode 不重复执行；最后用 Day 22/23 生成统计与 evidence。保存终端日志、视频索引、异常与 receipt。付费 GPU 只有 learner 明确授权后才能启动。

排错：目录非空就换新的 clean path，不删除证据；hash 不同先逐文件比较；episode 数不符回查 task×trial；spec commit 漂移立即停止；synthetic adapter 的成功位绝不复制进 formal registry。

## 8. 独立挑战

不照抄 A 命令参数，阅读 `day25_mini_spec_b.json`，选一个新的 empty 目录生成 B package。写 ≥220 字 Gate memo，必须原样包含 `empty`、`manifest`、`protocol lock`、`registry`、`task_stats`、`SHA-256`、`synthetic adapter`、`Gate 4`、`GPU`、`claim`。

memo 解释五个产物如何从 spec 形成、receipt 能/不能证明什么、为何 B 不是模型结果，并口述真实 adapter 的中断恢复证据。正文不展示 B episode 数与统计。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day25.tests.test_day25_tools
.venv-day06/bin/python mainline/day25/code/check_day25.py \
  --example-spec shared/fixtures/day25_mini_spec_a.json \
  --example-dir learner_outputs/mainline/day25/package_a \
  --challenge-spec shared/fixtures/day25_mini_spec_b.json \
  --challenge-dir learner_outputs/mainline/day25/package_b \
  --challenge-memo learner_outputs/mainline/day25/gate4_memo.md
```

口述 10 分：empty/spec→manifest 2；protocol/registry 2；stats/receipt 2；resume/evidence 2；GPU/synthetic/claim 边界 2。CPU 机器验收 + 口述 ≥8 只表示 rehearsal 通过；正式 Gate 4 还必须有真实 adapter 的中断恢复与 evidence。复用旧目录、手改输出、伪造 GPU/video 或把 hash 当科学真值均不通过。

## 10. 证据复盘

- 已运行：A/B clean directory package、非空拒绝、锁定 commit、SHA-256 与精确字节重建测试。
- 未运行：真实 evaluator、GPU、视频、真实中断恢复与 formal Gate 4。
- 可以主张：synthetic mini pipeline 能从 spec 完整重建指定 artifact set。
- 不能主张：真实 baseline 可复现、任何模型成功率或学习者已通过 Gate 4。

自测题（答案在 `shared/answer_keys/day25.md`）：

1. 为什么要求输出目录 empty？
2. receipt 的 SHA-256 能证明和不能证明什么？
3. 为什么 manifest 必须由 spec 生成？
4. CPU rehearsal 与 formal Gate 4 差什么证据？
5. 如何证明 resume 没有重复执行 completed episode？
