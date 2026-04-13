"""Image processing utility helpers."""

from __future__ import annotations

from PIL import Image


MAX_ATLAS_SIZE = 16384
MIN_ATLAS_SIZE = 1

def parse_atlas_size(preset: str, custom_width: str, custom_height: str) -> tuple[int, int]:
    """Return selected atlas size from preset or custom values."""
    try:
        if preset.lower() == "custom":
            w = int(custom_width)
            h = int(custom_height)

            w = max(MIN_ATLAS_SIZE, min(w, MAX_ATLAS_SIZE))
            h = max(MIN_ATLAS_SIZE, min(h, MAX_ATLAS_SIZE))

            return w, h

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
    img_w, img_h = image.size
    if img_w <= width and img_h <= height:
        return image.copy()

    # Calculate scale ratio to fit within target dimensions while preserving aspect ratio
    ratio = min(width / img_w, height / img_h)
    new_w = max(1, int(img_w * ratio + 0.5))
    new_h = max(1, int(img_h * ratio + 0.5))

    return image.resize((new_w, new_h), Image.Resampling.LANCZOS)


def crop_image(image: Image.Image, width: int, height: int) -> Image.Image:
    """Crop image from top-left to target dimensions."""
    return image.crop((0, 0, min(width, image.width), min(height, image.height)))
