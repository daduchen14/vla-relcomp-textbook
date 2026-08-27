# VLA-RelComp 70 天课程地图

状态记号：`✅ 完成` 表示当天教材、代码和本地适用检查已提交；`⬜ 未完成` 表示尚待编写。每天均遵守 `AUTHORING_RULES.md`，状态只能在当天验收并提交时改为完成。

## 阶段 1：编程与实验基础（Day 1–8）

| Day | 状态 | 标题 | 前置知识 | 当天核心产物 |
|---:|---|---|---|---|
| 1 | ✅ 完成 | 终端、项目目录与第一段 Python 程序 | 无 | `first_run.py` 与运行记录 |
| 2 | ✅ 完成 | Python 数据结构、CSV/JSON 与实验记录 | Day 1 | episode 规范 CSV 与 JSON 汇总 |
| 3 | ✅ 完成 | 函数、模块、路径与可测试的数据校验 | Day 2 字典/列表 | `episode_schema.py`、最小单元测试 |
| 4 | ✅ 完成 | Git 提交、分支、差异与可恢复实验 | Day 1 终端 | 练习仓库、提交清单与 diff 解读 |
| 5 | ✅ 完成 | Linux 文件、进程、环境变量与退出码 | Day 1–4 | `system_snapshot.py` 与进程练习 |
| 6 | ⬜ 未完成 | Python 环境、包、依赖锁定与异常 | Python 脚本 | 隔离环境、依赖清单、异常示例 |
| 7 | ⬜ 未完成 | NumPy、数组、图像和机器人状态 | Python 容器/循环 | 合成 RGB/state/action 数组 |
| 8 | ⬜ 未完成 | episode、step、success 与实验目录闭环 | Day 1–7 | CPU mini evaluator 与证据目录 |

## 阶段 2：深度学习与 PyTorch（Day 9–18）

| Day | 状态 | 标题 | 前置知识 | 当天核心产物 |
|---:|---|---|---|---|
| 9 | ⬜ 未完成 | Tensor、shape、dtype 与 device | NumPy | tensor 观察实验与 shape 检查器 |
| 10 | ⬜ 未完成 | 导数、梯度与 autograd | 高中函数、Tensor | 手算/自动梯度对照脚本 |
| 11 | ⬜ 未完成 | 线性回归：从数据到损失 | 梯度 | 从零线性回归与训练曲线数据 |
| 12 | ⬜ 未完成 | `nn.Module`、参数与前向传播 | 线性回归 | 最小网络和模型摘要 |
| 13 | ⬜ 未完成 | 优化器、batch、epoch 与过拟合 | 网络/损失 | 训练循环和对照实验 |
| 14 | ⬜ 未完成 | Dataset、DataLoader 与可复现随机性 | batch/seed | fixture 数据集与加载器 |
| 15 | ⬜ 未完成 | 图像张量、卷积和 CNN | Tensor/网络 | 最小图像分类 CNN |
| 16 | ⬜ 未完成 | 序列、token、embedding 与位置 | 线性层 | 字符 token 化和 embedding |
| 17 | ⬜ 未完成 | 注意力：查询、键、值 | 矩阵乘法/embedding | 单头 self-attention |
| 18 | ⬜ 未完成 | Transformer block 最小实现 | 注意力/网络 | CPU Transformer 与 shape 测试 |

## 阶段 3：多模态与 VLA 原理（Day 19–27）

| Day | 状态 | 标题 | 前置知识 | 当天核心产物 |
|---:|---|---|---|---|
| 19 | ⬜ 未完成 | 从像素到视觉 token | CNN/Transformer | patch embedding 可视化数据 |
| 20 | ⬜ 未完成 | 文本 token、提示模板与掩码 | token/attention | 指令编码器与 mask 实验 |
| 21 | ⬜ 未完成 | 多模态融合：图像怎样遇到语言 | 视觉/文本 token | 最小融合模型 |
| 22 | ⬜ 未完成 | VLM 到 VLA：表示如何变成动作 | 多模态融合 | fixture VLA 前向数据流 |
| 23 | ⬜ 未完成 | 机器人 observation、state 与 action | NumPy/Tensor | 观测动作 schema 与检查器 |
| 24 | ⬜ 未完成 | 行为克隆与监督式动作学习 | 训练循环/VLA | fixture 行为克隆训练 |
| 25 | ⬜ 未完成 | 连续动作、归一化与 7 维控制 | 回归/动作 | 动作归一化往返测试 |
| 26 | ⬜ 未完成 | action chunk 与时序预测 | 序列/动作 | chunk 构造与滚动窗口 |
| 27 | ⬜ 未完成 | 闭环控制、误差累积与失败来源 | episode/VLA | fixture 闭环模拟器 |

## 阶段 4：VLA-Arena 实战（Day 28–36）

| Day | 状态 | 标题 | 前置知识 | 当天核心产物 |
|---:|---|---|---|---|
| 28 | ⬜ 未完成 | VLA-Arena 全景、版本与免费静态准备 | Git/Linux/VLA | 上游资产清单与未运行声明 |
| 29 | ⬜ 未完成 | MuJoCo/仿真世界、坐标与位姿 | 状态/动作 | fixture 位姿计算脚本 |
| 30 | ⬜ 未完成 | BDDL/CBDDL 任务：init、对象与 goal | 仿真概念 | 教学任务解析器 |
| 31 | ⬜ 未完成 | PrepositionCombinations 与 L0/L1/L2 | BDDL | task manifest fixture |
| 32 | ⬜ 未完成 | evaluator 入口与配置数据流 | 模块/配置 | dry-run 配置检查器 |
| 33 | ⬜ 未完成 | observation 读取与图像/state 检查 | VLA 输入 | 观测摘要工具 |
| 34 | ⬜ 未完成 | action 适配、步进与终止条件 | 动作/闭环 | fixture 环境步进器 |
| 35 | ⬜ 未完成 | success predicate 与四段状态事件 | CBDDL/episode | 事件提取器及测试 |
| 36 | ⬜ 未完成 | 单 episode 运行手册与证据保存 | Day 28–35 | CPU dry-run + GPU 完整命令包 |

