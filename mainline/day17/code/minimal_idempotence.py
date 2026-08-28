#!/usr/bin/env python3
"""最小例子：终态 ID 再出现时跳过，而不是重复执行。"""

planned = ["ep-a", "ep-b", "ep-a", "ep-c"]
terminal = {"ep-a"}
executed = []

for episode_id in planned:
    if episode_id in terminal:
        print(f"SKIP {episode_id}")
        continue
    executed.append(episode_id)
    terminal.add(episode_id)
    print(f"RUN  {episode_id}")

print(f"executed={executed}")
