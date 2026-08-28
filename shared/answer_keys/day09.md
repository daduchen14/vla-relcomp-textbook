# Day 9 参考答案（独立挑战后再看）

1. `:objects` 声明可操作对象及类型；`:init` 是 episode 起点必须成立的谓词；`:goal` 是成功目标的逻辑条件。三者分别回答“有哪些实体、开始怎样、结束必须怎样”。
2. 对本套件的单个二元 goal，例如 `(On tomato_3 porcelain_bowl_1)`，第一个参数是被移动 target，第二个是 reference，谓词名 `On` 是终态关系。
3. `obj_of_interest` 是上游元数据，不能替代 goal。锁定 15 task 中有 7 个的 interest 没覆盖全部 goal 参数；教材保留并报警，不修改 upstream。
4. 自然语言用于给 policy 下指令，goal predicate 用于环境成功判定。两者若看起来不一致，应记录数据问题并沿 success 实现核实，不能凭语言手改 goal。
5. 静态解析能证明 commit blob 中的声明结构，不能证明对象实际生成、初态可恢复或 predicate 在仿真中按预期触发。

挑战 fixture 的 goal 是 `In apple_1 bowl_1`，但 `obj_of_interest` 只有 `apple_2`。正确结构必须以 goal 得出 target `apple_1`、reference `bowl_1`、relation `In`，并把不一致写入反思；该 fixture 不是 upstream task。
