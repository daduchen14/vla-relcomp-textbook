# Day 23 参考答案（挑战后再看）

1. registry 定义完整计划/运行分母；left join 保留每个 episode，即使证据缺失也不会从分析中消失。输出 cardinality 应与 registry 一致。
2. 1:m 或 m:m join 会把一条 episode 膨胀成多行，后续计数和审阅都可能重复。必须在 join 前拒绝 video/stage/exception 重复 key。
3. 立即报错并核对批次、命名与 ID 生成，不应静默丢弃或凭文件名猜配；orphan 可能是跨 run 混入。
4. missing video 是证据采集/索引状态；success=0 是一个有效完成 episode 的终态结果。前者不能覆盖或推断后者。
5. 不能。P0–P3 是审阅顺序；stage 与 success 冲突也只说明观测信号不一致。语言、视觉、控制等 causal 结论需要后续受控干预。

挑战 memo 示例：B 仍以 registry 的 episode_id 做 left join 左键，先验证每张右表 one-to-one cardinality；重复键会膨胀行数，orphan 则说明 video、exception 或 stage 混入错误批次。q4 即使 stage missing 也必须留在索引中，不能被 inner join 删除或改写 success。exception 是运行证据，video 和四段事件是行为证据；review priority 只做 triage，不是 causal diagnosis。所有路径均为 synthetic fixture，不能声称真实证据完整率。
