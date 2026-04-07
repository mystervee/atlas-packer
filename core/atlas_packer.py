"""Core atlas packing algorithms and composition logic."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, sqrt

from PIL import Image

from core.image_loader import LoadedImage
from utils.image_utils import background_to_rgba, crop_image, fit_image


@dataclass(slots=True)
class SpritePlacement:
    """Position and dimensions of a sprite in the atlas."""

    x: int
    y: int
    width: int
    height: int


@dataclass(slots=True)
class PackResult:
    """Result of pack operation including composed atlas image and warnings."""

    atlas: Image.Image
    placements: dict[str, SpritePlacement]
    warnings: list[str]
    fill_percent: float


class AtlasPacker:
    """Perform sprite packing using grid and simple tight shelf algorithms."""

    def pack(
        self,
        images: list[LoadedImage],
        atlas_size: tuple[int, int],
        packing_mode: str,
        border: int,
        padding: int,
        background_mode: str,
        oversize_rule: str,
        fixed_mode: str = "columns",
        fixed_value: int = 1,
    ) -> PackResult:
        """Pack images according to selected mode and return composed atlas."""
        atlas_width, atlas_height = atlas_size
        warnings: list[str] = []

        canvas = Image.new("RGBA", (atlas_width, atlas_height), color=background_to_rgba(background_mode))

        if packing_mode == "Grid packing":
            placements, warnings = self._pack_grid(
                images,
                atlas_size,
                border,
                padding,
                oversize_rule,
            )
        elif packing_mode == "Fixed columns or rows":
            placements, warnings = self._pack_fixed(
                images,
                atlas_size,
                border,
                padding,
                oversize_rule,
                fixed_mode,
                fixed_value,
            )
        else:
            placements, warnings = self._pack_tight(
                images,
                atlas_size,
                border,
                padding,
                oversize_rule,
            )

        used_area = 0
        for loaded in images:
            placement = placements.get(loaded.name)
            if not placement:
                continue

            processed = self._apply_oversize_rule(
                loaded.image,
                placement.width,
                placement.height,
                oversize_rule,
            )
            if processed is None:
                warnings.append(f"Skipped {loaded.name}: rejected by oversize handling rule.")
                continue

            canvas.paste(processed, (placement.x, placement.y), processed)
            used_area += placement.width * placement.height

        fill_percent = (used_area / (atlas_width * atlas_height)) * 100 if atlas_width and atlas_height else 0
        return PackResult(atlas=canvas, placements=placements, warnings=warnings, fill_percent=fill_percent)

    def _apply_oversize_rule(
        self,
        image: Image.Image,
        target_w: int,
        target_h: int,
        oversize_rule: str,
    ) -> Image.Image | None:
        """Apply scaling/cropping/rejection rule for oversized image placement."""
        if image.width <= target_w and image.height <= target_h:
            return image

        if oversize_rule == "Scale to fit":
            return fit_image(image, target_w, target_h)
        if oversize_rule == "Crop":
            return crop_image(image, target_w, target_h)
        return None

    def _pack_grid(
        self,
        images: list[LoadedImage],
        atlas_size: tuple[int, int],
        border: int,
        padding: int,
        oversize_rule: str,
    ) -> tuple[dict[str, SpritePlacement], list[str]]:
        """Pack images in a square-like grid with uniform cells."""
        if not images:
            return {}, []

        warnings: list[str] = []
        width, height = atlas_size
        columns = max(1, ceil(sqrt(len(images))))
        rows = max(1, ceil(len(images) / columns))

        cell_w = (width - 2 * border - (columns - 1) * padding) // columns
        cell_h = (height - 2 * border - (rows - 1) * padding) // rows

        if cell_w <= 0 or cell_h <= 0:
            return {}, ["Grid settings leave no space for cells."]

        placements: dict[str, SpritePlacement] = {}
        for idx, loaded in enumerate(images):
            row = idx // columns
            col = idx % columns
            x = border + col * (cell_w + padding)
            y = border + row * (cell_h + padding)
            placements[loaded.name] = SpritePlacement(x=x, y=y, width=cell_w, height=cell_h)

            if oversize_rule == "Reject with warning" and (loaded.width > cell_w or loaded.height > cell_h):
                warnings.append(
                    f"{loaded.name} exceeds grid cell {cell_w}x{cell_h} and will be rejected."
                )

        return placements, warnings

    def _pack_fixed(
        self,
        images: list[LoadedImage],
        atlas_size: tuple[int, int],
        border: int,
        padding: int,
        oversize_rule: str,
        fixed_mode: str,
        fixed_value: int,
    ) -> tuple[dict[str, SpritePlacement], list[str]]:
        """Pack images using fixed column or row counts with uniform cells."""
        if not images:
            return {}, []

        width, height = atlas_size
        fixed_value = max(1, fixed_value)
        if fixed_mode == "rows":
            rows = fixed_value
            columns = ceil(len(images) / rows)
        else:
            columns = fixed_value
            rows = ceil(len(images) / columns)

        cell_w = (width - 2 * border - (columns - 1) * padding) // columns
        cell_h = (height - 2 * border - (rows - 1) * padding) // rows
        if cell_w <= 0 or cell_h <= 0:
            return {}, ["Fixed layout leaves no usable cell area."]

        placements: dict[str, SpritePlacement] = {}
        warnings: list[str] = []

        for idx, loaded in enumerate(images):
            row = idx // columns
            col = idx % columns
            x = border + col * (cell_w + padding)
            y = border + row * (cell_h + padding)
            placements[loaded.name] = SpritePlacement(x=x, y=y, width=cell_w, height=cell_h)

            if oversize_rule == "Reject with warning" and (loaded.width > cell_w or loaded.height > cell_h):
                warnings.append(
                    f"{loaded.name} exceeds fixed cell {cell_w}x{cell_h} and will be rejected."
                )

        return placements, warnings

    def _pack_tight(
        self,
        images: list[LoadedImage],
        atlas_size: tuple[int, int],
        border: int,
        padding: int,
        oversize_rule: str,
    ) -> tuple[dict[str, SpritePlacement], list[str]]:
        """Pack images with a simple shelf algorithm (tight mode)."""
        width, height = atlas_size
        max_w = width - 2 * border
        max_h = height - 2 * border

        placements: dict[str, SpritePlacement] = {}
        warnings: list[str] = []

        x = border
        y = border
        shelf_height = 0

        ordered = sorted(images, key=lambda img: img.height, reverse=True)

        for loaded in ordered:
            processed = self._apply_oversize_rule(loaded.image, max_w, max_h, oversize_rule)
            if processed is None:
                warnings.append(f"Skipped {loaded.name}: larger than atlas bounds.")
                continue

            sprite_w, sprite_h = processed.width, processed.height

            if x + sprite_w > width - border:
                x = border
                y += shelf_height + padding
                shelf_height = 0

            if y + sprite_h > height - border:
                warnings.append(f"No space left for {loaded.name} in tight packing.")
                continue

            placements[loaded.name] = SpritePlacement(x=x, y=y, width=sprite_w, height=sprite_h)
            x += sprite_w + padding
            shelf_height = max(shelf_height, sprite_h)

        return placements, warnings
