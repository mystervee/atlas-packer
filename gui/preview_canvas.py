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
        self._selected_sprite: str | None = None
        self._render_job: str | None = None

        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.canvas.bind("<ButtonPress-2>", self._on_pan_start)
        self.canvas.bind("<B2-Motion>", self._on_pan_move)
        self.canvas.bind("<ButtonPress-3>", self._on_pan_start)
        self.canvas.bind("<B3-Motion>", self._on_pan_move)
        self.canvas.bind("<Configure>", self._on_resize)

    def set_image(
        self, image: Image.Image, placements: dict[str, SpritePlacement]
    ) -> None:
        """Load new atlas image and sprite placements into preview."""
        self._base_image = image
        self._placements = placements
        self._zoom = 1.0
        self._render()

    def highlight(self, sprite_name: str) -> None:
        """Highlight a placement rectangle for selected sprite name."""
        self._selected_sprite = sprite_name

        if self._highlight_id is not None:
            self.canvas.delete(self._highlight_id)
            self._highlight_id = None

        if not sprite_name:
            return

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

    def _schedule_render(self) -> None:
        """Schedule rendering with debounce to prevent UI freezing."""
        if self._render_job is not None:
            self.after_cancel(self._render_job)
        # 50ms delay is usually enough to batch fast wheel scroll events
        self._render_job = self.after(50, self._render)

    def _on_resize(self, event: tk.Event) -> None:
        """Handle canvas resize to update rendering region."""
        self._schedule_render()

    def _render(self) -> None:
        """Render atlas image according to current zoom value using a visible viewport optimization."""
        self._render_job = None

        if self._base_image is None:
            self.canvas.delete("all")
            return

        total_w = max(1, int(self._base_image.width * self._zoom))
        total_h = max(1, int(self._base_image.height * self._zoom))

        # Get the visible region of the canvas in scaled coordinates
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw <= 1 or ch <= 1:
            # Not fully initialized, reschedule rendering
            self._schedule_render()
            return

        cx = self.canvas.canvasx(0)
        cy = self.canvas.canvasy(0)

        # Add a buffer (1x canvas dimensions) to avoid flickering when panning
        buffer_x = cw
        buffer_y = ch

        left = max(0, cx - buffer_x)
        top = max(0, cy - buffer_y)
        right = min(total_w, cx + cw + buffer_x)
        bottom = min(total_h, cy + ch + buffer_y)

        # Convert back to original image coordinates for cropping
        orig_left = int(left / self._zoom)
        orig_top = int(top / self._zoom)
        orig_right = int(right / self._zoom)
        orig_bottom = int(bottom / self._zoom)

        # Ensure we don't try to crop an invalid 0x0 area
        if orig_right <= orig_left or orig_bottom <= orig_top:
            return

        # Crop the image first
        cropped = self._base_image.crop((orig_left, orig_top, orig_right, orig_bottom))

        # Resize only the cropped region
        target_w = int((orig_right - orig_left) * self._zoom)
        target_h = int((orig_bottom - orig_top) * self._zoom)

        # Guard against zero dimension due to floating point precision
        if target_w <= 0 or target_h <= 0:
            return

        resized = cropped.resize((target_w, target_h), Image.Resampling.NEAREST)
        self._photo = ImageTk.PhotoImage(resized)

        self.canvas.delete("all")

        # Place the image at the scaled 'left, top' coordinates we derived
        # We need to map 'orig_left, orig_top' precisely back to scaled coords
        # so it lines up with the full logical scrollregion.
        render_x = int(orig_left * self._zoom)
        render_y = int(orig_top * self._zoom)

        self._image_id = self.canvas.create_image(
            render_x, render_y, anchor="nw", image=self._photo
        )
        self.canvas.config(scrollregion=(0, 0, total_w, total_h))

        # Redraw highlight if any
        if self._selected_sprite is not None:
            self.highlight(self._selected_sprite)

    def _on_zoom(self, event: tk.Event) -> None:
        """Adjust zoom by mouse wheel movement."""
        if event.delta > 0:
            self._zoom = min(8.0, self._zoom * 1.1)
        else:
            self._zoom = max(0.1, self._zoom / 1.1)
        self._schedule_render()

    def _on_pan_start(self, event: tk.Event) -> None:
        """Start drag pan operation."""
        self.canvas.scan_mark(event.x, event.y)

    def _on_pan_move(self, event: tk.Event) -> None:
        """Apply drag pan operation and schedule render to show newly revealed areas."""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self._schedule_render()
