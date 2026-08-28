# Mainline Day 69：完成 10 分钟答辩故事、口述稿和 Q&A

今天从同一 talk spec 生成 8 页 assertion-title 幻灯片、恰好 600 秒的逐页口述稿和 10 题追问库。每页只有一个 message、一个 visual evidence 和一句 boundary；当前全部是 synthetic 教学答辩包。

## 1. 真实项目产物

- `slides.md`：8 页断言式标题、视觉、证据、边界和时间；
- `oral_script.md`：000–600 秒逐页口述；
- `qa.md`：short answer、evidence pointer 与 cannot claim；
- B 新故事线的答辩包与 memo。

## 2. 当前卡点

把报告目录搬进 PPT 会超时且没有主线；标题只写“方法/结果”让评委猜本页结论；Q&A 若临场发挥，最容易把 synthetic、oracle 或不显著结果说过界。

本课把 timing、message、evidence 和 boundary 同时版本化，机器拒绝非 600 秒或少于 10 题的包。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day69/code/minimal_talk_timing.py
```

应输出逐页时段和 `total=600s`。若列表/累计不熟补 [F03](../../foundation_library/f03_modules_testing/README.md)；表图与报告回看 [Day 62](../day62/README.md) 至 [Day 66](../day66/README.md)。

## 4. 即时知识

- **ten-minute story**：问题→方法→证据→边界→贡献的限时叙事。
- **assertion title**：可独立表达本页结论的完整句标题。
- **one message**：一页只要求观众带走一个命题。
- **visual evidence**：直接支持标题的图、链或表，而不是装饰。
- **timing budget**：逐页秒数总和与真实预演记录。
- **oral script**：补充视觉，不逐字朗读屏幕。
- **Q&A contract**：short answer→evidence pointer→boundary sentence。

## 5. 成熟材料处方

- **中文主材料（陕西师范大学资源，12 分钟）**：[《无痛读研：研究生学术能力提升与心理调适》PDF](https://faculty.snnu.edu.cn/_resources/group1/M00/00/19/2_RDHmof5S2AK7moANLjhd_ZN10671.pdf)。只读第 6 章的 6.1.2“五步完成法：MODEL”和 6.4.1“典型学术报告页面的基础要素”。
- **补充材料（MIT Communication Lab，10 分钟）**：[Slideshow](https://mitcommlab.mit.edu/broad/commkit/slideshow/)。重点看 single point、assertion title、先教观众读图和准备 talking part。
- **锁定项目定位（8 分钟）**：[evaluator Args 第 79–139 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L79-L139) 支持追问中的 suite/seed/state；[执行链第 280–334 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L280-L334) 支持核心链路页。

## 6. 最小实验

[minimal_talk_timing.py](code/minimal_talk_timing.py) 是完整 20 行代码：

```python
#!/usr/bin/env python3
"""最小例子：逐页预算必须恰好组成 10 分钟。"""

slides = [
    ("问题为什么重要", 60),
    ("调用链如何定义证据", 90),
    ("诊断与修复如何区分", 120),
    ("结果边界是什么", 150),
    ("限制与下一步", 120),
    ("一句话结论", 60),
]

elapsed = 0
for title, seconds in slides:
    start = elapsed
    elapsed += seconds
    print(f"{start:03d}–{elapsed:03d}s | {title}")

assert elapsed == 600
print("total=600s")
```

长文件 [build_defense_package.py](code/build_defense_package.py) 同源生成 slides/oral/Q&A/manifest。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day69/code/build_defense_package.py \
  --input shared/fixtures/day69_talk_a.json --config mainline/day69/config/talk_a.json \
  --output-dir learner_outputs/mainline/day69/defense_a
```

应报告 `slides=8 seconds=600 qa=10 formal=false`。未来正式答辩只替换 evidence pointer 指向的表图/episode，保留 timing 与 boundary；没有真实视频时不能用 synthetic 图或口述冒充。

## 8. 独立挑战

换 B talk spec/config 生成新包，并按新顺序口述一次。写 ≥280 字 memo，原样包含 `ten-minute story`、`assertion title`、`one message`、`visual evidence`、`timing budget`、`oral script`、`Q&A`、`short answer`、`evidence pointer`、`boundary sentence`、`synthetic`、`cannot claim`。正文不给 B 的讲法。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day69.tests.test_day69_tools
.venv-day06/bin/python mainline/day69/code/check_day69.py \
  --example-input shared/fixtures/day69_talk_a.json --example-config mainline/day69/config/talk_a.json --example-output-dir learner_outputs/mainline/day69/defense_a \
  --challenge-input shared/fixtures/day69_talk_b.json --challenge-config mainline/day69/config/talk_b.json --challenge-output-dir learner_outputs/mainline/day69/defense_b \
  --challenge-memo learner_outputs/mainline/day69/challenge_memo.md
```

口述 10 分：故事线 2；标题/一页一事 2；视觉/证据 2；600 秒 2；Q&A/边界 2。机器通过且真实口述 9–11 分钟、评分 ≥8 才完成 Day 69；超时、读稿、无 evidence、即兴越界或 synthetic 当实证均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic talk spec 到三类答辩产物的逐字节重建。
- 静态源码事实：锁定 evaluator 的配置与核心执行链。
- 未运行：真实口述计时、观众问答、VLA-Arena/GPU 与正式结果视频。
- 可以主张：答辩包包含 600 秒预算、8 页边界和 10 题 evidence-linked Q&A。
- 不能主张：学习者已通过口述、实证成立或正式答辩完成。

自测题（答案在 `shared/answer_keys/day69.md`）：

1. 10 分钟故事的基本顺序是什么？
2. assertion title 有何作用？
3. 为什么一页只讲一个 message？
4. Q&A 的三段合同是什么？
5. 机器 600 秒预算等于真实口述合格吗？
