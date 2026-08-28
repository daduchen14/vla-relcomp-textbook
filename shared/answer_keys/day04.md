# Day 4 参考答案（Gate 后再看）

1. preflight 只检查前置条件；真正 episode 还要成功 import、建环境、reset、step 到终止并落证据。
2. `status=completed, success=false` 是有效任务失败，进入分母；import/CUDA/渲染/资产错误是基础设施失败，不进入分母。
3. OpenGL backend 在相关库 import/初始化时选择；事后设置变量可能已经来不及改变 backend。
4. 这些字段共同确定“哪份代码、哪个输入、哪次初始化产生哪个视频”；少一项就难以复现或排查。

独立 Gate B 的输入和人工要点见 `gate01.md`。答案不能提供虚构 registry；真实行只能由合格环境中的 runner 生成。
