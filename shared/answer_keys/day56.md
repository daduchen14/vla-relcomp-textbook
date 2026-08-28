# Day 56 参考答案

1. **reach rate 分母是什么？** 该 condition 的全部注册 episodes。
2. **conversion rate 分母是什么？** 到达上一阶段的 episodes；不是全部 episodes。
3. **为什么检查单调性？** 后阶段发生而前阶段未发生通常说明事件定义/日志 join 错误。
4. **drop-off 怎么算？** 上一阶段人数减当前阶段人数。
5. **synthetic funnel 能否定位真实瓶颈？** 不能，只验证事件 schema 与计算。
