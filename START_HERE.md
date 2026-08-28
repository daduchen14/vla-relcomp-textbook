# 从这里开始：先诊断，再直接进项目

这套课程不是“先上 18 天基础课”。Day 0 用五类短任务确认你今天真正缺什么；通过就直接进入 70 天主线。诊断不会评价你是否“聪明”，只负责减少无效学习时间。

## 入口流程

1. 从仓库根运行 `.venv-day06/bin/python mainline/day00_diagnostic/code/prepare_form.py --form A`。
2. 按 [Day 0 说明](mainline/day00_diagnostic/README.md) 完成五项真实输入任务，不看答案区。
3. 运行 `.venv-day06/bin/python mainline/day00_diagnostic/code/grade_form.py --form A --workspace learner_outputs/mainline/day00_diagnostic/form_A`。
4. `entry_ready=true`：直接进入 [70 天主线](COURSE_MAP.md)。有缺口：只打开报告列出的 [F 模块](foundation_library/README.md)。
5. 补习后用 B 卷复测；A/B 输入不同，不能靠复制示例和改 ID 通过。

Day 0、F01–F18 都不计入主线完成天数。主线中的即时诊断可能稍后触发 F10–F18；提前通过的人继续跳过。

## 五分钟公开演示

从仓库根目录运行：

```bash
python3 shared/scripts/course_demo.py
```

预期看到 `PASS: demo=public-entry-a steps=3 gpu=false`，详细步骤与 failure fallback 写入 `learner_outputs/mainline/day68/demo_report.json`。若失败，按报告中对应步骤处理：路由失败回 Day 0，结构失败按 validator 路径修复，最小表失败核对 input/expected hash 和输出目录。

## 两条阅读路径

- **学习者路径**：Day 0 → 只补报告点名的 F 模块 → [COURSE_MAP](COURSE_MAP.md) 逐日完成；教材存在不等于你已通过。
- **审阅者路径**：[PROJECT_CONTEXT](PROJECT_CONTEXT.md) → [COURSE_MAP](COURSE_MAP.md) → [Day 3 样章](mainline/day03/README.md) → [Day 61–66 数据与报告](mainline/day61/README.md) → 免费测试。

## 证据图例

- `📘 教材已编写`：教学文本、fixture 和 checker 已存在。
- `学习者已通过`：必须有学习者自己的机器产物与口述 rubric；当前仍是 `0 / 70`。
- `fixture/synthetic`：只验证代码、统计或写作机制。
- `静态源码事实`：从锁定 commit 精确读取，未执行 simulator。
- `真实运行`：需 raw episode、版本和资源证据；GPU/MuJoCo 未运行时不得声称完成。
