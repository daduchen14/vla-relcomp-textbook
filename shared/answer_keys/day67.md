# Day 67 参考答案

1. fresh clone 排除当前工作树未提交文件、环境变量和手工缓存对结果的隐性贡献。
2. 应记录 branch/commit、Python/依赖、输入/脚本 hash、完整命令、exit code 与输出 hash。
3. expected output 是冻结验收对象；它不能由本次输出自动重写。
4. cache 应显式禁用或记录命中来源，否则无法证明从输入重建。
5. CPU synthetic table 复现不等于 VLA-Arena/GPU 实验复现。
