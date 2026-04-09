import unittest
import sys
from unittest.mock import MagicMock

# Mock PIL for environments where Pillow is not installed
if 'PIL' not in sys.modules:
    sys.modules['PIL'] = MagicMock()
    sys.modules['PIL.Image'] = MagicMock()

from core.atlas_packer import AtlasPacker

class TestAtlasPacker(unittest.TestCase):
    def test_pack_grid_empty_images(self):
        packer = AtlasPacker()
        placements, warnings = packer._pack_grid(
            images=[],
            atlas_size=(512, 512),
            border=0,
            padding=0,
            oversize_rule="Crop"
        )
        self.assertEqual(placements, {})
        self.assertEqual(warnings, [])

if __name__ == "__main__":
    unittest.main()
