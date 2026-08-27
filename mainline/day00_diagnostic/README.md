# Day 0（不计天数）：诊断与跳过机制

目标不是证明“会不会编程”，而是生成一条最短学习路线。五类入口任务每类 20–40 分钟；F10–F18 在主线接近模型或训练时做延迟诊断，不要求现在为了“全绿”提前补课。

## 五类入口任务

1. **从仓库根运行脚本并解释退出码和输出路径**：失败路由 F01；如果是进程/权限路由 F05；如果是 import/环境路由 F06。
2. **把含一条坏记录的 CSV 转为 JSON，并写一个失败测试**：CSV/JSON 阻塞路由 F02；函数、模块或测试阻塞路由 F03。
3. **在练习仓库展示 status、diff、commit 并恢复一处改动**：失败路由 F04。
4. **说出 NumPy 图像与 PyTorch batch 的 shape、dtype、device，并完成一次轴变换**：NumPy 阻塞路由 F07；tensor/device 阻塞路由 F09。
5. **读一个十行 episode loop，指出 observation、action、step 和 success**：失败路由 F08。

训练与模型延迟诊断按 [路由清单](../../shared/schemas/day00_routes.json) 执行：autograd/训练/模块/优化器/DataLoader/CNN/token/attention/Transformer 分别映射 F10–F18。它们在相关主线日触发，不阻止入口通过者从 Day 1 开工。

## 操作

```bash
python3 mainline/day00_diagnostic/code/diagnostic_router.py --check
python3 mainline/day00_diagnostic/code/diagnostic_router.py --init
python3 mainline/day00_diagnostic/code/diagnostic_router.py --record F07 needs_review
python3 mainline/day00_diagnostic/code/diagnostic_router.py --record F08 pass
python3 mainline/day00_diagnostic/code/diagnostic_router.py --report
```

对入口任务已经验证的 F01–F09 逐项记录；未到时机的延迟项保留 `untested`。`report` 没有补习项就直接进入主线，不必等待 F10–F18。

## 验收

```bash
python3 -m unittest -v mainline.day00_diagnostic.tests.test_diagnostic_router
python3 mainline/day00_diagnostic/code/diagnostic_router.py --check
```

机器只验证路由完整性，不替你判断概念掌握。参考判分原则位于 `shared/answer_keys/day00_diagnostic.md`，首次作答前不要打开。
