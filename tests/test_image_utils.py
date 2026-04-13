import unittest
import sys
from unittest.mock import MagicMock

# Mock PIL for environments where Pillow is not installed
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

from utils.image_utils import background_to_rgba, fit_image

class TestImageUtils(unittest.TestCase):
    def test_fit_image_no_upscale(self):
        # When image is smaller than target, it should just return a copy
        mock_img = MagicMock()
        mock_img.size = (100, 100)

        result = fit_image(mock_img, 200, 200)

        mock_img.copy.assert_called_once()
        self.assertFalse(mock_img.resize.called)
        self.assertEqual(result, mock_img.copy.return_value)

    def test_fit_image_downscale(self):
        # When image is larger than target, it should resize
        mock_img = MagicMock()
        mock_img.size = (400, 200) # 2:1 aspect ratio

        # Target 100x100 -> should result in 100x50
        result = fit_image(mock_img, 100, 100)

        mock_img.resize.assert_called_once()
        args, kwargs = mock_img.resize.call_args
        new_size, resampling = args
        self.assertEqual(new_size, (100, 50))
        self.assertFalse(mock_img.copy.called)

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
