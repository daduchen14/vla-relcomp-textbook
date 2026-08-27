# Gate 1：从新终端完成一个真实 episode

这是阶段 1 的基础设施 Gate。它必须在满足 Linux、Python 3.11、NVIDIA、EGL 和锁定 commit 的机器上执行；当前无合格环境时只保留诚实 preflight，不得用 fixture 冒充通过。

## 新输入

- Day 4 跟练使用 `mainline/day04/config/gate_a.json`。
- Gate 使用未跟练的 `mainline/day04/config/gate_b.json`：L0 task 1、seed 19、init state 0。
- 允许看 Day 1–4 正文、`--help` 和官方文档；禁止看 `shared/answer_keys/gate01.md`，禁止复用 Gate A registry/video。

## 从 fresh terminal 执行

```bash
cd /absolute/path/to/vla-relcomp-textbook
export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl
VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
python3.11 mainline/day04/code/real_preflight.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --output learner_outputs/mainline/gate01/preflight.json \
  --require-ready
python3.11 mainline/day04/code/run_single_episode.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --gate-config mainline/day04/config/gate_b.json \
  --output-dir learner_outputs/mainline/gate01
python3.11 mainline/day04/code/check_day04.py \
  --preflight learner_outputs/mainline/gate01/preflight.json \
  --registry learner_outputs/mainline/gate01/episode_registry.csv \
  --gate-config mainline/day04/config/gate_b.json
```

## 产物与结论

必须提交 preflight、单行 registry、非空日志、非空视频和三分钟口述。episode 的 `success=false` 可以是有效任务失败；import、渲染、CUDA、文件缺失属于基础设施失败，不能进入实验分母。

口述 10 分：observation 2、7 维 action 2、success/done/timeout 2、fixture/静态/真实边界 2、从 registry 反查版本与视频 2。机器通过且口述 ≥8 为“通过”；机器通过但口述 5–7 为“补做”；preflight/证据不完整为“停止扩张”。
