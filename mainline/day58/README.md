# Mainline Day 58：确定性选择代表案例并建立视频证据表

今天先冻结 stable success、recovery、damage、stable failure 四个 strata 和配额，再在每层用 salted SHA-256 排序 episode ID 选择案例。这样不会手挑最戏剧化的视频，也不会只展示正例。当前路径为 synthetic，视频未观看，casebook 尚非最终证据。

## 1. 真实项目产物

- `casebook_a.json`：coverage、selected cases、selection rank、episode hash 与 video review status；
- manual override/cherry-picking 防护；
- B 新 inventory/quota 的 casebook 与 `challenge_memo.md`。

## 2. 当前卡点

论文案例最容易事后挑选：只展示恢复、不展示 damage；在几十个相似视频里挑最清楚的一条也可能与结果相关。纯随机又可能漏掉关键少数 strata。

本课先分层再确定性抽样。salt 在看 episode IDs/结果前冻结；casebook 同时列 selected/unselected 数。synthetic video path 只测试表结构，审阅状态明确 NOT_VIEWED。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day58/code/minimal_deterministic_sample.py
```

应看到 recovery/damage 各选一条且 manual override false。若 hash/排序不熟回看 [Day 51](../day51/README.md)；transition strata 回看 [Day 47](../day47/README.md)。

## 4. 即时知识

- **casebook**：将代表 episode、视频、原始记录和解释边界连接的证据表。
- **representative case**：按预注册规则选中，不等于“最漂亮”。
- **stratum quota**：每类固定名额，覆盖正例与反例。
- **salted hash**：`hash(salt|episode_id)` 给出确定性伪随机排名。
- **deterministic selection**：相同 input/config 总能重建相同案例。
- **manual override**：人工换样本；本课禁止静默 override。
- **episode hash**：case 与原始 record 的身份连接。
- **video review status**：区分路径存在、已观看、已核验三种状态。

## 5. 成熟材料处方

- **中文主材料（Python 官方，8 分钟）**：[hashlib](https://docs.python.org/zh-cn/3/library/hashlib.html)。只理解 SHA-256 的确定性与 bytes 输入；它不是随机数也不是代表性保证。
- **补充材料（Matplotlib 官方，8 分钟）**：[Choosing Colormaps](https://matplotlib.org/stable/users/explain/colors/colormaps.html)。只理解展示选择会影响读者感知；Day 58 不画图。
- **锁定项目定位（8 分钟）**：[evaluator 第 199–218 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L199-L218) 生成带 episode/success/task 的视频文件；[第 456 行以后](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L456-L480) 按 save mode 选择视频。正式 casebook 必须从 all/完整 registry 选，不能只依赖 first success/failure 保存策略。

## 6. 最小实验

[minimal_deterministic_sample.py](code/minimal_deterministic_sample.py) 是完整 23 行代码：

```python
#!/usr/bin/env python3
"""最小例子：按预注册 strata 和 salted hash 选案例。"""

import hashlib

episodes = [
    ("ep01", "recovery"), ("ep02", "recovery"),
    ("ep03", "damage"), ("ep04", "damage"),
]
salt = "casebook-v1"
quota = {"recovery": 1, "damage": 1}

selected = []
for stratum, count in quota.items():
    candidates = [episode for episode, label in episodes if label == stratum]
    ranked = sorted(
        candidates,
        key=lambda item: hashlib.sha256(f"{salt}|{item}".encode()).hexdigest(),
    )
    selected.extend((stratum, item) for item in ranked[:count])

print(f"selected={selected}")
print("manual_override=false")
```

长文件 [build_casebook.py](code/build_casebook.py) 负责 quota、salted rank、coverage 和 NOT_VIEWED boundary。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day58/code/build_casebook.py \
  --input shared/fixtures/day58_cases_a.json --config mainline/day58/config/casebook_a.json \
  --casebook learner_outputs/mainline/day58/casebook_a.json
```

A 应选 4 cases、覆盖四 strata、videos viewed false。未来正式操作先从 Day 52–57 raw registry 生成 strata，再封存 salt/quota；选择后验证视频 bytes/hash、episode record、任务/初态/结果一致，并记录观察注释和 reviewer。视频缺失不得事后挑替代品，按冻结 fallback 处理。

## 8. 独立挑战

用 B inventory/config 生成新 casebook。写 ≥270 字 memo，必须原样包含 `casebook`、`representative case`、`stratum quota`、`stable success`、`recovery`、`damage`、`stable failure`、`salted hash`、`deterministic selection`、`manual override`、`cherry-picking`、`video path`、`episode hash`、`not viewed`、`cannot claim`。正文不给 B selected IDs。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day58.tests.test_day58_tools
.venv-day06/bin/python mainline/day58/code/check_day58.py \
  --example-input shared/fixtures/day58_cases_a.json --example-config mainline/day58/config/casebook_a.json --example-casebook learner_outputs/mainline/day58/casebook_a.json \
  --challenge-input shared/fixtures/day58_cases_b.json --challenge-config mainline/day58/config/casebook_b.json --challenge-casebook learner_outputs/mainline/day58/casebook_b.json \
  --challenge-memo learner_outputs/mainline/day58/challenge_memo.md
```

口述 10 分：strata/quota 2；hash selection 2；反 cherry-pick 2；证据链接 2；未观看边界 2。机器通过且 ≥8 进入 Day 59；漏 damage、人工替换、无 episode hash、synthetic path 当视频或声称 casebook final 均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic inventory 的分层、salted rank、coverage 和 case table。
- 静态源码事实：锁定 evaluator 的视频命名和 save-mode 入口。
- 未运行：真实视频生成、文件/hash 验证、观看和 reviewer 标注。
- 可以主张：案例选择规则可重建并覆盖四种结果 strata。
- 不能主张：选中视频真实存在、内容代表总体或任何机制解释成立。

自测题（答案在 `shared/answer_keys/day58.md`）：

1. 为什么先分 strata 再设 quota？
2. salted hash 防止什么选择偏差？
3. 视频不清楚时能否人工替换？
4. casebook 每条至少链接哪些证据？
5. synthetic video path 能否当正式视频证据？
