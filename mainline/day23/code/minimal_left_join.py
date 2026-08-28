#!/usr/bin/env python3
"""最小例子：registry 是左表，证据缺失必须保留。"""

episodes = [
    {"episode_id": "e1", "success": "1"},
    {"episode_id": "e2", "success": "0"},
    {"episode_id": "e3", "success": ""},
]
videos = {
    "e1": "evidence/e1.mp4",
    "e2": "evidence/e2.mp4",
}

for episode in episodes:
    episode_id = episode["episode_id"]
    video = videos.get(episode_id, "MISSING")
    print(episode_id, episode["success"], video)

print(f"input_rows={len(episodes)}")
print("boundary=missing_evidence_is_not_model_failure")
