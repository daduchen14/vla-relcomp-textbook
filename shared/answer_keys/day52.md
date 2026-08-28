# Day 52 参考答案

1. **clean-room baseline 允许哪些输入？** 锁定源码、指定 base model、raw dataset、environment lock、initial states，全部按 hash 指定。
2. **为什么拒绝旧 eval result？** 它可能被误当本次输出或影响选择/停止，破坏独立重跑。
3. **缓存是否一律禁止？** 不是；按 hash 的只读 base/dataset cache 可允许，eval cache 和 output 必须新建为空。
4. **cleanroom id 绑定什么？** 接受输入的角色/ID/hash、锁定 commit、condition 与 final manifest hash。
5. **packet 通过是否有 baseline data？** 没有；状态 NOT_RUN，records 为 null。
