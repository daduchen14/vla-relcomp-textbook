# Mainline Day 59：汇总时间、显存、失败运行和成本

今天把 planned、attempted、completed、failed、not-run 五个分母分开，汇总所有 attempted runs 的 wall time、GPU-hours、peak memory、storage 和估算费用。失败运行已经消耗资源，必须进入 GPU-hours/成本；not-run 保留在计划分母但测量为零。当前 ledger 全是 synthetic。

## 1. 真实项目产物

- `resource_report_a.json`：五分母、完成/失败率、资源总量、失败明细和 condition breakdown；
- 失败成本计入标志与 synthetic/real 边界；
- B 新 ledger/rate 的报告与 `challenge_memo.md`。

## 2. 当前卡点

只平均成功 runs 会把 OOM、crash 的时间和钱抹掉；用 planned 作 failure rate 分母又会把未启动 run 当成功。peak memory 若只报“典型”值，也可能隐藏失败 run 的真正峰值。

本课要求每个 planned run 恰好一条状态记录。attempted 必须有正 wall/GPU/memory，not-run 必须为零；费用按冻结 synthetic hourly rate 计算，并明确不是账单。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day59/code/minimal_resource_denominator.py
```

应看到 planned 3、attempted 2、failure rate .5、GPU-hours 1.5。若进程/退出码不熟补 [F05](../../foundation_library/f05_linux_processes/README.md)；预算概念回看 [Day 41](../day41/README.md)。

## 4. 即时知识

- **resource ledger**：每个 planned run 的状态、测量和失败原因原始表。
- **planned**：最终 manifest 中应运行的总数。
- **attempted**：实际启动过的 completed+failed。
- **not run**：未启动；不是成功，也没有实际资源测量。
- **failure denominator**：failed/attempted。
- **GPU-hours**：`gpu_count × gpu_seconds / 3600`，含失败。
- **peak memory**：每个 attempted run 峰值，汇总报告最大值。
- **estimated cost**：GPU-hours×冻结单价；需与真实账单区分。

## 5. 成熟材料处方

- **中文主材料（NVIDIA，10 分钟）**：[nvidia-smi 文档](https://docs.nvidia.com/deploy/nvidia-smi/index.html)。只定位 memory、utilization、process 和 query CSV 字段；真实运行要记录采样命令/频率。
- **补充材料（Python 官方，6 分钟）**：[time](https://docs.python.org/zh-cn/3/library/time.html#time.monotonic)。理解墙钟计时宜用 monotonic，不能用日志时间戳相减替代可靠测量。
- **锁定项目定位（8 分钟）**：[trainer 第 80–118 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/scripts/train.py#L80-L118) 记录 update time/loss/grad/lr；[第 237–269 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/scripts/train.py#L237-L269) 记录 dataloading 并进入日志。GPU memory/总墙钟/退出码仍需外层 runner 采集。

## 6. 最小实验

[minimal_resource_denominator.py](code/minimal_resource_denominator.py) 是完整 19 行代码：

```python
#!/usr/bin/env python3
"""最小例子：失败运行也进入尝试次数与资源成本。"""

runs = [
    {"status": "completed", "gpu_seconds": 3600},
    {"status": "failed", "gpu_seconds": 1800},
    {"status": "not_run", "gpu_seconds": 0},
]

attempted = [row for row in runs if row["status"] != "not_run"]
completed = [row for row in attempted if row["status"] == "completed"]
failed = [row for row in attempted if row["status"] == "failed"]
gpu_hours = sum(row["gpu_seconds"] for row in attempted) / 3600

print(f"planned={len(runs)}")
print(f"attempted={len(attempted)}")
print(f"completed={len(completed)} failed={len(failed)}")
print(f"failure_rate={len(failed)/len(attempted):.3f}")
print(f"gpu_hours_including_failures={gpu_hours:.3f}")
```

长文件 [summarize_resources.py](code/summarize_resources.py) 检查 run completeness/status-measurement consistency，再按 condition 和总表汇总。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day59/code/summarize_resources.py \
  --input shared/fixtures/day59_resources_a.json --config mainline/day59/config/resource_a.json \
  --report learner_outputs/mainline/day59/resource_report_a.json
```

A synthetic 应为 planned 5、attempted 4、failed 1、GPU-hours 约 3.667。未来正式 runner 要在启动/退出时写 monotonic wall time、GPU UUID/count、周期 nvidia-smi 与 peak、存储增量、exit code/signal、failure reason；not-run 也写原因。单价需附 provider/日期，账单与估算分栏。

## 8. 独立挑战

用 B ledger/config 生成新 report。写 ≥270 字 memo，必须原样包含 `resource ledger`、`planned`、`attempted`、`completed`、`failed`、`not run`、`failure denominator`、`wall time`、`GPU-hours`、`peak memory`、`storage`、`failed cost`、`hourly rate`、`synthetic measurements`、`cannot claim`。正文不给 B 总数。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day59.tests.test_day59_tools
.venv-day06/bin/python mainline/day59/code/check_day59.py \
  --example-input shared/fixtures/day59_resources_a.json --example-config mainline/day59/config/resource_a.json --example-report learner_outputs/mainline/day59/resource_report_a.json \
  --challenge-input shared/fixtures/day59_resources_b.json --challenge-config mainline/day59/config/resource_b.json --challenge-report learner_outputs/mainline/day59/resource_report_b.json \
  --challenge-memo learner_outputs/mainline/day59/challenge_memo.md
```

口述 10 分：五分母 2；失败成本 2；时间/GPU 2；显存/存储 2；synthetic 边界 2。机器通过且 ≥8 进入 Day 60；删失败、错分母、not-run 填测量、peak 取均值或估算冒充账单均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic run ledger 的分母、资源、失败和估算成本。
- 静态源码事实：锁定 trainer 的 update/dataload/log timing 入口。
- 未运行：真实 GPU、nvidia-smi、cloud bill、VLA-Arena experiments。
- 可以主张：脚本不会从资源/失败分母中删除失败 runs。
- 不能主张：实际花费、显存需求、吞吐或系统可靠性。

自测题（答案在 `shared/answer_keys/day59.md`）：

1. planned 与 attempted 有何区别？
2. failure rate 的正确分母是什么？
3. 失败运行消耗是否计入成本？
4. peak memory 应怎样汇总？
5. synthetic ledger 能否作为真实云账单？
