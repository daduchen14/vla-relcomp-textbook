# Day 28 参考答案（挑战后再看）

1. 双指接触可能只是夹到但未提起，物体仍在支撑面；lift 还要求持续高度增益与支撑释放。
2. 不同物体/场景绝对 z 不同；同 episode 的相对增益更可比，但 baseline 必须在稳定后的固定时刻。
3. 它排除目标仍靠原表面/容器承托的 z 波动；支撑对象与 contact margin 也必须预注册并抽查。
4. 原样保留 `LIFT_WITHOUT_BILATERAL_CONTACT`，检查视频、geom 与非典型推/勾路径，不能强改成一致或直接命名机制。
5. 不能。图只显示操作标签对高度阈值的敏感性；causal 机制需配对 intervention。

挑战 memo 示例：B 用同 episode 的 baseline z 计算 height gain，physical lift 还要求离开 support surface 并满足 threshold 的 sustained window。bilateral contact 单独记录；若 lift 成立而双指信号缺失，就是 probe gap。sensitivity SVG 展示阈值依赖，不是 causal 证据。全部输入是 synthetic trace，不能冒充 MuJoCo 或模型结果。
