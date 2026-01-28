
"""单元测试"""
import numpy as np


def test_basic():
    """基本测试"""
    state = np.ones(4) / 2
    assert abs(np.linalg.norm(state) - 1.0) < 1e-10
    print("✓ 基本测试通过")


if __name__ == "__main__":
    test_basic()
    print("✅ 所有测试通过")
