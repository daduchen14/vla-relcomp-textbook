# Day 17 参考答案（挑战后再看）

1. checkpoint 至少记录 episode_id、attempts、status、last_error、result_sha256；它必须在每次 work item 后 atomic 更新。
2. retry 只适用于临时错误。环境/输入无效记 INVALID；达到上限仍失败记 FAILED；二者都不能补 `success=0`。
3. idempotent 意味着同一输入与既有终态 checkpoint 再运行不会再次调用 executor，也不会改变结果证据。
4. 先写临时文件再 `os.replace` 的 atomic 模式，避免进程中断留下半个 JSON/CSV；它不替代 fsync、远程对象存储事务或跨文件事务。
5. B 中 task 3 经两次 retry 后第三次成功，task 4 一次执行为真实失败式的合成结果；二者都是 fixture，不是 VLA 模型证据。

挑战 memo 示例：runner 每个 attempt 后 atomic 写 checkpoint 和 registry。RETRYABLE_ERROR 可 retry，达到 max attempts 才是 FAILED；确定的环境无效是 INVALID，不能写 success=0。COMPLETED/INVALID/FAILED 是终态，后续 resume 必须 idempotent 跳过。result_sha256 把 checkpoint 连到 evidence，未知 episode checkpoint 会被拒绝。这里所有结果均来自脚本化 executor，不是模型运行。
