# Day 61 参考答案

1. Tidy data 的基本约定是一行一个观测单位、一列一个变量；本课观测单位是 episode。
2. 原始数据必须保持只读，所有清洗结果写入新的 derived artifact，并记录来源 hash。
3. `episode_id` 是主键；重复会让表格、视频和 claim 无法唯一追溯。
4. provenance index 把 tidy 行号/主键映回源记录和源文件摘要。
5. synthetic release candidate 只能证明发布流程可运行，不能作为真实模型实验结果。
