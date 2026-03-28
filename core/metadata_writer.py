"""Metadata writer for atlas sprite coordinates."""

from __future__ import annotations

import json
from pathlib import Path

from core.atlas_packer import SpritePlacement


def write_metadata_json(
    output_path: str | Path,
    atlas_filename: str,
    placements: dict[str, SpritePlacement],
) -> None:
    """Write sprite coordinates as JSON metadata next to atlas output."""
    payload = {
        "atlas": atlas_filename,
        "sprites": {
            name: {
                "x": placement.x,
                "y": placement.y,
                "w": placement.width,
                "h": placement.height,
            }
            for name, placement in placements.items()
        },
    }

    path = Path(output_path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
