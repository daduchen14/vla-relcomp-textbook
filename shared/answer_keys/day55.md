# Day 55 参考答案

1. **为什么 oracle 必须单列？** 它使用 BDDL/模拟器真值等部署时不可得信息，只能诊断瓶颈或给上界。
2. **recovery/damage 的分母是什么？** repair failures 与 repair successes；不能都除以总 episodes。
3. **headroom 说明什么？** oracle rate−repair rate，说明在特权干预下的差距；不唯一证明机制。
4. **oracle 能进入 primary method 平均吗？** 不能，否则把不可部署系统混入最终方法结果。
5. **synthetic oracle 通过后可声称什么？** 只能声称分栏和统计逻辑正确，不能声称真实 oracle 有效。
