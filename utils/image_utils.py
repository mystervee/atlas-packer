"""Image processing utility helpers."""

from __future__ import annotations

from PIL import Image


def parse_atlas_size(preset: str, custom_width: str, custom_height: str) -> tuple[int, int]:
    """Return selected atlas size from preset or custom values."""
    try:
        if preset.lower() == "custom":
            return int(custom_width), int(custom_height)

        width, height = preset.lower().split("x")
        return int(width), int(height)
    except (ValueError, TypeError, AttributeError):
        return 1024, 1024


def background_to_rgba(background_mode: str) -> tuple[int, int, int, int]:
    """Convert background mode string to RGBA tuple."""
    mode = background_mode.lower()
    if mode == "transparent":
        return (0, 0, 0, 0)
    if mode == "black":
        return (0, 0, 0, 255)
    return (255, 255, 255, 255)


def fit_image(image: Image.Image, width: int, height: int) -> Image.Image:
    """Scale image to fit target size while preserving aspect ratio."""
    source = image.copy()
    source.thumbnail((width, height), Image.Resampling.LANCZOS)
    return source


def crop_image(image: Image.Image, width: int, height: int) -> Image.Image:
    """Crop image from top-left to target dimensions."""
    return image.crop((0, 0, min(width, image.width), min(height, image.height)))
