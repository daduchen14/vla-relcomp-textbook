# Mainline Day 21：配对重跑并制作 reproducibility 表

今天不追求更高分，而是回答更基础的问题：同一 episode 的任务、seed、初始状态、模型和协议都不变，再跑一次时，`success` 与四段行为事件是否一致？你会先预注册重跑对象，再保留所有不一致，最后生成带分子/分母的表。免费部分只运行合成 fixture。

## 1. 真实项目产物

- `learner_outputs/mainline/day21/rerun_manifest_a.csv`：A 组 original/repeat 配对计划；
- `repro_details_a.csv`、`repro_report_a.json`：success 与 contact/lift/approach/relation 的一致性；
- B 组换任务后的 manifest、统计和 `challenge_memo.md`。

这里沿用项目文件名 `reproducibility`，但本日同条件短期重跑更接近 **repeatability** 检查；跨机器、跨日期、跨软件栈的 reproducibility 尚未测量。

## 2. 当前卡点

一次成功或失败可能受策略采样、GPU 算子、环境随机性、初始状态选择和运行故障影响。若只重跑“看起来奇怪”的失败，结果选择本身就受观察值影响；若第二次换了 init state，差异又不能归因于重复运行。

因此先按任务边界预注册 selector，再为每个 source episode 生成 original/repeat 两行。两行的 `seed`、`init_state_index`、模型 revision、协议锁和 BDDL 全部相同，只有 execution ID 与 replicate 不同。不同 pair 可以覆盖多个 seed/init strata，但 pair 内不许漂移。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day21/code/minimal_agreement.py
```

应看到 `matches=3`、`pairs=4`、`agreement=0.750`。若 CSV 字典读取或结构化数据不熟，补 [F02](../../foundation_library/f02_csv_json/README.md)；若 registry 主键不熟，回看 [Day 16](../day16/README.md)。

## 4. 即时知识

- **pair**：同一 source episode 的 original/repeat 两次执行。
- **条件一致**：pair 内 task、seed、init state、model、protocol 相同；否则不是本日对照。
- **success match**：两次 success 位相同，只看终态。
- **stage match**：逐段比较 contact、lift、approach、relation，可发现“结果相同但路径不同”。
- **exact match**：success 和四段事件全部一致；不是轨迹逐帧完全相同。
- **一致率**：`匹配 pair 数 / 全部有效 pair 数`。必须同时报告分子和分母；小样本的 1.0 不代表确定稳定。
- **多 seed**：不同 seed 各自形成 pair，再按 seed/task 分层看差异；不能拿 seed A 的 original 对 seed B 的 repeat。

## 5. 成熟材料处方

- **中文主材料（10 分钟）**：[Python `statistics` 官方中文文档：平均值等描述统计](https://docs.python.org/zh-cn/3/library/statistics.html)。只读开头的数据类型与 `mean`；理解统计函数不能替代保存原始计数。本课的二元一致率手算即可，Day 22 再学习区间。
- **术语材料（12 分钟）**：[NIST e-Handbook 2.1.1.4 “Variability”](https://www.itl.nist.gov/div898/handbook/mpc/section1/mpc114.htm)。重点读 repeatability 的短期同条件含义、reproducibility 的长期/跨条件含义及术语警告；本课据此限制主张范围。
- **锁定项目材料（12 分钟）**：[SmolVLA evaluator 第 381–435 行（锁定 commit）](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L381-L435)。逐行确认 RNG、`episode_idx`、`select_init_state_index`、`initial_state` 和 `run_episode` 的连接；这说明仅写 seed 还不够，必须记录实际 init index。

## 6. 最小实验

[minimal_agreement.py](code/minimal_agreement.py) 是完整 10 行代码：

```python
#!/usr/bin/env python3
"""最小例子：一致率必须保留原始分子与分母。"""

pairs = [(1, 1), (0, 0), (1, 0), (0, 0)]
matches = sum(original == repeat for original, repeat in pairs)
rate = matches / len(pairs)

