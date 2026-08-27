"""Day 6 最小版本：检查模块能否导入，并区分必需与可选依赖。"""

import importlib.util
import sys


def module_exists(module_name: str) -> bool:
    """只查找模块位置，不执行第三方模块代码。"""
    return importlib.util.find_spec(module_name) is not None


if __name__ == "__main__":
    required_module = "json"
    optional_module = "fixture_package_not_installed"
    print(f"python={sys.executable}")
    print(f"required:{required_module}={module_exists(required_module)}")
    print(f"optional:{optional_module}={module_exists(optional_module)}")
    if not module_exists(required_module):
        raise SystemExit(2)
