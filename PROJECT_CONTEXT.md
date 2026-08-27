# VLA-RelComp 项目与学习者上下文

## 学习者与课程策略

学习者已经接触过 C、数据结构、408 与 Python，不应默认从零连续学习 18 天通用基础。V2 使用 Day 0 发现真实缺口：通过者直接做项目，失败者只补对应 F 模块，主线遇到新卡点时再做延迟诊断。

当前教程制作阶段不租 GPU、不付费。Mac/本地可完成源码阅读、fixture、静态检查、schema 与单元测试；Linux/NVIDIA、MuJoCo、真实模型和真实 episode 的结果必须等具备环境后再产生。

## 正式研究目标（D1）

研究对象是 VLA-Arena 的 `PrepositionCombinations` 组合关系泛化任务。核心不是只报总成功率，而是：

1. 用目标接触、抬升、参照接近、终态关系四段事件定位行为瓶颈；
2. 用关系/对象匹配反事实与可撤销 oracle 干预检验替代解释；
3. 只有证据充分时，选择一个最小修复；
4. 修复数据严格限定 L0，L1/L2 只用于保留测试；允许结论为负结果或证据不足。

## 固定事实

- 上游：`https://github.com/PKU-Alignment/VLA-Arena.git`
- commit：`babe582ebffc82b979b77964a7e56417d02f63a4`
- suite display name：`PrepositionCombinations`
- suite registry name：`extrapolation_preposition_combinations`
- levels：`0, 1, 2`
- 每级任务数：`5`

## 仓库职责

本仓库只新增和维护教材、教学代码、fixture、schema、答案与免费检查脚本。原研究仓库和锁定 upstream 均为只读事实源；教材 `main` 不在作者分支中修改或合并。

## 当前 V2 状态

- Day 0：已建立诊断与跳过机制，不计入 70 天。
- F01–F18：由旧 Day 1–18 迁移而来，内容只作机械路径更新，不计入主线。
- mainline Day 1–14：阶段 1–2 教材已编写；Day 3 仍标记为代表性样章，下一编写入口为 Day 15。
- 学习者完成数仍为 `0 / 70`；Gate 1–3 没有学习者通过证据，真实 episode、模型 pilot、四段事件视频抽查和 oracle pilot 均未运行。
- Day 8–14 的静态源码契约、CPU fixture 和 Gate 样例只是教材验收，不是 VLA-Arena/MuJoCo/模型结果；后续从 Day 15 顺序制作并继续分离三类状态。
