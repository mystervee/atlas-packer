"""Zoomable preview canvas for atlas visualization and highlighting."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from core.atlas_packer import SpritePlacement


class PreviewCanvas(ttk.Frame):
    """Widget that renders atlas image with pan/zoom controls."""

    def __init__(self, master: tk.Widget) -> None:
        """Initialize canvas and interaction bindings."""
        super().__init__(master)
        self.canvas = tk.Canvas(self, background="#1f1f1f", width=700, height=520)
        self.canvas.pack(fill="both", expand=True)

        self._zoom = 1.0
        self._base_image: Image.Image | None = None
        self._photo: ImageTk.PhotoImage | None = None
        self._placements: dict[str, SpritePlacement] = {}
        self._image_id: int | None = None
        self._highlight_id: int | None = None

        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.canvas.bind("<ButtonPress-2>", self._on_pan_start)
        self.canvas.bind("<B2-Motion>", self._on_pan_move)
        self.canvas.bind("<ButtonPress-3>", self._on_pan_start)
        self.canvas.bind("<B3-Motion>", self._on_pan_move)

    def set_image(self, image: Image.Image, placements: dict[str, SpritePlacement]) -> None:
        """Load new atlas image and sprite placements into preview."""
        self._base_image = image
        self._placements = placements
        self._zoom = 1.0
        self._render()

    def highlight(self, sprite_name: str) -> None:
        """Highlight a placement rectangle for selected sprite name."""
        if self._highlight_id is not None:
            self.canvas.delete(self._highlight_id)
            self._highlight_id = None

        placement = self._placements.get(sprite_name)
        if not placement:
            return

        z = self._zoom
        self._highlight_id = self.canvas.create_rectangle(
            placement.x * z,
            placement.y * z,
            (placement.x + placement.width) * z,
            (placement.y + placement.height) * z,
            outline="#ff4040",
            width=2,
        )

    def _render(self) -> None:
        """Render atlas image according to current zoom value."""
        if self._base_image is None:
            self.canvas.delete("all")
            return

        view_w = max(1, int(self._base_image.width * self._zoom))
        view_h = max(1, int(self._base_image.height * self._zoom))
        resized = self._base_image.resize((view_w, view_h), Image.Resampling.NEAREST)
        self._photo = ImageTk.PhotoImage(resized)

        self.canvas.delete("all")
        self._image_id = self.canvas.create_image(0, 0, anchor="nw", image=self._photo)
        self.canvas.config(scrollregion=(0, 0, view_w, view_h))

    def _on_zoom(self, event: tk.Event) -> None:
        """Adjust zoom by mouse wheel movement."""
        if event.delta > 0:
            self._zoom = min(8.0, self._zoom * 1.1)
        else:
            self._zoom = max(0.1, self._zoom / 1.1)
        self._render()

    def _on_pan_start(self, event: tk.Event) -> None:
        """Start drag pan operation."""
        self.canvas.scan_mark(event.x, event.y)

    def _on_pan_move(self, event: tk.Event) -> None:
        """Apply drag pan operation."""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
