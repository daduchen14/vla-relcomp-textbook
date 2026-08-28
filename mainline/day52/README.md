# Mainline Day 52：干净重跑主基线并隔离缓存污染

今天先为最终 baseline 建立 clean-room allowlist：只接受按 hash 锁定的 upstream、base model、raw dataset、environment lock 与 initial states；repair checkpoints、旧评测结果和训练 cache 全部拒绝。输出是未运行 packet，不是 final baseline data。

## 1. 真实项目产物

- `clean_baseline_packet_a.json`：接受/拒绝清单、cache policy、cleanroom id 与计划命令；
- `baseline_records=null` 和 NOT_RUN 状态；
- B 新 inventory/config 的 packet 与 `challenge_memo.md`。

## 2. 当前卡点

同一目录重跑可能悄悄复用旧 result、repair checkpoint 或 optimizer state；即使命令写 baseline，输入污染也会让结果不可称为干净基线。另一方面，完全禁用下载 cache 会浪费资源，关键是只读、按 hash 和角色隔离。

本课采用 allowlist 而非文件名猜测。模型/数据 cache 只读，eval cache 新建为空，output 使用唯一目录；所有被拒绝 artifact 也记录下来作为污染审计证据。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day52/code/minimal_allowlist.py
```

应看到 3 个 accepted、2 个 rejected 和 `clean=true`。若角色/JSON 不熟补 [F02](../../foundation_library/f02_csv_json/README.md)；final hash 回看 [Day 51](../day51/README.md)。

## 4. 即时知识

- **clean-room rerun**：从显式允许输入开始、输出到新位置的独立重跑。
- **allowlist**：只接受列出的角色；未知角色默认拒绝。
- **cache contamination**：旧缓存改变输入、输出或决策而未被记录。
- **read-only cache**：可复用相同 hash 的 base/data bytes，但不得写回或自动升级。
- **empty eval cache**：本次结果目录起始为空，避免旧记录混入。
- **unique output**：run id 独占目录，不覆盖其他 condition/seed。
- **artifact hash**：确认 bytes 身份，不依赖易混淆文件名。
- **packet ≠ data**：准备清单通过不代表 evaluator 已运行。

## 5. 成熟材料处方

- **中文主材料（Git 官方，8 分钟）**：[Git 内部原理：环境变量](https://git-scm.com/book/zh/v2/Git-内部原理-环境变量)。只看环境变量如何改变仓库/对象位置，理解 clean-room 必须记录环境；不要求修改 Git。
- **补充材料（Reproducible Builds，8 分钟）**：[Build Path](https://reproducible-builds.org/docs/build-path/)。只理解绝对路径/环境残留会影响复现；本课不声称实现完整 reproducible build。
- **锁定项目定位（8 分钟）**：[VLA-Arena launcher 第 26–53 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/cli/train.py#L26-L53) 解析 config/trainer 路径；[SmolVLA evaluator 第 173–178 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L173-L178) 从 `policy_path` 加载模型。clean baseline 必须让该 path 指向锁定 base model，而非 repair。

## 6. 最小实验

[minimal_allowlist.py](code/minimal_allowlist.py) 是完整 22 行代码：

```python
#!/usr/bin/env python3
"""最小例子：clean-room 只复制显式允许的输入角色。"""

inventory = [
    ("upstream", "src@locked"),
    ("base_model", "smolvla-base"),
    ("raw_dataset", "l0-l2"),
    ("repair_checkpoint", "repair-seed1"),
    ("old_eval_cache", "results.json"),
]
allowed_roles = {"upstream", "base_model", "raw_dataset"}

accepted = [item for role, item in inventory if role in allowed_roles]
rejected = [
    {"role": role, "item": item}
    for role, item in inventory
    if role not in allowed_roles
]

print(f"accepted={accepted}")
print(f"rejected={rejected}")
print(f"clean={str(len(rejected) == 2).lower()}")
```

长文件 [build_clean_baseline_packet.py](code/build_clean_baseline_packet.py) 检查 required roles、拒绝污染源并绑定 cleanroom id。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day52/code/build_clean_baseline_packet.py \
  --inventory shared/fixtures/day52_inventory_a.json --config mainline/day52/config/clean_baseline_a.json \
  --packet learner_outputs/mainline/day52/clean_baseline_packet_a.json
```

A 应接受 5 项、拒绝 2 项并保持 NOT_RUN。未来授权后要从真实文件系统 inventory 计算强 hash，创建新的 eval/output dirs，校验 `policy_path` 是 base model，再按 Day 51 manifest 运行每个 cell；运行前后都保存 inventory 和环境。当前不执行 evaluator。

## 8. 独立挑战

用 B inventory/config 生成新 packet。写 ≥270 字 memo，必须原样包含 `clean-room`、`baseline`、`allowlist`、`locked upstream`、`base model`、`raw dataset`、`repair checkpoint`、`old eval result`、`cache contamination`、`read-only`、`empty eval cache`、`unique output`、`artifact hash`、`NOT_RUN`、`cannot claim`。正文不给 B cleanroom id。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day52.tests.test_day52_tools
.venv-day06/bin/python mainline/day52/code/check_day52.py \
  --example-inventory shared/fixtures/day52_inventory_a.json --example-config mainline/day52/config/clean_baseline_a.json --example-packet learner_outputs/mainline/day52/clean_baseline_packet_a.json \
  --challenge-inventory shared/fixtures/day52_inventory_b.json --challenge-config mainline/day52/config/clean_baseline_b.json --challenge-packet learner_outputs/mainline/day52/clean_baseline_packet_b.json \
  --challenge-memo learner_outputs/mainline/day52/challenge_memo.md
```

口述 10 分：allowlist 2；污染源 2；cache policy 2；hash/cleanroom 2；NOT_RUN 2。机器通过且 ≥8 进入 Day 53；接受 repair/旧结果、可写 cache、复用 output、无 hash 或声称 baseline data 已产生均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic inventory 的 allow/reject、cache policy 和 cleanroom id。
- 静态源码事实：锁定 launcher config 解析与 evaluator policy load。
- 未运行：真实文件扫描、SmolVLA、VLA-Arena、GPU 或 final baseline episodes。
- 可以主张：packet 不会接受已标记的 repair/old-result/training-cache 角色。
- 不能主张：真实环境无污染、baseline data 已存在或结果可复现。

自测题（答案在 `shared/answer_keys/day52.md`）：

1. clean-room baseline 允许哪些输入？
2. 为什么必须拒绝 old eval result？
3. cache 是否一律禁止，允许时有什么条件？
4. cleanroom id 绑定哪些身份？
5. packet 通过是否表示 final baseline data 已产生？