print(f"matches={matches}")
print(f"pairs={len(pairs)}")
print(f"agreement={rate:.3f}")
```

第三个 pair 是 mismatch，所以分子是 3、分母是 4。只写 0.75 会丢掉样本量信息；4 对与 400 对的 0.75 证据强度不同。

## 7. 真实 VLA-Arena 操作

先从 Day 18 的 L0 registry 预注册 pair，再分析本课合成结果：

```bash
.venv-day06/bin/python mainline/day21/code/build_rerun_manifest.py \
  --registry learner_outputs/mainline/day18/l0_registry_a.csv \
  --selection shared/fixtures/day21_rerun_selection_a.json \
  --output learner_outputs/mainline/day21/rerun_manifest_a.csv
.venv-day06/bin/python mainline/day21/code/analyze_reproducibility.py \
  --input shared/fixtures/day21_repro_results_a.csv \
  --details learner_outputs/mainline/day21/repro_details_a.csv \
  --report learner_outputs/mainline/day21/repro_report_a.json
```

应看到 2 个 pair/4 次计划执行，以及 `success_match=3/4 exact_match=2/4`。这些计数是教学 fixture，不是模型结果。

真实运行时，按 manifest 逐行调用 Day 17 evaluator adapter，并记录实际加载的 `initial_state_idx`。若 evaluator 只按内部 `episode_idx` 选状态，要么提供锁定 index 的 adapter，要么把实际 index 回填后检查；不能假定相同 seed 自动等于相同 init。original/repeat 都完成后，把 Day 12 四段事件按 pair join 成输入表。运行顺序可交错，选择规则不得查看结果后修改。

失败处理：pair 内冻结字段漂移则整对无效；单次异常单列，不默认为失败；missing repeat 保留缺失，不从分母静默删除；不同 seed 不强行配对；确定性设置也不能作为“必然逐帧相同”的保证。

## 8. 独立挑战

改用 Day 18 B registry、`day21_rerun_selection_b.json` 和 `day21_repro_results_b.csv`。不给具体输出：生成 B manifest、details、report，并写 ≥170 字 memo。memo 必须原样出现 `repeat`、`seed`、`init_state`、`success`、`stage`、`mismatch`、`reproducibility`。

说明一个“success 相同但 stage 不同”和一个“success 不同”的证据含义；指出为何 B 仍只是 synthetic fixture。不得复制 A 的 selector、统计或参考答案段落。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day21.tests.test_day21_tools
.venv-day06/bin/python mainline/day21/code/check_day21.py \
  --example-registry learner_outputs/mainline/day18/l0_registry_a.csv \
  --example-selection shared/fixtures/day21_rerun_selection_a.json \
  --example-manifest learner_outputs/mainline/day21/rerun_manifest_a.csv \
  --example-raw shared/fixtures/day21_repro_results_a.csv \
  --example-details learner_outputs/mainline/day21/repro_details_a.csv \
  --example-report learner_outputs/mainline/day21/repro_report_a.json \
  --challenge-registry learner_outputs/mainline/day18/l0_registry_b.csv \
  --challenge-selection shared/fixtures/day21_rerun_selection_b.json \
  --challenge-manifest learner_outputs/mainline/day21/rerun_manifest_b.csv \
  --challenge-raw shared/fixtures/day21_repro_results_b.csv \
  --challenge-details learner_outputs/mainline/day21/repro_details_b.csv \
  --challenge-report learner_outputs/mainline/day21/repro_report_b.json \
  --challenge-memo learner_outputs/mainline/day21/challenge_memo.md
```

口述 10 分：配对与冻结字段 2；预注册选择 2；success/stage/exact 三层指标 2；分子分母与多 seed 2；repeatability/reproducibility 和 synthetic/real 边界 2。机器通过且 ≥8 进入 Day 22；按结果挑重跑、跨 seed 配对、静默删 mismatch 或把 fixture 当模型稳定性证据均不通过。

## 10. 证据复盘

- 已运行：A/B 预注册 manifest、合成配对一致性统计、漂移/非法输入测试。
- 未运行：真实 SmolVLA/OpenVLA 重跑、GPU、跨机器/日期复现。
- 可以主张：脚本能冻结 pair 条件并精确重建 success/stage 一致性表。
- 不能主张：任何真实模型稳定率、跨环境 reproducibility 或 mismatch 的内部原因。

自测题（答案在 `shared/answer_keys/day21.md`）：

1. 为什么 pair 内必须固定 seed 和 init state？
2. success match 与 exact match 有什么区别？
3. 为什么选择重跑对象必须在看结果前预注册？
4. 4/4 一致能否证明模型稳定？
5. 本课为什么把同条件重跑称作更接近 repeatability？
