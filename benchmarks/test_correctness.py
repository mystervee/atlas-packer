import sys
from unittest.mock import MagicMock

# Mock PIL.Image
mock_pil = MagicMock()
sys.modules["PIL"] = mock_pil
sys.modules["PIL.Image"] = mock_pil

from utils.validation import build_validation_summary

class MockImage:
    def __init__(self, w, h):
        self.width = w
        self.height = h

def test_correctness():
    atlas_size = (100, 100)
    border = 2
    padding = 2

    # Case 1: Empty images
    res1 = build_validation_summary([], atlas_size, border, padding)
    assert res1.image_count == 0
    assert res1.total_pixel_area == 0
    assert res1.warnings == []

    # Case 2: One image, within bounds
    res2 = build_validation_summary([MockImage(10, 10)], atlas_size, border, padding)
    assert res2.image_count == 1
    # total_area = 10*10 + 2 * 2 * (100+100) + 2 * (1-1) * 100 = 100 + 800 + 0 = 900
    assert res2.total_pixel_area == 900
    assert res2.warnings == []

    # Case 3: Image too wide
    res3 = build_validation_summary([MockImage(97, 10)], atlas_size, border, padding)
    # width limit = 100 - (2 * 2) = 96. 97 > 96.
    assert "At least one image is wider than available atlas width." in res3.warnings

    # Case 4: Image too tall
    res4 = build_validation_summary([MockImage(10, 97)], atlas_size, border, padding)
    assert "At least one image is taller than available atlas height." in res4.warnings

    # Case 5: Area exceeded
    # atlas area = 10000.
    # img area = 90 * 100 = 9000.
    # border area = 800.
    # total = 9800. Not exceeded.
    # img area = 95 * 100 = 9500.
    # total = 9500 + 800 = 10300. Exceeded.
    res5 = build_validation_summary([MockImage(95, 100)], atlas_size, border, padding)
    assert "Estimated usage exceeds atlas area. Packing will likely fail." in res5.warnings

    print("Correctness tests passed!")

if __name__ == "__main__":
    test_correctness()
