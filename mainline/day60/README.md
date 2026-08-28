# Mainline Day 60：冻结结果与允许的论文主张（Gate 7）

今天把每条论文主张锁到表格、原始 episode、代码/数据版本和“不能推出的更强结论”。机器用冻结 seed 随机抽三条做 Gate 7 演练。当前输入全是 synthetic，因此只允许验证追溯机制，结论必须是“停止扩张”，学习者 Gate 7 仍未通过。

## 1. 真实项目产物

- `results_lock_a.json`：完整 claim registry、负结果计数、source hashes 与三条随机抽查；
- 每条 `allowed_claim → table → raw episode → version → forbidden_stronger_claim` 映射；
- B 新输入的结果锁与 `challenge_memo.md`。

## 2. 当前卡点

一张汇总表可以支持“这个冻结样本中观察到 X”，却未必支持“方法普遍改善 X”或因果解释。只保存最终数字还会断开原始 episode 和版本，事后很难发现换表、删失败或代码漂移。

本课把主张本身当作需版本化的数据。负结果不能静默删除；随机抽查用于防止作者只展示最容易回答的主张，但固定 seed 仅保证可重建，不等于统计随机抽样。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day60/code/minimal_claim_evidence.py
```

应看到两条 `evidence_complete=True` 和各自 `cannot_claim`。若字典/列表不熟补 [F03](../../foundation_library/f03_modules_testing/README.md)；统计边界回看 [Day 57](../day57/README.md)，案例与资源证据回看 [Day 58](../day58/README.md)、[Day 59](../day59/README.md)。

## 4. 即时知识

- **claim**：句子级、可核查的有限主张，不是宽泛愿景。
- **evidence link**：主张到 table、raw episode 与 version 的可追溯映射。
- **allowed claim**：现有设计与证据直接支持的表述。
- **stronger claim**：加入普遍性、因果性、真实系统结论等额外承诺的表述。
- **negative result**：冻结分析没有显示预期改善；仍需保留并限定解释。
- **results lock**：在写作前冻结主张、证据、版本、边界和负结果的机器可读清单。
- **Gate 7**：随机抽三条主张，现场指出证据链和不能说什么。

## 5. 成熟材料处方

- **中文主材料（开放科学促进联合体，12 分钟）**：[中国早期职业研究人员开放科学技术指南（PDF）](https://open4science.cn/static/ECR_OpenScience_Guide_CN.pdf)。只读“预注册”小节，理解预先冻结设计、分析和公开链接如何支持复核；不要把预注册本身当成结果正确的保证。
- **补充材料（OSF 官方，8 分钟）**：[Registrations & Preregistrations 指南](https://help.osf.io/article/330-welcome-to-registrations)。重点看 precise hypotheses、decision criteria、exclusion rules、outcomes 与 deviations，逐项对应 results lock 字段。
- **锁定项目定位（10 分钟）**：[evaluator 配置第 79–139 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L79-L139) 定义 suite、level、trials、initial state、seed、视频和 replacement；[action/step/success 第 280–334 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L280-L334) 是 raw episode 主张必须追溯的真实执行终点。

## 6. 最小实验

[minimal_claim_evidence.py](code/minimal_claim_evidence.py) 是完整 24 行代码：

```python
#!/usr/bin/env python3
"""最小例子：主张必须同时指向证据和越界边界。"""

claims = [
    {
        "claim": "合成样本中阶段二通过率较低",
        "table": "T-stage",
        "episodes": ["syn-001", "syn-002"],
        "version": "locked-analysis-v1",
        "forbidden": "真实系统普遍在阶段二失败",
    },
    {
        "claim": "合成配对样本未显示改善",
        "table": "T-pair",
        "episodes": ["syn-011", "syn-012"],
        "version": "locked-analysis-v1",
        "forbidden": "修复方法确定无效",
    },
]

for item in claims:
    complete = all(item[key] for key in ("table", "episodes", "version", "forbidden"))
    print(f"claim={item['claim']} evidence_complete={complete}")
    print(f"cannot_claim={item['forbidden']}")
```

长文件 [build_results_lock.py](code/build_results_lock.py) 校验 hashes/锁定 commit，用 seed 6007 从排序后的 claim IDs 抽三条，并在 formal evidence 缺失时阻止通过。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day60/code/build_results_lock.py \
  --input shared/fixtures/day60_claims_a.json \
  --config mainline/day60/config/results_lock_a.json \
  --report learner_outputs/mainline/day60/results_lock_a.json
```

报告应有 4 条 claim、抽查 3 条、至少 1 条 negative result，结论为“停止扩张 / FORMAL_EVIDENCE_MISSING”。未来正式替换时，table hash 必须对应 Day 61/62 发布数据，raw episode hash 必须来自锁定 evaluator 输出，version 同时锁 upstream 与分析脚本；缺任何一项只能补做或停止。

## 8. 独立挑战

换用 B registry/config 生成新结果锁；不要查看答案，也不要照抄 A 的 IDs。写 ≥280 字 memo，必须原样包含 `Gate 7`、`random sample`、`claim`、`table`、`raw episode`、`version`、`allowed claim`、`stronger claim`、`negative result`、`formal evidence`、`synthetic`、`停止扩张`、`learner status`、`results lock`、`cannot claim`。对抽中的三条逐一说明映射。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day60.tests.test_day60_tools
.venv-day06/bin/python mainline/day60/code/check_day60.py \
  --example-input shared/fixtures/day60_claims_a.json --example-config mainline/day60/config/results_lock_a.json --example-report learner_outputs/mainline/day60/results_lock_a.json \
  --challenge-input shared/fixtures/day60_claims_b.json --challenge-config mainline/day60/config/results_lock_b.json --challenge-report learner_outputs/mainline/day60/results_lock_b.json \
  --challenge-memo learner_outputs/mainline/day60/challenge_memo.md
```

口述 10 分：三条 claim 2；table/raw episode 2；version 2；stronger claim 2；负结果和证据边界 2。机器通过且口述 ≥8 才完成 Day 60 教学；漏映射、手挑主张、删负结果、把 synthetic 当 formal 或记录 Gate passed 均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic claim registry 的 hash、随机三条追溯与边界验收。
- 静态源码事实：锁定 evaluator 的配置、action→step 与 success 判定位置。
- 未运行：正式 table、raw episode、GPU、VLA-Arena、学习者现场口述。
- 可以主张：结果锁能拒绝缺版本/原始 episode/越界边界的主张。
- 不能主张：任何模型效果、因果机制、真实成本，或 Gate 7 已通过。

自测题（答案在 `shared/answer_keys/day60.md`）：

1. 一条可审计 claim 最少要连接哪些对象？
2. 为什么 Gate 7 要固定随机 seed 抽三条？
3. 为什么负结果不能从 results lock 删除？
4. 当前追溯链完整为何仍必须停止扩张？
5. Day 60 教材完成是否等于学习者 Gate 7 通过？
