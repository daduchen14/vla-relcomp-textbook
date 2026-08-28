# Mainline Day 46：冻结 seed 2–3 重复与方差口径

今天把 Day 45 的 seed 1 扩展为 seed 2、3 的公平重复计划。机器要求所有 run 使用同一 split、同一 frozen recipe 和同一 locked commit，只允许 seed、run id、output dir 改变；同时冻结总 GPU-hours cap 和“每 seed+均值+样本标准差”报告规则。没有 GPU 授权，因此 checkpoint 2–3 仍是 NOT_RUN 合同。

## 1. 真实项目产物

- `repeat_manifest_a.json`：seed 2–3 的身份、不变量、预算、命令与 checkpoint contracts；
- `variance_policy`：必须纳入 seed 1–3，禁止 best-seed selection；
- B 新 recipe/split 组合的 manifest 与 `challenge_memo.md`。

## 2. 当前卡点

单 seed 可能碰巧好或坏。若重复时顺手调 learning rate、换 split，差异就无法归因于 seed；若只汇报最好一次，则失去稳定性信息。预算内重复还必须先计算总上限，不能跑到一半才决定保留哪些 seed。

本课预注册 `[1,2,3]`，其中 Day 46 只计划 2、3；只允许三个身份字段变化。variance metrics 在真实运行前必须为 null，checkpoint hash 也必须为空。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day46/code/minimal_seed_variance.py
```

应看到全部三 seed、mean 0.4200、sample stdev 0.0400 和 `best_seed_selection=false`。若均值/标准差不熟补 [F02](../../foundation_library/f02_csv_json/README.md) 的表格汇总；launch 边界回看 [Day 45](../day45/README.md)。

## 4. 即时知识

- **repeat**：在不变量完全相同的情况下只改变随机 seed。
- **allowed differences**：预先列出可变字段；未列出的变化都算 protocol deviation。
- **per-seed**：每次结果逐项保留，不能只留聚合值。
- **mean**：全部预注册 seed 的算术平均。
- **sample standard deviation**：用 `n−1` 分母估计 seed 间离散度。
- **cherry-picking**：根据结果选择要报告的 seed，会造成乐观偏差。
- **resource cap**：所有重复预算之和的硬上限。
- **checkpoint contract**：未来产物规范；NOT_RUN 状态不等于 checkpoint。

## 5. 成熟材料处方

- **中文主材料（Python 官方，10 分钟）**：[statistics：均值与样本标准差](https://docs.python.org/zh-cn/3/library/statistics.html#statistics.stdev)。只读 `mean` 与 `stdev` 的定义，并区分总体标准差 `pstdev`。
- **补充材料（NumPy 官方，8 分钟）**：[numpy.std](https://numpy.org/doc/stable/reference/generated/numpy.std.html)。只看 `ddof` 如何改变分母；本课用样本标准差，不能默认混用。
- **锁定项目定位（8 分钟）**：[SmolVLA train 第 134–140 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/scripts/train.py#L134-L140) 设置真实 seed 与 CUDA 开关；[第 277–285 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/scripts/train.py#L277-L285) 保存每个 run 的 checkpoint。不同 seed 必须使用隔离 output dir，避免覆盖。

## 6. 最小实验

[minimal_seed_variance.py](code/minimal_seed_variance.py) 是完整 21 行代码：

```python
#!/usr/bin/env python3
"""最小例子：保留全部预注册 seed，并报告均值与样本标准差。"""

from statistics import mean, stdev

results = [
    {"seed": 1, "score": 0.42},
    {"seed": 2, "score": 0.38},
    {"seed": 3, "score": 0.46},
]

registered = {1, 2, 3}
observed = {row["seed"] for row in results}
if observed != registered:
    raise SystemExit("缺少或多出 seed，禁止选择性报告")

scores = [row["score"] for row in results]
print(f"all_seeds={sorted(observed)}")
print(f"mean={mean(scores):.4f}")
print(f"sample_stdev={stdev(scores):.4f}")
print("best_seed_selection=false")
```

长文件 [prepare_repeat_launches.py](code/prepare_repeat_launches.py) 重点阅读 Day 45 身份继承、allowed differences、预算求和和空结果策略。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day46/code/prepare_repeat_launches.py \
  --split shared/fixtures/day45_split_a.json --seed1-plan mainline/day45/config/seed1_plan_a.json \
  --repeat-plan mainline/day46/config/repeat_plan_a.json \
  --stability-input shared/fixtures/day44_stability_a.json --candidate-recipe mainline/day44/config/candidate_recipe_a.json \
  --manifest learner_outputs/mainline/day46/repeat_manifest_a.json
```

应报告 repeats `[2,3]`、same recipe/split 与 NOT_RUN。获授权后才逐个执行 manifest 中的命令；每次先比对 recipe/split/commit hash，独立记录资源与 checkpoint hash。任何 seed 失败都保留失败状态，不补跑“更好 seed”替代；是否按相同规则重试必须统一记录。当前不执行 GPU。

## 8. 独立挑战

用 B repeat plan、Day 45 B split/plan 和 Day 44 B recipe 生成新 manifest。写 ≥260 字 memo，必须原样包含 `seed 2`、`seed 3`、`repeat`、`same recipe`、`same split`、`allowed differences`、`variance`、`mean`、`sample standard deviation`、`per-seed`、`cherry-picking`、`resource cap`、`checkpoint 2`、`checkpoint 3`、`NOT_RUN`。正文不给 B hash。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day46.tests.test_day46_tools
.venv-day06/bin/python mainline/day46/code/check_day46.py \
  --example-split shared/fixtures/day45_split_a.json --example-base mainline/day45/config/seed1_plan_a.json --example-repeat mainline/day46/config/repeat_plan_a.json --example-stability shared/fixtures/day44_stability_a.json --example-candidate mainline/day44/config/candidate_recipe_a.json --example-manifest learner_outputs/mainline/day46/repeat_manifest_a.json \
  --challenge-split shared/fixtures/day45_split_b.json --challenge-base mainline/day45/config/seed1_plan_b.json --challenge-repeat mainline/day46/config/repeat_plan_b.json --challenge-stability shared/fixtures/day44_stability_b.json --challenge-candidate mainline/day44/config/candidate_recipe_b.json --challenge-manifest learner_outputs/mainline/day46/repeat_manifest_b.json \
  --challenge-memo learner_outputs/mainline/day46/challenge_memo.md
```

口述 10 分：重复不变量 2；allowed differences 2；方差口径 2；预算 2；NOT_RUN 边界 2。机器通过且 ≥8 进入 Day 47；改 recipe/split、挑最好 seed、遗漏 per-seed、预算超限或伪造 checkpoint 均不通过。

## 10. 证据复盘

- 已运行：A/B 免费 manifest 构造、身份不变量、预算和空结果检查。
- 静态源码事实：锁定 trainer 的 seed 设置与 checkpoint 保存入口。
- 未运行：SmolVLA、GPU、seed 1–3 formal runs、checkpoint 1–3 与真实 variance。
- 可以主张：重复计划可保证除 seed/run/output 外的比较条件一致，并禁止挑选 seed。
- 不能主张：多 seed 稳定、均值/标准差已取得或 checkpoint 2–3 存在。

自测题（答案在 `shared/answer_keys/day46.md`）：

1. seed 重复允许改变哪些字段？
2. 为什么报告 sample standard deviation 并保留 per-seed？
3. cherry-picking seed 会造成什么偏差？
4. 总 resource cap 怎样计算？
5. 本日是否已经产生 checkpoint 2–3 或 variance 结果？
