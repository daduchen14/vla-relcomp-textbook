# VLA-RelComp：70 天教科书式实战教程

这是一条从“会一点 C/Python，但没有完整 AI 项目经验”走到 VLA-RelComp 研究成品的连续学习路线。课程每天约 7—9 小时；每一课都先讲为什么，再用完整代码落地，最后要求学习者亲手改一个变量并解释结果。

本仓库只保存新增教材和教学代码，不替换或修改已经冻结的项目决策与实验协议。研究背景保存在私有仓库 [`daduchen14/vla-relcomp-research-plan`](https://github.com/daduchen14/vla-relcomp-research-plan)；本仓库不复制其中的审计、闸门或可移植性文件。

教学数据的标识统一以 `fixture_` 开头；它们只用于学习代码，绝不是模型实验结果。模型权重、真实实验数据、个人输出、虚拟环境和缓存均不进入本仓库。

## 70 天、8 阶段

| 阶段 | 天数 | 核心内容 |
|---|---:|---|
| 1. 编程与实验基础 | Day 1–8 | 终端、Git、Python、CSV/JSON、调试、实验目录 |
| 2. 深度学习与 PyTorch | Day 9–18 | 张量、梯度、网络、优化器、CNN、Transformer 最小实现 |
| 3. 多模态与 VLA 原理 | Day 19–27 | token、视觉编码、VLM、模仿学习、动作块、闭环控制 |
| 4. VLA-Arena 实战 | Day 28–36 | BDDL、MuJoCo、环境、观测、动作、success、单 episode |
| 5. 基线实验 | Day 37–45 | SmolVLA/OpenVLA、L0/L1/L2、日志、视频、结果数据 |
| 6. 失效诊断 | Day 46–56 | 阶段分解、匹配反事实、语言 oracle、视觉诊断、统计分析 |
| 7. 最小修复 | Day 57–65 | 根据诊断选择修复、训练、消融、保持 L0、评测 L1/L2 |
| 8. 项目收尾 | Day 66–70 | 最终实验、图表、论文式写作、答辩材料、完整复现说明 |

## 当前交付

- [Day 1：终端、项目目录与第一段 Python 程序](day01/README.md)
- [Day 2：Python 数据结构、CSV/JSON 与第一份实验记录程序](day02/README.md)

## 统一执行约定

所有命令都从仓库根目录执行。打开终端后先运行：

```bash
cd "$(git rev-parse --show-toplevel)"
git branch --show-current
python3 --version
```

本课程的程序默认把学习输出写入 `learner_outputs/`。该目录已被本课程自己的 `.gitignore` 忽略，所以可以反复练习，不会把个人输出误当成教材源码。
