# Mainline Day 45：准备正式训练 seed 1，并隔离测试集

今天不启动 GPU，而是把正式 seed 1 所需的身份、数据边界、资源上限与 checkpoint 内容一次冻结。免费脚本生成 launch packet 和 checkpoint contract；由于没有 GPU 授权，checkpoint 1 保持 `NOT_RUN_NO_GPU_AUTHORIZATION`，绝不拿空目录或 toy 权重冒充。

## 1. 真实项目产物

- `seed1_launch_packet_a.json`：commit、seed、split/recipe hash、训练读取范围、预算和计划命令；
- `checkpoint1_contract_a.json`：预期路径、必含状态与诚实的 NOT_RUN 状态；
- B 新 split/plan 的同类证据与 `challenge_memo.md`。

## 2. 当前卡点

“准备训练”若不绑定 split 和 recipe，运行时很容易换数据或超参数；若训练过程读取 held-out test 做选择，即使没有把标签直接喂给 optimizer，也已造成泄漏。资源方面，预算是上限，measurement 是运行事实，二者不能混写。

本课要求 train/validation/test episode id 两两互斥，training reads 只含 train+validation，test access log 为空。launch packet 固定 seed=1、锁定 commit 和两个 SHA-256；未获 GPU 授权时只生成合同，不执行 planned command。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day45/code/minimal_split_guard.py
```

应看到三个 overlap 都为空且 `test_isolated=true`。若 JSON/字典不熟补 [F02](../../foundation_library/f02_csv_json/README.md)；recipe 身份回看 [Day 44](../day44/README.md)。

## 4. 即时知识

- **formal run**：按预注册 recipe/split 执行、可进入最终比较的训练运行。
- **seed 1**：本项目正式多 seed 序列的第一个标识，不代表只需一个 seed。
- **held-out test**：训练和模型选择期间不可访问的最终评估集合。
- **test isolation**：test id 不出现在训练/验证读取及调参访问日志中。
- **resource budget**：运行前允许的 GPU 数、墙钟时间、GPU-hours 和存储上限。
- **resource measurement**：运行后实际 device、时间、峰值显存、磁盘和退出状态。
- **launch packet**：把 command、commit、seed、split/recipe hash 与预算绑定的执行清单。
- **checkpoint contract**：规定 checkpoint 必须包含什么；它本身不是模型产物。

## 5. 成熟材料处方

- **中文主材料（Google ML，10 分钟）**：[数据集的划分](https://developers.google.com/machine-learning/crash-course/overfitting/dividing-datasets?hl=zh-cn)。只读训练/验证/测试各自用途，写一句为什么 test 不能参与选择。
- **中文补充（PyTorch 中文文档，8 分钟）**：[Profiler 配方](https://docs.pytorch.ac.cn/tutorials/recipes/recipes/profiler_recipe.html)。只理解真实测量来自运行活动；本日不把计划 budget 写成 profiler 结果。
- **锁定项目定位（10 分钟）**：[VLA-Arena launcher 第 26–53 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/cli/train.py#L26-L53) 解析模型配置与 trainer；[SmolVLA 默认配置第 1–18 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/configs/train/smolvla.yaml#L1-L18) 含真实 dataset/model/device/lr/steps/output/save 字段，但其中路径仍是占位值，不能直接启动。

## 6. 最小实验

[minimal_split_guard.py](code/minimal_split_guard.py) 是完整 22 行代码：

```python
#!/usr/bin/env python3
"""最小例子：训练启动前证明 train/val/test 三者互斥。"""

splits = {
    "train": {"ep01", "ep02", "ep03"},
    "validation": {"ep04"},
    "test": {"ep05", "ep06"},
}

pairs = (("train", "validation"),
         ("train", "test"),
         ("validation", "test"))
overlaps = {
    f"{left}_{right}": sorted(splits[left] & splits[right])
    for left, right in pairs
}
training_reads = splits["train"] | splits["validation"]
test_isolated = not overlaps["train_test"] and not overlaps["validation_test"]

