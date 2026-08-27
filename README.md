# VLA-RelComp：70 天项目驱动教程（V2）

本仓库是 VLA-RelComp 的教材与教学代码仓库。V2 不再要求“先学完通用基础再进入项目”：学习者先完成不计天数的 [Day 0 诊断](mainline/day00_diagnostic/README.md)，通过者直接进入 70 天项目主线；遇到具体阻塞时再按诊断结果进入 [foundation_library](foundation_library/README.md)。

## 当前交付状态

- 主线进度：`0 / 70`。样章是教学设计验证，不代表学习者已经完成 Day 3。
- 已建立：Day 0 诊断与跳过机制。
- 唯一主线样章：[mainline/day03](mainline/day03/README.md)。
- 旧 Day 1–18 已原样迁移为 F01–F18 可选补习库，不计入主线完成天数。
- 本轮没有编写 mainline Day 1、Day 2 或 Day 4–70。

## 从哪里开始

1. 阅读 [START_HERE.md](START_HERE.md)。
2. 完成 [Day 0](mainline/day00_diagnostic/README.md) 并生成个人路由文件。
3. 通过诊断就按 [COURSE_MAP.md](COURSE_MAP.md) 进入主线；失败项只补对应 F 模块。
4. 所有学习者产物写入 `learner_outputs/`，不要覆盖教材 fixture 或参考答案。

研究目标以正式项目决策 D1 为准；上游 VLA-Arena 固定为 commit `babe582ebffc82b979b77964a7e56417d02f63a4`，目标 suite 的 registry 名称为 `extrapolation_preposition_combinations`。教材只保存教学文件，不修改研究仓库或 VLA-Arena 上游。

## 写作与事实边界

- 主线每天都采用固定十段模板，见 [AUTHORING_RULES.md](AUTHORING_RULES.md)。
- 真实项目事实必须引用锁定 commit 的文件、函数或配置。
- 免费本地 fixture、静态追踪和语法测试可以实际运行；VLA-Arena、MuJoCo、模型或 GPU 未运行时必须明确标记“未运行”。
- `main` 不在教材制作流程中被修改或合并；当前内容通过 Draft PR 审阅。

## 索引

- [课程逐日地图](COURSE_MAP.md)
- [作者规则](AUTHORING_RULES.md)
- [项目上下文](PROJECT_CONTEXT.md)
- [可选基础补习库](foundation_library/README.md)
- [Day 3 样章参考答案区](shared/answer_keys/day03.md)
