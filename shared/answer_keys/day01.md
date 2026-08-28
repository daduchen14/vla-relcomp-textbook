# Day 1 参考答案（独立挑战后再看）

## 自测题

1. commit hash 锁定的是整个版本快照；分支名会继续移动，不能替代实验版本。
2. config 选择 suite/level，evaluator 驱动 episode，benchmark registry 把名称变成类，task map/BDDL 给出任务，environment 执行动作并写 success。
3. `extrapolation_preposition_combinations` 是代码 registry 名；README 的展示名称不能直接代替配置值。
4. 静态地图证明文件和调用契约存在，不证明依赖安装、MuJoCo 渲染、模型加载或 episode 成功。

## 独立挑战参考 JSON

```json
{
  "model": "smolvla",
  "evaluator": "vla_arena/models/smolvla/evaluator.py",
  "config": "vla_arena/configs/evaluation/smolvla.yaml",
  "config_class": "Args",
  "hooks": ["initialize_model", "run_episode", "run_task", "main"],
  "requires_gpu": true,
  "source_kind": "locked_upstream_static_map"
}
```

这些字段来自锁定源码的顶层符号与真实路径，不是根据文件名猜测。`requires_gpu=true` 描述未来真实模型操作的环境要求，不表示今天运行过 GPU。
