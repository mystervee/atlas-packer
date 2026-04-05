import unittest
from unittest.mock import MagicMock
from utils.validation import build_validation_summary

class TestValidation(unittest.TestCase):
    def create_mock_image(self, width, height):
        img = MagicMock()
        img.width = width
        img.height = height
        return img

    def test_empty_images(self):
        summary = build_validation_summary([], (512, 512), 0, 0)
        self.assertEqual(summary.image_count, 0)
        self.assertEqual(summary.total_pixel_area, 0)
        self.assertEqual(summary.estimated_fill_percent, 0.0)
        self.assertEqual(len(summary.warnings), 0)

    def test_fitting_images(self):
        images = [self.create_mock_image(100, 100), self.create_mock_image(200, 200)]
        summary = build_validation_summary(images, (512, 512), 0, 0)
        self.assertEqual(summary.image_count, 2)
        self.assertEqual(summary.total_pixel_area, 100*100 + 200*200)
        self.assertEqual(len(summary.warnings), 0)

    def test_oversized_image_width(self):
        images = [self.create_mock_image(600, 100)]
        summary = build_validation_summary(images, (512, 512), 0, 0)
        self.assertIn("At least one image is wider than available atlas width.", summary.warnings)

    def test_oversized_image_height(self):
        images = [self.create_mock_image(100, 600)]
        summary = build_validation_summary(images, (512, 512), 0, 0)
        self.assertIn("At least one image is taller than available atlas height.", summary.warnings)

    def test_area_exceedance(self):
        images = [self.create_mock_image(400, 400), self.create_mock_image(400, 400)]
        summary = build_validation_summary(images, (512, 512), 0, 0)
        self.assertGreater(summary.estimated_fill_percent, 100.0)
        self.assertIn("Estimated usage exceeds atlas area. Packing will likely fail.", summary.warnings)

    def test_zero_atlas_size(self):
        images = [self.create_mock_image(100, 100)]
        summary = build_validation_summary(images, (0, 0), 0, 0)
        self.assertEqual(summary.atlas_pixel_area, 0)
        self.assertEqual(summary.estimated_fill_percent, 0.0)

    def test_border_and_padding(self):
        # width=512, height=512, border=10, padding=5
        # atlas_area = 512 * 512 = 262144
        # images: 2x (100x100) -> total_img_area = 20000
        # border_area = 10 * 2 * (512 + 512) = 20 * 1024 = 20480
        # padding_area = 5 * (2-1) * min(512, 512) = 5 * 1 * 512 = 2560
        # total_area = 20000 + 20480 + 2560 = 43040
        images = [self.create_mock_image(100, 100), self.create_mock_image(100, 100)]
        summary = build_validation_summary(images, (512, 512), 10, 5)
        self.assertEqual(summary.total_pixel_area, 43040)

    def test_border_affects_size_warnings(self):
        # Image is 500 wide, atlas is 512. Border is 10.
        # Available width = 512 - (2*10) = 492.
        # 500 > 492 -> should warn.
        images = [self.create_mock_image(500, 100)]
        summary = build_validation_summary(images, (512, 512), 10, 0)
        self.assertIn("At least one image is wider than available atlas width.", summary.warnings)

if __name__ == "__main__":
    unittest.main()
