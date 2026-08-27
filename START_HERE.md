# 从这里开始：先诊断，再直接进项目

这套课程不是“先上 18 天基础课”。Day 0 用五类短任务确认你今天真正缺什么；通过就直接进入 70 天主线。诊断不会评价你是否“聪明”，只负责减少无效学习时间。

## 入口流程

1. 从仓库根目录运行 `python3 mainline/day00_diagnostic/code/diagnostic_router.py --init`。
2. 按 [Day 0 说明](mainline/day00_diagnostic/README.md) 完成五类入口任务与后续延迟检查。
3. 用 `--record FNN pass` 或 `--record FNN needs_review` 记录结果。
4. 运行 `python3 mainline/day00_diagnostic/code/diagnostic_router.py --report`。
5. 报告没有 `needs_review`：直接进入 [70 天主线](COURSE_MAP.md)。有缺口：只打开报告列出的 [F 模块](foundation_library/README.md)，完成快速路径后重测。

Day 0、F01–F18 都不计入主线完成天数。主线中的即时诊断可能稍后触发 F10–F18；提前通过的人继续跳过。
