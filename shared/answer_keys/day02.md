# Day 2 参考答案（独立挑战后再看）

## 自测题

1. `pyproject.toml` 把命令 `vla-arena` 指向 `vla_arena.cli.main:main`；`main` 的 eval 子命令调用 `eval_main`。
2. `eval_main` 先用 `resolve_config_path` 找 YAML，再动态导入 `vla_arena.models.<model>.evaluator` 并调用其 `main(cfg=config_path)`。
3. random evaluator 的 `_parse_cfg` 把 YAML 字典构造成 `EvaluatorConfig`；`main` 再用 `get_benchmark_dict()[suite_name]()` 实例化 suite。
4. 目标 task map 是 L0/L1/L2 各 5 条，共 15 条；配置中的 `task_level` 只选择当次运行级别，不会把另外两级从源码清单删除。
5. 稀疏 checkout 中工作树没有 CLI 文件不等于 commit 没有；`git show HEAD:vla_arena/cli/main.py` 读取锁定 blob。

## 独立挑战

参考配置见相邻 `day02_challenge_config.yaml`。关键是同时满足：目标 registry、L2、每任务 2 次、seed 19、只开本地日志、关闭 W&B、结果路径在 learner_outputs。评分器会重新解析全部值，并重新生成 trace；复制主示例 JSON 后只改 stem 或 ID 不通过。
