"""Validation helpers for atlas packing estimates and warnings."""

from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.image_loader import LoadedImage


@dataclass(slots=True)
class ValidationSummary:
    """Aggregated validation stats shown before packing."""

    image_count: int
    total_pixel_area: int
    atlas_pixel_area: int
    estimated_fill_percent: float
    warnings: list[str]


def build_validation_summary(
    images: list[LoadedImage],
    atlas_size: tuple[int, int],
    border: int,
    padding: int,
) -> ValidationSummary:
    """Calculate simple pre-pack statistics and warnings."""
    width, height = atlas_size
    atlas_area = width * height
    count = len(images)
    total_area = sum(img.width * img.height for img in images)

    if count > 0:
        total_area += border * 2 * (width + height)
        total_area += padding * max(0, count - 1) * min(width, height)

    fill = (total_area / atlas_area * 100.0) if atlas_area > 0 else 0.0

    warnings: list[str] = []
    if fill > 100:
        warnings.append("Estimated usage exceeds atlas area. Packing will likely fail.")
    if images and max(i.width for i in images) > width - (2 * border):
        warnings.append("At least one image is wider than available atlas width.")
    if images and max(i.height for i in images) > height - (2 * border):
        warnings.append("At least one image is taller than available atlas height.")

    return ValidationSummary(
        image_count=count,
        total_pixel_area=total_area,
        atlas_pixel_area=atlas_area,
        estimated_fill_percent=fill,
        warnings=warnings,
    )
