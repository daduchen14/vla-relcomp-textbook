# Day 38 参考答案（挑战后再看）

1. single repair module 只负责把 L0 结构标签变为固定 TARGET、START、ACTION、GOAL 指令，不改图像、动作、evaluator 或模型。
2. canonical relation 把 NextTo/On/In/Between 映射成唯一 token，减少表面表达差异；它不证明模型学会空间关系。
3. pure function 对相同输入返回相同输出且 input unchanged，便于单测、回退和定位副作用。
4. unknown relation 必须失败而不是猜测，否则新关系会静默落入错误标签并污染 training pairs。
5. regression test 证明接口和已知例子没有回退；synthetic 通过不等于 model run 或真实修复有效。

挑战 memo 示例：single repair module 只接受 L0，输出 TARGET、START、ACTION、GOAL 与 canonical relation。它是 pure function，要求 input unchanged，并对 unknown relation 失败。regression test 不修改 upstream；当前全是 synthetic，没有 model run。
