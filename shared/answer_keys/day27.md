# Day 27 参考答案（挑战后再看）

1. near 是人为距离阈值事件；contact 是 collision geoms 的仿真接触。中心很近可能表面未碰，接触也可能在代表点距离较大时发生。
2. 要求连续 k 步，过滤一次抖动或掠过；k 和采样频率共同决定实际持续时间，必须随证据保存。
3. 它区分“没有接触任何物体”“先碰干扰物”“直接碰目标”。只保留最终 target contact 会掩盖对象选择错误。
4. 不能。它显示结论对阈值的稳定程度；最终操作定义仍需单位/几何依据、视频抽查和预注册。
5. 不能。也可能是动作控制、可达性、episode 超时、contact geom 配置或 probe/日志错误，需要后续 intervention 区分。

挑战 memo 示例：B 必须固定每个 episode 的 target_object_id，用同一 distance 定义和单位。near 由 threshold 与 sustained window 决定，contact 则来自真实 contact geom，二者不能互换。若 first contact 是 wrong object，之后再碰目标也要保留选择轨迹。sensitivity 只检查阈值依赖，不给 causal 机制。当前输入是 synthetic trace，不是 MuJoCo 或模型结果。
