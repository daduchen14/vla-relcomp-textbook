# AGENTS.md — VLA-RelComp 教材 V2

## 唯一课程路线

课程采用项目驱动的 70 天、8 阶段主线。Day 0 不计天数，用于诊断与跳过；`foundation_library/F01–F18` 是按需补习库，不是主线前置课，也不计入主线完成天数。

任何后续作者都不得：恢复旧 COURSE_MAP、从旧 Day 19 续写、把 F01–F18 重新排列成必修连续课程，或把样章存在误报为学习者已完成 Day 3。

## 研究与版本真相

- 研究目标以 `25_正式项目决策D1_VLA-RelComp.md` 为最高项目依据。
- 上游仓库：`https://github.com/PKU-Alignment/VLA-Arena.git`。
- 锁定 commit：`babe582ebffc82b979b77964a7e56417d02f63a4`。
- 目标 suite 显示名：`PrepositionCombinations`；registry 名：`extrapolation_preposition_combinations`。
- 研究策略是行为级诊断，以及证据触发的唯一最小 L0-only 修复；L1/L2 保持为测试。

不得修改研究仓库、上游 checkout 或教材 `main`，不得伪造 VLA-Arena、MuJoCo、模型或 GPU 运行结果。

## 主线每日强制结构

每个 mainline Day 必须严格按以下顺序：

1. 真实项目产物
2. 当前卡点
3. 前置诊断
4. 即时知识
5. 成熟材料处方
6. 最小实验
7. 真实 VLA-Arena 操作
8. 独立挑战
9. 验收 rubric
10. 证据复盘

答案必须放入 `shared/answer_keys/`，正文不能直接展示独立挑战答案。教学代码优先使用免费、本地、确定性 fixture；真实操作与 fixture 证据必须分栏。

## 当前边界

本轮只允许课程 V2 迁移、Day 0 和 `mainline/day03` 样章。不要自动补写 mainline Day 1、Day 2 或 Day 4–70。修改前阅读 [AUTHORING_RULES.md](AUTHORING_RULES.md)、[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) 与 [COURSE_MAP.md](COURSE_MAP.md)。