## 阶段 5：基线实验（Day 37–45）

| Day | 状态 | 标题 | 前置知识 | 当天核心产物 |
|---:|---|---|---|---|
| 37 | ⬜ 未完成 | baseline、random policy 与 E0 对照 | evaluator | random baseline 配置/记录器 |
| 38 | ⬜ 未完成 | SmolVLA 架构、模型卡与加载路径 | VLA/PyTorch | 静态配置与 GPU 运行手册 |
| 39 | ⬜ 未完成 | SmolVLA 单任务 pilot | Day 36/38 | pilot 命令、证据模板 |
| 40 | ⬜ 未完成 | OpenVLA 架构与推理接口 | VLA/模型加载 | 静态接口映射与运行手册 |
| 41 | ⬜ 未完成 | OpenVLA 单任务 pilot 与模型选择 | Day 39/40 | 可比 pilot 模板 |
| 42 | ⬜ 未完成 | seed、init state 与重复实验 | 实验记录 | trial matrix 生成器 |
| 43 | ⬜ 未完成 | L0 基线计划与任务级汇总 | L0/统计基础 | L0 manifest 与汇总脚本 |
| 44 | ⬜ 未完成 | L1/L2 保留测试与数据泄漏防线 | L0/L1/L2 | split 守卫器与测试 |
| 45 | ⬜ 未完成 | 基线总表、视频索引与异常分类 | Day 37–44 | baseline report builder |

## 阶段 6：行为级失效诊断（Day 46–56）

| Day | 状态 | 标题 | 前置知识 | 当天核心产物 |
|---:|---|---|---|---|
| 46 | ⬜ 未完成 | 从总体失败到四段可观测链 | 状态事件 | failure taxonomy |
| 47 | ⬜ 未完成 | 接触与目标选择诊断 | 坐标/事件 | target contact detector |
| 48 | ⬜ 未完成 | 抓取、抬升与阈值敏感性 | 事件/控制变量 | lift detector 对照 |
| 49 | ⬜ 未完成 | 搬运、参照接近与终态关系 | 空间关系 | approach/relation 指标 |
| 50 | ⬜ 未完成 | 最小反事实与控制变量 | 实验设计 | pair manifest validator |
| 51 | ⬜ 未完成 | 空间关系匹配对的构造 | BDDL/反事实 | relation pairs fixture |
| 52 | ⬜ 未完成 | 对象组合匹配对与混淆因素 | task manifest | object pairs fixture |
| 53 | ⬜ 未完成 | 语言 oracle：规范化而非提示词魔法 | VLA 指令/反事实 | language oracle transform |
| 54 | ⬜ 未完成 | 视觉对象提示 oracle 与特权信息边界 | 图像/grounding | visual oracle fixture |
| 55 | ⬜ 未完成 | Wilson 区间、恢复率与损伤率 | Python/概率直觉 | 统计脚本与手算对照 |
| 56 | ⬜ 未完成 | McNemar、失败案例与诊断结论 | 配对结果 | diagnosis report builder |

## 阶段 7：最小修复（Day 57–65）

| Day | 状态 | 标题 | 前置知识 | 当天核心产物 |
|---:|---|---|---|---|
| 57 | ⬜ 未完成 | 用证据选择唯一最小修复 | 诊断结论 | decision matrix（教学模板） |
| 58 | ⬜ 未完成 | L0 训练集构造与泄漏测试 | split/行为克隆 | L0-only dataset builder |
| 59 | ⬜ 未完成 | 关系规范化修复路线 | language oracle | normalization module |
| 60 | ⬜ 未完成 | 对比式 L0 样本与损失 | 训练/配对 | contrastive fixture pipeline |
| 61 | ⬜ 未完成 | 轻量微调配置、显存与 checkpoint | PyTorch/GPU 概念 | 训练配置与 CPU dry-run |
| 62 | ⬜ 未完成 | 训练日志、早停与失败恢复 | 训练循环/split | checkpoint/log manager |
| 63 | ⬜ 未完成 | 消融设计：只改变一个组件 | 对照实验 | ablation matrix |
| 64 | ⬜ 未完成 | 重新评测 L0 保持与 L1/L2 泛化 | 基线/统计 | evaluation matrix |
| 65 | ⬜ 未完成 | 正结果、负结果与最小修复结论 | 全阶段 | repair report builder |

## 阶段 8：项目收尾（Day 66–70）

| Day | 状态 | 标题 | 前置知识 | 当天核心产物 |
|---:|---|---|---|---|
| 66 | ⬜ 未完成 | 冻结最终实验矩阵与复现清单 | 全部实验 | final manifest validator |
| 67 | ⬜ 未完成 | 从 CSV 到可信表格与图形 | 统计/记录 | figure/table scripts |
| 68 | ⬜ 未完成 | 论文式报告：方法、结果与限制 | 图表/诊断 | 报告初稿模板 |
| 69 | ⬜ 未完成 | README、环境说明与一键复现入口 | Git/Linux/实验 | reproduction guide |
| 70 | ⬜ 未完成 | 答辩故事、现场演示与最终自检 | 全课程 | slides outline、口述稿、V1 清单 |

## 恢复点

- 已完成最后一天：Day 5。
- 下一天：Day 6。
- 当前阶段：阶段 1（编程与实验基础）。
- 远端工作位置：现有教材分支与 Draft PR #1；不得自动合并 `main`。
