# Mainline Day 53：干净重跑 repair 并绑定 checkpoint provenance

今天为 final repair evaluation 建立 provenance chain：checkpoint hash、parent base、recipe hash、split hash、seed、step、完成状态和内容清单必须同时匹配；evaluation protocol 固定后与 checkpoint metadata 一起生成 cleanroom id。本地只验证 synthetic metadata，不加载模型或生成 repair data。

## 1. 真实项目产物

- `clean_repair_packet_a.json`：完整 provenance checks、evaluation protocol、cleanroom id 与 NOT_RUN 状态；
- `repair_records=null` 的诚实边界；
- B 新 checkpoint/protocol 的 packet 与 `challenge_memo.md`。

## 2. 当前卡点

文件名叫 `repair-final` 并不能证明它来自冻结 recipe；checkpoint 可能由错误 base、split、seed 或中途 step 产生。即使 checkpoint 正确，repair 使用不同 trials/initial states 也无法与 baseline 公平比较。

本课逐字段比对 provenance，并要求 policy/optimizer/scheduler/step/config 内容清单完整。protocol 绑定 levels、trials、init mode/offset 和 evaluator seed；packet 通过仍不是实际 bytes/load/eval 证据。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day53/code/minimal_provenance_chain.py
```

应看到 7 项 checks 全 true 与 `provenance_valid=true`。若 checkpoint state 不熟回看 [Day 43](../day43/README.md)；clean-room 规则回看 [Day 52](../day52/README.md)。

## 4. 即时知识

- **checkpoint provenance**：从 base/data/recipe/run 到 checkpoint 的可追溯链。
- **checkpoint hash**：标识实际 checkpoint bytes 或目录 manifest。
- **parent base**：训练起点模型身份，不能被另一个 base 替换。
- **recipe/split hash**：训练方法和数据划分身份。
- **seed/step/status**：具体运行与保存时点，必须满足最终选择规则。
- **required contents**：policy、optimizer、scheduler、step 与 config。
- **protocol freeze**：baseline/repair 的评测条件固定且对称。
- **metadata ≠ bytes**：fixture 能验逻辑，不能证明真实文件存在/可加载。

## 5. 成熟材料处方

- **中文主材料（PyTorch 中文文档，12 分钟）**：[保存和加载通用 checkpoint](https://docs.pytorch.ac.cn/tutorials/beginner/saving_loading_models.html#saving-loading-a-general-checkpoint-for-inference-and-or-resuming-training)。核对 model、optimizer、epoch/step、loss 与加载模式。
- **补充材料（MLflow 官方，8 分钟）**：[Model Registry](https://mlflow.org/docs/latest/ml/model-registry/)。只理解 version、alias、lineage metadata；本日不安装或使用 MLflow。
- **锁定项目定位（10 分钟）**：[trainer 第 169–173 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/scripts/train.py#L169-L173) 从 checkpoint 恢复训练状态；[第 277–285 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/scripts/train.py#L277-L285) 保存 policy/optimizer/scheduler；[evaluator 第 173–178 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L173-L178) 从 policy path 加载并切 eval。

## 6. 最小实验

[minimal_provenance_chain.py](code/minimal_provenance_chain.py) 是完整 21 行代码：

```python
#!/usr/bin/env python3
"""最小例子：逐环验证 repair checkpoint 的来源链。"""

expected = {
    "checkpoint_sha256": "ckpt-123",
    "parent_base_sha256": "base-456",
    "recipe_sha256": "recipe-789",
    "split_sha256": "split-abc",
    "seed": 1,
}
observed = dict(expected)

checks = {
    key: observed.get(key) == value
    for key, value in expected.items()
}
checks["completed"] = True
checks["step_positive"] = 1000 > 0

print(f"checks={checks}")
print(f"provenance_valid={str(all(checks.values())).lower()}")
```

长文件 [build_clean_repair_packet.py](code/build_clean_repair_packet.py) 检查 provenance、protocol 与 NOT_RUN evidence boundary。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day53/code/build_clean_repair_packet.py \
  --checkpoint-metadata shared/fixtures/day53_checkpoint_a.json --config mainline/day53/config/clean_repair_a.json \
  --packet learner_outputs/mainline/day53/clean_repair_packet_a.json
```

A 应报告 valid、seed 1 与 NOT_RUN。未来授权后先对真实 checkpoint 目录生成文件清单/hash，验证 parent/recipe/split/run metadata并实际加载；再将 Day 52 baseline 的 evaluator protocol 做字段级 diff，只允许 policy path/condition 变化。之后才运行 final repair cells，输出逐 episode records。当前不执行。

## 8. 独立挑战

用 B metadata/config 生成新 packet。写 ≥270 字 memo，必须原样包含 `checkpoint provenance`、`checkpoint hash`、`parent base`、`recipe hash`、`split hash`、`seed`、`step`、`optimizer`、`scheduler`、`evaluation protocol`、`same evaluator`、`clean-room`、`repair`、`NOT_RUN`、`cannot claim`。正文不给 B cleanroom id。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day53.tests.test_day53_tools
.venv-day06/bin/python mainline/day53/code/check_day53.py \
  --example-metadata shared/fixtures/day53_checkpoint_a.json --example-config mainline/day53/config/clean_repair_a.json --example-packet learner_outputs/mainline/day53/clean_repair_packet_a.json \
  --challenge-metadata shared/fixtures/day53_checkpoint_b.json --challenge-config mainline/day53/config/clean_repair_b.json --challenge-packet learner_outputs/mainline/day53/clean_repair_packet_b.json \
  --challenge-memo learner_outputs/mainline/day53/challenge_memo.md
```

口述 10 分：provenance fields 2；内容/恢复 2；protocol fairness 2；metadata/bytes 2；NOT_RUN 2。机器通过且 ≥8 进入 Day 54；hash 不匹配、缺状态、换 evaluator、未试加载或冒充 final repair data 均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic checkpoint metadata 与 protocol 的字段验证、cleanroom id。
- 静态源码事实：锁定 trainer save/resume 与 evaluator load 入口。
- 未运行：真实 checkpoint hash/load、SmolVLA、VLA-Arena、GPU 或 repair episodes。
- 可以主张：packet 会拒绝任一 provenance/contents 不匹配。
- 不能主张：真实 repair checkpoint 存在、可加载或 final repair data 已生成。

自测题（答案在 `shared/answer_keys/day53.md`）：

1. checkpoint provenance 至少包含哪些身份？
2. 评测时为什么仍关心 optimizer/scheduler 内容？
3. repair 与 baseline evaluation 允许哪些差异？
4. synthetic metadata 验证是否等于验证真实 checkpoint bytes？
5. packet 通过是否已经产生 final repair data？
