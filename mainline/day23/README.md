# Mainline Day 23：把视频、异常和四段事件连接到 episode

今天建立一张可审计的 evidence index：以 episode registry 为唯一左表，把 video、exception 和 Day 12 的四段事件按 `episode_id` 一对一连接。输出行数必须与 registry 相同；缺证据保留为空并进入审阅队列，不能把 episode 静默删掉。

## 1. 真实项目产物

- `learner_outputs/mainline/day23/evidence_index_a.csv`：每个 episode 的视频、异常、stage 与分级；
- `evidence_report_a.json`：输入/输出 cardinality、证据状态和审阅优先级计数；
- B 换输入后的 index/report 与 `challenge_memo.md`。

## 2. 当前卡点

成功率表告诉你“发生了什么”，但排错需要找到对应视频、异常和行为链。直接 inner join 会丢掉没有视频的行；右表重复键会把一个 episode 乘成多行；文件名解析若与 registry ID 不同，会产生 orphan。更危险的是把 missing video 当作失败，或把某个 stage=false 直接写成 causal 原因。

本课将 registry 定为事实主表，其他表只补证据。每张右表都必须 `episode_id` 唯一且不得出现主表外 ID；left join 后 cardinality 不变。输出 `evidence_state` 只做 triage：P0 运行异常、P1 缺证据/信号冲突、P2 完整失败、P3 完整成功。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day23/code/minimal_left_join.py
```

应看到 e3 仍在输出且 video 为 `MISSING`，最后 `input_rows=3`。若字典 key/`get` 不熟，补 [F02](../../foundation_library/f02_csv_json/README.md)；若 episode 主键不熟，回看 [Day 16](../day16/README.md)。

## 4. 即时知识

- **left join**：保留左表所有行；右表匹配不到就填空。
- **primary key**：registry 的 `episode_id` 非空且唯一。
- **1:1 cardinality**：左右同一 key 最多各一行；输出行数等于左表。
- **orphan evidence**：video/stage/exception 出现 registry 不认识的 ID，通常表示命名或批次混入。
- **missing ≠ failure**：缺视频/探针是证据质量问题；success=0 是完成运行后的行为结果。
- **signal conflict**：success 与 relation probe 不一致，应保留两者并优先复查，而非覆盖其中一个。
- **triage ≠ causal diagnosis**：P0–P3 决定先看什么，不说明语言、视觉或控制机制。

## 5. 成熟材料处方

- **中文主材料（8 分钟）**：[Python 字典与 `get()` 教程](https://docs.python.org/zh-cn/3/tutorial/datastructures.html#dictionaries)。只读“键唯一”和 `get()` 缺键返回默认值；对应最小 left join。
- **工程主材料（12 分钟）**：[pandas `merge` 官方 API](https://pandas.pydata.org/docs/reference/api/pandas.merge.html)。只读 `how='left'`、`indicator` 和 `validate='one_to_one'`；本课不用 pandas，但在纯 CSV 脚本中手工实现相同约束。
- **锁定项目材料（10 分钟）**：[SmolVLA evaluator 第 452–483 行（锁定 commit）](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L452-L483)。确认 success 计数、选择性保存视频与日志是不同输出；`first_success_failure` 模式天然让部分 episode 没视频，因此缺视频不能自动等于失败。

## 6. 最小实验

[minimal_left_join.py](code/minimal_left_join.py) 是完整 20 行代码：

```python
#!/usr/bin/env python3
"""最小例子：registry 是左表，证据缺失必须保留。"""

episodes = [
    {"episode_id": "e1", "success": "1"},
    {"episode_id": "e2", "success": "0"},
    {"episode_id": "e3", "success": ""},
]
videos = {
    "e1": "evidence/e1.mp4",
    "e2": "evidence/e2.mp4",
}

for episode in episodes:
    episode_id = episode["episode_id"]
    video = videos.get(episode_id, "MISSING")
    print(episode_id, episode["success"], video)

