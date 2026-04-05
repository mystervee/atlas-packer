import unittest
import sys
from unittest.mock import MagicMock

# Mock PIL for environments where Pillow is not installed
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

from utils.image_utils import background_to_rgba

class TestImageUtils(unittest.TestCase):
    def test_background_to_rgba_valid_strings(self):
        test_cases = [
            ("transparent", (0, 0, 0, 0)),
            ("TRANSPARENT", (0, 0, 0, 0)),
            ("Transparent", (0, 0, 0, 0)),
            ("black", (0, 0, 0, 255)),
            ("BLACK", (0, 0, 0, 255)),
            ("Black", (0, 0, 0, 255)),
            ("white", (255, 255, 255, 255)),
            ("WHITE", (255, 255, 255, 255)),
            ("White", (255, 255, 255, 255)),
            ("unknown", (255, 255, 255, 255)),
            ("blue", (255, 255, 255, 255)),
            ("", (255, 255, 255, 255)),
        ]

        for bg_mode, expected_rgba in test_cases:
            with self.subTest(bg_mode=bg_mode):
                self.assertEqual(background_to_rgba(bg_mode), expected_rgba)

    def test_background_to_rgba_invalid_types(self):
        invalid_inputs = [None, 123, 3.14, [], {}]

        for invalid_input in invalid_inputs:
            with self.subTest(invalid_input=invalid_input):
                with self.assertRaises(AttributeError):
                    background_to_rgba(invalid_input)

if __name__ == "__main__":
    unittest.main()
