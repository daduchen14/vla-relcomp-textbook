# Mainline Day 8：把 pilot 扩成矩阵，并用 L0 选择主诊断模型

今天结束“凭印象选轻量模型”。你会把两个锁定模型展开为 L0/L1/L2 × 5 task × 5 seed/init 的 150 行计划矩阵，冻结有效分母与 L0-only 选择规则。真实 GPU 结果尚不存在，因此项目结论仍是“待运行”；Gate 2 只用明确标记的合成陌生 registry 检验判断能力。

## 1. 真实项目产物

- `learner_outputs/mainline/day08/pilot_matrix.json`：2 模型 × 3 level × 5 task × 5 seed/init；
- 真实运行后才会有 `pilot_registry.csv` 与 `model_selection.json`；本机不制造这两项真实结果；
- `learner_outputs/mainline/day08/gate2_fixture_report.json`：对合成 Gate registry 的可复算摘要；
- `learner_outputs/mainline/day08/gate2_decision.json`：独立给出有效分母、模型选择与下一步最小实验。

D1 的硬条件是至少一个模型完成 5 task × 3 level × 5 次试验，即 75 个有效 episode。这里为两个候选都预登记 75 行，便于同口径比较；计划 150 行不等于已运行 150 次。

## 2. 当前卡点

官方表提示 OpenVLA 的 L0 可能高于 SmolVLA，但论文数字不是你当前锁定 checkpoint、代码与 seed 的本地证据。主诊断模型需要足够多的 L0 成功行为，才能比较“成功链在哪一段断掉”；若 L0 几乎总失败，后续关系诊断会把基础控制无能误当成组合泛化。

另一个陷阱是错误分母。OOM、环境启动失败、视频/日志缺失都不是任务失败；把它们填成 `success=false` 会系统性压低模型成绩。反过来删除这些行又会隐藏系统不稳定，所以必须“保留原记录，但排除模型成功率分母”。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day08/code/minimal_denominator.py
```

应得到 `1/2=50.0%`，排除 `e3` 和 `e4`。若把分母算成 4，补 [F02 CSV/JSON](../../foundation_library/f02_csv_json/README.md)；说不清 episode loop 与基础设施错误，补 [F08](../../foundation_library/f08_episode_evaluator/README.md)；不理解 L0/L1/L2，先读本日材料，不回头连续学整套基础库。

## 4. 即时知识

- **训练分布与 OOD**：锁定研究把 L0 视为训练分布能力，L1 为近分布外组合，L2 为更强分布偏移；它们不是简单的“容易、中等、困难”标签。
- **有效分母**：只有 `completed + evidence_complete=true + success∈{true,false}` 才计入模型 success rate。
- **任务覆盖**：只看 L0 总成功数可能由单个 task 垄断；诊断需要每个 task 都至少出现一次成功行为。
- **预注册工作规则**：先要求每个 level 各 25 个有效 episode，满足 D1 的 75 次完整 pilot；再看 25 个 L0 中是否至少 10 个成功、5/5 task 有成功。阈值不是 VLA-Arena 官方标准。
- **L0-only 选模**：L1/L2 是否跑齐属于执行完整性；它们的成功率不用来选择模型/checkpoint。多个合格候选按 L0 成功数择优，精确并列则输出证据不足。

## 5. 成熟材料处方

- **中文主材料（20 分钟）**：[《动手学深度学习》4.9 环境和分布偏移](https://zh.d2l.ai/chapter_multilayer-perceptrons/environment.html)。读 4.9.1–4.9.3，重点区分训练/测试分布与分布偏移；不做数学推导。
- **项目论文（英文主源，15 分钟）**：[VLA-Arena §2.2 Task Structure](https://arxiv.org/html/2512.22539v4#S2.SS2)。只读 L0/L1/L2 定义和它们为何提供非冗余信息；论文表格是外部基准背景，不替代本项目 registry。

## 6. 最小实验

[minimal_denominator.py](code/minimal_denominator.py) 是完整 26 行例子：

```python
#!/usr/bin/env python3
"""最小例子：基础设施错误不进入模型成功率分母。"""

ROWS = [
    {"episode": "e1", "status": "completed", "evidence": True, "success": True},
    {"episode": "e2", "status": "completed", "evidence": True, "success": False},
    {"episode": "e3", "status": "infrastructure_error", "evidence": False, "success": None},
    {"episode": "e4", "status": "completed", "evidence": False, "success": True},
]


def summarize(rows: list[dict]) -> tuple[int, int, list[str]]:
    valid, excluded = [], []
    for row in rows:
        if row["status"] == "completed" and row["evidence"] and isinstance(row["success"], bool):
            valid.append(row)
        else:
            excluded.append(row["episode"])
    successes = sum(row["success"] for row in valid)
    return successes, len(valid), excluded


if __name__ == "__main__":
    successes, denominator, excluded = summarize(ROWS)
    print(f"success_rate={successes}/{denominator}={successes / denominator:.1%}")
    print(f"excluded={excluded}")