print(f"input_rows={len(episodes)}")
print("boundary=missing_evidence_is_not_model_failure")
```

把 `videos` 中 e2 删除，输出仍有三行。把相同 key 存入字典两次会覆盖旧值，所以正式脚本不能直接推导字典，必须先显式检测重复。

## 7. 真实 VLA-Arena 操作

免费合成 A：

```bash
.venv-day06/bin/python mainline/day23/code/build_evidence_index.py \
  --registry shared/fixtures/day23_registry_a.csv \
  --videos shared/fixtures/day23_videos_a.csv \
  --stages shared/fixtures/day23_stages_a.csv \
  --exceptions shared/fixtures/day23_exceptions_a.csv \
  --output learner_outputs/mainline/day23/evidence_index_a.csv \
  --report learner_outputs/mainline/day23/evidence_report_a.json
```

应看到 `evidence_rows=5 cardinality_preserved=true`，并同时包含完整、缺失、冲突和运行异常状态。这些路径与 probe 是 synthetic fixture。

接真实数据时，从 Day 16/17 registry 导出终态；Day 18 video index 必须记录实际存在性，不只拼路径；Day 12 stage summary 必须按同一 episode ID 聚合；异常表保留 type/message 与日志路径。先检查各右表唯一键和 orphan，再 left join。文件确实不存在就写 `MISSING/NOT_INDEXED`，不要创建空 mp4；运行错误保留 success 为空。

P0 先查环境/adapter 日志；P1 查视频缺失或 success/relation 冲突；P2 用完整视频与四段事件做失败复盘；P3 可抽样质控。这个顺序节省审阅时间，但不能拿 priority 当失败严重程度或模型内部原因。

## 8. 独立挑战

用四个 `day23_*_b.csv` 生成 B index/report，不给出正文输出。写 ≥180 字 memo，必须原样包含 `episode_id`、`left join`、`cardinality`、`orphan`、`video`、`exception`、`stage`、`missing`、`causal`。

解释 q4 为什么必须保留、重复右键为何会膨胀行数、孤儿证据为何应报错，以及 triage 为什么不是 causal diagnosis。不得复制 A 计数或参考答案段落。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day23.tests.test_day23_tools
.venv-day06/bin/python mainline/day23/code/check_day23.py \
  --example-registry shared/fixtures/day23_registry_a.csv --example-videos shared/fixtures/day23_videos_a.csv \
  --example-stages shared/fixtures/day23_stages_a.csv --example-exceptions shared/fixtures/day23_exceptions_a.csv \
  --example-output learner_outputs/mainline/day23/evidence_index_a.csv --example-report learner_outputs/mainline/day23/evidence_report_a.json \
  --challenge-registry shared/fixtures/day23_registry_b.csv --challenge-videos shared/fixtures/day23_videos_b.csv \
  --challenge-stages shared/fixtures/day23_stages_b.csv --challenge-exceptions shared/fixtures/day23_exceptions_b.csv \
  --challenge-output learner_outputs/mainline/day23/evidence_index_b.csv --challenge-report learner_outputs/mainline/day23/evidence_report_b.json \
  --challenge-memo learner_outputs/mainline/day23/challenge_memo.md
```

口述 10 分：主键/left join 2；1:1 cardinality 2；orphan/重复检测 2；missing 与 triage 2；causal/fixture 边界 2。机器通过且 ≥8 进入 Day 24；inner join 丢行、右键重复、伪造视频或把证据状态当机制均不通过。

## 10. 证据复盘

- 已运行：A/B 合成 registry/video/stage/exception 的严格连接、缺失/冲突分类和键约束测试。
- 未运行：真实视频存在性扫描、真实日志异常、真实四段事件 join、GPU。
- 可以主张：evidence index 可一对一重建且保持 registry cardinality。
- 不能主张：真实模型证据完整率或任何 causal 失败结论。

自测题（答案在 `shared/answer_keys/day23.md`）：

1. 为什么 registry 必须是 left join 的左表？
2. 右表重复 episode_id 会造成什么问题？
3. orphan evidence 应如何处理？
4. missing video 与 success=0 有何不同？
5. review priority 能否说明模型内部原因？
