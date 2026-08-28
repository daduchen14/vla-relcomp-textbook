# Day 0 参考判分原则（首次诊断后再看）

## A/B 卷参考执行

完成首次作答后，教师可用独立参考作答器复核评分器：

```bash
.venv-day06/bin/python shared/answer_keys/day00_reference.py \
  --form B \
  --workspace learner_outputs/mainline/day00_diagnostic/form_B
.venv-day06/bin/python mainline/day00_diagnostic/code/grade_form.py \
  --form B \
  --workspace learner_outputs/mainline/day00_diagnostic/form_B
```

参考作答器从当前卷的真实输入计算结果，不复制固定 A 卷 ID。它还会只提交 `settings.txt`、删除 `scratch.txt`，并创建 `diagnostic:` 开头的提交。完整实现见相邻 `day00_reference.py`。

## 人工判分边界

- 任务 1：能从根目录运行、区分 stdout/stderr、解释退出码 0 与非 0，并指出输出实际位置。
- 任务 2：坏行不会静默进入输出；JSON 字段类型稳定；至少一个测试能在错误实现上失败。
- 任务 3：能区分工作区、暂存区与 commit；恢复目标明确，不使用破坏性宽范围命令。
- 任务 4：能把 shape 的每一维绑定到语义，区分 dtype 与 device，轴变换后给出新 shape。
- 任务 5：能按 observation→policy→action→step→success 顺序复述，并说明 success 不等于“程序没报错”。

某一条需要照抄答案才能完成，就记录对应 `needs_review`；独立完成则记录 `pass`。延迟诊断只在任务将要用到时评分。
