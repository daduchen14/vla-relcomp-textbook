"""Day 8 最小版本：一个策略与环境交替运行的 CPU episode。"""

TARGET = 1.0
MAX_STEPS = 6


def observe(position: float) -> dict[str, float]:
    """环境暴露当前位置和目标，不包含隐藏状态。"""
    return {"position": position, "target": TARGET}


def policy(observation: dict[str, float]) -> float:
    """fixture 策略每步最多向目标移动 0.25。"""
    error = observation["target"] - observation["position"]
    return max(-0.25, min(0.25, error))


position = 0.0
success = False
for step_index in range(MAX_STEPS):
    observation = observe(position)
    action = policy(observation)
    position += action
    success = abs(TARGET - position) <= 0.05
    print(step_index, observation["position"], action, position, success)
    if success:
        break

print(f"episode_success={success}; steps={step_index + 1}")
print("synthetic CPU episode; not a VLA experiment result")