print(f"overlaps={overlaps}")
print(f"training_reads={sorted(training_reads)}")
print(f"test_isolated={str(test_isolated).lower()}")
```

长文件 [prepare_seed1_launch.py](code/prepare_seed1_launch.py) 重建 Day 44 recipe hash，检查 split，再生成 launch/checkpoint 两份不同性质的文件。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day45/code/prepare_seed1_launch.py \
  --split shared/fixtures/day45_split_a.json --plan mainline/day45/config/seed1_plan_a.json \
  --stability-input shared/fixtures/day44_stability_a.json --candidate-recipe mainline/day44/config/candidate_recipe_a.json \
  --packet learner_outputs/mainline/day45/seed1_launch_packet_a.json \
  --checkpoint-contract learner_outputs/mainline/day45/checkpoint1_contract_a.json
```

应报告 seed 1、test isolated 和两项 `NOT_RUN_NO_GPU_AUTHORIZATION`。未来获授权后，先把 fixture ID 换成真实 L0 manifest，解析默认 YAML 的占位路径，生成并人工核对最终配置；随后执行 packet 中的 `vla-arena train` 命令，实时写资源 measurement。只有退出成功且 checkpoint 内容齐全、可加载、hash 可计算，才能把合同升级为 checkpoint 1 证据。当前不得运行。

## 8. 独立挑战

用 B split/plan 和 Day 44 B recipe 生成新 packet/contract。写 ≥260 字 memo，必须原样包含 `seed 1`、`formal run`、`train split`、`validation split`、`held-out test`、`test isolation`、`resource budget`、`resource measurement`、`launch packet`、`checkpoint contract`、`NOT_RUN`、`authorization`、`recipe hash`、`split hash`、`GPU`。正文不给 B hash。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day45.tests.test_day45_tools
.venv-day06/bin/python mainline/day45/code/check_day45.py \
  --example-split shared/fixtures/day45_split_a.json --example-plan mainline/day45/config/seed1_plan_a.json --example-stability shared/fixtures/day44_stability_a.json --example-candidate mainline/day44/config/candidate_recipe_a.json --example-packet learner_outputs/mainline/day45/seed1_launch_packet_a.json --example-contract learner_outputs/mainline/day45/checkpoint1_contract_a.json \
  --challenge-split shared/fixtures/day45_split_b.json --challenge-plan mainline/day45/config/seed1_plan_b.json --challenge-stability shared/fixtures/day44_stability_b.json --challenge-candidate mainline/day44/config/candidate_recipe_b.json --challenge-packet learner_outputs/mainline/day45/seed1_launch_packet_b.json --challenge-contract learner_outputs/mainline/day45/checkpoint1_contract_b.json \
  --challenge-memo learner_outputs/mainline/day45/challenge_memo.md
```

口述 10 分：formal/seed 2；split/test isolation 2；身份 hash 2；资源记录 2；checkpoint/授权边界 2。机器通过且 ≥8 进入 Day 46；test 泄漏、预算冒充测量、未绑定 recipe/split、空目录冒充 checkpoint 或执行 GPU 命令均不通过。

## 10. 证据复盘

- 已运行：A/B 免费 packet 构造、split 互斥、test access、recipe/split hash 与合同重建。
- 静态源码事实：锁定 launcher 的 config/trainer 解析和默认 SmolVLA 训练字段。
- 未运行：真实 L0 数据、SmolVLA、GPU、formal seed 1、资源测量和 checkpoint 写入。
- 可以主张：seed-1 执行前身份、预算、test isolation 和 checkpoint 验收条件已明确。
- 不能主张：formal run 已启动、checkpoint 1 存在、GPU-hours 已消耗或模型有结果。

自测题（答案在 `shared/answer_keys/day45.md`）：

1. 为什么 formal training 阶段仍不能读取 held-out test？
2. resource budget 与 resource measurement 有何区别？
3. launch packet 必须绑定哪些身份？
4. checkpoint contract 为什么不是 checkpoint 证据？
5. 本日能否声称 seed 1 正式训练完成？
