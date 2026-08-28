#!/usr/bin/env python3
"""最小例子：恢复率只以原本失败的配对为分母。"""

PAIRS = [(0, 1), (0, 0), (1, 1), (1, 0), (0, 1)]
failed = [pair for pair in PAIRS if pair[0] == 0]
succeeded = [pair for pair in PAIRS if pair[0] == 1]

recovered = sum(control == 0 and oracle == 1 for control, oracle in PAIRS)
damaged = sum(control == 1 and oracle == 0 for control, oracle in PAIRS)
recovery_rate = recovered / len(failed) if failed else None
damage_rate = damaged / len(succeeded) if succeeded else None

print(f"recovery={recovered}/{len(failed)}={recovery_rate:.3f}")
print(f"damage={damaged}/{len(succeeded)}={damage_rate:.3f}")
