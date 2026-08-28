# Day 50 参考答案

1. **为什么 synthetic 指标全达标仍停止扩张？** Gate 先检查证据资格；没有 formal checkpoints/evaluator records，数值不能进入项目结论。
2. **“补做”与“停止扩张”如何区分？** formal 证据已存在但某项可修复地缺失/失败时补做；证据层级根本不够或关键安全条件失败时停止扩张。
3. **为什么从 raw inputs 重建？** 防止摘要抄错、阈值漂移、挑 seed 或隐藏失败记录。
4. **Gate 通过需要哪些类证据？** 多 seed、L0 保持、L1/L2、最小消融/成本公平全部来自正式且身份锁定的原始记录。
5. **教材完成是否等于 learner Gate 通过？** 不等于；当前状态是 rehearsal only、未通过。