```

`e4` 特意展示“status completed 也不够”：没有证据，不能进入分母。代码只算 fixture，不代表任何模型成功率。

## 7. 真实 VLA-Arena 操作

复用 Day 6/7 已生成的锁定模型 manifest：

```bash
.venv-day06/bin/python mainline/day08/code/build_pilot_matrix.py \
  --matrix-config mainline/day08/config/pilot_matrix.json \
  --smolvla-manifest learner_outputs/mainline/day06/pilot_a_manifest.json \
  --openvla-manifest learner_outputs/mainline/day07/openvla_manifest.json \
  --output learner_outputs/mainline/day08/pilot_matrix.json
```

输出必须是 `total_episodes=150`、`episodes_per_model=75`、`real_model_runs=0`。每个 ID 同时固定 model/level/task/seed/init，两个模型复用相同外部条件。生成器拒绝非锁定 Day 6/7 manifest、重复 seed、缺 level 或把静态计划标成真实运行。

将来获批 GPU 后，runner 必须逐行执行并写入独立 registry；本日不提供“一口气启动 150 次”的自动命令，避免在 Gate 1、单模型 pilot 尚未真实通过时误烧资源。结果到齐后才运行：

```bash
.venv-day06/bin/python mainline/day08/code/select_diagnostic_model.py \
  --registry learner_outputs/mainline/day08/pilot_registry.csv \
  --output learner_outputs/mainline/day08/model_selection.json
```

[select_diagnostic_model.py](code/select_diagnostic_model.py) 保留排除 ID、按 model/level 报原始计数，并只用 L0 做选择。研究依据是 D1 的“SmolVLA 不自动成为主模型、必须先有足够 L0 能力”和实验协议 E1；课程阈值是额外预注册的可执行定义。

## 8. 独立挑战：Gate 2

允许材料：`shared/fixtures/day08_gate2_results.csv`、本日概念、你自己的短脚本。禁止材料：`shared/answer_keys/gate02.md`、修改 fixture、运行 GPU、用 L1/L2 选择候选。

该 CSV 是 `synthetic_gate_fixture_not_model_result`，候选名和 seed 都不同于 A 矩阵。先独立计算，再创建：

```json
{
  "selected_model": "你的结论或 null",
  "excluded_episode_ids": ["..."],
  "valid_denominators": {"候选": {"0": 0, "1": 0, "2": 0}},
  "next_minimal_experiment": "至少 60 字，固定候选、task、seed 和不扩张边界"
}
```

保存为 `learner_outputs/mainline/day08/gate2_decision.json`。随后可运行汇总器生成 `gate2_fixture_report.json` 交叉检查，但正文不给出选中名称和排除 ID。Gate 结论只有三种：通过；补做分母/规则；若无候选满足 L0，则停止扩张并补最小 pilot，不能强选。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day08.tests.test_day08_tools
.venv-day06/bin/python mainline/day08/code/select_diagnostic_model.py \
  --registry shared/fixtures/day08_gate2_results.csv \
  --output learner_outputs/mainline/day08/gate2_fixture_report.json
.venv-day06/bin/python mainline/day08/code/check_day08.py \
  --matrix-config mainline/day08/config/pilot_matrix.json \
  --smolvla-manifest learner_outputs/mainline/day06/pilot_a_manifest.json \
  --openvla-manifest learner_outputs/mainline/day07/openvla_manifest.json \
  --matrix learner_outputs/mainline/day08/pilot_matrix.json \
  --registry shared/fixtures/day08_gate2_results.csv \
  --selection-report learner_outputs/mainline/day08/gate2_fixture_report.json \
  --gate-answer learner_outputs/mainline/day08/gate2_decision.json
```

口述 10 分：150 行矩阵算式 1；有效分母与排除项 3；L0 成功数/覆盖 2；L1/L2 禁止选模 2；下一步最小实验与边界 2。机器通过且 ≥8 为 Gate 2 通过；5–7 补做；任何强造真实结果、改 fixture 或用 L1/L2 调选择都停止扩张。

## 10. 证据复盘

- 已运行：150 行静态矩阵生成、合成 registry 分母/选择、Gate 语义检查与单元测试。
- 未运行：150 个 VLA episode；真实主诊断模型尚未选择，GPU 成本也未测量。
- 可以主张：矩阵覆盖 D1 的 75 episode/模型硬口径，选择规则在结果前冻结，Gate fixture 可复算。
- 不能主张：合成候选对应 SmolVLA/OpenVLA、外部论文成功率会在本地复现、或 planned 矩阵已满足执行 Gate。

自测题（答案在 `shared/answer_keys/day08.md`）：

1. 为什么完整计划是 150 行，而 D1 硬条件写 75？
2. 哪三项同时成立才进入 success rate 分母？
3. 本课程 L0 选择规则是什么，它是不是官方阈值？
4. 为什么 L1/L2 pilot 可以看，却不能用于选模型？
5. 没有候选满足规则时应该输出什么、下一步做什么？
