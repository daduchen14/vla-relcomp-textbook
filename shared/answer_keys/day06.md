# Day 6 参考答案（完成独立挑战后再看）

1. checkpoint repo 名可以继续指向变化中的仓库；40 位 revision 才把本次模型文件固定到一个不可变版本。VLA-Arena commit 与模型 revision 是两条不同的 provenance。
2. 锁定配置的 `chunk_size=50`、`n_action_steps=50`：队列空时 policy 生成 action chunk，转置后把前 50 步放入队列；每次 `select_action` 只弹出一步。第 51 次取动作前才需要重新生成 chunk（episode 提前结束除外）。
3. `policy.reset()` 清掉跨 episode 的 action/observation 队列；不清理会让新 episode 执行旧 episode 剩余动作，破坏独立性。
4. `status=planned` 的 manifest 只证明参数和锁定源码契约一致。真实 pilot 还必须有通过的 preflight、真实 checkpoint 加载、非空帧、日志、视频和单行 registry。成功可以是 `false`，但运行必须真实完成。
5. 模型加载或环境启动失败属于基础设施错误，不进入成功率分母；只有 evaluator 完成该 episode 并写出 `status=completed` 的记录，才是有效分母。

挑战 B 应保持同一 checkpoint、suite、level、trial 数和 max steps，只改变 task、seed 与 init state。其关键字段是 `task_id=3`、`seed=31`、`init_state_index=2`；不能复制 A 的 manifest 后只改 `form`，因为验收器会从 B config 和锁定源码重建全部内容。
