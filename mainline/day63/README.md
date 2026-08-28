# Mainline Day 63：生成阶段漏斗、pair 和干预图

今天把阶段漏斗、配对转移和干预对照做成一个三面板 SVG。比例轴固定 0–1，点估计带 95% Wilson interval，分母直接写在图上；颜色不是唯一编码。输入仍是 synthetic，图只验证诚实可视化流程。

## 1. 真实项目产物

- `paper_figures.svg`：funnel、paired transitions、intervention 三面板；
- `caption.md`：观察单位、区间、轴和证据边界；
- `manifest.json`：输入/config/产物 hashes 与可访问性契约；
- B 新 figure spec 的 SVG 和说明 memo。

## 2. 当前卡点

截断比例轴会把小差异画得巨大；没有 error bar 会隐藏不确定性；只靠颜色区分条件会妨碍色觉差异读者。oracle 若与 repair 同列又不标诊断属性，还会制造不可部署方法似乎可比较的错觉。

本课用固定 0–1 坐标、直接标签、数值、分母和色盲友好 palette。SVG 由数据生成，不手拖图形，也不从图片读取数据。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day63/code/minimal_honest_axis.py
```

应显示两点的 normalized height 与 interval。若比例/列表不熟补 [F02](../../foundation_library/f02_csv_json/README.md)；漏斗回看 [Day 56](../day56/README.md)，配对区间回看 [Day 57](../day57/README.md)。

## 4. 即时知识

- **visual encoding**：位置、长度、颜色、形状等把数据映射为图形。
- **0–1 axis**：比例柱图的完整量程，避免截轴放大。
- **error bar**：本课画 95% Wilson interval，不是标准差。
- **direct label**：在图元旁写条件、值与 n，减少图例跳读。
- **colorblind-safe**：选可区分 palette，同时不用颜色作唯一信息。
- **panel**：共享视觉规则但回答不同问题的小图。
- **caption**：脱离正文也能解释对象、指标、区间和边界。

## 5. 成熟材料处方

- **中文主材料（开放科学促进联合体，8 分钟）**：[中国早期职业研究人员开放科学技术指南](https://open4science.cn/static/ECR_OpenScience_Guide_CN.pdf)。只读结果共享/可复现部分，思考图、数据和脚本应怎样一起发布。
- **补充材料（Datawrapper Academy，10 分钟）**：[Why our column and bar charts start at zero](https://www.datawrapper.de/academy/why-our-column-and-bar-charts-start-at-zero)。重点看截轴为何夸大长度差异，以及 bar/column 必须保留 zero baseline 的理由。
- **锁定项目定位（8 分钟）**：[success/cost 记录第 425–499 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L425-L499) 是图的 episode 来源；[suite 汇总第 697–741 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L697-L741) 不足以重建 pair/funnel，正式图必须使用逐 episode release。

## 6. 最小实验

[minimal_honest_axis.py](code/minimal_honest_axis.py) 是完整 17 行代码：

```python
#!/usr/bin/env python3
"""最小例子：比例图固定 0–1 轴，并保留区间。"""

points = [
    {"label": "baseline", "rate": 0.45, "low": 0.25, "high": 0.67},
    {"label": "repair", "rate": 0.60, "low": 0.39, "high": 0.78},
]

y_min, y_max = 0.0, 1.0
for point in points:
    if not (y_min <= point["low"] <= point["rate"] <= point["high"] <= y_max):
        raise ValueError("点估计或区间超出冻结比例轴")
    height = (point["rate"] - y_min) / (y_max - y_min)
    print(
        f"{point['label']}: normalized_height={height:.2f}, "
        f"interval=[{point['low']:.2f}, {point['high']:.2f}]"
    )
```

长文件 [generate_paper_figures.py](code/generate_paper_figures.py) 生成无外部绘图库依赖的 SVG、caption 与 manifest。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day63/code/generate_paper_figures.py \
  --input shared/fixtures/day63_figure_a.json --config mainline/day63/config/figure_a.json \
  --output-dir learner_outputs/mainline/day63/figures_a
```

应生成可解析的 3-panel SVG。正式替换只接受 Day 56/57/61 冻结统计和 hashes：funnel 用同一 episode cohort，pair 用同一 initial-state join，oracle 明示 diagnostic-only；不得手改 SVG 数值。

## 8. 独立挑战

换 B spec/config 生成新图。写 ≥260 字 memo，原样包含 `paper figure`、`stage funnel`、`paired transitions`、`intervention`、`0–1 axis`、`Wilson interval`、`denominator`、`colorblind-safe`、`direct label`、`caption`、`synthetic`、`cannot claim`。不给完整操作步骤，也不要复制 A 数值。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day63.tests.test_day63_tools
.venv-day06/bin/python mainline/day63/code/check_day63.py \
  --example-input shared/fixtures/day63_figure_a.json --example-config mainline/day63/config/figure_a.json --example-output-dir learner_outputs/mainline/day63/figures_a \
  --challenge-input shared/fixtures/day63_figure_b.json --challenge-config mainline/day63/config/figure_b.json --challenge-output-dir learner_outputs/mainline/day63/figures_b \
  --challenge-memo learner_outputs/mainline/day63/challenge_memo.md
```

口述 10 分：三面板 2；轴 2；区间/n 2；颜色/标签 2；caption/boundary 2。机器通过且 ≥8 才完成 Day 63；截轴、无区间、只靠颜色、混淆 oracle 或冒充正式图均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic spec 到 SVG/caption/manifest 的逐字节重建与 XML 解析。
- 静态源码事实：锁定 evaluator 的 episode success/cost 与 suite 汇总位置。
- 未运行：真实图数据、VLA-Arena、GPU 和视频。
- 可以主张：生成器强制 0–1 轴、区间、分母、直接标签和边界。
- 不能主张：图中 repair/oracle 对真实模型有效或具有因果意义。

自测题（答案在 `shared/answer_keys/day63.md`）：

1. 为什么比例柱图固定 0–1？
2. whisker 在本课表示什么？
3. 为什么不能只靠颜色编码？
4. oracle 面板应怎样解释？
5. caption 至少包含什么？
