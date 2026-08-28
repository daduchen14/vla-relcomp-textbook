#!/usr/bin/env python3
"""最小例子：每种关系取相同数量，再展开 control/normalized 两臂。"""

samples = {
    "NextTo": ["n1", "n2", "n3"],
    "On": ["o1", "o2"],
    "In": ["i1", "i2", "i3"],
}
target_per_relation = min(len(rows) for rows in samples.values())
selected = {
    relation: rows[:target_per_relation]
    for relation, rows in samples.items()
}
pairs = [
    (sample_id, arm)
    for rows in selected.values()
    for sample_id in rows
    for arm in ("control", "normalized")
]
print(f"target_per_relation={target_per_relation}")
print(f"pair_count={len(pairs) // 2} arm_count={len(pairs)}")
print(f"balanced_counts={{{', '.join(f'{k}:{len(v)}' for k, v in selected.items())}}}")
