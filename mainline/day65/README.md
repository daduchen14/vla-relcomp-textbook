# Mainline Day 65：写结果、诊断与修复结论

今天按冻结证据顺序生成 results draft：先分母，再主要效应/区间，随后诊断、repair、L0 retention、oracle、资源与负结果。每段都链接 evidence ref 并写出不能推出的更强结论。输入仍为 synthetic。

## 1. 真实项目产物

- `results_draft.md`：八段证据顺序与有限语言主张；
- `manifest.json`：source/draft hashes、负结果与边界完整性；
- B 新结果 registry 的独立 draft 与 memo。

## 2. 当前卡点

直接用“提高、解决、证明”串联结果，会把点估计写成确定效果，把诊断关联写成因果，把 oracle 写成可部署修复。若先说最好数字再补分母，缺失 pairs 和失败 runs 也容易消失。

本课让 claim registry 决定段落顺序；每条 allowed sentence 必须绑定 evidence ref 与 forbidden stronger claim，负结果不能删除。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day65/code/minimal_limited_language.py
```

应看到点估计、跨零区间和“不能推出真实改善”。若区间解释不熟回看 [Day 57](../day57/README.md)；claim 边界回看 [Day 60](../day60/README.md)。

## 4. 即时知识

- **evidence order**：分母→主要估计→诊断→修复/保持→oracle→资源→负结果。
- **limited language**：明确数据范围、点估计、不确定性和不能推出什么。
- **descriptive association**：观察到共变，不等于因果机制。
- **minimum improvement**：预先冻结的实质改善标准，不由 p 值代替。
- **negative result**：未达标准或不确定的结果，仍进入正文。
- **equivalence boundary**：未显著不等于等价；等价需要独立设计与界值。

## 5. 成熟材料处方

- **中文主材料（开放科学促进联合体，10 分钟）**：[中国早期职业研究人员开放科学技术指南](https://open4science.cn/static/ECR_OpenScience_Guide_CN.pdf)。只读结果公开与预注册偏离部分，检查是否完整报告不利结果。
- **补充材料（美国统计协会，10 分钟）**：[ASA Statement on Statistical Significance and P-Values](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)。重点看 p 值不等于效果大小、重要性或“假设为真概率”。
- **锁定项目定位（8 分钟）**：[success 判定第 310–334 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L310-L334) 定义单 episode outcome；[汇总第 697–756 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L697-L756) 只给 suite aggregate，正式结果必须回链逐 episode release。

## 6. 最小实验

[minimal_limited_language.py](code/minimal_limited_language.py) 是完整 19 行代码：

```python
#!/usr/bin/env python3
"""最小例子：把点估计、区间和解释边界放在同一句。"""

result = {
    "scope": "synthetic paired sample",
    "estimate": 0.15,
    "interval": (-0.08, 0.36),
    "formal": False,
}

sentence = (
    f"在 {result['scope']} 中，paired delta 为 "
    f"{result['estimate']:+.2f}，95% 区间为 "
    f"[{result['interval'][0]:+.2f}, {result['interval'][1]:+.2f}]。"
)
boundary = "该教学估计不能推出真实模型改善或因果效果。"

print(sentence)
print(boundary)
```

长文件 [build_results_draft.py](code/build_results_draft.py) 校验八段顺序、证据链接、禁用越界措辞和负结果保留。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day65/code/build_results_draft.py \
  --input shared/fixtures/day65_results_a.json --config mainline/day65/config/results_a.json \
  --output-dir learner_outputs/mainline/day65/results_a
```

应报告 `claims=8 negative_preserved=true formal=false`。正式写作只接受 Day 60 results lock 与 Day 61–63 的 hash-matched 表图；若 Gate 7 停止扩张，就保留有限/负结论，不新增分析追逐正结果。

## 8. 独立挑战

用 B registry/config 生成新稿。写 ≥280 字 memo，原样包含 `evidence order`、`denominator`、`effect estimate`、`confidence interval`、`diagnosis`、`repair`、`retention`、`oracle`、`resource`、`negative result`、`limited language`、`synthetic`、`cannot claim`。不复制 A 结果句。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day65.tests.test_day65_tools
.venv-day06/bin/python mainline/day65/code/check_day65.py \
  --example-input shared/fixtures/day65_results_a.json --example-config mainline/day65/config/results_a.json --example-output-dir learner_outputs/mainline/day65/results_a \
  --challenge-input shared/fixtures/day65_results_b.json --challenge-config mainline/day65/config/results_b.json --challenge-output-dir learner_outputs/mainline/day65/results_b \
  --challenge-memo learner_outputs/mainline/day65/challenge_memo.md
```

口述 10 分：分母/顺序 2；估计/区间 2；诊断边界 2；repair/oracle 2；负结果/资源 2。机器通过且 ≥8 才完成 Day 65；删负结果、p 值等于效果、关联当因果、oracle 当部署或 synthetic 冒充正式均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic claim registry 到 results/manifest 的逐字节重建。
- 静态源码事实：锁定 evaluator 的 outcome 与 suite aggregate 位置。
- 未运行：formal episode、VLA-Arena、GPU 和真实统计。
- 可以主张：draft 强制证据顺序、引用、负结果和 stronger-claim 边界。
- 不能主张：repair 改善、机制成立、真实成本或统计等价。

自测题（答案在 `shared/answer_keys/day65.md`）：

1. 为什么先报告 denominator？
2. estimate、interval 与 test 有何区别？
3. diagnosis 能否直接写成因果？
4. oracle 应如何表述？
5. not significant 是否等于 no effect？
