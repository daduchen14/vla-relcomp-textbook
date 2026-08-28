# Day 15 参考答案（挑战后再看）

1. branch/tag 名会移动，commit hash 指向确定 Git 对象；模型名同样可能更新，必须锁 revision。
2. 文件名和字节数相同仍可能内容不同，sha256 才能发现静默替换；hash 证明内容一致，不证明内容正确。
3. seed 不能替代 init_state：随机调用顺序可变，正式 manifest 必须同时登记显式 seed 与实际初态索引/内容。
4. L1/L2 是最终泛化测试，不能用来选 checkpoint、改阈值或调 prompt；否则 held-out 口径被污染。
5. 当前 A/B 都是 synthetic demonstration，且创建时 worktree dirty；formal lock 必须在真实模型 revision、正式文件和 clean commit 上重建。

挑战 memo 示例：B lock 同时记录教材 commit、锁定 upstream commit、模型 revision、每个文件 sha256、seed/init_state 口径和 L1/L2 保留规则。sha256 只能证明字节未变，不能证明协议合理；seed 也不能代替精确 init_state。当前 mode 不是 formal，因真实模型尚未选定且工作区不干净，所以只能叫合成冻结演示，不能作为 baseline 开跑依据。
