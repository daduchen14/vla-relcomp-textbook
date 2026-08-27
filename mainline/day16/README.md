# Mainline Day 16：建立 run/episode registry 与证据命名

今天把 Day 15 冻结口径变成两张可续跑的数据表：run 表保存批次共同身份，episode 表保存 task×seed×init 的逐项计划。你会生成稳定主键、外键、状态相关缺失值和不会串线的证据路径；当前 fixture 仍是合成计划，不是模型结果。

## 1. 真实项目产物

- `learner_outputs/mainline/day16/runs_a.csv`、`episodes_a.csv`：A 批次的一条 run 与三条 planned episodes；
- `learner_outputs/mainline/day16/schema_a.json`、`validation_a.json`：主外键、状态枚举与缺失值契约；
- 对新 B spec 生成同构的四个挑战资产和 `challenge_memo.md`。

Day 17 的可恢复 runner 将按 `episode_id` 更新这些行，不再靠文件数量猜进度。

## 2. 当前卡点

一个 CSV 若只写 task/seed，很容易在两个模型、两个 config 或两个 level 间撞行；若用第 17 行当 ID，排序后身份立刻变化。更严重的是把“尚未运行”写成 `success=0`，这会让缺失 episode 进入失败分母。

本课把共同身份提升为 `run_id`，再把 run_id+task+seed+init 变成 `episode_id`。结果字段在 `PLANNED` 时必须为空；0/1 只在实际观察后出现。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day16/code/minimal_primary_key.py
```

应看到规范化 JSON identity 和 `ep-` 开头的稳定 ID。若字典/JSON 卡住补 [F02](../../foundation_library/f02_csv_json/README.md)，若 hash 概念卡住回看 [Day 15](../day15/README.md)。

## 4. 即时知识

- **primary key**：表内唯一、非空、稳定标识一行；本课分别是 run_id 与 episode_id。
- **foreign key**：episode.run_id 必须指向真实 runs.run_id，防止孤儿行。
- **自然身份**：task×seed×init 等业务字段；规范化后 hash 得到便于传递的代理键。
- **missing**：未观察不是失败。PLANNED 的 success/steps/wall_seconds 留空。
- **状态约束**：COMPLETED 要求结果齐全；INVALID/FAILED 保存 exception，环境异常不进入模型失败分母。
- **证据命名**：`learner_outputs/evidence/<run_id>/<episode_id>/rollout.mp4`，路径身份与表身份一致。

## 5. 成熟材料处方

- **中文主材料（10 分钟）**：[Python 官方 `csv` 文档](https://docs.python.org/zh-cn/3/library/csv.html)。只读 DictReader/DictWriter 与 `newline=''`，确认 CSV 读回后值都是字符串。
- **schema 补充（英文规范，15 分钟）**：[Frictionless Table Schema](https://specs.frictionlessdata.io/table-schema/)。只读 fields、primaryKey、foreignKeys、missingValues；本课用轻量 JSON 契约实现相同思想，不要求安装工具。

## 6. 最小实验

[minimal_primary_key.py](code/minimal_primary_key.py) 是完整 12 行例子：

```python
#!/usr/bin/env python3
"""最小例子：稳定主键来自规范化身份，不来自 CSV 行号。"""

import hashlib
import json

identity = {"run_id": "run-demo", "task_id": 2, "seed": 17, "init_state_index": 4}
canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
episode_id = "ep-" + hashlib.sha256(canonical.encode()).hexdigest()[:16]

print(f"identity={canonical}")
print(f"episode_id={episode_id}")
```

字段排序和紧凑分隔符固定 canonical bytes；换 CSV 行序不会换 ID，改 init 会换 ID。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day16/code/build_registry.py \
  --spec shared/fixtures/day16_registry_spec_a.json \
  --runs learner_outputs/mainline/day16/runs_a.csv \
  --episodes learner_outputs/mainline/day16/episodes_a.csv \
  --schema learner_outputs/mainline/day16/schema_a.json
.venv-day06/bin/python mainline/day16/code/validate_registry.py \
  --runs learner_outputs/mainline/day16/runs_a.csv \
  --episodes learner_outputs/mainline/day16/episodes_a.csv \
  --schema learner_outputs/mainline/day16/schema_a.json \
  --report learner_outputs/mainline/day16/validation_a.json
```

应看到一条 run、三条 planned episode，所有结果字段 blank。打开 episodes，确认四种 evidence path 均含相同 run_id/episode_id。长脚本 [build_registry.py](code/build_registry.py) 按 `stable_id→validate_spec→build→write_csv` 阅读；[validate_registry.py](code/validate_registry.py) 会重算两级 ID、外键、count、路径和状态缺失规则。

真实运行前，用 Day 15 formal lock hash、实际 code commit/model revision/config hash 创建新 spec；A/B 的 synthetic 值不能替换。当前不创建空视频文件：路径是登记目标，证据必须由真实 evaluator 原子写入。

若 ID 校验失败，检查是否手改身份列；外键悬空先找 runs 行；PLANNED 报结果非空时删掉猜测值而非改 status；证据路径错配时重新生成，禁止批量字符串替换 ID。

## 8. 独立挑战

换用 `day16_registry_spec_b.json` 生成 B 的 runs/episodes/schema/report。写 ≥150 字 `challenge_memo.md`，必须出现 `primary key`、`foreign key`、`PLANNED`、`missing`、`success=0`、`evidence`，解释 B 的两级身份、空值语义和完成/异常状态。

不得复制 A 后只改 run_id：机器会从 B model/config/level/task/seed/init 重算所有 ID 与路径。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day16.tests.test_day16_tools
.venv-day06/bin/python mainline/day16/code/check_day16.py \
  --example-spec shared/fixtures/day16_registry_spec_a.json \
  --example-runs learner_outputs/mainline/day16/runs_a.csv \
  --example-episodes learner_outputs/mainline/day16/episodes_a.csv \
  --example-schema learner_outputs/mainline/day16/schema_a.json \
  --example-report learner_outputs/mainline/day16/validation_a.json \
  --challenge-spec shared/fixtures/day16_registry_spec_b.json \
  --challenge-runs learner_outputs/mainline/day16/runs_b.csv \
  --challenge-episodes learner_outputs/mainline/day16/episodes_b.csv \
  --challenge-schema learner_outputs/mainline/day16/schema_b.json \
  --challenge-report learner_outputs/mainline/day16/validation_b.json \
  --challenge-memo learner_outputs/mainline/day16/challenge_memo.md
```

口述 10 分：两级主键 2；外键/count 2；missing 与 0 2；状态转换 2；证据命名 2。机器通过且 ≥8 进入 Day 17；用行号作 ID、把未跑写失败或用空证据冒充结果必须重做。

## 10. 证据复盘

- 已运行：A/B 生成与验证、主外键/重复身份/状态缺失/路径错配测试。
- 未运行：formal lock 对应 registry、任何 evaluator、视频或模型结果。
- 可以主张：schema、稳定 ID、计划空值和证据命名可重算。
- 不能主张：计划 episode 已运行、空 success 是失败，或登记路径上的证据已存在。

自测题（答案在 `shared/answer_keys/day16.md`）：

1. run_id 与 episode_id 各标识什么，怎样连接？
2. 为什么 CSV 行号不能当 primary key？
3. 空 success 与 success=0 有何本质区别？
4. evidence path 为什么同时包含两级 ID？
5. COMPLETED/INVALID 分别要求保留什么？
