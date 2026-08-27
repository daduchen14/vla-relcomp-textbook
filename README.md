# VLA-RelComp：70 天教科书式实战教程

这是一条从“会一点 C/Python，但没有完整 AI 项目经验”走到 VLA-RelComp 研究成品的连续学习路线。课程每天约 7—9 小时；每一课都先讲为什么，再用完整代码落地，最后要求学习者亲手改一个变量并解释结果。

本仓库只保存新增教材和教学代码，不替换或修改已经冻结的项目决策与实验协议。研究背景保存在私有仓库 [`daduchen14/vla-relcomp-research-plan`](https://github.com/daduchen14/vla-relcomp-research-plan)；本仓库不复制其中的审计、闸门或可移植性文件。

教学数据的标识统一以 `fixture_` 开头；它们只用于学习代码，绝不是模型实验结果。模型权重、真实实验数据、个人输出、虚拟环境和缓存均不进入本仓库。

## 获取当前教材

Draft PR #1 尚未合并到 `main`，所以普通克隆后只看默认分支时，可能暂时看不到教材目录。请显式切换到教材分支：

```bash
git clone https://github.com/daduchen14/vla-relcomp-textbook.git
cd vla-relcomp-textbook
git switch --track origin/content/day01-02
```

如果已经克隆过仓库：

```bash
cd "$(git rev-parse --show-toplevel)"
git fetch origin
git switch content/day01-02 2>/dev/null || \
  git switch --track origin/content/day01-02
git pull --ff-only
```

看到 `day01/`、`day02/` 和 `COURSE_MAP.md` 就说明位置正确。不要为了“看得到教材”自行合并 `main`。

## 教材的长期上下文

- [`COURSE_MAP.md`](COURSE_MAP.md)：70 天逐日标题、依赖、产物与完成状态；
- [`AUTHORING_RULES.md`](AUTHORING_RULES.md)：每天的固定结构、代码和资料标准；
- [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md)：学习者画像、冻结研究问题、实验主线与算力边界；
- [`AGENTS.md`](AGENTS.md)：写作、中断恢复、Git 和禁止事项。

## 70 天、8 阶段

| 阶段 | 天数 | 核心内容 |
|---|---:|---|
| 1. 编程与实验基础（已完成） | Day 1–8 | 终端、Git、Python、CSV/JSON、调试、实验目录 |
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
- [Day 3：函数、模块、路径与可测试的数据校验](day03/README.md)
- [Day 4：Git 提交、分支、差异与可恢复实验](day04/README.md)
- [Day 5：Linux 文件、进程、环境变量与退出码](day05/README.md)
- [Day 6：Python 环境、包、依赖锁定与异常](day06/README.md)
- [Day 7：NumPy、数组、图像和机器人状态](day07/README.md)
- [Day 8：episode、step、success 与实验目录闭环](day08/README.md)
- [Day 9：Tensor、shape、dtype 与 device](day09/README.md)
- [Day 10：导数、计算图与 autograd](day10/README.md)
- [Day 11：线性回归——从数据、损失到参数更新](day11/README.md)
- [Day 12：nn.Module、参数与前向传播](day12/README.md)
- [Day 13：optimizer、mini-batch、epoch 与过拟合](day13/README.md)

## 统一执行约定

所有命令都从仓库根目录执行。打开终端后先运行：

```bash
cd "$(git rev-parse --show-toplevel)"
git branch --show-current
python3 --version
```

本课程的程序默认把学习输出写入 `learner_outputs/`。该目录已被本课程自己的 `.gitignore` 忽略，所以可以反复练习，不会把个人输出误当成教材源码。
