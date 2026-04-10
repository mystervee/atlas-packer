import unittest
import sys
from unittest.mock import MagicMock

# Mock PIL to avoid ModuleNotFoundError
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

from gui.settings_panel import SettingsPanel
from utils.image_utils import parse_atlas_size

class MockVar:
    def __init__(self, value):
        self.value = value
    def get(self):
        return self.value

class TestSecurityFix(unittest.TestCase):
    def test_settings_panel_safe_conversion(self):
        # Mocking SettingsPanel because we can't initialize it without Tk
        panel = MagicMock(spec=SettingsPanel)
        panel.preset_var = MockVar("1024x1024")
        panel.custom_w_var = MockVar("1024")
        panel.custom_h_var = MockVar("1024")
        panel.background_var = MockVar("Transparent")
        panel.border_var = MockVar("invalid")
        panel.padding_var = MockVar("not_a_number")
        panel.packing_mode_var = MockVar("Tight packing")
        panel.fixed_mode_var = MockVar("columns")
        panel.fixed_value_var = MockVar("also_invalid")
        panel.oversize_rule_var = MockVar("Scale to fit")
        panel.export_metadata_var = MockVar(True)
        panel.export_format_var = MockVar("PNG")

        # Use the actual methods from SettingsPanel
        panel._int_or_default = SettingsPanel._int_or_default.__get__(panel, SettingsPanel)
        panel.get_settings = SettingsPanel.get_settings.__get__(panel, SettingsPanel)

        settings = panel.get_settings()

        self.assertEqual(settings["border"], 0)
        self.assertEqual(settings["padding"], 0)
        self.assertEqual(settings["fixed_value"], 1)
        self.assertIsInstance(settings["border"], int)
        self.assertIsInstance(settings["padding"], int)
        self.assertIsInstance(settings["fixed_value"], int)

    def test_parse_atlas_size_safe_conversion(self):
        # Test valid inputs
        self.assertEqual(parse_atlas_size("1024x1024", "0", "0"), (1024, 1024))
        self.assertEqual(parse_atlas_size("Custom", "512", "512"), (512, 512))

        # Test invalid inputs
        self.assertEqual(parse_atlas_size("invalid_preset", "0", "0"), (1024, 1024))
        self.assertEqual(parse_atlas_size("Custom", "not_a_number", "512"), (1024, 1024))
        self.assertEqual(parse_atlas_size("Custom", "512", "not_a_number"), (1024, 1024))
        self.assertEqual(parse_atlas_size(None, "512", "512"), (1024, 1024))

    def test_parse_atlas_size_clamping(self):
        # Test lower bounds
        self.assertEqual(parse_atlas_size("Custom", "0", "0"), (1, 1))
        self.assertEqual(parse_atlas_size("Custom", "-100", "-50"), (1, 1))

        # Test upper bounds
        self.assertEqual(parse_atlas_size("Custom", "99999", "99999"), (16384, 16384))
        self.assertEqual(parse_atlas_size("Custom", "16385", "100"), (16384, 100))
        self.assertEqual(parse_atlas_size("Custom", "100", "16385"), (100, 16384))

if __name__ == "__main__":
    unittest.main()
