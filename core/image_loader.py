"""Utilities for loading supported image assets for atlas packing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tga", ".webp"}


@dataclass(slots=True)
class LoadedImage:
    """Container representing a user-imported image."""

    name: str
    path: Path
    image: Image.Image

    @property
    def width(self) -> int:
        """Return loaded image width in pixels."""
        return self.image.width

    @property
    def height(self) -> int:
        """Return loaded image height in pixels."""
        return self.image.height


class ImageLoader:
    """Load image files from folders or explicit file paths."""

    def load_from_folder(self, folder: str | Path) -> list[LoadedImage]:
        """Load all supported images found directly in a folder."""
        folder_path = Path(folder)
        files = [
            path
            for path in sorted(folder_path.iterdir())
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        return self.load_from_files(files)

    def load_from_files(self, files: Iterable[str | Path]) -> list[LoadedImage]:
        """Load supported files and return a list of loaded images."""
        loaded: list[LoadedImage] = []
        for raw_path in files:
            path = Path(raw_path)
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            with Image.open(path) as img:
                loaded.append(LoadedImage(name=path.name, path=path, image=img.convert("RGBA")))
        return loaded
