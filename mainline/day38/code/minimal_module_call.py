#!/usr/bin/env python3
"""最小例子：用一个 L0 结构样本调用规范化模块。"""

try:
    from .relation_normalizer import normalize_relation_instruction
except ImportError:
    from relation_normalizer import normalize_relation_instruction

example = {
    "level": "0",
    "target_object_id": "tomato_1",
    "start_relation": "NextTo",
    "start_reference_ids": "cereal_1",
    "goal_relation": "On",
    "goal_reference_ids": "bowl_1",
}
before = dict(example)
print(normalize_relation_instruction(example))
print(f"input_unchanged={example == before}")
