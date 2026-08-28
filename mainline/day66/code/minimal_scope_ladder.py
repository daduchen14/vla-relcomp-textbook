#!/usr/bin/env python3
"""最小例子：结论不能跨越证据的外推层级。"""

scope_ladder = [
    "synthetic fixture",
    "locked simulator episodes",
    "held-out simulator tasks",
    "new VLA checkpoints",
    "physical robots",
]
evidence_scope = "synthetic fixture"
requested_claim = "physical robots"

evidence_level = scope_ladder.index(evidence_scope)
claim_level = scope_ladder.index(requested_claim)
allowed = claim_level <= evidence_level

print(f"evidence_scope={evidence_scope}")
print(f"requested_claim={requested_claim}")
print(f"allowed={allowed}")
